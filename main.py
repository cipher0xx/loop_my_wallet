import csv
import datetime
import os
import time

import alpaca_trade_api as trade
import pandas as pd
import schedule
import talib as tb
import yfinance as yf

import config
import lib

link: str = "https://paper-api.alpaca.markets"
api = trade.REST(config.key, config.sec, link, api_version='v2')
account = api.get_account()

reward = 2  # target
risk = 1  # stops


def on_data():
    with open('data_sets/company.csv') as j:
        companies = j.read().splitlines()
        for company in companies:
            symbol = company.split(',')[0]
            # mention period: #########################################################################################
            df = yf.download(symbol, period='1h', interval='1h')
            last = df.tail(2)  # y finance gives present time as output at last
            # drop the row with improper time frame
            last_value = last.head(1)  # get last two and get head
            last_value.to_csv(f'data_sets/1hour_timeframe/{symbol}.csv', mode='a', header=False)

    j.close()


def read_data():
    # clear old buy,sell data
    f = open('data_sets/buy_stock.csv', "w+")
    f.close()

    # loop each pattern and company
    for index_name in lib.pattern_symbols:
        pattern_function = getattr(tb, index_name)  # string to attribute
        data_files = os.listdir(f'data_sets/1hour_timeframe/')
        for file_name in data_files:
            # mention (df['Open'], df['High'], df['Low'], df['Close'])in csv
            df = pd.read_csv(f'data_sets/1hour_timeframe/{file_name}')
            try:
                # warning,copy before editing,ta-lib returns module error: if there is no data in file
                # returns error if no data to read
                results = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
                last_results = results.tail(1).values[0]
                pattern_name = (lib.candlestick_patterns.get(index_name))
                if last_results != 0:
                    if last_results == 100 or 200:
                        trend = 1  # bullish
                        # data rows of csv file
                        try:
                            df = pd.read_csv(f'data_sets/1hour_timeframe/{file_name}')
                            atr = tb.ATR(df['High'], df['Low'], df['Close'], timeperiod=14)
                            macd, macdsignal, macdhist = tb.MACDEXT(df['Close'], fastperiod=3, fastmatype=0,
                                                                    slowperiod=10,
                                                                    slowmatype=0, signalperiod=16, signalmatype=0)
                            g = (atr.iloc[-1])
                            macd = macd.iloc[-2:]
                            macdsignal = macdsignal.iloc[-2:]
                            macd_previous = macd.iloc[0]
                            macd_now = macd.iloc[-1]
                            macdsign_previous = macdsignal.iloc[0]
                            macdsign_now = macdsignal.iloc[-1]
                            flag = -1
                            if macd_now > macdsign_now and macd_previous < macdsign_previous:  # if macd cross the signal
                                sell = 'nan'
                                if flag != 1:
                                    buy = 'buy'
                                    flag = 1
                                else:
                                    buy = 'nan'
                            elif macd_now < macdsign_now and macd_previous > macdsign_previous:
                                buy = 'nan'
                                if flag != 0:
                                    sell = 'sell'
                                    flag = 0
                                else:
                                    buy = 'nan'
                            else:
                                buy = 'nan'
                                sell = 'nan'
                        except OSError:
                            pass
                        write_csv = [file_name, pattern_name, trend, g, buy, sell]
                        rows = [write_csv]

                        # writing to csv file
                        with open('data_sets/buy_stock.csv', 'a') as csvfile:
                            # creating a csv writer object
                            csvwriter = csv.writer(csvfile)

                            # writing the data rows
                            csvwriter.writerows(rows)
                            csvfile.close()
                    else:
                        pass

            except():
                pass


# stop loss,target,risk to win ratio:
# market order
def market_order():
    with open('data_sets/buy_stock.csv') as h:
        buy_name = h.read().splitlines()
        for symbol_sym in buy_name:  # sym = symbol
            buy_order = symbol_sym.split(',')[0]
            atr_stock = symbol_sym.split(',')[3]  # get atr value from row
            buy = symbol_sym.split(',')[4]
            df = pd.read_csv(f'data_sets/1hour_timeframe/{buy_order}')  # get high,low to set target,stoploss
            if atr_stock != "nan" and buy == 'buy':
                target = (round(float(atr_stock), 2) * reward)
                stops = (round(float(atr_stock), 2) * risk)
                close = round(df['Close'].tail(1), 2)
                low = round(df['Low'].tail(1), 2)
                if int(account.buying_power) < int(close * 500):
                    return
                else:
                    try:
                        api.submit_order(
                            symbol=buy_order.split('.')[0],
                            side='buy',
                            type='market',
                            qty='500',
                            time_in_force='day',
                            order_class='bracket',
                            take_profit=dict(
                                limit_price=int(close + target),
                            ),
                            stop_loss=dict(
                                stop_price=int(low - stops),
                                limit_price=int(low - stops)))
                    except trade.rest.APIError:
                        print('fucked')

            else:
                pass

    h.close()


# sleep function
def market_handler():
    schedule.every(1).hour.do(on_data, read_data(), market_order())  # note sched only start at 9:30
    while 1:
        schedule.run_pending()
        time.sleep(3599)


schedule.every().monday.at("08:30").do(market_handler)
schedule.every().tuesday.at("08:30").do(market_handler)
schedule.every().wednesday.at("08:30").do(market_handler)
schedule.every().thursday.at("08:30").do(market_handler)
schedule.every().friday.at("08:30").do(market_handler)

# Create time bounds -- program should run between RUN_LB and RUN_UB
RUN_LB = datetime.time(hour=8, minute=25)  # 8am
RUN_UB = datetime.time(hour=16)  # 16pm


# Helper function to determine whether we should be currently running


def should_run():
    # Get the current time
    ct = datetime.datetime.now().time()
    # Compare current time to run bounds
    lbok = RUN_LB <= ct
    ubok = RUN_UB >= ct
    # If the bounds wrap the 24-hour day, use a different check logic
    if RUN_LB > RUN_UB:
        return lbok or ubok
    else:
        return lbok and ubok


# Helper function to determine how far from now RUN_LB is
def get_wait_secs():
    # Get the current datetime
    cd = datetime.datetime.now()
    # Create a datetime with *today's* RUN_LB
    ld = datetime.datetime.combine(datetime.date.today(), RUN_LB)
    # Create a timedelta for the time until *today's* RUN_LB
    td = ld - cd
    # Ignore td days (may be negative), return td.seconds (always positive)
    return td.seconds


while True:
    if should_run():
        schedule.run_pending()
    else:
        wait_secs = get_wait_secs()
        print("Sleeping for %d seconds..." % wait_secs)
        time.sleep(wait_secs)

