# ========== 来自文件：01_get_data.ipynb ==========
import yfinance as yf
import time
import random

# 各类资产代码说明（和你原来一模一样）
assets = {
    '^GSPC':  'SP500',       # 标普 500 指数
    '^NDX':   'Nasdaq100',   # 纳斯达克 100
    'GLD':    'Gold_ETF',    # 黄金 ETF（SPDR）
    'TLT':    'TBond_20Y',   # 20 年期美债 ETF
    'BTC-USD':'Bitcoin',     # 比特币（2014 年起有数据）
    'DX-Y.NYB':'DXY',        # 美元指数
    '^VIX':   'VIX',         # 恐慌指数
}

# ✅ 修复：分批下载 + 随机延时 + 重试，绕过限流
def safe_download(ticker, start):
    retries = 3
    for i in range(retries):
        try:
            data = yf.download(ticker, start=start, auto_adjust=True, progress=False)['Close']
            time.sleep(random.uniform(1, 3))
            return data
        except Exception as e:
            print(f"重试 {ticker}... {i+1}/3")
            time.sleep(2 ** (i+1))
    return None

# 逐个下载（比批量下载更不容易被封）
prices = {}
for ticker, name in assets.items():
    print(f"下载: {name}")
    data = safe_download(ticker, '1993-01-01')
    if data is not None:
        prices[name] = data

# 合并数据
import pandas as pd
prices = pd.DataFrame(prices)
prices_monthly = prices.resample('ME').last()
prices_monthly.to_csv('../data_raw/assets_raw.csv')

print("✅ 下载完成！")
print(prices_monthly.tail())

# -------------------------

# ========== 来自文件：02_data_clean.ipynb ==========
import pandas as pd
import numpy as np
import os

# 读取原始数据（使用绝对路径）
macro = pd.read_csv(r'C:\Users\zxm_laptop\Desktop\ds2026-G04-T-B2_FedPolicyAssets-main\data_raw\fed_rates_raw.csv',
                    index_col=0, parse_dates=True)
assets = pd.read_csv(r'C:\Users\zxm_laptop\Desktop\ds2026-G04-T-B2_FedPolicyAssets-main\data_raw\assets_raw0515.csv',
                     index_col=0, parse_dates=True)

# 合并
merged = macro.join(assets, how='outer').sort_index()

# 定义周期标签
cycles = [
    ('1994-02', '1995-02', 'hike'),
    ('1995-07', '1998-09', 'cut'),
    ('1999-06', '2000-05', 'hike'),
    ('2001-01', '2003-06', 'cut'),
    ('2004-06', '2006-06', 'hike'),
    ('2007-09', '2015-12', 'cut'),
    ('2015-12', '2018-12', 'hike'),
    ('2019-07', '2022-03', 'cut'),
    ('2022-03', '2023-07', 'hike'),
    ('2024-09', '2025-12', 'cut'),
]

merged['cycle'] = 'neutral'
for start, end, label in cycles:
    mask = (merged.index >= start) & (merged.index <= end)
    merged.loc[mask, 'cycle'] = label

# 确保输出目录存在（自动创建）
output_dir = '../data_clean'
os.makedirs(output_dir, exist_ok=True)

# 保存合并后的数据
merged.to_csv(os.path.join(output_dir, 'macro_assets_merged.csv'))

# -------------------------

# ========== 来自文件：03_2_analysis_visualization .ipynb ==========
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

# ========== 来自文件：03_analysis_visualization.ipynb ==========
import pandas as pd
import matplotlib.pyplot as plt

# 中文字体配置，避免标题和坐标文字显示方块
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'STHeiti', 'Heiti TC']
plt.rcParams['axes.unicode_minus'] = False

# 读取资产数据（假设从01_get_data获取）
assets = pd.read_csv('data_raw/assets_raw.csv', index_col=0, parse_dates=True)

# 中文字体配置，避免标题和坐标文字显示方块
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'STHeiti', 'Heiti TC']
plt.rcParams['axes.unicode_minus'] = False

