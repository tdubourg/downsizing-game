Latex input:        mmd-article-header
author:             Théo Dubourg
Title:              Real Life Security - Security Protocols
Subtitle:           Case Study with the Downsizing Game
Base Header Level:  2
documentclass:      llncs
latex input:        mmd-article-begin-doc

<!--
\nonstopmode
\begin{abstract}
--> 

Real life security use cases often include multiple parties talking to each
other and making basic contracts between each  other. A contract can take several forms: A contract between two programs
about how they are going to communicate,  a contract  between two business men about a deal between their respective
companies,  etc. .  In this paper, we are going to focus on contracts that can be modeled as _transactions_ sequences. More
specifically, we are going to do a case study using the Downsizing Game invented by <!-- \cite{downgame} -->. The Downsizing
Game puts in place multiple players that are all pursuing the same goal of maximizing their own profit. Players can make
transactions between each other in order to trade every sort of resources that is available in the game. The goal of the case
study is to see what are the steps to put in place a judging party that will enforce security protocol rules and what are the
security requirements we can add on top of the functional requirements. Thorough our work setting up such a system and
environment, we will report on the issues we face, the solutions we find and the decision we make with the justifications 
for such choices.

<!--
\keywords{security, security protocols}
\end{abstract}
-->

# Introduction

## The Downsizing Game 
The Downsizing Game puts in place multiple players that are all pursuing the same goal of maximizing their own profit.
Players also have to gain the maximum amount of "votes" in order to win the game.

Players can make transactions between each other in order to trade every sort of resources that is available in the game: 
Money, trust, loyalty, and votes.

Every 100 rounds, a _voting round_ takes places. On voting rounds, _all_ players should vote for _another_ player. We will 
describe the game in details in [][gamerules]

Although it may seem like a simple game, players behaviour can largely vary between each other, which makes ensuring that
everything goes as it should not completely trivial.

## Objective

The objective, in this paper, is to use the Downsizing Game as an example to study the process of a small-sized 
software development project that would start with functional requirements and then add security requirements.

We want to build a platform to allow players to play the Downsizing Game but we do not want any cheaters.

Thorough our design and implementation, we will report on the issues we faced and the solutions and decisions we took to 
overcome them, along with the justifications of such choices. We think this material can be of some interest to computer 
science students or beginners in providing them with a concrete and detailed example.

The work will indeed be split into 3 main steps:

1. Functional requirements: design & implementation
2. Security requirements: design & implementation 
3. Comparison against coding guidelines

The second step of the work will bring security requirements that we found to be necessary to be added by intuition. By 
simply thinking about the different cases that will be faced in the game and what could be attempted by player to cheat on 
the game and what should be done to ensure those cheating attempts will fail.

In the last step, we will compare our already security-aware application to coding guidelines and conclude on what we were
able to fulfill or not of those guidelines, what applies here and what does not, and what following those guidelines would
have changed in the cases where the guidelines would not have been followed.

We will look at the last step as a partial answer to the question "How secure can I code?".

# Case Study [cs]

## Assumptions

In our design and implementation of the Downsizing Game, we will start from the following assumptions:

1. There is no communication layer between the different part of the game (e.g. : no networking)
2. Everything is happening in the same process on a single CPU machine. That is to say: only one instruction can be executed 
at a time, there is no parallelism/concurrency.
3. The technology used to develop the game prevents arbitrary memory from being read. A player program will thus only be 
allowed to access data from objects it has been given an explicit pointer and/or reference to.

The reason for working under those assumptions is that the focus here on the security of the interaction protocol between
players and the implementation of the judging party. A communication layer would bring with  it all sorts of communication-
related security concerns that are not of interest here. The same reason goes for parallelism  and/or concurrency.

## Functional Requirements

The functional requirements are the set of features that our instance of the Downsizing Game should implement/respect.

### Game's rules [gamerules]

The rules of our instance of the Downsizing Game will be stated as follows:

- The game has a fixed length of 1,000 rounds.
- 3 players participate in the game.
- Players can only participate once in the game.
- Every player is given a million units of the game currency (let us call it dollars) and a hundred of the other resources 
at the beginning of the game. [FIXME: The other resources start a 0 or 100? What does "buying some trust" actually mean?]
- At the end of the game, every player must return the original one million dollars that she was given in the beginning, 
she can keep the remainder of the money for her.
- At the end of the game, if players cannot give back the entire amount of money that they were given in the beginning, 
they have contracted a 
debt that they will have to reimburse.
- Players can make transactions between each other about every available resource in the game.
- A judging party enforces the game's rules and manages transactions, ensuring their validity and preventing players 
from cheating.
- There are 10 voting rounds: rounds 100, 200, 300, 400, 500, 600, 700, 900 and 1,000.
- All players must vote on voting rounds.
<!--% Note: I chose 1 vote because if we have 3 players and 2 votes, then they are forced to vote for everyone...-->
- Players must cast exactly 1 vote at every voting rounds.
- Players can not vote for themselves.
- Every time a player receives a vote, his _score_ increases by 1.
- At the end of the game, the player(s) with the highest score win(s). The one(s) with the lowest score lose(s).
- The winning player earns 1 million dollars.

