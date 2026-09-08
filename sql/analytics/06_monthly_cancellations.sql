SELECT
    d.year,
    d.month,

    ROUND(
        SUM(
            CASE
                WHEN f.is_cancelled = TRUE
                THEN f.sales_amount
                ELSE 0
            END
        ),
        2
    ) AS cancelled_sales,

    COUNT(
        CASE
            WHEN f.is_cancelled = TRUE
            THEN 1
        END
    ) AS cancelled_transactions

FROM warehouse.fact_sales f

JOIN warehouse.dim_date d
    ON f.date_key = d.date_key

GROUP BY
    d.year,
    d.month

ORDER BY
    d.year,
    d.month;