# T-B2：美联储货币政策与全球资产价格传导

> 难度：⭐⭐⭐ 中等偏难｜类别：宏观经济与国际数据  
> 核心工具：`fredapi` · `yfinance` · `pandas` · `matplotlib`  
> 建议人数：7～8 人｜预计完成时间：1～2 周

---

## 一、项目背景

美联储的货币政策是影响全球资产价格最重要的单一变量之一。2022 年 3 月至 2023 年 7 月，美联储经历了 40 年来最激进的加息周期，联邦基金利率从 0.25% 升至 5.5%，全球股市、债市、黄金、加密货币无不剧烈波动。

本题通过获取 FRED 利率数据和多类资产的价格序列，系统梳理历次加息/降息周期，定量分析不同资产在货币政策转向时的表现规律，是数据驱动理解宏观经济的绝佳案例。

---

## 二、学习目标

完成本题后，你将能够：

- 使用 `fredapi` 获取美联储宏观经济数据（利率、通胀、货币供应量）
- 使用 `yfinance` 获取股指、黄金、债券 ETF 的历史价格
- 根据规则自动划分「加息/降息/平稳」周期并可视化
- 分析不同资产在各周期中的表现特征（平均收益、波动率、最大回撤）
- 理解「紧缩周期 → 资产价格传导」的基本逻辑

---

## 三、项目目录结构

```
T-B2_FedPolicyAssets/
├── readme.md
├── data_raw/
│   ├── fed_rates_raw.csv          ← 联邦基金利率（FRED）
│   ├── m2_raw.csv                 ← M2 货币供应量（FRED）
│   ├── pce_raw.csv                ← PCE 通胀指数（FRED）
│   └── assets_raw.csv             ← 各类资产价格（yfinance）
├── data_clean/
│   ├── macro_monthly.csv          ← 宏观数据月度合并
│   ├── assets_monthly.csv         ← 资产价格月度合并
│   └── cycle_labels.csv           ← 加息/降息周期标签
├── output/
│   ├── fig_fed_rate_history.png
│   ├── fig_assets_in_cycles.png
│   ├── fig_cycle_performance.png
│   └── fig_correlation_heatmap.png
├── 01_get_data.ipynb
├── 02_data_clean_merge.ipynb
└── 03_analysis_visualization.ipynb
```

---

## 四、前置知识：美联储加息周期定义

本题采用以下规则划分周期（已整理，直接使用）：

| 周期 | 起止时间 | 类型 |
|------|----------|------|
| 周期 1 | 1994-02 → 1995-02 | 加息 |
| 周期 2 | 1995-07 → 1998-09 | 降息/平稳 |
| 周期 3 | 1999-06 → 2000-05 | 加息 |
| 周期 4 | 2001-01 → 2003-06 | 降息 |
| 周期 5 | 2004-06 → 2006-06 | 加息 |
| 周期 6 | 2007-09 → 2015-12 | 降息/零利率 |
| 周期 7 | 2015-12 → 2018-12 | 加息 |
| 周期 8 | 2019-07 → 2022-03 | 降息/零利率 |
| 周期 9 | 2022-03 → 2023-07 | 加息（40年最激进） |
| 周期 10 | 2024-09 → 至今 | 降息 |

---

## 五、任务分解

### 任务 1：获取数据（`01_get_data.ipynb`）

#### 1a：FRED 宏观数据

```python
from fredapi import Fred
import pandas as pd
from config import FRED_API_KEY  # 见 T-A3 说明

fred = Fred(api_key=FRED_API_KEY)

# 联邦基金利率目标（有效利率，日度）
fedfunds = fred.get_series('FEDFUNDS', observation_start='1993-01-01')

# M2 货币供应量（月度，十亿美元）
m2 = fred.get_series('M2SL', observation_start='1993-01-01')

# PCE 通胀（月度，同比%）
pce = fred.get_series('PCEPI', observation_start='1993-01-01')
pce_yoy = pce.pct_change(12) * 100  # 转为同比增速

# 整理为 DataFrame
macro = pd.DataFrame({
    'fedfunds': fedfunds,
    'm2': m2,
    'pce_yoy': pce_yoy,
}).resample('ME').last()

macro.to_csv('../data_raw/fed_rates_raw.csv')
print(macro.tail())
```

#### 1b：多类资产价格（yfinance）

```python
import yfinance as yf

# 各类资产代码说明
assets = {
    '^GSPC':  'SP500',       # 标普 500 指数
    '^NDX':   'Nasdaq100',   # 纳斯达克 100
    'GLD':    'Gold_ETF',    # 黄金 ETF（SPDR）
    'TLT':    'TBond_20Y',   # 20 年期美债 ETF
    'BTC-USD':'Bitcoin',     # 比特币（2014 年起有数据）
    'DX-Y.NYB':'DXY',        # 美元指数
    '^VIX':   'VIX',         # 恐慌指数
}

prices = yf.download(
    list(assets.keys()),
    start='1993-01-01',
    auto_adjust=True
)['Close']

prices.columns = [assets[c] for c in prices.columns]
prices_monthly = prices.resample('ME').last()
prices_monthly.to_csv('../data_raw/assets_raw.csv')
print(prices_monthly.tail())
```

---

### 任务 2：数据清洗与周期标注（`02_data_clean_merge.ipynb`）

```python
import pandas as pd
import numpy as np

macro = pd.read_csv('../data_raw/fed_rates_raw.csv',
                    index_col=0, parse_dates=True)
assets = pd.read_csv('../data_raw/assets_raw.csv',
                     index_col=0, parse_dates=True)

# 合并
merged = macro.join(assets, how='outer').sort_index()

# 定义周期标签（直接使用上方表格）
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

merged.to_csv('../data_clean/macro_assets_merged.csv')
```

