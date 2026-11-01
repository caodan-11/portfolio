# -*- coding: utf-8 -*-
"""天猫订单数据（2020.02）复盘分析：指标计算 + 图表输出 + 指标 JSON"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager

OUT = r"D:\deepseek工作文件夹\作品集\电商订单经营分析"
CHART = os.path.join(OUT, "charts")
os.makedirs(CHART, exist_ok=True)

# ---- 中文字体 ----
for f in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\msyhbd.ttc"]:
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
plt.rcParams["grid.linewidth"] = 0.8
ACCENT = "#1F3A5F"
ACCENT2 = "#C0504D"
MUTED = "#8FA9C4"

SRC = r"D:\python\PythonProject\OrderFromTmall\data\tmall_order_report.csv"
df = pd.read_csv(SRC)
df.columns = [c.strip() for c in df.columns]
df["订单创建时间"] = pd.to_datetime(df["订单创建时间"])
df["订单付款时间"] = pd.to_datetime(df["订单付款时间"])
df["已付款"] = df["订单付款时间"].notna()
df["退款"] = df["退款金额"] > 0
df["省份"] = df["收货地址"].astype(str).str.replace("自治区|维吾尔|回族|壮族|省|市", "", regex=True).str.strip()
df["日期"] = df["订单创建时间"].dt.date
df["小时"] = df["订单创建时间"].dt.hour

M = {}
M["总订单数"] = int(len(df))
M["已付款订单数"] = int(df["已付款"].sum())
M["未付款订单数"] = int((~df["已付款"]).sum())
M["成交率"] = round(M["已付款订单数"] / M["总订单数"] * 100, 2)
M["退款订单数"] = int(df["退款"].sum())
M["退款率"] = round(M["退款订单数"] / M["已付款订单数"] * 100, 2)
M["GMV"] = round(float(df.loc[df["已付款"], "总金额"].sum()), 2)
M["实收金额"] = round(float(df.loc[df["已付款"], "买家实际支付金额"].sum()), 2)
M["退款金额"] = round(float(df.loc[df["已付款"], "退款金额"].sum()), 2)
M["GMV流失率"] = round((1 - M["实收金额"] / M["GMV"]) * 100, 2)
M["客单价"] = round(M["GMV"] / M["已付款订单数"], 2)
M["日期范围"] = f"{df['日期'].min()} ~ {df['日期'].max()}"
M["日均订单"] = round(M["总订单数"] / df["日期"].nunique(), 1)

# 每日
daily = df.groupby("日期").agg(订单数=("订单编号", "count"), 已付款=("已付款", "sum")).reset_index()
daily["成交率"] = daily["已付款"] / daily["订单数"] * 100
daily["日期"] = pd.to_datetime(daily["日期"])
d10 = daily[daily["日期"] <= "2020-02-10"]["订单数"].mean()
d20 = daily[(daily["日期"] > "2020-02-10") & (daily["日期"] <= "2020-02-20")]["订单数"].mean()
d29 = daily[daily["日期"] > "2020-02-20"]["订单数"].mean()
M["上旬日均"] = round(float(d10), 1)
M["中旬日均"] = round(float(d20), 1)
M["下旬日均"] = round(float(d29), 1)
M["下旬较上旬增幅"] = round((d29 / d10 - 1) * 100, 1)
peak_day = daily.loc[daily["订单数"].idxmax()]
M["峰值日"] = str(peak_day["日期"].date())
M["峰值日订单"] = int(peak_day["订单数"])

# 断档期识别（2/10–2/16 仅 33 单，其中 2/8、2/16 整日缺失）
gap_lo, gap_hi = pd.Timestamp("2020-02-10"), pd.Timestamp("2020-02-16")
gap_mask = (daily["日期"] >= gap_lo) & (daily["日期"] <= gap_hi)
M["断档天数"] = int(gap_mask.sum())
M["断档期订单数"] = int(daily.loc[gap_mask, "订单数"].sum())
M["断档期订单占比"] = round(M["断档期订单数"] / M["总订单数"] * 100, 2)
M["缺失日期"] = [str(d.date()) for d in pd.date_range("2020-02-01", "2020-02-29")
                 if d.date() not in set(daily["日期"].dt.date)]
rest = df[~((df["订单创建时间"] >= gap_lo) & (df["订单创建时间"] < gap_hi + pd.Timedelta(days=1)))]
M["剔除断档后成交率"] = round(float(rest["已付款"].mean() * 100), 2)

# 小时
hourly = df.groupby("小时").agg(订单数=("订单编号", "count"), 已付款=("已付款", "sum")).reset_index()
hourly["成交率"] = hourly["已付款"] / hourly["订单数"] * 100
top_hours = hourly.sort_values("订单数", ascending=False).head(3)
M["下单高峰时段"] = [f"{int(r.小时)}:00（{int(r.订单数)} 单）" for r in top_hours.itertuples()]
M["成交率最高时段"] = [f"{int(r.小时)}:00（{r.成交率:.1f}%）" for r in hourly.sort_values("成交率", ascending=False).head(3).itertuples()]
M["成交率最低时段"] = [f"{int(r.小时)}:00（{r.成交率:.1f}%）" for r in hourly.sort_values("成交率").head(3).itertuples()]
M["全天成交率"] = round(M["成交率"], 2)
M["峰值小时成交率"] = round(float(hourly.loc[hourly["订单数"].idxmax(), "成交率"]), 2)
M["晚间20_22点订单占比"] = round(float(hourly[hourly["小时"].isin([20, 21, 22])]["订单数"].sum() / M["总订单数"] * 100), 2)
M["凌晨0_6点订单占比"] = round(float(hourly[hourly["小时"].isin([0, 1, 2, 3, 4, 5, 6])]["订单数"].sum() / M["总订单数"] * 100), 2)
for name, hs in [("凌晨0_6点", range(0, 7)), ("白天7_18点", range(7, 19)), ("晚间19_23点", range(19, 24))]:
    sub = df[df["小时"].isin(list(hs))]
    M[name + "成交率"] = round(float(sub["已付款"].mean() * 100), 2)
    M[name + "占比"] = round(len(sub) / M["总订单数"] * 100, 2)

# 地区
prov = df.groupby("省份").agg(
    订单数=("订单编号", "count"),
    已付款=("已付款", "sum"),
    GMV=("总金额", lambda s: s[df.loc[s.index, "已付款"]].sum()),
    退款订单=("退款", "sum"),
).reset_index()
prov["成交率"] = prov["已付款"] / prov["订单数"] * 100
prov["退款率"] = prov["退款订单"] / prov["已付款"] * 100
prov = prov.sort_values("订单数", ascending=False)
M["省份数"] = int(len(prov))
M["TOP5省份"] = [
    {"省": r.省份, "订单数": int(r.订单数), "占比": round(r.订单数 / M["总订单数"] * 100, 2),
     "成交率": round(r.成交率, 2), "退款率": round(r.退款率, 2)}
    for r in prov.head(5).itertuples()
]
M["TOP5集中度"] = round(prov.head(5)["订单数"].sum() / M["总订单数"] * 100, 2)
M["TOP10集中度"] = round(prov.head(10)["订单数"].sum() / M["总订单数"] * 100, 2)

# 退款维度
ref_by_prov = prov[prov["已付款"] >= 30].sort_values("退款率", ascending=False).head(8)
M["高退款率省份"] = [
    {"省": r.省份, "退款率": round(r.退款率, 2), "已付款": int(r.已付款)} for r in ref_by_prov.itertuples()
]

# 客单价分布
paid_df = df[df["已付款"]]
M["客单价中位数"] = round(float(paid_df["总金额"].median()), 2)
M["客单价P90"] = round(float(paid_df["总金额"].quantile(0.9)), 2)
M["500元以上订单占比"] = round(float((paid_df["总金额"] > 500).mean() * 100), 2)
M["100元以下订单占比"] = round(float((paid_df["总金额"] <= 100).mean() * 100), 2)
# GMV 集中度
paid_sorted = paid_df["总金额"].sort_values(ascending=False)
M["头部10%订单GMV占比"] = round(float(paid_sorted.head(int(len(paid_sorted) * 0.1)).sum() / paid_sorted.sum() * 100), 2)

json.dump(M, open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---------------- 图 1：每日订单量与成交率 ----------------
fig, ax1 = plt.subplots(figsize=(8.2, 4.0))
ax1.axvspan(gap_lo, gap_hi, color="#F2E6E6", zorder=0)
ax1.text(gap_lo + pd.Timedelta(days=3, hours=12), 3050,
         "2/10–2/16 断档\n仅 %d 单" % M["断档期订单数"], ha="center", va="center", fontsize=7.5, color="#A05A5A")
ax1.bar(daily["日期"], daily["订单数"], color=MUTED, width=0.7, label="创建订单数", zorder=2)
ax1.plot(daily["日期"], daily["已付款"], color=ACCENT, lw=1.8, marker="o", ms=3, label="已付款订单数", zorder=3)
ax1.set_ylabel("订单数（单）")
ax1.set_xlabel("")
ax2 = ax1.twinx()
conv_masked = daily["成交率"].where(daily["订单数"] >= 50)
ax2.plot(daily["日期"], conv_masked, color=ACCENT2, lw=1.4, ls="--", marker="s", ms=2.5, label="成交率")
ax2.set_ylabel("成交率（%）")
ax2.set_ylim(75, 100)
ax2.grid(False)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8, frameon=False)
ax1.set_title("图1  下旬日均 %d 单，为上旬（%d 单）的 %.1f 倍；成交率稳定在 %.0f%% 上下"
              % (M["下旬日均"], M["上旬日均"], M["下旬日均"] / M["上旬日均"], M["成交率"]),
              fontsize=9.5, color=ACCENT, loc="left")
fig.autofmt_xdate(rotation=90)
fig.savefig(os.path.join(CHART, "01_daily_trend.png"))
plt.close(fig)

# ---------------- 图 2：小时分布 ----------------
fig, ax1 = plt.subplots(figsize=(8.2, 4.0))
ax1.bar(hourly["小时"], hourly["订单数"], color=MUTED, width=0.7, label="订单数")
ax1.set_xticks(range(0, 24))
ax1.set_xlabel("下单小时")
ax1.set_ylabel("订单数（单）")
ax2 = ax1.twinx()
ax2.plot(hourly["小时"], hourly["成交率"], color=ACCENT2, lw=1.8, marker="o", ms=3, label="成交率")
ax2.set_ylabel("成交率（%）")
ax2.grid(False)
ax2.set_ylim(82, 89)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8, frameon=False)
ax1.set_title("图2  晚间 19–23 点贡献 %.1f%% 的订单，20–22 点为峰值；凌晨 0–6 点占 %.1f%% 且成交率最低（%.1f%%）"
              % (M["晚间19_23点占比"], M["凌晨0_6点占比"], M["凌晨0_6点成交率"]),
              fontsize=9.5, color=ACCENT, loc="left")
fig.savefig(os.path.join(CHART, "02_hourly.png"))
plt.close(fig)

# ---------------- 图 3：省份 TOP10 ----------------
p10 = prov.head(10).sort_values("订单数")
fig, ax = plt.subplots(figsize=(8.2, 4.0))
bars = ax.barh(p10["省份"], p10["订单数"], color=ACCENT, height=0.62)
for b, v, c in zip(bars, p10["订单数"], p10["成交率"]):
    ax.text(b.get_width() + 12, b.get_y() + b.get_height() / 2,
            f"{int(v)} 单 / 成交率 {c:.0f}%", va="center", fontsize=8, color="#444444")
ax.set_xlabel("订单数（单）")
ax.set_xlim(0, p10["订单数"].max() * 1.35)
ax.set_title("图3  TOP10 省份贡献 %.1f%% 的订单，头部集中明显（上海、江苏、浙江、广东为第一梯队）"
             % M["TOP10集中度"], fontsize=9.5, color=ACCENT, loc="left")
fig.savefig(os.path.join(CHART, "03_province.png"))
plt.close(fig)

# ---------------- 图 4：退款率对比 ----------------
rr = prov[prov["已付款"] >= 30].sort_values("退款率", ascending=False)
head_rr = rr.head(8).sort_values("退款率")
fig, ax = plt.subplots(figsize=(8.2, 3.8))
bars = ax.barh(head_rr["省份"], head_rr["退款率"], color=ACCENT2, height=0.6)
ax.axvline(M["退款率"], color=ACCENT, ls="--", lw=1.2)
ax.text(M["退款率"] + 0.15, -0.6, f"全站均值 {M['退款率']:.1f}%", color=ACCENT, fontsize=8)
for b, v in zip(bars, head_rr["退款率"]):
    ax.text(b.get_width() + 0.1, b.get_y() + b.get_height() / 2, f"{v:.1f}%", va="center", fontsize=8, color="#444444")
ax.set_xlabel("退款率（%，已付款订单口径）")
ax.set_xlim(0, head_rr["退款率"].max() * 1.25)
ax.set_title("图4  退款率最高的 8 个省份（已付款≥30 单），最高为全站均值的 %.1f 倍"
             % (head_rr["退款率"].max() / M["退款率"]), fontsize=9.5, color=ACCENT, loc="left")
fig.savefig(os.path.join(CHART, "04_refund.png"))
plt.close(fig)

# ---------------- 图 5：订单金额分布 ----------------
fig, ax = plt.subplots(figsize=(8.2, 3.6))
bins = [0, 50, 100, 200, 300, 500, 1000, 1e9]
labels = ["<50", "50-100", "100-200", "200-300", "300-500", "500-1000", ">1000"]
cut = pd.cut(paid_df["总金额"], bins=bins, labels=labels, right=False)
cnt = cut.value_counts().reindex(labels)
share = cnt / cnt.sum() * 100
bars = ax.bar(labels, share, color=[MUTED] * 5 + [ACCENT, ACCENT2], width=0.62)
for b, v in zip(bars, share):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.6, f"{v:.1f}%", ha="center", fontsize=8, color="#444444")
ax.set_ylabel("订单占比（%）")
ax.set_xlabel("订单金额区间（元）")
ax.set_title("图5  已付款订单以 100–300 元为主（占 %.1f%%），>500 元订单仅占 %.1f%%"
             % (share["100-200"] + share["200-300"], share["500-1000"] + share[">1000"]),
             fontsize=9.5, color=ACCENT, loc="left")
fig.savefig(os.path.join(CHART, "05_amount.png"))
plt.close(fig)

print(json.dumps(M, ensure_ascii=False, indent=2))
print("\ncharts:", sorted(os.listdir(CHART)))
