# Rules vs Triggery

## Wprowadzenie

**Rules** i **Triggery** to dwa mechanizmy w PostgreSQL służące do **automatycznego wykonywania akcji** w odpowiedzi na operacje na bazie danych. Chociaż mogą wydawać się podobne, różnią się fundamentalnie w sposobie działania i zastosowaniach.

### Kluczowe różnice:
- **Rules**: **przepisywanie zapytań** na poziomie parsera
- **Triggery**: **wykonywanie kodu** na poziomie danych

## Triggery (Wyzwalacze)

### 1. **Definicja i podstawy**

**Trigger** to **procedura**, która jest **automatycznie wykonywana** (wyzwalana) w odpowiedzi na określone wydarzenia w bazie danych.

#### Typy triggerów:
```sql
-- Według momentu wykonania
BEFORE    -- Przed operacją
AFTER     -- Po operacji
INSTEAD OF -- Zamiast operacji (tylko dla widoków)

-- Według operacji
INSERT    -- Wstawianie
UPDATE    -- Aktualizacja
DELETE    -- Usuwanie
TRUNCATE  -- Czyszczenie tabeli (tylko BEFORE/AFTER)

-- Według poziomu
FOR EACH ROW       -- Dla każdego wiersza
FOR EACH STATEMENT -- Dla całej instrukcji (domyślne)
```

### 2. **Składnia tworzenia triggera**

```sql
-- Krok 1: Utwórz funkcję trigger
CREATE OR REPLACE FUNCTION nazwa_funkcji_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Logika triggera
    RETURN NEW;  -- lub OLD, lub NULL
END;
$$;

-- Krok 2: Utwórz trigger
CREATE TRIGGER nazwa_triggera
    BEFORE|AFTER|INSTEAD OF INSERT|UPDATE|DELETE|TRUNCATE
    ON nazwa_tabeli
    [FOR EACH ROW|FOR EACH STATEMENT]
    [WHEN (warunek)]
    EXECUTE FUNCTION nazwa_funkcji_trigger();
```

### 3. **Przykłady podstawowych triggerów**

#### BEFORE INSERT - walidacja i modyfikacja danych:
```sql
-- Funkcja triggera
CREATE OR REPLACE FUNCTION validate_employee_insert()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Walidacja wieku
    IF NEW.birth_date > CURRENT_DATE - INTERVAL '18 years' THEN
        RAISE EXCEPTION 'Pracownik musi mieć co najmniej 18 lat';
    END IF;
    
    -- Automatyczne generowanie email
    IF NEW.email IS NULL THEN
        NEW.email := lower(NEW.first_name || '.' || NEW.last_name || '@company.com');
    END IF;
    
    -- Automatyczne ustawienie daty zatrudnienia
    IF NEW.hire_date IS NULL THEN
        NEW.hire_date := CURRENT_DATE;
    END IF;
    
    -- Normalizacja danych
    NEW.first_name := initcap(trim(NEW.first_name));
    NEW.last_name := initcap(trim(NEW.last_name));
    
    RETURN NEW;
END;
$$;

-- Trigger
CREATE TRIGGER trg_employee_before_insert
    BEFORE INSERT ON employees
    FOR EACH ROW
    EXECUTE FUNCTION validate_employee_insert();
```

#### AFTER UPDATE - audyt zmian:
```sql
-- Tabela audytu
CREATE TABLE employee_audit (
    audit_id SERIAL PRIMARY KEY,
    employee_id INTEGER,
    field_name VARCHAR(50),
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Funkcja audit triggera
CREATE OR REPLACE FUNCTION audit_employee_changes()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Sprawdź zmiany w poszczególnych polach
    IF OLD.salary IS DISTINCT FROM NEW.salary THEN
        INSERT INTO employee_audit (employee_id, field_name, old_value, new_value, changed_by)
        VALUES (NEW.employee_id, 'salary', OLD.salary::TEXT, NEW.salary::TEXT, current_user);
    END IF;
    
    IF OLD.department_id IS DISTINCT FROM NEW.department_id THEN
        INSERT INTO employee_audit (employee_id, field_name, old_value, new_value, changed_by)
        VALUES (NEW.employee_id, 'department_id', OLD.department_id::TEXT, NEW.department_id::TEXT, current_user);
    END IF;
    
    IF OLD.position IS DISTINCT FROM NEW.position THEN
        INSERT INTO employee_audit (employee_id, field_name, old_value, new_value, changed_by)
        VALUES (NEW.employee_id, 'position', OLD.position, NEW.position, current_user);
    END IF;
    
    RETURN NEW;
END;
$$;

-- Trigger
CREATE TRIGGER trg_employee_audit
    AFTER UPDATE ON employees
    FOR EACH ROW
    WHEN (OLD.* IS DISTINCT FROM NEW.*)  -- Tylko gdy coś się zmieniło
    EXECUTE FUNCTION audit_employee_changes();
```

