SELECT
    COUNT(*) AS total_transactions,

    SUM(
        CASE
            WHEN is_cancelled = TRUE THEN 1
            ELSE 0
        END
    ) AS cancelled_transactions,

    SUM(
        CASE
            WHEN is_cancelled = FALSE THEN 1
            ELSE 0
        END
    ) AS normal_transactions,

    ROUND(
        100.0 *
        SUM(CASE WHEN is_cancelled = TRUE THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS cancellation_rate
FROM warehouse.fact_sales;