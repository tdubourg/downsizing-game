from config import ALLOWED_TRANSACTIONS_PER_ROUND
from transactions import BaseTransaction

class PlayerKilledException(Exception):
    """
    This exception will be raised by the judge when he kills a player. 
    It holds the player that has been killed
    """
    def __init__(self, player):
        super(PlayerKilledException, self).__init__()
        self.player = player

class Judge(object):
    """
    The Judge is the one ruling the game. It allows or not actions to be taken, 
    and kills misbehaving players.
    """
    def __init__(self, game, clock):
        super(Judge, self).__init__()
        self.clock = clock
        self.players = []
        self.game = game
        self.current_pid = None
        self.interface = {"make_transaction": self.make_transaction}

    def play_round(self):
        for pid in self.game.players_ids:
            p = self.players[pid]
            try:
                self.current_pid = pid
                p.play_round()
            except PlayerKilledException as e:
                self.game.loser = e.player
                return False
            print self.game
            self.clock.tick()
            if self.clock.is_over():
                print "Game Over"
                return False
            return True

    def make_transaction(self, transaction):
        try:
            if not isinstance(transaction, BaseTransaction):
                return False
            if transaction.player_from is not self.current_pid:
                return False
            else:
                valid_transaction = transaction.is_valid(self)
                if valid_transaction[0] is True:
                    # Note that there will not be any concurrent modification between the check of the transaction and 
                    print "Transaction is valid, applying it"
                    valid_transaction[1].apply(self.game.players_resources)
                    # Transaction is applied, tick the clock
                    self.clock.tick()
                    return True
                # The transaction was not valid
                return False
        except:
            # If anything failed, the transaction should not be accepted
            return False
    def is_valid_player(self, pid):
        return pid in self.game.players_ids

    def has_enough_resource(self, pid_from, rtype, amount):
        return self.game.players_resources[pid_from][rtype] >= amount