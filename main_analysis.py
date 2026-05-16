# ==========================================================
# 美联储货币政策周期与资产价格传导 · 完整版（零报错 · 纯本地）
# 小组：T-B2
# ==========================================================
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ===================== 路径配置 =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE_DIR, "data_raw")
CLEAN = os.path.join(BASE_DIR, "data_clean")
OUT = os.path.join(BASE_DIR, "output")
os.makedirs(RAW, exist_ok=True)
os.makedirs(CLEAN, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ===================== 1. 本地读取数据 =====================
def load_local_data():
    macro = pd.read_csv(os.path.join(RAW, "fed_rates_raw.csv"), index_col=0, parse_dates=True)
    assets = pd.read_csv(os.path.join(RAW, "assets_raw.csv"), index_col=0, parse_dates=True)
    return macro, assets

# ===================== 2. 周期划分 =====================
def classify_cycles(rate_series):
    change = rate_series.diff()
    regime = ['neutral'] * len(change)
    up = 0
    down = 0
    for i in range(1, len(change)):
        if change.iloc[i] > 0:
            up += 1
            down = 0
        elif change.iloc[i] < 0:
            down += 1
            up = 0
        else:
            up = 0
            down = 0
        if up >= 3:
            regime[i] = 'hike'
        elif down >= 3:
            regime[i] = 'cut'
        else:
            regime[i] = 'neutral'
    return regime

# ===================== 3. 清洗合并 =====================
def clean_and_merge(macro, assets):
    df = macro.join(assets, how='outer').sort_index().ffill(limit=3)
    df['cycle'] = classify_cycles(df['fedfunds'])
    for col in assets.columns:
        try:
            df[f'{col}_ret'] = df[col].pct_change() * 100
        except:
            pass
    df.to_csv(os.path.join(CLEAN, "macro_assets_merged.csv"))
    return df

# ===================== 4. 绘图 =====================
def plot_all(df):
    # 利率图
    plt.figure(figsize=(14, 5))
    plt.plot(df.index, df['fedfunds'], color='#2c3e50', lw=2)
    plt.title("联邦基金利率历史走势")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "fig_fed_rate_history.png"))
    plt.close()

    # 周期收益图
    assets_use = [c for c in ['SP500', 'Nasdaq100', 'Gold_ETF', 'Bitcoin'] if f'{c}_ret' in df.columns]
    if assets_use:
        ret_df = df[[f'{a}_ret' for a in assets_use]].copy()
        ret_df.columns = assets_use
        ret_df['cycle'] = df['cycle']
        g = ret_df.groupby('cycle').mean().T
        plt.figure(figsize=(11, 5))
        g.plot(kind='bar')
        plt.title("各周期资产平均收益")
        plt.tight_layout()
        plt.savefig(os.path.join(OUT, "fig_cycle_performance.png"))
        plt.close()

    # 2022 走势图
    try:
        sub = df['2022':'2024'][assets_use].dropna()
        sub = sub / sub.iloc[0] * 100
        plt.figure(figsize=(12, 5))
        sub.plot(lw=2)
        plt.axvspan('2022-03', '2023-07', color='red', alpha=0.1)
        plt.title("2022 加息周期资产表现")
        plt.tight_layout()
        plt.savefig(os.path.join(OUT, "fig_assets_in_cycles.png"))
        plt.close()
    except:
        pass

# ===================== 拓展方向代码（零依赖 · 无报错） =====================
def export_extra_results(df):
    # 拓展1：实际利率（兼容pce_yoy列缺失的情况）
    df['real_rate'] = df['fedfunds'] - df.get('pce_yoy', 0)

    # 拓展2：利率敏感性 β（修复维度不匹配问题）
    def beta_np(x, y):
        # 步骤1：对齐索引（只保留两者都非空的行）
        common_idx = x.dropna().index.intersection(y.dropna().index)
        if len(common_idx) < 2:  # 样本数不足时返回0，避免除以0错误
            return 0.0
        x_aligned = x.loc[common_idx].values
        y_aligned = y.loc[common_idx].values
        
        # 步骤2：计算协方差/方差（确保维度匹配）
        cov = np.cov(x_aligned, y_aligned)[0, 1]
        var_x = np.var(x_aligned)
        return cov / var_x if var_x != 0 else 0.0  # 避免除以0

    # 输出β
    beta_result = {}
    for ast in ['SP500', 'Gold_ETF', 'Bitcoin', 'Nasdaq100']:
        if f'{ast}_ret' in df.columns:
            b = beta_np(df['fedfunds'], df[f'{ast}_ret'])
            beta_result[ast] = round(b, 4)

    # 保存β结果（用csv更规范，也兼容txt）
    pd.DataFrame(beta_result, index=['β']).T.to_csv(os.path.join(CLEAN, "beta_result.csv"), encoding='utf-8')
    with open(os.path.join(CLEAN, "beta_result.txt"), 'w', encoding='utf-8') as f:
        f.write(str(beta_result))

    # 拓展3：VIX 周期分析（兼容VIX列缺失）
    if 'VIX' in df.columns:
        vix_mean = df.groupby('cycle')['VIX'].mean().round(2)
        vix_mean.to_csv(os.path.join(CLEAN, "vix_by_cycle.csv"), encoding='utf-8')

    # 保存拓展数据
    df.to_csv(os.path.join(CLEAN, "extended_data.csv"), encoding='utf-8')
    print("✅ 拓展分析完成：实际利率、利率敏感性β、VIX周期分析")

# ===================== 主程序 =====================
if __name__ == "__main__":
    macro_data, assets_data = load_local_data()
    df = clean_and_merge(macro_data, assets_data)
    plot_all(df)
    export_extra_results(df)
    print("🎉 全部运行完成：数据、图表、拓展分析 ✅")