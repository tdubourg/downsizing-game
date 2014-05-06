class Player(object):
    def __init__(self, player_id, judge):
        super(Player, self).__init__()
        self.player_id = player_id
        self.judge = judge

    def play_round(self):
        print "Player", self.player_id, "here, I'm playing, yay!"