import pandas as pd
import os
from typing import List, Union, Optional

def load_csv_files(directory: str, file_pattern: str = "*.csv") -> pd.DataFrame:
    """
    Load all CSV files
    Returns:
    pd.DataFrame: Combined DataFrame of all loaded CSV files.
    """
    all_files = []
    for root, _, files in os.walk(directory):
        csv_files = [os.path.join(root, file) for file in files if file.endswith('.csv')]
        all_files.extend(csv_files)
    
    if not all_files:
        raise ValueError(f"No CSV files found in directory: {directory}")
    
    print(f"Found {len(all_files)} CSV files.")
    
    # Read and combine all CSV files
    df_list = []
    for filename in all_files:
        df = pd.read_csv(filename)
        df_list.append(df)
    
    combined_df = pd.concat(df_list, ignore_index=True)    
    return combined_df

def preprocess_timestamp(combined_df: pd.DataFrame, timestamp: str = 'timestamp') -> pd.DataFrame:
    """
    Returns:
    pd.DataFrame: DataFrame with preprocessed timestamp column.
    """
    if combined_df[timestamp].dtype == 'object':
        combined_df[timestamp] = combined_df[timestamp].str.replace('D', ' ')
        combined_df[timestamp] = pd.to_datetime(combined_df[timestamp], format='%Y-%m-%d %H:%M:%S.%f')
    return combined_df

def filter_data(combined_df: pd.DataFrame, 
                tickers: Optional[Union[str, List[str]]] = None, 
                start_time: Optional[str] = None, 
                end_time: Optional[str] = None) -> pd.DataFrame:
    """
    Filter the combined DataFrame for specific tickers and/or time range.
    Returns:
    pd.DataFrame: Filtered DataFrame.
    """
    filtered_df = combined_df.copy()
    
    # Preprocess timestamp
    filtered_df = preprocess_timestamp(filtered_df, 'timestamp')
    
    # Filter by ticker(s)
    if tickers:
        if isinstance(tickers, str):
            tickers = [tickers]
        filtered_df = filtered_df[filtered_df['stockcode'].isin(tickers)]
    
    # Filter by time range
    if start_time:
        start_time = pd.to_datetime(start_time)
        filtered_df = filtered_df[filtered_df['timestamp'] >= start_time]
    if end_time:
        end_time = pd.to_datetime(end_time)
        filtered_df = filtered_df[filtered_df['timestamp'] <= end_time]
    
    print(f"Filtered DataFrame shape: {filtered_df.shape}")
    return filtered_df
