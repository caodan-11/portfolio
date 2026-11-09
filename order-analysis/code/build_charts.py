# -*- coding: utf-8 -*-
"""电商订单数据分析（3 份数据）—— 只按 notebook 里做过的分析出图"""
import os
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

warnings.filterwarnings("ignore")

BASE = r"D:\python\PythonProject\OrderFromTmall"
DATA = os.path.join(BASE, "data")
OUT = r"D:\deepseek工作文件夹\作品集\电商订单数据分析\charts"
os.makedirs(OUT, exist_ok=True)

# 字体
for f in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyhbd.ttc"]:
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = "Microsoft YaHei"
plt.rcParams["axes.unicode_minus"] = False

NAVY, BLUE, RED, GRAY = "#1F3A5F", "#8FA9C4", "#C0504D", "#9AA5B1"


def style(ax, title, xlabel="", ylabel=""):
    ax.set_title(title, fontsize=13, color=NAVY, pad=12, fontweight="bold")
    ax.set_xlabel(xlabel, fontsize=10, color="#444")
    ax.set_ylabel(ylabel, fontsize=10, color="#444")
    ax.grid(axis="y", alpha=0.25, linestyle="--")
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# ============ Part 1 天猫订单 ============
d1 = pd.read_csv(os.path.join(DATA, "tmall_order_report.csv"), encoding="utf-8", on_bad_lines="skip")
d1.columns = d1.columns.str.strip()
d1["收货地址"] = d1["收货地址"].astype(str).str.replace("自治区|维吾尔|回族|壮族|省", "", regex=True)
d1["订单创建时间"] = pd.to_datetime(d1["订单创建时间"])
d1["订单付款时间"] = pd.to_datetime(d1["订单付款时间"], errors="coerce")

total = len(d1)
paid = d1["订单付款时间"].notna().sum()
gmv = d1.loc[d1["订单付款时间"].notna(), "总金额"].sum()
real = d1.loc[d1["订单付款时间"].notna(), "买家实际支付金额"].sum()
refund = d1["退款金额"].fillna(0).sum()
print(f"[天猫] 总单 {total} 已付款 {paid} 成交率 {paid/total*100:.1f}% GMV {gmv/1e4:.2f}万 实收 {real/1e4:.2f}万 退款 {refund/1e4:.2f}万")

# 1) 每日订单量
daily = d1.groupby(d1["订单创建时间"].dt.strftime("%m-%d")).size()
fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(list(daily.index), daily.values, color=NAVY, lw=2)
style(ax, "2 月上半月订单偏低，下旬复工后明显回升", "日期", "订单量")
ax.set_xticks([i for i in range(0, len(daily), 4)])
ax.set_xticklabels([list(daily.index)[i] for i in range(0, len(daily), 4)])
plt.tight_layout()
plt.savefig(os.path.join(OUT, "01_tmall_daily.png"), dpi=150)
plt.close()

# 2) 每小时订单量
hourly = d1.groupby(d1["订单创建时间"].dt.hour).size()
fig, ax = plt.subplots(figsize=(9, 3.8))
colors = [RED if h in (21, 22) else (BLUE if h in (10, 15) else NAVY) for h in hourly.index]
ax.bar(list(hourly.index), hourly.values, color=colors)
style(ax, "一天有三个下单高峰（10 点 / 15 点 / 21 点），21–22 点最高", "小时", "订单量")
ax.set_xticks(list(hourly.index))
plt.tight_layout()
plt.savefig(os.path.join(OUT, "02_tmall_hourly.png"), dpi=150)
plt.close()

