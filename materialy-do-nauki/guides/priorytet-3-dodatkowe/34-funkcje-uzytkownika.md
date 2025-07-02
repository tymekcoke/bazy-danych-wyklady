# Funkcje użytkownika

## Definicja funkcji użytkownika

**Funkcje użytkownika (User-Defined Functions - UDF)** to **niestandardowe funkcje** tworzone przez programistów w celu implementacji **logiki biznesowej**, **obliczeń** lub **operacji** specyficznych dla danej aplikacji.

### Kluczowe cechy:
- **Enkapsulacja logiki** - hermetyzacja złożonych operacji
- **Ponowne użycie** - funkcje można wywołać wielokrotnie
- **Modularność** - podział kodu na mniejsze, zarządzalne części
- **Wydajność** - wykonywanie po stronie serwera
- **Bezpieczeństwo** - kontrola dostępu do danych

### Typy funkcji:
- **Skalarne** - zwracają pojedynczą wartość
- **Tabelowe** - zwracają zbiór wierszy
- **Agregujące** - operują na grupach danych
- **Okienkowe** - działają w kontekście okien danych

## Funkcje skalarne

### 1. **Podstawowe funkcje skalarne**

```sql
-- Prosta funkcja obliczeniowa
CREATE OR REPLACE FUNCTION calculate_circle_area(radius NUMERIC)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE  -- Funkcja czysta - dla tych samych argumentów zawsze ten sam wynik
AS $$
BEGIN
    IF radius < 0 THEN
        RAISE EXCEPTION 'Promień nie może być ujemny';
    END IF;
    
    RETURN PI() * radius * radius;
END;
$$;

-- Użycie:
SELECT calculate_circle_area(5.0);  -- 78.5398...

-- Funkcja formatująca
CREATE OR REPLACE FUNCTION format_polish_phone(phone_number TEXT)
RETURNS TEXT
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    cleaned TEXT;
BEGIN
    -- Usuń wszystkie znaki niebędące cyframi
    cleaned := regexp_replace(phone_number, '[^0-9]', '', 'g');
    
    -- Sprawdź długość
    IF length(cleaned) != 9 THEN
        RETURN 'Nieprawidłowy numer';
    END IF;
    
    -- Formatuj: XXX-XXX-XXX
    RETURN substring(cleaned, 1, 3) || '-' || 
           substring(cleaned, 4, 3) || '-' || 
           substring(cleaned, 7, 3);
END;
$$;

-- Użycie:
SELECT format_polish_phone('123456789');    -- 123-456-789
SELECT format_polish_phone('+48123456789'); -- 123-456-789
```

### 2. **Funkcje biznesowe**

```sql
-- Obliczanie podatku VAT
CREATE OR REPLACE FUNCTION calculate_vat(
    net_amount NUMERIC,
    vat_rate NUMERIC DEFAULT 23
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    IF net_amount < 0 THEN
        RAISE EXCEPTION 'Kwota netto nie może być ujemna';
    END IF;
    
    IF vat_rate < 0 OR vat_rate > 100 THEN
        RAISE EXCEPTION 'Stawka VAT musi być między 0 a 100%%';
    END IF;
    
    RETURN ROUND(net_amount * vat_rate / 100, 2);
END;
$$;

-- Walidacja PESEL
CREATE OR REPLACE FUNCTION validate_pesel(pesel TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    weights INTEGER[] := ARRAY[1, 3, 7, 9, 1, 3, 7, 9, 1, 3];
    sum_val INTEGER := 0;
    check_digit INTEGER;
    i INTEGER;
BEGIN
    -- Sprawdź długość i czy zawiera tylko cyfry
    IF length(pesel) != 11 OR pesel !~ '^[0-9]{11}$' THEN
        RETURN FALSE;
    END IF;
    
    -- Oblicz sumę kontrolną
    FOR i IN 1..10 LOOP
        sum_val := sum_val + (substring(pesel, i, 1)::INTEGER * weights[i]);
    END LOOP;
    
    -- Cyfra kontrolna
    check_digit := (10 - (sum_val % 10)) % 10;
    
    -- Porównaj z ostatnią cyfrą PESEL
    RETURN check_digit = substring(pesel, 11, 1)::INTEGER;
END;
$$;

-- Funkcja rabatów progresywnych
CREATE OR REPLACE FUNCTION calculate_progressive_discount(
    amount NUMERIC,
    customer_type TEXT DEFAULT 'regular'
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    base_discount NUMERIC := 0;
    final_discount NUMERIC := 0;
BEGIN
    -- Rabat bazowy według typu klienta
    base_discount := CASE customer_type
        WHEN 'vip' THEN 0.10
        WHEN 'premium' THEN 0.05
        WHEN 'regular' THEN 0.02
        ELSE 0
    END;
    
    -- Rabat progresywny według kwoty
    IF amount >= 10000 THEN
        final_discount := base_discount + 0.15;  -- +15% dla dużych zamówień
    ELSIF amount >= 5000 THEN
        final_discount := base_discount + 0.10;  -- +10%
    ELSIF amount >= 1000 THEN
        final_discount := base_discount + 0.05;  -- +5%
    ELSE
        final_discount := base_discount;
    END IF;
    
    -- Maksymalny rabat 30%
    final_discount := LEAST(final_discount, 0.30);
    
    RETURN ROUND(amount * final_discount, 2);
END;
$$;
```

