import pandas as pd
import sys

def ingest_data(filepath):
    print(f"Loading data from {filepath}")
    df = pd.read_csv(filepath)
    print(f"Original shape: {df.shape}")
    return df

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else r'G:/My Drive/URL-Phish_Dataset.csv'
    ingest_data(filepath)
