import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from hft_data_prep.data_loader import load_csv_files, preprocess_timestamp, filter_data


def test_data_loader():
    tickdata_path = os.path.join('/home/kzy/Desktop/hft_data_prep', 'Tickdata')
    combined_df = load_csv_files(tickdata_path)


    # Preprocess timestamp
    combined_df = preprocess_timestamp(combined_df)
    print("Timestamp preprocessed successfully.")
    
    # Filter data for specific tickers and time range
    filtered_df = filter_data(combined_df, 
                                tickers=['CJLU'], 
                                interval= '1mo')
    print(filtered_df['date'].unique())


if __name__ == "__main__":
    test_data_loader()
