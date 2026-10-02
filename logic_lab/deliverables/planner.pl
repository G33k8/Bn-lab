% Logic Lab - Prolog as an independent plan verifier (Tasks 6-8 + extension)
% Run: swipl -q -s planner.pl -g run_queries -t halt

:- use_module(library(lists)).

% ---------------------------------------------------------------- Task 6
connected(a,b).
connected(b,a).
connected(b,c).
connected(c,b).

can_move(X,Y) :-
    connected(X,Y).

% ---------------------------------------------------------------- Task 7
valid_move(X,Y) :-
    connected(X,Y).

% ---------------------------------------------------------------- Task 8
wet_road.

slippery :-
    wet_road.

reduce_speed :-
    slippery.

% ------------------------------------------- Extension: full plan verifier
% A state is a sorted list of facts. Each action has preconditions and effects
% matching the Python planner, so the Python plan can be checked independently.

% action(Name, PositivePre, NegativePre, AddList, DeleteList)
action(move(X,Y),   [at(robot,X)],               [],                [at(robot,Y)],   [at(robot,X)]) :-
    connected(X,Y).
action(pickup(L),   [at(robot,L), at(package,L)], [holding(package)], [holding(package)], [at(package,L)]).
action(drop(L),     [at(robot,L), holding(package)], [],             [at(package,L)], [holding(package)]).

holds_all(Facts, State) :- subtract(Facts, State, []).
holds_none(Facts, State) :- intersection(Facts, State, []).

step(State, Act, Next) :-
    action(Act, Pos, Neg, Add, Del),
    holds_all(Pos, State),
    holds_none(Neg, State),
    subtract(State, Del, S1),
    union(S1, Add, S2),
    sort(S2, Next).

% valid_plan(+Initial, +Plan, +Goal): every action applicable, goal holds at the end.
valid_plan(State, [], Goal) :-
    holds_all(Goal, State).
valid_plan(State, [A|As], Goal) :-
    step(State, A, Next),
    valid_plan(Next, As, Goal).

initial([at(package,a), at(robot,a)]).
goal([at(package,c)]).

% ---------------------------------------------------------------- driver
show(Q) :-
    % An exception is reported as 'error', never confused with logical 'false'.
    catch(( call(Q) -> R = true ; R = false ), E, (print_message(error, E), R = error)),
    format("?- ~q.~n      -> ~w~n", [Q, R]).

run_queries :-
    format("--- Task 6~n"),
    show(can_move(a,b)),
    show(can_move(a,c)),
    format("--- Task 7~n"),
    show(valid_move(a,b)),
    show(valid_move(b,c)),
    show(valid_move(a,c)),
    format("--- Task 7 challenge: proposed Move(a,c)~n"),
    show(valid_move(a,c)),
    format("--- Task 8~n"),
    show(reduce_speed),
    format("--- Extension: verify whole plans~n"),
    initial(I), goal(G),
    show(valid_plan(I, [pickup(a), move(a,b), move(b,c), drop(c)], G)),
    show(valid_plan(I, [move(a,b), pickup(b), move(b,c), drop(c)], G)),
    show(valid_plan(I, [pickup(a), move(a,c), drop(c)], G)),
    show(valid_plan(I, [move(a,b), move(b,c)], G)).
