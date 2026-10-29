-- ============================================================
-- 多源电商数据对比（MySQL 8.0+）
-- 覆盖：美妆快照的日增量与折扣分析、日化订单的客户帕累托
-- ============================================================

-- ===================== 一、美妆（C 端快照） =====================
DROP TABLE IF EXISTS beauty_snapshot;
CREATE TABLE beauty_snapshot (
    snap_date  DATE          NOT NULL COMMENT '快照日期',
    item_id    VARCHAR(32)   NOT NULL COMMENT '商品 id',
    price      DECIMAL(10,2) NOT NULL COMMENT '当日展示价',
    sale_count INT           NOT NULL COMMENT '当日累计销量',
    shop       VARCHAR(64)   NOT NULL COMMENT '店铺名',
    PRIMARY KEY (snap_date, item_id),
    KEY idx_item (item_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- 1.1 当日新增销量：用 LAG 取前一日累计值做差
WITH t AS (
    SELECT snap_date, item_id, sale_count,
           LAG(sale_count) OVER (PARTITION BY item_id ORDER BY snap_date) AS prev_sale
    FROM beauty_snapshot
)
SELECT snap_date                               AS 日期,
       SUM(GREATEST(sale_count - prev_sale, 0)) AS 当日新增销量
FROM t
WHERE prev_sale IS NOT NULL                    -- 首日没有“前一日”，必须剔除
GROUP BY snap_date
ORDER BY 日期;

-- 1.2 双十一折扣：11/11 与 11/10 两日价格对比
SELECT
    a.item_id                                  AS 商品,
    a.price                                    AS 前一日价,
    b.price                                    AS 双十一价,
    ROUND((1 - b.price / a.price) * 100, 1)    AS 折扣率_pct
FROM beauty_snapshot a
JOIN beauty_snapshot b
  ON a.item_id = b.item_id
 AND a.snap_date = '2016-11-10'
 AND b.snap_date = '2016-11-11'
WHERE a.price > 0
ORDER BY 折扣率_pct DESC;

-- 1.3 折扣分档 vs 当日增量（含未降价）
WITH price_pair AS (
    SELECT a.item_id,
           (1 - b.price / a.price) AS disc,
           GREATEST(b.sale_count - a.sale_count, 0) AS inc
    FROM beauty_snapshot a
    JOIN beauty_snapshot b
      ON a.item_id = b.item_id
     AND a.snap_date = '2016-11-10'
     AND b.snap_date = '2016-11-11'
    WHERE a.price > 0
)
SELECT
    CASE
        WHEN disc <= 0.001 THEN '未降价'
        WHEN disc <= 0.10  THEN '0-10%'
        WHEN disc <= 0.20  THEN '10-20%'
        WHEN disc <= 0.30  THEN '20-30%'
        WHEN disc <= 0.40  THEN '30-40%'
        ELSE '>40%'
    END                                        AS 折扣档,
    COUNT(*)                                   AS 商品数,
    SUM(inc)                                   AS 当日增量,
    ROUND(SUM(inc) / COUNT(*), 0)              AS 单商品均增量
FROM price_pair
GROUP BY 折扣档
ORDER BY 单商品均增量 DESC;

-- 1.4 价格带结构（取最后一天快照）
SELECT
    CASE
        WHEN price < 100  THEN '<100'
        WHEN price < 200  THEN '100-200'
        WHEN price < 300  THEN '200-300'
        WHEN price < 500  THEN '300-500'
        WHEN price < 1000 THEN '500-1000'
        ELSE '>1000'
    END                                        AS 价格带,
    COUNT(*)                                   AS 商品数,
    SUM(sale_count)                            AS 销量,
    SUM(price * sale_count)                    AS 销售额
FROM beauty_snapshot
WHERE snap_date = (SELECT MAX(snap_date) FROM beauty_snapshot)
GROUP BY 价格带
ORDER BY MIN(price);

-- 1.5 店铺集中度（TOP5 占比）
WITH s AS (
    SELECT shop, SUM(sale_count) AS sale
    FROM beauty_snapshot
    WHERE snap_date = (SELECT MAX(snap_date) FROM beauty_snapshot)
    GROUP BY shop
), r AS (
    SELECT shop, sale,
           ROW_NUMBER() OVER (ORDER BY sale DESC) AS rk,
           SUM(sale) OVER () AS total
    FROM s
)
SELECT shop AS 店铺, sale AS 销量,
       ROUND(sale / total * 100, 1) AS 占比_pct,
       ROUND(SUM(CASE WHEN rk <= 5 THEN sale ELSE 0 END) OVER () / MAX(total) * 100, 1) AS TOP5占比_pct
FROM r
ORDER BY rk
LIMIT 10;


-- ===================== 二、日化（B 端订单） =====================
DROP TABLE IF EXISTS dailychem_item;
CREATE TABLE dailychem_item (
    item_id   VARCHAR(16) NOT NULL COMMENT '商品编号',
    item_name VARCHAR(64) COMMENT '商品名称',
    sub_cat   VARCHAR(32) COMMENT '商品小类',
    big_cat   VARCHAR(32) COMMENT '商品大类',
    list_price DECIMAL(10,2) COMMENT '销售单价',
    PRIMARY KEY (item_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

DROP TABLE IF EXISTS dailychem_order;
CREATE TABLE dailychem_order (
    order_id   VARCHAR(32) NOT NULL COMMENT '订单编码',
    order_date DATE        NOT NULL COMMENT '订单日期',
    cust_id    VARCHAR(32) NOT NULL COMMENT '客户编码',
    region     VARCHAR(16) COMMENT '所在区域',
    province   VARCHAR(32) COMMENT '所在省份',
    city       VARCHAR(32) COMMENT '所在地市',
    item_id    VARCHAR(16) NOT NULL COMMENT '商品编号',
    qty        INT         NOT NULL COMMENT '订购数量',
    unit_price DECIMAL(10,2) NOT NULL COMMENT '订购单价',
    amount     DECIMAL(14,2) NOT NULL COMMENT '金额',
    KEY idx_cust (cust_id),
    KEY idx_date (order_date)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- 2.1 月度采购额（只保留 2019 年，缺月不外推）
SELECT MONTH(order_date)          AS 月份,
       ROUND(SUM(amount) / 10000, 0) AS 采购额_万元,
       COUNT(DISTINCT order_id)   AS 订单数,
       COUNT(DISTINCT cust_id)    AS 客户数
FROM dailychem_order
WHERE order_date >= '2019-01-01' AND order_date < '2020-01-01'
GROUP BY MONTH(order_date)
ORDER BY 月份;

-- 2.2 客户帕累托：TOP10% / 20% / 30% 的采购额占比
WITH c AS (
    SELECT cust_id, SUM(amount) AS amt
    FROM dailychem_order
    WHERE order_date >= '2019-01-01' AND order_date < '2020-01-01'
    GROUP BY cust_id
), r AS (
    SELECT amt,
           ROW_NUMBER() OVER (ORDER BY amt DESC) AS rk,
           COUNT(*) OVER ()                      AS n,
           SUM(amt) OVER ()                      AS total
    FROM c
)
SELECT
    ROUND(SUM(CASE WHEN rk <= n * 0.1 THEN amt ELSE 0 END) / MAX(total) * 100, 1) AS TOP10_pct,
    ROUND(SUM(CASE WHEN rk <= n * 0.2 THEN amt ELSE 0 END) / MAX(total) * 100, 1) AS TOP20_pct,
    ROUND(SUM(CASE WHEN rk <= n * 0.3 THEN amt ELSE 0 END) / MAX(total) * 100, 1) AS TOP30_pct
FROM r;

-- 2.3 客户复购率与平均下单次数
SELECT
    COUNT(*)                                  AS 客户数,
    ROUND(AVG(cnt), 2)                        AS 人均下单次数,
    ROUND(SUM(cnt >= 2) / COUNT(*) * 100, 1)  AS 复购率_pct
FROM (
    SELECT cust_id, COUNT(DISTINCT order_id) AS cnt
    FROM dailychem_order
    WHERE order_date >= '2019-01-01' AND order_date < '2020-01-01'
    GROUP BY cust_id
) t;

-- 2.4 区域结构（先去空格，异常区域单独可见）
SELECT TRIM(REPLACE(region, ' ', '')) AS 区域,
       ROUND(SUM(amount) / 10000, 0)  AS 采购额_万元,
       COUNT(DISTINCT cust_id)        AS 客户数
FROM dailychem_order
GROUP BY 区域
ORDER BY 采购额_万元 DESC;

-- 2.5 品类结构（联商品维表）
SELECT i.big_cat                       AS 商品大类,
       ROUND(SUM(o.amount) / 10000, 0) AS 采购额_万元,
       ROUND(SUM(o.amount) / (SELECT SUM(amount) FROM dailychem_order) * 100, 1) AS 占比_pct
FROM dailychem_order o
LEFT JOIN dailychem_item i ON i.item_id = o.item_id
GROUP BY i.big_cat
ORDER BY 采购额_万元 DESC;
