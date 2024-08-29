import pandas as pd
import numpy as np
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

class OrderBookProcessor:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.clean = self.df.set_index("timestamp")[["order_number", "mp_quantity", "price", "bid_or_ask"]]

    def build_order_history(self, bo2: pd.DataFrame) -> pd.core.groupby.DataFrameGroupBy:
        prev = (
            bo2.groupby("order_number")
            .apply(lambda x: x.pivot(columns="price", values="mp_quantity").shift(1))
            .fillna(0)
        )
        current = (
            bo2.groupby("order_number")
            .apply(lambda x: x.pivot(columns="price", values="mp_quantity"))
            .fillna(0)
        )

        order_history = current - prev
        return order_history.reset_index(0).groupby("order_number")

    def build_mbp(self, bo2: pd.DataFrame, order_type: str) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
        order_history = self.build_order_history(bo2)

        mbp = pd.DataFrame([])

        for _, y in order_history:
            mbp = mbp.add(y.drop("order_number", axis=1), fill_value=0)
        mbp = mbp.sort_index(axis=1).expanding().sum()

        best_price = mbp.copy()
        if order_type == "bid":
            best_price[best_price != 0] = 1
            best_price = best_price.mul(best_price.columns).max(axis=1)
        elif order_type == "ask":
            best_price[best_price != 0] = 1
            best_price = best_price.replace(0, np.nan)
            best_price = best_price.mul(best_price.columns).min(axis=1)

        best_size = mbp.copy()
        best_size[best_size == 0] = None
        if order_type == "bid":
            best_size = best_size.ffill(axis=1).iloc[:, -1]
        elif order_type == "ask":
            best_size = best_size.bfill(axis=1).iloc[:, 0]

        return mbp, best_price, best_size

    def process(self) -> dict[str, pd.Series]:
        bid_mbp, bid_best_price, _ = self.build_mbp(self.clean[self.clean["bid_or_ask"] == 1], "bid")
        ask_mbp, ask_best_price, _ = self.build_mbp(self.clean[self.clean["bid_or_ask"] == 2], "ask")
        
        return {
            'bid_price': bid_best_price,
            'ask_price': ask_best_price
        }

# New function to combine data loading, filtering, and order book processing
def process_orderbook(directory: str, 
                      stock_code: str, 
                      start_time: Optional[str] = None, 
                      end_time: Optional[str] = None,
                      interval: Optional[str] = None) -> dict[str, pd.Series]:
    """
    Load data, filter it, and process the order book.

    Args:
    directory (str): Path to the directory containing CSV files.
    stock_code (str): Stock code to filter data for.
    start_time (Optional[str]): Start time for filtering data.
    end_time (Optional[str]): End time for filtering data.
    interval (Optional[str]): Time interval for filtering data.

    Returns:
    Dict[str, pd.Series]: Dictionary containing 'bid_price' and 'ask_price' Series.
    """
    try:
        # Load data
        combined_df = load_csv_files(directory)
        
        # Filter data
        filtered_df = filter_data(combined_df, 
                                  tickers=stock_code, 
                                  start_time=start_time, 
                                  end_time=end_time,
                                  interval=interval)
        
        # Process order book
        processor = OrderBookProcessor(filtered_df)
        results = processor.process()
        
        return results
    
    
    except Exception as e:
        print(f"An error occurred while processing the order book: {str(e)}")
        raise

