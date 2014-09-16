from config import *
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

    def __init__(self, game, clock):
        super(Judge, self).__init__()
        self.clock = clock
        self.players = []
        self.game = game
        self.current_pid = None
        self.interface = {"make_transaction": self.make_transaction}
        self.current_player_transaction_attempts = 0 
        self.current_player_transactions = 0 
        self.banned_players = []
        self.players_ids = None
        self.passwords = None

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
            self.current_player_transactions = 0
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
                self.current_player_thread.join(PLAYER_TIMEOUT)
                if self.current_player_thread.is_alive():
                    l("#"*100)
                    l("Player", self.current_pid, "timed out! After", time() - t)
                    l("#"*100)
                    self.bann_player(pid)
            except PlayerBannedException:
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
        """

            Submits a transaction to the judging party. The judging party will go through standard checks to see if the
            calling player has the right to submit a transaction, then it will try to validate the transaction and
            potentially refuse it. For a complete description of what happens when a transaction is submitted to the
            judging party, please refer to the paper, located in the `paper/` directory.

            :param{AbstractPlayer} calling_player: The player that is calling the method (typically, `self`)
            :param{string} type: The type of transaction to be performed
            :param{dict} args: Arguments to be passed to the transaction

        """

        d("make_transaction()")
        d("Banned players", self.banned_players)
        if self.current_pid in self.banned_players:
            return  # Just return until it times out

        # The calling player has to be the current player, only the current player is allowed to submit transactions
        # during her own turn. When calling make_transaction the player has to pass itself as a parameter to prove who 
        # she claims she is. In case this does not match the comparison with the current player, it means the calling 
        # player is trying to submit transaction while it is not her turn and thus she is cheating, so we ban her.
        if kwargs['calling_player'] is not self.players[self.current_pid]:
            # bann_player takes the player id as a parameter but all we have is the player object reference itself
            # so we need to first retrieve its id, which is nothing else than the index in the players' list
            # @TODO stop using the index of the list as the id, move to a dict {id: player_reference}
            self.bann_player(self.players.index(kwargs['calling_player']))
            raise PlayerBannedException("Attempted to submit a transaction while it was not her turn.")

        if self.current_player_transaction_attempts >= ALLOWED_TRANSACTIONS_ATTEMPTS_PER_ROUND \
            or self.current_player_transactions >= ALLOWED_TRANSACTIONS_PER_ROUND:
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
                    valid_transaction[1].apply(self)
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
                  self.players[tr.player_1].agree_with_transaction(data) == self.passwords[tr.player_1]
                and self.players[tr.player_2].agree_with_transaction(data) == self.passwords[tr.player_2]
            )
        except Exception as e:
            d(e)
            return False

    def is_valid_player(self, pid):
        return pid in self.players_ids

    def has_enough_resource(self, pid_from, rtype, amount):
        return self.game.players_resources[pid_from][rtype] >= amount