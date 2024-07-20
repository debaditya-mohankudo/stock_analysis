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
import matplotlib.pyplot as plt
import logging
import os

import numpy as np
import pandas as pd

# Function to calculate various metrics
def calculate_metrics(data):
    daily_returns = data.pct_change().dropna()
    
    

    
    # Proportion of Up and Down Movements
    up_movements = (daily_returns > 0).sum()
    upward_volatility = up_movements.std()
    down_movements = (daily_returns < 0).sum()
    downward_volatility = down_movements.std()
    
    # Volatility
    volatility = daily_returns.std()
    
    return {
        'upward_volatility': upward_volatility,
        'downward_volatility': downward_volatility,
        'volatility': volatility
    }

# Function to calculate Volatility Impact Score (VIS)
def calculate_vis(metrics, alpha=2, beta=2, gamma=1):
    volatility = metrics['volatility']
    upward_volatility = metrics['upward_volatility']
    downward_volatility = metrics['downward_volatility']
    vis = (alpha * volatility + beta * upward_volatility + gamma * downward_volatility) / (alpha + beta +gamma)

    return vis

# Suppress messages from yfinance
#logging.getLogger('yfinance').setLevel(logging.ERROR)
#csv_file = "NSE_large_midcap_250"
csv_file = "NSE_small_cap_list"
# Load data from CSV
data = pd.read_csv(f"{csv_file}.csv")

## Define the date range
start_date = '2024-06-02'
end_date = '2024-06-07'

## OR define period and interval ( dynamic data, dont store in csv)
#period = "1d"
#interval = "1m"

# Create a DataFrame to store volatilities
volatility_data = pd.DataFrame(columns=['Company Name', 'VIS'])

# Directory to save CSV files of stock data
data_directory = './stock_data/'
if not os.path.exists(data_directory):
    os.makedirs(data_directory)

# Loop through each row in the DataFrame
for index, row in data.iterrows():
    symbol = row['Symbol'] + ".NS"  # Appending .NS for NSE
    company_name = row['Company Name']
    
    file_path = f"{data_directory}{symbol}_{start_date}_{end_date}.csv"

    # Check if data already exists
    if os.path.exists(file_path):
        # Load stock data from CSV file
        stock_data = pd.read_csv(file_path)
    else:
        # Download stock data
        stock_data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        #stock_data = yf.download(symbol, period="1d", interval="1m", progress=False)
        # Save to CSV
        stock_data.to_csv(file_path)

    # Calculate metrics
    metrics = calculate_metrics(stock_data['Adj Close'])


    # Calculate VIS 
    vis = calculate_vis(metrics)

    # Append to the DataFrame using concat
    new_row = pd.DataFrame({
        'Company Name': [company_name],
        'VIS': [vis]
    })
    volatility_data = pd.concat([volatility_data, new_row], ignore_index=True)

# Sort the data by VIS in ascending order and select the top 30
volatility_data_30_least = volatility_data.sort_values(by='VIS').head(30)

# Plotting
plt.figure(figsize=(12, 8))  # Adjusted for better visibility
plt.bar(volatility_data_30_least['Company Name'], volatility_data_30_least['VIS'], color='skyblue')
plt.xlabel('Company Name')
plt.ylabel('VIS')
plt.title('30 Least Volatile Companies (VIS)')
plt.xticks(rotation=90)  # Rotate company names for better visibility
plt.tight_layout()  # Adjust layout to make room for label

file_path = os.path.join(data_directory, "30_least_volatile_stocks.png")
plt.savefig(file_path)


# Sort the data by VIS in ascending order and select the top 30
volatility_data_30_most = volatility_data.sort_values(by='VIS').tail(30)

# Plotting
plt.figure(figsize=(12, 8))  # Adjusted for better visibility
plt.bar(volatility_data_30_most['Company Name'], volatility_data_30_most['VIS'], color='skyblue')
plt.xlabel('Company Name')
plt.ylabel('VIS')
plt.title('30 Most Volatile Companies (VIS)')
plt.xticks(rotation=90)  # Rotate company names for better visibility
plt.tight_layout()  # Adjust layout to make room for label
file_path = os.path.join(data_directory, "30_most_volatile_stocks.png")
plt.savefig(file_path)

volatility_data.sort_values(by='VIS').to_html(f"{data_directory}{csv_file}volatility_data.html")