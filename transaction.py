class BaseTransaction(object):
    """Base class for a transaction"""
    def __init__(self, judge):
        super(BaseTransaction, self).__init__()
        self.judge = judge
    
    def is_valid(self):
        """ Returns True if the transaction is valid, false else"""
        raise NotImplementedError()