def time_filter(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter the DataFrame to include only morning and afternoon trading sessions.

    Args:
    df (pd.DataFrame): Input DataFrame with a 'timestamp' column.

    Returns:
    pd.DataFrame: Filtered DataFrame.
    """
    time = df['timestamp'].dt.time
    morning_mask = (time >= pd.to_datetime('08:58:00').time()) & (time <= pd.to_datetime('09:02:00').time())
    afternoon_mask = (time >= pd.to_datetime('16:59:00').time()) & (time <= pd.to_datetime('17:16:00').time())
    return df[morning_mask | afternoon_mask]

def find_morning_matching_price(df: pd.DataFrame) -> tuple[pd.Timestamp, float]:
    """
    Find the morning matching price and its timestamp.

    Args:
    df (pd.DataFrame): Input DataFrame for a single day.

    Returns:
    tuple: (timestamp, matching_price)
    """
    morning_df = df[(df['timestamp'].dt.time >= pd.to_datetime('08:58:00').time()) & 
                    (df['timestamp'].dt.time <= pd.to_datetime('09:00:00').time())]

    if morning_df.empty:
        return pd.NaT, 0

    most_frequent_timestamp = morning_df['timestamp'].value_counts().idxmax()

    matching_trades = morning_df[(morning_df['timestamp'] == most_frequent_timestamp) & 
                                 (morning_df['change_reason'] == 3) & 
                                 (morning_df['mp_quantity'] != 0)]

    if not matching_trades.empty:
        matching_price = matching_trades['price'].iloc[0]
        return most_frequent_timestamp, matching_price
    else:
        return most_frequent_timestamp, 0

def find_closing_matching_price(df: pd.DataFrame) -> tuple[pd.Timestamp, float]:
    """
    Find the closing matching price and its timestamp.

    Args:
    df (pd.DataFrame): Input DataFrame for a single day.

    Returns:
    tuple: (timestamp, matching_price)
    """
    closing_df = df[(df['timestamp'].dt.time >= pd.to_datetime('17:04:00').time()) & 
                    (df['timestamp'].dt.time <= pd.to_datetime('17:06:00').time())]

    if closing_df.empty:
        return pd.NaT, 0

    most_frequent_timestamp = closing_df['timestamp'].value_counts().idxmax()

    matching_trades = closing_df[(closing_df['timestamp'] == most_frequent_timestamp) & 
                                 (closing_df['change_reason'] == 3) & 
                                 (closing_df['mp_quantity'] != 0)]

    if not matching_trades.empty:
        matching_price = matching_trades['price'].iloc[0]
        return most_frequent_timestamp, matching_price
    else:
        return most_frequent_timestamp, 0

def find_bid_ask_prices(df: pd.DataFrame, timestamp: pd.Timestamp, is_closing: bool = False) -> tuple[float, float]:
    """
    Find the bid and ask prices for a given timestamp.

    Args:
    df (pd.DataFrame): Input DataFrame.
    timestamp (pd.Timestamp): Timestamp to find prices for.
    is_closing (bool): Whether to find closing prices.

    Returns:
    tuple: (bid_price, ask_price)
    """
    if pd.isnull(timestamp):
        return 0, 0

    if is_closing:
        relevant_df = df[(df['timestamp'].dt.time >= pd.to_datetime('16:59:00').time()) & 
                         (df['timestamp'].dt.time <= pd.to_datetime('17:00:00').time())]

        if relevant_df.empty:
            return 0, 0

        bid_df = relevant_df[relevant_df['bid_or_ask'] == 1]
        ask_df = relevant_df[relevant_df['bid_or_ask'] == 2]
    else:
        timestamp_df = df[df['timestamp'] == timestamp]

        if timestamp_df.empty:
            return 0, 0

        bid_df = timestamp_df[timestamp_df['bid_or_ask'] == 1]
        ask_df = timestamp_df[timestamp_df['bid_or_ask'] == 2]

    bid_price = bid_df['bestprice'].iloc[-1] if not bid_df.empty else 0
    ask_price = ask_df['bestprice'].iloc[-1] if not ask_df.empty else 0

    return bid_price, ask_price

def process_daily_data(filtered_df: pd.DataFrame) -> pd.DataFrame:
    """
    Process daily data to find matching prices and bid-ask prices.

    Args:
    filtered_df (pd.DataFrame): Filtered DataFrame containing data for multiple days and tickers.

    Returns:
    pd.DataFrame: Processed daily data.
    """
    daily_data = []
    for (date, ticker), group in filtered_df.groupby([filtered_df['timestamp'].dt.date, 'stockcode']):
        morning_timestamp, morning_matching_price = find_morning_matching_price(group)
        closing_timestamp, closing_matching_price = find_closing_matching_price(group)

        morning_bid_price, morning_ask_price = find_bid_ask_prices(group, morning_timestamp)
        closing_bid_price, closing_ask_price = find_bid_ask_prices(group, closing_timestamp, is_closing=True)

        daily_data.append({
            'date': date,
            'ticker': ticker,
            'morning_matching_timestamp': morning_timestamp,
            'morning_matching_price': morning_matching_price,
            'morning_bid_price': morning_bid_price,
            'morning_ask_price': morning_ask_price,
            'closing_matching_timestamp': closing_timestamp,
            'closing_matching_price': closing_matching_price,
            'closing_bid_price': closing_bid_price,
            'closing_ask_price': closing_ask_price
        })

    return pd.DataFrame(daily_data)
