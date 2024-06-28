### Find Stock trend ( EXPERIMENTAL )
### Get the stock symbol from yahoo finance site

"""
Explanation of Trend Logic:
SMA Trend: 
    If the 20-day SMA is above the 50-day SMA, it indicates an uptrend; otherwise, a downtrend.
EMA Trend: 
    If the 20-day EMA is above the 50-day EMA, it indicates an uptrend; otherwise, a downtrend.
Bollinger Bands Trend: 
    If the closing price is above the middle band, it indicates an uptrend; otherwise, a downtrend.
RSI Trend: 
    If the RSI is above 50, it indicates an uptrend; otherwise, a downtrend.
MACD Trend: 
    If the MACD is above the signal line, it indicates an uptrend; otherwise, a downtrend.
OBV Trend: 
    If the OBV is increasing (current OBV > previous OBV), it indicates an uptrend; otherwise, a downtrend.
"""

""" Explanation of support and resistance

Support and Resistance Levels
Support Level: A support level is a price level where a stock tends to stop falling because there is a lot of buying interest at that level. Think of it as a "floor" that the price typically doesn't go below.
Resistance Level: A resistance level is a price level where a stock tends to stop rising because there is a lot of selling interest at that level. Think of it as a "ceiling" that the price typically doesn't go above.
Pivot Points Method
Pivot Points use the previous day's high, low, and closing prices to calculate potential support and resistance levels for the current day.

Pivot Point (PP): An average of the high, low, and close prices from the previous period. It serves as a central reference point.
Resistance 1 (R1), Resistance 2 (R2), Resistance 3 (R3): Potential resistance levels above the pivot point.
Support 1 (S1), Support 2 (S2), Support 3 (S3): Potential support levels below the pivot point.
Swing Highs and Lows Method
Swing highs and lows are based on recent peaks and troughs in the stock price.

Swing High: The highest price point over a specified recent period. It's a potential resistance level because it's a peak where the price previously reversed.
Swing Low: The lowest price point over a specified recent period. It's a potential support level because it's a trough where the price previously reversed.

"""

""" Break out signals

Volume Analysis: 
Breakouts are often accompanied by increased trading volume. A significant increase in volume can indicate strong interest and momentum.

Price Patterns: 
Certain price patterns, such as triangles, flags, pennants, and rectangles, can signal a potential breakout. When the price breaks out of these patterns, it can be an indicator of a strong move.

Moving Averages: 
Moving averages can help identify breakout opportunities. When a short-term moving average crosses above a long-term moving average (a bullish crossover), it can indicate a potential breakout.

Bollinger Bands: 
A stock price breaking above the upper Bollinger Band or below the lower Bollinger Band can signal a breakout. However, confirmation with other indicators is recommended.

Relative Strength Index (RSI): 
An RSI above 70 can indicate overbought conditions, while an RSI below 30 can indicate oversold conditions. A stock moving out of these extremes can signal a breakout.

MACD (Moving Average Convergence Divergence): 
A bullish MACD crossover (when the MACD line crosses above the signal line) can indicate a potential breakout.

Support and Resistance Levels: 
Breakouts often occur when a stock moves above a resistance level or below a support level. Identifying key support and resistance levels is crucial.

"""

"""
Triangles: 
 Ascending, descending, or symmetrical triangles.
Flags and Pennants: 
 Small consolidations that form after a sharp price movement.
Rectangles: 
Consolidation patterns where the price bounces between two parallel levels.
"""

# pip install pandas-ta
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema

