import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from hft_data_prep.data_loader import load_csv_files, preprocess_timestamp, filter_data


def test_data_loader():
    tickdata_path = os.path.join('/home/kzy/Desktop/hft_data_prep', 'Tickdata')
    combined_df = load_csv_files(tickdata_path)
    print(combined_df.head())

    # Preprocess timestamp
    combined_df = preprocess_timestamp(combined_df)
    print("Timestamp preprocessed successfully.")
    
    # Filter data for specific tickers and time range
    filtered_df = filter_data(combined_df, 
                                tickers=['CJLU'], 
                                start_time='2023-01-26', 
                                end_time='2023-01-27')
    print("Data filtered successfully.")
    print(filtered_df.head())


if __name__ == "__main__":
    test_data_loader()
