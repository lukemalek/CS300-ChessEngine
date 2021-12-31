from botClass import *
import chess
import random
from datetime import datetime
import time

random.seed(datetime.now())
board = chess.Board()

#Here's a program where you can play
#a game against yourself, if you'd like. 
#checks if moves are valid and all that jazz

buddy = MaterialEngine(0.3)
pal = DevelopEngine(0.01)


while not board.is_game_over():
    
    if  board.turn:
        print(board)
        print("White to move: ")
        choice = input()
        move = chess.Move.from_uci(choice)
        if move in board.legal_moves:
            board.push(move)
        else:
            print("Invalid!")
    else:
        t1 = time.time()
        a = pal.evaluate2(board, 3,2)
        t2 = time.time()
        print(board.san(a[1]), "in ", t2-t1)
        board.push(a[1])
        

    
    

print(board)
print(board.outcome())
print("Game is over")