### 3. **Funkcje daty i czasu**

```sql
-- Obliczanie wieku w latach
CREATE OR REPLACE FUNCTION calculate_age(birth_date DATE)
RETURNS INTEGER
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    IF birth_date > CURRENT_DATE THEN
        RAISE EXCEPTION 'Data urodzenia nie może być w przyszłości';
    END IF;
    
    RETURN EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date))::INTEGER;
END;
$$;

-- Następny dzień roboczy
CREATE OR REPLACE FUNCTION next_business_day(input_date DATE DEFAULT CURRENT_DATE)
RETURNS DATE
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    result_date DATE := input_date + 1;
    day_of_week INTEGER;
BEGIN
    LOOP
        day_of_week := EXTRACT(DOW FROM result_date); -- 0=Sunday, 6=Saturday
        
        -- Jeśli nie jest weekendem, zwróć datę
        IF day_of_week NOT IN (0, 6) THEN
            RETURN result_date;
        END IF;
        
        result_date := result_date + 1;
    END LOOP;
END;
$$;

-- Liczba dni roboczych między datami
CREATE OR REPLACE FUNCTION business_days_between(
    start_date DATE,
    end_date DATE
)
RETURNS INTEGER
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    current_date DATE := start_date;
    count_days INTEGER := 0;
    day_of_week INTEGER;
BEGIN
    IF start_date > end_date THEN
        RAISE EXCEPTION 'Data początkowa nie może być późniejsza niż końcowa';
    END IF;
    
    WHILE current_date <= end_date LOOP
        day_of_week := EXTRACT(DOW FROM current_date);
        
        -- Licz tylko dni robocze (poniedziałek-piątek)
        IF day_of_week BETWEEN 1 AND 5 THEN
            count_days := count_days + 1;
        END IF;
        
        current_date := current_date + 1;
    END LOOP;
    
    RETURN count_days;
END;
$$;
```

## Funkcje tabelowe

### 1. **Funkcje zwracające TABLE**

```sql
-- Funkcja zwracająca tabelę pracowników działu
CREATE OR REPLACE FUNCTION get_department_employees(dept_name TEXT)
RETURNS TABLE (
    employee_id INTEGER,
    full_name TEXT,
    salary NUMERIC,
    hire_date DATE,
    years_employed INTEGER
)
LANGUAGE plpgsql
STABLE  -- Wynik może się zmienić między transakcjami
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.employee_id,
        e.first_name || ' ' || e.last_name,
        e.salary,
        e.hire_date,
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.hire_date))::INTEGER
    FROM employees e
    JOIN departments d ON e.department_id = d.department_id
    WHERE d.department_name = dept_name
    ORDER BY e.salary DESC;
END;
$$;

-- Użycie:
SELECT * FROM get_department_employees('IT');

-- Funkcja z parametrami opcjonalnymi
CREATE OR REPLACE FUNCTION search_products(
    p_category TEXT DEFAULT NULL,
    p_min_price NUMERIC DEFAULT NULL,
    p_max_price NUMERIC DEFAULT NULL,
    p_in_stock BOOLEAN DEFAULT NULL
)
RETURNS TABLE (
    product_id INTEGER,
    product_name TEXT,
    category TEXT,
    price NUMERIC,
    stock_quantity INTEGER
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.price,
        p.stock_quantity
    FROM products p
    WHERE 
        (p_category IS NULL OR p.category = p_category)
        AND (p_min_price IS NULL OR p.price >= p_min_price)
        AND (p_max_price IS NULL OR p.price <= p_max_price)
        AND (p_in_stock IS NULL OR (p_in_stock AND p.stock_quantity > 0) OR (NOT p_in_stock AND p.stock_quantity = 0))
    ORDER BY p.product_name;
END;
$$;
```

