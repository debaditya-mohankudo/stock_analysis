

import asyncio
import json
import yfinance as yf

import os

def play_music(file_path):
    os.system(f"afplay {file_path}") #mac os command afplay


# Function to fetch stock price synchronously
def get_stock_price(ticker):
    stock = yf.Ticker(ticker)
    price = stock.history(period="1d", interval="15m")['Close'].iloc[-1]  # Get the last closing price
    return price

# Asynchronous wrapper to check the stock price and play an alarm if a threshold is crossed
async def check_stock_price(ticker, threshold):
    loop = asyncio.get_running_loop()
    price = await loop.run_in_executor(None, get_stock_price, ticker)
    await asyncio.sleep(2)
    print(f"The current price of {ticker} is {price:.2f}")

    if abs(price - threshold) < 3:
        print(f"Alert: {ticker} has crossed the threshold price of {threshold}")
        play_music('./Alarm-Clock-Short-chosic.com_.mp3')  # Ensure you have an alarm mp3 file in your working directory

async def main():
    # Dictionary of tickers and their price thresholds
    
    '''stock_thresholds = {
        'RVNL.NS': 615,   # Apple with a threshold of $150
        'TITAGARH.NS': 1667,   # Microsoft with a threshold of $280
        'TATAPOWER.NS': 446
    }'''


    while True:
        with open('./stock_price_thresholds.json', 'r') as file:
            stock_thresholds = json.load(file)
        tasks = [check_stock_price(ticker, threshold) for ticker, threshold in stock_thresholds.items()]
        await asyncio.gather(*tasks)
        print("Sleep some time")
        await asyncio.sleep(60)  # Wait for 60 seconds before checking again


if __name__ == "__main__":
    asyncio.run(main())
