# 💾 SQL CHEATSHEET - SKŁADNIA W PIGUŁCE

## 📊 DDL - DATA DEFINITION LANGUAGE

### CREATE TABLE
```sql
CREATE TABLE nazwa (
    id SERIAL PRIMARY KEY,
    nazwa VARCHAR(100) NOT NULL,
    wiek INTEGER CHECK (wiek > 0),
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### ALTER TABLE
```sql
-- Dodanie kolumny
ALTER TABLE nazwa ADD COLUMN nowa_kolumna VARCHAR(50);

-- Modyfikacja kolumny
ALTER TABLE nazwa ALTER COLUMN kolumna SET NOT NULL;
ALTER TABLE nazwa ALTER COLUMN kolumna TYPE TEXT;

-- Dodanie constraint
ALTER TABLE nazwa ADD CONSTRAINT nazwa_chk CHECK (warunek);
ALTER TABLE nazwa ADD FOREIGN KEY (id) REFERENCES inna_tabela(id);

-- Usunięcie
ALTER TABLE nazwa DROP COLUMN kolumna;
ALTER TABLE nazwa DROP CONSTRAINT nazwa_constraint;
```

### CONSTRAINTS
```sql
-- Primary Key
PRIMARY KEY (kolumna)
PRIMARY KEY (kol1, kol2)  -- klucz złożony

-- Foreign Key  
FOREIGN KEY (kolumna) REFERENCES tabela(kolumna)
FOREIGN KEY (kol) REFERENCES tab(kol) ON DELETE CASCADE
FOREIGN KEY (kol) REFERENCES tab(kol) ON UPDATE SET NULL

-- Other
NOT NULL
UNIQUE
UNIQUE (kol1, kol2)  -- unikalność złożona
CHECK (warunek)
DEFAULT wartość
```

### INDEXES
```sql
-- Podstawowy
CREATE INDEX idx_nazwa ON tabela(kolumna);

-- Unique
CREATE UNIQUE INDEX idx_nazwa ON tabela(kolumna);

-- Złożony
CREATE INDEX idx_nazwa ON tabela(kol1, kol2);

-- Partial
CREATE INDEX idx_nazwa ON tabela(kolumna) WHERE warunek;

-- Functional
CREATE INDEX idx_nazwa ON tabela(LOWER(kolumna));
```

## 🔍 DQL - DATA QUERY LANGUAGE

### SELECT - PODSTAWY
```sql
SELECT kolumna1, kolumna2, *
FROM tabela
WHERE warunek
ORDER BY kolumna ASC/DESC
LIMIT liczba OFFSET liczba;
```

### WHERE - WARUNKI
```sql
-- Porównania
WHERE kol = wartość
WHERE kol != wartość / kol <> wartość
WHERE kol > wartość
WHERE kol BETWEEN val1 AND val2
WHERE kol IN (val1, val2, val3)
WHERE kol NOT IN (val1, val2)

-- Pattern matching
WHERE kol LIKE 'wzorzec%'     -- zaczyna się od
WHERE kol LIKE '%wzorzec'     -- kończy się na
WHERE kol LIKE '%wzorzec%'    -- zawiera
WHERE kol ILIKE 'WZORZEC'     -- case insensitive (PostgreSQL)

-- NULL
WHERE kol IS NULL
WHERE kol IS NOT NULL

-- Logiczne
WHERE warunek1 AND warunek2
WHERE warunek1 OR warunek2
WHERE NOT warunek
```

### JOIN'Y
```sql
-- INNER JOIN (tylko pasujące)
SELECT *
FROM a INNER JOIN b ON a.id = b.a_id;

-- LEFT JOIN (wszystkie z a + pasujące z b)
SELECT *
FROM a LEFT JOIN b ON a.id = b.a_id;

-- RIGHT JOIN (wszystkie z b + pasujące z a)
SELECT *
FROM a RIGHT JOIN b ON a.id = b.a_id;

-- FULL OUTER JOIN (wszystkie z obu)
SELECT *
FROM a FULL OUTER JOIN b ON a.id = b.a_id;

-- CROSS JOIN (iloczyn kartezjański)
SELECT *
FROM a CROSS JOIN b;

