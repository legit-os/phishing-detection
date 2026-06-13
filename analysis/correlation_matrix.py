import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Load dataset
df = pd.read_csv(r'G:/My Drive/URL-Phish_Dataset.csv')
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Correlation Matrix Heatmap
corr_matrix = df[numeric_cols].corr()

fig_corr, ax = plt.subplots(figsize=(16, 12))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
masked_corr = np.ma.array(corr_matrix.values, mask=mask)

im = ax.imshow(masked_corr, cmap='RdBu_r', vmin=-1, vmax=1, aspect='equal')
ax.set_xticks(range(len(numeric_cols)))
ax.set_yticks(range(len(numeric_cols)))
ax.set_xticklabels(numeric_cols, rotation=45, ha='right', fontsize=8)
ax.set_yticklabels(numeric_cols, fontsize=8)

# Add text annotations
for i in range(len(numeric_cols)):
    for j in range(len(numeric_cols)):
        if not mask[i, j]:
            val = corr_matrix.iloc[i, j]
            color = 'white' if abs(val) > 0.6 else 'black'
            ax.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=6, color=color)

fig_corr.colorbar(im, ax=ax, shrink=0.8, label='Correlation')
ax.set_title('Feature Correlation Matrix', fontsize=16, fontweight='bold')
plt.tight_layout()

# High correlation pairs table
high_corr_pairs = []
for i in range(len(corr_matrix.columns)):
    for j in range(i + 1, len(corr_matrix.columns)):
        if abs(corr_matrix.iloc[i, j]) > 0.7:
            high_corr_pairs.append({
                'Feature 1': corr_matrix.columns[i],
                'Feature 2': corr_matrix.columns[j],
                'Correlation': round(corr_matrix.iloc[i, j], 3)
            })

high_corr_df = pd.DataFrame(high_corr_pairs).sort_values('Correlation', key=abs, ascending=False) if high_corr_pairs else pd.DataFrame({'Info': ['No highly correlated feature pairs found (|r| > 0.7)']})
