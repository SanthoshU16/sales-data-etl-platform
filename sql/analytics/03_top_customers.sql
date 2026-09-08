SELECT
    c.customer_id,
    ROUND(SUM(f.sales_amount), 2) AS total_sales
FROM warehouse.fact_sales f
JOIN warehouse.dim_customer c
    ON f.customer_key = c.customer_key
WHERE f.is_cancelled = FALSE
GROUP BY
    c.customer_id
ORDER BY
    total_sales DESC
LIMIT 10;