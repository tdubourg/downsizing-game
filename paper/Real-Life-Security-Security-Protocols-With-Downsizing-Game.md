Latex input:        mmd-article-header
Title:              Real Life Security - Security Protocols
Subtitle:           Case Study with the Downsizing Game
Base Header Level:  2  
documentclass:      llncs
latex input:        mmd-article-begin-doc

<!-- 
\author{Théo Dubourg \and Eric Rothstein}
-->
<!-- \begin{abstract} -->
<!-- 
% The abstract should summarize the contents of the paper
% using at least 70 and at most 150 words. It will be set in 9-point
% font size and be inset 1.0 cm from the right and left margins.
% There will be two blank lines before and after the Abstract. \dots
% \keywords{computational geometry, graph theory, Hamilton cycles}
-->
Real life security use cases often include multiple parties talking to each other and making basic contracts between each other.
A contract can take several forms: A contract between two programs about how they are going to communicate,  a contract between two business men about a deal between their respective companies,  etc. . 
In this paper, we are going to focus on contracts that can be modeled as _transactions_ sequences.
More specifically, we are going to do a case study using the Downsizing Game invented by <!-- \cite{downgame} -->.
The Downsizing Game puts in place multiple players that are all pursuing the same goal of maximizing their own profit while trying to lower the one of the other ones in order to either make the other ones lose the game or win the game themselves.
Players can make transactions between each other in order to trade every sort of resources that is available in the game: Money, trust, loyalty, and votes.
The goal of the case study is two see what are the step to put in place a judging party that will enforce security protocol rules and make sure that all participants of an exchange, here players of the game,  respect the rules,  and punish them in case they do not. Thorough our work setting up such a system and environment,  we will report on the issues we face, the solution we find and the decision we make with the justifications for such choices.

<!-- \end{abstract} -->

# Introduction

## The Downsizing Game
The Downsizing Game puts in place multiple players that are all pursuing the same goal of maximizing their own profit while trying to lower the one of the other ones and in order to either make the other ones lose the game or win the game themselves. Players also have to gain the maximum amount of "votes" in order to win the game.

Players can make transactions between each other in order to trade every sort of resources that is available in the game: Money, trust, loyalty, and votes.
Every given amount of time, a _voting round_ takes places. On voting rounds, _all_ players should vote for _another_ player.

### Rules
The Downsizing Game rules are stated as follows:

- The game has a fixed length,  defined in number of rounds
- A fixed number of players are in the game
- Every player is given a million dollars at the beginning of the game
- At the end of the game,  every player must return the original one million dollars that she was given in the beginning,  she can keep the remainder of the money for her.
- If players cannot give back the entire amount of money that they were given in the beginning, they have contracted a debt that they will have to reimburse.
- Players can make transactions between each other about mostly every available resource in the game.
- A judging party overlooks at the game manages transaction,  ensuring their validity and preventing players from cheating.

### Definitions

#### Cheater
A cheater is a player that breaks a game's rule. Cheaters are immediately killed and thus removed from the game. If,  at the moment they are killed they owe some resources to another player,  the remaining resources of the killed player will be transferred to the one they were owed to,  up the owed amount,  and up to the remaining balance of this resource on this killed player account.
If they owe resources to multiple players. The judging party will try to give the remaining balance amount to "loaners players" in historical order. [note: Better solution?  If we want to divide it equally we need to do it with some sort of incremental algorithm: first try to divide equally,  then,  sum up the amount of money that remain after taking into account the exact debt amounts,  in case any debt amount was smaller than the balance divided equally,  then re-directed this balance equally,  and so on until there is either no debt left or no money left...]

#### Transaction
A _transaction_ is [copy definition from Google docs]
A transaction can either be unidirectional, that is to say,  a player transfers resource to another player and that is all,  or bidirectional.  The latter case,  two players transfers resources to each other.  A bidirectional transaction is composed of two unidirectional transactions.

#### Delayed / scheduled transactions
Scheduled transactions are transaction where the transfer of resources is not immediate.
A delayed transaction is a transaction with an additional information about an absolute game time unit.
When the game's clock ticks to this absolute time unit,  it will tell the judge that there is some delayed transaction that should be checked for being completed. The judging party will then check if the transactions has been completed by the players participating in the schedule transaction. If the player that was supposed to transfer the resources did not transfer the exact amount of resources it was supposed to,  this player will be considered as a cheater.
Just like immediate transactions, delayed transactions can be either unidirectional or bidirectional.
A bidirectional transaction is said to be _delayed_ or _scheduled_ if and only if at least one of the two unidirectional transactions is it composed of,  is a delayed transaction.

# Related work... ?

# Experimental work

# Appendix

### Game initialization
    Game::init
        self.clock = initialize_clock()
        self.judge = initialize_judge()
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

# References

<!-- 
\begin{thebibliography}{1}
\bibitem{downgame}
Shinobu Kaitani:
Downsizing Game, Liar Game
\end{thebibliography}
-->