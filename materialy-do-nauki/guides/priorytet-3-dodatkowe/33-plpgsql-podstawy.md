# PL/pgSQL - podstawy języka

## Definicja PL/pgSQL

**PL/pgSQL** (Procedural Language/PostgreSQL) to **proceduralny język programowania** wbudowany w PostgreSQL, służący do tworzenia **funkcji, procedur, triggerów** i innych elementów logiki biznesowej po stronie serwera bazy danych.

### Kluczowe cechy:
- **Proceduralność** - zmienne, pętle, warunki, obsługa wyjątków
- **Integracja z SQL** - bezpośrednie wykonywanie zapytań SQL
- **Wydajność** - wykonywane po stronie serwera
- **Bezpieczeństwo** - kontrola dostępu, walidacja danych
- **Atomowość** - automatyczne transakcje

### Zastosowania:
- **Funkcje użytkownika** - logika biznesowa
- **Triggery** - automatyczne reakcje na zmiany danych
- **Procedury składowane** - złożone operacje
- **Walidacja danych** - kontrola integralności
- **Audyt** - śledzenie zmian

## Struktura funkcji PL/pgSQL

### Podstawowa składnia:
```sql
CREATE OR REPLACE FUNCTION nazwa_funkcji(parametry)
RETURNS typ_zwracany
LANGUAGE plpgsql
AS $$
DECLARE
    -- Deklaracje zmiennych
BEGIN
    -- Ciało funkcji
    RETURN wartość;
EXCEPTION
    -- Obsługa wyjątków (opcjonalne)
END;
$$;
```

### Przykład prostej funkcji:
```sql
CREATE OR REPLACE FUNCTION dodaj_liczby(a INTEGER, b INTEGER)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    wynik INTEGER;
BEGIN
    wynik := a + b;
    RETURN wynik;
END;
$$;

-- Wywołanie:
SELECT dodaj_liczby(5, 3);  -- Wynik: 8
```

## Typy danych i zmienne

### 1. **Deklaracja zmiennych**

```sql
CREATE OR REPLACE FUNCTION demo_zmiennych()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    -- Podstawowe typy
    liczba INTEGER := 10;
    tekst VARCHAR(100) := 'Hello World';
    data_var DATE := CURRENT_DATE;
    bool_var BOOLEAN := TRUE;
    
    -- Typy bazujące na kolumnach tabeli
    user_name users.name%TYPE;
    user_record users%ROWTYPE;
    
    -- Typy z zapytań
    max_salary NUMERIC;
    
    -- Tablice
    liczby INTEGER[] := ARRAY[1, 2, 3, 4, 5];
    
    -- Records (struktury)
    employee_info RECORD;
BEGIN
    -- Inicjalizacja w kodzie
    max_salary := (SELECT MAX(salary) FROM employees);
    user_name := 'Jan Kowalski';
    
    RETURN 'Zmienne zainicjowane';
END;
$$;
```

### 2. **Operatory przypisania**

```sql
CREATE OR REPLACE FUNCTION demo_przypisania()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    x INTEGER := 5;
    y INTEGER;
    nazwa TEXT;
BEGIN
    -- Podstawowe przypisanie
    y := x * 2;
    
    -- Przypisanie z zapytania SQL
    SELECT first_name INTO nazwa
    FROM employees 
    WHERE employee_id = 1;
    
    -- Przypisanie z funkcji
    y := LENGTH('PostgreSQL');
    
    -- Wyrażenia
    x := CASE 
        WHEN y > 10 THEN y * 2
        ELSE y / 2
    END;
    
    RETURN format('x=%s, y=%s, nazwa=%s', x, y, nazwa);
END;
$$;
```

## Instrukcje kontrolne

### 1. **IF-THEN-ELSE**

