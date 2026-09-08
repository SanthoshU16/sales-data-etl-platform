CREATE TABLE IF NOT EXISTS warehouse.fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,

    invoice_no VARCHAR(20) NOT NULL,

    product_key INTEGER NOT NULL,
    customer_key INTEGER,
    date_key INTEGER NOT NULL,
    country_key INTEGER NOT NULL,

    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    sales_amount NUMERIC(14, 2) NOT NULL,

    is_cancelled BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_product
        FOREIGN KEY (product_key)
        REFERENCES warehouse.dim_product(product_key),

    CONSTRAINT fk_customer
        FOREIGN KEY (customer_key)
        REFERENCES warehouse.dim_customer(customer_key),

    CONSTRAINT fk_date
        FOREIGN KEY (date_key)
        REFERENCES warehouse.dim_date(date_key),

    CONSTRAINT fk_country
        FOREIGN KEY (country_key)
        REFERENCES warehouse.dim_country(country_key)
);