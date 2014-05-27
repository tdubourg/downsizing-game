Latex input:        mmd-article-header
author:             Théo Dubourg
Title:              Real Life Security - Security Protocols
Subtitle:           Case Study with the Downsizing Game
Base Header Level:  2
documentclass:      llncs
latex input:        mmd-article-begin-doc

<!--% Note: For some reason it seems that when adding a new reference the file needs to be compiled twice for ref to appear  -->
<!--
\nonstopmode
\begin{abstract}
--> 

Real life security use cases often include multiple parties talking to each other and making basic contracts between each  other. A
contract can take several forms: A contract between two programs about how they are going to communicate,  a contract  between two
business men about a deal between their respective companies,  etc. .  In this paper, we are going to focus on contracts that can be
modeled as _transactions_ sequences. More specifically, we are going to do a case study using the Downsizing Game invented by <!--
\cite{downgame} -->. The Downsizing Game puts in place multiple players that are all pursuing the same goal of maximizing their own
profit. Players can make transactions between each other in order to trade every sort of resources that is available in the game. The
goal of the case study is to see what are the steps to put in place a judging party that will enforce security protocol related to
cheating  prevention and what are the security requirements we can add on top of the functional requirements. Thorough our work setting
up such a system and environment, we will report on the issues we face, the solutions we find and the decision we make with the
justifications  for such choices.

<!--
\keywords{Keywords: enforcement, security, security protocols}
\end{abstract}
-->

# Introduction

## The Downsizing Game 
The Downsizing Game is a strategy game that puts in place multiple players that are all pursuing the same goal of maximizing their own profit.
Players also have to gain the maximum amount of "votes" in order to win the game. [FIXME: ADD A LITTLE BIT DETAILS TO THE DESCRIPTION OF THE GAME]

Players can make transactions between each other in order to trade every sort of resources that is available in the game: 
Money, trust, loyalty, and votes.

Every 100 rounds, a _voting round_ takes places. On voting rounds, _all_ players should vote for _another_ player. We will 
describe the game in details in [][gamerules]

Although it may seem like a simple game, it poses interesting challenges in terms of security because players will almost certainly try
to cheat in order to win the game and maximize their profit.

## Objective

The objective, in this paper, is to use the Downsizing Game as an example to study the process of a small-sized 
software development project that would start with functional requirements and then add security requirements.

We want to build a platform to allow players to play the Downsizing Game but we do not want any cheaters.

Thorough our design and implementation, we will report on the issues we faced and the solutions and decisions we took to 
overcome them, along with the justifications of such choices. We think this material can be of some interest to computer 
science students or beginners in providing them with a concrete and detailed example.

The work is split into 3 main steps:

1. Functional requirements: design & implementation
2. Security requirements: design & implementation 
3. Comparison against existing coding guidelines (see [_Roadmap_][Roadmap])

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

1. The communication channels, e.g. between the players and the judging party, are secure
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
- Valid / tradable _resources_ are votes, score and the game currency.
- Every player is given a million units of the game currency (let us call it dollars) and 10 votes to cast.
- Every player starts with a score of zero.
- At the end of the game, every player must return the original one million dollars that she was given in the beginning, 
she can keep the remainder of the money for her.
- At the end of the game, if players cannot give back the entire amount of mon,ey that they were given in the beginning, 
they have contracted a debt that they will have to reimburse.
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
- The winning player(s) earn(s) 1 million dollars (evenly split, if multiple winners).

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

#### Rounds [roundsdef]

A _round_ is an atomic unit of time in the game. A round can thus not be divided into subrounds. A round passes every time 
any of the following actions is executed:

- A transaction is applied
- Changing the current player
- Applying the result of a voting round (see [_Voting rounds_][votingrounds])

#### Voting rounds [votingrounds]

A voting round is a round where, **before** any action, all players will be asked to vote as described in the game's rules.

According to the definition of the rounds, no other actions can be taken during a voting round, as a round passes when
applying the result of a voting round.

#### Vote
Vote is a special resource that can only be transferred during a voting round.

#### Resources

A _resource_ is an integer quantity that the judging party allows to trade.
In our case study, the set of resources will be fixed at the beginning of the game, to:

- Cash/money/currency
- Votes
- Score