-- Multiple JOINs
SELECT *
FROM a
JOIN b ON a.id = b.a_id
JOIN c ON b.id = c.b_id
WHERE warunek;
```

### SUBQUERIES
```sql
-- Skalarne
SELECT *, (SELECT COUNT(*) FROM orders WHERE customer_id = c.id) as order_count
FROM customers c;

-- IN
SELECT * FROM products WHERE category_id IN (
    SELECT id FROM categories WHERE name = 'Electronics'
);

-- EXISTS
SELECT * FROM customers c WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id
);

-- ANY/ALL
SELECT * FROM products WHERE price > ANY (
    SELECT price FROM products WHERE category = 'Books'
);
```

### AGREGACJE
```sql
-- Podstawowe funkcje
SELECT 
    COUNT(*),           -- wszystkie wiersze
    COUNT(kolumna),     -- nie-NULL w kolumnie
    COUNT(DISTINCT kol), -- unikalne nie-NULL
    SUM(kolumna),
    AVG(kolumna),
    MIN(kolumna),
    MAX(kolumna)
FROM tabela;

-- GROUP BY
SELECT kolumna, COUNT(*)
FROM tabela
GROUP BY kolumna
HAVING COUNT(*) > 5;

-- Zaawansowane grupowanie
GROUP BY ROLLUP(kol1, kol2)     -- hierarchiczne
GROUP BY CUBE(kol1, kol2)       -- wszystkie kombinacje
GROUP BY GROUPING SETS((kol1), (kol2), ())  -- wybrane kombinacje
```

### WINDOW FUNCTIONS
```sql
-- Ranking
SELECT 
    kolumna,
    ROW_NUMBER() OVER (PARTITION BY grupa ORDER BY kolumna) as rn,
    RANK() OVER (ORDER BY kolumna DESC) as rank,
    DENSE_RANK() OVER (ORDER BY kolumna) as dense_rank
FROM tabela;

-- Aggregate windows
SELECT 
    kolumna,
    SUM(wartość) OVER (PARTITION BY grupa) as group_sum,
    AVG(wartość) OVER (ORDER BY data ROWS 2 PRECEDING) as moving_avg
FROM tabela;

-- LAG/LEAD
SELECT 
    kolumna,
    LAG(kolumna, 1) OVER (ORDER BY data) as previous_value,
    LEAD(kolumna, 1) OVER (ORDER BY data) as next_value
FROM tabela;
```

### CTE (Common Table Expressions)
```sql
-- Podstawowe CTE
WITH cte_name AS (
    SELECT kolumna FROM tabela WHERE warunek
)
SELECT * FROM cte_name;

-- Multiple CTE
WITH 
    cte1 AS (SELECT ...),
    cte2 AS (SELECT ... FROM cte1)
SELECT * FROM cte2;

-- Recursive CTE
WITH RECURSIVE hierarchy AS (
    -- Base case
    SELECT id, parent_id, name, 0 as level
    FROM categories WHERE parent_id IS NULL
    
    UNION ALL
    
    -- Recursive case
    SELECT c.id, c.parent_id, c.name, h.level + 1
    FROM categories c
    JOIN hierarchy h ON c.parent_id = h.id
)
SELECT * FROM hierarchy;
```

## ✏️ DML - DATA MANIPULATION LANGUAGE

### INSERT
```sql
-- Podstawowy
INSERT INTO tabela (kol1, kol2) VALUES (val1, val2);

-- Multiple rows
INSERT INTO tabela (kol1, kol2) VALUES 
    (val1, val2),
    (val3, val4),
    (val5, val6);

-- Z SELECT
INSERT INTO tabela (kol1, kol2)
SELECT kol1, kol2 FROM inna_tabela WHERE warunek;

-- UPSERT (PostgreSQL)
INSERT INTO tabela (id, nazwa) VALUES (1, 'test')
ON CONFLICT (id) DO UPDATE SET nazwa = EXCLUDED.nazwa;

-- UPSERT z warunkiem
INSERT INTO tabela (id, nazwa) VALUES (1, 'test')
ON CONFLICT (id) DO UPDATE SET 
    nazwa = EXCLUDED.nazwa
WHERE tabela.updated_at < EXCLUDED.updated_at;
```

### UPDATE
```sql
-- Podstawowy
UPDATE tabela SET kolumna = wartość WHERE warunek;

