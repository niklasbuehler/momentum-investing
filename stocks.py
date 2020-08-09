################################################################################
#                          MOMENTUM INVESTING TOOLS                            #
#                             Niklas Bühler, 2020                              #
#          http://www.niklasbuehler.com/blog/momentum-investing.html           #
################################################################################

from pandas_datareader import data
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date
from termcolor import colored
import os

def loadData(symbols, start_date, end_date):
    panel_data = data.DataReader(symbols, 'yahoo', start_date, end_date)
    close = panel_data['Close']
    all_weekdays = pd.date_range(start=start_date, end=end_date, freq='B')
    close = close.reindex(all_weekdays)
    close = close.fillna(method='ffill')
    return close

def init(source):
    symbols = pd.read_csv(source)["Symbol"][:100]
    start_date = '2015-01-01'
    end_date = date.today().strftime("%Y-%m-%d")
    stocks = loadData(symbols, start_date, end_date)
    return stocks

def pick(stocks, symbol):
    return stocks.loc[:,symbol]

def calcSMA(stock, window_size):
    return stock.rolling(window=window_size).mean()

def decideAbsolute(stock, rolling, perc):
    current = stock[-1]
    higher = rolling[-1]*(1 + 0.01*perc)
    lower = rolling[-1]*(1 - 0.01*perc)
    if (stock[-1] > higher):
        return 1
    elif (stock[-1] < lower):
        return -1
    else:
        return 0

def filterAbsolute(stockdata, sma_window, envelope_perc):
    stocks = stockdata.copy()
    sma = calcSMA(stocks, sma_window)
    for symbol in stocks.columns:
        stock = stocks.get(symbol)
        absolute = decideAbsolute(stock, sma[symbol], envelope_perc)
        if (absolute < 0):
            stocks = stocks.drop(symbol, axis=1)
    return stocks

def absoluteMomentumStrategy(stocks, sma_window, envelope_perc):
    rolling = calcSMA(stocks, sma_window)
    for symbol in stocks.columns:
        stock = stocks.get(symbol)
        signal = decideAbsolute(stock, rolling[symbol], envelope_perc)
        print(symbol + ":")
        if (signal < 0):
            print(colored("> Negative.", "red"))
        elif (signal > 0):
            print(colored("> Positive.", "green"))
        else:
            print(colored("> Neutral.", "white"))

def rankRelative(stocks, sma_long_size, sma_short_size):
    deltas = []
    for symbol in stocks.columns:
        stock = stocks.get(symbol)
        current = symbol[-1]
        sma_long = calcSMA(stock, sma_long_size)[-1]
        sma_short = calcSMA(stock, sma_short_size)[-1]
        ratio = sma_short / sma_long
        delta = (ratio-1) * 100
        deltas.append(delta)
    data = list(zip(stocks.columns, deltas))
    data.sort(key=lambda tup: tup[1], reverse=True)
    return data

def printRelative(stocks, limit, sma_long_size, sma_short_size):
    relatives = rankRelative(stocks, sma_long_size, sma_short_size)
    print("Rnk Symb Delta")
    for i in range(0, limit):
        if (i >= len(relatives)):
            break
        rank = str(i+1)
        symbol = str(relatives[i][0])
        delta = str(relatives[i][1])
        color = "green" if (relatives[i][1] >= 0) else "red"
        print(colored("#"+rank+" ", "white"), colored(symbol, "white"), colored(delta, color))

def momentumStrategy(stocks, amount):
    preselection = filterAbsolute(stocks, 200, 3)
    printRelative(preselection, amount, 200, 38)

def plot(values, label_x, label_y):
    fig, ax = plt.subplots(figsize=(16,9))
    ax.set_xlabel(label_x)
    ax.set_ylabel(label_y)
    for symbol in values.columns:
        ax.plot(values.get(symbol).index, values.get(symbol), label=symbol)
    ax.legend()
    plt.show()

