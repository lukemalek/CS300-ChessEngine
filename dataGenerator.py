import chess
import os
import chess.engine
from botClass import *
import math

def sigmoid(x):
    if x >= 0:
        z = math.exp(-x)
        sig = 1 / (1 + z)
        return sig
    else:
        z = math.exp(x)
        sig = z / (1 + z)
        return sig

def stringify(fen):
    res = ''
    for letter in fen:
        if letter.isnumeric():
            for i in range(0, int(letter)):
                res += ' '
        elif letter == '/':
            continue 
        else:
            res += letter
    return res

def toCSV(fen):
    #"(k,q,r,b,n,p,K,Q,R,B,N,P)"
    res = ''
    for letter in fen:
        if letter == 'k':
            res+= '1,0,0,0,0,0,0,0,0,0,0,0,'
        elif letter == 'q':
            res+= '0,1,0,0,0,0,0,0,0,0,0,0,'
        elif letter == 'r':
            res+= '0,0,1,0,0,0,0,0,0,0,0,0,'
        elif letter == 'b':
            res+= '0,0,0,1,0,0,0,0,0,0,0,0,'
        elif letter == 'n':
            res+= '0,0,0,0,1,0,0,0,0,0,0,0,'
        elif letter == 'p':
            res+= '0,0,0,0,0,1,0,0,0,0,0,0,'
        elif letter == 'K':
            res+= '0,0,0,0,0,0,1,0,0,0,0,0,'
        elif letter == 'Q':
            res+= '0,0,0,0,0,0,0,1,0,0,0,0,'
        elif letter == 'R':
            res+= '0,0,0,0,0,0,0,0,1,0,0,0,'
        elif letter == 'B':
            res+= '0,0,0,0,0,0,0,0,0,1,0,0,'
        elif letter == 'N':
            res+= '0,0,0,0,0,0,0,0,0,0,1,0,'
        elif letter == 'P':
            res+= '0,0,0,0,0,0,0,0,0,0,0,1,'
        elif letter.isnumeric():
            for i in range(0, int(letter)):
                res += '0,0,0,0,0,0,0,0,0,0,0,0,'
    return res

def convert(stockRating, curve = 1):
    #curve 1 is a line,
    #curve 2 is a sigmoid

    #MAKE SURE stockfish mate score set to 100 000


    #a value of 1 means that you are cetain that you will win, haven't found mate yet. a value of -1 means that you are certain you will lose, though mate is not evident.
    #to represent mate in n, a score of 1+(1/n) is given. 
    
    if stockRating ==0:
        return 0
    if abs(stockRating) > 99900:
        val = 1+ (1/(100000-abs(stockRating)))
        if stockRating> 0:
            return val
        return -val
    
    
    if curve == 1:
        return stockRating/10000

    return 2 * sigmoid(stockRating/200) - 1





engine = chess.engine.SimpleEngine.popen_uci(r"/mnt/c/Users/luke/Downloads/stockfish_14.1_win_x64/stockfish_14.1_win_x64_avx2.exe")

f = open('stockMoves.csv', 'w')
#f.truncate(0)
for i in range(0, 769):
    f.write(str(i) + ', ')
f.write('eval\n')
entries = 0
buddy = RandomEngine()

#f.write('Fen, ToMove, povScore\n')

while entries<10000:
    board = chess.Board()
    for i in range(0,6):
        a = buddy.evaluate(board, depth = 1)
        board.push(a[1])
    while not board.is_game_over():
        info = engine.analyse(board, chess.engine.Limit(time=0.01))
        f.write(toCSV(board.board_fen()))
        if board.turn:
            f.write('1,')
        else:
            f.write('0,')
        f.write(str( convert( info['score'].relative.score(mate_score = 100000), 2 )) + '\n')
        entries +=1
        board.push(info['pv'][0])


engine.quit()
