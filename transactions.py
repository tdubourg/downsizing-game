class BaseTransaction(object):
    """Base class for a transaction"""
    def __init__(self, player_from, player_to):
        super(BaseTransaction, self).__init__()
        self.player_from = player_from
        self.player_to = player_to
    
    def is_valid(self):
        """ Returns True if the transaction is valid, false else"""
        raise NotImplementedError()