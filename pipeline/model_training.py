import pandas as pd
import numpy as np
import sys
import os
import json
import joblib
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from datetime import datetime

def train_and_evaluate_models(train_path, test_path, models_dir='models'):
    os.makedirs(models_dir, exist_ok=True)
    
    # Load data
    print(f"Loading data from {train_path} and {test_path}...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    X_train = train_df.drop(columns=['label'])
    y_train = train_df['label']
    X_test = test_df.drop(columns=['label'])
    y_test = test_df['label']
    
    models = {
        'LogisticRegression': {
            'model': LogisticRegression(random_state=42, max_iter=1000),
            'params': {
                'C': [0.1, 1.0, 10.0]
            }
        },
        'DecisionTree': {
            'model': DecisionTreeClassifier(random_state=42),
            'params': {
                'max_depth': [None, 10, 20],
                'min_samples_split': [2, 5, 10]
            }
        },
        'RandomForest': {
            'model': RandomForestClassifier(random_state=42),
            'params': {
                'n_estimators': [50, 100],
                'max_depth': [None, 10, 20]
            }
        },
        'XGBoost': {
            'model': XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss'),
            'params': {
                'n_estimators': [50, 100],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            }
        },
        'LightGBM': {
            'model': LGBMClassifier(random_state=42),
            'params': {
                'n_estimators': [50, 100],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [-1, 5, 10]
            }
        }
    }
    
    registry = []
    
    for model_name, config in models.items():
        print(f"\nTraining {model_name}...")
        grid_search = GridSearchCV(
            estimator=config['model'],
            param_grid=config['params'],
            cv=3,
            scoring='f1',
            n_jobs=-1
        )
        
        # Train
        grid_search.fit(X_train, y_train)
        best_model = grid_search.best_estimator_
        
        # Evaluate
        y_pred = best_model.predict(X_test)
        metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred)),
            'recall': float(recall_score(y_test, y_pred)),
            'f1_score': float(f1_score(y_test, y_pred))
        }
        
        # Save model
        model_filename = f"{model_name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
        model_path = os.path.join(models_dir, model_filename)
        joblib.dump(best_model, model_path)
        print(f"Saved {model_name} to {model_path}")
        
        # Update registry info
        registry.append({
            'model_name': model_name,
            'model_path': model_path,
            'best_params': grid_search.best_params_,
            'metrics': metrics
        })
    
    # Save registry
    registry_path = os.path.join(models_dir, 'models_registry.json')
    
    # Merge with existing registry if it exists
    if os.path.exists(registry_path):
        with open(registry_path, 'r') as f:
            existing_registry = json.load(f)
            registry.extend(existing_registry)
            
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=4)
        
    print(f"\nRegistry updated at {registry_path}")

if __name__ == '__main__':
    train_path = sys.argv[1] if len(sys.argv) > 1 else 'data/train.csv'
    test_path = sys.argv[2] if len(sys.argv) > 2 else 'data/test.csv'
    models_dir = sys.argv[3] if len(sys.argv) > 3 else 'models'
    
    train_and_evaluate_models(train_path, test_path, models_dir)