#### BEFORE DELETE - soft delete:
```sql
-- Dodaj kolumnę deleted_at do tabeli
ALTER TABLE employees ADD COLUMN deleted_at TIMESTAMP;

-- Funkcja soft delete
CREATE OR REPLACE FUNCTION soft_delete_employee()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Zamiast usuwać, oznacz jako usunięty
    UPDATE employees 
    SET deleted_at = CURRENT_TIMESTAMP
    WHERE employee_id = OLD.employee_id;
    
    -- Log operacji
    INSERT INTO employee_audit (employee_id, field_name, old_value, new_value, changed_by)
    VALUES (OLD.employee_id, 'deleted_at', NULL, CURRENT_TIMESTAMP::TEXT, current_user);
    
    -- Zwróć NULL aby zatrzymać faktyczne DELETE
    RETURN NULL;
END;
$$;

-- Trigger
CREATE TRIGGER trg_employee_soft_delete
    BEFORE DELETE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION soft_delete_employee();
```

### 4. **Zaawansowane triggery**

#### Trigger z warunkami:
```sql
-- Trigger tylko dla wysokich pensji
CREATE TRIGGER trg_high_salary_audit
    AFTER UPDATE OF salary ON employees
    FOR EACH ROW
    WHEN (NEW.salary > 100000)  -- Tylko dla wysokich pensji
    EXECUTE FUNCTION audit_high_salary_changes();

-- Trigger dla określonych działów
CREATE TRIGGER trg_it_department_changes
    AFTER INSERT OR UPDATE ON employees
    FOR EACH ROW
    WHEN (NEW.department_id = (SELECT id FROM departments WHERE name = 'IT'))
    EXECUTE FUNCTION handle_it_employee_changes();
```

#### Trigger statement-level:
```sql
-- Funkcja dla całej operacji
CREATE OR REPLACE FUNCTION log_bulk_employee_operation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO operation_log (table_name, operation_type, affected_rows, performed_by, performed_at)
    VALUES ('employees', TG_OP, TG_NARGS, current_user, CURRENT_TIMESTAMP);
    
    RETURN COALESCE(NEW, OLD);
END;
$$;

-- Statement-level trigger
CREATE TRIGGER trg_employee_bulk_log
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH STATEMENT
    EXECUTE FUNCTION log_bulk_employee_operation();
```

#### Cascading updates z triggerem:
```sql
-- Automatyczna aktualizacja powiązanych tabel
CREATE OR REPLACE FUNCTION update_department_statistics()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    dept_id INTEGER;
    emp_count INTEGER;
    avg_salary NUMERIC;
BEGIN
    -- Określ który dział zaktualizować
    dept_id := COALESCE(NEW.department_id, OLD.department_id);
    
    -- Oblicz statystyki
    SELECT 
        COUNT(*),
        AVG(salary)
    INTO 
        emp_count,
        avg_salary
    FROM employees
    WHERE department_id = dept_id 
      AND deleted_at IS NULL;
    
    -- Aktualizuj statystyki działu
    UPDATE departments
    SET 
        employee_count = emp_count,
        average_salary = avg_salary,
        last_updated = CURRENT_TIMESTAMP
    WHERE department_id = dept_id;
    
    RETURN COALESCE(NEW, OLD);
END;
$$;

-- Trigger na różne operacje
CREATE TRIGGER trg_update_dept_stats
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION update_department_statistics();
```

