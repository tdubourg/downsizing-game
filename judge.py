from config import ALLOWED_TRANSACTIONS_PER_ROUND
from transactions import *
from utils import d, l, e as err, i

from threading import Timer
from time import time

class PlayerBannedException(Exception):
    """
    This exception will be raised by the judge when he kills a player. 
    It holds the player that has been killed
    """
    def __init__(self, player):
        super(PlayerBannedException, self).__init__()
        self.player = player

# def timer_func(*args):
#     l("Forever is over!")
#     raise Exception("Forever is over")

def player_thread(player, round_number):
    try:
        player.play_round(round_number)
    except SystemExit:
        l("Thread exited by force!")
        return

# import threading

# class MyT(threading.Thread):
#     def exit(self):
#         print("Exiting??")
#         raise SystemExit


import ctypes

def terminate_thread(thread):
    """Terminates a python thread from another thread.

    :param thread: a threading.Thread instance
    """
    if not thread.isAlive():
        print ("Thread WAS NOT ALIVE!")
        return

    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError("nonexistent thread id")
    elif res > 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
    # print ("Waiting for thread to exit...")
    # thread.join(None)

class Judge(object):
    """
    The Judge is the one ruling the game. It allows or not actions to be taken, 
    and kills misbehaving players.
    """

    transaction_types = {
        "UnidirectionalTransaction": UnidirectionalTransaction,
        "BidirectionalTransaction": BidirectionalTransaction,
        "ScheduledUnidirectionalTransaction": ScheduledUnidirectionalTransaction,
        "ScheduledBidirectionalTransaction": ScheduledBidirectionalTransaction,
    }

    TRANSACTION_ATTEMPTS_QUOTA = 500000000000
    TIMEOUT = 1  # seconds

    def __init__(self, game, clock):
        super(Judge, self).__init__()
        self.clock = clock
        self.players = []
        self.game = game
        self.current_pid = None
        self.interface = {"make_transaction": self.make_transaction}
        self.current_player_transaction_attempts = 0 
        self.banned_players = []

    def play_round(self):
        d("Players ids:", self.players_ids)
        for pid in self.players_ids:
            d("=" * 30, "Changing player")
            # This is a quick and dirty fix, @TODO
            d("Banned players", self.banned_players)
            if pid in self.banned_players:
                continue
            d("Current player id:", pid)
            self.current_player_transaction_attempts = 0
            p = self.players[pid]
            t = None
            self.current_pid = pid
            try:
                t = time()
                import threading
                self.current_player_thread = threading.Thread(
                    target=player_thread, 
                    args=(p, self.clock.current_turn_number())
                )
                self.current_player_thread.start()
                self.current_player_thread.join(self.TIMEOUT)
                if self.current_player_thread.is_alive():
                    l("#"*100)
                    l("Player", self.current_pid, "timed out! After", time() - t)
                    l("#"*100)
                    self.bann_player(pid)
            except PlayerBannedException as e:
                # This is a quick and dirty fix, @TODO
                self.bann_player(pid)
            except SystemExit as ex:
                l("Player", self.current_pid, "timed out (exception)! After", time() - t)
                self.bann_player(pid)
                d(ex)
                return False  # @TODO
            
            # This displays the state of the game
            l(self.game)

            self.clock.tick()
            if self.clock.is_over():
                l("Game Over")
                return False
        return True

    def bann_player(self, pid):
        l("Player", pid, "is being banned.")
        while self.current_player_thread.is_alive():
            d("Killing it!")
            terminate_thread(self.current_player_thread)
            self.current_player_thread.join(0.01)  # Wait ten ms between each kill attempt
        self.banned_players.append(pid)
        l("Banned players:", self.banned_players)


    def make_transaction(self, **kwargs):
        d("make_transaction()")
        d("Banned players", self.banned_players)
        if self.current_pid in self.banned_players:
            return  # Just return until it times out
        if self.current_player_transaction_attempts > self.TRANSACTION_ATTEMPTS_QUOTA:
            self.bann_player(self.current_pid)
            raise PlayerBannedException("Attempted too many transactions.")
        self.current_player_transaction_attempts += 1
        try:
            type_str = kwargs['type']
            args = kwargs['args']
        except KeyError as ex:
            d(ex)
            return False
        d("make_transaction() with:", str(type_str), str('args'))
        try:
            transaction = self.transaction_types[type_str](*args)
        except Exception as e:
            d(e)
            return False
        try:
            d("Instantiated transaction", transaction)
            if not isinstance(transaction, AbstractTransaction):
                d("Not an instance of AbstractTransaction")
                return False
            else:
                d("Is a rightful instance")
                if not self._check_player_agreements(transaction):
                    d("A player refused the transaction")
                    return False

                d("Was agreed by all players")
                valid_transaction = transaction.is_valid(self)
                if valid_transaction[0] is True:
                    # Note that there will not be any concurrent modification between the check of the transaction and 
                    l("Transaction is valid, applying it")
                    valid_transaction[1].apply(self.game.players_resources)
                    # Transaction is applied, tick the clock
                    self.clock.tick()
                    return True
                # The transaction was not valid
                d("Transaction is invalid")
                return False
        except:
            # If anything failed, the transaction should not be accepted
            return False
    
    def _check_player_agreements(self, tr):
        # Make a copy of the data of the transaction...
        d("WTF")
        data = dict(tr.get_data())
        d("WTF")
        try:
            return bool(
                  self.players[tr.player_1].agree_with_transaction(data)
                & self.players[tr.player_2].agree_with_transaction(data)
            )
        except Exception as e:
            d(e)
            return False

    def is_valid_player(self, pid):
        return pid in self.players_ids

    def has_enough_resource(self, pid_from, rtype, amount):
        return self.game.players_resources[pid_from][rtype] >= amount