Latex input:        mmd-article-header
author:             Théo Dubourg
Title:              Real Life Security - Security Protocols
Subtitle:           Case Study with the Downsizing Game
Base Header Level:  2
documentclass:      llncs
latex input:        mmd-article-begin-doc

<!-- \nonstopmode -->
<!--\begin{abstract} -->
Real life security use cases often include multiple parties talking to each other and making basic contracts between each other.
A contract can take several forms: A contract between two programs about how they are going to communicate,  a contract between two business men about a deal between their respective companies,  etc. . 
In this paper, we are going to focus on contracts that can be modeled as _transactions_ sequences.
More specifically, we are going to do a case study using the Downsizing Game invented by <!-- \cite{downgame} -->.
The Downsizing Game puts in place multiple players that are all pursuing the same goal of maximizing their own profit while trying to lower the one of the other ones in order to either make the other ones lose the game or win the game themselves.
Players can make transactions between each other in order to trade every sort of resources that is available in the game.
The goal of the case study is to see what are the steps to put in place a judging party that will enforce security protocol rules and make sure that all participants of an exchange, here players of the game, respect the rules, and punish them in case they do not. Thorough our work setting up such a system and environment, we will report on the issues we face, the solution we find and the decision we make with the justifications for such choices.

<!--\keywords{security, security protocols} -->
<!--\end{abstract} -->

# Introduction

## The Downsizing Game
The Downsizing Game puts in place multiple players that are all pursuing the same goal of maximizing their own profit while trying to lower the one of the other ones and in order to either make the other ones lose the game or win the game themselves. Players also have to gain the maximum amount of "votes" in order to win the game.

Players can make transactions between each other in order to trade every sort of resources that is available in the game: Money, trust, loyalty, and votes.
Every given amount of time, a _voting round_ takes places. On voting rounds, _all_ players should vote for _another_ player.

### Rules
The Downsizing Game rules are stated as follows:

- The game has a fixed length, defined in number of rounds.
- A fixed number of players are in the game.
- Every player is given a million units of the game currency (let us call it dollars) at the beginning of the game.
- At the end of the game, every player must return the original one million dollars that she was given in the beginning,  she can keep the remainder of the money for her.
- If players cannot give back the entire amount of money that they were given in the beginning, they have contracted a debt that they will have to reimburse.
- Players can make transactions between each other about every available resource in the game.
- A judging party overlooks at the game manages transaction,  ensuring their validity and preventing players from cheating.
- All players must vote on voting rounds.
- Players can not vote for themselves.
- At the end of the game, the player with the most votes wins. The one with the least votes loses.

### Definitions

#### Current player
Players play on a turn-by-turn basis. We will call _current player_ the player of which it is currently the turn. The current player is the only one that can make calls to the judging party's interface.

#### Rounds
A _round_ is an atomic unit of time in the game. A round can thus not be divided into subrounds. A round passes everytime the following actions are executed:

- A transaction is applied
- Changing the current player
- Applying the result of a voting round (see after)

#### Voting rounds
A voting round is a round where, __before__ any is taken (before even the current player plays), all players will be asked to vote according with the game's rules.

#### Cheater
A cheater is a player that breaks a game's rule. Cheaters are immediately killed and thus removed from the game. If,  at the moment they are killed they owe some resources to another player,  the remaining resources of the killed player will be transferred to the one they were owed to,  up the owed amount,  and up to the remaining balance of this resource on this killed player account.
If they owe resources to multiple players. The judging party will try to give the remaining balance amount to "loaners players" in historical order. [note: Better solution?  If we want to divide it equally we need to do it with some sort of incremental algorithm: first try to divide equally,  then,  sum up the amount of money that remain after taking into account the exact debt amounts,  in case any debt amount was smaller than the balance divided equally,  then re-directed this balance equally,  and so on until there is either no debt left or no money left...]

#### Resources

A _resource_ is a quantity that is allowed to be traded by the judging party.

In our case study, the set of resources will be fixed at the beginning of the game, to:

- Trust
- Loyalty
- Cash / money / currency
- Voting promises

However, a more complex scenario is to give players an interface to declare the tradable resources they have at the judging party. Such an interface would basically take as argument the name of the resource and the original balance / initial quantity of this resource that the player possesses, so that the judging party can check, when validating transactions, that the player is not making up new amounts of its self-made resource between every round.

