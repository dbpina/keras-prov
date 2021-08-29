import data_utils as du
import os

from keras.optimizers import Adam, SGD

from keras.callbacks import LearningRateScheduler

from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.layers import Embedding, BatchNormalization
from keras.layers import Conv1D, GlobalMaxPooling1D, Conv2D, MaxPooling2D, Flatten

from sklearn.model_selection import train_test_split

import time
import math

import numpy as np

np.random.seed(1000)

x, y = du.load_data()


y_tmp = np.zeros((x.shape[0], 17))

for i in range(0, x.shape[0]):
  y_tmp[i][y[i]] = 1
y = y_tmp

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, shuffle=True)
drop = 0.5

drop = 0.5
epochs = 2
lerate = 0.001

initial_lrate = lerate
epochs_drop = 10.0
adaptation_id = 0

# (3) Create a sequential model
model = Sequential()

# 1st Convolutional Layer
model.add(Conv2D(filters=96, input_shape=(224,224,3), kernel_size=(11,11), strides=(3,3), padding='valid'))
model.add(Activation('relu'))
# Pooling
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2), padding='valid'))
# Batch Normalisation before passing it to the next layer
model.add(BatchNormalization())

# 2nd Convolutional Layer
model.add(Conv2D(filters=256, kernel_size=(11,11), strides=(1,1), padding='valid'))
model.add(Activation('relu'))
# Pooling
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2), padding='valid'))
# Batch Normalisation
model.add(BatchNormalization())

# 3rd Convolutional Layer
model.add(Conv2D(filters=384, kernel_size=(3,3), strides=(1,1), padding='valid'))
model.add(Activation('relu'))
# Batch Normalisation
model.add(BatchNormalization())


# 4th Convolutional Layer
model.add(Conv2D(filters=384, kernel_size=(3,3), strides=(1,1), padding='valid'))
model.add(Activation('relu'))
# Batch Normalisation
model.add(BatchNormalization())

# 5th Convolutional Layer
model.add(Conv2D(filters=256, kernel_size=(3,3), strides=(1,1), padding='valid'))
model.add(Activation('relu'))
# Pooling
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2), padding='valid'))
# Batch Normalisation
model.add(BatchNormalization())


# Passing it to a dense layer
model.add(Flatten())
# 1st Dense Layer
model.add(Dense(4096, input_shape=(224*224*3,)))
model.add(Activation('relu'))
# Add Dropout to prevent overfitting
model.add(Dropout(drop))
# Batch Normalisation
model.add(BatchNormalization())

# 2nd Dense Layer
model.add(Dense(4096))
model.add(Activation('relu'))
# Add Dropout
model.add(Dropout(drop))
# Batch Normalisation
model.add(BatchNormalization())

# 3rd Dense Layer
model.add(Dense(1000))
model.add(Activation('relu'))
# Add Dropout
model.add(Dropout(drop))
# Batch Normalisation
model.add(BatchNormalization())

# Output Layer
model.add(Dense(17))
model.add(Activation('softmax'))


model.summary()

hyps = {"OPTIMIZER_NAME": True,
    "LEARNING_RATE": True,
    "DECAY": True,
    "MOMENTUM": True,
    "NUM_EPOCHS": True,
    "BATCH_SIZE": True,
    "NUM_LAYERS": True}

model.provenance(dataflow_tag="alexnet",
                adaptation=True,
                hyps = hyps)


# learning rate schedule
def step_decay(epoch):
    lrate = initial_lrate * math.pow(drop, math.floor((1+epoch)/epochs_drop))
    return lrate

lrate = LearningRateScheduler(step_decay, verbose=1)

# (4) Compile
opt = Adam(learning_rate=initial_lrate)
#opt = SGD(lr=lerate)

model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])


# (5) Train
model.fit(x_train, y_train, batch_size=64, epochs=epochs, callbacks=[lrate], verbose=1, validation_split=0.2, shuffle=True)

model.evaluate(x_test, y_test)
