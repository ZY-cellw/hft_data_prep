# HFT Data Preparation Library

## Overview

The HFT Data Preparation Library is a Python package designed to streamline the process of loading, preprocessing, and analyzing SGX tick data. This library provides efficient tools for handling SGX tick data, preprocessing timestamps, filtering data based on specific tickers and time ranges, and calculating various metrics such as matching prices and bid-ask spreads.

## Features

- Load multiple CSV files from a directory
- Preprocess timestamp data
- Filter data by ticker symbol, time range, and interval
- Support for various time intervals (daily, weekly, monthly, quarterly, yearly)
- Flexible time filtering for trading sessions
- Calculate morning and closing matching prices
- Determine bid and ask prices for specific timestamps
- Process daily data to compile key statistics

## Installation

You can install the HFT Data Preparation Library using pip:

```
git clone https://github.com/ZY-cellw/hft_data_prep.git
cd hft_data_prep
pip install -e .
```

## Usage

Here's a quick example of how to use the library:

```python
from hft_data_prep import load_csv_files, preprocess_timestamp, filter_data, time_filter, process_daily_data

# Load CSV files
df = load_csv_files("/path/to/csv/directory")

# Preprocess timestamp
df = preprocess_timestamp(df)

# Filter data
filtered_df = filter_data(df, 
                          tickers=["AAPL", "GOOGL"], 
                          start_time="2023-01-01", 
                          end_time="2023-12-31", 
                          interval="1mo")

# Apply time filter
filtered_df = time_filter(filtered_df)

# Process daily data
daily_data = process_daily_data(filtered_df)
```

## API Reference

### `load_csv_files(directory: str, file_pattern: str = "*.csv") -> pd.DataFrame`

Loads all CSV files from the specified directory.

### `preprocess_timestamp(combined_df: pd.DataFrame, timestamp: str = 'timestamp') -> pd.DataFrame`

Preprocesses the timestamp column by replacing 'D' with a space and converting to datetime.

### `filter_data(combined_df: pd.DataFrame, tickers: Optional[Union[str, List[str]]] = None, start_time: Optional[str] = None, end_time: Optional[str] = None, interval: Optional[str] = None) -> pd.DataFrame`

Filters the combined DataFrame based on specified tickers, time range, and interval.

### `time_filter(df: pd.DataFrame) -> pd.DataFrame`

Filters the DataFrame to include only morning (08:58:00-09:02:00) and afternoon (16:59:00-17:16:00) trading sessions.

### `find_morning_matching_price(df: pd.DataFrame) -> tuple[pd.Timestamp, float]`

Finds the morning matching price and its timestamp within the 08:58:00-09:00:00 time range.

### `find_closing_matching_price(df: pd.DataFrame) -> tuple[pd.Timestamp, float]`

Finds the closing matching price and its timestamp within the 17:04:00-17:06:00 time range.

### `find_bid_ask_prices(df: pd.DataFrame, timestamp: pd.Timestamp, is_closing: bool = False) -> tuple[float, float]`

Finds the bid and ask prices for a given timestamp. For closing prices, it searches within the 16:59:00-17:00:00 time range.

### `process_daily_data(filtered_df: pd.DataFrame) -> pd.DataFrame`

Processes daily data to find matching prices and bid-ask prices for each day and ticker.

## Contributing

Contributions to the HFT Data Preparation Library are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or feedback, please open an issue on the GitHub repository.
