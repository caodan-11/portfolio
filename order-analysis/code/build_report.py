# -*- coding: utf-8 -*-
"""《电商订单数据分析报告》v3：每个部分按「数据集介绍 → 关键数据 → 可视化与成果」展开"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = r"D:\deepseek工作文件夹\作品集\电商订单数据分析"
CHARTS = os.path.join(ROOT, "charts")
OUT = os.path.join(ROOT, "电商订单数据分析报告.docx")

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


def para(text="", size=10.5, bold=False, color=None, before=0, after=6, spacing=1.5,
         align=None, indent=0):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = spacing
    if indent:
        pf.first_line_indent = Cm(indent)
    if align:
        p.alignment = align
    if text:
        r = p.add_run(text)
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.name = FONT
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
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.name = FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    r.font.color.rgb = NAVY
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single"); b.set(qn("w:sz"), "8"); b.set(qn("w:space"), "4"); b.set(qn("w:color"), "1F3A5F")
    pBdr.append(b)
    pPr.append(pBdr)


def h2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.name = FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    r.font.color.rgb = RGBColor(0x2E, 0x5A, 0x88)


def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.45
    r = p.add_run(text)
    r.font.size = Pt(10.5)
    r.font.name = FONT
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
    r.font.size = Pt(9)
    r.font.name = FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    r.font.color.rgb = GRAY


def data_box(rows):
    """关键数据：两列小表（指标 / 数值）"""
    t = doc.add_table(rows=0, cols=4)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    # 每行放两组（指标, 数值）
    for i in range(0, len(rows), 2):
        cells = t.add_row().cells
        pair = rows[i:i + 2]
        for j, (k, v) in enumerate(pair):
            c1, c2 = cells[j * 2], cells[j * 2 + 1]
            for c, txt, bold, color in ((c1, k, False, GRAY), (c2, v, True, NAVY)):
                c.text = ""
                p = c.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(txt)
                r.font.size = Pt(10)
                r.font.bold = bold
                r.font.name = FONT
                r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
                r.font.color.rgb = color
    for row in t.rows:
        for i, w in enumerate([5.2, 3.2, 5.2, 3.2]):
            row.cells[i].width = Cm(w)
    return t


def finding(text):
    """小结论块：左侧竖线的段落"""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(4)
    pf.space_after = Pt(6)
    pf.line_spacing = 1.5
    pf.left_indent = Cm(0.3)
    r = p.add_run("成果：" + text)
    r.font.size = Pt(10.5)
    r.font.name = FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    r.font.color.rgb = RGBColor(0x2E, 0x5A, 0x88)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single"); left.set(qn("w:sz"), "18"); left.set(qn("w:space"), "8"); left.set(qn("w:color"), "8FA9C4")
    pBdr.append(left)
    pPr.append(pBdr)


# ==================== 封面 ====================
para(); para()
para("电商订单数据分析报告", size=26, bold=True, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, after=4)
para("天猫订单 · 双十一美妆 · 日化批发", size=12, color=GRAY, align=WD_ALIGN_PARAGRAPH.CENTER, after=30)
para("曹丹 ｜ 信息与计算科学 ｜ 现居广州", size=10.5, color=GRAY, align=WD_ALIGN_PARAGRAPH.CENTER, after=4)
para("2026 年 8 月", size=10.5, color=GRAY, align=WD_ALIGN_PARAGRAPH.CENTER, after=40)
para("关于这份报告", size=11, bold=True, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, after=6)
para("手上是三份公开数据集，来源、字段与统计口径都不同——订单粒度、时间范围、商品体系都对不上。\n"
     "因此按三部分分别分析，每一部分都按「先看数据长什么样 → 挑出关键数字 → 用图说明 → 得出成果」的顺序展开，"
     "不做跨数据集的横向对比。",
     size=10, color=GRAY, align=WD_ALIGN_PARAGRAPH.CENTER, after=0, spacing=1.7)
doc.add_page_break()

# ==================== 一、三份数据 ====================
h1("一、三份数据分别是什么")
table_rows = [
    ["部分", "数据集", "规模", "分析目标"],
    ["Part 1", "天猫订单明细", "28,010 单，2020 年 2 月", "下单在时间和地域上的规律"],
    ["Part 2", "双十一淘宝美妆", "27,598 条，22 家店铺，10 天快照", "大促期间销量走势、谁卖得多谁卖得贵"],
    ["Part 3", "日化批发订单", "3.1 万单，1,084 个客户，122 个 SKU", "需求在月份 / 地区 / 品类上的分布"],
]
t = doc.add_table(rows=0, cols=4)
t.style = "Table Grid"
t.alignment = WD_TABLE_ALIGNMENT.CENTER
for ri, row in enumerate(table_rows):
    cells = t.add_row().cells
    for ci, v in enumerate(row):
        cells[ci].text = ""
        p = cells[ci].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(v)
        r.font.size = Pt(9.5)
        r.font.bold = ri == 0
        r.font.name = FONT
        r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        if ri == 0:
            shd = OxmlElement("w:shd"); shd.set(qn("w:fill"), "E8EEF5")
            cells[ci]._tc.get_or_add_tcPr().append(shd)
for row in t.rows:
    for i, w in enumerate([2.2, 4.2, 7.6, 3.6]):
        row.cells[i].width = Cm(w)

para()
para("三份数据的关联性弱，合并会掩盖各自的业务特征，所以保持独立分析——这是刻意的处理，"
     "不是把不同来源的数字硬凑到一起。", color=GRAY, size=10, spacing=1.6)

# ==================== 二、Part 1 ====================
doc.add_page_break()
h1("二、Part 1：天猫订单数据分析")

h2("2.1 数据集介绍")
para("2020 年 2 月的天猫订单明细，共 28,010 条。字段包括订单编号、总金额、买家实际支付金额、收货地址、"
     "订单创建时间、订单付款时间与退款金额。", indent=0.74)
para("清洗用代码完成：去掉列名与单元格里的空格、处理空值与重复记录，把收货地址里的省份名称统一（去掉「省 / 自治区」）。"
     "其中「订单付款时间」为空代表该订单未付款，这是判断成交的依据。", indent=0.74)

h2("2.2 关键数据")
data_box([
    ("总订单数", "28,010 单"),
    ("已付款订单", "24,087 单"),
    ("成交率", "86.0%"),
    ("退款率", "23.4%"),
])
para("这组数字用来交代基本盘；本部分真正的分析放在时间维度上。", color=GRAY, size=9.5, after=4)

h2("2.3 下单的地域分布：没有形成规律")
para("按省份统计订单量与销售额并做分布图，各省之间的差异没有呈现稳定结构——既没有明显的头部省份，"
     "也没有可解释的区域特征。因此这一维度不展开，把分析重点转到时间。", indent=0.74)

h2("2.4 每日订单量：上半月受疫情压制，下旬回升")
para("按订单创建日期汇总每日订单量，趋势非常清晰：2 月上半月日均处于低位，中旬起快速抬升，下旬明显高于上旬。"
     "这与 2020 年 2 月的复工节奏一致。", indent=0.74)
figure(os.path.join(CHARTS, "01_tmall_daily.png"), "图 1　每日订单量走势（2020 年 2 月）")
finding("时间维度的结论可以直接用来解释「为什么上旬数据难看」——不是需求消失，而是复工节奏问题。")

h2("2.5 每小时订单量：一天有三个高峰")
para("把下单时间按小时聚合，一天中出现三个明显高峰：10 点、15 点与 21 点；其中 21–22 点是一天中最高的时段，"
     "凌晨 0–6 点则处于低位。", indent=0.74)
figure(os.path.join(CHARTS, "02_tmall_hourly.png"), "图 2　每小时订单量分布")
para("这条结论对运营有直接用处：", after=3)
bullet("高峰期尤其是夜间 21–22 点，应保障客服响应速度，避免因回复不及时丢单；")
bullet("这也解释了电商为什么普遍设夜班——夜间是下单主力时段，但响应能力往往最弱；")
bullet("凌晨订单量低，客服排班可以向白天与夜间高峰倾斜，而不是平均分配。")

# ==================== 三、Part 2 ====================
h1("三、Part 2：双十一淘宝美妆数据分析")

h2("3.1 数据集介绍")
para("双十一期间（11 月 5 日–11 月 14 日）各店铺、各商品的每日销售快照，共 27,598 条，覆盖 22 家店铺。"
     "字段包括日期、店铺、商品、价格、销量与评论数。", indent=0.74)
para("清洗用代码完成：处理空格、空值与重复记录，把日期统一成日级，并派生出「销售额 = 销量 × 单价」用于横向比较。",
     indent=0.74)

h2("3.2 关键数据")
data_box([
    ("日销量峰值", "约 3,332 万"),
    ("峰值出现日", "11 月 9 日"),
    ("TOP10 第一名占比", "23.21%"),
    ("最贵店铺均价", "约 1,361 元"),
])

h2("3.3 每日销量走势：大促期间起落明显")
para("把每天所有商品销量相加得到日销量曲线：最高约 3,332 万、最低约 2,782 万、平均约 3,160 万，"
     "峰值出现在 11 月 9 日，11 日前后出现明显回落。", indent=0.74)
figure(os.path.join(CHARTS, "03_beauty_daily.png"), "图 3　每日整体销量走势")
finding("大促的放量集中在前半段，后半段回落——备货和投放节奏应跟着这个曲线走，而不是平均铺在整个活动期。")

h2("3.4 谁卖得最多：TOP10 里第一名独占两成")
para("按 11 月 5–14 日累计销量排出 TOP10，同时看销量与销售额；结果头部集中度很高："
     "第一名相宜本草一家就占了前十总量的 23.21%。", indent=0.74)
figure(os.path.join(CHARTS, "04_beauty_top10.png"), "图 4　店铺累计销量 TOP10")
finding("资源集中投放到头部店铺的确定性最高，但长尾店铺仍然值得留一点预算做测款。")

h2("3.5 谁卖得最贵：均价 TOP20")
para("按各店铺商品的平均价格排序，最贵的是娇兰，约 1,361 元。把价格榜与销量榜放在一起，"
     "可以区分两类店铺：一类靠低价走量，一类靠高客单支撑。", indent=0.74)
figure(os.path.join(CHARTS, "05_beauty_price.png"), "图 5　店铺平均价格 TOP20")
finding("同样的销售额，可能来自两种完全不同的经营模型——分析时不区分，就会把两种店混为一谈。")

# ==================== 四、Part 3 ====================
h1("四、Part 3：日化批发订单分析")

h2("4.1 数据集介绍")
para("日化美妆的批发订单，分成两张表：订单表 3.1 万条（订单日期、客户编码、区域 / 省份 / 地市、商品编号、"
     "订购数量、单价、金额），商品表 122 个 SKU（含商品大类与小类）。", indent=0.74)
para("清洗用代码完成：按商品编号把两张表关联，处理空格、空值与重复记录，统一日期格式，"
     "并把「订购数量」里带「个」的文本去掉、转成数值。", indent=0.74)

h2("4.2 关键数据")
data_box([
    ("订购峰值月", "7 月"),
    ("客户数", "1,084 个"),
    ("护肤品占比", "约 85%"),
    ("需求最大小类", "面膜"),
])

h2("4.3 月度订购：单峰结构")
para("按月汇总订购量，呈单峰曲线：1 月最低，7 月达到顶峰，之后回落（数据覆盖 1–9 月）。"
     "这种结构说明这批客户的下单有明显季节性，备货与资金安排应围绕夏季高峰展开。", indent=0.74)
figure(os.path.join(CHARTS, "06_chem_monthly.png"), "图 6　每月订购情况")
finding("旺季集中在夏季，1 月是最低点——淡季做客户维护、旺季前一个月备货，节奏比平均用力更有效。")

h2("4.4 地区分布：集中在华东与华南几座城市")
para("按地市统计订购量，前五名依次为上海、苏州、重庆、深圳、泉州。需求集中在几座城市而不是均匀分布，"
     "这与批发业务依托区域代理或大客户的模式相符。", indent=0.74)
figure(os.path.join(CHARTS, "07_chem_city.png"), "图 7　地区订购量 TOP20")
finding("区域集中意味着可以用少量人力覆盖主要市场，但也意味着单点风险——前五城市的客户流失值得单独盯。")

h2("4.5 品类结构：护肤品占绝对主导")
para("把订单与商品表关联后按品类汇总，护肤品约占订购量的 85%，彩妆约 15%；细分到小类，需求量最大的是面膜。",
     indent=0.74)
figure(os.path.join(CHARTS, "08_chem_category.png"), "图 8　商品小类需求量 TOP8")
finding("选品与库存的重心应放在护肤品，尤其是面膜这类高频消耗品。")

h2("4.6 客户价值：RFM 加权打分")
para("用 RFM 对 1,084 个批发客户打分：R 取最近一次购买时间、F 取订单数、M 取累计金额，三项排名后"
     "按 R 20%、F 30%、M 50% 加权，得到价值分数并排序。80 分以上可视为优质客户。", indent=0.74)
figure(os.path.join(CHARTS, "09_chem_rfm.png"), "图 9　客户 RFM 得分分布")
finding("同一个 RFM 方法在天猫（C 端）和日化（B 端）上的效果完全不同——B 端客户基数小、单笔大，分层更依赖金额。")

# ==================== 五、结论 ====================
h1("五、结论与局限")
h2("5.1 三部分各自的结论")
table2 = [
    ["部分", "核心结论"],
    ["天猫订单", "上半月受疫情压制、下旬回升；下单集中在 10 / 15 / 21 点，21–22 点最高，夜间需保障客服响应"],
    ["双十一美妆", "日销量峰值在 11 月 9 日；头部集中度高，相宜本草占 TOP10 的 23.2%；均价最高为娇兰约 1,361 元"],
    ["日化批发", "订购单峰、7 月最高；地区集中在前五城市；护肤品占 85%、面膜需求最大；客户可按 RFM 排序"],
]
t2 = doc.add_table(rows=0, cols=2)
t2.style = "Table Grid"
t2.alignment = WD_TABLE_ALIGNMENT.CENTER
for ri, row in enumerate(table2):
    cells = t2.add_row().cells
    for ci, v in enumerate(row):
        cells[ci].text = ""
        p = cells[ci].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(v)
        r.font.size = Pt(9.5); r.font.bold = ri == 0; r.font.name = FONT
        r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        if ri == 0:
            shd = OxmlElement("w:shd"); shd.set(qn("w:fill"), "E8EEF5")
            cells[ci]._tc.get_or_add_tcPr().append(shd)
for row in t2.rows:
    for i, w in enumerate([3.6, 13.4]):
        row.cells[i].width = Cm(w)

para()
h2("5.2 局限")
bullet("三份数据的时间范围、商品体系与订单粒度都不同，结论只在各自数据内成立，不能互相外推；")
bullet("天猫数据没有退款原因字段，退款率只能描述规模，不能归因；")
bullet("美妆数据为每日销售快照，反映当天销量，不能当作累计值使用；")
bullet("地区维度在天猫数据上没有形成规律，这不代表「地区不重要」，只代表这份数据里看不出结构。")

doc.save(OUT)
print("已生成:", OUT)