### 2. **Funkcje generujące dane**

```sql
-- Generator liczb
CREATE OR REPLACE FUNCTION generate_numbers(
    start_num INTEGER,
    end_num INTEGER,
    step_size INTEGER DEFAULT 1
)
RETURNS TABLE (number_value INTEGER)
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    current_num INTEGER := start_num;
BEGIN
    IF step_size <= 0 THEN
        RAISE EXCEPTION 'Krok musi być dodatni';
    END IF;
    
    WHILE current_num <= end_num LOOP
        number_value := current_num;
        RETURN NEXT;
        current_num := current_num + step_size;
    END LOOP;
END;
$$;

-- Użycie:
SELECT * FROM generate_numbers(1, 10, 2);  -- 1, 3, 5, 7, 9

-- Generator dat
CREATE OR REPLACE FUNCTION generate_date_series(
    start_date DATE,
    end_date DATE,
    interval_str TEXT DEFAULT '1 day'
)
RETURNS TABLE (date_value DATE)
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    current_date DATE := start_date;
    interval_val INTERVAL := interval_str::INTERVAL;
BEGIN
    WHILE current_date <= end_date LOOP
        date_value := current_date;
        RETURN NEXT;
        current_date := current_date + interval_val;
    END LOOP;
END;
$$;

-- Kalendarz roboczych dni miesiąca
CREATE OR REPLACE FUNCTION get_business_days_in_month(
    year_num INTEGER,
    month_num INTEGER
)
RETURNS TABLE (
    business_date DATE,
    day_name TEXT,
    week_number INTEGER
)
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    first_day DATE;
    last_day DATE;
    current_date DATE;
    dow INTEGER;
BEGIN
    first_day := make_date(year_num, month_num, 1);
    last_day := (first_day + INTERVAL '1 month - 1 day')::DATE;
    current_date := first_day;
    
    WHILE current_date <= last_day LOOP
        dow := EXTRACT(DOW FROM current_date);
        
        -- Tylko dni robocze (poniedziałek-piątek)
        IF dow BETWEEN 1 AND 5 THEN
            business_date := current_date;
            day_name := to_char(current_date, 'Day');
            week_number := EXTRACT(WEEK FROM current_date);
            RETURN NEXT;
        END IF;
        
        current_date := current_date + 1;
    END LOOP;
END;
$$;
```

### 3. **Funkcje analityczne**

```sql
-- Analiza sprzedaży z trendem
CREATE OR REPLACE FUNCTION sales_analysis(
    start_date DATE,
    end_date DATE,
    group_by_period TEXT DEFAULT 'month'  -- 'day', 'week', 'month', 'quarter'
)
RETURNS TABLE (
    period_start DATE,
    period_end DATE,
    total_sales NUMERIC,
    order_count INTEGER,
    avg_order_value NUMERIC,
    growth_rate NUMERIC
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    date_trunc_format TEXT;
    prev_sales NUMERIC := 0;
BEGIN
    date_trunc_format := CASE group_by_period
        WHEN 'day' THEN 'day'
        WHEN 'week' THEN 'week'
        WHEN 'month' THEN 'month'
        WHEN 'quarter' THEN 'quarter'
        ELSE 'month'
    END;
    
    FOR period_start, total_sales, order_count, avg_order_value IN
        SELECT 
            date_trunc(date_trunc_format, o.order_date)::DATE,
            SUM(o.total_amount),
            COUNT(*),
            AVG(o.total_amount)
        FROM orders o
        WHERE o.order_date BETWEEN start_date AND end_date
        GROUP BY date_trunc(date_trunc_format, o.order_date)
        ORDER BY date_trunc(date_trunc_format, o.order_date)
    LOOP
        -- Oblicz koniec okresu
        period_end := CASE group_by_period
            WHEN 'day' THEN period_start
            WHEN 'week' THEN period_start + INTERVAL '6 days'
            WHEN 'month' THEN (period_start + INTERVAL '1 month - 1 day')::DATE
            WHEN 'quarter' THEN (period_start + INTERVAL '3 months - 1 day')::DATE
        END;
        
        -- Oblicz wzrost
        IF prev_sales > 0 THEN
            growth_rate := ROUND(((total_sales - prev_sales) / prev_sales * 100), 2);
        ELSE
            growth_rate := NULL;
        END IF;
        
        RETURN NEXT;
        prev_sales := total_sales;
    END LOOP;
END;
$$;
```