```sql
CREATE OR REPLACE FUNCTION klasyfikuj_wiek(wiek INTEGER)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
BEGIN
    IF wiek < 18 THEN
        RETURN 'Nieletni';
    ELSIF wiek < 65 THEN
        RETURN 'Dorosły';
    ELSE
        RETURN 'Senior';
    END IF;
END;
$$;

-- Złożony przykład z zagnieżdżonymi warunkami
CREATE OR REPLACE FUNCTION oceń_pracownika(
    p_pensja NUMERIC,
    p_lata_pracy INTEGER,
    p_wydajność NUMERIC
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    ocena TEXT;
BEGIN
    IF p_pensja > 8000 THEN
        IF p_wydajność > 85 THEN
            ocena := 'Doskonały';
        ELSE
            ocena := 'Dobry';
        END IF;
    ELSIF p_pensja > 5000 THEN
        IF p_lata_pracy > 5 AND p_wydajność > 75 THEN
            ocena := 'Satysfakcjonujący';
        ELSE
            ocena := 'Przeciętny';
        END IF;
    ELSE
        IF p_lata_pracy < 2 THEN
            ocena := 'Początkujący';
        ELSE
            ocena := 'Wymaga poprawy';
        END IF;
    END IF;
    
    RETURN ocena;
END;
$$;
```

### 2. **CASE**

```sql
CREATE OR REPLACE FUNCTION dzien_tygodnia_pl(dzien INTEGER)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN CASE dzien
        WHEN 1 THEN 'Poniedziałek'
        WHEN 2 THEN 'Wtorek'
        WHEN 3 THEN 'Środa'
        WHEN 4 THEN 'Czwartek'
        WHEN 5 THEN 'Piątek'
        WHEN 6 THEN 'Sobota'
        WHEN 7 THEN 'Niedziela'
        ELSE 'Nieprawidłowy dzień'
    END;
END;
$$;

-- CASE z warunkami
CREATE OR REPLACE FUNCTION kategoria_bmı(bmi NUMERIC)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN CASE
        WHEN bmi < 18.5 THEN 'Niedowaga'
        WHEN bmi >= 18.5 AND bmi < 25 THEN 'Norma'
        WHEN bmi >= 25 AND bmi < 30 THEN 'Nadwaga'
        WHEN bmi >= 30 THEN 'Otyłość'
        ELSE 'Nieprawidłowe BMI'
    END;
END;
$$;
```

## Pętle

### 1. **LOOP - pętla podstawowa**

```sql
CREATE OR REPLACE FUNCTION suma_do_n(n INTEGER)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    suma INTEGER := 0;
    i INTEGER := 1;
BEGIN
    LOOP
        EXIT WHEN i > n;  -- Warunek wyjścia
        
        suma := suma + i;
        i := i + 1;
        
        -- Alternatywne wyjście z warunkiem
        IF i > 1000 THEN  -- Zabezpieczenie przed nieskończoną pętlą
            RAISE EXCEPTION 'Za duża wartość n: %', n;
        END IF;
    END LOOP;
    
    RETURN suma;
END;
$$;
```

### 2. **WHILE**

```sql
CREATE OR REPLACE FUNCTION silnia(n INTEGER)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    wynik BIGINT := 1;
    i INTEGER := 1;
BEGIN
    IF n < 0 THEN
        RAISE EXCEPTION 'Silnia nie jest zdefiniowana dla liczb ujemnych';
    END IF;
    
    WHILE i <= n LOOP
        wynik := wynik * i;
        i := i + 1;
    END LOOP;
    
    RETURN wynik;
END;
$$;

-- Przykład z wczesnym wyjściem
CREATE OR REPLACE FUNCTION znajdz_pierwszą_liczbę_pierwszą_powyżej(start_num INTEGER)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    current_num INTEGER := start_num + 1;
    i INTEGER;
    jest_pierwsza BOOLEAN;
BEGIN
    WHILE current_num < 10000 LOOP  -- Limit bezpieczeństwa
        jest_pierwsza := TRUE;
        i := 2;
        
        WHILE i * i <= current_num AND jest_pierwsza LOOP
            IF current_num % i = 0 THEN
                jest_pierwsza := FALSE;
            END IF;
            i := i + 1;
        END LOOP;
        
        IF jest_pierwsza THEN
            RETURN current_num;
        END IF;
        
        current_num := current_num + 1;
    END LOOP;
    
    RETURN NULL;  -- Nie znaleziono
END;
$$;
```

