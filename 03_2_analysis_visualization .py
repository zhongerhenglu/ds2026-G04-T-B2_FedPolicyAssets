import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

os.makedirs('output', exist_ok=True)

# 设置中文字体（Windows 系统推荐 SimHei）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150

# -------------------------

# 读取清洗后的数据
df = pd.read_csv('data_clean/macro_assets_merged.csv', index_col=0, parse_dates=True)
print(f'数据范围: {df.index[0].strftime("%Y-%m")} ~ {df.index[-1].strftime("%Y-%m")}')
print(f'数据维度: {df.shape}')
df.head()

# -------------------------

# 定义分析用的资产列
asset_cols = ['SP500', 'Nasdaq100', 'Gold_ETF', 'TBond_20Y', 'DXY']
available = [col for col in asset_cols if col in df.columns]
print(f'可用资产列: {available}')

# 计算月度收益率（百分比）
returns = df[available].pct_change() * 100
returns['cycle'] = df['cycle']
returns_plot = returns[returns['cycle'] != 'neutral'].dropna()
print(f'有效观测: {len(returns_plot)} 个月')

# -------------------------

# 按周期类型分组计算
cycle_mean = returns_plot.groupby('cycle')[available].mean()
cycle_std  = returns_plot.groupby('cycle')[available].std()

print('各周期类型下的平均月度收益率（%）:')
display(cycle_mean)
print('\n各周期类型下的月度收益率标准差（%）:')
display(cycle_std)

# -------------------------

fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(available))
width = 0.35

hike_vals = [cycle_mean.loc['hike', col] if 'hike' in cycle_mean.index else 0 for col in available]
cut_vals  = [cycle_mean.loc['cut', col] if 'cut' in cycle_mean.index else 0 for col in available]

bars1 = ax.bar(x - width/2, hike_vals, width, label='加息周期',
               color='#e74c3c', alpha=0.8, edgecolor='darkred', linewidth=0.5)
bars2 = ax.bar(x + width/2, cut_vals, width, label='降息周期',
               color='#27ae60', alpha=0.8, edgecolor='darkgreen', linewidth=0.5)

ax.axhline(0, color='black', linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(available, fontsize=11)
ax.set_ylabel('平均月度收益率（%）', fontsize=12)
ax.set_title('各类资产在加息/降息周期的平均月度表现', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)

# 在柱子上显示数值
for bars in [bars1, bars2]:
    for bar in bars:
        h = bar.get_height()
        offset = 3 if h >= 0 else -15
        ax.annotate(f'{h:.2f}%', xy=(bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, offset), textcoords='offset points', ha='center', fontsize=9)

plt.tight_layout()
plt.savefig('output/fig_cycle_performance.png', dpi=150, bbox_inches='tight')
plt.show()
print('已保存: output/fig_cycle_performance.png')

# -------------------------

# 按具体周期明细分析
returns['period'] = '其他'
for i, (start, end, label) in enumerate(cycles, 1):
    period_name = f'{start}~{end}'
    mask = (returns.index >= start) & (returns.index <= end)
    returns.loc[mask, 'period'] = period_name

period_perf = returns.groupby('period')[available].mean()
print('各具体周期资产平均月度收益率（%）:')
display(period_perf.round(2))

# -------------------------

