# This .py script takes in a stock, and backtracks the stock trading strategy to derive the theoretical historical performance.
# it is currently using the Red White Blue method with exponetial moving averages (emas)

import pandas as pd    
import numpy as np 
import yfinance as yf 
import datetime as dt 
from pandas_datareader import data as pdr 

yf.pdr_override()
dateNow = dt.datetime.now()
stockName = input("Enter the stock symbol: ")
print(stockName)

startYear = 2019
startMonth = 1
startDay = 1

stockDataStart = dt.datetime(startYear, startMonth, startDay)

dataFrame = pdr.get_data_yahoo(stockName, stockDataStart, dateNow)

# movingAvg = 50
# simpleMovingAvg = "simpleMovingAvg_" + str(movingAvg)
# dataFrame[simpleMovingAvg] = dataFrame.iloc[:,4].rolling(window = movingAvg).mean()

expMovingAvgsUsed=[3,5,8,10,12,15,30,35,40,45,50,60]

for x in expMovingAvgsUsed:
    expMovingAvg = x
    dataFrame["Ema_" + str(expMovingAvg)] = round(dataFrame.iloc[:,4].ewm(span=expMovingAvg, adjust=False).mean(), 2)

print(dataFrame.tail())

positionFlag = 0
num = 0
percentChange = []

# Change this loop below to repurpose for a different trading strategy
for i in dataFrame.index:
    cmin = min(dataFrame["Ema_3"][i], dataFrame["Ema_5"][i], dataFrame["Ema_8"][i], dataFrame["Ema_10"][i], 
                dataFrame["Ema_12"][i], dataFrame["Ema_15"][i])
    cmax = max(dataFrame["Ema_30"][i], dataFrame["Ema_35"][i], dataFrame["Ema_40"][i], dataFrame["Ema_45"][i], 
                dataFrame["Ema_50"][i], dataFrame["Ema_60"][i])
    close = dataFrame["Adj Close"][i]

    if (cmin > cmax):
        print("Red White Blue")
        if (positionFlag== 0):
            buyPrice = close
            positionFlag = 1
            print("Buying now at " + str(buyPrice))

    elif (cmin < cmax):
        print("Blue White Red")
        if (positionFlag == 1):
            positionFlag = 0
            sellPrice = close
            print("Selling now at " + str(sellPrice))
            pc = (sellPrice / buyPrice - 1) * 100
            percentChange.append(pc)

    if (num == dataFrame["Adj Close"].count() - 1 and positionFlag == 1):
        positionFlag = 0
        sellPrice = close
        print("Selling now at " + str(sellPrice))
        pc = (sellPrice / buyPrice - 1) * 100
        percentChange.append(pc)
    num += 1
# Change this loop above to repurpose for a different trading strategy
print(percentChange)


# This section below calculates summary statistics
gains = 0
numGains = 0
losses = 0
numLosses = 0
totalReturn = 1

for i in percentChange:
    if (i > 0):
        gains += i
        numGains += 1
    else:
        losses += i
        numLosses += 1
    totalReturn = totalReturn * ((i / 100) +1)

totalReturn = round((totalReturn - 1) * 100, 2)   

if (numGains > 0):
    avgGain = gains / numGains
    maxReturn = str(max(percentChange))
else:
    avgGain = 0
    maxReturn = "undefined"

if (numLosses > 0):
    avgLoss= losses / numLosses
    maxLoss = str(min(percentChange))
    ratio = str(-avgGain / avgLoss)
else:
    avgLoss = 0
    maxLoss = "undefined"
    ratio = "inf"

if (numGains > 0 or numLosses > 0):
    battingAvg = numGains / (numGains + numLosses)
else:
    battingAvg = 0

print()
print("Results for " + stockName + " going back to " + str(dataFrame.index[0]) + ", Sample size: " + str(numGains + numLosses) + " trades")
print("EMAs used: " + str(expMovingAvgsUsed))
print("Batting Avg: " + str(battingAvg))
print("Gain/loss ratio: " + ratio)
print("Average Gain: " + str(avgGain))
print("Average Loss: " + str(avgLoss))
print("Max Return: " + maxReturn)
print("Max Loss: " + maxLoss)
print("Total return over " + str(numGains + numLosses) + " trades: " + str(totalReturn) + "%")
print()