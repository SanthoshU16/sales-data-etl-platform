SELECT
    c.country_name,
    ROUND(SUM(f.sales_amount), 2) AS total_sales
FROM warehouse.fact_sales f
JOIN warehouse.dim_country c
    ON f.country_key = c.country_key
WHERE f.is_cancelled = FALSE
GROUP BY
    c.country_name
ORDER BY
    total_sales DESC
LIMIT 10;