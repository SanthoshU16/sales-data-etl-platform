SELECT
    p.stock_code,
    p.description,
    ROUND(SUM(f.sales_amount), 2) AS total_sales
FROM warehouse.fact_sales f
JOIN warehouse.dim_product p
    ON f.product_key = p.product_key
WHERE f.is_cancelled = FALSE
GROUP BY
    p.stock_code,
    p.description
ORDER BY
    total_sales DESC
LIMIT 10;