## Funkcje agregujące użytkownika

### 1. **Niestandardowe agregacje**

```sql
-- Funkcja agregująca - średnia ważona
CREATE OR REPLACE FUNCTION weighted_avg_state_func(
    internal_state NUMERIC[],
    value NUMERIC,
    weight NUMERIC
)
RETURNS NUMERIC[]
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    IF internal_state IS NULL THEN
        internal_state := ARRAY[0, 0];  -- [suma_ważona, suma_wag]
    END IF;
    
    internal_state[1] := internal_state[1] + (value * weight);
    internal_state[2] := internal_state[2] + weight;
    
    RETURN internal_state;
END;
$$;

CREATE OR REPLACE FUNCTION weighted_avg_final_func(internal_state NUMERIC[])
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    IF internal_state IS NULL OR internal_state[2] = 0 THEN
        RETURN NULL;
    END IF;
    
    RETURN internal_state[1] / internal_state[2];
END;
$$;

-- Tworzenie agregatu
CREATE AGGREGATE weighted_avg(NUMERIC, NUMERIC) (
    SFUNC = weighted_avg_state_func,
    STYPE = NUMERIC[],
    FINALFUNC = weighted_avg_final_func,
    INITCOND = '{0,0}'
);

-- Użycie:
SELECT 
    category,
    weighted_avg(price, quantity_sold) as avg_weighted_price
FROM product_sales
GROUP BY category;
```

### 2. **Agregacja tekstowa niestandardowa**

```sql
-- Funkcja agregująca - concatenate z separatorem i limitem
CREATE OR REPLACE FUNCTION concat_limited_state_func(
    internal_state TEXT,
    new_value TEXT,
    separator TEXT DEFAULT ', ',
    max_length INTEGER DEFAULT 1000
)
RETURNS TEXT
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    IF internal_state IS NULL THEN
        internal_state := '';
    END IF;
    
    IF new_value IS NULL THEN
        RETURN internal_state;
    END IF;
    
    IF length(internal_state) = 0 THEN
        internal_state := new_value;
    ELSIF length(internal_state) + length(separator) + length(new_value) <= max_length THEN
        internal_state := internal_state || separator || new_value;
    ELSIF position('...' in internal_state) = 0 THEN
        internal_state := internal_state || '...';
    END IF;
    
    RETURN internal_state;
END;
$$;

-- Wykorzystanie w zapytaniach
SELECT 
    department,
    concat_limited_state_func(
        string_agg(employee_name, ', '), 
        ', ', 
        100
    ) as employee_list
FROM employees
GROUP BY department;
```

## Funkcje okienkowe użytkownika

### 1. **Custom window functions**

```sql
-- Funkcja okienkowa - running median (uproszczona)
CREATE OR REPLACE FUNCTION running_median(
    values NUMERIC[]
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    sorted_values NUMERIC[];
    array_length INTEGER;
    median_val NUMERIC;
BEGIN
    IF array_length(values, 1) IS NULL THEN
        RETURN NULL;
    END IF;
    
    -- Sortowanie wartości
    SELECT array_agg(val ORDER BY val)
    INTO sorted_values
    FROM unnest(values) AS val;
    
    array_length := array_length(sorted_values, 1);
    
    -- Oblicz medianę
    IF array_length % 2 = 1 THEN
        median_val := sorted_values[(array_length + 1) / 2];
    ELSE
        median_val := (sorted_values[array_length / 2] + 
                      sorted_values[array_length / 2 + 1]) / 2.0;
    END IF;
    
    RETURN median_val;
END;
$$;

-- Użycie z array_agg w window function
SELECT 
    date,
    value,
    running_median(
        array_agg(value) OVER (
            ORDER BY date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        )
    ) as rolling_median_7days
FROM time_series_data
ORDER BY date;
```

## Optymalizacja funkcji

### 1. **Oznaczenia stabilności**

