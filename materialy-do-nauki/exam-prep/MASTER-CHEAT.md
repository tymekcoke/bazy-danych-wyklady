# 🎯 MASTER CHEAT - ŚCIĄGAWKA EGZAMINACYJNA

## 🔥 TOP TEMATY EGZAMINACYJNE

### 1. NORMALIZACJA
- **1NF**: atomowe wartości
- **2NF**: 1NF + eliminacja zależności częściowych  
- **3NF**: 2NF + eliminacja zależności przechodnich
- **BCNF**: każda zależność funkcyjna X→Y gdzie X jest superkluczem

```sql
-- Przykład denormalizacji → normalizacja
-- Źźle: student_id, imie, przedmiot, ocena, prowadzacy_imie
-- DOBRZE: 
-- studenci(id, imie)
-- przedmioty(id, nazwa, prowadzacy_id) 
-- oceny(student_id, przedmiot_id, ocena)
```

### 2. ACID & TRANSAKCJE
- **A**tomicity - wszystko albo nic
- **C**onsistency - spójność danych
- **I**solation - izolacja transakcji
- **D**urability - trwałość zmian

```sql
BEGIN;
UPDATE konto SET saldo = saldo - 100 WHERE id = 1;
UPDATE konto SET saldo = saldo + 100 WHERE id = 2;
COMMIT; -- albo ROLLBACK;
```

### 3. POZIOMY IZOLACJI
1. **READ UNCOMMITTED** - dirty reads
2. **READ COMMITTED** - standard PostgreSQL
3. **REPEATABLE READ** - phantom reads możliwe
4. **SERIALIZABLE** - najwyższy poziom

### 4. KLUCZE
- **PRIMARY KEY**: unikalny + NOT NULL
- **FOREIGN KEY**: referencja do innej tabeli
- **UNIQUE**: unikalny ale NULL dozwolone
- **Klucz kandydujący**: minimalny zbiór jednoznacznie identyfikujący

### 5. RELACJE
- **1:1** - jedna tabela z FK lub łączenie tabel
- **1:N** - FK w tabeli "wiele"
- **M:N** - tabela łącząca z dwoma FK

```sql
-- 1:N
CREATE TABLE orders (id INT, customer_id INT REFERENCES customers(id));

-- M:N  
CREATE TABLE student_course (
    student_id INT REFERENCES students(id),
    course_id INT REFERENCES courses(id),
    PRIMARY KEY (student_id, course_id)
);
```

## 📊 SQL ESSENTIALS

### JOIN'Y
```sql
-- INNER JOIN - tylko pasujące
SELECT * FROM a JOIN b ON a.id = b.a_id;

-- LEFT JOIN - wszystkie z lewej + pasujące z prawej
SELECT * FROM a LEFT JOIN b ON a.id = b.a_id;

-- FULL OUTER JOIN - wszystkie z obu stron
SELECT * FROM a FULL OUTER JOIN b ON a.id = b.a_id;
```

### AGREGACJE
```sql
-- GROUP BY + HAVING
SELECT department, AVG(salary)
FROM employees 
GROUP BY department
HAVING AVG(salary) > 5000;

-- Window functions (bez GROUP BY)
SELECT name, salary, 
       AVG(salary) OVER (PARTITION BY department) as dept_avg
FROM employees;
```

### SUBQUERIES
```sql
-- EXISTS (szybsze niż IN)
SELECT * FROM customers c 
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

-- IN vs NOT IN (uwaga na NULL!)
SELECT * FROM products WHERE category_id IN (1,2,3);
SELECT * FROM products WHERE category_id NOT IN (1,2,3,NULL); -- BŁĄD!
```

## 🔒 BLOKADY & MVCC

### BLOKADY
- **Shared (S)** - czytanie, wiele naraz
- **Exclusive (X)** - pisanie, tylko jedna
- **Update (U)** - przejściowa przed X

### DEADLOCK
```sql
-- Transakcja 1: A→B
-- Transakcja 2: B→A  
-- = deadlock → jedna zostanie anulowana
```

### MVCC
- Każdy wiersz ma **xmin** (utworzenie) i **xmax** (usunięcie)
- Czytanie nie blokuje pisania
- Pisanie nie blokuje czytania

## 🎨 PROJEKTOWANIE

### ER → SQL
```sql
-- ENCJA → TABELA
-- ATRYBUT → KOLUMNA
-- ZWIĄZEK 1:N → FOREIGN KEY
-- ZWIĄZEK M:N → TABELA ŁĄCZĄCA
-- ATRYBUT WIELOWARTOŚCIOWY → OSOBNA TABELA
```

