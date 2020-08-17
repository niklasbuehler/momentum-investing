################################################################################
#                          MOMENTUM INVESTING TOOLS                            #
#                             Niklas Bühler, 2020                              #
#          http://www.niklasbuehler.com/blog/momentum-investing.html           #
################################################################################

from pandas_datareader import data
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date, datetime, timedelta
from termcolor import colored
import os
import math

def loadData(symbols, start_date, end_date):
    panel_data = data.DataReader(symbols, 'yahoo', start_date, end_date)
    close = panel_data['Close']
    all_weekdays = pd.date_range(start=start_date, end=end_date, freq='B')
    close = close.reindex(all_weekdays)
    close = close.fillna(method='ffill')
    return close

def init(source, start_date='2000-01-01'):
    symbols = pd.read_csv(source)["Symbol"][:100]
    end_date = date.today().strftime("%Y-%m-%d")
    print("Please wait, fetching stock data for symbols given in "+source+" for time frame "+start_date+" to "+end_date+"...")
    stocks = loadData(symbols, start_date, end_date)
    return stocks

def pick(stocks, symbol):
    return stocks.loc[:,symbol]

def calcSMA(stock, window_size):
    return stock.rolling(window=window_size).mean()

def decideAbsolute(stock, rolling, perc, datestr=""):
    current = stock[-1]
    higher = rolling[-1]*(1 + 0.01*perc)
    lower = rolling[-1]*(1 - 0.01*perc)
    if datestr != "":
        current = getNextPrice(stock, datestr)
        higher = getNextPrice(rolling, datestr)*(1 + 0.01*perc)
        lower = getNextPrice(rolling, datestr)*(1 - 0.01*perc)
    if (current > higher):
        return 1
    elif (current < lower):
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

def plotStocks(values, label_x, label_y):
    fig, ax = plt.subplots(figsize=(16,9))
    ax.set_xlabel(label_x)
    ax.set_ylabel(label_y)
    for symbol in values.columns:
        ax.plot(values.get(symbol).index, values.get(symbol), label=symbol)
    ax.legend()
    plt.show()

def plotValues(values):
    plt.plot(values)
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

