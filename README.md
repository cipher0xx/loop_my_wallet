# loop_my_wallet

## Description

loop_my_wallet a tading bot which uses 50+candlestick patterns,Moving average convergence divergence (MACD) to find entry points and average true range (ATR) to tail stops and targets.By default it is set to trade in Alpaca paper-trade

## Trading Strategy

#1 if a candlestick is recognized

#2 and if its bullish 

#3 if MACD > signalline 

#4 setting targets and stops according to risk/reward

#5 fill order 

## Installation

Install TA-Lib:

Use the package [talib](https://mrjbq7.github.io/ta-lib/) to install

## Install requirements

```bash
pip install requirements.txt
```

## API login

Create a account in [Alpaca.markets](https://app.alpaca.markets/signup)

open config.py
  
key = 'your alpaca key here'

sec = 'your alpaca secret key here'

## Create a Directory

By default program is set to tade in 1hour timeframe

```python
        for company in companies:
            symbol = company.split(',')[0]
            # mention period: #########################################################################################
# if any other time is needed change the  period='' (note time frames:'1m','15m','30m','1h','1d')
# change interval accordingly
            df = yf.download(symbol, period='1h', interval='1h')
            last = df.tail(2)  # y finance gives present time as output at last
            # drop the row with improper time frame
            last_value = last.head(1)  # get last two and get head            
            last_value.to_csv(f'data_sets/1hour_timeframe/{symbol}.csv', mode='a', header=False)
```
Open datasets/create a directory named '1hour_timeframe'

## Risk to reward

Risk to Reward ratio is set to 1/2,it can be modified

```python
link: str = "https://paper-api.alpaca.markets"
api = trade.REST(config.key, config.sec, link, api_version='v2')
account = api.get_account()

reward = 2  # target
risk = 1  # stops
```
main.py #line:19

## Before deploying

>> Make sure timezone is set to (ET) (program will sleep on non-trading hours 16:00 to 9:30(ET)

>> Setup MACD to preferred settings >main.py>line:63 (by defualt: fastperiod=3,slowperiod=10,signalperiod=16)

>> Best if the program is deployed on a cloud server

>>Note:There will not trades placed unitil minimum amount of data in downloaded....
>>Example:if timeframe is set to 1h...order will be terminated for 14 periods.
>>this is because of calculating 'ATR','MACD'

## common Error

>>talib returns error if there is no data to read

>>connection error