Such study is left for future work but would allow to model real life trade where businesses might have exclusive resources that they are alone to possess, compared to everyone trading the same resources.

#### Amount
An _amount_ is a defined, positive integer, quantity of a resource.

#### Transactions
A _transaction_ is one or multiple transfer(s) _fixed amounts_ of resources between two _identified / authenticated_ players.

A transaction can either be unidirectional, that is to say, a player transfers resource to another player and that is all,  or bidirectional. In the latter case, two players transfer resources to each other.  

A bidirectional transaction is _composed_ of two unidirectional transactions.

#### Immediate transactions
_Immediate_ transaction are the basic transactions: As soon as the transaction is validated, the transfer(s) of resources is/are applied. There can be no other interaction, nothing else can happen in the game between validation and application of the transaction.

A a consequence, when a player agrees on an _immediate_ transaction, she is assured that the transaction will be fulfilled if it's validated by the judging party.

#### Delayed / scheduled transactions
_Scheduled_ or _delayed_ transactions are transaction where some transfer(s) of resources is/are not immediate.

A delayed transaction is a transaction with an additional information about an absolute game time unit. The amount to be transferred in this _delayed_ transaction has to be completed (strictly) _before_ this absolute game time.

When the game's clock ticks to this absolute time unit, it will tell the judge that there is some delayed transaction that should be checked for having been completed. The judging party will then check if the transactions has been completed by the players participating in the scheduled transaction. If the player that was supposed to transfer the resources did not transfer the exact amount of resources it was supposed to, this player will be considered as a cheater.

Just like immediate transactions, delayed transactions can be either _unidirectional_ or _bidirectional_.
A bidirectional transaction is said to be _delayed_ or _scheduled_ if and only if at least one of the two unidirectional transactions is it composed of, is a delayed transaction.

<!-- 
%# Related work... ?
%
%We're inventors! We do not need HISTORY!

-->

# Experimental work / Implementation

## Game flow

#### Rounds
On **every round**, the judging party will always check for completeness of scheduled transaction **before** any other action is taken, including before the current player plays.

#### Voting rounds

On voting rounds, the judging party will ask for players to vote.

Players should vote immediately, no delay is given. Players should vote according to the rules and they should respect any official vote promise agreement they made via a transaction.

The judging party, for every player's vote, will check that it respects the rule, and then check that it respects vote promises that have been registered via previous transaction. To summerize, a voting round go through the following steps, in order:

1. Check for scheduled transaction completeness, as for any round
2. Ask every player, one by one, to vote
3. Validate vote according to the rules and to the history of transactions
4. Either accept the vote, of qualify voting player as a cheater if the vote was not valid
5. Ask next player and go 3. and 4. again until all players have voted
6. Publicly disclose the new number of votes that every player received.
7. Allow the current player to play


## Scheduled transactions implementation

System of transaction identifiers, "sub-transaction" flag + identifier of "parent" transaction, sum over all the transactions...

## Miscellaneous security measures

### Python-related security measures

As _final_ objects do not exist in Python, we make sure critical objects are not accessible by the players.

For instance, the judging party object is not passed to the players. only pointers to its methods. Thus, players can still call methods of the juding party but cannot override any attribute of the judging party's instance, like resources balances, for instance.

Another example is transactions objets. Transactions are instantiated by the player and passed to the judge. A player could try to change the transaction object between it is validated and applied, thus making the transaction applied without having been checked on the values it has when it is applied. In order to mitigate this, we make a copy of the transaction passed by the player. The player thus do not have a pointer to the object we are going to use anymore. We can then validate and apply the transaction without risks of tampering.

# Appendix

### Game initialization
    Game::init
        self.clock = initialize_clock()
        self.judge = initialize_judge()
        decide_of_player_ids()
        self.players_starting_resources =   allocate starting resources 
                                            storage structure for every 
                                            player id
        self.players = instantiate every player with a player id 
                       and a copy of its starting resources data 
                       and a copy of its allowed "interface" (set of functions)
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
\url{http://en.wikipedia.org/wiki/Liar_Game#Revival_Round:_Downsizing_Game}
\end{thebibliography}
-->
<!-- \end{document} -->