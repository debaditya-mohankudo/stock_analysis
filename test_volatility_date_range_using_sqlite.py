"""
To create a single measurement that encapsulates both the direction and the magnitude of the movements in a dataset, we can combine the metrics into a composite score. One way to do this is by defining a Volatility Impact Score that takes into account:

Proportion of Upward and Downward Movements: To account for the balance between up and down movements.
Mean Positive and Negative Returns: To account for the magnitude of these movements.
Volatility: To account for the overall variability.
Here’s how you can construct such a composite score:


VIS=(α⋅upward_volatitlity+β⋅downward_volatility+γ⋅Volatility) / (α + β + γ)
"""

import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine, inspect
import os

# Create an SQLite database engine
engine = create_engine('sqlite:///stock_data.db')

# Function to fetch stock data
def fetch_stock_data(symbol, start_date, end_date):
    table_name = f"{symbol}_{start_date}_{end_date}"
    # Check if the table for the ticker exists in the database
    if inspect(engine).has_table(table_name):
        print(f"Fetching {symbol} data from the database...")
        df = pd.read_sql(table_name, con=engine)
    else:
        print(f"Fetching {symbol} data from Yahoo Finance...")
        df = yf.download(symbol, start=start_date, end=end_date)
        df.to_sql(table_name, con=engine, index=True, if_exists='replace')
    return df

# Function to calculate various metrics
def calculate_metrics(data):
    daily_returns = data.pct_change().dropna()

    # Proportion of Up and Down Movements

    upward_volatility = (daily_returns > 0).std()
    downward_volatility = (daily_returns < 0).std()

    # Volatility
    volatility = daily_returns.std()

    # Trend
    trend = daily_returns.sum()

    return {
        'upward_volatility': upward_volatility,
        'downward_volatility': downward_volatility,
        'volatility': volatility,
        'trend': trend
    }

# Function to calculate Volatility Impact Score (VIS)
def calculate_vis(metrics, alpha=2, beta=2, gamma=1):
    volatility = metrics['volatility']
    upward_volatility = metrics['upward_volatility']
    downward_volatility = metrics['downward_volatility']
    vis = (alpha * volatility + beta * upward_volatility + gamma * downward_volatility) / (alpha + beta + gamma)
    return vis

def calculate_trend(metrics):
    if metrics['trend'] == 0:
        return 'flat'
    elif metrics['trend'] > 0:
        return 'up'
    else:
        return 'down'

# Suppress messages from yfinance
#logging.getLogger('yfinance').setLevel(logging.ERROR)
# csv_file = "NSE_large_midcap_250"
csv_file = "NSE_small_cap_list"
# Load data from CSV
data = pd.read_csv(f"{csv_file}.csv")

# Define the date range
start_date = '2024-06-01'
end_date = '2024-07-20'

# Create a DataFrame to store volatilities
volatility_data = pd.DataFrame(columns=['Company Name', 'VIS', 'Trend'])

# Loop through each row in the DataFrame
for index, row in data.iterrows():
    symbol = row['Symbol'] + ".NS"  # Appending .NS for NSE
    company_name = row['Company Name']

    # Fetch stock data
    stock_data = fetch_stock_data(symbol, start_date, end_date)

    # Calculate metrics
    metrics = calculate_metrics(stock_data['Adj Close'])

    # Calculate VIS
    vis = calculate_vis(metrics)

    # Calculate Trend
    trend = calculate_trend(metrics)

    # Append to the DataFrame using concat
    new_row = pd.DataFrame({
        'Company Name': [company_name],
        'VIS': [vis],
        'Trend': [trend],
        'Start Date': [start_date],
        'End Date': [end_date]
    })
    volatility_data = pd.concat([volatility_data, new_row], ignore_index=True)



data_directory = "./stock_data/"
if not os.path.isdir(data_directory):
    os.mkdir(data_directory)

volatility_data.sort_values(by='VIS').to_html(f"{data_directory}{csv_file}volatility_data.html")