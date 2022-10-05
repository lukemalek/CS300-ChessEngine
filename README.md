# CS300: Artificial Intelligence Final Project
## TLDR
Set out with the broad goal of creating a program which could play decent chess. Ultimately, I created a small army of chess engines, all of varied complexity and chess-playing strength.

File "botClass.py" holds the bulk of the code.

## Anatomy of my engines
As a bit of an oversimplification, chess engines are defined by two distinct parts: a heuristic, and a game tree search algorithm.

A heuristic is a function which takes a quick look at a chess board and decides if the position is favorable to the White pieces or the Black pieces. Heuristics don't consider future moves at all. They merely provide a sort of "hunch". 

The game tree search considers the ever-expanding space of board states that can be reached by various sequences of moves. It considers these posibilities then returns a move which maximizes the chance of winning. The "best move" is found via a mini-max algorithm. 

By choosing a specific heuristic function and pairing it with a specific game tree search, you've just created a chess engine.

## Heuristics featured in this project
The functions are listed in order of their chronological creation.

### Random
For a given board state, return a random value in (-1,1). 

### Material
The pieces on the board are not created equally. Certain pieces are much more valuable than others. We say that bishops and knights are worth 3 pawns, rooks are worth 5 pawns, and queens are worth 9. A sum of pieces based on their pawn value is called "material".

Pretend the White player had a king and 2 bishops on the board. We say this player has 6 points of material. If the Black player has a king, a queen, and a pawn, we say the player has 10 points of material. Further, we say that the Black player is "Up 4 points of Material."

This heuristic returns the material difference on the board. 

### Development
A knight in the center of the board has more attacking potential than one on the edge. 

This heuristic counts material first, then takes into account the prospects of each side's pieces. The side whose pieces can reach more squares gets a slightly higher score.

### Attacking
To win a game of chess, you must checkmate the opponent's king. Thus, it is wise to have your pieces trained toward the enemy king. 

This heuristic counts material first, then considers the "danger" of the opposing king. The side with the king in more danger gets a slightly lower evaluation.

### Neural Net
This Heuristic is based on the opinion of a neural network model. I trained this model by creating a large dataset of chess positions accompanied by their Stockfish evaluation. Stockfish is the current strongest chess-playing entity in the world. My neural net literally learned from the best.

## Tree searches featured in this project
Next, here are the versions of tree search I created, again listed chronologically.
### Simple Mini Max
Expand the game tree to some depth 'n'. Calculate the heuristic on all leaf positions.  Assume that your opponent will pick moves which maximize their own chance of winning. 

### Mini Max with Alpha/beta pruning
Significantly reduces the number of positions which must be considered

### Mini Max with A/B pruning with varied depth tree
Expanding the complete game tree is often overkill. There are certain moves which deserve more computational focus than others. This algorithm allows extra search depth on moves which involve a check to the king or a capture of a piece. 

