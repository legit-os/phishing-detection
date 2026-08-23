import pandas as pd
import sys

def ingest_data(filepath, output_path=None):
    print(f"Loading data from {filepath}")
    df = pd.read_csv(filepath)
    print(f"Original shape: {df.shape}")
    if output_path:
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
    return df

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'data/input_data.csv'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'data/raw.csv'
    ingest_data(filepath, output_path)
