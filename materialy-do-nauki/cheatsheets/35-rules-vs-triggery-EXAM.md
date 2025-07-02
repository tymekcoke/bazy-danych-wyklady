# ⚡ RULES vs TRIGGERY - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Rules i Triggery to mechanizmy automatycznego wykonywania kodu w odpowiedzi na zdarzenia DML:

**RULES:**
- System przepisywania zapytań na poziomie parsera
- Transformują zapytania przed wykonaniem
- Mogą tworzyć dodatkowe akcje (DO ALSO) lub zastępować (DO INSTEAD)
- Używane głównie dla widoków i logowania

**TRIGGERY:**
- Funkcje wykonywane przed/po zdarzeniach DML
- Działają na poziomie wierszy lub całej operacji
- Dostęp do OLD/NEW, możliwość modyfikacji danych
- Bardziej intuicyjne i powszechnie używane

Triggery są preferowane dla logiki biznesowej, Rules dla transformacji zapytań."

## ✍️ CO NAPISAĆ NA KARTCE

```sql
RULES vs TRIGGERY - PORÓWNANIE:

RULES - PRZEPISYWANIE ZAPYTAŃ:
CREATE RULE rule_name AS
ON INSERT/UPDATE/DELETE TO table_name
[WHERE condition]
DO [ALSO | INSTEAD] action;

TRIGGERY - FUNKCJE ZDARZENIOWE:
CREATE TRIGGER trigger_name
BEFORE/AFTER/INSTEAD OF INSERT/UPDATE/DELETE
ON table_name
FOR EACH ROW/STATEMENT
EXECUTE FUNCTION trigger_function();

RÓŻNICE KLUCZOWE:

RULES:
• Działają na poziomie parsera SQL
• Przepisują zapytania przed wykonaniem
• DO ALSO - dodatkowa akcja
• DO INSTEAD - zastąpienie akcji
• Mogą tworzyć nieskończone rekursje
• Trudniejsze w debugowaniu
• Używane głównie dla widoków

TRIGGERY:
• Działają podczas wykonywania
• BEFORE - mogą modyfikować NEW
• AFTER - mogą wykonywać dodatkowe akcje
• INSTEAD OF - tylko dla widoków
• FOR EACH ROW - dla każdego wiersza
• FOR EACH STATEMENT - raz na operację
• Dostęp do OLD, NEW, TG_* zmiennych

PRZYKŁADY ZASTOSOWAŃ:

RULES:
• Updatable views (DO INSTEAD)
• Query logging (DO ALSO)
• Data transformation
• Complex view operations

TRIGGERY:
• Business logic validation
• Auditing and logging
• Automatic field updates
• Cascade operations
• Data synchronization

WYDAJNOŚĆ:
RULES - szybsze dla prostych operacji
TRIGGERY - lepsze dla złożonej logiki

DEBUGGING:
RULES - bardzo trudne do debugowania
TRIGGERY - łatwiejsze, więcej narzędzi
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- KOMPLEKSOWE PORÓWNANIE RULES vs TRIGGERY

-- Przygotowanie tabel testowych
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    salary DECIMAL(10,2),
    department VARCHAR(50),
    hire_date DATE DEFAULT CURRENT_DATE,
    last_modified TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE salary_history (
    id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES employees(id),
    old_salary DECIMAL(10,2),
    new_salary DECIMAL(10,2),
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100),
    change_reason VARCHAR(200)
);

CREATE TABLE employee_audit_log (
    id SERIAL PRIMARY KEY,
    employee_id INT,
    operation VARCHAR(10),
    old_values JSONB,
    new_values JSONB,
    operation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operation_user VARCHAR(100)
);

CREATE TABLE query_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    operation VARCHAR(20),
    query_text TEXT,
    execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_name VARCHAR(100)
);

-- Dane testowe
INSERT INTO employees (name, salary, department) VALUES
('Jan Kowalski', 5000.00, 'IT'),
('Anna Nowak', 6000.00, 'HR'),
('Piotr Wiśniewski', 4500.00, 'IT'),
('Maria Kowalczyk', 7000.00, 'Sales'),
('Tomasz Zieliński', 5500.00, 'IT');

-- 1. RULES - PODSTAWOWE ZASTOSOWANIA

-- Rule dla logowania wszystkich operacji na tabeli employees
CREATE OR REPLACE RULE log_employee_operations AS
ON INSERT TO employees
DO ALSO 
INSERT INTO query_log (table_name, operation, query_text, user_name)
VALUES ('employees', 'INSERT', 
        'INSERT employee: ' || NEW.name || ' salary: ' || NEW.salary,
        current_user);

-- Rule dla aktualizacji czasu ostatniej modyfikacji
CREATE OR REPLACE RULE update_last_modified AS
ON UPDATE TO employees
WHERE OLD.last_modified IS DISTINCT FROM NEW.last_modified
DO ALSO
UPDATE employees SET last_modified = CURRENT_TIMESTAMP
WHERE id = NEW.id;

-- Rule INSTEAD dla "soft delete"
CREATE OR REPLACE RULE soft_delete_employee AS
ON DELETE TO employees
DO INSTEAD
UPDATE employees SET status = 'deleted', last_modified = CURRENT_TIMESTAMP
WHERE id = OLD.id;

-- 2. TRIGGERY - PODSTAWOWE ZASTOSOWANIA

-- Funkcja trigger dla audytu
CREATE OR REPLACE FUNCTION employee_audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO employee_audit_log (
            employee_id, operation, old_values, operation_user
        ) VALUES (
            OLD.id, 'DELETE', row_to_json(OLD)::JSONB, current_user
        );
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO employee_audit_log (
            employee_id, operation, old_values, new_values, operation_user
        ) VALUES (
            NEW.id, 'UPDATE', row_to_json(OLD)::JSONB, 
            row_to_json(NEW)::JSONB, current_user
        );
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO employee_audit_log (
            employee_id, operation, new_values, operation_user
        ) VALUES (
            NEW.id, 'INSERT', row_to_json(NEW)::JSONB, current_user
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger audytu
CREATE TRIGGER employee_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION employee_audit_trigger();

-- Funkcja trigger dla historii wynagrodzeń
CREATE OR REPLACE FUNCTION salary_history_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Tylko przy zmianie wynagrodzenia
    IF TG_OP = 'UPDATE' AND OLD.salary IS DISTINCT FROM NEW.salary THEN
        INSERT INTO salary_history (
            employee_id, old_salary, new_salary, changed_by, change_reason
        ) VALUES (
            NEW.id, OLD.salary, NEW.salary, current_user, 
            'Salary updated from ' || OLD.salary || ' to ' || NEW.salary
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger dla historii wynagrodzeń
CREATE TRIGGER salary_history_trigger
    AFTER UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION salary_history_trigger();

-- Funkcja trigger walidacyjna (BEFORE)
CREATE OR REPLACE FUNCTION validate_employee_data()
RETURNS TRIGGER AS $$
BEGIN
    -- Walidacja wynagrodzenia
    IF NEW.salary <= 0 THEN
        RAISE EXCEPTION 'Salary must be positive, got: %', NEW.salary;
    END IF;
    
    -- Walidacja maksymalnego wynagrodzenia
    IF NEW.salary > 50000 THEN
        RAISE EXCEPTION 'Salary cannot exceed 50000, got: %', NEW.salary;
    END IF;
    
    -- Automatyczne ustawienie daty modyfikacji
    NEW.last_modified := CURRENT_TIMESTAMP;
    
    -- Normalizacja nazwy departamentu
    NEW.department := UPPER(TRIM(NEW.department));
    
    -- Walidacja długości nazwy
    IF LENGTH(NEW.name) < 2 THEN
        RAISE EXCEPTION 'Employee name too short: %', NEW.name;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger walidacyjny
CREATE TRIGGER validate_employee_trigger
    BEFORE INSERT OR UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION validate_employee_data();

-- 3. ZAAWANSOWANE RULES - UPDATABLE VIEWS

-- Widok z Rules dla operacji CRUD
CREATE VIEW employee_view AS
SELECT 
    id,
    name,
    salary,
    department,
    hire_date,
    CASE status 
        WHEN 'active' THEN 'Active'
        WHEN 'deleted' THEN 'Deleted'
        ELSE 'Unknown'
    END as status_display
FROM employees
WHERE status = 'active';

-- Rule dla INSERT na widoku
CREATE OR REPLACE RULE employee_view_insert AS
ON INSERT TO employee_view
DO INSTEAD
INSERT INTO employees (name, salary, department, hire_date, status)
VALUES (NEW.name, NEW.salary, NEW.department, 
        COALESCE(NEW.hire_date, CURRENT_DATE), 'active');

-- Rule dla UPDATE na widoku
CREATE OR REPLACE RULE employee_view_update AS
ON UPDATE TO employee_view
DO INSTEAD
UPDATE employees 
SET name = NEW.name,
    salary = NEW.salary,
    department = NEW.department,
    hire_date = NEW.hire_date
WHERE id = OLD.id AND status = 'active';

-- Rule dla DELETE na widoku (soft delete)
CREATE OR REPLACE RULE employee_view_delete AS
ON DELETE TO employee_view
DO INSTEAD
UPDATE employees 
SET status = 'deleted', last_modified = CURRENT_TIMESTAMP
WHERE id = OLD.id;

-- 4. COMPLEX RULES - CONDITIONAL ACTIONS

-- Rule z warunkiem - tylko dla wysokich wynagrodzeń
CREATE OR REPLACE RULE high_salary_notification AS
ON INSERT TO employees
WHERE NEW.salary > 10000
DO ALSO
INSERT INTO query_log (table_name, operation, query_text, user_name)
VALUES ('employees', 'HIGH_SALARY_INSERT',
        'High salary employee added: ' || NEW.name || ' (' || NEW.salary || ')',
        current_user);

-- Rule dla cascade update departamentów
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    budget DECIMAL(12,2)
);

INSERT INTO departments VALUES (1, 'IT', 100000), (2, 'HR', 50000), (3, 'SALES', 75000);

-- Rule dla synchronizacji przy zmiane nazwy departamentu
CREATE OR REPLACE RULE sync_department_name AS
ON UPDATE TO departments
WHERE OLD.name IS DISTINCT FROM NEW.name
DO ALSO
UPDATE employees SET department = NEW.name WHERE department = OLD.name;

-- 5. ZAAWANSOWANE TRIGGERY

-- Trigger na poziomie STATEMENT
CREATE OR REPLACE FUNCTION employee_statement_trigger()
RETURNS TRIGGER AS $$
DECLARE
    operation_count INT;
BEGIN
    -- Policz ile operacji w tej transakcji
    SELECT COUNT(*) INTO operation_count
    FROM employee_audit_log
    WHERE operation_timestamp > CURRENT_TIMESTAMP - INTERVAL '1 second';
    
    -- Log operacji na poziomie statement
    INSERT INTO query_log (table_name, operation, query_text, user_name)
    VALUES ('employees', 'STATEMENT_' || TG_OP,
            'Statement operation completed. Previous operations in transaction: ' || operation_count,
            current_user);
    
    RETURN NULL; -- AFTER STATEMENT triggers zwracają NULL
END;
$$ LANGUAGE plpgsql;

-- Statement-level trigger
CREATE TRIGGER employee_statement_trigger
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH STATEMENT
    EXECUTE FUNCTION employee_statement_trigger();

-- Conditional trigger (tylko dla określonych kolumn)
CREATE OR REPLACE FUNCTION salary_change_notification()
RETURNS TRIGGER AS $$
BEGIN
    -- Tylko przy istotnej zmianie wynagrodzenia (>10%)
    IF TG_OP = 'UPDATE' AND 
       OLD.salary IS DISTINCT FROM NEW.salary AND
       ABS(NEW.salary - OLD.salary) / OLD.salary > 0.1 THEN
        
        -- Notyfikacja o znaczącej zmianie wynagrodzenia
        RAISE NOTICE 'Significant salary change for %: % -> % (%.1f%%)',
            NEW.name, OLD.salary, NEW.salary,
            ((NEW.salary - OLD.salary) / OLD.salary * 100);
            
        -- Dodatkowe logowanie
        INSERT INTO query_log (table_name, operation, query_text, user_name)
        VALUES ('employees', 'SIGNIFICANT_SALARY_CHANGE',
                format('Employee %s salary changed from %s to %s',
                       NEW.name, OLD.salary, NEW.salary),
                current_user);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger tylko dla zmian wynagrodzenia
CREATE TRIGGER salary_change_notification_trigger
    AFTER UPDATE OF salary ON employees
    FOR EACH ROW
    EXECUTE FUNCTION salary_change_notification();

-- 6. PORÓWNANIE WYDAJNOŚCI

-- Funkcja testująca wydajność Rules vs Triggers
CREATE OR REPLACE FUNCTION performance_test_rules_vs_triggers(
    test_iterations INT DEFAULT 1000
) RETURNS TABLE(
    test_type VARCHAR(50),
    execution_time_ms DECIMAL(10,3),
    operations_per_second DECIMAL(10,2)
) AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    duration DECIMAL;
    i INT;
BEGIN
    -- Test 1: Insert with Rules
    start_time := clock_timestamp();
    FOR i IN 1..test_iterations LOOP
        INSERT INTO employees (name, salary, department)
        VALUES ('Test Rule User ' || i, 5000 + (i % 1000), 'TEST');
        DELETE FROM employees WHERE name = 'Test Rule User ' || i;
    END LOOP;
    end_time := clock_timestamp();
    duration := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
    
    test_type := 'Rules Performance';
    execution_time_ms := duration;
    operations_per_second := test_iterations / (duration / 1000);
    RETURN NEXT;
    
    -- Disabled rules for trigger test
    ALTER TABLE employees DISABLE RULE log_employee_operations;
    ALTER TABLE employees DISABLE RULE update_last_modified;
    
    -- Test 2: Insert with only Triggers
    start_time := clock_timestamp();
    FOR i IN 1..test_iterations LOOP
        INSERT INTO employees (name, salary, department)
        VALUES ('Test Trigger User ' || i, 5000 + (i % 1000), 'TEST');
        DELETE FROM employees WHERE name = 'Test Trigger User ' || i;
    END LOOP;
    end_time := clock_timestamp();
    duration := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
    
    test_type := 'Triggers Performance';
    execution_time_ms := duration;
    operations_per_second := test_iterations / (duration / 1000);
    RETURN NEXT;
    
    -- Re-enable rules
    ALTER TABLE employees ENABLE RULE log_employee_operations;
    ALTER TABLE employees ENABLE RULE update_last_modified;
END;
$$ LANGUAGE plpgsql;

-- 7. DEBUGGING I MONITORING

-- Funkcja do analizy Rules
CREATE OR REPLACE FUNCTION analyze_rules()
RETURNS TABLE(
    rule_name VARCHAR(100),
    table_name VARCHAR(100),
    event_type VARCHAR(20),
    rule_definition TEXT
) AS $$
    SELECT 
        r.rulename::VARCHAR(100),
        c.relname::VARCHAR(100),
        CASE r.ev_type
            WHEN '1' THEN 'SELECT'
            WHEN '2' THEN 'UPDATE'
            WHEN '3' THEN 'INSERT'
            WHEN '4' THEN 'DELETE'
        END::VARCHAR(20),
        pg_get_ruledef(r.oid)
    FROM pg_rewrite r
    JOIN pg_class c ON r.ev_class = c.oid
    WHERE r.rulename != '_RETURN'
    ORDER BY c.relname, r.rulename;
$$ LANGUAGE sql;

-- Funkcja do analizy Triggers
CREATE OR REPLACE FUNCTION analyze_triggers()
RETURNS TABLE(
    trigger_name VARCHAR(100),
    table_name VARCHAR(100),
    event_type VARCHAR(50),
    timing VARCHAR(20),
    function_name VARCHAR(100)
) AS $$
    SELECT 
        t.tgname::VARCHAR(100),
        c.relname::VARCHAR(100),
        CASE t.tgtype & 28
            WHEN 4 THEN 'INSERT'
            WHEN 8 THEN 'DELETE'
            WHEN 16 THEN 'UPDATE'
            WHEN 12 THEN 'INSERT OR DELETE'
            WHEN 20 THEN 'INSERT OR UPDATE'
            WHEN 24 THEN 'DELETE OR UPDATE'
            WHEN 28 THEN 'INSERT OR UPDATE OR DELETE'
        END::VARCHAR(50),
        CASE t.tgtype & 2
            WHEN 0 THEN 'AFTER'
            WHEN 2 THEN 'BEFORE'
        END::VARCHAR(20),
        p.proname::VARCHAR(100)
    FROM pg_trigger t
    JOIN pg_class c ON t.tgrelid = c.oid
    JOIN pg_proc p ON t.tgfoid = p.oid
    WHERE NOT t.tgisinternal
    ORDER BY c.relname, t.tgname;
$$ LANGUAGE sql;

-- 8. TESTOWANIE FUNKCJONALNOŚCI

-- Test Rules
SELECT 'Testing Rules...' as test_phase;

-- Test insert rule
INSERT INTO employees (name, salary, department) 
VALUES ('Rule Test User', 8000.00, 'Testing');

-- Sprawdź log
SELECT * FROM query_log WHERE table_name = 'employees' ORDER BY id DESC LIMIT 3;

-- Test soft delete rule
DELETE FROM employees WHERE name = 'Rule Test User';

-- Sprawdź czy rekord został "soft deleted"
SELECT name, status FROM employees WHERE name = 'Rule Test User';

-- Test Triggers
SELECT 'Testing Triggers...' as test_phase;

-- Test trigger walidacji
BEGIN;
    -- To powinno się nie udać
    INSERT INTO employees (name, salary, department) 
    VALUES ('Bad Salary User', -1000.00, 'Testing');
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Validation trigger worked: %', SQLERRM;
ROLLBACK;

-- Test trigger historii wynagrodzeń
UPDATE employees SET salary = salary + 500 WHERE name = 'Jan Kowalski';

-- Sprawdź historię
SELECT * FROM salary_history ORDER BY id DESC LIMIT 3;

-- Test audytu
SELECT * FROM employee_audit_log ORDER BY id DESC LIMIT 5;

-- 9. CLEAN UP I PERFORMANCE ANALYSIS

-- Porównanie wydajności
SELECT * FROM performance_test_rules_vs_triggers(100);

-- Analiza Rules i Triggers
SELECT * FROM analyze_rules();
SELECT * FROM analyze_triggers();

-- 10. BEST PRACTICES EXAMPLES

-- Rule dla prostej transformacji danych
CREATE OR REPLACE RULE normalize_department_names AS
ON INSERT TO employees
WHERE NEW.department IS NOT NULL
DO ALSO
UPDATE employees 
SET department = CASE 
    WHEN UPPER(NEW.department) IN ('IT', 'INFORMATION TECHNOLOGY') THEN 'IT'
    WHEN UPPER(NEW.department) IN ('HR', 'HUMAN RESOURCES') THEN 'HR'
    WHEN UPPER(NEW.department) IN ('SALES', 'MARKETING') THEN 'SALES'
    ELSE UPPER(NEW.department)
END
WHERE id = NEW.id;

-- Trigger dla kompleksowej logiki biznesowej
CREATE OR REPLACE FUNCTION complex_business_logic()
RETURNS TRIGGER AS $$
DECLARE
    dept_avg_salary DECIMAL(10,2);
    emp_count INT;
BEGIN
    -- Sprawdź średnie wynagrodzenie w departamencie
    SELECT AVG(salary), COUNT(*) 
    INTO dept_avg_salary, emp_count
    FROM employees 
    WHERE department = NEW.department AND status = 'active';
    
    -- Logika biznesowa: ostrzeżenie jeśli wynagrodzenie znacznie powyżej średniej
    IF NEW.salary > dept_avg_salary * 1.5 AND emp_count > 1 THEN
        RAISE NOTICE 'High salary alert: % (%.2f) is %.1f%% above department average (%.2f)',
            NEW.name, NEW.salary,
            ((NEW.salary - dept_avg_salary) / dept_avg_salary * 100),
            dept_avg_salary;
    END IF;
    
    -- Automatyczna korekta jeśli wynagrodzenie jest ekstremalne
    IF NEW.salary > dept_avg_salary * 3 AND emp_count > 2 THEN
        NEW.salary := dept_avg_salary * 2;
        RAISE NOTICE 'Salary automatically adjusted for % from %.2f to %.2f',
            NEW.name, OLD.salary, NEW.salary;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER complex_business_logic_trigger
    BEFORE INSERT OR UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION complex_business_logic();
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Rules działają na poziomie parsera, Triggers podczas wykonywania
2. **UWAGA**: Rules mogą powodować nieskończone rekursje łatwiej niż Triggers
3. **BŁĄD**: INSTEAD OF rules działają tylko z widokami, nie z tabelami
4. **WAŻNE**: Triggers BEFORE mogą modyfikować NEW, AFTER nie
5. **PUŁAPKA**: Rules są trudniejsze do debugowania niż Triggers

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Query rewriting** - przepisywanie zapytań (Rules)
- **Event-driven functions** - funkcje zdarzeniowe (Triggers)
- **DO ALSO/DO INSTEAD** - typy akcji Rules
- **BEFORE/AFTER/INSTEAD OF** - timing Triggers
- **FOR EACH ROW/STATEMENT** - poziom wykonania
- **Updatable views** - widoki z możliwością edycji
- **Business logic** - logika biznesowa
- **Data validation** - walidacja danych

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **33-pl-pgsql-podstawy** - funkcje trigger w PL/pgSQL
- **34-funkcje-uzytkownika** - implementacja funkcji trigger
- **01-integralnosc** - walidacja przez triggers
- **16-widoki** - INSTEAD OF rules/triggers
- **42-optymalizacja-wydajnosci** - wydajność Rules vs Triggers