# ============ Part 2 双十一美妆 ============
d2 = pd.read_csv(os.path.join(DATA, "双十一淘宝美妆数据.csv"), encoding="utf-8", on_bad_lines="skip")
d2["update_time"] = pd.to_datetime(d2["update_time"], errors="coerce").dt.strftime("%Y-%m-%d")
d2 = d2.dropna(subset=["update_time"])
d2["sale_count"] = pd.to_numeric(d2["sale_count"], errors="coerce").fillna(0)
d2["price"] = pd.to_numeric(d2["price"], errors="coerce").fillna(0)
d2["sale_amount"] = d2["sale_count"] * d2["price"]

daily2 = d2.groupby("update_time").agg(cnt=("sale_count", "sum")).sort_index()
print(f"[美妆] 记录 {len(d2)} 店铺 {d2['店名'].nunique()} 日销量 最大{daily2['cnt'].max():,} 最小{daily2['cnt'].min():,} 平均{daily2['cnt'].mean():,.0f} 峰值 {daily2['cnt'].idxmax()}")

fig, ax = plt.subplots(figsize=(9, 3.8))
x = list(daily2.index)
v = daily2["cnt"].values
ax.plot(x, v / 1e4, color=NAVY, lw=2, marker="o", ms=4)
ax.fill_between(range(len(x)), v / 1e4, min(v) / 1e4 * 0.995, color=BLUE, alpha=0.25)
style(ax, "大促期间日销量起落明显，峰值出现在 11 月 9 日", "日期", "当日销量（万件）")
ax.set_xticks(range(len(x)))
ax.set_xticklabels([i[5:] for i in x], rotation=0, fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "03_beauty_daily.png"), dpi=150)
plt.close()

# 店铺累计销量 TOP10（11/5–11/14 全期累计）
top10 = d2.groupby("店名").agg(销量=("sale_count", "sum"), 销售额=("sale_amount", "sum")).sort_values("销量", ascending=False).head(10)
share = top10["销量"] / top10["销量"].sum() * 100
print("[美妆] TOP10 第一:", top10.index[0], f"占TOP10 {share.iloc[0]:.2f}%")

fig, ax = plt.subplots(figsize=(9, 4.2))
y = range(len(top10))[::-1]
ax.barh(list(y), top10["销量"].values / 1e4, color=[RED if i == 0 else NAVY for i in range(len(top10))])
ax.set_yticks(list(y))
ax.set_yticklabels(top10.index, fontsize=9)
style(ax, f"累计销量 TOP10：{top10.index[0]} 一家占前十总量的 {share.iloc[0]:.1f}%", "累计销量（万件）")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "04_beauty_top10.png"), dpi=150)
plt.close()

# 均价 TOP20
avg_price = d2.groupby("店名")["price"].mean().sort_values(ascending=False).head(20)
print(f"[美妆] 均价最贵: {avg_price.index[0]} {avg_price.iloc[0]:.2f} 元")

fig, ax = plt.subplots(figsize=(9, 4.4))
yy = range(len(avg_price))
ax.barh(list(yy), avg_price.values, color=[RED if i == 0 else BLUE for i in range(len(avg_price))])
ax.set_yticks(list(yy))
ax.set_yticklabels(avg_price.index, fontsize=8.5)
ax.invert_yaxis()
style(ax, f"店铺平均价格 TOP20：最贵的 {avg_price.index[0]} 约 {avg_price.iloc[0]:.0f} 元", "平均单价（元）")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "05_beauty_price.png"), dpi=150)
plt.close()

# ============ Part 3 日化批发 ============
f = pd.read_excel(os.path.join(DATA, "日化.xlsx"), sheet_name="销售订单表")
p = pd.read_excel(os.path.join(DATA, "日化.xlsx"), sheet_name="商品信息表")
f = f.drop_duplicates()
f["订单日期"] = pd.to_datetime(f["订单日期"], errors="coerce", format="mixed")
f = f[f["订单日期"].notna()]
f["订购数量"] = pd.to_numeric(f["订购数量"].astype(str).str.replace("个", "", regex=False), errors="coerce")
f["金额"] = pd.to_numeric(f["金额"], errors="coerce")
f["月"] = f["订单日期"].dt.month
print(f"[日化] 订单 {len(f)} 客户 {f['客户编码'].nunique()} SKU {p['商品编号'].nunique()}")

