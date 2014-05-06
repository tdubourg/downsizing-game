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

    def play_round(self):
        for p in self.players:
            try:
                p.play_round()
            except PlayerKilledException as e:
                self.game.loser = e.player
                return False
            if self.clock.is_over():
                return False
        