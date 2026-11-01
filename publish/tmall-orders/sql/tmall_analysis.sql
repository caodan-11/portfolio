-- ============================================================
-- 天猫订单经营分析（2020-02）MySQL 版取数逻辑
-- 与 analyze_tmall.py 的 Pandas 口径完全一致，可用于面试演示
-- 环境：MySQL 8.0+
-- ============================================================

-- 1. 建表 -----------------------------------------------------
DROP TABLE IF EXISTS tmall_orders;
CREATE TABLE tmall_orders (
    order_id      VARCHAR(32)   NOT NULL COMMENT '订单编号',
    total_amount  DECIMAL(12,2) NOT NULL COMMENT '总金额',
    paid_amount   DECIMAL(12,2) NOT NULL COMMENT '买家实际支付金额',
    province_raw  VARCHAR(64)   NOT NULL COMMENT '收货地址（原始）',
    created_at    DATETIME      NOT NULL COMMENT '订单创建时间',
    paid_at       DATETIME      NULL     COMMENT '订单付款时间，NULL = 未付款',
    refund_amount DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '退款金额',
    PRIMARY KEY (order_id),
    KEY idx_created (created_at),
    KEY idx_paid (paid_at)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- 入库：先用 LOAD DATA 直接导入原始 CSV，再统一更新省份
-- LOAD DATA LOCAL INFILE 'tmall_order_report.csv'
-- INTO TABLE tmall_orders_stage
-- FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
-- LINES TERMINATED BY '\n' IGNORE 1 LINES;
-- （stage 表字段与 CSV 一一对应，之后按需清洗入 tmall_orders）

-- 省份标准化：去掉“省/市/自治区/维吾尔/回族/壮族”
UPDATE tmall_orders
SET province_raw = TRIM(
        REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(province_raw,
            '自治区',''), '维吾尔',''), '回族',''), '壮族',''), '省',''), '市','')
    );


-- 2. 整体指标（订单 / 成交率 / 退款率 / GMV / 实收） ----------
SELECT
    COUNT(*)                                        AS 总订单数,
    SUM(paid_at IS NOT NULL)                        AS 已付款订单数,
    SUM(paid_at IS NULL)                            AS 未付款订单数,
    ROUND(SUM(paid_at IS NOT NULL) / COUNT(*) * 100, 2)  AS 成交率_pct,
    SUM(refund_amount > 0)                          AS 退款订单数,
    ROUND(SUM(refund_amount > 0) / SUM(paid_at IS NOT NULL) * 100, 2) AS 退款率_pct,
    ROUND(SUM(IF(paid_at IS NOT NULL, total_amount, 0)), 2)    AS GMV,
    ROUND(SUM(IF(paid_at IS NOT NULL, paid_amount, 0)), 2)     AS 实收金额,
    ROUND(SUM(IF(paid_at IS NOT NULL, refund_amount, 0)), 2)   AS 退款金额,
    ROUND(SUM(IF(paid_at IS NOT NULL, total_amount, 0))
          / SUM(paid_at IS NOT NULL), 2)            AS 客单价
FROM tmall_orders;


-- 3. 日趋势：每日订单量、已付款量、成交率 ----------------------
--    用于观察 2/10–2/16 断档与下旬爆发
SELECT
    DATE(created_at)                                AS 日期,
    COUNT(*)                                        AS 创建订单数,
    SUM(paid_at IS NOT NULL)                        AS 已付款订单数,
    ROUND(SUM(paid_at IS NOT NULL) / COUNT(*) * 100, 1) AS 成交率_pct
FROM tmall_orders
GROUP BY DATE(created_at)
ORDER BY 日期;


-- 4. 分时段下单结构与成交率（一天 24 小时） ---------------------
SELECT
    HOUR(created_at)                                AS 小时,
    COUNT(*)                                        AS 订单数,
    ROUND(COUNT(*) / (SELECT COUNT(*) FROM tmall_orders) * 100, 1) AS 订单占比_pct,
    ROUND(SUM(paid_at IS NOT NULL) / COUNT(*) * 100, 1)           AS 成交率_pct
FROM tmall_orders
GROUP BY HOUR(created_at)
ORDER BY 小时;