## Rules (Reguły)

### 1. **Definicja i podstawy**

**Rule** to mechanizm **przepisywania zapytań** w PostgreSQL, który pozwala na **modyfikację lub zastąpienie** operacji SQL podczas parsowania.

#### Charakterystyka rules:
- **Query rewriting** - przepisywanie na poziomie parsera
- **Makro-podobne** - rozwijanie definicji
- **Zero overhead** - brak dodatkowego kodu wykonywania
- **Głównie dla widoków** - modyfikowalne widoki

### 2. **Składnia tworzenia rule**

```sql
CREATE [OR REPLACE] RULE nazwa_rule AS
    ON operacja TO nazwa_tabeli/widoku
    [WHERE warunek]
    DO [ALSO | INSTEAD] [NOTHING | zapytanie | (zapytania)];
```

### 3. **Rules dla widoków - modyfikowalne widoki**

#### Prosty widok z rules:
```sql
-- Widok na aktywnych pracowników
CREATE VIEW active_employees AS
SELECT employee_id, first_name, last_name, email, salary, department_id
FROM employees
WHERE deleted_at IS NULL;

-- Rule dla INSERT
CREATE OR REPLACE RULE active_employees_insert AS
    ON INSERT TO active_employees
    DO INSTEAD
        INSERT INTO employees (first_name, last_name, email, salary, department_id)
        VALUES (NEW.first_name, NEW.last_name, NEW.email, NEW.salary, NEW.department_id);

-- Rule dla UPDATE
CREATE OR REPLACE RULE active_employees_update AS
    ON UPDATE TO active_employees
    DO INSTEAD
        UPDATE employees
        SET first_name = NEW.first_name,
            last_name = NEW.last_name,
            email = NEW.email,
            salary = NEW.salary,
            department_id = NEW.department_id
        WHERE employee_id = OLD.employee_id
          AND deleted_at IS NULL;

-- Rule dla DELETE (soft delete)
CREATE OR REPLACE RULE active_employees_delete AS
    ON DELETE TO active_employees
    DO INSTEAD
        UPDATE employees
        SET deleted_at = CURRENT_TIMESTAMP
        WHERE employee_id = OLD.employee_id;
```

#### Złożony przykład - widok z JOIN:
```sql
-- Widok łączący dane
CREATE VIEW employee_details AS
SELECT 
    e.employee_id,
    e.first_name,
    e.last_name,
    e.email,
    e.salary,
    d.department_name,
    d.department_id
FROM employees e
JOIN departments d ON e.department_id = d.department_id
WHERE e.deleted_at IS NULL;

-- Rule dla UPDATE (tylko kolumny z tabeli employees)
CREATE OR REPLACE RULE employee_details_update AS
    ON UPDATE TO employee_details
    WHERE OLD.employee_id = NEW.employee_id  -- Nie można zmieniać ID
    DO INSTEAD (
        UPDATE employees
        SET first_name = NEW.first_name,
            last_name = NEW.last_name,
            email = NEW.email,
            salary = NEW.salary,
            department_id = NEW.department_id
        WHERE employee_id = OLD.employee_id;
        
        -- Aktualizuj nazwę działu jeśli się zmieniła
        UPDATE departments
        SET department_name = NEW.department_name
        WHERE department_id = NEW.department_id
          AND department_name != NEW.department_name;
    );
```

### 4. **Rules dla logowania i audytu**

```sql
-- Tabela logów
CREATE TABLE query_log (
    log_id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    operation VARCHAR(10),
    query_text TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_by VARCHAR(100) DEFAULT current_user
);

-- Rule logujące wszystkie operacje
CREATE OR REPLACE RULE employees_log_insert AS
    ON INSERT TO employees
    DO ALSO
        INSERT INTO query_log (table_name, operation, query_text)
        VALUES ('employees', 'INSERT', 
                'INSERT INTO employees VALUES(' || NEW.employee_id || ',...)');

CREATE OR REPLACE RULE employees_log_update AS
    ON UPDATE TO employees
    DO ALSO
        INSERT INTO query_log (table_name, operation, query_text)
        VALUES ('employees', 'UPDATE',
                'UPDATE employees SET ... WHERE employee_id = ' || OLD.employee_id);

CREATE OR REPLACE RULE employees_log_delete AS
    ON DELETE TO employees
    DO ALSO
        INSERT INTO query_log (table_name, operation, query_text)
        VALUES ('employees', 'DELETE',
                'DELETE FROM employees WHERE employee_id = ' || OLD.employee_id);
```

