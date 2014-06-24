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
