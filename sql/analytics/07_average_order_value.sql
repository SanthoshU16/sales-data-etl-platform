SELECT
    COUNT(DISTINCT f.invoice_no) AS total_orders,

    ROUND(
        SUM(f.sales_amount),
        2
    ) AS total_sales,

    ROUND(
        SUM(f.sales_amount)
        / COUNT(DISTINCT f.invoice_no),
        2
    ) AS average_order_value

FROM warehouse.fact_sales f

WHERE f.is_cancelled = FALSE;