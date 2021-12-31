import numpy as np
import pandas as pd
import os
import tensorflow as tf
from tensorflow.keras import layers

evals = pd.read_csv("stockMoves.csv")



eval_context = evals.copy()
eval_scores = evals.copy()

eval_context = eval_context.iloc[:, :769]
eval_scores = eval_scores.iloc[:, 769 :]

print(eval_context.head())
print(eval_scores.head())

model = tf.keras.Sequential([
    tf.keras.layers.Dense(769)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10)
])


