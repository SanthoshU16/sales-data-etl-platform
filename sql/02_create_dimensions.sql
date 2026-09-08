CREATE TABLE IF NOT EXISTS warehouse.dim_customer(
    customer_key SERIAL PRIMARY KEY,
    customer_id INTEGER UNIQUE
);

CREATE TABLE IF NOT EXISTS warehouse.dim_product(
    product_key SERIAL PRIMARY KEY,
    stock_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS warehouse.dim_country(
    country_key SERIAL PRIMARY KEY,
    country_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse.dim_date(
    date_key INTEGER PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    day INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter INTEGER NOT NULL ,
    year INTEGER NOT NULL,
    week INTEGER NOT NULL
);