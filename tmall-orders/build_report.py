# -*- coding: utf-8 -*-
"""生成《天猫订单经营分析》报告 docx（真实数据）"""
import json
import os

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = r"D:\deepseek工作文件夹\作品集\电商订单经营分析"
M = json.load(open(os.path.join(OUT, "metrics.json"), encoding="utf-8"))
FONT = "微软雅黑"
ACCENT = (0x1F, 0x3A, 0x5F)
GRAY = (0x78, 0x78, 0x78)
BLACK = (0x20, 0x20, 0x20)


def n0(x):
    return f"{x:.0f}"


def n1(x):
    return f"{x:.1f}"


def style_run(run, size=10.5, bold=False, color=BLACK, italic=False):
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.name = FONT
    run.font.color.rgb = RGBColor(*color)
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(attr), FONT)


def p(doc, text, size=10.5, bold=False, color=BLACK, before=0, after=3,
      spacing=1.4, align=None, italic=False, keep=False):
    par = doc.add_paragraph()
    pf = par.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = spacing
    pf.keep_with_next = keep
    if align is not None:
        par.alignment = align
    style_run(par.add_run(text), size, bold, color, italic)
    return par


def h1(doc, text):
    par = doc.add_paragraph()
    pf = par.paragraph_format
    pf.space_before = Pt(13)
    pf.space_after = Pt(5)
    pf.line_spacing = 1.0
    pf.keep_with_next = True
    style_run(par.add_run(text), 13.5, True, ACCENT)
    pPr = par._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single")
    b.set(qn("w:sz"), "8")
    b.set(qn("w:space"), "3")
    b.set(qn("w:color"), "1F3A5F")
    pBdr.append(b)
    pPr.append(pBdr)
    return par


def h2(doc, text):
    par = doc.add_paragraph()
    pf = par.paragraph_format
    pf.space_before = Pt(9)
    pf.space_after = Pt(2)
    pf.line_spacing = 1.0
    pf.keep_with_next = True
    style_run(par.add_run(text), 11, True, BLACK)
    return par


def bullet(doc, text, size=10.5):
    par = doc.add_paragraph()
    pf = par.paragraph_format
    pf.left_indent = Cm(0.6)
    pf.first_line_indent = Cm(-0.6)
    pf.space_after = Pt(1.5)
    pf.line_spacing = 1.35
    style_run(par.add_run("•  "), size, False, ACCENT)
    style_run(par.add_run(text), size)
    return par


def table(doc, headers, rows, widths=None, size=9):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        par = hdr[i].paragraphs[0]
        par.paragraph_format.space_after = Pt(1)
        style_run(par.add_run(h), size, True, (0xFF, 0xFF, 0xFF))
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), "1F3A5F")
        hdr[i]._tc.get_or_add_tcPr().append(shd)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            par = cells[i].paragraphs[0]
            par.paragraph_format.space_after = Pt(1)
            style_run(par.add_run(str(v)), size, False, BLACK)
    if widths:
        t.autofit = False
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "fixed")
        t._tbl.tblPr.append(layout)
        for i, gc in enumerate(t._tbl.tblGrid.findall(qn("w:gridCol"))):
            if i < len(widths):
                gc.set(qn("w:w"), str(int(widths[i] * 567)))
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    trPr.append(th)
    for row in t.rows:
        rpr = row._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit")
        rpr.append(cs)
    return t


def figure(doc, path, caption):
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_before = Pt(4)
    par.paragraph_format.space_after = Pt(1)
    par.paragraph_format.keep_with_next = True
    par.add_run().add_picture(path, width=Cm(14.2))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(4)
    style_run(cap.add_run(caption), 8, False, GRAY, True)


doc = Document()
sec = doc.sections[0]
sec.page_height = Cm(29.7)
sec.page_width = Cm(21.0)
sec.top_margin = Cm(1.9)
sec.bottom_margin = Cm(1.7)
sec.left_margin = Cm(2.1)
sec.right_margin = Cm(2.1)
normal = doc.styles["Normal"]
normal.font.name = FONT
normal.font.size = Pt(10.5)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

