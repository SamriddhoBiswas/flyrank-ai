CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    ordered_at DATE NOT NULL DEFAULT CURRENT_DATE
);

INSERT INTO products (name, category, unit_price)
SELECT * FROM (VALUES
    ('Notebook', 'Stationery', 4.50),
    ('Pen set', 'Stationery', 6.00),
    ('USB drive', 'Electronics', 12.99),
    ('Headphones', 'Electronics', 39.99),
    ('Coffee mug', 'Home', 9.50),
    ('Desk lamp', 'Home', 24.00)
) AS v(name, category, unit_price)
WHERE NOT EXISTS (SELECT 1 FROM products);

INSERT INTO orders (product_id, quantity, ordered_at)
SELECT * FROM (VALUES
    (1, 3, CURRENT_DATE - 2),
    (1, 1, CURRENT_DATE - 1),
    (2, 5, CURRENT_DATE - 3),
    (3, 2, CURRENT_DATE - 1),
    (3, 4, CURRENT_DATE),
    (4, 1, CURRENT_DATE - 4),
    (4, 2, CURRENT_DATE - 1),
    (5, 6, CURRENT_DATE - 2),
    (6, 1, CURRENT_DATE),
    (2, 2, CURRENT_DATE),
    (5, 3, CURRENT_DATE - 5),
    (1, 4, CURRENT_DATE)
) AS v(product_id, quantity, ordered_at)
WHERE NOT EXISTS (SELECT 1 FROM orders);
