from transactions import BaseTransaction

class Player(object):
    def __init__(self, player_id, interface):
        super(Player, self).__init__()
        self.player_id = player_id
        self.interface = interface

    def play_round(self):
        print "Player", self.player_id, "here, I'm playing, yay!"
        tr = BaseTransaction(self, self)
        self.interface['make_transaction'](tr)