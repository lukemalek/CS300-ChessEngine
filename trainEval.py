import numpy as np
import chess
import pandas as pd
import os
import tensorflow as tf
from tensorflow.keras import layers
from botClass import toCSV
from io import StringIO


evals = pd.read_csv("stockMoves.csv")
cutoff = 9000
eval_context = evals.copy()
eval_score = evals.copy()
eval_context = eval_context.iloc[:, :769]
eval_score = eval_score.iloc[:, 769 :]

train_context = eval_context.copy().iloc[:cutoff,:]
train_score = eval_score.copy().iloc[:cutoff,:]

validate_context = eval_context.copy().iloc[cutoff:,:]
validate_score = eval_score.copy().iloc[cutoff:,:]




model = tf.keras.Sequential([
    tf.keras.layers.InputLayer(input_shape = 769),
    tf.keras.layers.Dense(100, activation = "relu"),
    tf.keras.layers.Dense(10, activation = "relu"),
    tf.keras.layers.Dense(1)
])

model.compile(optimizer='adam',
              loss=tf.keras.losses.MeanSquaredError(),
              metrics=['accuracy'])


history = model.fit(
    train_context,
    train_score,
    steps_per_epoch = 200,
    validation_data = (validate_context, validate_score),
    epochs = 4)

boardState = chess.Board()
data = toCSV(boardState.board_fen())
if boardState.turn:
    data+='1'
else:
    data+='0'
data += "\n"
data += data
boop = StringIO(data)

print(model.predict(pd.read_csv(boop))[0][0])

