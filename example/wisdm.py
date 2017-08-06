import sys
sys.path.append('../..')
print(sys.path)

import csv
import numpy as np
from sklearn import preprocessing
from keras.utils.np_utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras_weight_animator import image_saver_callback

def get_data(batch_size):

	def activity_as_int(activity):
	    if activity == 'Walking':
	        return 0
	    elif activity == 'Jogging':
	        return 1
	    elif activity == 'Sitting':
	        return 2
	    elif activity == 'Standing':
	        return 3
	    elif activity == 'Upstairs':
	        return 4
	    elif activity == 'Downstairs':
	        return 5
	    else: 
	        # error
	        return -1

	def get_sliding_windows(X, y, window_size):
	    X_, y_ = [], []
	    for i in range(len(X) - window_size):
	        X_.append(X[i:i + window_size])
	        y_.append(y[i + window_size])
	    return np.array(X_), y_
	    
	data = []
	# load the csv
	print('LOADING DATA')
	with open('../data/WISDM_ar_v1.1/WISDM_ar_v1.1_raw.txt', 'r') as f:
	    reader = csv.reader(f)
	    for row in reader:
	        # some of the data has bad lines, ignore
	        if len(row) == 6 or len(row) == 7:
	            try:
	                z = float(row[5].replace(';', ''))
	            except:
	                continue
	            # create a design matrix with:
	            # user, activity (string), timestamp, x, y, and z accelerometer data
	            data.append((int(row[0]), row[1], int(row[2]), float(row[3]), float(row[4]), z))


	print('PROCESSING DATA')
	x = [d[3] for d in data]
	y = [d[4] for d in data]
	z = [d[5] for d in data]

	# feature-wise min-max scale normalization 
	x = preprocessing.MinMaxScaler(feature_range=(-1.0, 1.0)).fit_transform(x)
	y = preprocessing.MinMaxScaler(feature_range=(-1.0, 1.0)).fit_transform(y)
	z = preprocessing.MinMaxScaler(feature_range=(-1.0, 1.0)).fit_transform(z)

	split = 0.85
	window_size = 60 # 20hz sample rate, so we use a window size of 3 seconds
	targets = to_categorical([activity_as_int(d[1]) for d in data], 6)
	inputs, targets = get_sliding_windows(zip(x, y, z), targets, window_size)

	X_train = inputs[0:int(len(inputs) * split)]
	X_test  = inputs[int(len(inputs) * split):]

	y_train = targets[0:int(len(targets) * split)]
	y_test  = targets[int(len(targets) * split):]

	# make the number of samples a multiple of the batch size, otherwise fit 
	# predict throw errors
	X_train = np.array(X_train[0: len(X_train) - (len(X_train) % batch_size)])
	y_train = np.array(y_train[0: len(y_train) - (len(y_train) % batch_size)])
	X_test  = np.array(X_test[0: len(X_test) - (len(X_test) % batch_size)])
	y_test  = np.array(y_test[0: len(y_test) - (len(y_test) % batch_size)])

	return (X_train, y_train), (X_test, y_test) 

def get_model(window_size):
    
    model = Sequential()
    model.add(LSTM(64, 
                   batch_input_shape=(32, window_size, 3), 
                   return_sequences=False, stateful=False))
    model.add(Activation('relu'))
    model.add(Dropout(0.25))
    model.add(Dense(6))
    model.add(Activation('softmax'))
    
    model.compile(optimizer='rmsprop',
              loss='categorical_crossentropy',
              metrics=['accuracy'])
    
    return model

def main():

	(X_train, y_train), (X_test, y_test) = get_data(32)

	# number of training samples must be a multiple of the batch size (32)
	model = get_model(60) # window size of 60 (3 seconds of accelerometer data @ 20hz)
	# add the weight animator image_saver_callback to save image sequences each 100 batches
	callbacks = [image_saver_callback(model, '../data/wisdm', interval=100, cmap='bwr', render_videos=True)]
	
	# fit and evaluate our model
	print('FITTING MODEL')
	history = model.fit(X_train, y_train, epochs=2, shuffle=True, callbacks=callbacks)
	score = model.evaluate(X_test, np.array(y_test))
	print(score)

if __name__ == '__main__':
	main()