# 资产列
asset_cols = ['SP500', 'Nasdaq100', 'Gold_ETF', 'TBond_20Y', 'Bitcoin']

# 切片2022-01到2024-06
recent = assets['2022-01':'2024-06'][asset_cols].copy()

# 归一化到基期=100
recent_norm = recent / recent.iloc[0] * 100

# 绘制
fig, ax = plt.subplots(figsize=(12, 5))
colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2980b9', '#9b59b6']
for col, color in zip(asset_cols, colors):
    if col in recent_norm.columns:
        ax.plot(recent_norm.index, recent_norm[col], label=col, color=color, linewidth=1.8)

ax.axhline(100, color='gray', linewidth=0.6, linestyle='--')
ax.axvspan('2022-03', '2023-07', alpha=0.1, color='red', label='加息区间')
ax.set_title('2022 年加息周期各类资产表现(2022-01=100)', fontsize=13)
ax.set_ylabel('指数(2022-01 = 100)')
ax.legend(ncol=2)
plt.tight_layout()
plt.savefig('output/fig_assets_in_cycles.png', dpi=150)
print('图表已保存到 output/fig_assets_in_cycles.png')

# -------------------------

# ========== 来自文件：[3-1]fig_fed_rate_history.ipynb ==========

%matplotlib inline

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Micro Hei', 'Heiti TC']
plt.rcParams['axes.unicode_minus'] = False

try:
    df = pd.read_csv(
        'fed_rates_raw.csv',
        index_col=0,       # 把第一列（日期列）设为数据索引
        parse_dates=True   # 自动解析日期格式，适配绘图
    )
 
    print("✅ 数据读取成功！数据前5行预览：")
    print(df.head())
    print(f"\n📊 数据时间范围：{df.index.min().date()} 至 {df.index.max().date()}")
except FileNotFoundError:
    print("❌ 错误：找不到 fed_rates_raw.csv 文件，请确保文件和笔记本在同一文件夹！")
except KeyError as e:
    print(f"❌ 错误：数据中找不到列 {e}，请检查 CSV 文件的列名是否为 'fedfunds'！")

cycles = [
    ('1994-02-01', '1995-02-01', 'hike'),
    ('1998-09-01', '1999-06-01', 'cut'),
    ('1999-06-01', '2000-05-01', 'hike'),
    ('2001-01-01', '2003-06-01', 'cut'),
    ('2004-06-01', '2006-06-01', 'hike'),
    ('2007-09-01', '2008-12-01', 'cut'),
    ('2015-12-01', '2018-12-01', 'hike'),
    ('2019-08-01', '2020-05-01', 'cut'),
    ('2022-03-01', '2023-07-01', 'hike'),
]

fig, ax = plt.subplots(figsize=(14, 5))

ax.plot(
    df.index, 
    df['fedfunds'], 
    color='#2c3e50', 
    linewidth=2,
    label='联邦基金利率'
)

for start_date, end_date, cycle_type in cycles:
    fill_color = '#fadbd8' if cycle_type == 'hike' else '#d5f5e3'
    ax.axvspan(
        pd.Timestamp(start_date),
        pd.Timestamp(end_date),
        alpha=0.4,
        color=fill_color,
        zorder=0  
    )

ax.set_title('美联储联邦基金利率历史走势（1993-2025）', fontsize=13, fontweight='medium')
ax.set_ylabel('利率（%）', fontsize=11)
ax.set_xlabel('日期', fontsize=11)

hike_patch = mpatches.Patch(color='#fadbd8', alpha=0.8, label='加息周期')
cut_patch = mpatches.Patch(color='#d5f5e3', alpha=0.8, label='降息周期')
ax.legend(handles=[hike_patch, cut_patch], loc='upper right', frameon=False)

plt.tight_layout()

plt.savefig('fig_fed_rate_history.png', dpi=150, bbox_inches='tight')
print("\n✅ 图表已保存到当前文件夹：fig_fed_rate_history.png")

plt.show()

# -------------------------

