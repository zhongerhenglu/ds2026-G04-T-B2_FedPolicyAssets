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

