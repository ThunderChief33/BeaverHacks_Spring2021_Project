import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pandas_datareader as web
import datetime as dt

from sklearn.preprocessing import MinMaxScaler
#from tensorflow.keras.models import Sequential
from sklearn.ensemble import RandomForestClassifier
from tensorflow.keras.layers import Dense, Dropout, LSTM

#load data
company = 'GOOGL'
start = dt.datetime(2012,1,1)
end = dt.datetime(2020,1,1)
future_date = 7

data = web.DataReader(company, 'yahoo', start, end)

#prepare data
scaler = MinMaxScaler(feature_range = (0,1))
scaled_data = scaler.fit_transform(data['Adj Close'].values.reshape(-1,1))
#uses the adjusted close price

prediction_days = 20

x_train = []
y_train = []

for x in range(prediction_days, len(scaled_data)):
    x_train.append(scaled_data[x-prediction_days:x,0])
    y_train.append(scaled_data[x,0])

x_train = np.array(x_train)
y_train = np.array(y_train)

x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1],1))
#print(len(x_train))
#build model (simple tree)


model = Sequential()
#https://www.tensorflow.org/api_docs/python/tf/keras/Sequential
model.add(LSTM(units = 50, return_sequences = True, input_shape = (x_train.shape[1],1)))
model.add(Dropout(0.2))
model.add(LSTM(units = 50, return_sequences = True))
model.add(Dropout(0.2))
model.add(LSTM(units = 50))
model.add(Dropout(0.2))
model.add(Dense(units = 1)) #prediction of next closing day

model.compile(optimizer = 'rmsprop', loss = 'mean_squared_error')

#fitting
model.fit(x_train, y_train, epochs = 20, batch_size = None)
print(model.summary())
#print(model.evaluate())

#model accuracy

test_start = dt.datetime(2020,1,1)
test_end = dt.datetime.now()

test_data = web.DataReader(company, 'yahoo', test_start)
actual_prices = test_data['Adj Close'].values

total_dataset = pd.concat((data['Adj Close'], test_data['Adj Close']), axis = 0)

model_inputs = total_dataset[len(total_dataset) - len(test_data) - prediction_days:].values
model_inputs = model_inputs.reshape(-1,1)
model_inputs = scaler.transform(model_inputs)


x_test = []

for x in range(prediction_days, len(model_inputs + future_date)):
    x_test.append(model_inputs[x-prediction_days:x,0])

x_test = np.array(x_test)


x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

predicted_prices = model.predict(x_test, batch_size=None)
predicted_prices = scaler.inverse_transform(predicted_prices)

# make predictions on test data
real_data = [model_inputs[len(model_inputs) + future_date - prediction_days:len(model_inputs + future_date), 0]]
real_data = np.array(real_data)
real_data = np.reshape(real_data, (real_data.shape[0], real_data.shape[1], 1))

prediction = model.predict(real_data, batch_size=None)
prediction = scaler.inverse_transform(prediction)
print('prediction for next n day is')
print(prediction)

#plotting
plt.plot(actual_prices, color = 'black', label = 'Actual Price')
plt.plot(predicted_prices, color = 'red', label = 'Predicted Price')
plt.title('Share Price')
plt.xlabel('Time (days)')
plt.ylabel('Share Price (USD)')
plt.legend()

plt.show()
