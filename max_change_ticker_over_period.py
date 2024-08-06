''' 
ouputs a html table with the max changes sorted by ASC
If you want to run on the same day again , you need to delete the sqlite database,
stock_data.db
'''

import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, inspect
from datetime import datetime

# List of CSV files
csv_files = ["NSE_large_midcap_250"]  # Update this list if you have multiple files

# Initialize an empty list to store the DataFrames
dataframes = []

# Loop through the list of CSV files and read each one into a DataFrame
for file in csv_files:
    df = pd.read_csv(f"{file}.csv")
    dataframes.append(df)

# Concatenate all the DataFrames in the list into a single DataFrame
data = pd.concat(dataframes, ignore_index=True)

# Ensure the data contains 'Symbol' column
if 'Symbol' not in data.columns:
    raise ValueError("CSV files must contain 'Symbol' column")

# Define the period for fetching historical data
period = "5d"

# Get today's date
today_date = datetime.today().strftime('%Y-%m-%d')

# Initialize a dictionary to store percentage changes
percentage_changes = []

# Create SQLAlchemy engine
engine = create_engine('sqlite:///stock_data.db')
inspector = inspect(engine)

# Function to check if table exists
def table_exists(symbol):
    table_name = f"{symbol}_{today_date}_{period}"
    return inspector.has_table(table_name)

# Function to create table and store data
def store_data(symbol, df):
    table_name = f"{symbol}_{today_date}_{period}"
    df.to_sql(table_name, engine, if_exists='replace', index=True)

# Function to fetch data from SQLite
def fetch_data(symbol):
    table_name = f"{symbol}_{today_date}_{period}"
    return pd.read_sql(table_name, engine, index_col='Date')

# Fetch data from yfinance for each symbol and calculate the percentage change
for symbol in data['Symbol']:
    if table_exists(symbol):
        stock_data = fetch_data(symbol)
    else:
        stock_data = yf.download(symbol + ".NS", period=period)
        if not stock_data.empty:
            store_data(symbol, stock_data)
    
    if not stock_data.empty:
        initial_close = stock_data['Close'].iloc[0]
        final_close = stock_data['Close'].iloc[-1]
        percentage_change = ((final_close / initial_close) - 1) * 100
        start_date = stock_data.index[0].strftime('%Y-%m-%d')
        percentage_changes.append({
            'Symbol': symbol,
            'Start Date': start_date,
            'Period': period,
            'Percentage Change': percentage_change
        })

# Convert the percentage_changes list to a DataFrame
percentage_changes_df = pd.DataFrame(percentage_changes)

# Sort the DataFrame by Percentage Change in ascending order
sorted_df = percentage_changes_df.sort_values(by='Percentage Change')

# Print the sorted percentage changes as HTML
html_output = sorted_df.to_html(index=False)
print(html_output)

# Optionally, save the HTML to a file
with open("percentage_changes.html", "w") as file:
    file.write(html_output)
