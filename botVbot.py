from botClass import *
import chess
import random
from datetime import datetime
import time

random.seed(datetime.now())

#Here's a program where you can play
#a game against yourself, if you'd like. 
#checks if moves are valid and all that jazz

matt = MaterialEngine(0.1)
dev = DevelopEngine(0.01)
tack = AttackEngine(0.01, 0.2)
rando = RandomEngine()

board = chess.Board()
wins = [0,0]

for i in range(0,1):
    print("\ndev  v tac")
    while not board.is_game_over():
        if board.turn:
            a = dev.evaluate2(board, 2,6)
            board.push(a[1])
        else:
            a = tack.evaluate2(board, 2,6)
            board.push(a[1])
    printGame(board)

    break
    board = chess.Board()
    board.push(f[1])
    board.push(g[1])

    print("\n3 v 1.2")
    while not board.is_game_over():
        if board.turn:
            a = matt.evaluate2(board, 3,0)
            board.push(a[1])
        else:
            a = matt.evaluate2(board, 1,2)
            board.push(a[1])
    printGame(board)