# ================= 封面 =================
p(doc, "天猫订单经营分析", size=24, bold=True, color=ACCENT, before=40, after=2,
  align=WD_ALIGN_PARAGRAPH.CENTER)
p(doc, "2020 年 2 月：订单波动结构与退款归因", size=14, bold=True, after=18,
  align=WD_ALIGN_PARAGRAPH.CENTER)
p(doc, "曹  丹", size=12, bold=True, after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
p(doc, "19152046468  ｜  19152046468@163.com  ｜  长沙", size=10, color=GRAY, after=2,
  align=WD_ALIGN_PARAGRAPH.CENTER)
p(doc, "2026 年 10 月 ｜ 数据来源：和鲸社区公开数据集 tmall_order_report.csv（28,010 条订单）",
  size=9, color=GRAY, after=24, align=WD_ALIGN_PARAGRAPH.CENTER)

t = doc.add_table(rows=1, cols=1)
t.style = "Table Grid"
cell = t.rows[0].cells[0]
cell.text = ""
par = cell.paragraphs[0]
par.paragraph_format.space_before = Pt(6)
par.paragraph_format.space_after = Pt(6)
style_run(par.add_run("一句话结论："), 10.5, True, ACCENT)
style_run(par.add_run(
    f"2 月日均订单从 {n0(M['上旬日均'])} 单恢复至 {M['下旬日均']:,.0f} 单（{n1(M['下旬日均']/M['上旬日均'])} 倍），"
    f"流量侧不是问题；真正的损失来自退款——{n1(M['退款率'])}% 的退款率吞掉 {n1(M['GMV流失率'])}% 的 GMV"
    f"（{n1(M['退款金额']/10000)} 万元），其中湖北退款率 {n1(M['高退款率省份'][0]['退款率'])}%、"
    f"为全站的 {n1(M['高退款率省份'][0]['退款率']/M['退款率'])} 倍，问题在履约能力而非需求。"), 10.5)

doc.add_page_break()

# ================= 一 =================
h1(doc, "一、业务背景与问题定义")
h2(doc, "1.1 背景")
p(doc, "2020 年 2 月是疫情冲击最剧烈的一个月：线下门店大面积关闭，线上订单短期集中爆发，同时跨省物流、仓储、"
       "客服大量停摆。对平台和商家来说，这个月最典型的困惑不是“有没有订单”，而是“订单来了，能不能履约”。")
p(doc, f"本次分析基于 {M['日期范围']} 的 {M['总订单数']:,} 条订单数据，从时间结构、地区结构、退款结构三个维度，"
       "定位这个月 GMV 的实际损失来源。")

h2(doc, "1.2 核心问题")
bullet(doc, "问题 1：订单量的波动是需求端还是履约端造成的？时间结构上有什么特征？")
bullet(doc, "问题 2：从“下单”到“实收”之间，GMV 在哪一环流失、流失多少？")
bullet(doc, "问题 3：流失是否集中在特定地区或时段，能否被前置拦截？")

h2(doc, "1.3 分析范围")
table(doc, ["项目", "说明"], [
    ["分析对象", "订单明细（1 张表，7 个字段：订单编号、总金额、实付金额、收货地址、创建时间、付款时间、退款金额）"],
    ["时间范围", f"{M['日期范围']}，共 29 天"],
    ["样本量", f"{M['总订单数']:,} 条订单，覆盖 {M['省份数']} 个省级行政区"],
    ["不纳入", "无用户行为/流量数据、无商品维度、无退款原因字段（见 5.1 局限性）"],
], widths=[3.0, 14.0])

# ================= 二 =================
h1(doc, "二、数据说明与口径")
h2(doc, "2.1 数据来源")
table(doc, ["数据表", "来源", "行数", "时间跨度", "关键字段"], [
    ["tmall_order_report.csv", "和鲸社区公开数据集", f"{M['总订单数']:,}", "2020-02-01 ~ 02-29",
     "订单编号、总金额、实付金额、收货地址、创建时间、付款时间、退款金额"],
], widths=[3.4, 3.4, 1.6, 3.0, 5.6])

h2(doc, "2.2 清洗规则")
table(doc, ["问题", "处理方式", "影响行数", "处理理由"], [
    ["列名含前后空格", "strip 统一列名", "7 列", "避免取列时报 KeyError"],
    ["省份名带“省/市/自治区”", "正则去后缀，统一为简称", f"{M['总订单数']:,}", "保证地区聚合口径一致"],
    ["付款时间为空", "判定为“未付款订单”，不删除", f"{M['未付款订单数']:,}", "这是业务语义，不是缺失值"],
    ["整日数据缺失", "标注断档期，不插值、不平滑", "2 天（2/8、2/16）", "避免虚构数据"],
], widths=[3.6, 5.2, 2.8, 5.4])

h2(doc, "2.3 指标定义")
table(doc, ["指标", "定义", "计算公式"], [
    ["成交率", "创建订单中完成付款的比例", "已付款订单数 / 创建订单数"],
    ["退款率", "已付款订单中发生退款的比例", "退款订单数 / 已付款订单数"],
    ["GMV", "已付款订单的总金额（未扣退款）", "SUM(总金额) WHERE 已付款"],
    ["实收金额", "扣除退款后实际到账金额", "SUM(买家实际支付金额)"],
    ["客单价", "已付款订单的平均金额", "GMV / 已付款订单数"],
    ["集中度", "TOP N 省份订单占全量的比例", "TOP N 订单数 / 总订单数"],
], widths=[2.8, 7.4, 6.8])

h2(doc, "2.4 数据质量提示（重要）")
p(doc, f"数据在 2 月 10 日–16 日出现断档：7 天仅 {M['断档期订单数']} 条订单（占全量 {n1(M['断档期订单占比'])}%），"
       f"其中 {'、'.join(M['缺失日期'])} 整日无数据。这更可能是疫情停摆叠加数据采集中断，而非真实需求归零。"
       f"因此日趋势只做“区间对比”，不做逐日归因；剔除断档后成交率为 {n1(M['剔除断档后成交率'])}%，"
       f"与全月 {n1(M['成交率'])}% 基本一致，说明断档不影响整体结构判断。")

# ================= 三 =================
h1(doc, "三、分析框架")
p(doc, "总览 → 时间结构 → 地区结构 → 退款归因 → 建议。核心思路是把“量”的问题和“钱”的问题分开：量看趋势，钱看流失。")
bullet(doc, "第 1 步：算总账——订单、成交率、退款率、GMV 与实收的差额")
bullet(doc, "第 2 步：拆时间——日粒度看恢复节奏，小时粒度看下单集中度")
bullet(doc, "第 3 步：拆地区——找头部集中度和高退款地区，做交叉验证")
bullet(doc, "第 4 步：对流失环节做归因，给出可前置拦截的动作")

# ================= 四 =================
h1(doc, "四、核心发现")

h2(doc, f"发现 1：订单量“低位—断档—爆发”，下旬日均是上旬的 {n1(M['下旬日均']/M['上旬日均'])} 倍")
figure(doc, os.path.join(OUT, "charts", "01_daily_trend.png"),
       f"数据来源：tmall_order_report.csv，n={M['总订单数']:,}；虚线右轴为成交率（仅统计当日订单≥50 的日期）")
p(doc, f"上旬（2/1–2/10）日均 {n0(M['上旬日均'])} 单，下旬（2/21–2/29）日均 {n0(M['下旬日均'])} 单，恢复倍数达 "
       f"{n1(M['下旬日均']/M['上旬日均'])} 倍；峰值出现在 {M['峰值日']}，单日 {M['峰值日订单']:,} 单。")
p(doc, f"所以呢：这不是一次常规促销，而是“需求被压抑后集中释放”。对运营的含义是——备货、客服、仓配必须按峰值"
       f"（{M['峰值日订单']:,} 单/日）而不是按均值（{n0(M['日均订单'])} 单/日）配置，否则必然出现履约缺口，"
       "而履约缺口正是后文高退款的直接来源。")

h2(doc, "发现 2：下单高度集中在晚间，凌晨仍占近一成")
figure(doc, os.path.join(OUT, "charts", "02_hourly.png"),
       "数据来源：tmall_order_report.csv；成交率右轴已裁切至 82%–89% 以看清差异")
p(doc, f"晚间 19–23 点贡献 {n1(M['晚间19_23点占比'])}% 的订单，其中 20–22 点三个小时就占 {n1(M['晚间20_22点订单占比'])}%；"
       f"白天 7–18 点占 {n1(M['白天7_18点占比'])}%，成交率最高（{n1(M['白天7_18点成交率'])}%）；"
       f"凌晨 0–6 点仍有 {n1(M['凌晨0_6点占比'])}% 的订单，成交率最低（{n1(M['凌晨0_6点成交率'])}%）。")
p(doc, f"所以呢：客服与仓储排班应重点覆盖 19–23 点；凌晨订单无法即时沟通，是未付款订单（全月 {M['未付款订单数']:,} 单）"
       "的高发区，适合用“次日 10 点前提醒付款”这类自动化动作补位。")

h2(doc, f"发现 3：订单高度集中在头部省份，TOP10 贡献 {n1(M['TOP10集中度'])}%")
figure(doc, os.path.join(OUT, "charts", "03_province.png"),
       "数据来源：tmall_order_report.csv；标签为“订单数 / 该省成交率”")
p(doc, f"{M['TOP5省份'][0]['省']}以 {M['TOP5省份'][0]['订单数']:,} 单居首（占 {n1(M['TOP5省份'][0]['占比'])}%），"
       f"且成交率 {n1(M['TOP5省份'][0]['成交率'])}%，为头部省份中最高；TOP5 合计占 {n1(M['TOP5集中度'])}%，"
       f"TOP10 占 {n1(M['TOP10集中度'])}%。")
p(doc, "所以呢：资源可以按“3+2”结构投放——上海、江苏、浙江为核心盘，广东、北京为规模盘；"
       "其余 21 个省份更适合标准化策略（统一活动 + 统一话术），不做定制投入。")

h2(doc, "发现 4：退款是本月最大的黑洞，湖北、新疆异常突出")
figure(doc, os.path.join(OUT, "charts", "04_refund.png"),
       "数据来源：tmall_order_report.csv；仅纳入已付款 ≥30 单的省份，虚线为全站均值")
p(doc, f"全站退款率 {n1(M['退款率'])}%，退款金额 {n1(M['退款金额']/10000)} 万元，"
       f"相当于 GMV（{n1(M['GMV']/10000)} 万元）的 {n1(M['GMV流失率'])}%；实收仅 {n1(M['实收金额']/10000)} 万元。"
       f"地区上看，湖北退款率 {n1(M['高退款率省份'][0]['退款率'])}%（{M['高退款率省份'][0]['已付款']} 单）、"
       f"新疆 {n1(M['高退款率省份'][1]['退款率'])}%（{M['高退款率省份'][1]['已付款']} 单），"
       f"分别是全站均值的 {n1(M['高退款率省份'][0]['退款率']/M['退款率'])} 倍和 "
       f"{n1(M['高退款率省份'][1]['退款率']/M['退款率'])} 倍。")
p(doc, "所以呢：湖北是 2 月疫情中心、新疆属长距离干线，两地共同点是“无法履约”而非“不满意”。"
       "退款不是客服问题，是履约承诺问题——这类退款不需要更多客服，需要在下单环节就把发货预期讲清楚。")

h2(doc, "发现 5：客单价低、结构扁平，头部订单贡献三成 GMV")
figure(doc, os.path.join(OUT, "charts", "05_amount.png"),
       "数据来源：tmall_order_report.csv；仅统计已付款订单（n=24,087）")
p(doc, f"客单价 {n1(M['客单价'])} 元，中位数仅 {n0(M['客单价中位数'])} 元；100 元以下订单占 {n1(M['100元以下订单占比'])}%，"
       f"500 元以上仅 {n1(M['500元以上订单占比'])}%；但头部 10% 的高金额订单贡献了 {n1(M['头部10%订单GMV占比'])}% 的 GMV。")
p(doc, "所以呢：这是一门“高频、低单价”的生意，硬推高客单商品并不现实；提升 GMV 更有效的路径是"
       "组合装/凑单门槛（把 76 元的中位数推过 99 元包邮线），而不是拉高单品价格。")

# ================= 五 =================
h1(doc, "五、结论与建议")
table(doc, ["#", "建议", "对象", "预期影响", "优先级"], [
    ["1", "对湖北、新疆等履约受限地区，下单页前置展示“预计发货时间 + 可延迟发货”选项",
     "商品/履约", "按两地退款金额测算，理论上可拦截 30% 以上相关退款，约 4–5 万元", "P0"],
    ["2", "补齐退款原因字段，按“未发货/物流慢/商品不符/七天无理由”拆分后重新归因",
     "数据/客服", "当前归因靠推断，补齐后可把定位精度提升到原因级", "P0"],
    ["3", "客服与仓配排班覆盖 19–23 点；凌晨订单次日 10 点自动提醒付款",
     "客服/运营", f"针对 {M['未付款订单数']:,} 单未付款订单，成交率每提升 1 个百分点约增 30 万元 GMV", "P1"],
    ["4", "设计 99 元凑单/组合装，把中位数 76 元的客单价推过包邮门槛",
     "商品/营销", "客单价每提升 5%，按当前 GMV 测算月增约 12 万元", "P2"],
], widths=[0.8, 6.8, 2.2, 6.0, 1.4], size=8.5)

h2(doc, "5.1 局限性")
bullet(doc, "样本限制：只有 2020 年 2 月一个月，且处于疫情极端期，恢复倍数不能外推到常态月份。")
bullet(doc, f"数据缺口：{('、'.join(M['缺失日期']))} 整日无数据，2/10–2/16 仅 {M['断档期订单数']} 单，日趋势只能做区间对比。")
bullet(doc, "归因限制：无退款原因字段、无流量/曝光数据，本文对退款的归因是“相关性推断”，不是因果结论。")
bullet(doc, "口径限制：GMV 按订单总金额计，未剔除优惠券成本与平台佣金，与财务口径可能存在差异。")

h2(doc, "5.2 下一步")
bullet(doc, "拉取 1 月与 3 月数据做前后对比，把“疫情异常”和“常态波动”分开。")
bullet(doc, "接入商品维度（类目/SPU），做“地区 × 类目”交叉，验证高退款是否集中在特定品类。")
bullet(doc, "把日/小时/地区/退款四个指标做成周度监控看板，让异常从“月级发现”变成“周级发现”。")

# ================= 六 =================
h1(doc, "六、附录")
table(doc, ["内容", "说明"], [
    ["分析代码", "analyze_tmall.py：Pandas 清洗 + 指标计算 + Matplotlib 出图，一键复现全部数字"],
    ["SQL 版本", "sql/tmall_analysis.sql：与 Python 等价的 MySQL 取数逻辑（建表 + 6 段查询）"],
    ["指标数据", "metrics.json：报告中所有数字的原始计算结果"],
    ["图表源文件", "charts/01–05：150 dpi PNG，可直接复用到汇报 PPT"],
], widths=[3.2, 13.8])

doc.core_properties.title = "天猫订单经营分析"
doc.core_properties.author = "曹丹"
path_docx = os.path.join(OUT, "天猫订单经营分析报告.docx")
doc.save(path_docx)
print("saved:", path_docx)
