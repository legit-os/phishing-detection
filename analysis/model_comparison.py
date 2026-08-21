import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Build absolute path to models/models_registry.json
# Assuming this script is located in the 'analysis' directory of the project
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
registry_path = os.path.join(project_root, 'models', 'models_registry.json')

if os.path.exists(registry_path):
    with open(registry_path, 'r') as f:
        registry = json.load(f)
else:
    registry = []

# Parse metrics into a list of dicts
data = []
for entry in registry:
    metrics = entry.get('metrics', {})
    data.append({
        'Model': entry.get('model_name', 'Unknown'),
        'Accuracy': metrics.get('accuracy', 0),
        'Precision': metrics.get('precision', 0),
        'Recall': metrics.get('recall', 0),
        'F1 Score': metrics.get('f1_score', 0)
    })

# Create a DataFrame. If multiple entries for the same model, we keep the last one.
models_df = pd.DataFrame(data).drop_duplicates(subset=['Model'], keep='last')

# Create a figure for visual comparison
fig_model_comparison = plt.figure(figsize=(14, 8))
if not models_df.empty:
    models = models_df['Model'].tolist()
    
    x = np.arange(len(models))  # the label locations
    width = 0.2  # the width of the bars
    
    ax = fig_model_comparison.add_subplot(111)
    
    # Add bars for each metric
    rects1 = ax.bar(x - 1.5*width, models_df['Accuracy'], width, label='Accuracy', color='#440154')
    rects2 = ax.bar(x - 0.5*width, models_df['Precision'], width, label='Precision', color='#3b528b')
    rects3 = ax.bar(x + 0.5*width, models_df['Recall'], width, label='Recall', color='#21918c')
    rects4 = ax.bar(x + 1.5*width, models_df['F1 Score'], width, label='F1 Score', color='#5ec962')
    
    ax.set_ylabel('Score', fontsize=14)
    ax.set_title('Model Performance Comparison', fontsize=16)
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=45, ha='right')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Metrics')
    ax.set_ylim(0, 1.1)
    
    plt.tight_layout()
else:
    plt.text(0.5, 0.5, f"No models found in registry.\nPath checked: {registry_path}", ha='center', va='center', fontsize=16)
