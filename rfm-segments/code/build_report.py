# -*- coding: utf-8 -*-
"""《RFM 会员价值分层分析报告》v2：加入 3D 柱形图，成果与简历对齐"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = r"D:\deepseek工作文件夹\作品集\RFM用户分层"
CHARTS = os.path.join(ROOT, "charts")
OUT = os.path.join(ROOT, "会员价值分层分析报告.docx")

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
GRAY = RGBColor(0x55, 0x5F, 0x6B)
FONT = "微软雅黑"

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.top_margin, sec.bottom_margin = Cm(2.2), Cm(2.0)
sec.left_margin, sec.right_margin = Cm(2.4), Cm(2.4)
st = doc.styles["Normal"]
st.font.name = FONT
st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)


def para(text="", size=10.5, bold=False, color=None, before=0, after=6, spacing=1.5, align=None, indent=0):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(before); pf.space_after = Pt(after); pf.line_spacing = spacing
    if indent:
        pf.first_line_indent = Cm(indent)
    if align:
        p.alignment = align
    if text:
        r = p.add_run(text)
        r.font.size = Pt(size); r.font.bold = bold; r.font.name = FONT
        r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        if color:
            r.font.color.rgb = color
    return p


def h1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.size = Pt(15); r.font.bold = True; r.font.name = FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    r.font.color.rgb = NAVY
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single"); b.set(qn("w:sz"), "8"); b.set(qn("w:space"), "4"); b.set(qn("w:color"), "1F3A5F")
    pBdr.append(b); pPr.append(pBdr)


def h2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.size = Pt(12); r.font.bold = True; r.font.name = FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    r.font.color.rgb = RGBColor(0x2E, 0x5A, 0x88)


def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.45
    r = p.add_run(text)
    r.font.size = Pt(10.5); r.font.name = FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)


def figure(path, caption, width=14.2):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Cm(width))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(8)
    r = c.add_run(caption)
    r.font.size = Pt(9); r.font.name = FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    r.font.color.rgb = GRAY


def finding(text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(4); pf.space_after = Pt(8); pf.line_spacing = 1.5
    pf.left_indent = Cm(0.3)
    r = p.add_run("成果：" + text)
    r.font.size = Pt(10.5); r.font.name = FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    r.font.color.rgb = RGBColor(0x2E, 0x5A, 0x88)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single"); left.set(qn("w:sz"), "18"); left.set(qn("w:space"), "8"); left.set(qn("w:color"), "8FA9C4")
    pBdr.append(left); pPr.append(pBdr)


def data_box(rows):
    t = doc.add_table(rows=0, cols=4)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i in range(0, len(rows), 2):
        cells = t.add_row().cells
        for j, (k, v) in enumerate(rows[i:i + 2]):
            for c, txt, bold, color in ((cells[j * 2], k, False, GRAY), (cells[j * 2 + 1], v, True, NAVY)):
                c.text = ""
                p = c.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(txt)
                r.font.size = Pt(10); r.font.bold = bold; r.font.name = FONT
                r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
                r.font.color.rgb = color
    for row in t.rows:
        for i, w in enumerate([5.2, 3.2, 5.2, 3.2]):
            row.cells[i].width = Cm(w)


def table(headers, rows, widths):
    t = doc.add_table(rows=0, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for ri, row in enumerate([headers] + rows):
        cells = t.add_row().cells
        for ci, v in enumerate(row):
            cells[ci].text = ""
            p = cells[ci].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(v))
            r.font.size = Pt(9.5); r.font.bold = ri == 0; r.font.name = FONT
            r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
            if ri == 0:
                shd = OxmlElement("w:shd"); shd.set(qn("w:fill"), "E8EEF5")
                cells[ci]._tc.get_or_add_tcPr().append(shd)
    for row in t.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)


# ==================== 封面 ====================
para(); para()
para("RFM 会员价值分层分析报告", size=26, bold=True, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, after=4)
para("2015–2018 年会员订单 · 12.9 万会员 · 20.3 万单", size=12, color=GRAY, align=WD_ALIGN_PARAGRAPH.CENTER, after=30)
para("曹丹 ｜ 信息与计算科学 ｜ 现居广州", size=10.5, color=GRAY, align=WD_ALIGN_PARAGRAPH.CENTER, after=4)
para("2026 年 6 月", size=10.5, color=GRAY, align=WD_ALIGN_PARAGRAPH.CENTER, after=40)
para("这份报告回答什么", size=11, bold=True, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, after=6)
para("用四年的会员订单数据，按最近购买时间（R）、购买频次（F）、消费金额（M）三项打分，\n"
     "把会员划分成不同人群，回答一个问题：**有限的运营资源，先投给谁？**",
     size=10, color=GRAY, align=WD_ALIGN_PARAGRAPH.CENTER, after=0, spacing=1.7)
doc.add_page_break()

# ==================== 一、数据 ====================
h1("一、数据集与清洗")
h2("1.1 数据长什么样")
para("原始数据是一份 Excel，包含 5 个 sheet：2015、2016、2017、2018 与「会员等级」。"
     "前四张表结构一致，字段为会员 ID、订单号、提交日期与订单金额；「会员等级」表记录每个会员的等级，"
     "本次分析只作参考、未参与计算。", indent=0.74)
table(["Sheet", "行数", "字段", "是否参与计算"],
      [["2015", "30,774", "会员ID / 订单号 / 提交日期 / 订单金额", "是"],
       ["2016", "41,278", "同上", "是"],
       ["2017", "50,839", "同上", "是"],
       ["2018", "81,349", "同上", "是"],
       ["会员等级", "154,385", "会员ID / 会员等级", "否（仅参考）"]],
      [3.2, 3.2, 7.6, 3.6])

h2("1.2 三步清洗")
para("原始数据无法直接出报表，先合并四张年度表，再做三步处理：", after=4)
bullet("删除缺失值：去掉会员 ID、日期或金额为空的记录；")
bullet("过滤异常金额：只保留订单金额大于 1 元的记录，剔掉测试单与异常单；")
bullet("固定观察节点：以每年最后一天作为该年的分析截止日，并算出每笔订单距该节点的天数——这是计算 R 的基础。")

h2("1.3 清洗后的规模")
data_box([
    ("年-会员记录", "148,591 条"),
    ("去重会员数", "129,447 名"),
    ("订单总数", "202,827 单"),
    ("覆盖年份", "2015–2018"),
])

# ==================== 二、怎么算 ====================
h1("二、RFM 是怎么算的")
h2("2.1 三项指标")
table(["指标", "含义", "取值方向"],
      [["R（Recency）", "最近一次购买距今多少天", "越小越好"],
       ["F（Frequency）", "当年购买次数", "越大越好"],
       ["M（Monetary）", "当年累计消费金额", "越大越好"]],
      [4.0, 8.0, 5.0])

h2("2.2 分档与打分")
para("用 Pandas 的区间切分（pd.cut）把三项各切成三档，区间边界是手动指定的业务阈值，不是等距划分：", after=4)
bullet("R：≤79 天 / 80–255 天 / 256–365 天 → 打 3 / 2 / 1 分（最近买过的得分最高）；")
bullet("F：1 次 / 2–5 次 / 6 次以上 → 打 1 / 2 / 3 分；")
bullet("M：≤69 元 / 70–1,199 元 / 1,200 元以上 → 打 1 / 2 / 3 分。")
para("三项分数拼成一个三位标签（如 213 表示 R 2 档、F 1 档、M 3 档），实际数据中出现 25 种组合。",
     indent=0.74)
figure(os.path.join(CHARTS, "04_dist.png"), "图 1　R / F / M 三档人数分布")

# ==================== 三、人群结构 ====================
h1("三、人群结构与三维可视化")
h2("3.1 先用 3D 图看整体")
para("把「人群标签 × 年份 × 人数」做成三维柱形图：横轴是人群标签，纵轴是年份，柱子高度代表该年这类人有多少。"
     "这样一眼能看出哪些人群在变大、哪些在萎缩。", indent=0.74)
figure(os.path.join(CHARTS, "05_3d_bar.png"), "图 2　人群 × 年份 × 人数（三维柱形图）", width=15.0)
finding("人数最多的是 212 类，且四年持续增长，2018 年达到 14,297 人；而 213、313 这类人群虽然人数不多，"
        "金额贡献却排在最前面——这正是分层要解决的问题。")

h2("3.2 四年的规模变化")
para("把每年的会员数与订单数放在一起看：会员数从 2.8 万增长到 5.4 万，订单数同步上升，说明盘子主要靠拉新扩张。",
     indent=0.74)
figure(os.path.join(CHARTS, "01_year.png"), "图 3　四年会员数与订单数")

h2("3.3 谁贡献了销售额")
para("只看 2018 年，按金额贡献排序，前 10 类人群的「人数占比」与「金额占比」对比非常明显："
     "人数最多的 212 类金额贡献只有 5.4%，而人数只占 11.8% 的 213 类贡献了 30.9%。", indent=0.74)
figure(os.path.join(CHARTS, "03_top_groups.png"), "图 4　2018 年金额贡献 TOP10 人群")
finding("213 类：人数占 11.8%、金额占 30.9%——这类客户买得多、金额高，是最该优先维护的一群。")

# ==================== 四、业务解读 ====================
h1("四、业务解读")
h2("4.1 复购才是增长空间")
para("2018 年的 5.4 万名会员里，只有 14.4% 当年购买过两次及以上，其余 85.6% 只买过一次。"
     "换句话说，这个生意的盘子主要靠不断拉新撑起来，复购环节几乎是空的——"
     "把复购率往上提一点，带来的增量会比多投一笔广告更确定。", indent=0.74)
finding("复购率 14.4%、85.6% 的会员全年只买一次，说明「留住老客」比「再拉一波新客」更划算。")

h2("4.2 分层的用法：先找谁")
para("分层的价值不在分数本身，而在排序：", after=4)
bullet("金额贡献高、且最近还买过（如 213、313）→ 优先维护，适合做专属权益与新品试用；")
bullet("金额贡献高、但很久没买 → 唤醒优先级最高，因为流失成本最大；")
bullet("只买过一次、金额也低的大多数 → 用通用活动覆盖即可，不投过多资源。")

h2("4.3 结果落库")
para("分层结果同时导出到 Excel 与 MySQL（用 sqlalchemy 写入数据表），便于后续按月增量刷新；"
     "三维图与二维修表配合使用：三维图看趋势，二维表看具体数字。", indent=0.74)

# ==================== 五、局限 ====================
h1("五、局限")
bullet("「会员等级」表未参与计算，若作为分层维度可能得到更细的结论；")
bullet("分档边界是手动指定的业务阈值，不是等距或等频划分，换一套边界会得到不同的人群划分；")
bullet("数据只覆盖 2015–2018 年，没有更近期的数据，结论无法外推到当前业务；")
bullet("本报告基于公开数据集计算，不代表任何公司真实经营情况。")

doc.save(OUT)
print("已生成:", OUT)
