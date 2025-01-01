import pandas as pd

df = pd.read_csv('admission_dataset.csv')

y = df['Chance of Admit ']
x = df.drop('Chance of Admit ', axis=1)

x_treino, x_teste = x[0:300], x[300:]
y_treino, y_teste = y[0:300], y[300:]

from keras.models import Sequential
from keras.layers import Dense

# Criando a arquitetura da rede neural:
modelo = Sequential()
modelo.add(Dense(units=3, activation='relu', input_dim=x_treino.shape[1]))
modelo.add(Dense(units=1, activation='linear'))

# Treinando a rede neural:
modelo.compile(loss='mse', optimizer='adam', metrics=['mae'])
resultado = modelo.fit(x_treino, y_treino, epochs=200, batch_size=32, validation_data=(x_teste, y_teste))