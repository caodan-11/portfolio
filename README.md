# 曹丹 · 数据分析作品集

> 1 年数据相关经验（AI 数据生产 / 数据质量），信息与计算科学专业。
> 3 个完整分析项目，从取数到报告全链路可复现，全部基于**公开数据集**。

**在线看板**：[caodan-11.github.io/portfolio](https://caodan-11.github.io/portfolio/) ｜ **仓库**：[github.com/caodan-11/portfolio](https://github.com/caodan-11/portfolio)

---

## 项目一览

| # | 项目 | 报告 | 关键结论 |
|---|---|---|---|
| 1 | [天猫订单经营分析](./tmall-orders/) | [PDF](./tmall-orders/天猫订单经营分析报告.pdf) | 退款率 23.4% 吞掉 23.1% GMV；湖北退款率 71.9%，问题在履约不在需求 |
| 2 | [RFM 会员价值八分层](./rfm-segments/) | [PDF](./rfm-segments/会员价值分层分析报告.pdf) | 51.1% 的"重要类"客户贡献 97.4% GMV；4,623 名"重要保持"客户挂着 29.0% GMV 却已沉睡 |
| 3 | [多源电商数据对比](./multi-source/) | [PDF](./multi-source/多源电商数据对比报告.pdf) | C 端靠大促脉冲与头部店铺，B 端靠持续复购与客户覆盖，KPI 不可互换 |

## 技能栈

SQL（MySQL：窗口函数 / CTE / LAG）｜Python（Pandas / NumPy / Matplotlib / Pyecharts）｜
Excel（Power Query / 透视表）｜RFM 分层、贡献度拆解、集中度 / 帕累托、指标口径设计

## 目录

```
.
├── index.html              # 三 Tab 在线看板（14 张图）
├── tmall-orders/           # 项目 1：7 页报告 + 5 图 + SQL
├── rfm-segments/           # 项目 2：7 页报告 + 4 图 + SQL
└── multi-source/           # 项目 3：8 页报告 + 6 图 + SQL
```

## 复现

每个项目目录下都有 `README.md`，按里面的命令执行即可（Python 3 + pandas）。

## 说明

- 数据全部为公开数据集，不含任何公司内部数据；
- 报告中的"可挽回 GMV"等均为情景估算，不是实际收益；
- 本作品集用于求职展示，分析代码与结论均可复现。