```sql
-- IMMUTABLE - dla czystych funkcji matematycznych
CREATE OR REPLACE FUNCTION calculate_compound_interest(
    principal NUMERIC,
    rate NUMERIC,
    time_years INTEGER
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE  -- Zawsze ten sam wynik dla tych samych argumentów
AS $$
BEGIN
    RETURN principal * power(1 + rate, time_years);
END;
$$;

-- STABLE - wynik może się zmienić między transakcjami
CREATE OR REPLACE FUNCTION get_current_exchange_rate(currency_code TEXT)
RETURNS NUMERIC
LANGUAGE plpgsql
STABLE  -- Może się zmienić, ale nie w obrębie transakcji
AS $$
DECLARE
    rate NUMERIC;
BEGIN
    SELECT exchange_rate INTO rate
    FROM currency_rates
    WHERE currency = currency_code
      AND rate_date = CURRENT_DATE;
    
    RETURN COALESCE(rate, 1.0);
END;
$$;

-- VOLATILE - może się zmienić w każdym wywołaniu (domyślne)
CREATE OR REPLACE FUNCTION generate_random_id()
RETURNS TEXT
LANGUAGE plpgsql
VOLATILE  -- Zawsze inny wynik
AS $$
BEGIN
    RETURN 'ID_' || to_char(now(), 'YYYYMMDD_HH24MISS') || '_' || 
           lpad((random() * 10000)::INTEGER::TEXT, 4, '0');
END;
$$;
```

### 2. **Optymalizacja wydajności**

```sql
-- Użycie indeksów i cache'owania
CREATE OR REPLACE FUNCTION get_customer_category(customer_id INTEGER)
RETURNS TEXT
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    total_orders INTEGER;
    total_spent NUMERIC;
    last_order_date DATE;
    category TEXT;
BEGIN
    -- Jedno zapytanie zamiast wielu
    SELECT 
        COUNT(*),
        COALESCE(SUM(total_amount), 0),
        MAX(order_date)
    INTO 
        total_orders,
        total_spent,
        last_order_date
    FROM orders
    WHERE customer_id = get_customer_category.customer_id;
    
    -- Logika kategoryzacji
    IF last_order_date < CURRENT_DATE - INTERVAL '1 year' THEN
        category := 'Inactive';
    ELSIF total_spent > 10000 AND total_orders > 20 THEN
        category := 'VIP';
    ELSIF total_spent > 5000 OR total_orders > 10 THEN
        category := 'Premium';
    ELSE
        category := 'Regular';
    END IF;
    
    RETURN category;
END;
$$;

-- Tworzenie indeksu wspomagającego
CREATE INDEX IF NOT EXISTS idx_orders_customer_summary 
ON orders(customer_id) 
INCLUDE (total_amount, order_date);
```

## Bezpieczeństwo funkcji

### 1. **SECURITY DEFINER vs SECURITY INVOKER**

```sql
-- SECURITY DEFINER - wykonuje z prawami twórcy funkcji
CREATE OR REPLACE FUNCTION admin_get_user_data(user_id INTEGER)
RETURNS TABLE (
    user_name TEXT,
    email TEXT,
    created_at TIMESTAMP
)
LANGUAGE plpgsql
SECURITY DEFINER  -- Wykonuje jako admin (twórca funkcji)
SET search_path = public  -- Bezpieczeństwo - ustaw search_path
AS $$
BEGIN
    -- Tylko admin może dostać się do tej tabeli bezpośrednio
    RETURN QUERY
    SELECT u.username, u.email, u.created_at
    FROM admin.users u
    WHERE u.id = user_id;
END;
$$;

-- SECURITY INVOKER - wykonuje z prawami wywołującego (domyślne)
CREATE OR REPLACE FUNCTION user_get_own_data()
RETURNS TABLE (
    user_name TEXT,
    email TEXT
)
LANGUAGE plpgsql
SECURITY INVOKER  -- Wykonuje jako aktualny użytkownik
AS $$
BEGIN
    RETURN QUERY
    SELECT u.username, u.email
    FROM users u
    WHERE u.username = current_user;  -- Tylko własne dane
END;
$$;
```

### 2. **Walidacja i sanityzacja**