## Porównanie Rules vs Triggery

### 1. **Mechanizm działania**

#### Triggery:
```sql
-- TRIGGER: Wykonywany na poziomie danych
-- Rzeczywista sekwencja:
-- 1. Parser analizuje SQL
-- 2. Planner tworzy plan wykonania
-- 3. Executor wykonuje plan
-- 4. Podczas wykonania wyzwalany jest trigger
-- 5. Trigger wykonuje funkcję PL/pgSQL

CREATE TRIGGER przykład_trigger
    BEFORE INSERT ON tabela
    FOR EACH ROW
    EXECUTE FUNCTION funkcja_trigger();  -- Kod się wykonuje
```

#### Rules:
```sql
-- RULE: Przepisywanie na poziomie parsera
-- Rzeczywista sekwencja:
-- 1. Parser analizuje SQL
-- 2. Rule przepisuje zapytanie (makro-rozwinięcie)
-- 3. Planner tworzy plan dla przepisanego zapytania
-- 4. Executor wykonuje przepisany plan

CREATE RULE przykład_rule AS
    ON INSERT TO tabela
    DO INSTEAD INSERT INTO inna_tabela VALUES (NEW.*);  -- Zapytanie się przepisuje
```

### 2. **Wydajność**

```sql
-- Test wydajności - INSERT 1000 rekordów

-- Z TRIGGER:
-- - 1000 wywołań funkcji trigger
-- - Overhead wykonywania PL/pgSQL
-- - Możliwość optymalizacji przez cache

-- Z RULE:
-- - Jedno przepisane zapytanie
-- - Brak overhead'u wykonywania
-- - Optymalizacja na poziomie planera
```

### 3. **Możliwości i ograniczenia**

#### Triggery - zalety:
```sql
-- ✅ Pełna kontrola logiki
CREATE OR REPLACE FUNCTION complex_trigger()
RETURNS TRIGGER AS $$
DECLARE
    external_api_result TEXT;
    calculated_value NUMERIC;
BEGIN
    -- Złożone obliczenia
    calculated_value := calculate_complex_formula(NEW.input_data);
    
    -- Wywołanie zewnętrznego API
    external_api_result := call_external_service(NEW.customer_id);
    
    -- Warunkowa logika
    IF external_api_result = 'approved' THEN
        NEW.status := 'active';
    ELSE
        RAISE EXCEPTION 'Customer not approved';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ✅ Dostęp do zmiennych sesji
-- ✅ Obsługa wyjątków
-- ✅ Dynamiczne zapytania
-- ✅ Loops i złożona logika
```

#### Rules - zalety:
```sql
-- ✅ Bardzo wysoka wydajność
CREATE RULE fast_insert AS
    ON INSERT TO view_table
    DO INSTEAD
        INSERT INTO real_table (col1, col2, col3)
        VALUES (NEW.col1, NEW.col2, calculate_col3(NEW.col1));

-- ✅ Automatyczne przepisywanie
-- ✅ Integracja z optymalizatorem
-- ✅ Brak overhead'u runtime
```

#### Ograniczenia Rules:
```sql
-- ❌ Ograniczona logika - tylko SQL
-- ❌ Brak dostępu do zmiennych sesji
-- ❌ Brak obsługi wyjątków
-- ❌ Problemy z wartościami volatile (CURRENT_TIMESTAMP, RANDOM())

-- Przykład problemu:
CREATE RULE problematic_rule AS
    ON INSERT TO audit_table
    DO ALSO
        INSERT INTO log_table (message, timestamp)
        VALUES ('Record inserted', CURRENT_TIMESTAMP);

-- Problem: CURRENT_TIMESTAMP może być różny
-- dla każdego przepisanego zapytania!
```

### 4. **Przypadki użycia**