def inspect(stock):
    sma200 = calcSMA(stock, 200)
    sma38 = calcSMA(stock, 38)

    fig, ax = plt.subplots(figsize=(16,9))
    ax.set_xlabel("Date")
    ax.set_ylabel("Close")
    ax.plot(stock.index, stock, label=stock.name)
    ax.plot(sma38.index, sma38, label=stock.name+" SMA38")
    ax.plot(sma200.index, sma200, label=stock.name+" SMA200")
    ax.legend()
    plt.show()

def genPortfolio(stocks):
    datestr = date.today().strftime("%Y-%m-%d")
    dir = "export/"+datestr+"/"
    os.makedirs(dir, exist_ok = True)
    
    sma200 = calcSMA(stocks, 200)
    sma38 = calcSMA(stocks, 38)

    for symbol in stocks.columns:
        fig, ax = plt.subplots(figsize=(16,9))
        ax.set_xlabel("Date")
        ax.set_ylabel("Close")
        ax.plot(stocks.get(symbol).index, stocks.get(symbol), label=symbol)
        ax.plot(sma38[symbol].index, sma38[symbol], label=symbol+" SMA38")
        ax.plot(sma200[symbol].index, sma200[symbol], label=symbol+" SMA200")
        ax.legend()
        plt.savefig(dir+symbol+'.png')
        plt.close(fig)

def help():
    print(colored("=== HELP ===", "green"))
    print(colored("Utility commands:", "green"))
    print(colored("> ", "white"), colored("loadData(symbols, start_date, end_date):", "blue"), colored("Load stock data of the given symbols in the given time frame.", "white"))
    print(colored("> ", "white"), colored("init(csv_file):", "blue"), colored("Load stockdata from list of symbols.", "white"))
    print(colored("> ", "white"), colored("pick(stocks, symbol):", "blue"), colored("Pick the data of the given symbol out of the list of given stock data.", "white"))
    print(colored("> ", "white"), colored("calcSMA(stock, window_size):", "blue"), colored("Calculate the SMA for the given stock data.", "white"))
    print(colored("> ", "white"), colored("plot(values, label_x, label_y):", "blue"), colored("Plot multiple values in a 2d graph.", "white"))
    print(colored("> ", "white"), colored("inspect(stock):", "blue"), colored("Plot the given stocks value as well as its SMA200 and SMA38.", "white"))
    print(colored("> ", "white"), colored("genPortfolio(stocks):", "blue"), colored("Generate portfolio images for the given stocks in an export folder.", "white"))
    print(colored("> ", "white"), colored("help():", "blue"), colored("Show this help.", "white"))
    print()
    print(colored("Analysis commands:", "green"))
    print(colored("> ", "white"), colored("decideAbsolute(stock, rolling, perc):", "blue"), colored("Use the absolute momentum to determine if the given stock is in an upward or downward trend.", "white"))
    print(colored("> ", "white"), colored("filterAbsolute(stockdata, sma_window, envelope_perc):", "blue"), colored("Use the absolute momentum to filter out all stocks currently in a downward trend.", "white"))
    print(colored("> ", "white"), colored("rankRelative(stocks, sma_long_size, sma_short_size):", "blue"), colored("Rank the given stocks by their relative momentum delta values.", "white"))
    print(colored("> ", "white"), colored("printRelative(stocks, limit, sma_long_size, sma_short_size):", "blue"), colored("Print the given stocks sorted by their delta values.", "white"))
    print("")
    print(colored("Strategies:", "green"))
    print(colored("> ", "white"), colored("absoluteMomentumStrategy(stocks, sma_window, envelope_perc):", "blue"), colored("Apply the absolute momentum strategy.", "white"))
    print(colored("> ", "white"), colored("momentumStrategy(stocks, amount):", "blue"), colored("Apply the momentum strategy, with a limit on the amount of stocks to invest in.", "white"))
    print()
    print(colored("Visit ", "green"), colored("www.niklasbuehler.com/blog/momentum_investing.html", "magenta"))
    print(colored("Contact me at ", "green"), colored("hi@niklasbuehler.com", "magenta"))
    print(colored("============", "green"))

help()

print()
print("Loading initial stock data for symbols given in symbols.csv...")
stocks = init("symbols.csv")
print(colored(">>> stocks = init('symbols.csv')", "green"))
print()
