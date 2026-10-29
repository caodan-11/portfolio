-- ============================================================
-- 会员 RFM 八分层（MySQL 8.0+）
-- 与 analyze_rfm.py 口径一致：R≤90 天、F≥2 次、M≥当年中位数
-- ============================================================

-- 1. 建表（4 年订单合并入库） --------------------------------
DROP TABLE IF EXISTS member_orders;
CREATE TABLE member_orders (
    member_id  BIGINT        NOT NULL COMMENT '会员ID',
    order_id   BIGINT        NOT NULL COMMENT '订单号',
    order_date DATE          NOT NULL COMMENT '提交日期',
    amount     DECIMAL(12,2) NOT NULL COMMENT '订单金额',
    PRIMARY KEY (order_id),
    KEY idx_member (member_id),
    KEY idx_date (order_date)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- 入库建议：每年一个 CSV，用 LOAD DATA 导入后加 year 列，或建 4 张分年表再 UNION ALL。
-- ALTER TABLE member_orders ADD COLUMN year INT AS (YEAR(order_date)) STORED;

-- 2. 每年每人算 R / F / M ------------------------------------
CREATE OR REPLACE VIEW v_rfm_raw AS
SELECT
    YEAR(order_date)                   AS year,
    member_id,
    DATEDIFF(MAKEDATE(YEAR(order_date), 1) + INTERVAL 1 YEAR - INTERVAL 1 DAY,
             MAX(order_date))          AS r_days,   -- 距当年最后一天的天数
    COUNT(DISTINCT order_id)           AS f_times,
    SUM(amount)                        AS m_amount
FROM member_orders
WHERE amount > 1                            -- 剔除测试单/补偿单
GROUP BY YEAR(order_date), member_id;

-- 3. 取当年 M 的中位数（MySQL 8 用窗口函数取中位） -----------
CREATE OR REPLACE VIEW v_m_median AS
SELECT year, AVG(m_amount) AS m_median
FROM (
    SELECT year, m_amount,
           ROW_NUMBER() OVER (PARTITION BY year ORDER BY m_amount) AS rn,
           COUNT(*)     OVER (PARTITION BY year)                   AS cnt
    FROM v_rfm_raw
) t
WHERE rn IN (FLOOR((cnt + 1) / 2), CEIL((cnt + 1) / 2))
GROUP BY year;

-- 4. 八分层 --------------------------------------------------
CREATE OR REPLACE VIEW v_rfm_layers AS
SELECT
    r.year              AS 年份,
    r.member_id         AS 会员ID,
    r.r_days            AS R天,
    r.f_times           AS F次,
    r.m_amount          AS M金额,
    CASE WHEN r.r_days <= 90 THEN 1 ELSE 0 END                    AS R高,
    CASE WHEN r.f_times >= 2 THEN 1 ELSE 0 END                    AS F高,
    CASE WHEN r.m_amount >= m.m_median THEN 1 ELSE 0 END          AS M高,
    CASE
        WHEN r.r_days <= 90 AND r.f_times >= 2 AND r.m_amount >= m.m_median THEN '重要价值'
        WHEN r.r_days >  90 AND r.f_times >= 2 AND r.m_amount >= m.m_median THEN '重要保持'
        WHEN r.r_days <= 90 AND r.f_times <  2 AND r.m_amount >= m.m_median THEN '重要发展'
        WHEN r.r_days >  90 AND r.f_times <  2 AND r.m_amount >= m.m_median THEN '重要挽留'
        WHEN r.r_days <= 90 AND r.f_times >= 2 AND r.m_amount <  m.m_median THEN '一般价值'
        WHEN r.r_days >  90 AND r.f_times >= 2 AND r.m_amount <  m.m_median THEN '一般保持'
        WHEN r.r_days <= 90 AND r.f_times <  2 AND r.m_amount <  m.m_median THEN '一般发展'
        ELSE '一般挽留'
    END                 AS 群体
FROM v_rfm_raw r
JOIN v_m_median m ON m.year = r.year;

-- 5. 2018 年分层汇总（人数 / GMV / 人均 / 贡献倍数） ---------
WITH agg AS (
    SELECT 群体,
           COUNT(*)               AS 人数,
           SUM(M金额)             AS GMV,
           SUM(F次)               AS 订单数,
           AVG(M金额)             AS 人均消费,
           AVG(F次)               AS 人均订单,
           AVG(R天)               AS 平均R天
    FROM v_rfm_layers
    WHERE 年份 = 2018
    GROUP BY 群体
)
SELECT
    群体,
    人数,
    ROUND(人数 / SUM(人数) OVER () * 100, 2)            AS 人数占比_pct,
    ROUND(GMV / SUM(GMV) OVER () * 100, 2)              AS GMV占比_pct,
    ROUND((GMV / SUM(GMV) OVER ()) / (人数 / SUM(人数) OVER ()) , 2) AS 贡献倍数,
    ROUND(人均消费, 0)                                   AS 人均消费,
    ROUND(人均订单, 1)                                   AS 人均订单,
    ROUND(平均R天, 0)                                    AS 平均R天
FROM agg
ORDER BY GMV占比_pct DESC;

-- 6. 头部四类 vs 长尾四类 ------------------------------------
SELECT
    CASE WHEN 群体 LIKE '重要%' THEN '头部四类' ELSE '长尾四类' END AS 分组,
    COUNT(*)                                              AS 人数,
    ROUND(COUNT(*) / (SELECT COUNT(*) FROM v_rfm_layers WHERE 年份 = 2018) * 100, 2) AS 人数占比_pct,
    ROUND(SUM(M金额) / (SELECT SUM(M金额) FROM v_rfm_layers WHERE 年份 = 2018) * 100, 2) AS GMV占比_pct
FROM v_rfm_layers
WHERE 年份 = 2018
GROUP BY 分组;

-- 7. 复购率年度趋势 ------------------------------------------
SELECT
    年份,
    COUNT(*)                                              AS 会员数,
    SUM(F次 >= 2)                                         AS 复购会员数,
    ROUND(SUM(F次 >= 2) / COUNT(*) * 100, 2)               AS 复购率_pct,
    ROUND(SUM(M金额), 0)                                   AS GMV
FROM v_rfm_layers
GROUP BY 年份
ORDER BY 年份;