<!-- 
\vspace{1\baselineskip}
-->
As a consequence of these rules, here are some examples of possible basic strategies:

- A player can try to get the maximum amount of votes, in order to be the winner, thus maximizing profit by getting the 
winning prize.
- A player can try to maximize its profit, without caring about votes. She will not win, but will still make profit out 
of the game, as she will keep the remainder of the money after giving back the original one million dollars.

### Definitions & needed features

#### Current player
Players play on a turn-by-turn basis. We will call _current player_ the player of which it is currently the turn.

#### Score

The _score_ of a player at a given round $r$ is the number of votes the player received until $r$.

#### Rounds

A _round_ is an atomic unit of time in the game. A round can thus not be divided into subrounds. A round passes every time 
any of the following actions is executed:

- A transaction is applied
- Changing the current player
- Applying the result of a voting round (see after)

#### Voting rounds

A voting round is a round where, **before** any action, all players will be asked to vote as described in the game's rules.

According to the definition of the rounds, no other action can be taken at during a voting round, as a round passes when
applying the result of a voting round.

#### Cheater

<!-- 
% Note: This is on the edge between security requirement and functional requirement. But I would still say it is a
% functional requirement because the concept of "cheater" by itself and the fact cheaters should be punished is
% necessary for the game itself, it does not, imho, represent a specific security check 
-->

A cheater is a player that breaks one or several game's rules. Cheaters are immediately killed and thus removed from the game. If, at the
moment they are killed they owe some resources to another player, the remaining resources of the killed player will be 
transferred to the one they were owed to, up the owed amount,  and up to the remaining balance of this resource on this 
killed player account.

If they owe resources to multiple players. The judging party will distribute the money proportionately, rounded to the 
closest integer. The exact formula is:

$$part\ of\ the\ remaining\ balance\ you\ get = round(\cfrac{total\ amount\ cheater\ owed\ to\ you}{total\ debt\ of\ the\ cheater})$$

#### Transactions

A _transaction_ is one or multiple transfer(s) of _fixed amounts_ of resources between two _identified/authenticated_
players. The player _sending_ the resource will later be referred to either as the _sending player_ or _paying player_ or
_payer_ or _sender_. The player _receiving_ the resource will later be referred to either as the _receiving player_ or 
_paid player_ or _payee_ or _recipient_.

A transaction can either be unidirectional, that is to say, a player transfers some resource to another player and that is
all, or bidirectional. In the latter case, two players transfer resources to each other.

A bidirectional transaction is composed (in the OOP meaning) of two unidirectional transactions. A bidirectional is **not**
a special unidirectional transaction (it does not inherit from it).

Every resource except _voting promises_ can be traded using a transaction. Voting promises have to be traded using 
_voting promises transactions_ [ ][votepromtrans]

#### Resources

A _resource_ is an integer quantity that the judging party allows to trade.
In our case study, the set of resources will be fixed at the beginning of the game, to:

- Trust
- Loyalty
- Cash/money/currency
- Voting promises

#### Amount
An _amount_ is a defined, positive integer, quantity of a single resource.

#### Immediate transactions

_Immediate_ transactions are the basic transactions: As soon as the transaction is validated, the transfer(s) of resources
is/are applied.

As a consequence, when a player agrees on an _immediate_ transaction, she is assured that the transaction will be fulfilled
if it's validated by the judging party.

#### Delayed/scheduled transactions

_Scheduled_ or _delayed_ transactions are transactions where some transfer(s) of resources is/are not immediate.

A delayed transaction is a transaction with an additional information about an **absolute game time unit**. The amount in this
_delayed_ transaction has to be completely transferred (strictly) _before_ this absolute game time unit.

Just like immediate transactions, delayed transactions can be either _unidirectional_ or _bidirectional_. A bidirectional
transaction is said to be _delayed_ or _scheduled_ if and only if at least one of the two unidirectional transactions it is
composed of, is a delayed transaction.

#### Voting promises transactions [votepromtrans]

Voting promises are a type of delayed transactions. Voting promises are promises that a given player will cast a given number
of votes to the _recipient_ of the transaction before a given absolute game's time unit.


