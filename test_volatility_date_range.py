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
    
    # Mean Absolute Return
    mean_abs_return = daily_returns.abs().mean()
    
    # Mean Positive and Negative Returns
    mean_positive_return = daily_returns[daily_returns > 0].mean()
    mean_negative_return = daily_returns[daily_returns < 0].mean()
    
    # Proportion of Up and Down Movements
    up_movements = (daily_returns > 0).sum()
    down_movements = (daily_returns < 0).sum()
    total_movements = up_movements + down_movements
    proportion_up = up_movements / total_movements
    proportion_down = down_movements / total_movements
    
    # Volatility
    volatility = daily_returns.std()
    
    return {
        'mean_abs_return': mean_abs_return,
        'mean_positive_return': mean_positive_return,
        'mean_negative_return': mean_negative_return,
        'proportion_up': proportion_up,
        'proportion_down': proportion_down,
        'volatility': volatility
    }

# Function to calculate Volatility Impact Score (VIS)
def calculate_vis(metrics, alpha=1, beta=1, gamma=1):
    proportion_diff = metrics['proportion_up'] - metrics['proportion_down']
    mean_return_sum = metrics['mean_positive_return'] + abs(metrics['mean_negative_return'])
    volatility = metrics['volatility']
    
    vis = alpha * proportion_diff + beta * mean_return_sum + gamma * volatility
    return vis

# Suppress messages from yfinance
#logging.getLogger('yfinance').setLevel(logging.ERROR)

# Load data from CSV
data = pd.read_csv('./NSE_large_midcap_250.csv')

## Define the date range
start_date = '2024-06-01'
end_date = '2024-06-10'

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
plt.bar(volatility_data_30_most['Company Name'], volatility_data_30_least['VIS'], color='skyblue')
plt.xlabel('Company Name')
plt.ylabel('VIS')
plt.title('30 Most Volatile Companies (VIS)')
plt.xticks(rotation=90)  # Rotate company names for better visibility
plt.tight_layout()  # Adjust layout to make room for label
file_path = os.path.join(data_directory, "30_most_volatile_stocks.png")
plt.savefig(file_path)

volatility_data.sort_values(by='VIS').to_html(f"{data_directory}volatility_data.html")