from transactions import *
from transactions import Resources
from utils import i, e, d

class AbstractPlayer(object):
    def __init__(self, player_id, players_ids, starting_resources, interface):
        """
        :param player_id: int The id of the currently being created player
        :param players_ids: [int] The ids of the players in the order players are going to play
        :param interface: {string: function} interface to be used by the player to make actions on the game
        :param starting_resources: {Resource: int} the amount of each resource we have at the beginning
        """
        super(AbstractPlayer, self).__init__()
        self.player_id = player_id
        self.interface = interface
        self.players_ids = players_ids
        self.resources = starting_resources

    def play_round(self):
        i("AbstractPlayer", self.player_id, "plays round")
        raise NotImplementedError()

    def __str__(self):
        s = "AbstractPlayer %s %s" % (
            self.player_id,
            self.resources
        )
        return s

class DummyPlayer(AbstractPlayer):
    """Dummy Player!"""

    def play_round(self, current_round):
        d('Dummy player', self.player_id, 'is playing yay!')
        tr = UnidirectionalTransaction(
            self.player_id,
            self.players_ids[self.player_id-1],  # Just transfer money to the player that is player just before us
            Resources.CASH,
            self.resources[Resources.CASH]/2
        )
        self.interface['make_transaction'](tr)

class CheaterPlayer(AbstractPlayer):
    """I am going to attempt to cheat"""

    def __init__(self, *args):
        super(CheaterPlayer, self).__init__(*args)
        self.other_player_ids = [_ for _ in self.players_ids if _ is not self.player_id]
        from random import randrange as rr, choice as rc
        self.c = rc
        self.rr = rr
    
    def random_scheduled_transaction(self, current_round):
        # To appeal other players, we offer them X > Y cash in exchange of Y cash (in other words: free cash!)
        amount1 = self.rr(0, 1000000)
        amount2 = self.rr(amount1, 1000000)
        return ScheduledBidirectionalTransaction(
            self.c(self.other_player_ids),  # Just transfer money to the player that is player just before us
            self.player_id,
            Resources.CASH,
            amount1,
            None,
            Resources.CASH,
            amount2,
            self.rr(current_round, 10000)
        )

    def play_round(self, round_number):
        # Try to make schedule transaction with anyone that accepts it, to sell whatever they accepts
        # and try to set a impossible deadline (> the end of the game)
        # or just never pay them back
        #@TODO
        tr = self.random_scheduled_transaction(round_number)
        while not self.interface['make_transaction'](tr):
            tr = self.random_scheduled_transaction(round_number)
