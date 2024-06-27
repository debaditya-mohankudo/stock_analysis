import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense, LSTM
import math
from sklearn.preprocessing import MinMaxScaler


import yfinance as yf


tata_motors = yf.Ticker('TATAMOTORS.NS')


#  Plotting date vs the close market stock price
tata_motors[-60:].plot('date','close',color="red")
 

 
plt.show()