#### Kiedy używać TRIGGERÓW:
```sql
-- 1. Złożona logika biznesowa
CREATE FUNCTION validate_business_rules() RETURNS TRIGGER AS $$
BEGIN
    -- Złożone walidacje
    -- Wywołania funkcji
    -- Warunkowa logika
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Audyt z metadanymi
CREATE FUNCTION audit_with_context() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (
        table_name, operation, old_values, new_values,
        user_session, application_name, client_ip
    ) VALUES (
        TG_TABLE_NAME, TG_OP, to_json(OLD), to_json(NEW),
        current_setting('myapp.session_id'),
        current_setting('application_name'),
        inet_client_addr()
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. Integracja z zewnętrznymi systemami
-- 4. Obsługa błędów i rollback
-- 5. Logika wymagająca zmiennych i obliczeń
```

#### Kiedy używać RULES:
```sql
-- 1. Modyfikowalne widoki
CREATE VIEW simple_employee_view AS
SELECT id, name, email FROM employees WHERE active = true;

CREATE RULE employee_view_insert AS
    ON INSERT TO simple_employee_view
    DO INSTEAD
        INSERT INTO employees (name, email, active)
        VALUES (NEW.name, NEW.email, true);

-- 2. Proste przekierowania
CREATE RULE archive_old_data AS
    ON INSERT TO current_data
    WHERE NEW.created_date < CURRENT_DATE - INTERVAL '1 year'
    DO INSTEAD
        INSERT INTO archived_data VALUES (NEW.*);

-- 3. Automatyczne partycjonowanie (historyczne)
-- 4. Proste logowanie bez metadanych
-- 5. Wysokowydajne operacje bulk
```

## Praktyczne przykłady

### 1. **System audytu porównanie**

#### Implementacja z triggerem:
```sql
CREATE OR REPLACE FUNCTION comprehensive_audit()
RETURNS TRIGGER AS $$
DECLARE
    audit_data JSONB;
    change_summary TEXT;
BEGIN
    -- Przygotuj dane audytu
    audit_data := jsonb_build_object(
        'table_name', TG_TABLE_NAME,
        'operation', TG_OP,
        'timestamp', CURRENT_TIMESTAMP,
        'user', current_user,
        'session_id', current_setting('myapp.session_id', true),
        'old_values', to_jsonb(OLD),
        'new_values', to_jsonb(NEW)
    );
    
    -- Przygotuj podsumowanie zmian
    IF TG_OP = 'UPDATE' THEN
        change_summary := generate_change_summary(to_jsonb(OLD), to_jsonb(NEW));
    ELSE
        change_summary := TG_OP;
    END IF;
    
    -- Zapisz audit
    INSERT INTO comprehensive_audit_log (audit_data, change_summary)
    VALUES (audit_data, change_summary);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
```

#### Implementacja z rule:
```sql
CREATE RULE simple_audit_insert AS
    ON INSERT TO monitored_table
    DO ALSO
        INSERT INTO simple_audit_log (table_name, operation, record_id, timestamp)
        VALUES ('monitored_table', 'INSERT', NEW.id, CURRENT_TIMESTAMP);

CREATE RULE simple_audit_update AS
    ON UPDATE TO monitored_table
    DO ALSO
        INSERT INTO simple_audit_log (table_name, operation, record_id, timestamp)
        VALUES ('monitored_table', 'UPDATE', NEW.id, CURRENT_TIMESTAMP);
```

### 2. **Automatyczne timestamping**

#### Z triggerem:
```sql
CREATE OR REPLACE FUNCTION update_timestamps()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    
    IF TG_OP = 'INSERT' THEN
        NEW.created_at := CURRENT_TIMESTAMP;
        NEW.created_by := current_user;
    END IF;
    
    NEW.updated_by := current_user;
    NEW.version := COALESCE(OLD.version, 0) + 1;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_timestamps
    BEFORE INSERT OR UPDATE ON versioned_table
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamps();
```

