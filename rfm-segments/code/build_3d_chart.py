# -*- coding: utf-8 -*-
"""RFM 3D 柱形图 —— 按 render.html 里的 pyecharts Bar3D 配置还原
   标题：RFM分组结果 ｜ 轴：分组名称 / 年份 / 会员数量
   色阶：visualMap 的 11 色 ｜ 视角：alpha 20 / beta 40 ｜ 25 类人群全显示
"""
import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.mplot3d import Axes3D  # noqa

warnings.filterwarnings("ignore")

SRC = r"D:\python\JupyterProject\data\sale_rfm_group.xlsx"
OUT = r"D:\deepseek工作文件夹\作品集\RFM用户分层\charts"
os.makedirs(OUT, exist_ok=True)

for f in [r"C:\Windows\Fonts\msyh.ttc"]:
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = "Microsoft YaHei"
plt.rcParams["axes.unicode_minus"] = False

# render.html 里 visualMap.inRange.color
RANGE_COLOR = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8',
               '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
cmap = LinearSegmentedColormap.from_list("rfm", RANGE_COLOR)

g = pd.read_excel(SRC)
g["rfm_group"] = g["rfm_group"].astype(str)

pivot = g.pivot_table(index="rfm_group", columns="year", values="会员ID", aggfunc="count").fillna(0)
pivot = pivot.sort_index()          # 与 render.html 一致：111 → 333
years = sorted(pivot.columns)
zmax = int(pivot.values.max())

fig = plt.figure(figsize=(13.2, 6.8))
ax = fig.add_subplot(111, projection="3d")

xpos, ypos = np.meshgrid(np.arange(len(pivot.index)), np.arange(len(years)), indexing="ij")
xpos = xpos.ravel().astype(float)
ypos = ypos.ravel().astype(float)
zpos = np.zeros_like(xpos)
dz = pivot.values.ravel().astype(float)

dx = dy = 0.58
norm = Normalize(vmin=0, vmax=zmax)
ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=cmap(norm(dz)),
         edgecolor="#FFFFFF", linewidth=0.25, shade=False)

ax.set_xticks(np.arange(len(pivot.index)) + dx / 2)
ax.set_xticklabels(pivot.index, fontsize=6.8, rotation=45, ha="right")
ax.set_yticks(np.arange(len(years)) + dy / 2)
ax.set_yticklabels([str(y) for y in years], fontsize=9)

ax.set_xlabel("分组名称", fontsize=10, labelpad=12)
ax.set_ylabel("年份", fontsize=10, labelpad=10)
ax.set_zlabel("")

ax.set_zlim(0, zmax * 1.02)
ax.view_init(elev=20, azim=-40)
ax.set_box_aspect((2.2, 1.0, 1.0))

for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
    axis.pane.fill = True
    axis.pane.set_facecolor((1, 1, 1, 1))
    axis.pane.set_edgecolor("#E8EDF3")
ax.grid(True, color="#F0F4F8", linewidth=0.5)

ax.set_title("RFM分组结果", fontsize=14, color="#2F4554", fontweight="bold", pad=6)

# visualMap：竖排连续色阶，约 5 段刻度
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
ticks = MaxNLocator(nbins=5).tick_values(0, zmax)
cbar = fig.colorbar(sm, ax=ax, shrink=0.62, pad=0.06, aspect=16, ticks=ticks)
cbar.ax.tick_params(labelsize=8, colors="#7A8A9A")
cbar.set_label("会员数量", fontsize=9, color="#44566C", labelpad=8)
cbar.outline.set_edgecolor("#E8EDF3")

plt.tight_layout()
path = os.path.join(OUT, "05_3d_bar.png")
plt.savefig(path, dpi=170, bbox_inches="tight", facecolor="white")
plt.close()
print("已生成:", path)
print("人群数:", len(pivot.index), "| 最大值:", zmax)
