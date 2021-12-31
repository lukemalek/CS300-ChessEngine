import chess
import random
from botClass import *



#Here's a program where you can play
#a game against yourself, if you'd like. 
#checks if moves are valid and all that jazz

board = chess.Board()
mat = NNEngine()


#example = '8/8/8/8/8/K7/7Q/k7'
example2 = '8/qQ5p/3pN2K/3pp1R1/4k3/7N/1b1PP3/8'
example3 = '8/8/8/8/8/3Q4/r7/k6K'
friedLiva = 'r1bqkb1r/ppp2Npp/2n5/3np3/2B5/8/PPPP1PPP/RNBQK2R b KQkq - 0 6'
#board.set_fen(example3)
#board.push(chess.Move.from_uci('0000'))

print(board)



print(mat.blind_eval(board))





#print(board)
#Nf3 = chess.Move.from_uci("g1f3")
#board.push(Nf3)