-- Multiple columns
UPDATE tabela SET 
    kol1 = val1,
    kol2 = val2,
    updated_at = CURRENT_TIMESTAMP
WHERE warunek;

-- Z JOIN (PostgreSQL)
UPDATE tabela1 SET kolumna = t2.wartość
FROM tabela2 t2
WHERE tabela1.id = t2.ref_id;

-- Z subquery
UPDATE products SET price = price * 1.1
WHERE category_id IN (SELECT id FROM categories WHERE name = 'Electronics');
```

### DELETE
```sql
-- Podstawowy
DELETE FROM tabela WHERE warunek;

-- Z JOIN (PostgreSQL)
DELETE FROM tabela1
USING tabela2
WHERE tabela1.id = tabela2.ref_id AND tabela2.status = 'inactive';

-- Z subquery
DELETE FROM orders 
WHERE customer_id IN (
    SELECT id FROM customers WHERE status = 'deleted'
);
```

## 🔄 TRANSACTIONS

### Podstawy
```sql
BEGIN;                    -- Start transaction
-- SQL operations here
COMMIT;                   -- Save changes

BEGIN;
-- SQL operations here  
ROLLBACK;                 -- Cancel changes
```

### Savepoints
```sql
BEGIN;
INSERT INTO tabela VALUES (...);
SAVEPOINT save1;
UPDATE tabela SET ...;
ROLLBACK TO save1;        -- Rollback to savepoint
COMMIT;
```

### Isolation Levels
```sql
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;      -- PostgreSQL default
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

## 🛠️ UTILITIES

### CASE WHEN
```sql
SELECT 
    nazwa,
    CASE 
        WHEN wiek < 18 THEN 'Minor'
        WHEN wiek < 65 THEN 'Adult'
        ELSE 'Senior'
    END as category
FROM osoby;

-- W WHERE
WHERE CASE WHEN warunek THEN 'A' ELSE 'B' END = 'A'
```

### NULL Handling
```sql
-- Sprawdzanie
WHERE kolumna IS NULL
WHERE kolumna IS NOT NULL

-- Zamiana
COALESCE(kol1, kol2, 'default')    -- pierwszy NOT NULL
NULLIF(kol1, kol2)                 -- NULL jeśli równe
CASE WHEN kol IS NULL THEN 'empty' ELSE kol END
```

### String Functions
```sql
CONCAT(str1, str2)
UPPER(string) / LOWER(string)
LENGTH(string)
SUBSTRING(string FROM start FOR length)
TRIM(string)
REPLACE(string, from, to)
```

### Date/Time
```sql
CURRENT_DATE
CURRENT_TIME  
CURRENT_TIMESTAMP
NOW()

EXTRACT(YEAR FROM date)
EXTRACT(MONTH FROM date)
DATE_TRUNC('month', timestamp)

date + INTERVAL '1 day'
date - INTERVAL '1 month'
```

### Math Functions
```sql
ROUND(number, digits)
CEIL(number) / CEILING(number)
FLOOR(number)
ABS(number)
RANDOM()
```

## 📋 QUICK REFERENCE

### Kolejność klauzul SELECT
```sql
SELECT     -- 5. Wybierz kolumny
FROM       -- 1. Z której tabeli
JOIN       -- 2. Połącz z innymi tabelami  
WHERE      -- 3. Filtruj wiersze
GROUP BY   -- 4. Grupuj
HAVING     -- 6. Filtruj grupy
ORDER BY   -- 7. Sortuj
LIMIT      -- 8. Ograniczenie liczby wyników
```

### Operator precedence (od najwyższego)
1. `()` Parentheses
2. `*`, `/`, `%` Arithmetic  
3. `+`, `-` Arithmetic
4. `=`, `!=`, `<`, `>`, `<=`, `>=`, `IN`, `LIKE` Comparison
5. `NOT`
6. `AND`
7. `OR`

### Przydatne wzorce
```sql
-- Pagination
SELECT * FROM tabela ORDER BY id LIMIT 20 OFFSET 100;

-- Top N w każdej grupie
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY grupa ORDER BY wartość DESC) as rn
    FROM tabela
) t WHERE rn <= 3;

-- Eliminate duplicates
SELECT DISTINCT ON (kolumna) *
FROM tabela
ORDER BY kolumna, inna_kolumna DESC;
```