#### Valid transaction 

A _transaction_ is said to be _valid_ if and only if: 

- Transaction does not break a game rule. 
- Transaction is able to be completed to the extent of the judging party’s knowledge. (e.g. : Enough money on the account, 
in case of an immediate money transfer).

A bidirectional transaction will be considered valid if both unidirectional transactions it is composed of are valid. If
any of them is not, then the bidirectional transaction is also invalid.


## Additional Security Requirements

Functional requirements now defined, we are going to define and describe _security requirements_ that are necessary to ensure
the players do not exploit singularities of the game in order to achieve behaviours that should not be achieved according to
the rules.

### Judging party exclusiveness aka turn-by-turn enforcement

The _current player_ is the only one that can make calls to the judging party's interface.
This is needed in order to prevent other players from trying to steal the CPU and make transactions on the transaction quota
of another player instead of their own quota.

<!-- 
% Note: Better solution?  If we want to divide it equally we need to do it with some sort of incremental algorithm: first 
% try to divide equally,  then,  sum up the amount of money that remain after taking into account the exact debt amounts,  
% in case any debt amount was smaller than the balance divided equally,  then re-directed this balance equally,  and so on 
% until there is either no debt left or no money left...
-->

### Immediate transactions: guaranteeing "immediateness" (atomicity) [immatom]

There should be no other interaction, no change to the state of the game should happen between validation and application of
an immediate transaction.