### 3. **FOR - pętle numeryczne**

```sql
-- FOR z zakresem liczb
CREATE OR REPLACE FUNCTION tabelka_mnożenia(n INTEGER)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    wynik TEXT := '';
    i INTEGER;
    j INTEGER;
BEGIN
    FOR i IN 1..n LOOP
        FOR j IN 1..n LOOP
            wynik := wynik || format('%3s ', i * j);
        END LOOP;
        wynik := wynik || E'\n';  -- Nowa linia
    END LOOP;
    
    RETURN wynik;
END;
$$;

-- FOR z krokiem
CREATE OR REPLACE FUNCTION liczby_parzyste(start_num INTEGER, end_num INTEGER)
RETURNS INTEGER[]
LANGUAGE plpgsql
AS $$
DECLARE
    result INTEGER[] := '{}';
    i INTEGER;
BEGIN
    FOR i IN start_num..end_num BY 2 LOOP
        result := array_append(result, i);
    END LOOP;
    
    RETURN result;
END;
$$;

-- FOR odwrotnie
CREATE OR REPLACE FUNCTION countdown(from_num INTEGER)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    result TEXT := '';
    i INTEGER;
BEGIN
    FOR i IN REVERSE from_num..1 LOOP
        result := result || i || ' ';
    END LOOP;
    result := result || 'Start!';
    
    RETURN result;
END;
$$;
```

### 4. **FOR z kursorami**

```sql
-- FOR z zapytaniem
CREATE OR REPLACE FUNCTION lista_pracowników_działu(dept_name TEXT)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    employee_record RECORD;
    result TEXT := '';
BEGIN
    FOR employee_record IN 
        SELECT first_name, last_name, salary
        FROM employees e
        JOIN departments d ON e.department_id = d.department_id
        WHERE d.department_name = dept_name
        ORDER BY salary DESC
    LOOP
        result := result || format('%s %s (%.2f)' || E'\n', 
                                 employee_record.first_name,
                                 employee_record.last_name,
                                 employee_record.salary);
    END LOOP;
    
    IF result = '' THEN
        result := 'Brak pracowników w dziale: ' || dept_name;
    END IF;
    
    RETURN result;
END;
$$;

-- FOR z tablicą
CREATE OR REPLACE FUNCTION suma_tablicy(liczby INTEGER[])
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    element INTEGER;
    suma INTEGER := 0;
BEGIN
    FOREACH element IN ARRAY liczby LOOP
        suma := suma + element;
    END LOOP;
    
    RETURN suma;
END;
$$;
```

## Praca z SQL w PL/pgSQL

### 1. **SELECT INTO**

```sql
CREATE OR REPLACE FUNCTION info_o_kliencie(klient_id INTEGER)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    klient_nazwa TEXT;
    liczba_zamowien INTEGER;
    suma_zamowien NUMERIC;
    ostatnie_zamowienie DATE;
BEGIN
    -- Pojedynczy SELECT INTO
    SELECT name INTO klient_nazwa
    FROM customers
    WHERE customer_id = klient_id;
    
    -- Sprawdzenie czy znaleziono
    IF NOT FOUND THEN
        RETURN 'Klient o ID ' || klient_id || ' nie został znaleziony';
    END IF;
    
    -- Złożone zapytanie z wieloma wartościami
    SELECT 
        COUNT(*),
        COALESCE(SUM(total_amount), 0),
        MAX(order_date)
    INTO 
        liczba_zamowien,
        suma_zamowien,
        ostatnie_zamowienie
    FROM orders
    WHERE customer_id = klient_id;
    
    RETURN format('Klient: %s, Zamówienia: %s, Suma: %.2f, Ostatnie: %s',
                  klient_nazwa, liczba_zamowien, suma_zamowien, ostatnie_zamowienie);
END;
$$;
```

### 2. **PERFORM - wykonywanie bez zwracania**

