# -*- coding: utf-8 -*-
"""多源数据对比项目：美妆（C 端大促）× 日化（B 端分销）

分析口径要点：
1) 美妆数据是「每日累计快照」，10 天（11/5–11/14），直接加总会重复计数；
   先取每个商品最后一次快照 = 累计销量，再用相邻两日差值 = 当日新增销量。
2) 日化是 B 端批发订单明细（2019），一单可含多商品多数量，金额字段可直接汇总。
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager

OUT = r"D:\deepseek工作文件夹\作品集\多源数据对比"
CHART = os.path.join(OUT, "charts")
os.makedirs(CHART, exist_ok=True)

for f in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"]:
    if os.path.exists(f):
        try:
            font_manager.fontManager.addfont(f)
        except Exception:
            pass
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.bbox"] = "tight"
plt.rcParams["axes.edgecolor"] = "#CCCCCC"
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.color"] = "#EEEEEE"
INK, MUTED, RED, GREY = "#1F3A5F", "#8FA9C4", "#C0504D", "#B8C9DA"

# ==================== 美妆（C 端） ====================
m = pd.read_csv(r"D:\python\PythonProject\OrderFromTmall\data\双十一淘宝美妆数据.csv")
m["update_time"] = pd.to_datetime(m["update_time"], format="%Y/%m/%d")
m = m.dropna(subset=["sale_count"]).copy()

# 每日累计快照 -> 取当日每商品最后一条
snap = (m.sort_values("update_time")
          .groupby(["update_time", "id"], as_index=False)
          .agg(price=("price", "last"), sale=("sale_count", "last"), shop=("店名", "last"),
               comment=("comment_count", "last")))
days = sorted(snap["update_time"].unique())
piv = snap.pivot_table(index="id", columns="update_time", values="sale", aggfunc="last").sort_index(axis=1)

# 日增量 = 当日 - 前一日；首日只有累计值、没有增量，必须剔除
inc = piv.diff(axis=1)
inc[inc < 0] = 0                      # 负值视为口径调整，按 0 处理
daily_inc = inc.sum(axis=0).iloc[1:]          # 首日无增量，剔除
daily_inc.index = [pd.Timestamp(d).strftime("%m-%d") for d in daily_inc.index]

latest = snap.sort_values("update_time").groupby("id").last()
latest["amount"] = latest["price"] * latest["sale"]

# 双十一折扣：11/11 价格 vs 11/10 价格（显式指定日期，避免索引偏移）
D10, D11 = pd.Timestamp("2016-11-10"), pd.Timestamp("2016-11-11")


def day_price(d):
    return snap[snap["update_time"] == d].set_index("id")["price"]


p10, p11 = day_price(D10), day_price(D11)
pair = pd.DataFrame({"p10": p10, "p11": p11}).dropna()
pair = pair[pair["p10"] > 0]
pair["disc"] = 1 - pair["p11"] / pair["p10"]
pair["inc"] = inc[D11].reindex(pair.index).fillna(0)
pair["shop"] = latest["shop"].reindex(pair.index)

M = {}
M["美妆_快照天数"] = len(days)
M["美妆_商品数"] = int(latest.shape[0])
M["美妆_商品数_原始"] = int(m["id"].nunique())
M["美妆_店铺数"] = int(m["店名"].nunique())
M["美妆_累计销量"] = int(latest["sale"].sum())
M["美妆_累计销售额"] = round(float(latest["amount"].sum()) / 1e8, 2)
M["美妆_价格中位数"] = round(float(latest["price"].median()), 1)
M["美妆_日常日增"] = round(float(daily_inc.drop(["11-11", "11-12"]).mean()), 0)
M["美妆_双十一增量"] = int(daily_inc.loc["11-11"])
M["美妆_双十一后一天"] = int(daily_inc.loc["11-12"])
M["美妆_双十一倍数"] = round(float(daily_inc.loc["11-11"] / daily_inc.drop(["11-11", "11-12"]).mean()), 1)
M["美妆_降价商品占比"] = round(float((pair["disc"] > 0.001).mean() * 100), 1)
M["美妆_降价商品数"] = int((pair["disc"] > 0.001).sum())
M["美妆_折扣中位数"] = round(float(pair.loc[pair["disc"] > 0.001, "disc"].median() * 100), 1)
M["美妆_折扣75分位"] = round(float(pair.loc[pair["disc"] > 0.001, "disc"].quantile(0.75) * 100), 1)
M["美妆_参与对比商品数"] = int(len(pair))
M["美妆_降价商品增量占比"] = round(
    float(pair.loc[pair["disc"] > 0.001, "inc"].sum() / pair["inc"].sum() * 100), 1)

# 折扣分档 vs 当日增量
bins = [-0.01, 0, 0.1, 0.2, 0.3, 0.4, 1.0]
labels = ["未降价", "0-10%", "10-20%", "20-30%", "30-40%", ">40%"]
pair["档"] = pd.cut(pair["disc"], bins=bins, labels=labels)
disc_g = pair.groupby("档", observed=False).agg(商品数=("inc", "count"), 增量=("inc", "sum"))
disc_g["占比"] = (disc_g["商品数"] / disc_g["商品数"].sum() * 100).round(1)
M["美妆_折扣分档"] = [
    {"档": str(i), "商品数": int(r.商品数), "当日增量": int(r.增量), "商品占比": float(r.占比)}
    for i, r in disc_g.iterrows()
]

# 店铺集中度
shop = latest.groupby("shop").agg(销量=("sale", "sum"), 金额=("amount", "sum"), 商品数=("sale", "size")).sort_values("销量", ascending=False)
M["美妆_TOP5店铺销量占比"] = round(float(shop["销量"].head(5).sum() / shop["销量"].sum() * 100), 1)
M["美妆_TOP3店铺"] = [{"店": i, "销量": int(r.销量), "金额万": round(r.金额 / 1e4, 0)} for i, r in shop.head(3).iterrows()]

# 价格带
pb = [0, 100, 200, 300, 500, 1000, 1e9]
pl = ["<100", "100-200", "200-300", "300-500", "500-1000", ">1000"]
latest["价格带"] = pd.cut(latest["price"], bins=pb, labels=pl, right=False)
price_g = latest.groupby("价格带", observed=False).agg(商品数=("sale", "size"), 销量=("sale", "sum"), 金额=("amount", "sum"))
price_g["商品占比"] = (price_g["商品数"] / price_g["商品数"].sum() * 100).round(1)
price_g["销量占比"] = (price_g["销量"] / price_g["销量"].sum() * 100).round(1)
price_g["金额占比"] = (price_g["金额"] / price_g["金额"].sum() * 100).round(1)
M["美妆_价格带"] = [
    {"带": str(i), "商品占比": float(r.商品占比), "销量占比": float(r.销量占比), "金额占比": float(r.金额占比)}
    for i, r in price_g.iterrows()
]

# ==================== 日化（B 端） ====================
f = pd.read_excel(r"D:\python\PythonProject\OrderFromTmall\data\日化.xlsx", sheet_name="销售订单表")
dim = pd.read_excel(r"D:\python\PythonProject\OrderFromTmall\data\日化.xlsx", sheet_name="商品信息表")
f["订单日期"] = pd.to_datetime(f["订单日期"], errors="coerce")
f = f.dropna(subset=["订单日期"]).copy()
f = f[(f["订单日期"] >= "2019-01-01") & (f["订单日期"] < "2020-01-01")]
f["所在区域"] = f["所在区域"].astype(str).str.replace(" ", "", regex=False).str.strip()
f["月"] = f["订单日期"].dt.month

M["日化_订单数"] = int(f["订单编码"].nunique())
M["日化_客户数"] = int(f["客户编码"].nunique())
M["日化_SKU数"] = int(f["商品编号"].nunique())
M["日化_总金额万"] = round(float(f["金额"].sum()) / 1e4, 0)
M["日化_客单价"] = round(float(f["金额"].sum() / f["订单编码"].nunique()), 0)
M["日化_单客户年采购"] = round(float(f["金额"].sum() / f["客户编码"].nunique()), 0)
M["日化_客户均单数"] = round(float(f["订单编码"].nunique() / f["客户编码"].nunique()), 2)
M["日化_区域"] = f.groupby("所在区域")["金额"].sum().div(1e4).round(0).to_dict()

monthly = f.groupby("月").agg(金额=("金额", "sum"), 订单数=("订单编码", "nunique"), 客户数=("客户编码", "nunique")).reset_index()
monthly["金额万"] = (monthly["金额"] / 1e4).round(1)
M["日化_月度"] = [{"月": int(r.月), "金额万": float(r.金额万)} for r in monthly.itertuples()]
M["日化_峰值月"] = int(monthly.loc[monthly["金额"].idxmax(), "月"])
M["日化_缺失月份"] = sorted(set(range(1, 13)) - set(monthly["月"]))
M["日化_谷值月"] = int(monthly.loc[monthly["金额"].idxmin(), "月"])

# 客户帕累托
cust = f.groupby("客户编码")["金额"].sum().sort_values(ascending=False)
cum = cust.cumsum() / cust.sum() * 100
n = np.arange(1, len(cust) + 1) / len(cust) * 100
pareto_x = [0.0] + list(n)
pareto_y = [0.0] + list(cum.values)
for frac in [10, 20, 30]:
    idx = int(len(cust) * frac / 100) - 1
    M[f"日化_TOP{frac}客户贡献"] = round(float(cum.iloc[idx]), 1)
M["日化_客户数_帕累托"] = int(len(cust))

# 品类结构
fc = f.merge(dim[["商品编号", "商品大类", "商品小类"]], on="商品编号", how="left")
cat = fc.groupby("商品大类")["金额"].sum().sort_values(ascending=False)
M["日化_品类"] = [{"类": i, "金额万": round(float(v) / 1e4, 0), "占比": round(float(v / cat.sum() * 100), 1)}
                 for i, v in cat.head(6).items()]

# 复购
cnt = f.groupby("客户编码")["订单编码"].nunique()
M["日化_复购率"] = round(float((cnt >= 2).mean() * 100), 1)

json.dump(M, open(os.path.join(OUT, "metrics_multi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ==================== 图 1：日销量增量 ====================
fig, ax = plt.subplots(figsize=(8.4, 3.9))
vals = daily_inc.values
colors = [RED if v == max(vals) else MUTED for v in vals]
bars = ax.bar(daily_inc.index, vals, color=colors, width=0.62)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + max(vals) * 0.02, f"{v/1e4:.1f}万",
            ha="center", fontsize=7.5, color="#444444")
ax.set_ylabel("当日新增销量（件）")
ax.set_title("图1  双十一当天新增 %s 件，是日常日均的 %.1f 倍；11/12 余温仍有 %s 件"
             % (f"{M['美妆_双十一增量']:,}", M["美妆_双十一倍数"], f"{M['美妆_双十一后一天']:,}"),
             fontsize=9.5, color=INK, loc="left")
fig.savefig(os.path.join(CHART, "01_daily_inc.png"))
plt.close(fig)

# ==================== 图 2：折扣力度 vs 增量 ====================
fig, ax1 = plt.subplots(figsize=(8.4, 3.9))
x = range(len(disc_g))
bars = ax1.bar(x, disc_g["商品数"], color=MUTED, width=0.6, label="商品数")
for b, v in zip(bars, disc_g["商品数"]):
    ax1.text(b.get_x() + b.get_width() / 2, v + 12, f"{int(v)}", ha="center", fontsize=8, color="#444444")
ax1.set_xticks(list(x))
ax1.set_xticklabels(disc_g.index, fontsize=8.5)
ax1.set_ylabel("商品数（个）")
ax1.set_xlabel("双十一当天相对 11/10 的降价幅度")
ax2 = ax1.twinx()
ax2.plot(x, disc_g["增量"] / 1e4, color=RED, lw=1.8, marker="o", ms=6, label="当日新增销量")
for i, v in enumerate(disc_g["增量"] / 1e4):
    ax2.annotate(f"{v:.0f}万", (i, v), textcoords="offset points", xytext=(0, 9),
                 ha="center", fontsize=7.5, color=RED)
ax2.set_ylabel("当日新增销量（万件）")
ax2.grid(False)
ax1.set_title("图2  %.1f%% 的商品在双十一当天降价（中位折扣 %.1f%%），贡献了当天 %.1f%% 的增量"
              % (M["美妆_降价商品占比"], M["美妆_折扣中位数"], M["美妆_降价商品增量占比"]),
              fontsize=9.5, color=INK, loc="left")
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8, frameon=False)
fig.savefig(os.path.join(CHART, "02_discount.png"))
plt.close(fig)

# ==================== 图 3：价格带结构 ====================
fig, ax = plt.subplots(figsize=(8.4, 3.9))
w = 0.27
x = np.arange(len(price_g))
ax.bar(x - w, price_g["商品占比"], w, color=GREY, label="商品数占比")
ax.bar(x, price_g["销量占比"], w, color=MUTED, label="销量占比")
ax.bar(x + w, price_g["金额占比"], w, color=INK, label="销售额占比")
ax.set_xticks(x)
ax.set_xticklabels(price_g.index, fontsize=8.5)
ax.set_ylabel("占比（%）")
ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper right")
hi = price_g["金额占比"].idxmax()
ax.set_title("图3  销售额最大的是 %s 价格带（占 %.1f%%），<100 元商品多但不赚钱"
             % (hi, price_g.loc[hi, "金额占比"]), fontsize=9.5, color=INK, loc="left")
fig.savefig(os.path.join(CHART, "03_price_band.png"))
plt.close(fig)

# ==================== 图 4：店铺集中度 ====================
top = shop.head(10).sort_values("销量")
fig, ax = plt.subplots(figsize=(8.4, 4.0))
bars = ax.barh(top.index, top["销量"] / 1e4, color=[RED if i in top.tail(3).index else INK for i in top.index], height=0.62)
for b, (i, r) in zip(bars, top.iterrows()):
    ax.text(b.get_width() * 1.01, b.get_y() + b.get_height() / 2,
            f"{r.销量/1e4:.0f}万 / {r.商品数}款", va="center", fontsize=7.8, color="#444444")
ax.set_xlabel("累计销量（万件）")
ax.set_xlim(0, top["销量"].max() / 1e4 * 1.28)
ax.set_title("图4  22 家店铺中 TOP5 贡献 %.1f%% 的销量，头部 3 家均破 3,900 万件"
             % M["美妆_TOP5店铺销量占比"], fontsize=9.5, color=INK, loc="left")
ax.grid(axis="y", visible=False)
fig.savefig(os.path.join(CHART, "04_shop.png"))
plt.close(fig)

# ==================== 图 5：日化月度 ====================
fig, ax1 = plt.subplots(figsize=(8.4, 3.9))
bars = ax1.bar(monthly["月"].astype(str), monthly["金额万"], color=MUTED, width=0.62, label="采购金额")
for b, v in zip(bars, monthly["金额万"]):
    ax1.text(b.get_x() + b.get_width() / 2, v + 12, f"{v:.0f}", ha="center", fontsize=7.5, color="#444444")
ax1.set_ylabel("采购金额（万元）")
ax1.set_xlabel("月份（2019 年）")
ax1.set_ylim(0, monthly["金额万"].max() * 1.25)
ax2 = ax1.twinx()
ax2.plot(monthly["月"].astype(str), monthly["客户数"], color=RED, lw=1.8, marker="o", ms=5, label="下单客户数")
ax2.set_ylabel("下单客户数（人）")
ax2.grid(False)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8, frameon=False)
ax1.set_title("图5  B 端采购 1→7 月逐月走高（%.1f 亿 → %.1f 亿，%.1f 倍），8 月起回落；3 月与 10–12 月无数据"
              % (monthly["金额万"].min() / 1e4, monthly["金额万"].max() / 1e4,
                 monthly["金额万"].max() / monthly["金额万"].min()),
              fontsize=9.5, color=INK, loc="left")
fig.savefig(os.path.join(CHART, "05_monthly.png"))
plt.close(fig)

# ==================== 图 6：客户帕累托 ====================
fig, ax = plt.subplots(figsize=(8.4, 4.0))
ax.plot(pareto_x, pareto_y, color=INK, lw=2)
ax.fill_between(pareto_x, pareto_y, color=MUTED, alpha=0.25)
ax.axvline(20, color=RED, ls="--", lw=1.2)
ax.axhline(M["日化_TOP20客户贡献"], color=RED, ls="--", lw=1.2)
ax.annotate(f"TOP20% 客户贡献 {M['日化_TOP20客户贡献']}% 金额", (21, M["日化_TOP20客户贡献"] - 8),
            fontsize=8.5, color=RED)
ax.set_xlabel("客户累计占比（%，按采购金额降序）")
ax.set_ylabel("累计采购金额占比（%）")
ax.set_xlim(0, 100)
ax.set_ylim(0, 101)
ax.set_title("图6  B 端客户并不集中：TOP10%% 客户仅贡献 %.1f%%、TOP20%% 贡献 %.1f%%——无大客户依赖"
             % (M["日化_TOP10客户贡献"], M["日化_TOP20客户贡献"]), fontsize=9.5, color=INK, loc="left")
fig.savefig(os.path.join(CHART, "06_pareto.png"))
plt.close(fig)

print(json.dumps(M, ensure_ascii=False, indent=2)[:2600])
print("\ncharts:", sorted(os.listdir(CHART)))
