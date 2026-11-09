-- =============================================================
-- RFM 会员价值分层 · SQL 脚本
-- 数据：sales.xlsx（2015–2018 四个年度 sheet + 会员等级）
-- 口径：R/F/M 各切三档，R 越小分越高、F 与 M 越大分越高
-- 分档边界（与 Pandas 中的手动分箱一致）：
--   R: <=79 天 → 3 分；80–255 天 → 2 分；256 天以上 → 1 分
--   F: 1 次   → 1 分；2–5 次   → 2 分；6 次以上  → 3 分
--   M: <=69 元 → 1 分；70–1199 元 → 2 分；1200 元以上 → 3 分
-- =============================================================

-- 1. 合并四个年度表（表结构一致：会员ID、订单号、提交日期、订单金额）
CREATE OR REPLACE VIEW v_orders_all AS
SELECT 2015 AS 年份, 会员ID, 订单号, 提交日期, 订单金额 FROM sales_2015
UNION ALL
SELECT 2016, 会员ID, 订单号, 提交日期, 订单金额 FROM sales_2016
UNION ALL
SELECT 2017, 会员ID, 订单号, 提交日期, 订单金额 FROM sales_2017
UNION ALL
SELECT 2018, 会员ID, 订单号, 提交日期, 订单金额 FROM sales_2018;

-- 2. 三步清洗：删缺失、过滤金额 > 1、确定每年的观察截止日
CREATE OR REPLACE VIEW v_orders_clean AS
SELECT
    o.年份,
    o.会员ID,
    o.订单号,
    o.提交日期,
    o.订单金额,
    STR_TO_DATE(CONCAT(o.年份, '-12-31'), '%Y-%m-%d')                      AS 观察截止日,
    DATEDIFF(STR_TO_DATE(CONCAT(o.年份, '-12-31'), '%Y-%m-%d'), o.提交日期) AS 距截止日天数
FROM v_orders_all o
WHERE o.会员ID IS NOT NULL
  AND o.提交日期 IS NOT NULL
  AND o.订单金额 IS NOT NULL
  AND o.订单金额 > 1;

-- 3. 按「年份 + 会员」聚合出 R / F / M
CREATE OR REPLACE VIEW v_rfm_base AS
SELECT
    年份,
    会员ID,
    MIN(距截止日天数) AS R_天数,   -- 最近一次购买距今
    COUNT(订单号)     AS F_次数,   -- 当年购买次数
    SUM(订单金额)     AS M_金额    -- 当年消费金额
FROM v_orders_clean
GROUP BY 年份, 会员ID;

-- 4. 三档打分（R 反向）
CREATE OR REPLACE VIEW v_rfm_scored AS
SELECT
    年份, 会员ID, R_天数, F_次数, ROUND(M_金额, 2) AS M_金额,
    CASE WHEN R_天数 <= 79 THEN 3 WHEN R_天数 <= 255 THEN 2 ELSE 1 END AS R档,
    CASE WHEN F_次数 = 1 THEN 1 WHEN F_次数 <= 5 THEN 2 ELSE 3 END     AS F档,
    CASE WHEN M_金额 <= 69 THEN 1 WHEN M_金额 <= 1199 THEN 2 ELSE 3 END AS M档
FROM v_rfm_base;

-- 5. 拼成三位人群标签（如 213 表示 R2 / F1 / M3）
CREATE OR REPLACE VIEW v_rfm_group AS
SELECT 年份, 会员ID, R_天数, F_次数, M_金额,
       CONCAT(R档, F档, M档) AS 人群标签
FROM v_rfm_scored;

-- 6. 各年度概览：会员数、订单数、复购率
SELECT
    年份,
    COUNT(DISTINCT 会员ID)                          AS 会员数,
    SUM(F_次数)                                     AS 订单数,
    ROUND(SUM(F_次数 >= 2) / COUNT(*) * 100, 1)      AS 复购率_百分比,
    ROUND(SUM(M_金额) / 10000, 1)                    AS 销售额_万元
FROM v_rfm_base
GROUP BY 年份
ORDER BY 年份;

-- 7. 2018 年各人群：人数占比 vs 金额占比
SELECT
    人群标签,
    COUNT(*)                                              AS 人数,
    ROUND(SUM(M_金额) / 10000, 1)                          AS 金额_万元,
    ROUND(COUNT(*) / SUM(COUNT(*)) OVER () * 100, 2)       AS 人数占比,
    ROUND(SUM(M_金额) / SUM(SUM(M_金额)) OVER () * 100, 2) AS 金额占比,
    RANK() OVER (ORDER BY SUM(M_金额) DESC)                AS 金额排名
FROM v_rfm_group
WHERE 年份 = 2018
GROUP BY 人群标签
ORDER BY 金额排名;

-- 8. 分档人数分布（验证分箱是否合理）
SELECT 'R' AS 指标, R档 AS 分数, COUNT(*) AS 人数 FROM v_rfm_group GROUP BY R档
UNION ALL SELECT 'F', F档, COUNT(*) FROM v_rfm_group GROUP BY F档
UNION ALL SELECT 'M', M档, COUNT(*) FROM v_rfm_group GROUP BY M档
ORDER BY 指标, 分数;

-- 9. 导出结果表（对应 notebook 中 to_sql 写入的 rfm_table）
CREATE TABLE rfm_table AS SELECT * FROM v_rfm_group;
