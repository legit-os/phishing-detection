import pandas as pd
from sklearn.model_selection import train_test_split
import sys
import os

def split_and_save_data(df, output_dir='data'):
    os.makedirs(output_dir, exist_ok=True)
    
    X = df.drop(columns=['label'])
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    train_df = pd.concat([X_train, y_train], axis=1)
    test_df = pd.concat([X_test, y_test], axis=1)
    
    train_df.to_csv(os.path.join(output_dir, 'train.csv'), index=False)
    test_df.to_csv(os.path.join(output_dir, 'test.csv'), index=False)
    df.to_csv(os.path.join(output_dir, 'cleaned_full.csv'), index=False)
    
    print(f"Saved train.csv shape: {train_df.shape}")
    print(f"Saved test.csv shape: {test_df.shape}")
    print(f"Saved cleaned_full.csv shape: {df.shape}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        df = pd.read_csv(sys.argv[1])
        output_dir = sys.argv[2] if len(sys.argv) > 2 else 'data'
        split_and_save_data(df, output_dir)
