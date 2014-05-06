from config import ALLOWED_TRANSACTIONS_PER_ROUND

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
        self.current_player = None

    def play_round(self):
        for p in self.players:
            try:
                self.current_player = p
                p.play_round()
            except PlayerKilledException as e:
                self.game.loser = e.player
                return False
            self.clock.tick()
            if self.clock.is_over():
                print "Game Over"
                return False
            return True

    def make_transaction(self, transaction):
        if transaction.player_from is not self.current_player:
            return False
        elif transaction.is_valid() is True:
            # Transaction is valid, tick the clock
            self.clock.tick()
            return True
        # The transaction was not valid
        return False