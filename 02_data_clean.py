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