#### Score

The _score_ of a player is increased by 1 for every vote that is casted from another player for this player.

Players can also trade their score as a _resource_. The initial score is zero ([see rules][gamerules]).


#### Cheater

<!-- 
% Note: This is on the edge between security requirement and functional requirement. But I would still say it is a
% functional requirement because the concept of "cheater" by itself and the fact cheaters should be punished is
% necessary for the game itself, it does not, imho, represent a specific security check 
-->

A cheater is a player that breaks one or several game's rules. Cheaters must be immediately killed and thus removed 
from the game.

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
of votes to the _recipient_ of the transaction before a given absolute game's time unit (because it's a delayed transaction).

#### Valid transaction 

A _transaction_ is said to be _valid_ if and only if: 

- Transaction does not break a game rule. 
- Transaction is able to be completed to the extent of the judging party’s knowledge. (e.g.: Enough money on the account, 
in case of an immediate money transfer).

A bidirectional transaction will be considered valid if both unidirectional transactions it is composed of are valid. If
any of them is not, then the bidirectional transaction is also invalid.

## Security Requirements

Now that we have defined functional requirements, we are going to define and describe the addition _security requirements_ that are
necessary to ensure the players do not exploit singularities of the game in order to achieve behaviours that should not be achieved
according to the rules.

### Judging party exclusiveness aka turn-by-turn enforcement

The _current player_ must be the only one that can make calls to the judging party's interface.

This is needed in order to prevent other players from trying to steal the CPU and make transactions on the transaction quota
of another player instead of their own quota. We should thus implement a way to protect the judging party from executing
actions calls by other players than the _current player_.

<!-- 
% Note: Better solution?  If we want to divide it equally we need to do it with some sort of incremental algorithm: first 
% try to divide equally,  then,  sum up the amount of money that remain after taking into account the exact debt amounts,  
% in case any debt amount was smaller than the balance divided equally,  then re-directed this balance equally,  and so on 
% until there is either no debt left or no money left...
-->

### Immediate transactions: guaranteeing "immediateness" (atomicity) [immatom]

There should be no other interactions, no changes to the state of the game should happen between validation and application of an
immediate transaction.