This is partially guaranteed by the assumptions of no parallelism/concurrency. Although, a player program could still manage
to steal the CPU (effectively pausing the judging party program's execution) and try to change the state of the game by
submitting other transaction for instance. A player could use such an attack to submit multiple transactions that will be
validated on the same balances, but executed on different balances.

To avoid this, we will make use of synchronization tools to only allow one concurrent execution of the judging party
program's code of validation and application of an immediate transaction. This can be materialized for instance by the use of
operating system's _mutex_ tools, but any other synchronization tool providing equal guarantees can be used too.

### Delayed/scheduled transactions completion

Delayed transactions are validated without the transfers of resources actually taking place and have a deadline for this
transfer to happen. It has to be checked that the transfer was indeed done strictly before the deadline.

When the game's clock ticks to this absolute time unit (the deadline), it will tell the judge that there is some delayed transactions that
should be checked for having been completed. The judging party will then check if the transactions have been completed by the
players participating in the scheduled transaction.  Checks for completion of delayed transaction will **always** be
performed **before any other action** can be taken in the current round. If the player that was supposed to transfer the
resources did not transfer the exact amount of resources it was supposed to, this player will be considered a cheater.

Note that in order to guarantee that the current player is not able to talk to the judging party before the end of the
delayed transactions checks, we will once more make use of synchronization tools, as in the case of  immediate transactions
[atomicity][immatom].

But in order to be able to tell the difference between transfers of resources related to new deals between two players and
transfers of resources related to completion of a scheduled/delayed transaction, we need an additional, special type of
transaction. We will call it "subtransaction".
<!-- 
\vspace{1\baselineskip}
-->
A **subtransaction** is an **immediate** transaction that contains an additional information about the delayed transaction
is it related to.

When the judging party has to check that the delayed transaction was indeed completed, it will go through all
subtransactions that were made since the round of the delayed transaction between the same two players and sum everything
up. The sum has to be **exactly** what was initially agreed in the delayed transaction. If and only if it is the case, 
then the transaction can be marked as completed.

### Players authentication

When creating a transaction, a player could provide false information about the participants in this transaction and thus
attempt to impersonate other players and make transactions on their behalf.

As a consequence, we need a mechanism to authenticate the players and be sure that the player who submitted a request in her
name, is indeed the player she is saying she is.

To authenticate the player, we will go for the simple use of a password. At the beginning of the game, every player will be
given a unique password that she will have to pass along with every call she does to the judging party's interface in order
to prove this call is coming from the player it is said it comes from.

When the judging party calls players itself, the authentication is assured as the judging party has direct pointers to every
players and those pointers cannot be tampered by the other players (as [per assumption 3][Assumptions])

### Transactions validation

When asked to perform a new transaction, the judging party will sequentially (in the order below) go through multiples steps, or checks.

At every step, if the check fails, the transaction is marked as not valid, and thus, refused.

#### Players mutual agreement

For any transaction validation, the first step that the judge will follow is to ask both involved players whether they
confirm that they agree with this transaction. Both players have to answer "yes" for this check to succeed.

#### Input validation
The judge will then perform rational checks. These checks are the following:

- Is the amount a **positive integer**? (avoiding resources "generation" with negative values, and rounding errors exploits
if we were to use real numbers)
- Is the amount smaller than the global amount of resources of this type in the entire game?
- In case of voting promise, is the amount smaller than the number of votes the player will be able to cast before the end 
of the game? (voting rounds multiplied by votes per player and per voting round)

#### Balance check

The judge will then check the balance of the player _from_ which the transfer is going to happen for the resource that is
going to be transferred.

In the case of immediate transactions, the judge checks. The balance has to be equal or greater to the amount of the
transaction.

In the case of scheduled transactions, the judge will not check the balance, as the player could have planned to make other
agreements with other players between the round where the current transaction is being validated and the round where the
payment deadline is set.

That means that a scheduled, or delayed transaction, is not safe by itself, as the judging party cannot guarantee that the
payment will be made. Mitigation/punishment in case of lack of payment will be described later.

### Voting rounds

On voting rounds, the judging party will ask players to vote.

Players should vote immediately, no delay is given. Players should vote according to the rules and they should respect any
official vote promise agreement they made via a transaction.

The judging party, for every player's vote, will check that it respects the rules, and will then check that it respects vote
promises that have been registered via previous transaction. To summarise, a voting round go through the following steps, in
order:

1. Check for scheduled transaction completeness, as for any round
2. Ask every player, one by one, to vote
3. Validate vote according to the rules and to the history of transactions
4. Either accept the vote, of qualify voting player as a cheater if the vote was not valid
5. Ask next player and go 3. and 4. again until all players have voted
6. Publicly disclose the new number of votes that every player received and their new score.
7. Allow the current player to play

[FIXME: Voting promises model: next round / versus a transaction generated by every vote]


## Miscellaneous security measures

### Python-related security measures

As _final_ objects do not exist in Python, we have to make sure critical objects are not accessible by the players.

For instance, the judging party object is not passed to the players, only pointers to its methods. Thus, players can still
call methods of the judging party but cannot override any attribute of the judging party's instance, like resources balances,
for instance.

Another example is transactions objects. Transactions are instantiated by the player and passed to the judge. A player could
try to change the transaction object between it is validated and applied, thus making the transaction applied without having
been checked on the attributes values it holds when it is applied.

In order to mitigate this, we make a copy of the transaction passed by the player. The player thus do not have a pointer to
the object we are going to use anymore. We can then validate and apply the transaction without risks of tampering. The same
process is used when passing transactions as a parameter at the step of "player agreement" check (where we check the player
agrees with the currently being validated transaction).

# Roadmap

## Security enforcement
The roadmap for now is to continue the implementation of the Downsizing Game as described in the current paper and then
compare this implementation against the following coding guidelines:

- [FIXME I AM MISSING].

If we have enough time, we will try to compare against other coding guidelines. 

## Game complexification

The following parts and/or rules of the game and/or previous decisions could be changed in order to make the game a little 
bit more complex but a little bit more realistic in some way:

- When a cheater is killed, distributions the resources so that we try to minimize the amount of debts remaining open or so
that we minimize the dissatisfaction of the loaners.
- Allowing players to trade points of their score (a score trade directly adds points to the score, without the "voting" step)
- Give players an interface to declare the tradable resources they have to the judging party. It would allow to model real life 
trade where businesses might have exclusive resources that they are alone to possess, compared to everyone trading the same resources.
- [FIXME: Other suggestions?]

The same way as for the guidelines, if we get additional time we will look into those issues first. If the reviewers have
suggestions of complexifications that they think would be of higher priority they are welcomed to include those suggestions
in the review comments.
<!-- 
\vspace{1\baselineskip}
 -->
**Reviewers suggestions are welcomed.** If reviewers have specific coding guidelines that would best fit this case study
 in mind, they can suggest it along with their review.

# Appendix
[FIXME: This section, alone, does not really make any sense. I think we should either make a small presentation of the
implementation / game flow somewhere or completely remove anything related to game flow / implementation fro, th extended
abstract, keeping this for the final version of the paper.]
### Game initialization
    Game::init
        clock = initialize_clock()
        judge = initialize_judge()
        decide_of_player_ids()
        players_starting_resources =   allocate starting resources 
                                            storage structure for every 
                                            player id
        players = instantiate every player with a player id 
                       and a copy of its starting resources data 
                       and a copy of its allowed "interface" (set of functions)
        judge.setPlayers(players)


### Pseudo-code of a round:
    Game::play
        while judge.play_round():
            pass

    Judge::play_round
        for pid in game.players_ids:
            p = players[pid]
            try:
                current_pid = pid
                p.play_round()
            except PlayerKilledException as e:
                game.loser = e.player
                return False
            clock.tick()
            if clock.is_over():
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