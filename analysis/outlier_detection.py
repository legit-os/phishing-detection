import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv(r'G:/My Drive/URL-Phish_Dataset.csv')
df_s = df.sample(n=5000, random_state=42)
numeric_cols = [c for c in df_s.select_dtypes(include=[np.number]).columns if c != 'label']

n = len(numeric_cols)
ncols = 4
nrows = (n + ncols - 1) // ncols

fig_outliers, axes = plt.subplots(nrows, ncols, figsize=(18, nrows * 3))
axes = axes.flatten()

for i, col in enumerate(numeric_cols):
    data_legit = df_s.loc[df_s['label'] == 0, col].dropna().values
    data_phish = df_s.loc[df_s['label'] == 1, col].dropna().values
    bp = axes[i].boxplot([data_legit, data_phish], labels=['Legit', 'Phish'],
                         patch_artist=True, widths=0.4,
                         medianprops=dict(color='k', linewidth=1.5),
                         flierprops=dict(marker='.', ms=1, alpha=0.15))
    bp['boxes'][0].set(facecolor='#2ecc71', alpha=0.7)
    bp['boxes'][1].set(facecolor='#e74c3c', alpha=0.7)
    axes[i].set_title(col, fontsize=10, fontweight='bold')
    axes[i].grid(axis='y', alpha=0.3)

for j in range(i+1, len(axes)):
    axes[j].set_visible(False)

fig_outliers.suptitle('Outlier Box Plots by Class (All Features)', fontsize=15, fontweight='bold')
plt.tight_layout()