```sql
CREATE OR REPLACE FUNCTION aktualizuj_statystyki_klienta(klient_id INTEGER)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    stats_record RECORD;
BEGIN
    -- Sprawdź czy klient istnieje
    PERFORM 1 FROM customers WHERE customer_id = klient_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Klient o ID % nie istnieje', klient_id;
    END IF;
    
    -- Oblicz statystyki
    SELECT 
        COUNT(*) as total_orders,
        COALESCE(SUM(total_amount), 0) as total_spent,
        MAX(order_date) as last_order_date
    INTO stats_record
    FROM orders
    WHERE customer_id = klient_id;
    
    -- Aktualizuj lub wstaw statystyki
    UPDATE customer_statistics 
    SET 
        total_orders = stats_record.total_orders,
        total_spent = stats_record.total_spent,
        last_order_date = stats_record.last_order_date,
        updated_at = CURRENT_TIMESTAMP
    WHERE customer_id = klient_id;
    
    -- Jeśli nie ma rekordu, wstaw nowy
    IF NOT FOUND THEN
        INSERT INTO customer_statistics (
            customer_id, total_orders, total_spent, 
            last_order_date, updated_at
        ) VALUES (
            klient_id, stats_record.total_orders, stats_record.total_spent,
            stats_record.last_order_date, CURRENT_TIMESTAMP
        );
    END IF;
END;
$$;
```

### 3. **Dynamic SQL - EXECUTE**

```sql
CREATE OR REPLACE FUNCTION zlicz_rekordy_w_tabeli(table_name TEXT)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    result INTEGER;
    sql_query TEXT;
BEGIN
    -- Budowanie zapytania dynamicznie
    sql_query := 'SELECT COUNT(*) FROM ' || quote_ident(table_name);
    
    -- Wykonanie dynamicznego SQL
    EXECUTE sql_query INTO result;
    
    RETURN result;
END;
$$;

-- Zaawansowany przykład z parametrami
CREATE OR REPLACE FUNCTION filtruj_tabelę(
    p_table_name TEXT,
    p_column_name TEXT,
    p_filter_value TEXT
)
RETURNS TABLE(result_row RECORD)
LANGUAGE plpgsql
AS $$
DECLARE
    sql_query TEXT;
BEGIN
    -- Bezpieczne budowanie zapytania
    sql_query := format('SELECT * FROM %I WHERE %I = $1',
                       p_table_name, p_column_name);
    
    -- Wykonanie z parametrem
    RETURN QUERY EXECUTE sql_query USING p_filter_value;
END;
$$;
```

## Obsługa wyjątków

### 1. **EXCEPTION - podstawy**

```sql
CREATE OR REPLACE FUNCTION bezpieczne_dzielenie(a NUMERIC, b NUMERIC)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN a / b;
EXCEPTION
    WHEN division_by_zero THEN
        RAISE NOTICE 'Dzielenie przez zero! Zwracam NULL';
        RETURN NULL;
    WHEN OTHERS THEN
        RAISE NOTICE 'Nieoczekiwany błąd: %', SQLERRM;
        RETURN NULL;
END;
$$;
```

### 2. **Własne wyjątki**

