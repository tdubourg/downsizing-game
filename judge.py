from config import ALLOWED_TRANSACTIONS_PER_ROUND
from transactions import *
from utils import d, l, e

class PlayerBannedException(Exception):
    """
    This exception will be raised by the judge when he kills a player. 
    It holds the player that has been killed
    """
    def __init__(self, player):
        super(PlayerBannedException, self).__init__()
        self.player = player

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

    TRANSACTION_ATTEMPTS_QUOTA = 5

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
            # This is a quick and dirty fix, @TODO
            if pid in self.banned_players:
                continue
            d("Current player id:", pid)
            self.current_player_transaction_attempts = 0
            p = self.players[pid]
            try:
                self.current_pid = pid
                p.play_round(self.clock.current_turn_number())
            except PlayerBannedException as e:
                l("Player", pid, "is being banned.")
                # self.game.loser = e.player
                # This is a quick and dirty fix, @TODO
                self.banned_players.append(pid)
            
            # This displays the state of the game
            l(self.game)

            self.clock.tick()
            if self.clock.is_over():
                print "Game Over"
                return False
        return True

    def make_transaction(self, **kwargs):
        d("make_transaction()")
        if self.current_player_transaction_attempts > self.TRANSACTION_ATTEMPTS_QUOTA:
            raise PlayerBannedException("Attempted to many transactions.")
        self.current_player_transaction_attempts += 1
        try:
            type_str = kwargs['type']
            args = kwargs['args']
        except KeyError as e:
            d(e)
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