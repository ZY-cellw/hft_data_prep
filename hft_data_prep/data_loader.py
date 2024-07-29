import pandas as pd
import os
from typing import List, Union, Optional
from dateutil.relativedelta import relativedelta

def load_csv_files(directory: str, file_pattern: str = "*.csv") -> pd.DataFrame:
    """
    Load all CSV files from the specified directory.
    
    Args:
    directory (str): Path to the directory containing CSV files.
    file_pattern (str): Pattern to match CSV files. Default is "*.csv".
    
    Returns:
    pd.DataFrame: Combined DataFrame of all loaded CSV files.
    
    Raises:
    FileNotFoundError: If the specified directory does not exist.
    ValueError: If no CSV files are found in the directory.
    pd.errors.EmptyDataError: If any of the CSV files are empty.
    """
    try:
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        all_files = []
        for root, _, files in os.walk(directory):
            csv_files = [os.path.join(root, file) for file in files if file.endswith('.csv')]
            all_files.extend(csv_files)
        
        if not all_files:
            raise ValueError(f"No CSV files found in directory: {directory}")
        
        print(f"Found {len(all_files)} CSV files.")
        
        df_list = []
        for filename in all_files:
            try:
                df = pd.read_csv(filename)
                if df.empty:
                    print(f"Warning: Empty CSV file: {filename}")
                else:
                    df_list.append(df)
            except pd.errors.EmptyDataError:
                print(f"Warning: Empty CSV file: {filename}")
            except Exception as e:
                print(f"Error reading file {filename}: {str(e)}")
        
        if not df_list:
            raise ValueError("No valid data found in any of the CSV files.")
        
        combined_df = pd.concat(df_list, ignore_index=True)
        return combined_df
    
    except Exception as e:
        print(f"An error occurred while loading CSV files: {str(e)}")
        raise

def preprocess_timestamp(combined_df: pd.DataFrame, timestamp: str = 'timestamp') -> pd.DataFrame:
    """
    Preprocess the timestamp column in the DataFrame.
    
    Args:
    combined_df (pd.DataFrame): Input DataFrame.
    timestamp (str): Name of the timestamp column. Default is 'timestamp'.
    
    Returns:
    pd.DataFrame: DataFrame with preprocessed timestamp column.
    
    Raises:
    KeyError: If the specified timestamp column is not found in the DataFrame.
    ValueError: If the timestamp conversion fails.
    """
    try:
        if timestamp not in combined_df.columns:
            raise KeyError(f"Timestamp column '{timestamp}' not found in the DataFrame.")
        
        if combined_df[timestamp].dtype == 'object':
            combined_df[timestamp] = combined_df[timestamp].str.replace('D', ' ')
            combined_df[timestamp] = pd.to_datetime(combined_df[timestamp], format='%Y-%m-%d %H:%M:%S.%f', errors='coerce')
            
            if combined_df[timestamp].isnull().any():
                print(f"Warning: Some timestamp values could not be parsed. They have been set to NaT.")
        
        return combined_df
    
    except Exception as e:
        print(f"An error occurred while preprocessing timestamp: {str(e)}")
        raise

def interval_to_relativedelta(interval: str) -> relativedelta:
    """
    Convert interval string to relativedelta object.
    
    Args:
    interval (str): String representing the interval.
    
    Returns:
    relativedelta: Corresponding relativedelta object.
    
    Raises:
    ValueError: If an invalid interval is provided.
    """
    intervals = {
        "1d": relativedelta(days=1),
        "1wk": relativedelta(weeks=1),
        "1mo": relativedelta(months=1),
        "3mo": relativedelta(months=3),
        "1y": relativedelta(years=1)
    }
    
    if interval not in intervals:
        raise ValueError(f"Invalid interval: {interval}. Valid intervals are: {', '.join(intervals.keys())}")
    
    return intervals[interval]

def filter_data(combined_df: pd.DataFrame, 
                tickers: Optional[Union[str, List[str]]] = None, 
                start_time: Optional[str] = None, 
                end_time: Optional[str] = None,
                interval: Optional[str] = None) -> pd.DataFrame:
    """
    Filter the combined DataFrame for specific tickers and/or time range.
    
    Args:
    combined_df (pd.DataFrame): Input DataFrame.
    tickers (Optional[Union[str, List[str]]]): Ticker or list of tickers to filter.
    start_time (Optional[str]): Start time for filtering.
    end_time (Optional[str]): End time for filtering.
    interval (Optional[str]): Time interval for filtering.
    
    Returns:
    pd.DataFrame: Filtered DataFrame.
    
    Raises:
    ValueError: If invalid filter parameters are provided.
    KeyError: If required columns are missing in the DataFrame.
    """
    try:
        if combined_df.empty:
            raise ValueError("The input DataFrame is empty.")
        
        required_columns = ['stockcode', 'timestamp']
        missing_columns = [col for col in required_columns if col not in combined_df.columns]
        if missing_columns:
            raise KeyError(f"Missing required columns: {', '.join(missing_columns)}")
        
        filtered_df = combined_df.copy()
        
        # Preprocess timestamp
        filtered_df = preprocess_timestamp(filtered_df, 'timestamp')
        
        # Filter by ticker(s)
        if tickers:
            if isinstance(tickers, str):
                tickers = [tickers]
            filtered_df = filtered_df[filtered_df['stockcode'].isin(tickers)]
            if filtered_df.empty:
                raise ValueError(f"No data found for the specified ticker(s): {', '.join(tickers)}")
        
        # Filter by time range
        if start_time:
            start_time = pd.to_datetime(start_time)
            filtered_df = filtered_df[filtered_df['timestamp'] >= start_time]
        if end_time:
            end_time = pd.to_datetime(end_time)
            filtered_df = filtered_df[filtered_df['timestamp'] <= end_time]
        
        # Filter by interval
        if interval:
            delta = interval_to_relativedelta(interval)
            if not start_time:
                start_time = filtered_df['timestamp'].min()
            end_time = start_time + delta
            filtered_df = filtered_df[(filtered_df['timestamp'] >= start_time) & 
                                      (filtered_df['timestamp'] < end_time)]
        
        if filtered_df.empty:
            raise ValueError("No data found for the specified filter criteria.")
        
        filtered_df = filtered_df.sort_values(['stockcode', 'timestamp'])
        return filtered_df
    
    except Exception as e:
        print(f"An error occurred while filtering data: {str(e)}")
        raise
