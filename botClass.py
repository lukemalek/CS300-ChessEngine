import chess
import random
import numpy as np
import pandas as pd
import os
import tensorflow as tf
from tensorflow.keras import layers
from io import StringIO

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

def chaos(range):
    #Used for eval scores when things would be too similar otherwise
    return 2* range* random.random() - range

def distFromCenter(square):
    center = [chess.D4, chess.D5, chess.E4, chess.E5]
    tot = 0
    for i in range(0,4):
        tot+= chess.square_distance(square, center[i])
    return tot//4

def centerBonus(dist):
    return 1/(1+dist)

def kingDanger(board):
    whiteKingTerr = board.attacks(board.king(True))
    blackKingTerr = board.attacks(board.king(False))


    whiteDanger =  len(whiteKingTerr)
    blackDanger =  len(blackKingTerr)
    for square in whiteKingTerr:
            whiteDanger += len(board.attackers(False, square)) - len(board.attackers(True, square))
    
    for square in blackKingTerr:
        blackDanger += len(board.attackers(True, square)) - len(board.attackers(False, square))

    return [whiteDanger, blackDanger]


def materialBalance(boardState):
    #counts up white material, then counts up black material. returns a list of len 2
    whitePoints = 0
    blackPoints = 0
    data = boardState.board_fen()
    #warning, gross coding ahead
    for letter in data:
        if letter == 'r':
            blackPoints+= 5
        elif letter == 'R':
            whitePoints+= 5
        elif letter == 'b':
            blackPoints+= 3
        elif letter == 'B':
            whitePoints+= 3
        elif letter == 'n':
            blackPoints+= 3
        elif letter == 'N':
            whitePoints+= 3
        elif letter == 'q':
            blackPoints+= 9
        elif letter == 'Q':
            whitePoints+= 9
        elif letter == 'p':
            blackPoints+= 1
        elif letter == 'P':
            whitePoints+= 1

    return whitePoints, blackPoints

def developmentBalance(boardState):
    whitePieces = boardState.pieces(1, color = True)
    for i in [2,3,4,5]:
        whitePieces.update(boardState.pieces(i, color = True))

    blackPieces = boardState.pieces(1,color = False)
    for i in [2,3,4,5]:
        blackPieces.update(boardState.pieces(i, color = False))
    
    whitePoints = 0
    blackPoints = 0


    for square in whitePieces:
        piece = boardState.piece_at(square).symbol()
        if piece == 'Q':
            whitePoints += 9+  0.04 * len(boardState.attacks(square))
        elif piece == 'B':
            whitePoints += 3+ 0.1 * len(boardState.attacks(square))
        elif piece == 'N':
            whitePoints += 3+ 0.15 * len(boardState.attacks(square)) 
        elif piece == 'R':
            whitePoints += 5+ 0.08 * len(boardState.attacks(square)) 
        elif piece == 'P':
            whitePoints += 1+ 0.5 * centerBonus(distFromCenter(square)) 
            if chess.square_rank(square) >=5:
                whitePoints += chess.square_rank(square) -4

    for square in blackPieces:
        piece = boardState.piece_at(square).symbol()
        if piece == 'q':
            blackPoints += 9+ 0.04 * len(boardState.attacks(square))
        elif piece == 'b':
            blackPoints += 3+ 0.1 * len(boardState.attacks(square))
        elif piece == 'n':
            blackPoints += 3+0.15 * len(boardState.attacks(square))
        elif piece == 'r':
            blackPoints += 5+0.08 * len(boardState.attacks(square))
        elif piece == 'p':
            blackPoints += 1+0.4 * centerBonus(distFromCenter(square)) 
            if chess.square_rank(square) <=2:
                blackPoints += 3-chess.square_rank(square)

    return whitePoints, blackPoints


def orderedMoves(board):
    #retrieve all moves in position
    og = [move for move in board.legal_moves]
    
    
    caps = []
    other = []
    for i in range(0, len(og)):
        move = og[i]
        #dumps check and captures into one bucket, other moves in a second
        if board.is_capture(move) or board.gives_check(move):
            caps.append(move)
        else:
            other.append(move)
    return caps + other




