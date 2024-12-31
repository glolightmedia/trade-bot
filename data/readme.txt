# Define the file path for data/README.txt
data_readme_path = "/mnt/data/TradingBot/data/README.txt"

# Content for the README.txt
data_readme_content = """
# Data Directory

This directory is used for storing data related to the trading bot.

## Purpose
1. **Historical Data**: Store downloaded historical stock data for analysis.
2. **Live Data**: Save snapshots of live data fetched during trading.
3. **Processed Data**: Keep pre-processed data used for machine learning models or trading decisions.

## File Types
- **CSV Files**: For structured data like stock prices or trade logs.
- **JSON Files**: For configuration or unstructured data.

## Usage Notes
- Ensure sufficient storage for large datasets.
- Do not store sensitive information like API keys in this directory.

"""

# Write the README.txt content to data/README.txt
os.makedirs(os.path.dirname(data_readme_path), exist_ok=True)

with open(data_readme_path, "w") as file:
    file.write(data_readme_content)

data_readme_path