```sql
CREATE OR REPLACE FUNCTION transfer_funds(
    from_account INTEGER,
    to_account INTEGER, 
    amount NUMERIC
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    from_balance NUMERIC;
    to_account_exists BOOLEAN;
BEGIN
    -- Sprawdź saldo konta źródłowego
    SELECT balance INTO from_balance
    FROM accounts
    WHERE account_id = from_account;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'INVALID_ACCOUNT'
            USING MESSAGE = 'Konto źródłowe nie istnieje',
                  DETAIL = 'Account ID: ' || from_account,
                  HINT = 'Sprawdź poprawność numeru konta';
    END IF;
    
    -- Sprawdź czy jest wystarczające saldo
    IF from_balance < amount THEN
        RAISE EXCEPTION 'INSUFFICIENT_FUNDS'
            USING MESSAGE = 'Niewystarczające środki',
                  DETAIL = format('Saldo: %.2f, Żądana kwota: %.2f', 
                                from_balance, amount);
    END IF;
    
    -- Sprawdź konto docelowe
    SELECT EXISTS(SELECT 1 FROM accounts WHERE account_id = to_account)
    INTO to_account_exists;
    
    IF NOT to_account_exists THEN
        RAISE EXCEPTION 'INVALID_ACCOUNT'
            USING MESSAGE = 'Konto docelowe nie istnieje',
                  DETAIL = 'Account ID: ' || to_account;
    END IF;
    
    -- Wykonaj transfer
    UPDATE accounts SET balance = balance - amount WHERE account_id = from_account;
    UPDATE accounts SET balance = balance + amount WHERE account_id = to_account;
    
    -- Log transakcji
    INSERT INTO transaction_log (from_account, to_account, amount, transaction_date)
    VALUES (from_account, to_account, amount, CURRENT_TIMESTAMP);
    
    RETURN 'Transfer wykonany pomyślnie';
    
EXCEPTION
    WHEN SQLSTATE 'P0001' THEN  -- User-defined exception
        -- Re-raise with more context
        RAISE EXCEPTION 'Transfer failed: %', SQLERRM
            USING DETAIL = SQLSTATE;
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Unexpected error during transfer: %', SQLERRM
            USING DETAIL = 'SQLSTATE: ' || SQLSTATE;
END;
$$;
```

### 3. **Kody błędów**

```sql
CREATE OR REPLACE FUNCTION demo_error_codes()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
BEGIN
    -- Symulacja różnych błędów
    PERFORM 1/0;  -- Division by zero
    
EXCEPTION
    WHEN division_by_zero THEN
        RAISE NOTICE 'Kod błędu: %, Komunikat: %', SQLSTATE, SQLERRM;
        RETURN 'Przechwycono dzielenie przez zero';
        
    WHEN unique_violation THEN
        RAISE NOTICE 'Naruszenie unikalności: %', SQLERRM;
        RETURN 'Duplikat klucza';
        
    WHEN foreign_key_violation THEN
        RAISE NOTICE 'Naruszenie klucza obcego: %', SQLERRM;
        RETURN 'Nieprawidłowy klucz obcy';
        
    WHEN check_violation THEN
        RAISE NOTICE 'Naruszenie CHECK constraint: %', SQLERRM;
        RETURN 'Nieprawidłowa wartość';
        
    WHEN OTHERS THEN
        RAISE NOTICE 'Inny błąd - SQLSTATE: %, SQLERRM: %', SQLSTATE, SQLERRM;
        RETURN 'Nieznany błąd';
END;
$$;
```

## Debugging i logging

### 1. **RAISE - komunikaty diagnostyczne**

```sql
CREATE OR REPLACE FUNCTION debug_function(input_value INTEGER)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    result INTEGER;
    step_counter INTEGER := 0;
BEGIN
    RAISE NOTICE 'Funkcja rozpoczęta z parametrem: %', input_value;
    
    step_counter := step_counter + 1;
    RAISE NOTICE 'Krok %: Walidacja danych', step_counter;
    
    IF input_value < 0 THEN
        RAISE WARNING 'Wartość ujemna: %. Używam wartości bezwzględnej.', input_value;
        input_value := ABS(input_value);
    END IF;
    
    step_counter := step_counter + 1;
    RAISE NOTICE 'Krok %: Obliczenia', step_counter;
    
    result := input_value * 2 + 10;
    
    RAISE DEBUG 'Wynik obliczeń: %', result;
    RAISE NOTICE 'Funkcja zakończona pomyślnie';
    
    RETURN result;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Błąd w kroku %: %', step_counter, SQLERRM;
END;
$$;

-- Ustawienie poziomu logowania
SET client_min_messages TO NOTICE;  -- NOTICE, WARNING, ERROR
SET log_min_messages TO DEBUG;      -- Server-side logging
```

### 2. **ASSERT - asercje**