```sql
CREATE OR REPLACE FUNCTION safe_search_users(search_term TEXT)
RETURNS TABLE (
    user_id INTEGER,
    username TEXT,
    email TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Walidacja wejścia
    IF search_term IS NULL OR length(trim(search_term)) < 2 THEN
        RAISE EXCEPTION 'Search term must be at least 2 characters long';
    END IF;
    
    -- Sanityzacja - usuń potencjalnie niebezpieczne znaki
    search_term := regexp_replace(search_term, '[^\w\s]', '', 'g');
    
    -- Bezpieczne zapytanie z parametryzacją
    RETURN QUERY
    SELECT u.id, u.username, u.email
    FROM users u
    WHERE u.username ILIKE '%' || search_term || '%'
       OR u.email ILIKE '%' || search_term || '%'
    LIMIT 100;  -- Ogranicz wyniki
END;
$$;
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**

#### 1. **Dokumentacja i konwencje**
```sql
-- Kompleksowa dokumentacja
CREATE OR REPLACE FUNCTION calculate_shipping_cost(
    p_weight_kg NUMERIC,           -- Waga przesyłki w kg
    p_distance_km NUMERIC,         -- Dystans w km
    p_priority TEXT DEFAULT 'normal', -- 'normal', 'express', 'overnight'
    p_insurance_value NUMERIC DEFAULT 0  -- Wartość ubezpieczenia
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
AS $$
/*
Funkcja oblicza koszt wysyłki na podstawie:
- Wagi przesyłki (0.1-50 kg)
- Dystansu (1-10000 km)  
- Priorytetu dostawy
- Wartości ubezpieczenia

Zwraca: koszt w PLN
Autor: Jan Kowalski
Data: 2024-03-15
Wersja: 1.2
*/
DECLARE
    base_cost NUMERIC;
    priority_multiplier NUMERIC;
    insurance_cost NUMERIC;
BEGIN
    -- Walidacja parametrów
    IF p_weight_kg <= 0 OR p_weight_kg > 50 THEN
        RAISE EXCEPTION 'Waga musi być między 0.1 a 50 kg';
    END IF;
    
    -- Reszta implementacji...
    RETURN base_cost * priority_multiplier + insurance_cost;
END;
$$;

-- Komentarz funkcji
COMMENT ON FUNCTION calculate_shipping_cost IS 
'Oblicza koszt wysyłki na podstawie wagi, dystansu i priorytetu';
```

#### 2. **Error handling**
```sql
CREATE OR REPLACE FUNCTION safe_divide(a NUMERIC, b NUMERIC)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    IF b = 0 THEN
        RAISE EXCEPTION 'Division by zero'
            USING ERRCODE = 'P0001',
                  DETAIL = format('Attempted to divide %s by zero', a),
                  HINT = 'Check the denominator value';
    END IF;
    
    RETURN a / b;
EXCEPTION
    WHEN numeric_value_out_of_range THEN
        RAISE EXCEPTION 'Result too large for numeric type'
            USING ERRCODE = 'P0002';
END;
$$;
```

### ❌ **Złe praktyki:**

```sql
-- ❌ Brak walidacji
CREATE FUNCTION bad_function(val TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN upper(val);  -- Co jeśli val jest NULL?
END;
$$ LANGUAGE plpgsql;

-- ❌ SQL injection w dynamicznym SQL
CREATE FUNCTION vulnerable_search(table_name TEXT, search_val TEXT)
RETURNS TABLE(result TEXT) AS $$
BEGIN
    RETURN QUERY EXECUTE 'SELECT name FROM ' || table_name || 
                        ' WHERE name = ''' || search_val || '''';
END;
$$ LANGUAGE plpgsql;

-- ❌ Niewłaściwe oznaczenie stabilności
CREATE FUNCTION wrong_stability()
RETURNS TIMESTAMP AS $$
BEGIN
    RETURN now();  -- VOLATILE, ale oznaczone jako IMMUTABLE!
END;
$$ LANGUAGE plpgsql IMMUTABLE;  -- BŁĄD!
```

## Pułapki egzaminacyjne

### 1. **Typy zwracane**
```
RETURNS SETOF record - może zwrócić wiele wierszy
RETURNS TABLE(...) - określa strukturę zwracanej tabeli
RETURNS record - jeden wiersz o nieokreślonej strukturze
```

### 2. **Stabilność funkcji**
```
IMMUTABLE: czyste funkcje (sin, cos, matematyczne)
STABLE: mogą się zmienić między transakcjami (current_date)
VOLATILE: mogą się zmienić w każdym wywołaniu (now(), random())
```

### 3. **Security**
```
SECURITY DEFINER: prawa twórcy funkcji
SECURITY INVOKER: prawa wywołującego (domyślne)
Zawsze ustawiaj search_path w SECURITY DEFINER!
```

### 4. **RETURN NEXT vs RETURN QUERY**
```
RETURN NEXT: dodaje jeden wiersz do wyniku
RETURN QUERY: dodaje wynik całego zapytania
RETURN: kończy funkcję (w funkcjach skalarnych)
```