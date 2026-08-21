import pandas as pd
import sys

def clean_data(df):
    print("Dropping text columns...")
    df = df.drop(columns=['url', 'dom', 'tld'], errors='ignore')
    
    print("Dropping missing values...")
    df = df.dropna().reset_index(drop=True)
    
    print("Dropping highly correlated columns...")
    cols_to_drop = ['entropy', 'eq_cnt', 'letter_cnt', 'special_cnt', 'url_len']
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
    
    print(f"Dataset shape after cleaning: {df.shape}")
    return df

if __name__ == '__main__':
    if len(sys.argv) > 1:
        df = pd.read_csv(sys.argv[1])
        cleaned_df = clean_data(df)
        if len(sys.argv) > 2:
            cleaned_df.to_csv(sys.argv[2], index=False)