def calculate_indicators(stock_data: pd.DataFrame) -> pd.DataFrame:
    # Simple Moving Average (SMA)
    stock_data['SMA_20'] = ta.sma(stock_data['Close'], length=20)
    stock_data['SMA_50'] = ta.sma(stock_data['Close'], length=50)

    # Exponential Moving Average (EMA)
    stock_data['EMA_20'] = ta.ema(stock_data['Close'], length=20)
    stock_data['EMA_50'] = ta.ema(stock_data['Close'], length=50)

    # Bollinger Bands
    bbands = ta.bbands(stock_data['Close'], length=20, std=2)
    stock_data['MiddleBand'] = bbands['BBM_20_2.0']
    stock_data['UpperBand'] = bbands['BBU_20_2.0']
    stock_data['LowerBand'] = bbands['BBL_20_2.0']

    # Relative Strength Index (RSI)
    stock_data['RSI'] = ta.rsi(stock_data['Close'], length=14)

    # MACD
    macd = ta.macd(stock_data['Close'], fast=12, slow=26, signal=9)
    stock_data['MACD'] = macd['MACD_12_26_9']
    stock_data['Signal_Line'] = macd['MACDs_12_26_9']

    # Average True Range (ATR)
    stock_data['ATR'] = ta.atr(stock_data['High'], stock_data['Low'], stock_data['Close'], length=14)

    # On-Balance Volume (OBV)
    stock_data['OBV'] = ta.obv(stock_data['Close'], stock_data['Volume'])

    # ADX, +DI, -DI
    adx = ta.adx(stock_data['High'], stock_data['Low'], stock_data['Close'], length=14)
    stock_data['Plus_DI'] = adx['DMP_14']
    stock_data['Minus_DI'] = adx['DMN_14']
    stock_data['ADX'] = adx['ADX_14']

    # Volume Spike
    stock_data['Volume_Spike'] = stock_data['Volume'] > 2 * stock_data['Volume'].rolling(window=20).mean()

    return stock_data

def format_print(text):
    print(text)
    print('_' * len(text))

def determine_trend(stock_data: pd.DataFrame): 
    # Initialize counters
    uptrend_count = 0
    downtrend_count = 0

    # Helper function to increment trend counters
    def update_trend_count(condition, trend_name=""):
        nonlocal uptrend_count, downtrend_count
        if condition:
            uptrend_count += 1
            format_print("Positive Trend : " + trend_name)
        else:
            downtrend_count += 1
            format_print("Nagative Trend : " + trend_name)
    

    # SMA Trend
    update_trend_count(stock_data['SMA_20'].iat[-1] > stock_data['SMA_50'].iat[-1], "SMA TREND")

    # EMA Trend
    update_trend_count(stock_data['EMA_20'].iat[-1] > stock_data['EMA_50'].iat[-1], "EMA TREND")

    # Bollinger Bands Trend
    update_trend_count(stock_data['Close'].iat[-1] > stock_data['MiddleBand'].iat[-1], "BOLLINGER BANDS TREND")

    # RSI Trend
    update_trend_count(stock_data['RSI'].iat[-1] > 50, "RSI TREND")

    # MACD Trend
    update_trend_count(stock_data['MACD'].iat[-1] > stock_data['Signal_Line'].iat[-1], "MACD TREND")

    # OBV Trend
    update_trend_count(stock_data['OBV'].iat[-1] > stock_data['OBV'].iat[-2], "OBV TREND")

    # ADX Trend
    update_trend_count(stock_data['Plus_DI'].iat[-1] > stock_data['Minus_DI'].iat[-1] and stock_data['ADX'].iat[-1] > 20, "ADX TREND")

    # Determine overall trend
    if uptrend_count > downtrend_count:
        overall_trend = "Uptrend"
    elif downtrend_count > uptrend_count:
        overall_trend = "Downtrend"
    else:
        overall_trend = "Sideways"

    return overall_trend, uptrend_count, downtrend_count



def get_stock_data(stock_symbol, period, interval) -> pd.DataFrame:
    stock = yf.Ticker(stock_symbol)
    stock_data = stock.history(period=period, interval=interval)
    if stock_data.empty:
        print(f"No data found for {stock_symbol}.")
        return None
    format_print(f"Fetching stock data for the period: {period}" )
    format_print(f"Choosing interval: {interval}")
    return stock_data