```sql
CREATE OR REPLACE FUNCTION calculate_discount(
    order_amount NUMERIC,
    customer_level INTEGER
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    discount_rate NUMERIC;
    final_discount NUMERIC;
BEGIN
    -- Asercje walidacyjne
    ASSERT order_amount > 0, 'Kwota zamówienia musi być dodatnia';
    ASSERT customer_level BETWEEN 1 AND 5, 'Poziom klienta musi być 1-5';
    
    -- Oblicz rabat
    discount_rate := CASE customer_level
        WHEN 1 THEN 0.05
        WHEN 2 THEN 0.10
        WHEN 3 THEN 0.15
        WHEN 4 THEN 0.20
        WHEN 5 THEN 0.25
    END;
    
    final_discount := order_amount * discount_rate;
    
    -- Asercja wyniku
    ASSERT final_discount >= 0 AND final_discount <= order_amount,
           'Rabat poza oczekiwanym zakresem';
    
    RETURN final_discount;
END;
$$;
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**

#### 1. **Naming conventions**
```sql
-- Opisowe nazwy funkcji
CREATE OR REPLACE FUNCTION calculate_employee_bonus(
    p_employee_id INTEGER,          -- Prefix dla parametrów
    p_performance_rating NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_current_salary NUMERIC;      -- Prefix dla zmiennych
    v_bonus_multiplier NUMERIC;
    v_calculated_bonus NUMERIC;
BEGIN
    -- Jasny kod z komentarzami
END;
$$;
```

#### 2. **Error handling**
```sql
CREATE OR REPLACE FUNCTION safe_operation()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
BEGIN
    -- Główna logika
    RETURN 'Success';
EXCEPTION
    WHEN OTHERS THEN
        -- Log błędu
        INSERT INTO error_log (error_message, error_detail, occurred_at)
        VALUES (SQLERRM, SQLSTATE, CURRENT_TIMESTAMP);
        
        -- Re-raise lub zwróć error code
        RAISE;
END;
$$;
```

#### 3. **Performance**
```sql
-- Używaj FOUND zamiast COUNT(*)
SELECT id INTO v_id FROM table WHERE condition;
IF FOUND THEN
    -- Record exists
END IF;

-- Nie:
SELECT COUNT(*) INTO v_count FROM table WHERE condition;
IF v_count > 0 THEN
    -- Record exists  
END IF;
```

### ❌ **Złe praktyki:**

```sql
-- ❌ Brak obsługi błędów
CREATE FUNCTION bad_function()
RETURNS TEXT AS $$
BEGIN
    -- Niebezpieczne operacje bez try/catch
    RETURN (SELECT value FROM table WHERE id = some_id);
END;
$$ LANGUAGE plpgsql;

-- ❌ SQL injection w EXECUTE
CREATE FUNCTION vulnerable_function(table_name TEXT)
RETURNS INTEGER AS $$
BEGIN
    EXECUTE 'SELECT COUNT(*) FROM ' || table_name;  -- NIEBEZPIECZNE!
END;
$$ LANGUAGE plpgsql;

-- ✅ Bezpieczna alternatywa
CREATE FUNCTION safe_function(table_name TEXT)
RETURNS INTEGER AS $$
DECLARE
    result INTEGER;
BEGIN
    EXECUTE 'SELECT COUNT(*) FROM ' || quote_ident(table_name) INTO result;
    RETURN result;
END;
$$ LANGUAGE plpgsql;
```

## Pułapki egzaminacyjne

### 1. **Składnia przypisania**
```
PL/pgSQL: zmienna := wartość
SQL: SET zmienna = wartość

Różne operatory!
```

### 2. **FOUND vs NOT FOUND**
```
FOUND: TRUE jeśli ostatnie SELECT/UPDATE/DELETE dotknęło wiersze
NOT FOUND: TRUE jeśli ostatnie SELECT/UPDATE/DELETE nie dotknęło wierszy

Sprawdzaj zawsze po SELECT INTO!
```

### 3. **Zmienne vs kolumny**
```
W PL/pgSQL zmienne mogą przesłaniać nazwy kolumn
Używaj prefiksów lub aliasów tabel!
```

### 4. **EXCEPTION handling**
```
EXCEPTION blok przerywa wykonywanie funkcji
RAISE re-throws błąd jeśli nie zostanie przechwycony
SQLSTATE i SQLERRM dostępne w bloku EXCEPTION
```