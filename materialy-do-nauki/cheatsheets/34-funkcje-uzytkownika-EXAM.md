# ⚙️ FUNKCJE UŻYTKOWNIKA - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekunds)

"Funkcje użytkownika w PostgreSQL to wielorazowego użytku bloki kodu implementujące logikę biznesową. Typy funkcji:

1. **Skalarne** - zwracają pojedynczą wartość
2. **Tabelowe** - zwracają zbiór wierszy (TABLE, SETOF)
3. **Agregujące** - operują na zbiorach danych
4. **Window functions** - funkcje okienkowe
5. **Trigger functions** - wywoływane przez triggery

Funkcje mogą być pisane w różnych językach (SQL, PL/pgSQL, Python, C). Oferują hermetyzację logiki, wydajność przez cache'owanie planów wykonania i możliwość optymalizacji przez kompilator SQL."

## ✍️ CO NAPISAĆ NA KARTCE

```sql
FUNKCJE UŻYTKOWNIKA - TYPY I SKŁADNIA:

FUNKCJA SKALARNA:
CREATE OR REPLACE FUNCTION nazwa(param typ)
RETURNS typ AS $$
    SELECT wyrażenie FROM tabela WHERE warunek;
$$ LANGUAGE sql;

FUNKCJA TABELOWA:
CREATE OR REPLACE FUNCTION nazwa(param typ)
RETURNS TABLE(col1 typ, col2 typ) AS $$
    SELECT col1, col2 FROM tabela WHERE warunek;
$$ LANGUAGE sql;

FUNKCJA SETOF:
CREATE OR REPLACE FUNCTION nazwa()
RETURNS SETOF tabela AS $$
    SELECT * FROM tabela;
$$ LANGUAGE sql;

FUNKCJA PL/pgSQL:
CREATE OR REPLACE FUNCTION nazwa(param typ)
RETURNS typ AS $$
DECLARE
    zmienna typ;
BEGIN
    -- logika
    RETURN wynik;
END;
$$ LANGUAGE plpgsql;

FUNKCJA AGREGUJĄCA:
CREATE AGGREGATE nazwa(typ_danych) (
    SFUNC = state_function,
    STYPE = state_type,
    INITCOND = 'initial_value'
);

FUNCTION PROPERTIES:
• IMMUTABLE - zawsze ten sam wynik dla tych samych argumentów
• STABLE - wynik może się zmieniać w ramach transakcji  
• VOLATILE - wynik może się zmieniać w ramach statement (domyślne)
• STRICT - zwraca NULL gdy którykolwiek argument to NULL
• SECURITY DEFINER - uruchamiana z prawami właściciela

EXAMPLE DECLARATIONS:
CREATE FUNCTION func(int) RETURNS int
IMMUTABLE STRICT PARALLEL SAFE
AS $$ SELECT $1 * 2; $$ LANGUAGE sql;

OVERLOADING:
-- Można mieć funkcje o tej samej nazwie ale różnych parametrach
CREATE FUNCTION add_numbers(a int, b int) RETURNS int;
CREATE FUNCTION add_numbers(a decimal, b decimal) RETURNS decimal;

DEFAULT PARAMETERS:
CREATE FUNCTION greet(name text, greeting text DEFAULT 'Hello')
RETURNS text AS $$
    SELECT greeting || ', ' || name || '!';
$$ LANGUAGE sql;
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- KOMPLEKSOWA DEMONSTRACJA FUNKCJI UŻYTKOWNIKA

-- Przygotowanie tabel testowych
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10,2),
    cost DECIMAL(10,2),
    stock_quantity INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE sales_orders (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2),
    order_date DATE DEFAULT CURRENT_DATE,
    customer_name VARCHAR(100),
    discount_percent DECIMAL(5,2) DEFAULT 0
);

CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2),
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(200)
);

-- Dane testowe
INSERT INTO products (name, category, price, cost, stock_quantity) VALUES
('Laptop Dell XPS', 'Electronics', 4500.00, 3000.00, 15),
('Mouse Logitech', 'Electronics', 80.00, 45.00, 100),
('Office Chair', 'Furniture', 350.00, 200.00, 25),
('Coffee Mug', 'Kitchen', 25.00, 10.00, 200),
('Smartphone Samsung', 'Electronics', 2800.00, 1800.00, 30);

INSERT INTO sales_orders (product_id, quantity, unit_price, customer_name, discount_percent) VALUES
(1, 2, 4500.00, 'Jan Kowalski', 5.0),
(2, 5, 80.00, 'Anna Nowak', 0.0),
(3, 1, 350.00, 'Piotr Wiśniewski', 10.0),
(1, 1, 4500.00, 'Maria Kowalczyk', 0.0),
(5, 3, 2800.00, 'Tomasz Zieliński', 7.5);

-- 1. FUNKCJE SKALARNE

-- Prosta funkcja SQL skalarna
CREATE OR REPLACE FUNCTION calculate_profit_margin(
    selling_price DECIMAL,
    cost_price DECIMAL
) RETURNS DECIMAL AS $$
    SELECT ROUND(((selling_price - cost_price) / selling_price * 100), 2);
$$ LANGUAGE sql IMMUTABLE STRICT;

-- Funkcja z walidacją w PL/pgSQL
CREATE OR REPLACE FUNCTION calculate_discount_price(
    original_price DECIMAL,
    discount_percent DECIMAL
) RETURNS DECIMAL AS $$
BEGIN
    -- Walidacja parametrów
    IF original_price <= 0 THEN
        RAISE EXCEPTION 'Original price must be positive, got: %', original_price;
    END IF;
    
    IF discount_percent < 0 OR discount_percent > 100 THEN
        RAISE EXCEPTION 'Discount percent must be between 0 and 100, got: %', discount_percent;
    END IF;
    
    -- Obliczenie ceny po rabacie
    RETURN ROUND(original_price * (100 - discount_percent) / 100, 2);
END;
$$ LANGUAGE plpgsql IMMUTABLE STRICT;

-- Funkcja z parametrami domyślnymi
CREATE OR REPLACE FUNCTION format_currency(
    amount DECIMAL,
    currency_symbol TEXT DEFAULT 'PLN',
    decimal_places INT DEFAULT 2
) RETURNS TEXT AS $$
    SELECT TO_CHAR(amount, 'FM999,999.' || REPEAT('0', decimal_places)) || ' ' || currency_symbol;
$$ LANGUAGE sql IMMUTABLE;

-- Test funkcji skalarnych
SELECT 
    name,
    price,
    cost,
    calculate_profit_margin(price, cost) as profit_margin_percent,
    calculate_discount_price(price, 15) as price_with_15_discount,
    format_currency(price) as formatted_price
FROM products;

-- 2. FUNKCJE TABELOWE

-- Funkcja zwracająca tabelę - SQL
CREATE OR REPLACE FUNCTION get_products_by_category(category_name TEXT)
RETURNS TABLE(
    product_id INT,
    product_name VARCHAR(100),
    price DECIMAL(10,2),
    stock INT,
    profit_margin DECIMAL(5,2)
) AS $$
    SELECT 
        p.id,
        p.name,
        p.price,
        p.stock_quantity,
        calculate_profit_margin(p.price, p.cost)
    FROM products p
    WHERE p.category = category_name
    AND p.is_active = TRUE
    ORDER BY p.price DESC;
$$ LANGUAGE sql STABLE;

-- Funkcja tabelowa z kompleksową logiką PL/pgSQL
CREATE OR REPLACE FUNCTION analyze_product_performance(
    analysis_period_days INT DEFAULT 30
) RETURNS TABLE(
    product_id INT,
    product_name VARCHAR(100),
    category VARCHAR(50),
    total_sold INT,
    revenue DECIMAL(12,2),
    avg_sale_price DECIMAL(10,2),
    performance_rating VARCHAR(20)
) AS $$
DECLARE
    cutoff_date DATE;
BEGIN
    cutoff_date := CURRENT_DATE - analysis_period_days;
    
    RETURN QUERY
    SELECT 
        p.id,
        p.name,
        p.category,
        COALESCE(SUM(so.quantity), 0)::INT as total_sold,
        COALESCE(SUM(so.quantity * so.unit_price * (100 - so.discount_percent) / 100), 0) as revenue,
        COALESCE(AVG(so.unit_price), p.price) as avg_sale_price,
        CASE 
            WHEN COALESCE(SUM(so.quantity), 0) = 0 THEN 'No Sales'
            WHEN COALESCE(SUM(so.quantity), 0) >= 10 THEN 'Excellent'
            WHEN COALESCE(SUM(so.quantity), 0) >= 5 THEN 'Good'
            WHEN COALESCE(SUM(so.quantity), 0) >= 1 THEN 'Fair'
            ELSE 'Poor'
        END::VARCHAR(20)
    FROM products p
    LEFT JOIN sales_orders so ON p.id = so.product_id AND so.order_date >= cutoff_date
    WHERE p.is_active = TRUE
    GROUP BY p.id, p.name, p.category, p.price
    ORDER BY revenue DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- Test funkcji tabelowych
SELECT * FROM get_products_by_category('Electronics');
SELECT * FROM analyze_product_performance(30);

-- 3. FUNKCJE SETOF

-- Funkcja zwracająca SETOF record
CREATE OR REPLACE FUNCTION get_low_stock_products(threshold INT DEFAULT 20)
RETURNS SETOF products AS $$
    SELECT * FROM products 
    WHERE stock_quantity <= threshold 
    AND is_active = TRUE
    ORDER BY stock_quantity ASC;
$$ LANGUAGE sql STABLE;

-- Funkcja SETOF z dynamicznym SQL
CREATE OR REPLACE FUNCTION search_products_dynamic(
    search_term TEXT,
    search_field TEXT DEFAULT 'name'
) RETURNS SETOF products AS $$
DECLARE
    query_sql TEXT;
    allowed_fields TEXT[] := ARRAY['name', 'category'];
BEGIN
    -- Walidacja pola wyszukiwania
    IF NOT (search_field = ANY(allowed_fields)) THEN
        RAISE EXCEPTION 'Invalid search field: %. Allowed: %', search_field, allowed_fields;
    END IF;
    
    -- Budowanie zapytania
    query_sql := 'SELECT * FROM products WHERE ' || 
                quote_ident(search_field) || ' ILIKE $1 AND is_active = TRUE ' ||
                'ORDER BY name';
    
    -- Wykonanie i zwrócenie wyników
    RETURN QUERY EXECUTE query_sql USING '%' || search_term || '%';
END;
$$ LANGUAGE plpgsql STABLE;

-- Test funkcji SETOF
SELECT * FROM get_low_stock_products(50);
SELECT * FROM search_products_dynamic('Dell', 'name');

-- 4. FUNKCJE AGREGUJĄCE WŁASNE

-- Funkcja stanu dla agregacji
CREATE OR REPLACE FUNCTION weighted_avg_state(
    state DECIMAL[],
    value DECIMAL,
    weight DECIMAL
) RETURNS DECIMAL[] AS $$
BEGIN
    -- state[1] = suma ważona wartości
    -- state[2] = suma wag
    IF state IS NULL THEN
        RETURN ARRAY[value * weight, weight];
    ELSE
        RETURN ARRAY[state[1] + value * weight, state[2] + weight];
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Funkcja finalizująca dla agregacji
CREATE OR REPLACE FUNCTION weighted_avg_final(state DECIMAL[])
RETURNS DECIMAL AS $$
BEGIN
    IF state IS NULL OR state[2] = 0 THEN
        RETURN NULL;
    ELSE
        RETURN ROUND(state[1] / state[2], 4);
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Utworzenie funkcji agregującej
CREATE AGGREGATE weighted_avg(DECIMAL, DECIMAL) (
    SFUNC = weighted_avg_state,
    STYPE = DECIMAL[],
    FINALFUNC = weighted_avg_final,
    INITCOND = '{0,0}'
);

-- Test funkcji agregującej
SELECT 
    category,
    AVG(price) as simple_average,
    weighted_avg(price, stock_quantity) as stock_weighted_average
FROM products
GROUP BY category;

-- 5. FUNKCJE WINDOW

-- Custom window function
CREATE OR REPLACE FUNCTION running_total_with_reset(
    current_value DECIMAL,
    reset_condition BOOLEAN
) RETURNS DECIMAL AS $$
DECLARE
    total DECIMAL := 0;
BEGIN
    IF reset_condition THEN
        total := current_value;
    ELSE
        total := COALESCE(LAG(total) OVER (), 0) + current_value;
    END IF;
    
    RETURN total;
END;
$$ LANGUAGE plpgsql WINDOW;

-- 6. FUNKCJE Z RÓŻNYMI WŁAŚCIWOŚCIAMI

-- Funkcja IMMUTABLE (deterministic, cacheable)
CREATE OR REPLACE FUNCTION tax_calculation(
    amount DECIMAL,
    tax_rate DECIMAL DEFAULT 0.23
) RETURNS DECIMAL AS $$
    SELECT ROUND(amount * tax_rate, 2);
$$ LANGUAGE sql IMMUTABLE STRICT;

-- Funkcja STABLE (może używać current_date, current_user, etc.)
CREATE OR REPLACE FUNCTION get_daily_sales_summary(target_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE(
    total_orders INT,
    total_revenue DECIMAL(12,2),
    avg_order_value DECIMAL(10,2),
    top_product VARCHAR(100)
) AS $$
    WITH daily_stats AS (
        SELECT 
            COUNT(*) as order_count,
            SUM(quantity * unit_price * (100 - discount_percent) / 100) as revenue,
            AVG(quantity * unit_price * (100 - discount_percent) / 100) as avg_value
        FROM sales_orders
        WHERE order_date = target_date
    ),
    top_product_today AS (
        SELECT p.name
        FROM sales_orders so
        JOIN products p ON so.product_id = p.id
        WHERE so.order_date = target_date
        GROUP BY p.id, p.name
        ORDER BY SUM(so.quantity) DESC
        LIMIT 1
    )
    SELECT 
        ds.order_count::INT,
        COALESCE(ds.revenue, 0),
        COALESCE(ds.avg_value, 0),
        COALESCE(tp.name, 'No sales')::VARCHAR(100)
    FROM daily_stats ds
    CROSS JOIN top_product_today tp;
$$ LANGUAGE sql STABLE;

-- Funkcja VOLATILE (może mieć side effects)
CREATE OR REPLACE FUNCTION update_product_price(
    product_id_param INT,
    new_price DECIMAL,
    change_reason TEXT DEFAULT 'Manual update'
) RETURNS BOOLEAN AS $$
DECLARE
    old_price_val DECIMAL;
    rows_affected INT;
BEGIN
    -- Pobranie starej ceny
    SELECT price INTO old_price_val 
    FROM products 
    WHERE id = product_id_param;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Product with ID % not found', product_id_param;
    END IF;
    
    -- Aktualizacja ceny
    UPDATE products 
    SET price = new_price 
    WHERE id = product_id_param;
    
    GET DIAGNOSTICS rows_affected = ROW_COUNT;
    
    -- Zapis historii zmian
    INSERT INTO price_history (product_id, old_price, new_price, reason)
    VALUES (product_id_param, old_price_val, new_price, change_reason);
    
    -- Log
    RAISE NOTICE 'Price updated for product %: % -> %', 
        product_id_param, old_price_val, new_price;
    
    RETURN rows_affected > 0;
END;
$$ LANGUAGE plpgsql VOLATILE;

-- 7. FUNKCJE Z SECURITY DEFINER

-- Funkcja z podwyższonymi uprawnieniami
CREATE OR REPLACE FUNCTION admin_get_sensitive_data()
RETURNS TABLE(
    product_id INT,
    cost DECIMAL(10,2),
    profit_per_unit DECIMAL(10,2),
    total_stock_value DECIMAL(12,2)
) 
SECURITY DEFINER  -- Uruchomione z prawami właściciela
SET search_path = public  -- Bezpieczeństwo
AS $$
    SELECT 
        id,
        cost,
        price - cost as profit_per_unit,
        (price - cost) * stock_quantity as total_stock_value
    FROM products
    WHERE is_active = TRUE
    ORDER BY total_stock_value DESC;
$$ LANGUAGE sql STABLE;

-- 8. FUNKCJE OVERLOADED

-- Przeciążone funkcje o tej samej nazwie
CREATE OR REPLACE FUNCTION calculate_total(price DECIMAL, quantity INT)
RETURNS DECIMAL AS $$
    SELECT price * quantity;
$$ LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION calculate_total(
    price DECIMAL, 
    quantity INT, 
    discount_percent DECIMAL
) RETURNS DECIMAL AS $$
    SELECT price * quantity * (100 - discount_percent) / 100;
$$ LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION calculate_total(
    price DECIMAL, 
    quantity INT, 
    discount_percent DECIMAL, 
    tax_rate DECIMAL
) RETURNS DECIMAL AS $$
    SELECT price * quantity * (100 - discount_percent) / 100 * (100 + tax_rate) / 100;
$$ LANGUAGE sql IMMUTABLE;

-- Test przeciążonych funkcji
SELECT 
    calculate_total(100.00, 5) as total_basic,
    calculate_total(100.00, 5, 10.0) as total_with_discount,
    calculate_total(100.00, 5, 10.0, 23.0) as total_with_discount_and_tax;

-- 9. FUNKCJE VARIADIC (zmienna liczba argumentów)

CREATE OR REPLACE FUNCTION sum_all(VARIADIC numbers DECIMAL[])
RETURNS DECIMAL AS $$
    SELECT SUM(num) FROM UNNEST(numbers) AS num;
$$ LANGUAGE sql IMMUTABLE;

-- Test funkcji variadic
SELECT sum_all(1.5, 2.3, 3.7, 4.1, 5.9);

-- 10. FUNKCJE Z OUT PARAMETERS

CREATE OR REPLACE FUNCTION get_product_stats(
    product_id_param INT,
    OUT product_name VARCHAR(100),
    OUT current_price DECIMAL(10,2),
    OUT total_sold INT,
    OUT revenue_generated DECIMAL(12,2),
    OUT stock_status VARCHAR(20)
) AS $$
BEGIN
    SELECT 
        p.name,
        p.price,
        COALESCE(SUM(so.quantity), 0),
        COALESCE(SUM(so.quantity * so.unit_price), 0),
        CASE 
            WHEN p.stock_quantity = 0 THEN 'Out of Stock'
            WHEN p.stock_quantity <= 10 THEN 'Low Stock'
            WHEN p.stock_quantity <= 50 THEN 'Normal Stock'
            ELSE 'High Stock'
        END
    INTO product_name, current_price, total_sold, revenue_generated, stock_status
    FROM products p
    LEFT JOIN sales_orders so ON p.id = so.product_id
    WHERE p.id = product_id_param
    GROUP BY p.id, p.name, p.price, p.stock_quantity;
    
    IF product_name IS NULL THEN
        RAISE EXCEPTION 'Product with ID % not found', product_id_param;
    END IF;
END;
$$ LANGUAGE plpgsql STABLE;

-- Test funkcji z OUT parameters
SELECT * FROM get_product_stats(1);

-- 11. PERFORMANCE TESTING I MONITORING

-- Funkcja do benchmarkingu
CREATE OR REPLACE FUNCTION benchmark_function_calls(
    iterations INT DEFAULT 1000
) RETURNS TABLE(
    test_name VARCHAR(50),
    execution_time_ms DECIMAL(10,3),
    calls_per_second DECIMAL(10,2)
) AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    duration_ms DECIMAL;
    i INT;
BEGIN
    -- Test 1: Simple calculation
    start_time := clock_timestamp();
    FOR i IN 1..iterations LOOP
        PERFORM calculate_profit_margin(100.0, 60.0);
    END LOOP;
    end_time := clock_timestamp();
    duration_ms := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
    
    test_name := 'Simple Calculation';
    execution_time_ms := duration_ms;
    calls_per_second := iterations / (duration_ms / 1000);
    RETURN NEXT;
    
    -- Test 2: Table function
    start_time := clock_timestamp();
    FOR i IN 1..iterations LOOP
        PERFORM * FROM get_products_by_category('Electronics') LIMIT 1;
    END LOOP;
    end_time := clock_timestamp();
    duration_ms := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
    
    test_name := 'Table Function';
    execution_time_ms := duration_ms;
    calls_per_second := iterations / (duration_ms / 1000);
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- Test wydajności
SELECT * FROM benchmark_function_calls(100);

-- 12. FUNCTION MAINTENANCE

-- Funkcja do analizy użycia funkcji
CREATE OR REPLACE FUNCTION analyze_function_usage()
RETURNS TABLE(
    function_name VARCHAR(100),
    language VARCHAR(20),
    volatility VARCHAR(10),
    parallel_safety VARCHAR(10),
    function_type VARCHAR(20)
) AS $$
    SELECT 
        p.proname::VARCHAR(100),
        l.lanname::VARCHAR(20),
        CASE p.provolatile
            WHEN 'i' THEN 'IMMUTABLE'
            WHEN 's' THEN 'STABLE'
            WHEN 'v' THEN 'VOLATILE'
        END::VARCHAR(10),
        CASE p.proparallel
            WHEN 's' THEN 'SAFE'
            WHEN 'r' THEN 'RESTRICTED'
            WHEN 'u' THEN 'UNSAFE'
        END::VARCHAR(10),
        CASE 
            WHEN p.prokind = 'f' THEN 'FUNCTION'
            WHEN p.prokind = 'a' THEN 'AGGREGATE'
            WHEN p.prokind = 'w' THEN 'WINDOW'
            WHEN p.prokind = 'p' THEN 'PROCEDURE'
        END::VARCHAR(20)
    FROM pg_proc p
    JOIN pg_language l ON p.prolang = l.oid
    WHERE p.pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
    AND p.proname NOT LIKE 'pg_%'
    ORDER BY p.proname;
$$ LANGUAGE sql STABLE;

-- Analiza funkcji w schemacie
SELECT * FROM analyze_function_usage();
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: IMMUTABLE funkcje nie mogą używać CURRENT_DATE, RANDOM() itp.
2. **UWAGA**: SECURITY DEFINER wykonuje funkcję z prawami właściciela, nie wywołującego
3. **BŁĄD**: Funkcje SQL nie mogą mieć side effects (INSERT, UPDATE, DELETE)
4. **WAŻNE**: STRICT oznacza zwrócenie NULL gdy jakikolwiek argument to NULL
5. **PUŁAPKA**: Overloading rozróżnia tylko typy argumentów, nie ich nazwy

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **User-defined functions** - funkcje użytkownika
- **Scalar/Table functions** - funkcje skalarne/tabelowe
- **Function overloading** - przeciążanie funkcji
- **IMMUTABLE/STABLE/VOLATILE** - właściwości funkcji
- **SECURITY DEFINER** - bezpieczeństwo funkcji
- **Aggregate functions** - funkcje agregujące
- **Window functions** - funkcje okienkowe
- **Function optimization** - optymalizacja funkcji

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **33-pl-pgsql-podstawy** - implementacja w PL/pgSQL
- **32-funkcje-agregujace** - własne funkcje agregujące
- **35-rules-vs-triggery** - funkcje trigger
- **39-bezpieczenstwo-baz-danych** - SECURITY DEFINER
- **42-optymalizacja-wydajnosci** - wydajność funkcji