def getNextDay(date):
    return (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

def getNextPrice(stock, date):
    stock = stock.fillna(method='bfill')
    price = -1
    while not price >= 0:
        price = stock.get(date, default=-1)
        date = getNextDay(date)
    return price

class Strategy:
    def __init__(self, stocks, investment_sum):
        self.stocks = stocks
        self.investment_sum = investment_sum

class BuyAndHoldStrategy(Strategy):
    def simulate(self, start_date, end_date):
        stock = self.stocks[self.stocks.keys()[0]]
        price_start = getNextPrice(stock, start_date)
        price_end = getNextPrice(stock, end_date)

        amount_bought = math.floor(self.investment_sum / price_start)
        not_invested = self.investment_sum - amount_bought * price_start
        return amount_bought * price_end + not_invested - self.investment_sum

# TODO Marginal cases not considered?
class AbsoluteMomentumStrategy(Strategy):
    def __init__(self, stocks, investment_sum, sma_window=200, sma_envelope=3):
        Strategy.__init__(self, stocks, investment_sum)
        self.sma_window = sma_window
        self.sma_envelope = sma_envelope

    def simulate(self, start_date, end_date):
        date = start_date
        balance = self.investment_sum
        smas = calcSMA(self.stocks, self.sma_window)
        owned_count = [0] * self.stocks.columns.size
        cache_prices = [0] * self.stocks.columns.size
        stock_value = 0
        totals = []
        while date < end_date: # SIMULATE ONE DAY AT A TIME
            stock_value = 0
            for (index, symbol) in zip(range(self.stocks.size), self.stocks):
                cache_prices[index] = getNextPrice(pick(self.stocks, symbol), date)
                stock_value += owned_count[index] * cache_prices[index]
            single_invest = (balance + stock_value) / self.stocks.columns.size
            print(date + ": cash $" + str(balance) + ", total $" + str((stock_value+balance)))
            for (index, symbol) in zip(range(self.stocks.size), self.stocks): # LOOP THROUGH ALL STOCKS
                stock = pick(self.stocks, symbol)
                sma = pick(smas, symbol)
                price = cache_prices[index]
                signal = decideAbsolute(stock, sma, self.sma_envelope, datestr=date)
                if signal < 0: # SELLING SIGNAL
                    if owned_count[index] > 0:
                        print(colored("> Selling " + str(owned_count[index]) + "x " + symbol + " at $" + str(price), "red"))
                        balance += price * owned_count[index]
                        owned_count[index] = 0
                elif signal > 0: # BUYING SIGNAL
                    if single_invest <= 0:
                        print(colored("> Negative single investment amount, not buying", "red"))
                        break
                    already_invested = price * owned_count[index]
                    invest = single_invest - already_invested
                    buy_count = math.floor(invest/price)
                    if buy_count <= 0:
                        break
                    print(colored("> Buying " + (str(buy_count)) + "x " + symbol + " at $" + str(price), "green"))
                    owned_count[index] += buy_count
                    balance -= price * buy_count
            if balance < 0:
                print(colored("! BALANCE NEGATIVE", "red"))
            date = getNextDay(date)
            totals.append(balance + stock_value)
        print("Total balance: " + str(balance + stock_value))
        return totals

class MomentumStrategy(Strategy):
    pass

def help():
    print(colored("=== HELP ===", "green"))
    print(colored("Utility commands:", "green"))
    print(colored("> ", "white"), colored("loadData(symbols, start_date, end_date):", "blue"), colored("Load stock data of the given symbols in the given time frame.", "white"))
    print(colored("> ", "white"), colored("init(csv_file, start_date='2015-01-01'):", "blue"), colored("Fetch stock data from list of symbols.", "white"))
    print(colored("> ", "white"), colored("pick(stocks, symbol):", "blue"), colored("Pick the data of the given symbol out of the list of given stock data.", "white"))
    print(colored("> ", "white"), colored("calcSMA(stock, window_size):", "blue"), colored("Calculate the SMA for the given stock data.", "white"))
    print(colored("> ", "white"), colored("plotStocks(values, label_x, label_y):", "blue"), colored("Plot multiple values in a 2d graph.", "white"))
    print(colored("> ", "white"), colored("plotValues(values):", "blue"), colored("Simply plots an 1d array in a 2d graph.", "white"))
    print(colored("> ", "white"), colored("inspect(stock):", "blue"), colored("Plot the given stocks value as well as its SMA200 and SMA38.", "white"))
    print(colored("> ", "white"), colored("genPortfolio(stocks):", "blue"), colored("Generate portfolio images for the given stocks in an export folder.", "white"))
    print(colored("> ", "white"), colored("help():", "blue"), colored("Show this help.", "white"))
    print()
    print(colored("Analysis commands:", "green"))
    print(colored("> ", "white"), colored("decideAbsolute(stock, rolling, perc, datestr=''):", "blue"), colored("Use the absolute momentum to determine if the given stock is in an upward or downward trend, with an optional datestring argument.", "white"))
    print(colored("> ", "white"), colored("filterAbsolute(stockdata, sma_window, envelope_perc):", "blue"), colored("Use the absolute momentum to filter out all stocks currently in a downward trend.", "white"))
    print(colored("> ", "white"), colored("rankRelative(stocks, sma_long_size, sma_short_size):", "blue"), colored("Rank the given stocks by their relative momentum delta values.", "white"))
    print(colored("> ", "white"), colored("printRelative(stocks, limit, sma_long_size, sma_short_size):", "blue"), colored("Print the given stocks sorted by their delta values.", "white"))
    print("")
    print(colored("Strategies:", "green"))
    print(colored("> ", "white"), colored("absoluteMomentumStrategy(stocks, sma_window, envelope_perc):", "blue"), colored("Apply the absolute momentum strategy.", "white"))
    print(colored("> ", "white"), colored("momentumStrategy(stocks, amount):", "blue"), colored("Apply the momentum strategy, with a limit on the amount of stocks to invest in.", "white"))
    print("")
    print(colored("Simulations:", "green"))
    print(colored("Remember, you can use ^S and ^Q in the terminal for toggling the scroll lock. This is extremely helpful for viewing the logs of these simulations.", "white"))
    print(colored("> ", "white"), colored("strat = Strategy(stocks):", "blue"), colored("Initialize a strategy Strategy on the given stocks. Available strategies are BuyAndHoldStrategy, AbsoluteMomentumStrategy and MomentumStrategy. Some of them have some more, optional parameters.", "white"))
    print(colored("> ", "white"), colored("strat.simulate(start_date, end_date):", "blue"), colored("Simulate the strategy over the given time frame. Returns an array of the current balances of all simulated days.", "white"))
    print()
    print(colored("Visit ", "green"), colored("www.niklasbuehler.com/blog/momentum_investing.html", "magenta"))
    print(colored("Contact me at ", "green"), colored("hi@niklasbuehler.com", "magenta"))
    print(colored("============", "green"))

help()
stocks = init("symbols.csv")
print(colored(">>> stocks = init('symbols.csv')", "green"))

# TODO make report a function that applies a strategy and exports the results
#def report():
    #print("Applying Momentum Strategy for 20 stocks")
    #momentumStrategy(stocks, 20)
    #genPortfolio(stocks)
    #print("Exported portfolio images to export/ folder")
