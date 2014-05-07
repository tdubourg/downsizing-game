#!/usr/bin/python

from judge import Judge
from clock import Clock
from player import Player

from transactions import Resources

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
        self.players_ids = range(number_of_players)
        starting_resources = {}
        for r in Resources:
            starting_resources[r] = 100  # TODO: This is temporary, add some config / constants and implement properly later
        # Note: passing a copy of the dictionaries, as we do not want players to share anything...
        self.players = [Player(i, self.players_ids, dict(starting_resources), dict(self.j.interface)) for i in self.players_ids]
        print "Initialized players:", self.players
        self.players_resources = [dict(starting_resources) for _ in self.players_ids]
        self.j.players = self.players

    def start(self):
        # Play until the juding stops the game or until the game time is over
        while self.j.play_round():
            pass

    def __str__(self):
        return "\n".join(["Player %s %s" % (pid, str(self.players_resources[pid])) for pid in self.players_ids])

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
