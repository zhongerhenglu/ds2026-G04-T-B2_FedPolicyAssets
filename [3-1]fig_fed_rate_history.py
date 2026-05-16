
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

