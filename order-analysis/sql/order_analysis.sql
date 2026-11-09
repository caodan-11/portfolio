-- =============================================================
-- 电商订单数据分析 · SQL 脚本
-- 三份数据（天猫订单 / 双十一美妆 / 日化批发）分别建表、分别分析
-- 说明：三份数据来源与口径不同，不做跨表关联
-- =============================================================

-- -------------------------------------------------------------
-- Part 1：天猫订单（表 tmall_orders，28,010 行）
-- 字段：订单编号、总金额、买家实际支付金额、收货地址、订单创建时间、订单付款时间、退款金额
-- -------------------------------------------------------------

-- 1.1 整体指标：成交率、退款率、GMV、实收
SELECT
    COUNT(*)                                                          AS 总订单数,
    SUM(订单付款时间 IS NOT NULL)                                      AS 已付款订单,
    ROUND(SUM(订单付款时间 IS NOT NULL) / COUNT(*) * 100, 1)            AS 成交率_百分比,
    ROUND(SUM(退款金额 > 0) / SUM(订单付款时间 IS NOT NULL) * 100, 1)   AS 退款率_百分比,
    ROUND(SUM(CASE WHEN 订单付款时间 IS NOT NULL THEN 总金额 END) / 10000, 2)      AS GMV_万元,
    ROUND(SUM(CASE WHEN 订单付款时间 IS NOT NULL THEN 买家实际支付金额 END) / 10000, 2) AS 实收_万元,
    ROUND(SUM(退款金额) / 10000, 2)                                    AS 退款_万元
FROM tmall_orders;

-- 1.2 每日订单量（看上下半月差异）
SELECT
    DATE(订单创建时间)                     AS 日期,
    COUNT(*)                              AS 订单量,
    SUM(订单付款时间 IS NOT NULL)          AS 已付款,
    ROUND(SUM(订单付款时间 IS NOT NULL) / COUNT(*) * 100, 1) AS 成交率
FROM tmall_orders
GROUP BY DATE(订单创建时间)
ORDER BY 日期;

-- 1.3 每小时的订单量（找下单高峰）
SELECT
    HOUR(订单创建时间)   AS 小时,
    COUNT(*)             AS 订单量,
    RANK() OVER (ORDER BY COUNT(*) DESC) AS 时段排名
FROM tmall_orders
GROUP BY HOUR(订单创建时间)
ORDER BY 小时;

-- 1.4 各地区订单量与销售额（结论：未形成有效规律）
SELECT
    TRIM(REPLACE(REPLACE(REPLACE(收货地址, '省', ''), '自治区', ''), '市', '')) AS 省份,
    COUNT(*)                                                 AS 订单量,
    ROUND(SUM(总金额) / 10000, 2)                            AS 销售额_万元,
    ROUND(SUM(订单付款时间 IS NOT NULL) / COUNT(*) * 100, 1) AS 成交率
FROM tmall_orders
GROUP BY 省份
ORDER BY 订单量 DESC;

-- 1.5 成交率与订单量的时段对比（用窗口函数看时段贡献占比）
SELECT
    小时,
    订单量,
    ROUND(订单量 / SUM(订单量) OVER () * 100, 1) AS 占全天比
FROM (
    SELECT HOUR(订单创建时间) AS 小时, COUNT(*) AS 订单量
    FROM tmall_orders
    GROUP BY HOUR(订单创建时间)
) t
ORDER BY 小时;


-- -------------------------------------------------------------
-- Part 2：双十一美妆（表 beauty_snapshots，27,598 行）
-- 字段：update_time、id、title、price、sale_count、comment_count、店名
-- -------------------------------------------------------------

-- 2.1 每日整体销量（最大 / 最小 / 平均 / 峰值日）
SELECT
    update_time                 AS 日期,
    SUM(sale_count)             AS 当日销量
FROM beauty_snapshots
GROUP BY update_time
ORDER BY 日期;