#### Z rule (problematyczne):
```sql
-- ❌ PROBLEM: CURRENT_TIMESTAMP może być niespójny
CREATE RULE timestamp_insert AS
    ON INSERT TO timestamped_table
    WHERE NEW.created_at IS NULL
    DO INSTEAD
        INSERT INTO timestamped_table (data, created_at, updated_at)
        VALUES (NEW.data, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**

#### 1. **Wybór odpowiedniego mechanizmu**
```sql
-- TRIGGER dla złożonej logiki
CREATE TRIGGER complex_business_logic
    BEFORE INSERT OR UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION validate_and_process_order();

-- RULE dla prostego przekierowania
CREATE RULE partition_data AS
    ON INSERT TO main_table
    WHERE NEW.date >= '2024-01-01'
    DO INSTEAD
        INSERT INTO partition_2024 VALUES (NEW.*);
```

#### 2. **Optymalizacja triggerów**
```sql
-- Używaj warunków WHEN
CREATE TRIGGER optimized_trigger
    AFTER UPDATE OF salary, department_id ON employees  -- Tylko określone kolumny
    FOR EACH ROW
    WHEN (OLD.salary != NEW.salary OR OLD.department_id != NEW.department_id)  -- Tylko rzeczywiste zmiany
    EXECUTE FUNCTION process_employee_changes();

-- Batch processing w statement-level triggers
CREATE TRIGGER batch_process_trigger
    AFTER INSERT ON bulk_data_table
    FOR EACH STATEMENT
    EXECUTE FUNCTION process_bulk_insert();
```

#### 3. **Bezpieczeństwo**
```sql
-- Walidacja w triggerach
CREATE OR REPLACE FUNCTION secure_employee_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Sprawdź uprawnienia
    IF NOT has_table_privilege(current_user, 'employees', 'UPDATE') THEN
        RAISE EXCEPTION 'Insufficient privileges';
    END IF;
    
    -- Waliduj dane
    IF NEW.salary < 0 THEN
        RAISE EXCEPTION 'Salary cannot be negative';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### ❌ **Złe praktyki:**

```sql
-- ❌ Nieskończone loops w triggerach
CREATE FUNCTION bad_trigger() RETURNS TRIGGER AS $$
BEGIN
    UPDATE same_table SET col = col + 1 WHERE id = NEW.id;  -- Nieskończona pętla!
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ❌ Złożona logika w rules
CREATE RULE bad_rule AS
    ON INSERT TO table1
    DO ALSO (
        -- Zbyt skomplikowane dla rule
        UPDATE table2 SET count = count + 1;
        UPDATE table3 SET sum = sum + NEW.amount;
        INSERT INTO log_table VALUES (...);
    );

-- ❌ Ignorowanie błędów
CREATE FUNCTION bad_error_handling() RETURNS TRIGGER AS $$
BEGIN
    BEGIN
        -- Ryzykowna operacja
        INSERT INTO external_table VALUES (NEW.*);
    EXCEPTION WHEN OTHERS THEN
        -- Ignorowanie błędów - bardzo złe!
        NULL;
    END;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

## Pułapki egzaminacyjne

### 1. **Różnice mechanizmów**
```
TRIGGER: Wykonuje kod na poziomie runtime
RULE: Przepisuje zapytanie na poziomie parser

TRIGGER: Overhead wykonywania funkcji
RULE: Zero runtime overhead, ale ograniczona funkcjonalność
```

### 2. **Wartości OLD i NEW**
```
TRIGGER:
- INSERT: NEW dostępne, OLD = NULL
- UPDATE: NEW i OLD dostępne
- DELETE: OLD dostępne, NEW = NULL

RULE:
- Podobnie jak TRIGGER, ale w kontekście przepisywania zapytań
```

### 3. **RETURN values w triggerach**
```
BEFORE TRIGGER:
- RETURN NEW: kontynuuj z nowymi wartościami
- RETURN OLD: kontynuuj ze starymi wartościami
- RETURN NULL: przerwij operację

AFTER TRIGGER:
- Wartość RETURN ignorowana
```

### 4. **Wydajność**
```
RULE: Szybsze dla prostych operacji (przepisywanie zapytań)
TRIGGER: Wolniejsze, ale bardziej elastyczne

FOR EACH ROW: Wykonywany dla każdego wiersza
FOR EACH STATEMENT: Wykonywany raz na operację
```