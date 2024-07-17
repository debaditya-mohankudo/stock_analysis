

import yfinance as yf
import time
import os

def play_music(file_path):
    os.system(f"afplay {file_path}")

def check_stock_price(ticker, threshold):
    stock = yf.Ticker(ticker)
    price = stock.history(period="1d")['Close'].iloc[-1]  # Get the last closing price
    print(f"The current price of {ticker} is {price:.2f}")
    return price >= threshold

def main():
    ticker = "JWL.NS"  # Ticker for JWL , change as needed
    threshold = 670  # Set your price threshold here
    check_interval = 60  # Check every 60 seconds

    while True:
        if check_stock_price(ticker, threshold):
            print(f"Alert: {ticker} has crossed the threshold price of {threshold}")
            play_music('Alarm-Clock-Short-chosic.com_.mp3')  # Path to an alarm sound file
        time.sleep(check_interval)  # Wait before checking again

if __name__ == "__main__":
    main()
