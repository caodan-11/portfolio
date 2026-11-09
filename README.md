# 曹丹 · 数据分析作品集

> 1 年数据相关经验（AI 数据生产 / 数据质量），信息与计算科学专业。
> **2 个完整分析项目**，从取数、清洗、分析到报告全链路可复现，全部基于**公开数据集**。

**在线看板**：[caodan-11.github.io/portfolio](https://caodan-11.github.io/portfolio/) ｜ **仓库**：[github.com/caodan-11/portfolio](https://github.com/caodan-11/portfolio)

---

## 项目一览

### 项目 1｜电商订单数据分析（3 份数据，分 3 部分）

> 三份公开数据集的**来源、字段与口径都不相同**，因此各自独立分析、**不做跨数据集的横向对比**。
> 不是把不同来源的数字硬凑在一起，而是分别讲清各自的业务问题。

| 部分 | 数据 | 关键结论 |
|---|---|---|
| Part 1 | 天猫订单（28,010 单） | 成交率 **86.0%**、退款率 **23.4%**、GMV **247.48 万**；上半月受疫情影响偏低、下旬回升；下单集中在 **10 / 15 / 21 点**，21–22 点最高 |
| Part 2 | 双十一美妆（27,598 条 / 22 家店铺 / 10 天快照） | 日销量峰值在 **11 月 9 日**；相宜本草一家占 TOP10 的 **23.21%**；均价最高为娇兰，约 **1,361 元** |
| Part 3 | 日化批发（3.1 万单 / 1,084 客户 / 122 SKU） | 订购 **7 月最高**（单峰）；地区前五为上海、苏州、重庆、深圳、泉州；护肤品占 **85%**，面膜需求最大；客户可按 RFM 排序 |

📄 [完整报告（9 页）](./order-analysis/电商订单数据分析报告.pdf) ｜ 代码、数据与图表见 [order-analysis/](./order-analysis/)

### 项目 2｜RFM 会员价值分层（2015–2018，12.9 万会员）

| 报告 | 关键结论 |
|---|---|
| [PDF（6 页）](./rfm-segments/会员价值分层分析报告.pdf) | 4 年 20.3 万单、**12.9 万会员**；R/F/M 三档拼成 **25 类人群**；2018 年 `213` 类**人数占 11.8%、金额占 30.9%**；复购率仅 **14.4%**，85.6% 会员只买过一次 |

代码、数据与三维图见 [rfm-segments/](./rfm-segments/)

---

## 技能栈

SQL（MySQL：多表关联 / 窗口函数 / CTE）｜Python（Pandas / Matplotlib / Pyecharts）｜
Excel（透视表 / 函数）｜RFM 分层、时段与地区结构分析、品类与价格带

## 目录

```
.
├── index.html              # 在线看板（2 个 Tab，12 张图，RFM 3D 图可旋转）
├── order-analysis/         # 项目 1：9 页报告 + 9 图 + SQL + Notebook + 原始数据
└── rfm-segments/           # 项目 2：6 页报告 + 5 图 + SQL + Notebook + 原始数据
```

每个项目目录下包含：

```
├── 报告 PDF
├── README.md      # 项目说明 + 复现步骤
├── code/          # Jupyter Notebook（完整分析过程）+ 出图 / 出报告的脚本
├── data/          # 原始数据集（公开数据，可直接下载运行）
├── sql/           # 对应分析口径的 SQL 脚本
└── charts/        # 报告里用到的图
```

## 复现

**方式一：跑 Notebook（推荐）**

```bash
jupyter notebook order-analysis/code/订单数据分析.ipynb
jupyter notebook rfm-segments/code/RFM综合案例.ipynb
```

**方式二：只重画图 / 重新生成报告**

```bash
cd order-analysis/code && python build_charts.py
cd rfm-segments/code  && python build_rfm_charts.py && python build_3d_chart.py
```

## 说明

- 数据全部为公开数据集，不含任何公司内部数据；
- 项目 1 的三份数据来源不同，分部分分析，**不做跨数据集的横向对比**；
- 天猫数据没有退款原因字段，退款率只呈现规模、不做归因；
- 美妆数据为每日销售快照，反映当日销量，不当累计值使用；
- 本作品集用于求职展示，分析代码与结论均可复现。
