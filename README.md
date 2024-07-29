# HFT Data Preparation Library

## Overview

The HFT Data Preparation Library is a Python package designed to streamline the process of loading, preprocessing, and filtering SGX tick data. 
This library provides efficient tools for handling SGX tick data, preprocessing timestamps, and filtering data based on specific tickers and time ranges.

## Features

Load multiple CSV files from a directory
Preprocess timestamp data
Filter data by ticker symbol, time range, and interval
Support for various time intervals (daily, weekly, monthly, quarterly, yearly)

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
from hft_data_prep import load_csv_files, preprocess_timestamp, filter_data

# Load CSV files
df = sdp.load_csv_files("/path/to/csv/directory")

# Preprocess timestamp
df = sdp.preprocess_timestamp(df)

# Filter data
filtered_df = sdp.filter_data(df, 
                              tickers=["AAPL", "GOOGL"], 
                              start_time="2023-01-01", 
                              end_time="2023-12-31", 
                              interval="1mo")
```

## API Reference

### `load_csv_files(directory: str, file_pattern: str = "*.csv") -> pd.DataFrame`

Loads all CSV files from the specified directory.

### `preprocess_timestamp(combined_df: pd.DataFrame, timestamp: str = 'timestamp') -> pd.DataFrame`

Preprocesses the timestamp column by replacing 'D' with a space and converting to datetime.

### `filter_data(combined_df: pd.DataFrame, tickers: Optional[Union[str, List[str]]] = None, start_time: Optional[str] = None, end_time: Optional[str] = None, interval: Optional[str] = None) -> pd.DataFrame`

Filters the combined DataFrame based on specified tickers, time range, and interval.

## Contributing

Contributions to the HFT Data Preparation Library are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or feedback, please open an issue on the GitHub repository.
