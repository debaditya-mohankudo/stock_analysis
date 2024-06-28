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

# pip install pandas-ta
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



def get_stock_data(stock_symbol, period, interval):
    stock = yf.Ticker(stock_symbol)
    stock_data = stock.history(period=period, interval=interval)
    if stock_data.empty:
        print(f"No data found for {stock_symbol}.")
        return None
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

def summarize_support_resistance(stock_symbol, period, interval):
    stock_data = get_stock_data(stock_symbol, period, interval)
    if stock_data is not None:
        stock_data = calculate_pivot_points(stock_data)
        stock_data = find_swing_levels(stock_data, window=5)

        last_row = stock_data.iloc[-1]
        print(f"Stock Symbol: {stock_symbol}")
        print(f"Close: {last_row['Close']}")
        print("Pivot Points:")
        print(f"  Pivot: {last_row['Pivot']}")
        print(f"  Resistance Levels: R1={last_row['R1']}, R2={last_row['R2']}, R3={last_row['R3']}")
        print(f"  Support Levels: S1={last_row['S1']}, S2={last_row['S2']}, S3={last_row['S3']}")
        print("Swing Levels:")
        print(f"  Swing High: {last_row['Swing_High']}")
        print(f"  Swing Low: {last_row['Swing_Low']}")


def get_stock_trend(stock_symbol, period, interval):
    # Fetch historical market data
    stock_data = get_stock_data(stock_symbol, period=period, interval=interval)

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
    #print(stock_data[['Close', 'SMA_20', 'SMA_50', 'EMA_20', 'EMA_50']].tail(10))
    #print(stock_data[['Close', 'UpperBand', 'MiddleBand', 'LowerBand', 'RSI', 'MACD', 'Signal_Line']].tail(10))
    #print(stock_data[['Close', 'ATR', 'OBV', 'Plus_DI', 'Minus_DI', 'ADX']].tail(10))



if __name__ == "__main__":
    stock_symbol = input("Enter the stock symbol (e.g., TITAGARH.NS): ")
    PERIOD = "5d" # "1d", "1mo", "3mo", "6mo", "1y"
    INTERVAL = "15m" # "1m", "5m", "15m", "30m", "1h", "1d"
    get_stock_trend(stock_symbol.upper(), period=PERIOD, interval=INTERVAL)
    summarize_support_resistance(stock_symbol, period=PERIOD, interval=INTERVAL)


