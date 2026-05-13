## 作业1链接：
https://github.com/lianxhcn/ds2026/blob/main/homework/readme.md

## 个人作业：
https://github.com/lianxhcn/ds2026/blob/main/homework/ex_P01.md

## 小组作业内容：
https://github.com/lianxhcn/ds2026/blob/main/homework/Team01/T-B2_%E7%BE%8E%E8%81%94%E5%82%A8%E8%B4%A7%E5%B8%81%E6%94%BF%E7%AD%96%E4%B8%8E%E5%85%A8%E7%90%83%E8%B5%84%E4%BA%A7%E4%BB%B7%E6%A0%BC.md

三、项目目录结构
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