def loudMoves(board):
    #retrieve all moves in position
    og = [move for move in board.legal_moves]
    
    
    caps = []
    for i in range(0, len(og)):
        move = og[i]
        #keeps only the checks and captures.
        if board.is_capture(move) or board.gives_check(move):
            caps.append(move)
    return caps

def printGame(board):
    #function that will return a pgn of a game. Game cannot be played from a preset fen so far, else glidj
    tracer = chess.Board()
    sans = []
    for move in board.move_stack:
        sans.append(tracer.san(move))
        tracer.push(move)

    if len(sans) % 2 ==0:
        for i in range (0, len(sans)//2):
            print(i+1, sans[2*i], sans[2*i+1])
    else:
        for i in range (0, len(sans)//2):
            print(i+1, sans[2*i], sans[2*i+1])
        print(len(sans)//2+1, sans[len(sans)-1])
    if board.is_game_over():
        print(board.result())

class RandomEngine:
    def evaluate(self, boardState, depth= 1):
        #Will return the 'best move' suggested by engine.
        #for a random bot, this of course just a random move.
        if depth == 0 or boardState.is_game_over():
            #This is the core of the engine. what it thinks of a position
            #when blind, at no depth. this engine just takes a random guess.
            return 2* random.random() -1, chess.Move.null()
        
        
        
        #As far as I'm aware, this is an adequate minimax alg. 
        #SHould be able to use thif for every engine I make.
        children = [move for move in boardState.legal_moves]
        evals = [0]* len(children)
        for i in range(0, len(children)):
            boardState.push(children[i])
            evals[i] = - self.evaluate(boardState, depth-1)[0]
            boardState.pop()
        max_eval = max(evals)
        max_index = evals.index(max_eval)
        return max_eval, children[max_index]


class MaterialEngine:
    def __init__(self, wack = 0):
        self.wackiness = wack
    
    def blind_eval(self, boardState):
        #evaluates position without checking any moves. 
        #if board is in checkmate, that measn you lost.
        if boardState.is_game_over():
            if boardState.is_checkmate():
                return [-10000, chess.Move.null()]
            return [0, chess.Move.null()]

        #simply passes the difference in material from the player's perspective.
        color = boardState.turn
        balance = materialBalance(boardState)
        if color:
            return [balance[0]-balance[1] + chaos(self.wackiness), chess.Move.null()]
        return [balance[1]-balance[0] + chaos(self.wackiness), chess.Move.null()]

    def silent_eval(self, boardState, depth = 1, a=-100000, b=-100000):
        #the idea here is to have an eval function that checks deeper if the position has captures available.
        #if depth is low, (at leaves for a big tree) then just return the blind
        if depth < 1:
            return self.blind_eval(boardState)

        if boardState.is_game_over():
            if boardState.is_checkmate():
                return [-10000, chess.Move.null()]
            return [0, chess.Move.null()]

        #get the loud moves
        caps = loudMoves(boardState)

        if len(caps) == 0:
            #position is quiet, simply return material balance.
            return self.blind_eval(boardState)
        #otherwise, there are captures to analyse. 
        #perform minimax with alpha beta junk but just on the remaining captures.
            
        
        value = self.blind_eval(boardState)

        children = caps
        for i in range(0, len(children)):
            #retreive value of child node
            boardState.push(children[i])
            childval = self.silent_eval(boardState, depth-1, b,a)
            childval[0] *= -1
            boardState.pop()
            
            #here we adjust scores so that mate in 2 is chosen above mate in 3
            if childval[0] >9000:
                childval[0]-=1

            if value[0] < childval[0]:
                value[0] = childval[0]
                value[1] = children[i]


            if value[0] >= -b:
                break
            
            if a< value[0]:
                a = value[0]
        return value

    def evaluate(self, boardState, depth= 1, a = -100000, b = -100000):
        #Standard eval. No extra depth if max-depth position has captures.
        if boardState.is_game_over():
            if boardState.is_checkmate():
                return [-10000, chess.Move.null()]
            return [0, chess.Move.null()]
        
        if depth == 0:
            #This is the core of the engine. what it thinks of a position
            #when blind, at no depth. 
            return self.blind_eval(boardState)
            

        #Attempting to update to alpha beta pruning. 
        
        #unless we have evidence, all moves suck, aka the value of the node
        #is hella low
        value = [-100000, chess.Move.null()]


        children = orderedMoves(boardState)
        for i in range(0, len(children)):
            
            #retreive value of child node
            boardState.push(children[i])
            childval = self.evaluate(boardState, depth-1, b,a)
            childval[0] *= -1
            boardState.pop()
            
            #here we adjust scores so that mate in 2 is chosen above mate in 3
            if childval[0] >9000:
                childval[0]-=1

            if value[0] < childval[0]:
                value[0] = childval[0]
                value[1] = children[i]


            if value[0] >= -b:
                break
            
            if a< value[0]:
                a = value[0]
        return value

    def evaluate2(self, boardState, depth= 1,extraDepth = 0, a = -100000, b = -100000):
        #New eval function that will go a little deeper if captures and check exist.
        if boardState.is_game_over():
            if boardState.is_checkmate():
                return [-10000, chess.Move.null()]
            return [0, chess.Move.null()]
        
        if depth == 0:
            #get the silent eval of the position. This is just the blind eval if checks and caps don't exist.
            return self.silent_eval(boardState, extraDepth, a,b)
            

        #Attempting to update to alpha beta pruning. 
        
        #unless we have evidence, all moves suck, aka the value of the node
        #is hella low
        value = [-100000, chess.Move.null()]


        children = orderedMoves(boardState)
        for i in range(0, len(children)):
            
            #retreive value of child node
            boardState.push(children[i])
            childval = self.evaluate2(boardState,depth-1,extraDepth, b,a)
            childval[0] *= -1
            boardState.pop()
            
            #here we adjust scores so that mate in 2 is chosen above mate in 3
            if childval[0] >9000:
                childval[0]-=1

            if value[0] < childval[0]:
                value[0] = childval[0]
                value[1] = children[i]


            if value[0] >= -b:
                break
            
            if a< value[0]:
                a = value[0]
        return value


class DevelopEngine:
    def __init__(self, wack = 0):
        self.wackiness = wack
    
    def blind_eval(self, boardState):
        #evaluates position without checking any moves. 
        #if board is in checkmate, that measn you lost.
        if boardState.is_game_over():
            if boardState.is_checkmate():
                return [-10000, chess.Move.null()]
            return [0, chess.Move.null()]

        #passes material balance PLUS developmental balance.
        color = boardState.turn
        devBal = developmentBalance(boardState)
        if color:
            return [devBal[0] - devBal[1]+ chaos(self.wackiness), chess.Move.null()]
        return [devBal[1]-devBal[0]  + chaos(self.wackiness), chess.Move.null()]

    def silent_eval(self, boardState, depth = 1, a=-100000, b=-100000):
        #the idea here is to have an eval function that checks deeper if the position has captures available.
        #if depth is low, (at leaves for a big tree) then just return the blind
        if depth < 1:
            return self.blind_eval(boardState)

        if boardState.is_game_over():
            if boardState.is_checkmate():
                return [-10000, chess.Move.null()]
            return [0, chess.Move.null()]

        #get the loud moves
        caps = loudMoves(boardState)

        if len(caps) == 0:
            #position is quiet, simply return blind eval
            return self.blind_eval(boardState)
        #otherwise, there are captures to analyse. 
        #perform minimax with alpha beta junk but just on the remaining captures.
            
        
        value = self.blind_eval(boardState)

        children = caps
        for i in range(0, len(children)):
            #retreive value of child node
            boardState.push(children[i])
            childval = self.silent_eval(boardState, depth-1, b,a)
            childval[0] *= -1
            boardState.pop()
            
            #here we adjust scores so that mate in 2 is chosen above mate in 3
            if childval[0] >9000:
                childval[0]-=1

            if value[0] < childval[0]:
                value[0] = childval[0]
                value[1] = children[i]


            if value[0] >= -b:
                break
            
            if a< value[0]:
                a = value[0]
        return value

    def evaluate2(self, boardState, depth= 1,extraDepth = 0, a = -100000, b = -100000):
        #New eval function that will go a little deeper if captures and check exist.
        if boardState.is_game_over():
            if boardState.is_checkmate():
                return [-10000, chess.Move.null()]
            return [0, chess.Move.null()]
        
        if depth == 0:
            #get the silent eval of the position. This is just the blind eval if checks and caps don't exist.
            return self.silent_eval(boardState, extraDepth, a,b)
            

        #Attempting to update to alpha beta pruning. 
        
        #unless we have evidence, all moves suck, aka the value of the node
        #is hella low
        value = [-100000, chess.Move.null()]


        children = orderedMoves(boardState)
        for i in range(0, len(children)):
            
            #retreive value of child node
            boardState.push(children[i])
            childval = self.evaluate2(boardState,depth-1,extraDepth, b,a)
            childval[0] *= -1
            boardState.pop()
            
            #here we adjust scores so that mate in 2 is chosen above mate in 3
            if childval[0] >9000:
                childval[0]-=1

            if value[0] < childval[0]:
                value[0] = childval[0]
                value[1] = children[i]


            if value[0] >= -b:
                break
            
            if a< value[0]:
                a = value[0]
        return value

class AttackEngine:
    def __init__(self, wack = 0, butchfactor = 0):
        self.wackiness = wack
        #named after my friend butch who really enjoys being extremely agressive in chess
        self.bf = butchfactor
    def blind_eval(self, boardState):
        #evaluates position without checking any moves. 
        #if board is in checkmate, that measn you lost.
        if boardState.is_game_over():
            if boardState.is_checkmate():
                return [-10000, chess.Move.null()]
            return [0, chess.Move.null()]

        #simply passes the difference in material from the player's perspective.
        color = boardState.turn
        balance = developmentBalance(boardState)
        danger = kingDanger(boardState)
        if color:
            return [balance[0] + self.bf * danger[1] -balance[1] + chaos(self.wackiness), chess.Move.null()]
        return [balance[1] + self.bf * danger[0] -balance[0] + chaos(self.wackiness), chess.Move.null()]

    def silent_eval(self, boardState, depth = 1, a=-100000, b=-100000):
        #the idea here is to have an eval function that checks deeper if the position has captures available.
        #if depth is low, (at leaves for a big tree) then just return the blind
        if depth < 1:
            return self.blind_eval(boardState)

        if boardState.is_game_over():
            if boardState.is_checkmate():
                return [-10000, chess.Move.null()]
            return [0, chess.Move.null()]

        #get the loud moves
        caps = loudMoves(boardState)

        if len(caps) == 0:
            #position is quiet, simply return material balance.
            return self.blind_eval(boardState)
        #otherwise, there are captures to analyse. 
        #perform minimax with alpha beta junk but just on the remaining captures.
            
        
        value = self.blind_eval(boardState)

        children = caps
        for i in range(0, len(children)):
            #retreive value of child node
            boardState.push(children[i])
            childval = self.silent_eval(boardState, depth-1, b,a)
            childval[0] *= -1
            boardState.pop()
            
            #here we adjust scores so that mate in 2 is chosen above mate in 3
            if childval[0] >9000:
                childval[0]-=1

            if value[0] < childval[0]:
                value[0] = childval[0]
                value[1] = children[i]


            if value[0] >= -b:
                break
            
            if a< value[0]:
                a = value[0]
        return value

    def evaluate2(self, boardState, depth= 1,extraDepth = 0, a = -100000, b = -100000):
        #New eval function that will go a little deeper if captures and check exist.
        if boardState.is_game_over():
            if boardState.is_checkmate():
                return [-10000, chess.Move.null()]
            return [0, chess.Move.null()]
        
        if depth == 0:
            #get the silent eval of the position. This is just the blind eval if checks and caps don't exist.
            return self.silent_eval(boardState, extraDepth, a,b)
            

        #Attempting to update to alpha beta pruning. 
        
        #unless we have evidence, all moves suck, aka the value of the node
        #is hella low
        value = [-100000, chess.Move.null()]


        children = orderedMoves(boardState)
        for i in range(0, len(children)):
            
            #retreive value of child node
            boardState.push(children[i])
            childval = self.evaluate2(boardState,depth-1,extraDepth, b,a)
            childval[0] *= -1
            boardState.pop()
            
            #here we adjust scores so that mate in 2 is chosen above mate in 3
            if childval[0] >9000:
                childval[0]-=1

            if value[0] < childval[0]:
                value[0] = childval[0]
                value[1] = children[i]


            if value[0] >= -b:
                break
            
            if a< value[0]:
                a = value[0]
        return value

class NNEngine:
    def __init__(self):
        self.model = tf.keras.models.load_model("neuralNetData/evalModel.h5")
    def blind_eval(self, boardState):
        data = toCSV(boardState.board_fen())
        if boardState.turn:
           data+='1'
        else:
            data+='0'
        data += "\n"
        data += data
        boop = StringIO(data)
        return [self.model.predict(pd.read_csv(boop))[0][0], chess.Move.null()]

    def silent_eval(self, boardState, depth = 1, a=-2, b=-2):
        #the idea here is to have an eval function that checks deeper if the position has captures available.
        #if depth is low, (at leaves for a big tree) then just return the blind
        if depth < 1:
            return self.blind_eval(boardState)

        if boardState.is_game_over():
            if boardState.is_checkmate():
                return [-2, chess.Move.null()]
            return [0, chess.Move.null()]

        #get the loud moves
        caps = loudMoves(boardState)

        if len(caps) == 0:
            #position is quiet, simply return material balance.
            return self.blind_eval(boardState)
        #otherwise, there are captures to analyse. 
        #perform minimax with alpha beta junk but just on the remaining captures.
            
        
        value = self.blind_eval(boardState)

        children = caps
        for i in range(0, len(children)):
            #retreive value of child node
            boardState.push(children[i])
            childval = self.silent_eval(boardState, depth-1, b,a)
            childval[0] *= -1
            boardState.pop()
            
            #here we adjust scores so that mate in 2 is chosen above mate in 3
            if childval[0] >9000:
                childval[0]-=1

            if value[0] < childval[0]:
                value[0] = childval[0]
                value[1] = children[i]


            if value[0] >= -b:
                break
            
            if a< value[0]:
                a = value[0]
        return value

    def evaluate2(self, boardState, depth= 1,extraDepth = 0, a = -2, b = -2):
        #New eval function that will go a little deeper if captures and check exist.
        if boardState.is_game_over():
            if boardState.is_checkmate():
                return [-2, chess.Move.null()]
            return [0, chess.Move.null()]
        
        if depth == 0:
            #get the silent eval of the position. This is just the blind eval if checks and caps don't exist.
            return self.silent_eval(boardState, extraDepth, a,b)
            

        #Attempting to update to alpha beta pruning. 
        
        #unless we have evidence, all moves suck, aka the value of the node
        #is hella low
        value = [-2, chess.Move.null()]


        children = orderedMoves(boardState)
        for i in range(0, len(children)):
            
            #retreive value of child node
            boardState.push(children[i])
            childval = self.evaluate2(boardState,depth-1,extraDepth, b,a)
            childval[0] *= -1
            boardState.pop()
            
            #here we adjust scores so that mate in 2 is chosen above mate in 3
            if childval[0] >9000:
                childval[0]-=1

            if value[0] < childval[0]:
                value[0] = childval[0]
                value[1] = children[i]


            if value[0] >= -b:
                break
            
            if a< value[0]:
                a = value[0]
        return value

    