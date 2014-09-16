#!/usr/bin/python

from judge import Judge
from clock import Clock
from player import DummyPlayer

from transactions import Resources

from utils import l
from player import DummyPlayer, CheaterPlayer

from random import choice
from utils import d, l, e

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
        from uuid import uuid4 as uuid
        self.passwords = {i: uuid() for i in self.players_ids}
        self.players_at_game_start = [self.player_instance(
            i,
            self.players_ids,
            dict(starting_resources),
            self.passwords[i],
            dict(self.j.interface)
        ) for i in self.players_ids]
        l("Initialized players:", self.players_at_game_start)
        self.players_resources = [dict(starting_resources) for _ in self.players_ids]
        self.j.players = list(self.players_at_game_start)
        self.j.players_ids = list(self.players_ids)
        self.j.passwords = list(self.passwords)

    def player_instance(self, player_id, player_ids, starting_resources, judge_interface):
        # This is a local variable but for the sake of instantiating something that looks like a class instantiation
        # I am using class casing here
        PlayerClass = DummyPlayer if player_id % 2 else CheaterPlayer
        l("Instantiating player of type", PlayerClass)
        return PlayerClass(player_id, player_ids, starting_resources, judge_interface)

    def start(self):
        # Play until the judging stops the game or until the game time is over
        while self.j.play_round():
            pass

    def __str__(self):
        return "\n".join(["Player %s %s" % (pid, str(self.players_resources[pid])) for pid in self.players_ids])

if __name__ == '__main__':
    try:
        import sys
        n = len(sys.argv)
        if n is not 4:
            l("Usage: ./game.py number_of_players maximum_number_of_turns turns_between_voting_rounds")
            sys.exit()

        g = Game(
            number_of_players=int(sys.argv[1]),
            maximum_number_of_turns= int(sys.argv[2]),
            turns_between_voting_rounds=int(sys.argv[3])
        )
        l("Starting game...")
        g.start()
        input("Game is over, press enter to end process.")
        sys.exit()
    except Exception as ex:
        d("Exception??", ex)