-- 2.2 累计销量 TOP10 店铺 + 占前十总量的比例
WITH shop AS (
    SELECT 店名, SUM(sale_count) AS 累计销量, SUM(sale_count * price) AS 累计销售额
    FROM beauty_snapshots
    GROUP BY 店名
), top10 AS (
    SELECT * FROM shop ORDER BY 累计销量 DESC LIMIT 10
)
SELECT
    店名,
    累计销量,
    ROUND(累计销售额 / 10000, 1)                        AS 累计销售额_万元,
    ROUND(累计销量 / SUM(累计销量) OVER () * 100, 2)     AS 占TOP10比例
FROM top10
ORDER BY 累计销量 DESC;

-- 2.3 店铺平均价格 TOP20（谁最贵）
SELECT
    店名,
    ROUND(AVG(price), 2)   AS 平均单价,
    COUNT(*)               AS 商品数
FROM beauty_snapshots
GROUP BY 店名
ORDER BY 平均单价 DESC
LIMIT 20;


-- -------------------------------------------------------------
-- Part 3：日化批发（表 chem_orders 订单表 + chem_products 商品表）
-- 订单表：订单编码、订单日期、客户编码、所在区域、所在省份、所在地市、商品编号、订购数量、订购单价、金额
-- 商品表：商品编号、商品名称、商品小类、商品大类、销售单价
-- -------------------------------------------------------------

-- 3.1 月度订购量（看单峰结构）
SELECT
    MONTH(订单日期)      AS 月份,
    SUM(订购数量)        AS 订购量,
    ROUND(SUM(金额), 2)  AS 金额
FROM chem_orders
GROUP BY MONTH(订单日期)
ORDER BY 月份;

-- 3.2 地区订购量 TOP20（按地市）
SELECT
    所在地市,
    SUM(订购数量)        AS 订购量,
    COUNT(DISTINCT 客户编码) AS 客户数,
    RANK() OVER (ORDER BY SUM(订购数量) DESC) AS 排名
FROM chem_orders
GROUP BY 所在地市
ORDER BY 排名
LIMIT 20;

-- 3.3 品类需求结构（订单表关联商品表）
SELECT
    p.商品大类,
    p.商品小类,
    SUM(o.订购数量)                                   AS 订购量,
    ROUND(SUM(o.订购数量) / SUM(SUM(o.订购数量)) OVER () * 100, 2) AS 占总量比
FROM chem_orders o
JOIN chem_products p ON o.商品编号 = p.商品编号
GROUP BY p.商品大类, p.商品小类
ORDER BY 订购量 DESC;

-- 3.4 客户 RFM 打分（R 20% / F 30% / M 50%，三档手动分箱）
WITH base AS (
    SELECT
        客户编码,
        DATEDIFF((SELECT MAX(订单日期) FROM chem_orders), MAX(订单日期)) AS R_天数,
        COUNT(订单编码)  AS F_次数,
        SUM(金额)        AS M_金额
    FROM chem_orders
    GROUP BY 客户编码
), scored AS (
    SELECT
        *,
        CASE WHEN R_天数 <= 79 THEN 3 WHEN R_天数 <= 255 THEN 2 ELSE 1 END AS R档,
        CASE WHEN F_次数 = 1 THEN 1 WHEN F_次数 <= 5 THEN 2 ELSE 3 END    AS F档,
        CASE WHEN M_金额 <= 69 THEN 1 WHEN M_金额 <= 1199 THEN 2 ELSE 3 END AS M档
    FROM base
)
SELECT
    客户编码, R_天数, F_次数, ROUND(M_金额, 2) AS M_金额,
    R档, F档, M档,
    ROUND(R档 * 20 + F档 * 30 + M档 * 50, 1) AS 价值得分,
    RANK() OVER (ORDER BY R档 * 20 + F档 * 30 + M档 * 50 DESC) AS 价值排名
FROM scored
ORDER BY 价值排名;
