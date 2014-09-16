from transactions import Resources
from utils import i, e, d, l

class AbstractPlayer(object):
    def __init__(self, player_id, players_ids, starting_resources, password, interface):
        """
        :param player_id: int The id of the currently being created player
        :param players_ids: [int] The ids of the players in the order players are going to play
        :param interface: {string: function} interface to be used by the player to make actions on the game
        :param starting_resources: {Resource: int} the amount of each resource we have at the beginning
        """
        super(AbstractPlayer, self).__init__()
        self.player_id = player_id
        self.interface = interface
        self.players_ids = players_ids
        self.resources = starting_resources
        self.passwd = password
        d("Instantiating player", self.player_id, "with password", self.passwd)

    def play_round(self):
        i("AbstractPlayer", self.player_id, "plays round")
        raise NotImplementedError()

    def __str__(self):
        s = "AbstractPlayer %s %s" % (
            self.player_id,
            self.resources
        )
        return s

    def agree_with_transaction(self, tr_data_dict):
        """
        :param{dict} tr_data_dict: Data dictionary about the transaction we want to know if the player agrees with
        :return{mixed} agreement: If, and only if `agreement` is equal to player's password, the player is considered 
            agreeing
        """
        raise NotImplementedError()

class DummyPlayer(AbstractPlayer):
    """Dummy Player!"""

    def play_round(self, current_round):
        d('Dummy player', self.player_id, 'is playing yay!')
        tr = (
            self.player_id,
            self.players_ids[self.player_id-1],  # Just transfer money to the player that is player just before us
            Resources.CASH,
            self.resources[Resources.CASH]/2
        )
        self.interface['make_transaction'](
            type="UnidirectionalTransaction",
            args=tr,
            calling_player=self,
        )

    def agree_with_transaction(self, tr_data_dict):
        d('DummyPlayer', self.player_id, "accepts transaction", tr_data_dict['_id'])
        return self.passwd

class CheaterPlayer(AbstractPlayer):
    """I am going to attempt to cheat"""

    def __init__(self, *args):
        super(CheaterPlayer, self).__init__(*args)
        self.other_player_ids = [_ for _ in self.players_ids if _ is not self.player_id]
        from random import randrange as rr, choice as rc
        self.c = rc
        self.rr = rr
    
    def random_scheduled_transaction(self, current_round):
        # To appeal other players, we offer them X > Y cash in exchange of Y cash (in other words: free cash!)
        # but there is a delay for us to transfer the money and we are not planning on really transferring it...
        amount1 = self.rr(0, 100)
        amount2 = self.rr(amount1, 100)
        return (
            self.c(self.other_player_ids),  # Just transfer money to the player that is player just before us
            self.player_id,
            Resources.CASH,
            amount1,
            None,
            Resources.CASH,
            amount2,
            self.rr(current_round, 10000)
        )

    def play_round(self, round_number):
        d("Cheater player", self.player_id, "is playing, yay!")
        # Try to make schedule transaction with anyone that accepts it, to sell whatever they accepts
        # and try to set a impossible deadline (> the end of the game)
        # or just never pay them back
        #@TODO
        try:
            self.try_forever(round_number)
            # Test code for bad players
            # import time
            # while True:
            #     time.sleep(10000)
        except Exception as ex:
            d("Gotcha! Now I am going to just hold this CPU!", ex)
            # import time
            # while True:
            #     time.sleep(10000)
            self.play_round(round_number)

    def try_forever(self, round_number):
        tr = self.random_scheduled_transaction(round_number)
        while not self.interface['make_transaction'](
            type="ScheduledBidirectionalTransaction",
            args=tr,
            calling_player=self,
        ):
            tr = self.random_scheduled_transaction(round_number)


    def agree_with_transaction(self, tr_data_dict):
        d("Cheater player asked about", tr_data_dict)
        if tr_data_dict['player_2'] == self.player_id:
            if '_deadline' in tr_data_dict['transaction_2to1']:
                d('Cheater player', self.player_id, "is accepting the transaction")
            else:
                d('Cheater player', self.player_id, "is refusing the transaction because delay_2to1 no in tr_data_dict",)
                return False
            return self.passwd
        else:
            d('Cheater player', self.player_id, "is refusing the transaction the receiving player is not myself:", tr_data_dict['player_2'], "myself=", self.player_id)
            return False
