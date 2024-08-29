import sys
import os
import pandas as pd
import numpy as np
   
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from hft_data_prep.data_loader import (
    load_csv_files, preprocess_timestamp, filter_data, 
    time_filter, process_daily_data
)

def test_data_loader():
    tickdata_path = os.path.join('/home/kzy/Desktop/hft_data_prep', 'Tickdata')
    combined_df = load_csv_files(tickdata_path)

    combined_df = preprocess_timestamp(combined_df)

    tickers = ['A35']

    filtered_df = filter_data(combined_df,
                              tickers=tickers,
                              interval= '1y')

    filtered_df = time_filter(filtered_df)

    daily_data_df = process_daily_data(filtered_df)

    # Save results
    daily_data_df.to_csv('daily_data_test.csv', index=False)
    print("Data processing completed'")

if __name__ == "__main__":
    test_data_loader()