This is partially guaranteed by the assumptions of no parallelism/concurrency. Although, a player program could still manage
to steal the CPU (effectively pausing the judging party program's execution) and try to change the state of the game by
submitting other transactions for instance. A player could use such an attack to submit multiple transactions that will be
validated on the same balances, but executed on different balances (race-condition/"TOCTTOU" <!-- \cite{tocttou} -->).

### Delayed/scheduled transactions completion [schedtranscompletion]

Delayed transactions are validated without the transfers of resources actually taking place and have a deadline for this
transfer to happen. There should a mechanism in place to that the transfer was indeed done strictly before the deadline.

### Players authentication [playerauth]

When creating a transaction, a player could provide false information about the participants in this transaction and thus
attempt to impersonate other players and make transactions on their behalf.

As a consequence, we need a mechanism to authenticate the players and be sure that the player who submitted a request in her
name, is indeed the player she is saying she is.

# Implementation 

In this section, we will first parts of the implementation related to enforcing the _security requirements_ and then present the reste our the implementation.

## Security requirements implementation

### Judging party exclusiveness aka turn-by-turn enforcement

In order to allow only the current player to access the judging party and make call to it, we will simply keep track of the current player in the judging party and every judging party's interface function will check whether the calling player is the current player or not and immediately abort if not. Player [authentication][playerauth] guarantees that another player cannot submit 
transactions by using the _current player_ as the origin of the transaction.

### Immediate transactions: guaranteeing "immediateness" (atomicity) [immatomimpl]
As explained in [][immatom], even with the stated [assumptions][Assumptions], there is still room for a race-condition.

To avoid this, we will make use of synchronization tools to only allow one concurrent execution of the judging
party program's code of validation and application of an immediate transaction. This can be materialized for instance by the use of
operating system's _mutex_ tools, but any other synchronization tool providing equal guarantees can be used too.

### Delayed/scheduled transactions completion [schedtranscompletionimpl]

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

### Players authentication [playerauthimpl]

To authenticate the player, we will go for the simple use of a password. At the beginning of the game, every player will be
given a unique password that she will have to pass along with every call she does to the judging party's interface in order
to prove this call is coming from the player it is said it comes from.

When the judging party calls players itself, the authentication is assured as the judging party has direct pointers to every
players and those pointers cannot be tampered by the other players (as [per assumption 3][Assumptions])

### Transactions validation

When asked to perform a new transaction, the judging party will sequentially (in the order below) go through multiples steps, or checks.

At every step, if the check fails, the transaction is marked as not valid, and thus, refused.

#### 1. Players mutual agreement

For any transaction validation, the first step that the judge will follow is to ask both involved players whether they
confirm that they agree with this transaction. Both players have to answer "yes" for this check to succeed.

#### 2. Input validation
The judge will then perform rational checks. These checks are the following:

- Is the amount a **positive integer**? (avoiding resources "generation" with negative values, and rounding errors exploits
if we were to use real numbers)
- Is the amount smaller than the global amount of resources of this type in the entire game?
- If it is a delayed transaction, is the _deadline_ a valid round? ($current\ round < deadline < last\ round$ )
- In case of voting promise, is the amount smaller than the number of votes the player will be able to cast before the end 
of the game? (voting rounds multiplied by votes per player and per voting round)

#### 3. Balance check

The judge will then check the balance of the player _from_ which the transfer is going to happen for the resource that is
going to be transferred.

In the case of immediate transactions, the judge checks. The balance has to be equal or greater to the amount of the
transaction.

In the case of scheduled transactions, the judge will not check the balance, as the player could have planned to make other
agreements with other players between the round where the current transaction is being validated and the round where the
payment deadline is set.

That means that a scheduled, or delayed transaction, is not safe by itself, as the judging party cannot guarantee that the
payment will be made. Mitigation/punishment in case of lack of payment will be described later.

#### Additional virtual round for transactions validation

It should be noted that, as delayed transactions are validated at the beginning of rounds, a _virtual_ round, that is to say 
a non playable round, will be added at the end of the game for the purpose of validating the delayed transaction whose deadline
was the last round (excluding the additional virtual round).

As the game has 1,000 [rounds][gamerules], this round could be considered as the 1,001^st round.

### Casting votes aka _voting transactions_ [voting]

Casting votes is done (by the players) by returning, on the call of the judging party, a special transaction. We will call 
this type of special transaction _Voting Transaction_.

A voting transaction is an _immediate transaction_ where the resource type is always _votes_. The _payer_ is the player
casting the vote and the _payee_ is the player whose score will be increased by this vote, ie. the player "receiving" the
vote.

If the vote casting has to been linked to a delayed transaction in progress, the same process as for any other delayed
transaction will be applied: A "subtransaction" of type _Voting Subtransaction_ will be used. See [][schedtranscompletion]
for more details on _subtransactions_.

<!-- 
\vspace{1\baselineskip}
-->

Note that we also had the choice to make "votes" resource a "voting promises" resource and directly enforcing transferred amounts of
this resource by the judging party. We would do so by forcing the _payer_ player to vote less and casting automatically the _owed_
votes at the next voting round or at some voting round specified in the transaction. However, we finally decided to transform every
vote casting into a transaction so that not only we keep of every single action in the game as a transaction, allowing for logging, 
replay and potential error-recovery, but that also allows more flexible voting transactions to be created. Indeed, with our 
implementation, a player can tell another player "OK, I will for sure vote for you $X$ times before the round $r$, but I get to 
decide when". Such transactions, in a real world environment, are very important because it allows to add some preassure to some 
other  player for instance, and not to reveal one's true voting agreement too early, while still having strong voting agreements. We 
believe suchs advantages are better than the sole advantage of having the judging party to it instead of the player, that would 
prevent the player from cheating. It is to be also noted that this model allows more easily the implementation of _cancellation 
transactions_ as defined in the [future work][futurework].

### Voting rounds [votingrounds_security]

On voting rounds, the judging party will ask players to vote.

Players should vote immediately, no delay is given. Players should vote according to the rules and they should respect any
official vote promise agreement they made via a transaction.

The judging party, for every player's vote, will check that it respects the rules, and will then check that it respects vote
promises that have been registered via previous transaction. To summarise, a voting round go through the following steps, in
order:

1. Check for scheduled transaction completeness, as for any round.
2. Ask every player, one by one, to cast one vote.
3. Validate the vote according to the rules.
4. Either accept the vote, of qualify voting player as a cheater if the vote was not valid.
5. Do 3. and 4. again for the next player, until we went through all of them.
6. Publicly disclose the new number of votes that every player received and their new score.
7. Go to next round (as per [][roundsdef])

### Cheaters death and resources owed

If, at the moment a cheater is kill, she owes some resources to another player, the remaining resources of the killed player will be
transferred to the one they were owed to, up the owed amount, and up to the remaining balance of this resource on this killed
player account.

If she owes resources to _multiple_ players. The judging party will distribute the money proportionately, rounded to the closest
integer. The exact formula is:

$$part\ of\ the\ remaining\ balance\ you\ get = round\left(\cfrac{total\ amount\ cheater\ owed\ to\ you}{total\ debt\ of\ the\ cheater}\right)$$

Where $round$ is the function that rounds a real number to the closest integer.

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

## Implementation of the game / game execution flow

## Game initialization
[FIXME insert diagram here]

## Round
[FIXME insert diagram here]

The pseudo-code of a non-voting round is located in the [appendix][codegameinit]

### Non-voting round
[FIXME insert diagram here]

The pseudo-code of a non-voting round is located in the [appendix][coderound]

### Voting round
[FIXME insert diagram here]


# Roadmap

The roadmap for now is to continue the implementation of the Downsizing Game as described in the current paper and then
compare this implementation against the following coding guidelines: _"Building Secure Software: How to Avoid Security Problems the Right Way"_, by Viega and McGraw <!-- \cite{coding1} -->

If we have enough time, we will also try to compare against other coding guidelines. 

<!-- 
\vspace{1\baselineskip}
 -->
**Reviewers suggestions** are also welcomed. If reviewers have specific coding guidelines in mind that would especially well apply to our current implementation (in Python), they can submit suggestions together with their review.

# Future work: Game complexification

The following parts and/or rules of the game and/or previous decisions could be changed in order to make the game a little 
bit more complex but a little bit more realistic in some way:

- When a cheater is killed, distributions of the cheater's remaining resources so that we try to minimize the amount of debts remaining open or so that we minimize the dissatisfaction of the loaners.
- Allowing _cancellation transactions_ (together with a _refund_) for _delayed_ transactions. E.g.: a player finally does not want to give that many votes to another player, so she asks for cancellation and proposes a given amount as a refund for the cancelling of the "contract". As any other transaction, both players would need to agree. The judging party would then simply _discard_ the remaining open delayed transaction upon applying the _cancellation transaction_.
- Give players an interface to declare the tradable resources they have to the judging party. It would allow to model real life 
trade where businesses might have exclusive resources that they are alone to possess, compared to everyone trading the same resources.
- Introducting loyalty and trust "resources".

The same way as for the guidelines, if we get additional time we will look into those issues first. 

<!-- 
\vspace{1\baselineskip}
 -->

**If the reviewers have suggestions** of complexifications that they think would be of higher priority they are welcomed to include
those suggestions in the review comments.

# Appendix
[FIXME: This section, alone, does not really make any sense. I think we should either make a small presentation of the
implementation / game flow somewhere or completely remove anything related to game flow / implementation fro, th extended
abstract, keeping this for the final version of the paper.]

### Game initialization [codegameinit]
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


### Pseudo-code of a round [coderound]
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
\begin{thebibliography}{1} % Note: This is non-sense but I have to keep this {1} for it to work, any other parameter will screw something up
\bibitem{downgame}
Shinobu Kaitani:
Downsizing Game, Liar Game
\url{http://en.wikipedia.org/wiki/Liar_Game#Revival_Round:_Downsizing_Game}

\bibitem{coding1}
Gary McGraw, John Viega:
Building Secure Software: How to Avoid Security Problems the Right Way
2001

\bibitem{tocttou}
TOCTTOU: "Time of check to time of use"
\url{http://en.wikipedia.org/wiki/Time-of-check-to-time-of-use}

\end{thebibliography}
-->
<!-- \end{document} -->