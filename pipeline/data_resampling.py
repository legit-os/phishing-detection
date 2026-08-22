import pandas as pd
import sys
import os
from imblearn.over_sampling import SMOTE

def resample_data(input_path: str, output_path: str):
    print(f"Loading training data from {input_path}...")
    df = pd.read_csv(input_path)
    
    if 'label' not in df.columns:
        raise ValueError(f"'label' column missing in {input_path}")
        
    X = df.drop(columns=['label'])
    y = df['label']
    
    print(f"Original class distribution:\n{y.value_counts()}")
    
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X, y)
    
    print(f"Resampled class distribution:\n{y_resampled.value_counts()}")
    
    df_resampled = pd.concat([X_resampled, y_resampled], axis=1)
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    df_resampled.to_csv(output_path, index=False)
    print(f"Saved resampled training data to {output_path} (shape: {df_resampled.shape})")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        input_csv = sys.argv[1]
        output_csv = sys.argv[2] if len(sys.argv) > 2 else input_csv.replace('.csv', '_resampled.csv')
        resample_data(input_csv, output_csv)
    else:
        print("Usage: python data_resampling.py <input_train_csv> [output_train_csv]")
