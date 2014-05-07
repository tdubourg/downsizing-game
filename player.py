from transactions import BaseTransaction
from transactions import Resources
class Player(object):
    def __init__(self, player_id, players_ids, starting_resources, interface):
        """
        :param player_id: int The id of the currently being created player
        :param players_ids: [int] The ids of the players in the order players are going to play
        :param interface: {string: function} interface to be used by the player to make actions on the game
        :param starting_resources: {Resource: int} the amount of each resource we have at the beginning
        """
        super(Player, self).__init__()
        self.player_id = player_id
        self.interface = interface
        self.players_ids = players_ids
        self.resources = starting_resources

    def play_round(self):
        print "Player", self.player_id, "here, I'm playing, yay!"
        tr = BaseTransaction(
            self.player_id,
            self.players_ids[-1],
            Resources.CASH, self.resources[Resources.CASH]/2
        )
        self.interface['make_transaction'](tr)

    def __str__(self):
        print "Player", self.player_id
        print self.resources