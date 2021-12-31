import numpy as np
import pandas as pd


# Make numpy values easier to read.
np.set_printoptions(precision=3, suppress=True)

import tensorflow as tf
from tensorflow.keras import layers

evals_train = pd.read_csv("stockMoves.csv", names = ["position", "whiteToMove", "relEval"])

print(evals_train.head())

eval_features = evals_train.copy()
eval_labels = eval_features.pop('relEval')
eval_features = np.array(eval_features)
print(eval_features)

eval_model = tf.keras.Sequential([layers.Dense(64), layers.Dense(1)])

eval_model.compile(loss = tf.losses.MeanSquaredError(),
                      optimizer = tf.optimizers.Adam())

abalone_model.fit(abalone_features, abalone_labels, epochs=10)

