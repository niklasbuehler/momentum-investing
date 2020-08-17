Python tools for Momentum Investing
===

A simple python script that implements basic statistical methods to analyze stock data gathered from the Yahoo Finance API.
The implemented methods are the fundamentals needed to apply momentum investing strategies.
Two momentum investing strategies are already implemented as well: the simple _Absolute Momentum Strategy_ and the slightly more complex _Momentum Strategy_.

Start the script in interactive mode using `python -i stocks.py`.

This was developed using Python 3.8.5.

## Theory
Read about the theory behind this [on my website](http://www.niklasbuehler.com/blog/momentum-investing.html).

## Features
**Utility commands:**  
- `loadData(symbols, start_date, end_date)`  
	
	Load stock data of the given symbols in the given time frame.
	
- `init(csv_file)`
	
	Load stockdata from list of symbols.

- `pick(stocks, symbol)`
	
	Pick the data of the given symbol out of the list of given stock data.

- `calcSMA(stock, window_size)`
	
	Calculate the SMA for the given stock data.

- `plot(values, label_x, label_y)`
	
	Plot multiple values in a 2d graph.

- `inspect(stock)`
	
	Plot the given stocks value as well as its SMA200 and SMA38.

- `genPortfolio(stocks)`
	
	Generate portfolio images for the given stocks in an export folder.

- `help()`
	
	Show the help.


**Analysis commands:**  
- `decideAbsolute(stock, rolling, perc)`
	
	Use the absolute momentum to determine if the given stock is in an upward or downward trend.

- `filterAbsolute(stockdata, sma_window, envelope_perc)`
	
	Use the absolute momentum to filter out all stocks currently in a downward trend.

- `rankRelative(stocks, sma_long_size, sma_short_size)`
	
	Rank the given stocks by their relative momentum delta values.

- `printRelative(stocks, limit, sma_long_size, sma_short_size)`
	
	Print the given stocks sorted by their delta values


**Strategies:**  
- `absoluteMomentumStrategy(stocks, sma_window, envelope_perc)`
	
	Apply the absolute momentum strategy.

- `momentumStrategy(stocks, amount)`
	
	Apply the momentum strategy, with a limit on the amount of stocks to invest in.
