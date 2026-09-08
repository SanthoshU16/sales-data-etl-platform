SELECT
    d.full_date,
    ROUND(SUM(f.sales_amount), 2) AS daily_sales
FROM warehouse.fact_sales f
JOIN warehouse.dim_date d
    ON f.date_key = d.date_key
WHERE f.is_cancelled = FALSE
GROUP BY
    d.full_date
ORDER BY
    d.full_date;