### INTEGRALNOŚĆ
```sql
-- Constraint'y
ALTER TABLE products ADD CONSTRAINT chk_price CHECK (price > 0);
ALTER TABLE orders ADD FOREIGN KEY (customer_id) REFERENCES customers(id);
```

## ⚡ WYDAJNOŚĆ

### INDEKSY
```sql
-- B-tree (domyślny)
CREATE INDEX idx_name ON table(column);

-- Partial index
CREATE INDEX idx_active ON users(email) WHERE active = true;

-- Composite index (kolejność ma znaczenie!)
CREATE INDEX idx_dept_salary ON employees(department, salary);
```

### OPTYMALIZACJA
- **EXPLAIN ANALYZE** - plan wykonania
- **Indeksy na FK** - zawsze!
- **Statystyki aktualne** - ANALYZE
- **WHERE przed JOIN** - filtrowanie wcześnie

## 🛡️ NULL HANDLING

```sql
-- NIGDY nie używaj = NULL
WHERE column IS NULL;      -- ✓
WHERE column IS NOT NULL;  -- ✓
WHERE column = NULL;       -- ✗ zawsze FALSE

-- Funkcje agregujące ignorują NULL (oprócz COUNT(*))
SELECT COUNT(*), COUNT(column); -- różne wyniki!

-- COALESCE dla wartości domyślnych
SELECT COALESCE(nickname, firstname, 'Anonymous') as display_name;
```

## 🔧 ZAAWANSOWANE

### CTE & RECURSIVE
```sql
-- Common Table Expression
WITH high_earners AS (
    SELECT * FROM employees WHERE salary > 50000
)
SELECT department, COUNT(*) FROM high_earners GROUP BY department;

-- Recursive (hierarchie)
WITH RECURSIVE subordinates AS (
    SELECT id, name, manager_id FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, e.manager_id 
    FROM employees e JOIN subordinates s ON e.manager_id = s.id
)
SELECT * FROM subordinates;
```

### TRIGGER vs RULE
- **TRIGGER** - funkcje na zdarzenia (BEFORE/AFTER)
- **RULE** - przepisywanie zapytań (DO INSTEAD/DO ALSO)
- **Preferuj TRIGGER** - łatwiejsze w debug'u

```sql
-- Trigger
CREATE TRIGGER audit_trigger 
    AFTER UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION log_changes();
```

## 📚 KLUCZOWE WZORCE

### UPSERT
```sql
-- PostgreSQL
INSERT INTO users (id, name) VALUES (1, 'Jan')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;
```

### Paginacja
```sql
-- LIMIT + OFFSET (dla małych offset'ów)
SELECT * FROM products ORDER BY id LIMIT 20 OFFSET 100;

-- Cursor-based (dla dużych zbiorów)
SELECT * FROM products WHERE id > 1234 ORDER BY id LIMIT 20;
```

### Conditional Logic
```sql
-- CASE WHEN
SELECT name,
    CASE 
        WHEN salary > 8000 THEN 'Senior'
        WHEN salary > 5000 THEN 'Mid'
        ELSE 'Junior'
    END as level
FROM employees;
```

## ⚠️ NAJCZĘSTSZE PUŁAPKI

1. **NULL w NOT IN** → użyj NOT EXISTS
2. **GROUP BY bez wszystkich nieeagregowanych kolumn** → błąd
3. **= NULL zamiast IS NULL** → zawsze FALSE
4. **Brak indeksów na FK** → wolne JOIN'y
5. **COUNT(kolumna) vs COUNT(*)** → różne wyniki z NULL
6. **HAVING vs WHERE** → HAVING po GROUP BY
7. **Złe sekwencje w transakcjach** → deadlock
8. **VARCHAR bez limitu** → problemy z wydajnością

## 🎯 STRATEGIE EGZAMINACYJNE

### Słowa kluczowe do wplecenia:
- **ACID properties**, **Isolation levels**, **MVCC**
- **Functional dependencies**, **Normal forms**, **BCNF**
- **Foreign key constraints**, **Referential integrity**
- **Query optimization**, **Index performance**
- **Transaction management**, **Deadlock prevention**

### Odpowiedzi ustne (30-60s):
1. **Zdefiniuj problem** (np. "3NF eliminuje zależności przechodnie...")
2. **Podaj przykład** (konkretny case)
3. **Wyjaśnij korzyści/problemy**
4. **Wspomnij alternatywy** (jeśli są)

### Pisanie na kartce:
- **Zawsze rysuj schematy** dla ER/relacji
- **Pokazuj FK** strzałkami
- **Numeruj kroki** dla algorytmów
- **Przykłady SQL** - krótkie ale poprawne

---
*💡 PAMIĘTAJ: Na egzaminie liczy się precyzja, nie długość odpowiedzi!*