---

### 任务 3：分析与可视化（`03_analysis_visualization.ipynb`）

#### 图 1：联邦基金利率历史走势（背景色区分加息/降息）

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

df = pd.read_csv('../data_clean/macro_assets_merged.csv',
                 index_col=0, parse_dates=True)

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(df.index, df['fedfunds'], color='#2c3e50', linewidth=2)

# 加息周期背景色（红）
for start, end, label in cycles:
    color = '#fadbd8' if label == 'hike' else '#d5f5e3'
    ax.axvspan(pd.Timestamp(start), pd.Timestamp(end),
               alpha=0.4, color=color, zorder=0)

ax.set_title('美联储联邦基金利率（1993-2025）', fontsize=13)
ax.set_ylabel('利率（%）')
patch_hike = mpatches.Patch(color='#fadbd8', alpha=0.8, label='加息周期')
patch_cut  = mpatches.Patch(color='#d5f5e3', alpha=0.8, label='降息周期')
ax.legend(handles=[patch_hike, patch_cut])
plt.tight_layout()
plt.savefig('../output/fig_fed_rate_history.png', dpi=150)
```

#### 图 2：各类资产在加息 vs 降息周期中的平均月度收益

```python
# 计算月度收益率
asset_cols = ['SP500', 'Nasdaq100', 'Gold_ETF', 'TBond_20Y', 'Bitcoin']
returns = df[asset_cols].pct_change() * 100
returns['cycle'] = df['cycle']

# 按周期分组求均值和标准差
perf = returns.groupby('cycle')[asset_cols].agg(['mean', 'std'])
hike_mean = perf.loc['hike', (slice(None), 'mean')]
cut_mean  = perf.loc['cut',  (slice(None), 'mean')]
hike_mean.index = asset_cols
cut_mean.index  = asset_cols

x = range(len(asset_cols))
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar([i - 0.2 for i in x], hike_mean, width=0.35,
       label='加息周期', color='#e74c3c', alpha=0.8)
ax.bar([i + 0.2 for i in x], cut_mean, width=0.35,
       label='降息周期', color='#27ae60', alpha=0.8)
ax.axhline(0, color='black', linewidth=0.5)
ax.set_xticks(list(x))
ax.set_xticklabels(asset_cols)
ax.set_ylabel('平均月度收益率（%）')
ax.set_title('各类资产在加息/降息周期的平均月度表现', fontsize=13)
ax.legend()
plt.tight_layout()
plt.savefig('../output/fig_cycle_performance.png', dpi=150)
```

#### 图 3：2022 年加息周期各资产走势（最近一次，最有现实意义）

```python
recent = df['2022-01':'2024-06'][asset_cols].copy()
recent_norm = recent / recent.iloc[0] * 100  # 基期 = 100

fig, ax = plt.subplots(figsize=(12, 5))
colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2980b9', '#9b59b6']
for col, color in zip(asset_cols, colors):
    if col in recent_norm.columns:
        ax.plot(recent_norm.index, recent_norm[col],
                label=col, color=color, linewidth=1.8)

ax.axhline(100, color='gray', linewidth=0.6, linestyle='--')
ax.axvspan('2022-03', '2023-07', alpha=0.1, color='red', label='加息区间')
ax.set_title('2022 年加息周期各类资产表现（2022-01=100）', fontsize=13)
ax.set_ylabel('指数（2022-01 = 100）')
ax.legend(ncol=2)
plt.tight_layout()
plt.savefig('../output/fig_assets_in_cycles.png', dpi=150)
```

---

## 六、结果解读指引

- 哪类资产在加息周期受影响最大？与你的直觉是否一致？（提示：长期债券利率敏感性高）
- 黄金在历次加息周期中表现是否一致？有没有例外？如何解释？
- 比特币数据只有约 10 年，能否得出可靠结论？需要对结论的局限性做什么说明？
- 2022 年加息周期与历史相比有何特殊之处（速度、幅度）？对应资产表现是否也更剧烈？

---

## 七、拓展方向（选做）

- 扩展至新兴市场资产（如 MCHI 中国 ETF、EEM 新兴市场 ETF），分析「外溢效应」
- 构建「利率敏感性」指标：对每类资产做联邦基金利率变化与月度收益的回归，估计 β 系数
- 加入 VIX 恐慌指数，分析货币政策转向时市场情绪的变化

---

## 八、AI 辅助提示词

**划分周期时：**
```
我有一列月度联邦基金利率数据，想自动识别加息/降息周期：
- 加息周期：连续 3 个月以上利率上升
- 降息周期：连续 3 个月以上利率下降
请帮我写一个函数，返回每个月所属的周期类型（'hike'/'cut'/'neutral'）。
```

**多时期对比图：**
```
我想画一张图，横轴是距离加息开始的月数（-12 到 +24），
纵轴是各类资产相对加息开始时的累积收益，
多条线代表不同历史加息周期。请帮我整理数据并绘图。
```

---

## 九、参考资源

- FRED 数据库：<https://fred.stlouisfed.org/>
- 联邦基金利率历史：<https://fred.stlouisfed.org/series/FEDFUNDS>
- 美联储官方声明存档：<https://www.federalreserve.gov/monetarypolicy/fomc_historical.htm>
- 课程参考章节：ds2026 第 9 章（金融数据获取）、第 11 章（时序特征）

---

*最后更新：2026-05-10*