# 月度订购
m = f.groupby("月")["订购数量"].sum()
fig, ax = plt.subplots(figsize=(9, 3.8))
ax.bar([f"{i} 月" for i in m.index], m.values, color=NAVY)
ax.bar([f"{m.idxmax()} 月"], [m.max()], color=RED)
style(ax, f"月度订购呈单峰：1 月最低，{m.idxmax()} 月达到顶峰后回落", "月份", "订购数量")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "06_chem_monthly.png"), dpi=150)
plt.close()

# 地区 TOP20（按地市）
city = f.groupby("所在地市")["订购数量"].sum().sort_values(ascending=False).head(20)
print("[日化] 地区前五:", list(city.index[:5]))
fig, ax = plt.subplots(figsize=(9, 4.4))
yy = range(len(city))[::-1]
ax.barh(list(yy), city.values, color=[RED if i < 5 else BLUE for i in range(len(city))])
ax.set_yticks(list(yy))
ax.set_yticklabels(city.index, fontsize=8.5)
style(ax, "订购量 TOP20 城市：前五为上海、苏州、重庆、深圳、泉州", "订购数量")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "07_chem_city.png"), dpi=150)
plt.close()

# 品类
order = f.merge(p, on="商品编号", how="inner")
cat = order.groupby("商品大类")["订购数量"].sum().sort_values(ascending=False)
sub = order.groupby("商品小类")["订购数量"].sum().sort_values(ascending=False).head(8)
print("[日化] 大类:", {k: f"{v:,}" for k, v in cat.items()}, "| 护肤品占比", f"{cat.get('护肤品',0)/cat.sum()*100:.1f}%")

fig, ax = plt.subplots(figsize=(9, 4.2))
yy = range(len(sub))[::-1]
ax.barh(list(yy), sub.values / 1e4, color=[RED if i == 0 else BLUE for i in range(len(sub))])
ax.set_yticks(list(yy))
ax.set_yticklabels(sub.index, fontsize=9)
ax.invert_yaxis()
style(ax, f"需求量最大的小类是{sub.index[0]}；护肤品约占订购量的 {cat.get('护肤品',0)/cat.sum()*100:.0f}%", "订购数量（万件）")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "08_chem_category.png"), dpi=150)
plt.close()

# 日化客户 RFM（R20/F30/M50 加权）
rfm = f.groupby("客户编码").agg(最近=("订单日期", "max"), 频次=("订单编码", "count"), 金额=("金额", "sum"))
snap = f["订单日期"].max()
rfm["r_s"] = rfm["最近"].rank(pct=True)
rfm["f_s"] = rfm["频次"].rank(pct=True)
rfm["m_s"] = rfm["金额"].rank(pct=True)
rfm["score"] = (rfm["r_s"] * 20 + rfm["f_s"] * 30 + rfm["m_s"] * 50).round(1)
rfm = rfm.sort_values("score", ascending=False)
print(f"[日化] RFM 客户 {len(rfm)} 得分区间 {rfm['score'].min():.1f}–{rfm['score'].max():.1f}")

fig, ax = plt.subplots(figsize=(9, 3.8))
ax.hist(rfm["score"], bins=24, color=BLUE, edgecolor="white")
ax.axvline(80, color=RED, ls="--", lw=1.5)
ax.text(81, ax.get_ylim()[1] * 0.85, "80 分以上\n视为优质客户", color=RED, fontsize=9)
style(ax, "RFM 加权打分（R 20% / F 30% / M 50%）：80 分以上视为优质客户", "得分", "客户数")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "09_chem_rfm.png"), dpi=150)
plt.close()

print("\n图表输出完成 →", OUT)
for fn in sorted(os.listdir(OUT)):
    print("  ", fn)
