from enum import Enum
from utils import i, d

Resources = Enum("CASH", "VOTE", "TRUST")

class AbstractTransaction(object):
    """Transaction interface"""
    last_id = -1

    @staticmethod
    def next_id():
        # @TODO thread safety?
        AbstractTransaction.last_id += 1
        return AbstractTransaction.last_id

    def __init__(self):
        super(AbstractTransaction, self).__init__()
        self._id = AbstractTransaction.next_id()
    
    def is_valid(self, judge):
        """
        Is the transaction valid?
        :return (bool, AbstractTransaction)
            (True, CopyOfTheTransaction)    if the transaction is valid
            (False, None)                   if the transaction is invalid

            The copy of the transaction is to be used to avoid the transaction being modified between validation 
            and application
        This is a non-abstract method
        """
        cl = self.clone()
        valid = cl._is_valid(judge)
        if valid:
            return (True, cl)
        else:
            return (False, None)

    def apply(self, players_resources):
        """
        Apply the transaction to the players' resources
        Abstract method. Has to be overriden by children
        """
        raise NotImplementedError()

    def clone(self):
        """
        Returns a clone of current object. A clone is a 1-to-1 copy
        of the current object.
        Abstract method
        """
        raise NotImplementedError()

    def _is_valid(self, judge):
        """
        Internal use only. Validates in-place the current transaction
        This is not a private method, but a protected abstract one.
        It has to be implemented by children, but will be called
        by parent's is_valid() method unless is_valid() is overriden
        """
        raise NotImplementedError()

class UnidirectionalTransaction(AbstractTransaction):
    """Base class for a transaction"""
    def __init__(self, player_from, player_to, resource_type, amount):
        """
        :param player_from: int
        :param player_to: int
        :param resource_type: Resource
        :param amount: int
        """
        super(UnidirectionalTransaction, self).__init__()
        self.player_from = player_from
        self.player_to = player_to
        self.resource_type = resource_type
        try:
            self.amount = int(amount)
        except ValueError:
            self.amount = -1  # So that the transaction is invalid
    
    def _is_valid(self, judge):
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
        i("Transaction", self._id, "is being applied.")
        players_resources[self.player_from][self.resource_type] -= self.amount
        players_resources[self.player_to][self.resource_type] += self.amount

    def clone(self):
        return UnidirectionalTransaction(self.player_from, self.player_to, self.resource_type, self.amount)

class BidirectionalTransaction(AbstractTransaction):
    """Bidirectional transaction"""
    def __init__(self, player_1, player_2, rtype_1to2, amount_1to2, rtype_2to1, amount_2to1):
        super(BidirectionalTransaction, self).__init__()
        self.transaction_1to2 = UnidirectionalTransaction(player_1, player_2, rtype_1to2, amount_1to2)
        self.transaction_2to1 = UnidirectionalTransaction(player_2, player_1, rtype_2to1, amount_2to1)

    def _is_valid(self, judge):
        # Note: We already recreated the unidirectional internal transactions so we use the no-copy/in-place
        # validation method
        return self.transaction_1to2._is_valid(judge) and self.transaction_2to1._is_valid(judge)

    def apply(self, players_resources):
        self.transaction_1to2.apply(players_resources)
        self.transaction_2to1.apply(players_resources)

    def clone(self):
        return BidirectionalTransaction(
            self.transaction_1to2.player_from,
            self.transaction_1to2.player_to,
            self.transaction_1to2.resource_type,
            self.transaction_1to2.amount,
            self.transaction_2to1.resource_type,
            self.transaction_2to1.resource_type
        )


        
class ScheduledTransaction(UnidirectionalTransaction):
    def __init__(self, player_from, player_to, resource_type, amount, ):
        super(ScheduledTransaction, self).__init__(player_from, player_to, resource_type, amount)

    def is_valid(self, judge):
        # First, execute parent's checks
        if not super(ScheduledTransaction, self).is_valid(judge):
            return False
        # If nothing went wrong, execute additional checks
        # We are going to check that the player can indeed play before the round it specified