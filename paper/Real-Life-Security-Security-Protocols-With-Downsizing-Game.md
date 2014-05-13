Real Life Security
===================
Security Protocols
===================
_Case Study with the Downsizing Game_
-----------------------------------


### Game initialization
    Game::init
        self.clock = initialize_clock()
        self.judge = initialize_judge
        decide_of_player_ids()
        self.players_starting_resources = allocate starting resources storage structure for every player id
        self.players = instantiate every player with a player id and a copy of its starting resources data and a copy of its allowed "interface" (set of functions)
        self.judge.setPlayers(self.players)


### Pseudo-code of a round:
    Game::play
        while self.judge.play_round():
            pass

    Judge::play_round
        for pid in self.game.players_ids:
            p = self.players[pid]
            try:
                self.current_pid = pid
                p.play_round()
            except PlayerKilledException as e:
                self.game.loser = e.player
                return False
            self.clock.tick()
            if self.clock.is_over():
                return False
            return True
