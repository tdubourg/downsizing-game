#!/usr/bin/python

from judge import Judge
from clock import Clock
from player import Player

class Game(object):
    """
    Game class creates players, initializes the game, ticks the clock, activate the judge, 
    and finishes the game
    """
    def __init__(self, number_of_players, maximum_number_of_turns, turns_between_voting_rounds):
        super(Game, self).__init__()
        self.number_of_players = number_of_players
        self.clock = Clock(maximum_number_of_turns, turns_between_voting_rounds)
        self.j = Judge(self, self.clock)
        self.players = [Player(i, self.j) for i in range(number_of_players)]
        self.j.players = self.players

    def start(self):
        # Play until the juding stops the game or until the game time is over
        while self.j.play_round() and not self.clock.is_over():
            pass

if __name__ == '__main__':
    import sys
    n = len(sys.argv)
    if n is not 4:
        print "Usage: ./game.py number_of_players maximum_number_of_turns turns_between_voting_rounds"
        sys.exit()

    g = Game(
        number_of_players=int(sys.argv[1]),
        maximum_number_of_turns= int(sys.argv[2]),
        turns_between_voting_rounds=int(sys.argv[3])
    )
    print "Starting game..."
    g.start()
    print "Game Over"
