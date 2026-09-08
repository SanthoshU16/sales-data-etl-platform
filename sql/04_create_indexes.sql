CREATE INDEX IF NOT EXISTS idx_fact_sales_invoice
ON warehouse.fact_sales(invoice_no);

CREATE INDEX IF NOT EXISTS idx_fact_sales_product
ON warehouse.fact_sales(product_key);

CREATE INDEX IF NOT EXISTS idx_fact_sales_customer
ON warehouse.fact_sales(customer_key);

CREATE INDEX IF NOT EXISTS idx_fact_sales_date
ON warehouse.fact_sales(date_key);

CREATE INDEX IF NOT EXISTS idx_fact_sales_country
ON warehouse.fact_sales(country_key);