SELECT
    d.year,
    d.month,
    ROUND(SUM(f.sales_amount), 2) AS total_sales
FROM warehouse.fact_sales f
JOIN warehouse.dim_date d
    ON f.date_key = d.date_key
WHERE f.is_cancelled = FALSE
GROUP BY
    d.year,
    d.month
ORDER BY
    d.year,
    d.month;