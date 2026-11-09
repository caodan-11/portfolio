# -*- coding: utf-8 -*-
"""RFM 会员价值分层 —— 按 notebook 的真实做法出图"""
import os
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

warnings.filterwarnings("ignore")

SRC = r"D:\python\JupyterProject\data\sale_rfm_group.xlsx"
OUT = r"D:\deepseek工作文件夹\作品集\RFM用户分层\charts"
os.makedirs(OUT, exist_ok=True)

for f in [r"C:\Windows\Fonts\msyh.ttc"]:
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = "Microsoft YaHei"
plt.rcParams["axes.unicode_minus"] = False

NAVY, BLUE, RED, GRAY = "#1F3A5F", "#8FA9C4", "#C0504D", "#9AA5B1"

g = pd.read_excel(SRC)
g["rfm_group"] = g["rfm_group"].astype(str)

def style(ax, title, xlabel="", ylabel=""):
    ax.set_title(title, fontsize=13, color=NAVY, pad=12, fontweight="bold")
    ax.set_xlabel(xlabel, fontsize=10, color="#444")
    ax.set_ylabel(ylabel, fontsize=10, color="#444")
    ax.grid(axis="y", alpha=0.25, linestyle="--")
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

# 1) 年度会员数与订单数
year = g.groupby("year").agg(会员数=("会员ID", "nunique"), 订单数=("f", "sum"))
print(year.to_string())
fig, ax = plt.subplots(figsize=(8.6, 3.6))
x = np.arange(len(year))
ax.bar(x - 0.2, year["会员数"], width=0.38, color=NAVY, label="会员数")
ax.bar(x + 0.2, year["订单数"], width=0.38, color=BLUE, label="订单数")
ax.set_xticks(x)
ax.set_xticklabels([f"{y} 年" for y in year.index])
ax.legend(frameon=False, fontsize=9)
style(ax, "四年间会员数从 2.8 万增至 5.4 万，订单数同步上升", "年份", "数量")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "01_year.png"), dpi=150)
plt.close()

# 2) 人群组合 × 年份 热力图
pivot = g.pivot_table(index="rfm_group", columns="year", values="会员ID", aggfunc="count").fillna(0)
top_groups = pivot.sum(axis=1).sort_values(ascending=False).head(15).index
pivot_top = pivot.loc[top_groups]

fig, ax = plt.subplots(figsize=(8.6, 5.2))
im = ax.imshow(pivot_top.values, aspect="auto", cmap="Blues")
ax.set_xticks(range(len(pivot_top.columns)))
ax.set_xticklabels([f"{c} 年" for c in pivot_top.columns])
ax.set_yticks(range(len(pivot_top.index)))
ax.set_yticklabels(pivot_top.index, fontsize=9)
for i in range(len(pivot_top.index)):
    for j in range(len(pivot_top.columns)):
        v = int(pivot_top.values[i, j])
        ax.text(j, i, f"{v:,}", ha="center", va="center", fontsize=7.5,
                color="white" if v > pivot_top.values.max() * 0.5 else "#333")
ax.set_title("人数最多的 15 类人群在四年间的变化", fontsize=13, color=NAVY, pad=12, fontweight="bold")
ax.set_xlabel("年份", fontsize=10, color="#444")
ax.set_ylabel("人群标签（R F M 三档组合）", fontsize=10, color="#444")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "02_heatmap.png"), dpi=150)
plt.close()

# 3) 2018 年 TOP10 人群：人数占比 vs 金额占比
y18 = g[g["year"] == 2018]
grp = y18.groupby("rfm_group").agg(人数=("会员ID", "count"), 金额=("m", "sum"))
grp["人数占比"] = grp["人数"] / grp["人数"].sum() * 100
grp["金额占比"] = grp["金额"] / grp["金额"].sum() * 100
top10 = grp.sort_values("金额占比", ascending=False).head(10)
print(top10.round(2).to_string())

fig, ax = plt.subplots(figsize=(9, 4.2))
x = np.arange(len(top10))
ax.bar(x - 0.2, top10["人数占比"], width=0.38, color=BLUE, label="人数占比")
ax.bar(x + 0.2, top10["金额占比"], width=0.38, color=NAVY, label="金额占比")
ax.set_xticks(x)
ax.set_xticklabels(top10.index, fontsize=9)
ax.legend(frameon=False, fontsize=9)
style(ax, "2018 年金额贡献最高的 10 类人群：少数人群贡献了大部分销售额", "人群标签", "占比（%）")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "03_top_groups.png"), dpi=150)
plt.close()

# 4) R/F/M 三档人数分布
fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
for ax, (col, name) in zip(axes, [("r_label", "R 最近购买"), ("f_label", "F 购买频次"), ("m_label", "M 消费金额")]):
    vc = g[col].value_counts().sort_index()
    ax.bar([f"{int(i)} 档" for i in vc.index], vc.values, color=NAVY)
    ax.set_title(name, fontsize=11, color=NAVY)
    ax.grid(axis="y", alpha=0.25, linestyle="--")
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.suptitle("R / F / M 三档人数分布：绝大多数会员只落在最低频次档", fontsize=13,
             color=NAVY, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "04_dist.png"), dpi=150, bbox_inches="tight")
plt.close()

# 统计
print("\n复购率(2018):", round((y18["f"] >= 2).sum() / y18["会员ID"].nunique() * 100, 1), "%")
print("单次购买占比(2018):", round((y18["f"] == 1).sum() / y18["会员ID"].nunique() * 100, 1), "%")
print("人群组合数:", g["rfm_group"].nunique(), "| 会员数:", g["会员ID"].nunique(), "| 记录数:", len(g))
