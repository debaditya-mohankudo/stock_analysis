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
import yfinance as yf
import pandas as pd
import numpy as np

def calculate_indicators(stock_data: pd.DataFrame) -> pd.DataFrame:
    # Simple Moving Average (SMA)
    stock_data['SMA_20'] = stock_data['Close'].rolling(window=20).mean()
    stock_data['SMA_50'] = stock_data['Close'].rolling(window=50).mean()

    # Exponential Moving Average (EMA)
    stock_data['EMA_20'] = stock_data['Close'].ewm(span=20, adjust=False).mean()
    stock_data['EMA_50'] = stock_data['Close'].ewm(span=50, adjust=False).mean()

    # Bollinger Bands
    stock_data['MiddleBand'] = stock_data['Close'].rolling(window=20).mean()
    stock_data['UpperBand'] = stock_data['MiddleBand'] + 2 * stock_data['Close'].rolling(window=20).std()
    stock_data['LowerBand'] = stock_data['MiddleBand'] - 2 * stock_data['Close'].rolling(window=20).std()

    # Relative Strength Index (RSI)
    delta = stock_data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    RS = gain / loss
    stock_data['RSI'] = 100 - (100 / (1 + RS))

    # MACD
    stock_data['EMA_12'] = stock_data['Close'].ewm(span=12, adjust=False).mean()
    stock_data['EMA_26'] = stock_data['Close'].ewm(span=26, adjust=False).mean()
    stock_data['MACD'] = stock_data['EMA_12'] - stock_data['EMA_26']
    stock_data['Signal_Line'] = stock_data['MACD'].ewm(span=9, adjust=False).mean()

    # Average True Range (ATR)
    stock_data['High-Low'] = stock_data['High'] - stock_data['Low']
    stock_data['High-PrevClose'] = abs(stock_data['High'] - stock_data['Close'].shift(1))
    stock_data['Low-PrevClose'] = abs(stock_data['Low'] - stock_data['Close'].shift(1))
    stock_data['TrueRange'] = stock_data[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)
    stock_data['ATR'] = stock_data['TrueRange'].rolling(window=14).mean()

    # On-Balance Volume (OBV)
    stock_data['Daily_Change'] = stock_data['Close'].diff()
    stock_data['Volume_Change'] = stock_data['Volume'] * np.sign(stock_data['Daily_Change'])
    stock_data['OBV'] = stock_data['Volume_Change'].cumsum()

    print(stock_data.count)
    return stock_data

def determine_trend(stock_data: pd.DataFrame): 
    # Initialize counters
    uptrend_count = 0
    downtrend_count = 0

    # Helper function to increment trend counters
    def update_trend_count(condition):
        nonlocal uptrend_count, downtrend_count
        if condition:
            uptrend_count += 1
        else:
            downtrend_count += 1

    # SMA Trend
    update_trend_count(stock_data['SMA_20'].iloc[-1] > stock_data['SMA_50'].iloc[-1])

    # EMA Trend
    update_trend_count(stock_data['EMA_20'].iloc[-1] > stock_data['EMA_50'].iloc[-1])

    # Bollinger Bands Trend
    update_trend_count(stock_data['Close'].iloc[-1] > stock_data['MiddleBand'].iloc[-1])

    # RSI Trend
    update_trend_count(stock_data['RSI'].iloc[-1] > 50)

    # MACD Trend
    update_trend_count(stock_data['MACD'].iloc[-1] > stock_data['Signal_Line'].iloc[-1])

    # OBV Trend
    update_trend_count(stock_data['OBV'].iloc[-1] > stock_data['OBV'].iloc[-2])

    # Determine overall trend
    if uptrend_count > downtrend_count:
        overall_trend = "Uptrend"
    elif downtrend_count > uptrend_count:
        overall_trend = "Downtrend"
    else:
        overall_trend = "Sideways"

    return overall_trend, uptrend_count, downtrend_count

def get_stock_trend(stock_symbol, period, interval):
    # Fetch historical market data
    stock = yf.Ticker(stock_symbol)
    stock_data = stock.history(period=period, interval=interval)

    # Check if data is fetched
    if stock_data.empty:
        print(f"No data found for {stock_symbol}.")
        return

    # Calculate indicators
    stock_data = calculate_indicators(stock_data)

    # Determine trend
    overall_trend, uptrend_count, downtrend_count = determine_trend(stock_data)

    # Print summary
    print(f"Stock Symbol: {stock_symbol}")
    print(f"Overall Trend: {overall_trend}")
    print(f"Uptrend Indicators: {uptrend_count}")
    print(f"Downtrend Indicators: {downtrend_count}")

    # Print calculated indicators for inspection
    print(stock_data[['Close', 'SMA_20', 'SMA_50', 'EMA_20', 'EMA_50', 'UpperBand', 'MiddleBand', 'LowerBand', 'RSI', 'MACD', 'Signal_Line', 'ATR', 'OBV']].tail(10))

if __name__ == "__main__":
    stock_symbol = input("Enter the stock symbol (e.g., TITAGARH.NS): ")
    PERIOD = "1d" # "1d", "1mo", "3mo", "6mo", "1y"
    INTERVAL = "1m" # "1m", "5m", "15m", "30m", "1h", "1d"
    get_stock_trend(stock_symbol, period=PERIOD, interval=INTERVAL)
