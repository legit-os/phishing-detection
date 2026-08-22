import json
import pandas as pd
import matplotlib.pyplot as plt
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
registry_path = os.path.join(current_dir, '..', 'models', 'models_registry.json')

with open(registry_path, 'r') as f:
    registry = json.load(f)

data = []
for info in registry:
    model_name = info['model_name']
    metrics = info['metrics']
    metrics['Model'] = model_name
    data.append(metrics)

df = pd.DataFrame(data)
df = df.set_index('Model')

fig, ax = plt.subplots(figsize=(10, 6))
df.plot(kind='bar', ax=ax)
ax.set_title('Model Performance Comparison (After SMOTE)')
ax.set_ylabel('Score')
plt.tight_layout()