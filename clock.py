class Clock(object):
    """The clock will be ticking and giving information about the advancement of the game"""
    def __init__(self, maximum_turns, turns_between_voting_rounds):
        super(Clock, self).__init__()
        self.maximum_turns = maximum_turns
        self.turns_between_voting_rounds = turns_between_voting_rounds
        self.__turn = 0

    def tick(self):
        self.__turn += 1

    def turn(self):
        return self.__turn

    def is_over(self):
        return self.__turn >= self.maximum_turns

    def is_voting_round(self):
        return self.__turn % self.turns_between_voting_rounds is 0

    def current_turn_number(self):
        return self.__turn