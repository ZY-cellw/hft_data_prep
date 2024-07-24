# HFT Data Preparation Library

## Overview

The HFT Data Preparation Library is a Python package designed to streamline the process of loading, preprocessing, and filtering SGX tick data. 
This library provides efficient tools for handling SGX tick data, preprocessing timestamps, and filtering data based on specific tickers and time ranges.

## Features

- Load and combine multiple CSV files 
- Preprocess timestamp data to ensure consistency
- Filter data by specific tickers and time ranges
- Efficient handling of large datasets

## Installation

You can install the HFT Data Preparation Library using pip:

```
pip install hft_data_prep
```

## Usage

Here's a quick example of how to use the library:

```python
from hft_data_prep import load_csv_files, preprocess_timestamp, filter_data

# Load CSV files
data = load_csv_files("/path/to/your/data/directory")

# Preprocess timestamps
data = preprocess_timestamp(data)

# Filter data
filtered_data = filter_data(data, 
                            tickers=['AAPL', 'MSFT'], 
                            start_time='2023-01-01', 
                            end_time='2023-12-31')

print(filtered_data.head())
```

## API Reference

### `load_csv_files(directory: str, file_pattern: str = "*.csv") -> pd.DataFrame`

Loads all CSV files from the specified directory.

### `preprocess_timestamp(combined_df: pd.DataFrame, timestamp: str = 'timestamp') -> pd.DataFrame`

Preprocesses the timestamp column by replacing 'D' with a space and converting to datetime.

### `filter_data(combined_df: pd.DataFrame, tickers: Optional[Union[str, List[str]]] = None, start_time: Optional[str] = None, end_time: Optional[str] = None) -> pd.DataFrame`

Filters the combined DataFrame for specific tickers and/or time range.

## Contributing

Contributions to the HFT Data Preparation Library are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or feedback, please open an issue on the GitHub repository.
