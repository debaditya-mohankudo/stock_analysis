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

# pip install pandas-ta
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import pandas as pd
import pandas_ta as ta

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

    # Get the last value without using iloc
    last_values = stock_data.tail(1)

    # SMA Trend
    update_trend_count(last_values['SMA_20'].values[0] > last_values['SMA_50'].values[0])

    # EMA Trend
    update_trend_count(last_values['EMA_20'].values[0] > last_values['EMA_50'].values[0])

    # Bollinger Bands Trend
    update_trend_count(last_values['Close'].values[0] > last_values['MiddleBand'].values[0])

    # RSI Trend
    update_trend_count(last_values['RSI'].values[0] > 50)

    # MACD Trend
    update_trend_count(last_values['MACD'].values[0] > last_values['Signal_Line'].values[0])

    # OBV Trend
    update_trend_count(last_values['OBV'].values[0] > stock_data['OBV'].iloc[-2])

    # ADX Trend
    update_trend_count(last_values['Plus_DI'].values[0] > last_values['Minus_DI'].values[0] and last_values['ADX'].values[0] > 20)

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
    print(stock_data[['Close', 'SMA_20', 'SMA_50', 'EMA_20', 'EMA_50', 'UpperBand', 'MiddleBand', 'LowerBand', 'RSI', 'MACD', 'Signal_Line', 'ATR', 'OBV', 'Plus_DI', 'Minus_DI', 'ADX']].tail(10))

if __name__ == "__main__":
    stock_symbol = input("Enter the stock symbol (e.g., TITAGARH.NS): ")
    PERIOD = "1mo" # "1d", "1mo", "3mo", "6mo", "1y"
    INTERVAL = "1h" # "1m", "5m", "15m", "30m", "1h", "1d"
    get_stock_trend(stock_symbol, period=PERIOD, interval=INTERVAL)
