import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import logging
import os

# Suppress messages from yfinance
logging.getLogger('yfinance').setLevel(logging.ERROR)

# Load data from CSV
data = pd.read_csv('./NSE_large_midcap_250.csv')

## Define the date range
start_date = '2024-06-01'
end_date = '2024-06-10'

# Create a DataFrame to store volatilities
volatility_data = pd.DataFrame(columns=['Company Name', 'Annualized Volatility'])

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

    # Calculate daily returns
    daily_returns = stock_data['Adj Close'].pct_change()

    # Calculate daily volatility
    daily_volatility = daily_returns.std()

    # Calculate annualized volatility
    annualized_volatility = daily_volatility * (252**0.5)

    # Append to the DataFrame using concat
    new_row = pd.DataFrame({
        'Company Name': [company_name],
        'Annualized Volatility': [annualized_volatility]
    })
    volatility_data = pd.concat([volatility_data, new_row], ignore_index=True)

# Sort the data by annualized volatility in ascending order and select the top 30
volatility_data_30_least = volatility_data.sort_values(by='Annualized Volatility').head(30)

# Plotting
plt.figure(figsize=(12, 8))  # Adjusted for better visibility
plt.bar(volatility_data_30_least['Company Name'], volatility_data_30_least['Annualized Volatility'], color='skyblue')
plt.xlabel('Company Name')
plt.ylabel('Annualized Volatility')
plt.title('30 Least Volatile Companies (Annualized Volatility)')
plt.xticks(rotation=90)  # Rotate company names for better visibility
plt.tight_layout()  # Adjust layout to make room for label

file_path = os.path.join(data_directory, "30_least_volatile_stocks.png")
plt.savefig(file_path)


# Sort the data by annualized volatility in ascending order and select the top 30
volatility_data_30_most = volatility_data.sort_values(by='Annualized Volatility').tail(30)

# Plotting
plt.figure(figsize=(12, 8))  # Adjusted for better visibility
plt.bar(volatility_data_30_most['Company Name'], volatility_data_30_least['Annualized Volatility'], color='skyblue')
plt.xlabel('Company Name')
plt.ylabel('Annualized Volatility')
plt.title('30 Most Volatile Companies (Annualized Volatility)')
plt.xticks(rotation=90)  # Rotate company names for better visibility
plt.tight_layout()  # Adjust layout to make room for label
file_path = os.path.join(data_directory, "30_most_volatile_stocks.png")
plt.savefig(file_path)

volatility_data.sort_values(by='Annualized Volatility').to_html(f"{data_directory}volatility_data.html")