# DS2026 G04 T\-B2：美联储货币政策与全球资产价格传导分析

# ds2026\-G04\-T\-B2\_FedPolicyAssets

> 美联储货币政策与全球资产价格传导分析
> 课程：ds2026・小组作业・T\-B2 题

- 仓库地址：[https://github\.com/zhongerhenglu/ds2026\-G04\-T\-B2\_FedPolicyAssets](https://github.com/zhongerhenglu/ds2026-G04-T-B2_FedPolicyAssets)
- GitHub Pages：（已开启，可在仓库 `Settings → Pages` 查看访问链接）

---

## 一、项目简介

本项目围绕美联储货币政策周期，系统分析加息 / 降息对全球资产价格的传导效应，是 ds2026 课程小组作业 T\-B2 题的完整实现。

- **时间范围**：1993–2025 年（月度频率）
- **核心数据**：

  - 宏观数据：联邦基金利率、M2 货币供应量、PCE 通胀指数（来源：FRED 数据库）
  - 资产数据：标普 500（SP500）、纳斯达克 100（Nasdaq100）、黄金 ETF（Gold\_ETF）、20 年期美债 ETF（TLT）、比特币（Bitcoin）、美元指数（DXY）、VIX 恐慌指数（来源：yfinance）
- **研究目标**：

  1. 自动识别历次加息 / 降息 / 平稳周期
  2. 量化不同政策周期下资产的收益、波动与回撤特征
  3. 重点分析 2022 年激进加息对资产价格的冲击效应
  4. 拓展利率敏感性、VIX 情绪联动等深度分析

---

## 二、目录结构

```text
ds2026-G04-T-B2_FedPolicyAssets/
├── .gitignore                      # Git忽略文件配置
├── README.md                       # 项目说明文档（本文件）
├── main_analysis.py                # 完整主程序（含拓展分析）
├── all_extracted_code.py           # 项目核心代码合集
├── 01_get_data.ipynb               # 任务1：数据获取（FRED + yfinance）
├── 01_get_data.py                  # 任务1对应Python脚本
├── 02_data_clean.ipynb             # 任务2：数据清洗与周期标注
├── 02_data_clean.py                # 任务2对应Python脚本
├── 03_analysis_visualization.ipynb # 任务3：分析与可视化主文件
├── 03_analysis_visualization.py    # 任务3对应Python脚本
├── 03_2_analysis_visualization.py  # 拓展分析可视化脚本
├── data_raw/                       # 原始数据目录
│   ├── fed_rates_raw.csv           # FRED宏观数据（利率、M2、PCE）
│   └── assets_raw.csv              # yfinance资产价格原始数据
├── data_clean/                     # 清洗后数据目录
│   ├── macro_assets_merged.csv     # 宏观+资产合并月度数据
│   ├── cycle_labels.csv            # 加息/降息/平稳周期标签表
│   ├── extended_data.csv           # 拓展分析结果（含实际利率）
│   ├── beta_result.txt             # 资产利率敏感性β系数结果
│   └── vix_by_cycle.csv            # 不同周期VIX恐慌指数均值
├── output/                         # 可视化输出目录
│   ├── fig_fed_rate_history.png    # 联邦基金利率历史走势（周期着色）
│   ├── fig_cycle_performance.png   # 加息/降息周期资产平均收益对比
│   └── fig_assets_in_cycles.png    # 2022年加息周期资产价格表现特写
└── T-B2_美联储货币政策与全球资产价格传导.md # 项目完整分析报告
```

---

## 三、任务分工

| 姓名   | 任务内容                                                                  |
| ------ | ------------------------------------------------------------------------- |
| 易忠凯 | 任务 1a — FRED 宏观数据获取（联邦基金利率、M2 货币供应量、PCE 通胀指数） |
| 沈仕沐 | 任务 1b — yfinance 资产价格数据获取（股指、黄金、债券、加密资产、VIX）   |
| 吴玥   | 任务 2 — 数据清洗、合并、月度对齐、加息 / 降息周期标注                   |
| 荣渝渝 | 任务 3\-1 — 联邦基金利率历史走势可视化                                   |
| 王丽娜 | 任务 3\-2 — 加息 / 降息周期资产平均月度收益对比可视化                    |
| 连伊丽 | 任务 3\-3 — 2022 年加息周期资产价格表现特写可视化                        |
| 薛佳程 | 数据校验、拓展分析、报告撰写、项目整合与最终调试                          |

---

## 四、环境依赖与运行方式

### 1\. 环境要求

```bash
# 核心依赖（必装）
pip install pandas numpy matplotlib

# 如需重新获取数据（可选）
pip install fredapi yfinance
```

### 2\. 快速运行（推荐）

直接运行主程序，一键完成所有分析与可视化：

```bash
python main_analysis.py
```

程序将自动：

- 读取 `data\_raw/` 目录下的本地数据
- 完成数据清洗、合并与周期标注
- 生成三张核心图表并保存至 `output/`
- 输出拓展分析结果至 `data\_clean/` 目录

### 3\. 分步运行（Notebook 流程）

1. `01\_get\_data\.ipynb`：从 FRED 和 yfinance 获取原始数据，保存至 `data\_raw/`
2. `02\_data\_clean\.ipynb`：数据清洗、月度对齐、自动标注加息 / 降息周期
3. `03\_analysis\_visualization\.ipynb`：核心分析与可视化，输出三张核心图表

---

## 五、核心结果说明

### 1\. 联邦基金利率历史走势

`output/fig\_fed\_rate\_history\.png`

- 清晰呈现 1993–2025 年美联储历次加息 / 降息周期
- 重点标注 2022–2023 年史上最激进加息周期（利率从 0\.25% 升至 5\.5%）

### 2\. 加息 / 降息周期资产平均收益

`output/fig\_cycle\_performance\.png`

- 降息周期：权益类资产（SP500、Nasdaq100）表现显著更优
- 加息周期：长期债券、高成长科技股、比特币受冲击最明显，与利率估值理论完全一致

### 3\. 2022 年加息周期资产表现特写

`output/fig\_assets\_in\_cycles\.png`

- 2022\-03 至 2023\-07 加息区间内，高风险资产（比特币、Nasdaq100）大幅回撤
- 黄金受益于高通胀避险需求，表现相对抗跌
- 加息结束后，风险资产随政策预期快速反弹

---

## 六、拓展分析说明

主程序 `main\_analysis\.py` 内置以下拓展分析功能：

1. **实际利率测算**：计算 `real\_rate = 联邦基金利率 \- PCE通胀率`，分析实际利率对资产的驱动作用
2. **利率敏感性 β 系数**：通过纯 NumPy 回归，量化各类资产对利率变化的敏感度，结果输出至 `beta\_result\.txt`
3. **VIX 恐慌指数联动**：分析不同政策周期下市场恐慌指数的变化特征，结果输出至 `vix\_by\_cycle\.csv`

---

## 七、参考资料

1. ds2026 课程主页：[https://lianxhcn\.github\.io/ds2026/](https://lianxhcn.github.io/ds2026/)
2. FRED 数据库：[https://fred\.stlouisfed\.org/](https://fred.stlouisfed.org/)
3. 美联储 FOMC 历史声明：[https://www\.federalreserve\.gov/monetarypolicy/fomc\_historical\.htm](https://www.federalreserve.gov/monetarypolicy/fomc_historical.htm)
4. yfinance 官方文档：[https://pypi\.org/project/yfinance/](https://pypi.org/project/yfinance/)

---

## 八、提交说明

- 所有核心代码、数据、可视化结果已完整提交至本仓库
- 主程序 `main\_analysis\.py` 可独立运行，无需额外依赖
- 项目完整分析报告见 `T\-B2\_美联储货币政策与全球资产价格传导\.md`
- 代码已通过本地调试，所有文件路径与依赖配置均兼容 Windows 环境
