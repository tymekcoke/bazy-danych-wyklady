# 🔍 SUBQUERIES - PODZAPYTANIA SQL - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Subqueries (podzapytania) to zapytania zagnieżdżone wewnątrz innych zapytań SQL. Rodzaje:

1. **Nieskorelowane** - wykonywane raz, niezależnie od zapytania głównego
2. **Skorelowane** - wykonywane dla każdego wiersza zapytania głównego
3. **Skalarne** - zwracają jedną wartość
4. **Tabelowe** - zwracają wiele wierszy/kolumn

Zastosowania: WHERE (EXISTS, IN), FROM (derived tables), SELECT (skalarne), HAVING. Alternatywy to JOIN'y - często szybsze. Subqueries są potężne ale mogą być kosztowne dla dużych zbiorów danych."

## ✍️ CO NAPISAĆ NA KARTCE

```sql
SUBQUERIES - TYPY I ZASTOSOWANIA:

KLASYFIKACJA:
1. SKALARNE - zwracają jedną wartość
   SELECT * FROM products WHERE price > (SELECT AVG(price) FROM products);

2. WIELOWIERSZOWE - zwracają wiele wartości
   SELECT * FROM employees WHERE dept_id IN (SELECT id FROM departments WHERE budget > 100000);

3. SKORELOWANE - referencyjne do outer query
   SELECT * FROM e1 WHERE salary > (SELECT AVG(salary) FROM employees e2 WHERE e2.dept = e1.dept);

4. NIESKORELOWANE - niezależne od outer query
   SELECT * FROM products WHERE category_id = (SELECT id FROM categories WHERE name = 'Electronics');

OPERATORY Z SUBQUERIES:
• IN/NOT IN - przynależność do zbioru
• EXISTS/NOT EXISTS - sprawdzenie istnienia
• ANY/SOME - porównanie z którymkolwiek
• ALL - porównanie ze wszystkimi
• =, >, <, >= - z subquery skalarnym

POZYCJE SUBQUERIES:
• WHERE clause - filtrowanie
• FROM clause - derived tables
• SELECT clause - skalarne wartości
• HAVING clause - filtrowanie grup

EXAMPLES:
-- EXISTS
WHERE EXISTS (SELECT 1 FROM orders WHERE customer_id = customers.id)

-- IN vs EXISTS
WHERE customer_id IN (SELECT id FROM customers WHERE city = 'Warsaw')
WHERE EXISTS (SELECT 1 FROM customers c WHERE c.id = orders.customer_id AND c.city = 'Warsaw')

-- ANY/ALL
WHERE price > ANY (SELECT price FROM products WHERE category = 'books')
WHERE price > ALL (SELECT price FROM products WHERE category = 'books')

PERFORMANCE TIPS:
• EXISTS often faster than IN for large datasets
• Correlated subqueries can be slow - consider JOINs
• Use LIMIT in subqueries when possible
• Index columns used in subquery conditions
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- KOMPLEKSOWA DEMONSTRACJA SUBQUERIES

-- Przygotowanie tabel testowych
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    city VARCHAR(50),
    country VARCHAR(50),
    registration_date DATE
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    order_date DATE,
    total_amount DECIMAL(10,2),
    status VARCHAR(20)
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    product_id INT,
    quantity INT,
    unit_price DECIMAL(8,2)
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(8,2),
    supplier_id INT
);

-- Dane testowe
INSERT INTO customers VALUES
(1, 'Jan Kowalski', 'Warsaw', 'Poland', '2023-01-15'),
(2, 'Anna Nowak', 'Krakow', 'Poland', '2023-02-20'),
(3, 'John Smith', 'London', 'UK', '2023-03-10'),
(4, 'Marie Dubois', 'Paris', 'France', '2023-04-05'),
(5, 'Hans Mueller', 'Berlin', 'Germany', '2023-05-12');

INSERT INTO products VALUES
(1, 'Laptop Dell', 'Electronics', 2500.00, 1),
(2, 'Mouse Logitech', 'Electronics', 50.00, 1),
(3, 'Book SQL Guide', 'Books', 45.00, 2),
(4, 'Coffee Mug', 'Home', 15.00, 3),
(5, 'Monitor Samsung', 'Electronics', 350.00, 1);

INSERT INTO orders VALUES
(1, 1, '2024-01-10', 2550.00, 'completed'),
(2, 1, '2024-01-15', 45.00, 'completed'),
(3, 2, '2024-01-12', 350.00, 'pending'),
(4, 3, '2024-01-14', 65.00, 'completed'),
(5, 4, '2024-01-16', 2500.00, 'completed'),
(6, 2, '2024-01-18', 15.00, 'cancelled');

INSERT INTO order_items VALUES
(1, 1, 1, 1, 2500.00),
(2, 1, 2, 1, 50.00),
(3, 2, 3, 1, 45.00),
(4, 3, 5, 1, 350.00),
(5, 4, 3, 1, 45.00),
(6, 4, 4, 1, 20.00),
(7, 5, 1, 1, 2500.00),
(8, 6, 4, 1, 15.00);

-- 1. SUBQUERIES SKALARNE

-- Customers with above-average order values
SELECT 
    c.name,
    c.city,
    (SELECT AVG(total_amount) FROM orders) as avg_order_value,
    (SELECT SUM(total_amount) FROM orders o WHERE o.customer_id = c.id) as customer_total
FROM customers c
WHERE (SELECT SUM(total_amount) FROM orders o WHERE o.customer_id = c.id) > 
      (SELECT AVG(total_amount) FROM orders);

-- Products priced above category average
SELECT 
    p.name,
    p.category,
    p.price,
    (SELECT AVG(price) FROM products p2 WHERE p2.category = p.category) as category_avg_price
FROM products p
WHERE p.price > (
    SELECT AVG(price) 
    FROM products p2 
    WHERE p2.category = p.category
);

-- Latest order amount for each customer
SELECT 
    c.name,
    c.city,
    (SELECT total_amount 
     FROM orders o 
     WHERE o.customer_id = c.id 
     ORDER BY order_date DESC 
     LIMIT 1) as latest_order_amount,
    (SELECT order_date 
     FROM orders o 
     WHERE o.customer_id = c.id 
     ORDER BY order_date DESC 
     LIMIT 1) as latest_order_date
FROM customers c;

-- 2. SUBQUERIES W KLAUZULI WHERE

-- IN operator - customers who made orders
SELECT name, city
FROM customers
WHERE id IN (
    SELECT DISTINCT customer_id 
    FROM orders 
    WHERE status = 'completed'
);

-- NOT IN - customers without completed orders
SELECT name, city
FROM customers
WHERE id NOT IN (
    SELECT customer_id 
    FROM orders 
    WHERE status = 'completed' 
    AND customer_id IS NOT NULL  -- Important: handle NULLs
);

-- EXISTS - customers with orders (more efficient than IN for large datasets)
SELECT c.name, c.city
FROM customers c
WHERE EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.id 
    AND o.status = 'completed'
);

-- NOT EXISTS - customers without any orders
SELECT c.name, c.city
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.id
);

-- 3. OPERATORY ANY, SOME, ALL

-- Products more expensive than ANY electronics item
SELECT name, category, price
FROM products
WHERE price > ANY (
    SELECT price 
    FROM products 
    WHERE category = 'Electronics'
)
AND category != 'Electronics';

-- Products more expensive than ALL books
SELECT name, category, price
FROM products
WHERE price > ALL (
    SELECT price 
    FROM products 
    WHERE category = 'Books'
);

-- Orders with amount equal to ANY other customer's maximum
SELECT o.id, o.customer_id, o.total_amount
FROM orders o
WHERE o.total_amount = ANY (
    SELECT MAX(total_amount)
    FROM orders o2
    WHERE o2.customer_id != o.customer_id
    GROUP BY o2.customer_id
);

-- 4. SKORELOWANE SUBQUERIES

-- Customers whose last order was above their average
SELECT c.name, c.city
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM orders o1
    WHERE o1.customer_id = c.id
    AND o1.order_date = (
        SELECT MAX(order_date)
        FROM orders o2
        WHERE o2.customer_id = c.id
    )
    AND o1.total_amount > (
        SELECT AVG(total_amount)
        FROM orders o3
        WHERE o3.customer_id = c.id
    )
);

-- Products that are the most expensive in their category
SELECT p1.name, p1.category, p1.price
FROM products p1
WHERE p1.price = (
    SELECT MAX(price)
    FROM products p2
    WHERE p2.category = p1.category
);

-- Customers with orders above their historical average
SELECT DISTINCT c.name, o.total_amount
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE o.total_amount > (
    SELECT AVG(total_amount)
    FROM orders o2
    WHERE o2.customer_id = c.id
    AND o2.order_date < o.order_date
);

-- 5. SUBQUERIES W KLAUZULI FROM (DERIVED TABLES)

-- Customer statistics with rankings
SELECT 
    customer_stats.*,
    CASE 
        WHEN total_spent > avg_customer_spent THEN 'High Value'
        WHEN total_spent > avg_customer_spent * 0.5 THEN 'Medium Value'
        ELSE 'Low Value'
    END as customer_segment
FROM (
    SELECT 
        c.id,
        c.name,
        c.city,
        COUNT(o.id) as order_count,
        COALESCE(SUM(o.total_amount), 0) as total_spent,
        AVG(o.total_amount) as avg_order_value
    FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id AND o.status = 'completed'
    GROUP BY c.id, c.name, c.city
) customer_stats
CROSS JOIN (
    SELECT AVG(customer_total) as avg_customer_spent
    FROM (
        SELECT customer_id, SUM(total_amount) as customer_total
        FROM orders
        WHERE status = 'completed'
        GROUP BY customer_id
    ) totals
) averages;

-- Monthly sales analysis
SELECT 
    monthly.order_month,
    monthly.monthly_total,
    monthly.order_count,
    monthly.avg_order_value,
    overall.total_revenue,
    (monthly.monthly_total / overall.total_revenue * 100) as percent_of_total
FROM (
    SELECT 
        DATE_TRUNC('month', order_date) as order_month,
        SUM(total_amount) as monthly_total,
        COUNT(*) as order_count,
        AVG(total_amount) as avg_order_value
    FROM orders
    WHERE status = 'completed'
    GROUP BY DATE_TRUNC('month', order_date)
) monthly
CROSS JOIN (
    SELECT SUM(total_amount) as total_revenue
    FROM orders
    WHERE status = 'completed'
) overall
ORDER BY monthly.order_month;

-- 6. SUBQUERIES W KLAUZULI SELECT

-- Customer details with aggregated order information
SELECT 
    c.name,
    c.city,
    c.registration_date,
    (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id) as total_orders,
    (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id AND o.status = 'completed') as completed_orders,
    (SELECT SUM(total_amount) FROM orders o WHERE o.customer_id = c.id AND o.status = 'completed') as total_revenue,
    (SELECT MAX(order_date) FROM orders o WHERE o.customer_id = c.id) as last_order_date,
    (SELECT AVG(total_amount) FROM orders) as global_avg_order
FROM customers c;

-- Product analysis with category comparisons
SELECT 
    p.name,
    p.category,
    p.price,
    (SELECT COUNT(*) FROM products p2 WHERE p2.category = p.category) as products_in_category,
    (SELECT AVG(price) FROM products p2 WHERE p2.category = p.category) as category_avg_price,
    (SELECT MIN(price) FROM products p2 WHERE p2.category = p.category) as category_min_price,
    (SELECT MAX(price) FROM products p2 WHERE p2.category = p.category) as category_max_price,
    p.price - (SELECT AVG(price) FROM products p2 WHERE p2.category = p.category) as price_vs_category_avg
FROM products p;

-- 7. SUBQUERIES W KLAUZULI HAVING

-- Categories with above-average product counts
SELECT 
    category,
    COUNT(*) as product_count,
    AVG(price) as avg_price
FROM products
GROUP BY category
HAVING COUNT(*) > (
    SELECT AVG(category_count)
    FROM (
        SELECT COUNT(*) as category_count
        FROM products
        GROUP BY category
    ) category_stats
);

-- Customers with total spending above global average
SELECT 
    c.name,
    SUM(o.total_amount) as total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE o.status = 'completed'
GROUP BY c.id, c.name
HAVING SUM(o.total_amount) > (
    SELECT AVG(customer_total)
    FROM (
        SELECT SUM(total_amount) as customer_total
        FROM orders
        WHERE status = 'completed'
        GROUP BY customer_id
    ) customer_totals
);

-- 8. ZAAWANSOWANE WZORCE Z SUBQUERIES

-- Top 3 customers by spending in each country
SELECT *
FROM (
    SELECT 
        c.name,
        c.city,
        c.country,
        SUM(o.total_amount) as total_spent,
        ROW_NUMBER() OVER (PARTITION BY c.country ORDER BY SUM(o.total_amount) DESC) as country_rank
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    WHERE o.status = 'completed'
    GROUP BY c.id, c.name, c.city, c.country
) ranked_customers
WHERE country_rank <= 3;

-- Customers who bought the same product as customer with ID 1
SELECT DISTINCT c.name, c.city
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM orders o1
    JOIN order_items oi1 ON o1.id = oi1.order_id
    WHERE o1.customer_id = c.id
    AND oi1.product_id IN (
        SELECT oi2.product_id
        FROM orders o2
        JOIN order_items oi2 ON o2.id = oi2.order_id
        WHERE o2.customer_id = 1
    )
)
AND c.id != 1;

-- 9. OPTIMIZATION PATTERNS

-- Replace IN with EXISTS for better performance
-- SLOW (with large datasets):
SELECT c.name
FROM customers c
WHERE c.id IN (
    SELECT customer_id 
    FROM orders 
    WHERE total_amount > 1000
);

-- FASTER:
SELECT c.name
FROM customers c
WHERE EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.id 
    AND o.total_amount > 1000
);

-- Replace correlated subquery with window function
-- SLOW:
SELECT 
    c.name,
    (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id) as order_count
FROM customers c;

-- FASTER:
SELECT DISTINCT 
    c.name,
    COUNT(o.id) OVER (PARTITION BY c.id) as order_count
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id;

-- 10. COMPLEX NESTED SUBQUERIES

-- Customers who have ordered all products that customer 1 has ordered
SELECT c.name
FROM customers c
WHERE c.id != 1
AND NOT EXISTS (
    -- Products ordered by customer 1
    SELECT oi1.product_id
    FROM orders o1
    JOIN order_items oi1 ON o1.id = oi1.order_id
    WHERE o1.customer_id = 1
    
    EXCEPT
    
    -- Products ordered by current customer
    SELECT oi2.product_id
    FROM orders o2
    JOIN order_items oi2 ON o2.id = oi2.order_id
    WHERE o2.customer_id = c.id
);

-- Products that have never been ordered together with electronics
SELECT p.name, p.category
FROM products p
WHERE p.category != 'Electronics'
AND NOT EXISTS (
    SELECT 1
    FROM order_items oi1
    JOIN order_items oi2 ON oi1.order_id = oi2.order_id
    JOIN products p_electronics ON oi2.product_id = p_electronics.id
    WHERE oi1.product_id = p.id
    AND p_electronics.category = 'Electronics'
    AND oi1.id != oi2.id
);

-- 11. TROUBLESHOOTING COMMON ISSUES

-- Handle NULL values in NOT IN
-- WRONG (will return unexpected results if any customer_id is NULL):
SELECT name FROM customers 
WHERE id NOT IN (SELECT customer_id FROM orders);

-- CORRECT:
SELECT name FROM customers 
WHERE id NOT IN (SELECT customer_id FROM orders WHERE customer_id IS NOT NULL);

-- Or better, use NOT EXISTS:
SELECT name FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

-- 12. PERFORMANCE ANALYSIS

-- Check execution plans
EXPLAIN ANALYZE
SELECT c.name
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o 
    WHERE o.customer_id = c.id 
    AND o.total_amount > 1000
);

-- Compare with JOIN approach
EXPLAIN ANALYZE
SELECT DISTINCT c.name
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE o.total_amount > 1000;
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: NOT IN z NULL zwraca niespodziewane wyniki - używaj NOT EXISTS
2. **UWAGA**: Skorelowane subqueries mogą być bardzo wolne dla dużych tabel
3. **BŁĄD**: Subquery skalarne musi zwrócić dokładnie jedną wartość
4. **WAŻNE**: EXISTS jest często szybsze niż IN dla dużych zbiorów
5. **PUŁAPKA**: Subqueries w SELECT wykonują się dla każdego wiersza

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Correlated/Uncorrelated subqueries** - skorelowane/nieskorelowane
- **Scalar subqueries** - podzapytania skalarne
- **EXISTS/NOT EXISTS** - sprawdzanie istnienia
- **IN/NOT IN** - przynależność do zbioru
- **ANY/ALL operators** - operatory kwantyfikacji
- **Derived tables** - tabele pochodne
- **Nested queries** - zapytania zagnieżdżone
- **Query optimization** - optymalizacja zapytań

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **21-sql-joiny** - alternatywa dla subqueries
- **30-sql-dml-zaawansowany** - CTE vs subqueries
- **32-funkcje-agregujace** - agregacje w subqueries
- **42-optymalizacja-wydajnosci** - wydajność subqueries
- **24-wartosc-null** - NULL handling w subqueries