def calculate_pivot_points(stock_data: pd.DataFrame) -> pd.DataFrame:
    stock_data['Pivot'] = (stock_data['High'] + stock_data['Low'] + stock_data['Close']) / 3
    stock_data['R1'] = 2 * stock_data['Pivot'] - stock_data['Low']
    stock_data['S1'] = 2 * stock_data['Pivot'] - stock_data['High']
    stock_data['R2'] = stock_data['Pivot'] + (stock_data['High'] - stock_data['Low'])
    stock_data['S2'] = stock_data['Pivot'] - (stock_data['High'] - stock_data['Low'])
    stock_data['R3'] = stock_data['High'] + 2 * (stock_data['Pivot'] - stock_data['Low'])
    stock_data['S3'] = stock_data['Low'] - 2 * (stock_data['High'] - stock_data['Pivot'])
    return stock_data

def find_swing_levels(stock_data: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    stock_data['Swing_High'] = stock_data['High'].rolling(window=window, min_periods=1).max()
    stock_data['Swing_Low'] = stock_data['Low'].rolling(window=window, min_periods=1).min()
    return stock_data

def summarize_support_resistance(stock_data: pd.DataFrame) -> None:
    if stock_data is not None:
        stock_data = calculate_pivot_points(stock_data)
        stock_data = find_swing_levels(stock_data, window=5)

        last_row = stock_data.iloc[-1]
        format_print(f"Stock Symbol: {stock_symbol}")
        format_print(f"Close: {last_row['Close']}")
        format_print("Pivot Points:")
        format_print(f"  Pivot: {last_row['Pivot']}")
        format_print(f"  Resistance Levels: R1={last_row['R1']}, R2={last_row['R2']}, R3={last_row['R3']}")
        format_print(f"  Support Levels: S1={last_row['S1']}, S2={last_row['S2']}, S3={last_row['S3']}")
        format_print("Swing Levels:")
        format_print(f"  Swing High: {last_row['Swing_High']}")
        format_print(f"  Swing Low: {last_row['Swing_Low']}")



def get_stock_trend(stock_data: pd.DataFrame) -> None:

    # Calculate indicators
    stock_data = calculate_indicators(stock_data)

    # Determine trend
    overall_trend, uptrend_count, downtrend_count = determine_trend(stock_data)

    # Print summary
    format_print(f"Stock Symbol: {stock_symbol}")
    format_print(f"Overall Trend: {overall_trend}")
    format_print(f"Uptrend Indicators: {uptrend_count}")
    format_print(f"Downtrend Indicators: {downtrend_count}")

    # Print calculated indicators for inspection
    #print(stock_data[['Close', 'SMA_20', 'SMA_50', 'EMA_20', 'EMA_50']].tail(10))
    #print(stock_data[['Close', 'UpperBand', 'MiddleBand', 'LowerBand', 'RSI', 'MACD', 'Signal_Line']].tail(10))
    #print(stock_data[['Close', 'ATR', 'OBV', 'Plus_DI', 'Minus_DI', 'ADX']].tail(10))


def identify_breakout(stock_data: pd.DataFrame) -> None:
    last_row = stock_data.iloc[-1]
    prev_row = stock_data.iloc[-2]

    breakout_signals = []

    # Check Bollinger Bands breakout
    if last_row['Close'] > last_row['UpperBand']:
        breakout_signals.append('Bollinger Band Breakout')

    # Check Moving Averages crossover
    if prev_row['EMA_20'] <= prev_row['EMA_50'] and last_row['EMA_20'] > last_row['EMA_50']:
        breakout_signals.append('EMA Crossover')

    # Check RSI breakout from overbought/oversold
    if prev_row['RSI'] <= 30 and last_row['RSI'] > 30:
        breakout_signals.append('RSI Breakout from Oversold')
    elif prev_row['RSI'] >= 70 and last_row['RSI'] < 70:
        breakout_signals.append('RSI Breakout from Overbought')

    # Check MACD crossover
    if prev_row['MACD'] <= prev_row['Signal_Line'] and last_row['MACD'] > last_row['Signal_Line']:
        breakout_signals.append('MACD Crossover')

    # Check Volume Spike
    if last_row['Volume_Spike']:
        breakout_signals.append('Volume Spike')

    if breakout_signals:
        format_print(f"Potential Breakout Signals: {', '.join(breakout_signals)}")
    else:
        format_print("No breakout signals detected.")



def plot_stock_data(stock_data:pd.DataFrame, stock_symbol, pattern=None):
    plt.figure(figsize=(12, 6))
    plt.plot(stock_data['Close'], label='Close Price')
    if pattern:
        plt.title(f'{stock_symbol} - {pattern}')
    else:
        plt.title(stock_symbol)
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

def find_extrema(stock_data:pd.DataFrame, order:int =5) -> pd.DataFrame:
    stock_data['min'] = stock_data.iloc[argrelextrema(stock_data['Close'].values, np.less_equal, order=order)[0]]['Close']
    stock_data['max'] = stock_data.iloc[argrelextrema(stock_data['Close'].values, np.greater_equal, order=order)[0]]['Close']
    return stock_data

def detect_triangle(stock_data):
    min_points = stock_data.dropna(subset=['min'])
    max_points = stock_data.dropna(subset=['max'])

    if len(min_points) < 2 or len(max_points) < 2:
        return None

    # Calculate the time differences in days
    min_time_diff = (min_points.index[-1] - min_points.index[0]).days
    max_time_diff = (max_points.index[-1] - max_points.index[0]).days

    if min_time_diff == 0 or max_time_diff == 0:
        return None

    # Calculate the slope for min and max points
    min_slope = (min_points['min'].iloc[-1] - min_points['min'].iloc[0]) / min_time_diff
    max_slope = (max_points['max'].iloc[-1] - max_points['max'].iloc[0]) / max_time_diff

    if min_slope > 0 and max_slope < 0:
        return "Symmetrical Triangle"
    elif min_slope > 0 and max_slope > 0:
        return "Ascending Triangle"
    elif min_slope < 0 and max_slope < 0:
        return "Descending Triangle"
    else:
        return None

def detect_rectangle(stock_data: pd.DataFrame):
    min_points = stock_data.dropna(subset=['min'])
    max_points = stock_data.dropna(subset=['max'])

    if len(min_points) < 2 or len(max_points) < 2:
        return None

    if abs(min_points['min'].diff().dropna().mean()) < stock_data['Close'].std() and abs(max_points['max'].diff().dropna().mean()) < stock_data['Close'].std():
        return "Rectangle"
    else:
        return None

def find_price_patterns(stock_data: pd.DataFrame):
    stock_data = find_extrema(stock_data)
    
    triangle_pattern = detect_triangle(stock_data)
    if triangle_pattern:
        #plot_stock_data(stock_data, stock_symbol, pattern=triangle_pattern)
        print(f"Detected pattern: {triangle_pattern}")
    
    rectangle_pattern = detect_rectangle(stock_data)
    if rectangle_pattern:
        #plot_stock_data(stock_data, stock_symbol, pattern=rectangle_pattern)
        print(f"Detected pattern: {rectangle_pattern}")

    if not triangle_pattern and not rectangle_pattern:
        #plot_stock_data(stock_data, stock_symbol)
        print("No significant pattern detected.")

if __name__ == "__main__":
    stock_symbol = input("Enter the stock symbol (e.g., TITAGARH.NS): ")
    PERIOD = "5d" # "1d", "1mo", "3mo", "6mo", "1y"
    INTERVAL = "5m" # "1m", "5m", "15m", "30m", "1h", "1d"
    stock_data = get_stock_data(stock_symbol.upper(), period=PERIOD, interval=INTERVAL)

    get_stock_trend(stock_data=stock_data)
    summarize_support_resistance(stock_data=stock_data)
    identify_breakout(stock_data=stock_data)
    find_price_patterns(stock_data=stock_data)



