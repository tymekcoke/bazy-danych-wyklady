# 🔧 PL/pgSQL PODSTAWY - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"PL/pgSQL to proceduralny język programowania PostgreSQL umożliwiający pisanie funkcji i procedur. Kluczowe elementy:

1. **Zmienne i typy danych** - deklaracja i przypisywanie wartości
2. **Struktury kontrolne** - IF/ELSE, LOOP, FOR, WHILE
3. **Obsługa wyjątków** - BEGIN/EXCEPTION/END bloki
4. **Kursory** - iteracja przez wyniki zapytań
5. **Triggery** - automatyczne wykonywanie przy zdarzeniach DML

PL/pgSQL pozwala na implementację złożonej logiki biznesowej bezpośrednio w bazie danych, zwiększając wydajność i zapewniając spójność danych."

## ✍️ CO NAPISAĆ NA KARTCE

```sql
PL/pgSQL PODSTAWY - SKŁADNIA:

STRUKTURA FUNKCJI:
CREATE OR REPLACE FUNCTION nazwa(parametry)
RETURNS typ AS $$
DECLARE
    zmienna typ;
BEGIN
    -- kod funkcji
    RETURN wartość;
EXCEPTION
    WHEN warunek THEN
        -- obsługa błędu
END;
$$ LANGUAGE plpgsql;

TYPY DANYCH:
• INTEGER, BIGINT, DECIMAL(p,s)
• VARCHAR(n), TEXT, CHAR(n)
• BOOLEAN, DATE, TIMESTAMP
• RECORD - wiersz tabeli
• %TYPE - typ kolumny: kolumna%TYPE
• %ROWTYPE - typ wiersza: tabela%ROWTYPE

ZMIENNE:
DECLARE
    counter INTEGER := 0;
    user_name VARCHAR(50);
    emp_record employees%ROWTYPE;
    salary employees.salary%TYPE;

STRUKTURY KONTROLNE:
IF warunek THEN
    -- kod
ELSIF warunek THEN
    -- kod
ELSE
    -- kod
END IF;

LOOP
    -- kod
    EXIT WHEN warunek;
END LOOP;

FOR i IN 1..10 LOOP
    -- kod
END LOOP;

FOR record IN SELECT * FROM tabela LOOP
    -- kod z record.kolumna
END LOOP;

WHILE warunek LOOP
    -- kod
END LOOP;

WYJĄTKI:
BEGIN
    -- kod mogący rzucić wyjątek
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Błąd: %', SQLERRM;
        RETURN FALSE;
END;

KURSORY:
DECLARE
    cur CURSOR FOR SELECT * FROM tabela;
    rec RECORD;
BEGIN
    OPEN cur;
    LOOP
        FETCH cur INTO rec;
        EXIT WHEN NOT FOUND;
        -- przetwarzanie rec
    END LOOP;
    CLOSE cur;
END;

TRIGGERY:
CREATE TRIGGER nazwa
    BEFORE/AFTER INSERT/UPDATE/DELETE
    ON tabela
    FOR EACH ROW
    EXECUTE FUNCTION trigger_function();
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- KOMPLEKSOWA DEMONSTRACJA PL/pgSQL

-- Przygotowanie tabel testowych
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    owner_name VARCHAR(100) NOT NULL,
    balance DECIMAL(12,2) DEFAULT 0,
    account_type VARCHAR(20) DEFAULT 'checking',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    from_account_id INT REFERENCES accounts(id),
    to_account_id INT REFERENCES accounts(id),
    amount DECIMAL(10,2) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    description TEXT,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50),
    operation VARCHAR(10),
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dane testowe
INSERT INTO accounts (account_number, owner_name, balance, account_type) VALUES
('ACC001', 'Jan Kowalski', 5000.00, 'checking'),
('ACC002', 'Anna Nowak', 3000.00, 'savings'),
('ACC003', 'Piotr Wiśniewski', 1500.00, 'checking'),
('ACC004', 'Maria Kowalczyk', 8000.00, 'savings'),
('ACC005', 'Tomasz Zieliński', 500.00, 'checking');

-- 1. PODSTAWOWE FUNKCJE - TYPY DANYCH I ZMIENNE

-- Funkcja z różnymi typami danych
CREATE OR REPLACE FUNCTION calculate_account_stats(
    account_id_param INT
) RETURNS TABLE(
    account_info TEXT,
    current_balance DECIMAL(12,2),
    account_age_days INT,
    status_description TEXT
) AS $$
DECLARE
    -- Różne typy zmiennych
    acc_record accounts%ROWTYPE;  -- Typ wiersza tabeli
    balance_amount accounts.balance%TYPE;  -- Typ kolumny
    account_age INTEGER;
    status_text VARCHAR(100);
    account_exists BOOLEAN := FALSE;
BEGIN
    -- Sprawdzenie czy konto istnieje
    SELECT * INTO acc_record
    FROM accounts a
    WHERE a.id = account_id_param;
    
    -- Sprawdzenie czy znaleziono rekord
    IF FOUND THEN
        account_exists := TRUE;
        balance_amount := acc_record.balance;
        account_age := EXTRACT(DAY FROM CURRENT_TIMESTAMP - acc_record.created_at);
        
        -- Logika warunkowa
        IF acc_record.is_active THEN
            IF balance_amount > 5000 THEN
                status_text := 'Premium Active Account';
            ELSIF balance_amount > 1000 THEN
                status_text := 'Standard Active Account';
            ELSE
                status_text := 'Basic Active Account';
            END IF;
        ELSE
            status_text := 'Inactive Account';
        END IF;
        
        -- Zwrócenie wyników
        account_info := acc_record.account_number || ' - ' || acc_record.owner_name;
        current_balance := balance_amount;
        account_age_days := account_age;
        status_description := status_text;
        
        RETURN NEXT;  -- Zwrócenie wiersza w funkcji TABLE
    ELSE
        -- Konto nie istnieje
        account_info := 'Account not found';
        current_balance := 0;
        account_age_days := 0;
        status_description := 'No account with ID: ' || account_id_param;
        
        RETURN NEXT;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Test funkcji
SELECT * FROM calculate_account_stats(1);
SELECT * FROM calculate_account_stats(999);

-- 2. STRUKTURY KONTROLNE - PĘTLE I WARUNKI

-- Funkcja z różnymi typami pętli
CREATE OR REPLACE FUNCTION process_accounts_batch(
    min_balance DECIMAL DEFAULT 0,
    max_accounts INT DEFAULT 10
) RETURNS TEXT AS $$
DECLARE
    processed_count INT := 0;
    account_rec RECORD;
    result_message TEXT := '';
    counter INT;
    total_processed_amount DECIMAL(12,2) := 0;
BEGIN
    -- FOR LOOP z zapytaniem
    FOR account_rec IN 
        SELECT id, account_number, owner_name, balance 
        FROM accounts 
        WHERE balance >= min_balance AND is_active = TRUE
        ORDER BY balance DESC
        LIMIT max_accounts
    LOOP
        -- Zwiększenie licznika
        processed_count := processed_count + 1;
        total_processed_amount := total_processed_amount + account_rec.balance;
        
        -- Aktualizacja salda (przykładowa operacja)
        UPDATE accounts 
        SET balance = balance * 1.01  -- 1% bonus
        WHERE id = account_rec.id;
        
        -- Dodanie do komunikatu
        result_message := result_message || 
            'Processed: ' || account_rec.account_number || 
            ' (Balance: ' || account_rec.balance || ')' || E'\n';
    END LOOP;
    
    -- WHILE LOOP - przykład dodatkowego przetwarzania
    counter := 1;
    WHILE counter <= 3 AND processed_count > 0 LOOP
        result_message := result_message || 
            'Processing round ' || counter || ' completed.' || E'\n';
        counter := counter + 1;
    END LOOP;
    
    -- FOR LOOP z zakresem liczbowym
    FOR i IN 1..processed_count LOOP
        -- Symulacja dodatkowego przetwarzania
        IF i % 2 = 0 THEN
            result_message := result_message || 
                'Even iteration: ' || i || E'\n';
        END IF;
    END LOOP;
    
    -- Końcowy komunikat
    result_message := result_message || 
        'SUMMARY: Processed ' || processed_count || ' accounts, ' ||
        'Total amount processed: ' || total_processed_amount;
    
    RETURN result_message;
END;
$$ LANGUAGE plpgsql;

-- Test funkcji
SELECT process_accounts_batch(1000, 5);

-- 3. OBSŁUGA WYJĄTKÓW

-- Funkcja z kompleksową obsługą błędów
CREATE OR REPLACE FUNCTION transfer_money(
    from_account_id INT,
    to_account_id INT,
    transfer_amount DECIMAL(10,2),
    description_text TEXT DEFAULT 'Money transfer'
) RETURNS BOOLEAN AS $$
DECLARE
    from_balance DECIMAL(12,2);
    to_account_exists BOOLEAN;
    transaction_id INT;
    error_message TEXT;
BEGIN
    -- Sprawdzenie parametrów wejściowych
    IF transfer_amount <= 0 THEN
        RAISE EXCEPTION 'Transfer amount must be positive, got: %', transfer_amount;
    END IF;
    
    IF from_account_id = to_account_id THEN
        RAISE EXCEPTION 'Cannot transfer to the same account';
    END IF;
    
    BEGIN
        -- Sprawdzenie konta źródłowego i blokada
        SELECT balance INTO STRICT from_balance
        FROM accounts 
        WHERE id = from_account_id AND is_active = TRUE
        FOR UPDATE;  -- Blokada wiersza
        
        -- Sprawdzenie czy wystarczające środki
        IF from_balance < transfer_amount THEN
            RAISE EXCEPTION 'Insufficient funds. Balance: %, Required: %', 
                from_balance, transfer_amount;
        END IF;
        
        -- Sprawdzenie konta docelowego
        SELECT TRUE INTO to_account_exists
        FROM accounts 
        WHERE id = to_account_id AND is_active = TRUE;
        
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Destination account % not found or inactive', to_account_id;
        END IF;
        
        -- Rozpoczęcie transakcji w bazie
        -- (funkcja jest już w transakcji, ale pokazujemy strukturę)
        
        -- Pobranie z konta źródłowego
        UPDATE accounts 
        SET balance = balance - transfer_amount 
        WHERE id = from_account_id;
        
        -- Dodanie do konta docelowego
        UPDATE accounts 
        SET balance = balance + transfer_amount 
        WHERE id = to_account_id;
        
        -- Zapis transakcji
        INSERT INTO transactions (
            from_account_id, 
            to_account_id, 
            amount, 
            transaction_type, 
            description, 
            status
        ) VALUES (
            from_account_id, 
            to_account_id, 
            transfer_amount, 
            'transfer', 
            description_text, 
            'completed'
        ) RETURNING id INTO transaction_id;
        
        -- Log sukcesu
        RAISE NOTICE 'Transfer completed successfully. Transaction ID: %', transaction_id;
        
        RETURN TRUE;
        
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            error_message := 'Source account not found or inactive: ' || from_account_id;
            RAISE NOTICE '%', error_message;
            
            -- Log błędu
            INSERT INTO audit_log (table_name, operation, description) 
            VALUES ('accounts', 'transfer_error', error_message);
            
            RETURN FALSE;
            
        WHEN TOO_MANY_ROWS THEN
            error_message := 'Multiple accounts found with ID: ' || from_account_id;
            RAISE NOTICE '%', error_message;
            RETURN FALSE;
            
        WHEN OTHERS THEN
            error_message := 'Transfer failed: ' || SQLERRM;
            RAISE NOTICE '%', error_message;
            
            -- Log błędu
            INSERT INTO audit_log (table_name, operation, description) 
            VALUES ('accounts', 'transfer_error', error_message);
            
            RETURN FALSE;
    END;
END;
$$ LANGUAGE plpgsql;

-- Test funkcji z obsługą błędów
SELECT transfer_money(1, 2, 100.00, 'Test transfer');
SELECT transfer_money(1, 999, 100.00, 'Transfer to non-existent account');
SELECT transfer_money(1, 2, -50.00, 'Negative amount transfer');

-- 4. KURSORY I ITERACJA

-- Funkcja używająca kursorów
CREATE OR REPLACE FUNCTION generate_account_report(
    account_type_filter VARCHAR DEFAULT NULL
) RETURNS TEXT AS $$
DECLARE
    -- Deklaracja kursora
    account_cursor CURSOR(acc_type VARCHAR) FOR 
        SELECT id, account_number, owner_name, balance, account_type
        FROM accounts 
        WHERE (acc_type IS NULL OR account_type = acc_type)
        AND is_active = TRUE
        ORDER BY balance DESC;
    
    -- Alternatywny kursor bez parametrów
    all_accounts_cursor CURSOR FOR 
        SELECT * FROM accounts WHERE is_active = TRUE;
    
    account_rec RECORD;
    report_text TEXT := '';
    total_balance DECIMAL(12,2) := 0;
    account_count INT := 0;
    high_balance_count INT := 0;
BEGIN
    report_text := 'ACCOUNT REPORT' || E'\n';
    report_text := report_text || '==================' || E'\n';
    
    IF account_type_filter IS NOT NULL THEN
        report_text := report_text || 'Filter: ' || account_type_filter || E'\n\n';
    END IF;
    
    -- Otwarcie kursora z parametrem
    OPEN account_cursor(account_type_filter);
    
    LOOP
        -- Pobranie kolejnego rekordu
        FETCH account_cursor INTO account_rec;
        
        -- Wyjście z pętli gdy brak danych
        EXIT WHEN NOT FOUND;
        
        account_count := account_count + 1;
        total_balance := total_balance + account_rec.balance;
        
        -- Sprawdzenie wysokiego salda
        IF account_rec.balance > 3000 THEN
            high_balance_count := high_balance_count + 1;
        END IF;
        
        -- Dodanie do raportu
        report_text := report_text || 
            account_count || '. ' ||
            account_rec.account_number || ' - ' ||
            account_rec.owner_name || 
            ' (Type: ' || account_rec.account_type || ', ' ||
            'Balance: ' || TO_CHAR(account_rec.balance, 'FM999,999.00') || ')';
        
        -- Oznaczenie VIP klientów
        IF account_rec.balance > 5000 THEN
            report_text := report_text || ' [VIP]';
        END IF;
        
        report_text := report_text || E'\n';
    END LOOP;
    
    -- Zamknięcie kursora
    CLOSE account_cursor;
    
    -- Podsumowanie
    report_text := report_text || E'\n' || 'SUMMARY:' || E'\n';
    report_text := report_text || 'Total accounts: ' || account_count || E'\n';
    report_text := report_text || 'Total balance: ' || TO_CHAR(total_balance, 'FM999,999.00') || E'\n';
    report_text := report_text || 'High balance accounts (>3000): ' || high_balance_count || E'\n';
    
    IF account_count > 0 THEN
        report_text := report_text || 'Average balance: ' || 
            TO_CHAR(total_balance / account_count, 'FM999,999.00') || E'\n';
    END IF;
    
    RETURN report_text;
END;
$$ LANGUAGE plpgsql;

-- Test funkcji z kursorami
SELECT generate_account_report();
SELECT generate_account_report('savings');

-- 5. FUNKCJE TRIGGER

-- Funkcja trigger dla audytu
CREATE OR REPLACE FUNCTION accounts_audit_trigger()
RETURNS TRIGGER AS $$
DECLARE
    old_values JSONB;
    new_values JSONB;
    operation_type VARCHAR(10);
BEGIN
    -- Określenie typu operacji
    IF TG_OP = 'DELETE' THEN
        operation_type := 'DELETE';
        old_values := row_to_json(OLD)::JSONB;
        new_values := NULL;
    ELSIF TG_OP = 'UPDATE' THEN
        operation_type := 'UPDATE';
        old_values := row_to_json(OLD)::JSONB;
        new_values := row_to_json(NEW)::JSONB;
    ELSIF TG_OP = 'INSERT' THEN
        operation_type := 'INSERT';
        old_values := NULL;
        new_values := row_to_json(NEW)::JSONB;
    END IF;
    
    -- Zapis do audit log
    INSERT INTO audit_log (
        table_name, 
        operation, 
        old_values, 
        new_values, 
        changed_by
    ) VALUES (
        TG_TABLE_NAME,
        operation_type,
        old_values,
        new_values,
        current_user
    );
    
    -- Zwrócenie odpowiedniego rekordu
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Utworzenie triggera
CREATE TRIGGER accounts_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION accounts_audit_trigger();

-- Funkcja trigger walidacyjna
CREATE OR REPLACE FUNCTION validate_account_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- Walidacja przy INSERT i UPDATE
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        -- Sprawdzenie salda
        IF NEW.balance < 0 THEN
            RAISE EXCEPTION 'Account balance cannot be negative: %', NEW.balance;
        END IF;
        
        -- Sprawdzenie numeru konta
        IF NEW.account_number !~ '^ACC[0-9]{3}$' THEN
            RAISE EXCEPTION 'Invalid account number format: %. Expected: ACC###', NEW.account_number;
        END IF;
        
        -- Sprawdzenie typu konta
        IF NEW.account_type NOT IN ('checking', 'savings', 'business') THEN
            RAISE EXCEPTION 'Invalid account type: %. Allowed: checking, savings, business', NEW.account_type;
        END IF;
        
        -- Automatyczne ustawienie daty utworzenia przy INSERT
        IF TG_OP = 'INSERT' AND NEW.created_at IS NULL THEN
            NEW.created_at := CURRENT_TIMESTAMP;
        END IF;
        
        -- Log zmiany salda przy UPDATE
        IF TG_OP = 'UPDATE' AND OLD.balance != NEW.balance THEN
            RAISE NOTICE 'Balance changed for account %: % -> %', 
                NEW.account_number, OLD.balance, NEW.balance;
        END IF;
    END IF;
    
    -- Zabezpieczenie przed usunięciem kont z transakcjami
    IF TG_OP = 'DELETE' THEN
        IF EXISTS (SELECT 1 FROM transactions WHERE from_account_id = OLD.id OR to_account_id = OLD.id) THEN
            RAISE EXCEPTION 'Cannot delete account % with existing transactions', OLD.account_number;
        END IF;
    END IF;
    
    -- Zwrócenie odpowiedniego rekordu
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Utworzenie triggera walidacyjnego
CREATE TRIGGER validate_account_changes_trigger
    BEFORE INSERT OR UPDATE OR DELETE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION validate_account_changes();

-- 6. ZAAWANSOWANE TECHNIKI

-- Funkcja z dynamicznym SQL
CREATE OR REPLACE FUNCTION dynamic_account_search(
    search_column VARCHAR,
    search_value TEXT,
    limit_count INT DEFAULT 10
) RETURNS TABLE(
    account_id INT,
    account_number VARCHAR(20),
    owner_name VARCHAR(100),
    balance DECIMAL(12,2)
) AS $$
DECLARE
    query_sql TEXT;
    allowed_columns TEXT[] := ARRAY['owner_name', 'account_type', 'account_number'];
BEGIN
    -- Walidacja kolumny (bezpieczeństwo)
    IF NOT (search_column = ANY(allowed_columns)) THEN
        RAISE EXCEPTION 'Invalid search column: %. Allowed: %', 
            search_column, allowed_columns;
    END IF;
    
    -- Budowanie dynamicznego zapytania
    query_sql := 'SELECT id, account_number, owner_name, balance ' ||
                 'FROM accounts ' ||
                 'WHERE ' || quote_ident(search_column) || ' ILIKE $1 ' ||
                 'AND is_active = TRUE ' ||
                 'ORDER BY balance DESC ' ||
                 'LIMIT $2';
    
    -- Wykonanie dynamicznego zapytania
    RETURN QUERY EXECUTE query_sql USING '%' || search_value || '%', limit_count;
END;
$$ LANGUAGE plpgsql;

-- Test dynamicznego SQL
SELECT * FROM dynamic_account_search('owner_name', 'Kowal', 5);
SELECT * FROM dynamic_account_search('account_type', 'savings', 3);

-- 7. FUNKCJE ZWRACAJĄCE REKORDY

-- Funkcja zwracająca pojedynczy rekord
CREATE OR REPLACE FUNCTION get_account_details(account_id_param INT)
RETURNS accounts AS $$
DECLARE
    account_record accounts%ROWTYPE;
BEGIN
    SELECT * INTO account_record
    FROM accounts
    WHERE id = account_id_param;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Account with ID % not found', account_id_param;
    END IF;
    
    RETURN account_record;
END;
$$ LANGUAGE plpgsql;

-- Test funkcji
SELECT * FROM get_account_details(1);

-- 8. TESTING I DEBUGGING

-- Funkcja do testowania z logowaniem
CREATE OR REPLACE FUNCTION test_pl_functions()
RETURNS TEXT AS $$
DECLARE
    test_results TEXT := '';
    test_account_id INT;
    transfer_result BOOLEAN;
BEGIN
    test_results := 'PL/pgSQL FUNCTION TESTS' || E'\n';
    test_results := test_results || '========================' || E'\n\n';
    
    -- Test 1: Tworzenie konta testowego
    BEGIN
        INSERT INTO accounts (account_number, owner_name, balance, account_type)
        VALUES ('TEST001', 'Test User', 1000.00, 'checking')
        RETURNING id INTO test_account_id;
        
        test_results := test_results || '✓ Test 1 PASSED: Account created with ID ' || test_account_id || E'\n';
    EXCEPTION
        WHEN OTHERS THEN
            test_results := test_results || '✗ Test 1 FAILED: ' || SQLERRM || E'\n';
    END;
    
    -- Test 2: Transfer pieniędzy
    BEGIN
        SELECT transfer_money(1, test_account_id, 100.00, 'Test transfer') INTO transfer_result;
        
        IF transfer_result THEN
            test_results := test_results || '✓ Test 2 PASSED: Money transfer successful' || E'\n';
        ELSE
            test_results := test_results || '✗ Test 2 FAILED: Money transfer returned false' || E'\n';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            test_results := test_results || '✗ Test 2 FAILED: ' || SQLERRM || E'\n';
    END;
    
    -- Test 3: Statystyki konta
    BEGIN
        PERFORM calculate_account_stats(test_account_id);
        test_results := test_results || '✓ Test 3 PASSED: Account stats calculated' || E'\n';
    EXCEPTION
        WHEN OTHERS THEN
            test_results := test_results || '✗ Test 3 FAILED: ' || SQLERRM || E'\n';
    END;
    
    -- Cleanup
    BEGIN
        DELETE FROM accounts WHERE id = test_account_id;
        test_results := test_results || '✓ Cleanup: Test account removed' || E'\n';
    EXCEPTION
        WHEN OTHERS THEN
            test_results := test_results || '✗ Cleanup FAILED: ' || SQLERRM || E'\n';
    END;
    
    RETURN test_results;
END;
$$ LANGUAGE plpgsql;

-- Uruchomienie testów
SELECT test_pl_functions();
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Zmienne w DECLARE muszą być zadeklarowane przed BEGIN
2. **UWAGA**: %TYPE i %ROWTYPE kopiują typ w momencie tworzenia funkcji
3. **BŁĄD**: RETURN NEXT używa się w funkcjach TABLE, RETURN w skalarnych
4. **WAŻNE**: Triggery BEFORE mogą modyfikować NEW, AFTER nie
5. **PUŁAPKA**: FOUND jest globalne - sprawdzaj zaraz po SELECT/UPDATE

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **PL/pgSQL language** - język proceduralny PostgreSQL
- **Variables and types** - zmienne i typy danych
- **Control structures** - struktury kontrolne
- **Exception handling** - obsługa wyjątków
- **Cursors** - kursory do iteracji
- **Trigger functions** - funkcje trigger
- **Dynamic SQL** - dynamiczne zapytania SQL
- **Stored procedures** - procedury składowane

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **34-funkcje-uzytkownika** - zaawansowane funkcje
- **35-rules-vs-triggery** - porównanie z RULES
- **01-integralnosc** - triggery do walidacji
- **39-bezpieczenstwo-baz-danych** - bezpieczne funkcje
- **42-optymalizacja-wydajnosci** - wydajność PL/pgSQL