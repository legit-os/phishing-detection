import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import warnings
warnings.filterwarnings('ignore')

# Load dataset
df = pd.read_csv(r'G:/My Drive/URL-Phish_Dataset.csv')
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Compute skewness
skewness = df[numeric_cols].skew().sort_values(ascending=False)

# Categorize skewness
categories = []
for v in np.abs(skewness.values):
    if v > 1.0:
        categories.append('Highly Skewed (>1.0)')
    elif v > 0.5:
        categories.append('Moderate (0.5-1.0)')
    else:
        categories.append('Symmetric (<0.5)')

skew_summary_df = pd.DataFrame({
    'Feature': skewness.index,
    'Skewness': skewness.values.round(3),
    'Category': categories
})

# Skewness bar chart
fig_skew, ax = plt.subplots(figsize=(12, 8))

colors_skew = ['#e74c3c' if abs(v) > 1 else '#f39c12' if abs(v) > 0.5 else '#2ecc71' for v in skewness.values]

bars = ax.barh(range(len(skewness)), skewness.values, color=colors_skew, edgecolor='black', linewidth=0.5)
ax.set_yticks(range(len(skewness)))
ax.set_yticklabels(skewness.index, fontsize=10)
ax.axvline(x=0, color='black', linewidth=1)
ax.axvline(x=1, color='red', linewidth=1, linestyle='--', alpha=0.7)
ax.axvline(x=-1, color='red', linewidth=1, linestyle='--', alpha=0.7)
ax.set_title('Feature Skewness Analysis', fontsize=16, fontweight='bold')
ax.set_xlabel('Skewness Value', fontsize=12)

# Add value labels on bars
for i, (val, bar) in enumerate(zip(skewness.values, bars)):
    x_pos = val + 0.1 if val >= 0 else val - 0.1
    ha = 'left' if val >= 0 else 'right'
    ax.text(x_pos, i, f'{val:.2f}', va='center', ha=ha, fontsize=8, fontweight='bold')

legend_elements = [
    Patch(facecolor='#2ecc71', label='Symmetric (|skew| < 0.5)'),
    Patch(facecolor='#f39c12', label='Moderate (0.5 <= |skew| <= 1.0)'),
    Patch(facecolor='#e74c3c', label='Highly Skewed (|skew| > 1.0)')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10)
plt.tight_layout()
