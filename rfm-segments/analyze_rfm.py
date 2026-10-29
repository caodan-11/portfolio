# -*- coding: utf-8 -*-
"""RFM 八分层重构：4 年会员订单 -> 8 类客户 -> 指标 + 图表

分层规则（业务阈值，非中位数）：
  R：距今 ≤90 天 记为 R 高（近 3 个月仍活跃）
  F：订单数 ≥2 次 记为 F 高（有复购）
  M：年消费 ≥ 当年中位数 记为 M 高
原因：2018 年 85.6% 的会员全年只下过 1 单，F 的中位数恒为 1，
用中位数二分会让 F 失去区分度（全员被判为 F 高）。
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager

OUT = r"D:\deepseek工作文件夹\作品集\RFM用户分层"
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
ACCENT = "#1F3A5F"
ACCENT2 = "#C0504D"
MUTED = "#8FA9C4"

R_DAYS = 90
F_TIMES = 2

SRC = r"D:\python\JupyterProject\data\sales.xlsx"
sheets = pd.read_excel(SRC, sheet_name=["2015", "2016", "2017", "2018"])

frames = []
for y, d in sheets.items():
    d = d.dropna()
    d = d[d["订单金额"] > 1].copy()
    d["year"] = int(y)
    d["snapshot"] = d["提交日期"].max()
    frames.append(d)
df = pd.concat(frames, ignore_index=True)
df["r_days"] = (df["snapshot"] - df["提交日期"]).dt.days

rfm = (df.groupby(["year", "会员ID"])
         .agg(r=("r_days", "min"), f=("订单号", "count"), m=("订单金额", "sum"))
         .reset_index())

NAME = {
    (True, True, True): "重要价值",
    (False, True, True): "重要保持",
    (True, False, True): "重要发展",
    (False, False, True): "重要挽留",
    (True, True, False): "一般价值",
    (False, True, False): "一般保持",
    (True, False, False): "一般发展",
    (False, False, False): "一般挽留",
}
ORDER = ["重要价值", "重要保持", "重要发展", "重要挽留", "一般价值", "一般保持", "一般发展", "一般挽留"]

m_med = rfm.groupby("year")["m"].median()


def classify(row):
    return NAME[(row["r"] <= R_DAYS, row["f"] >= F_TIMES, row["m"] >= m_med.loc[row["year"]])]


rfm["群体"] = rfm.apply(classify, axis=1)

M = {}
M["数据年份"] = "2015–2018"
M["订单总数"] = int(len(df))
M["会员总数"] = int(rfm.groupby("year")["会员ID"].nunique().sum())
M["总GMV"] = round(float(df["订单金额"].sum()), 2)
M["阈值"] = {"R_天": R_DAYS, "F_次": F_TIMES,
             "M_中位数": {str(int(y)): round(float(m_med.loc[y]), 1) for y in [2015, 2016, 2017, 2018]}}

# ---- 年度概览 ----
year_rows = []
for y in [2015, 2016, 2017, 2018]:
    sub = rfm[rfm["year"] == y]
    n = len(sub)
    repeat = int((sub["f"] >= 2).sum())
    year_rows.append({
        "year": y,
        "会员数": n,
        "订单数": int(sub["f"].sum()),
        "GMV": round(float(sub["m"].sum()), 2),
        "复购会员数": repeat,
        "复购率": round(repeat / n * 100, 2),
        "单次客户占比": round((n - repeat) / n * 100, 2),
        "人均消费": round(float(sub["m"].mean()), 2),
        "客单价": round(float(sub["m"].sum() / sub["f"].sum()), 2),
    })
M["年度概览"] = year_rows

# ---- 2018 分层 ----
y18 = rfm[rfm["year"] == 2018]
gmv_total = float(y18["m"].sum())
orders_total = float(y18["f"].sum())
cnt_total = int(len(y18))
rows = []
for name in ORDER:
    sub = y18[y18["群体"] == name]
    rows.append({
        "群体": name,
        "人数": int(len(sub)),
        "人数占比": round(len(sub) / cnt_total * 100, 2) if cnt_total else 0,
        "GMV": round(float(sub["m"].sum()), 2),
        "GMV占比": round(float(sub["m"].sum()) / gmv_total * 100, 2),
        "订单数": int(sub["f"].sum()),
        "人均消费": round(float(sub["m"].mean()), 2) if len(sub) else 0,
        "人均订单": round(float(sub["f"].mean()), 2) if len(sub) else 0,
        "平均R_天": round(float(sub["r"].mean()), 1) if len(sub) else 0,
    })
for r in rows:
    r["贡献倍数"] = round(r["GMV占比"] / r["人数占比"], 2) if r["人数占比"] else 0
M["2018分层"] = rows

head = [r for r in rows if r["群体"].startswith("重要")]
tail = [r for r in rows if r["群体"].startswith("一般")]
M["2018头部四类"] = {"人数占比": round(sum(r["人数占比"] for r in head), 2),
                     "GMV占比": round(sum(r["GMV占比"] for r in head), 2)}
M["2018长尾四类"] = {"人数占比": round(sum(r["人数占比"] for r in tail), 2),
                     "GMV占比": round(sum(r["GMV占比"] for r in tail), 2)}
key = {r["群体"]: r for r in rows}
M["2018重要价值"] = key["重要价值"]
M["2018重要挽留"] = key["重要挽留"]
M["2018重要保持"] = key["重要保持"]
M["2018一般挽留"] = key["一般挽留"]
M["2018复购率"] = year_rows[-1]["复购率"]
M["2015复购率"] = year_rows[0]["复购率"]
M["会员增长"] = round((year_rows[-1]["会员数"] / year_rows[0]["会员数"] - 1) * 100, 1)
M["单次客户数"] = int((y18["f"] == 1).sum())

json.dump(M, open(os.path.join(OUT, "metrics_rfm.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

# ================= 图 1：人数占比 vs GMV 占比 =================
fig, ax = plt.subplots(figsize=(8.4, 4.2))
x = range(len(rows))
w = 0.38
b1 = ax.bar([i - w / 2 for i in x], [r["人数占比"] for r in rows], width=w, color=MUTED, label="人数占比")
b2 = ax.bar([i + w / 2 for i in x], [r["GMV占比"] for r in rows], width=w, color=ACCENT, label="GMV 占比")
for bars_ in (b1, b2):
    for bar in bars_:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{bar.get_height():.1f}", ha="center", fontsize=7.2, color="#444444")
ax.set_xticks(list(x))
ax.set_xticklabels([r["群体"] for r in rows], fontsize=9)
ax.set_ylabel("占比（%）")
ax.set_ylim(0, max(max(r["人数占比"] for r in rows), max(r["GMV占比"] for r in rows)) * 1.25)
ax.legend(frameon=False, fontsize=8.5, loc="upper right")
ax.set_title("图1  重要价值客户占 %.1f%% 人数、贡献 %.1f%% GMV（%.1f 倍）；一般挽留占 %.1f%% 人数仅贡献 %.1f%%"
             % (key["重要价值"]["人数占比"], key["重要价值"]["GMV占比"], key["重要价值"]["贡献倍数"],
                key["一般挽留"]["人数占比"], key["一般挽留"]["GMV占比"]),
             fontsize=9, color=ACCENT, loc="left")
fig.savefig(os.path.join(CHART, "01_head_vs_share.png"))
plt.close(fig)

# ================= 图 2：价值矩阵散点 =================
fig, ax = plt.subplots(figsize=(7.6, 4.6))
mx = max(r["人数占比"] for r in rows) * 1.18
my = max(r["GMV占比"] for r in rows) * 1.18
ax.plot([0, mx], [0, my], ls="--", lw=1, color="#BBBBBB", zorder=1)
ax.text(mx * 0.62, my * 0.68, "贡献 = 人数", color="#999999", fontsize=7.5, rotation=30)
for r in rows:
    color = ACCENT if r["群体"].startswith("重要") else ACCENT2
    ax.scatter(r["人数占比"], r["GMV占比"], s=r["人均消费"] / 4 + 45, color=color,
               alpha=0.78, edgecolor="white", zorder=3)
    ax.annotate(r["群体"], (r["人数占比"], r["GMV占比"]), textcoords="offset points",
                xytext=(7, 6), fontsize=8, color="#333333")
ax.set_xlabel("人数占比（%）")
ax.set_ylabel("GMV 占比（%）")
ax.set_xlim(0, mx)
ax.set_ylim(0, my)
ax.scatter([], [], s=90, color=ACCENT, label="重要类（M 高）")
ax.scatter([], [], s=90, color=ACCENT2, label="一般类（M 低）")
ax.legend(frameon=False, fontsize=8, loc="upper left")
ax.set_title("图2  对角线以上 = 贡献高于人数占比；气泡大小为客单价", fontsize=9.5, color=ACCENT, loc="left")
fig.savefig(os.path.join(CHART, "02_matrix.png"))
plt.close(fig)

# ================= 图 3：会员增长 vs 复购率 =================
fig, ax1 = plt.subplots(figsize=(8.4, 4.0))
ys = [str(t["year"]) for t in year_rows]
ax1.bar(ys, [t["会员数"] for t in year_rows], color=MUTED, width=0.5, label="会员数")
for i, t in enumerate(year_rows):
    ax1.text(i, t["会员数"] + 900, f"{t['会员数']:,}", ha="center", fontsize=8, color="#444444")
ax1.set_ylabel("会员数（人）")
ax1.set_ylim(0, max(t["会员数"] for t in year_rows) * 1.25)
ax2 = ax1.twinx()
ax2.plot(ys, [t["复购率"] for t in year_rows], color=ACCENT2, lw=2, marker="o", ms=5, label="复购率")
for i, t in enumerate(year_rows):
    ax2.annotate(f"{t['复购率']:.1f}%", (i, t["复购率"]), textcoords="offset points",
                 xytext=(0, 9), ha="center", fontsize=8, color=ACCENT2)
ax2.set_ylabel("复购率（%）")
ax2.set_ylim(0, max(t["复购率"] for t in year_rows) * 1.6)
ax2.grid(False)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8, frameon=False)
ax1.set_title("图3  会员数 4 年增长 %.0f%%，复购率 %.1f%%→%.1f%% 缓慢抬升，但 2018 年仍有 %.1f%%（%s 人）全年仅 1 单"
              % (M["会员增长"], M["2015复购率"], M["2018复购率"], 100 - M["2018复购率"],
                 f"{M['单次客户数']:,}"),
              fontsize=9, color=ACCENT, loc="left")
ax1.grid(axis="x", visible=False)
fig.savefig(os.path.join(CHART, "03_growth.png"))
plt.close(fig)

# ================= 图 4：人均消费对比 =================
rr = sorted(rows, key=lambda x: x["人均消费"])
fig, ax = plt.subplots(figsize=(8.4, 4.0))
bars = ax.barh([r["群体"] for r in rr], [r["人均消费"] for r in rr],
               color=[ACCENT if r["群体"].startswith("重要") else MUTED for r in rr], height=0.62)
for b, r in zip(bars, rr):
    ax.text(b.get_width() + 150, b.get_y() + b.get_height() / 2,
            f"{r['人均消费']:,.0f} 元 / 人均 {r['人均订单']:.1f} 单",
            va="center", fontsize=8, color="#444444")
ax.set_xlabel("2018 年人均消费（元）")
ax.set_xlim(0, max(r["人均消费"] for r in rr) * 1.45)
ax.set_title("图4  八类客户的人均消费与人均订单：重要价值客户人均 %.0f 元、%.1f 单"
             % (key["重要价值"]["人均消费"], key["重要价值"]["人均订单"]),
             fontsize=9.5, color=ACCENT, loc="left")
ax.grid(axis="y", visible=False)
fig.savefig(os.path.join(CHART, "04_value.png"))
plt.close(fig)

print(json.dumps({k: M[k] for k in ["订单总数", "阈值", "年度概览", "2018头部四类", "2018长尾四类",
                                    "2018复购率", "2015复购率", "会员增长", "单次客户数"]},
                 ensure_ascii=False, indent=2))
print("\n2018 分层：")
for r in rows:
    print(f"{r['群体']:<5} 人数{r['人数']:>6} ({r['人数占比']:>5.1f}%)  GMV占比{r['GMV占比']:>5.1f}%  "
          f"倍数{r['贡献倍数']:>5.1f}  人均{r['人均消费']:>8,.0f}元  人均{r['人均订单']:>4.1f}单")
print("\ncharts:", sorted(os.listdir(CHART)))