-- 4.1 三段式汇总（凌晨 / 白天 / 晚间）
SELECT
    CASE
        WHEN HOUR(created_at) BETWEEN 0  AND 6  THEN '凌晨 0-6'
        WHEN HOUR(created_at) BETWEEN 7  AND 18 THEN '白天 7-18'
        ELSE '晚间 19-23'
    END                                             AS 时段,
    COUNT(*)                                        AS 订单数,
    ROUND(COUNT(*) / (SELECT COUNT(*) FROM tmall_orders) * 100, 1) AS 订单占比_pct,
    ROUND(SUM(paid_at IS NOT NULL) / COUNT(*) * 100, 1)           AS 成交率_pct
FROM tmall_orders
GROUP BY 时段
ORDER BY 订单数 DESC;


-- 5. 省份 TOP10：订单量 + 成交率 + 退款率 -----------------------
SELECT
    province_raw                                    AS 省份,
    COUNT(*)                                        AS 订单数,
    ROUND(COUNT(*) / (SELECT COUNT(*) FROM tmall_orders) * 100, 2) AS 订单占比_pct,
    SUM(paid_at IS NOT NULL)                        AS 已付款订单数,
    ROUND(SUM(paid_at IS NOT NULL) / COUNT(*) * 100, 2)           AS 成交率_pct,
    ROUND(SUM(refund_amount > 0) / SUM(paid_at IS NOT NULL) * 100, 2) AS 退款率_pct,
    ROUND(SUM(IF(paid_at IS NOT NULL, total_amount, 0)) / 10000, 2)   AS GMV_万元
FROM tmall_orders
GROUP BY province_raw
ORDER BY 订单数 DESC
LIMIT 10;


-- 6. 高退款省份：与全站均值对比（已付款 ≥ 30 单） --------------
WITH site AS (
    SELECT SUM(refund_amount > 0) / SUM(paid_at IS NOT NULL) * 100 AS site_rate
    FROM tmall_orders
)
SELECT
    o.province_raw                                  AS 省份,
    SUM(o.paid_at IS NOT NULL)                      AS 已付款订单数,
    ROUND(SUM(o.refund_amount > 0) / SUM(o.paid_at IS NOT NULL) * 100, 2) AS 退款率_pct,
    ROUND((SUM(o.refund_amount > 0) / SUM(o.paid_at IS NOT NULL) * 100)
          / s.site_rate, 2)                         AS 相对全站倍数
FROM tmall_orders o
CROSS JOIN site s
GROUP BY o.province_raw, s.site_rate
HAVING 已付款订单数 >= 30
ORDER BY 退款率_pct DESC
LIMIT 8;


-- 7. 订单金额分布（已付款订单） --------------------------------
SELECT
    CASE
        WHEN total_amount <  50   THEN '<50'
        WHEN total_amount < 100   THEN '50-100'
        WHEN total_amount < 200   THEN '100-200'
        WHEN total_amount < 300   THEN '200-300'
        WHEN total_amount < 500   THEN '300-500'
        WHEN total_amount < 1000  THEN '500-1000'
        ELSE '>1000'
    END                                             AS 金额区间,
    COUNT(*)                                        AS 订单数,
    ROUND(COUNT(*) / (SELECT COUNT(*) FROM tmall_orders WHERE paid_at IS NOT NULL) * 100, 1) AS 订单占比_pct
FROM tmall_orders
WHERE paid_at IS NOT NULL
GROUP BY 金额区间
ORDER BY MIN(total_amount);


-- 8. 头部集中度：TOP5 / TOP10 省份订单占比 ---------------------
WITH prov AS (
    SELECT province_raw, COUNT(*) AS cnt
    FROM tmall_orders
    GROUP BY province_raw
),
ranked AS (
    SELECT province_raw, cnt,
           ROW_NUMBER() OVER (ORDER BY cnt DESC) AS rk,
           SUM(cnt) OVER () AS total_cnt
    FROM prov
)
SELECT
    ROUND(SUM(CASE WHEN rk <= 5  THEN cnt ELSE 0 END) / MAX(total_cnt) * 100, 2) AS TOP5集中度_pct,
    ROUND(SUM(CASE WHEN rk <= 10 THEN cnt ELSE 0 END) / MAX(total_cnt) * 100, 2) AS TOP10集中度_pct
FROM ranked;
