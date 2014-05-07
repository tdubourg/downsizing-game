from enum import Enum

Resources = Enum("CASH", "VOTE", "TRUST")

class BaseTransaction(object):
    """Base class for a transaction"""
    def __init__(self, player_from, player_to, resource_type, amount):
        """
        :param player_from: int
        :param player_to: int
        :param resource_type: Resource
        :param amount: int
        """
        super(BaseTransaction, self).__init__()
        self.player_from = player_from
        self.player_to = player_to
        self.resource_type = resource_type
        try:
            self.amount = int(amount)
        except ValueError:
            self.amount = -1  # So that the transaction is invalid
    
    def is_valid(self, judge):
        """ Returns True if the transaction is valid, false else"""
        if self.resource_type not in Resources:
            return False
        if self.amount < 0:
            return False
        if not judge.is_valid_player(self.player_from) or not judge.is_valid_player(self.player_to):
            return False
        if not judge.has_enough_resource(self.player_from, self.resource_type, self.amount):
            return False
        return True

    def apply(self, players_resources):
        players_resources[self.player_from][self.resource_type] -= self.amount
        players_resources[self.player_to][self.resource_type] += self.amount

class ScheduledTransaction(BaseTransaction):
    def __init__(self, player_from, player_to, resource_type, amount, ):
        super(ScheduledTransaction, self).__init__(player_from, player_to, resource_type, amount)

    def is_valid(self, judge):
        # First, execute parent's checks
        if not super(ScheduledTransaction, self).is_valid(judge):
            return False
        # If nothing went wrong, execute additional checks
        # We are going to check that the player can indeed play before the round it specified