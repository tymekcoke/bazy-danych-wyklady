# ⚠️ COMMON MISTAKES - NAJCZĘSTSZE BŁĘDY NA EGZAMINIE

## 🚨 TOP 10 KRYTYCZNYCH BŁĘDÓW

### 1. ❌ NULL COMPARISON
```sql
-- BŁĄD
WHERE salary = NULL        -- ZAWSZE FALSE!
WHERE salary != NULL       -- ZAWSZE FALSE!

-- POPRAWNIE  
WHERE salary IS NULL
WHERE salary IS NOT NULL
```
**Dlaczego:** NULL nie równa się niczemu, nawet NULL. To logika trójwartościowa.

### 2. ❌ NOT IN z NULL
```sql
-- BŁĄD - może zwrócić 0 wierszy gdy lista zawiera NULL
WHERE id NOT IN (1, 2, NULL)

-- POPRAWNIE
WHERE id NOT IN (1, 2) OR id IS NULL
-- LUB JESZCZE LEPIEJ
WHERE NOT EXISTS (SELECT 1 FROM tabela WHERE id IN (1, 2))
```
**Dlaczego:** NOT IN z NULL daje nieoczekiwane wyniki przez logikę SQL.

### 3. ❌ GROUP BY bez wszystkich kolumn
```sql
-- BŁĄD
SELECT name, department, AVG(salary)
FROM employees  
GROUP BY department;  -- name nie w GROUP BY!

-- POPRAWNIE
SELECT department, AVG(salary)
FROM employees
GROUP BY department;

-- LUB
SELECT name, department, AVG(salary)
FROM employees
GROUP BY name, department;
```
**Dlaczego:** Wszystkie kolumny w SELECT muszą być w GROUP BY lub być agregowane.

### 4. ❌ COUNT confusion
```sql
-- RÓŻNE WYNIKI!
SELECT COUNT(*) FROM employees;      -- wszystkie wiersze (z NULL)
SELECT COUNT(email) FROM employees;  -- tylko wiersze z email != NULL

-- PAMIĘTAJ
COUNT(*)           -- liczy wszystkie wiersze
COUNT(column)      -- ignoruje NULL w tej kolumnie  
COUNT(DISTINCT col) -- unikalne nie-NULL wartości
```

### 5. ❌ HAVING vs WHERE
```sql
-- BŁĄD - WHERE nie może używać funkcji agregujących
SELECT department, AVG(salary)
FROM employees
WHERE AVG(salary) > 5000    -- BŁĄD!
GROUP BY department;

-- POPRAWNIE
SELECT department, AVG(salary) 
FROM employees
GROUP BY department
HAVING AVG(salary) > 5000;
```
**Kolejność:** WHERE → GROUP BY → HAVING

### 6. ❌ JOIN syntax
```sql
-- STARY STYL (unikaj)
SELECT * FROM a, b WHERE a.id = b.a_id;

-- WSPÓŁCZESNY STYL
SELECT * FROM a JOIN b ON a.id = b.a_id;
SELECT * FROM a INNER JOIN b ON a.id = b.a_id;  -- to samo co JOIN
```
**Dlaczego:** Explicit JOIN jest czytelniejszy i mniej podatny na błędy.

### 7. ❌ Brak indeksów na Foreign Keys
```sql
-- BŁĄD - brak indeksu na FK
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id)  -- bez indeksu!
);

-- POPRAWNIE
CREATE TABLE orders (
    id SERIAL PRIMARY KEY, 
    customer_id INT REFERENCES customers(id)
);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```
**Dlaczego:** JOIN'y na FK bez indeksów są bardzo wolne.

### 8. ❌ String concatenation z NULL
```sql
-- PROBLEM
SELECT first_name || ' ' || last_name as full_name;  -- NULL jeśli last_name = NULL

-- ROZWIĄZANIE
SELECT CONCAT(first_name, ' ', COALESCE(last_name, '')) as full_name;
-- LUB
SELECT first_name || ' ' || COALESCE(last_name, '') as full_name;
```

### 9. ❌ Błędne WHERE w JOIN
```sql
-- MOŻE DAWAĆ NIEOCZEKIWANE WYNIKI
SELECT * FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id  
WHERE o.status = 'active';  -- eliminuje klientów bez zamówień!

-- POPRAWNIE dla "wszyscy klienci + ich aktywne zamówienia"
SELECT * FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id AND o.status = 'active';
```

### 10. ❌ Niewłaściwy typ klucza głównego
```sql
-- ZŁE POMYSŁY
CREATE TABLE users (
    email VARCHAR(100) PRIMARY KEY,  -- może się zmienić
    name VARCHAR(50) PRIMARY KEY     -- nie gwarantuje unikalności
);

-- DOBRA PRAKTYKA
CREATE TABLE users (
    id SERIAL PRIMARY KEY,           -- stabilny, liczbowy
    email VARCHAR(100) UNIQUE,
    name VARCHAR(50)
);
```

## 🎯 BŁĘDY PROJEKTOWANIA

### ❌ Naruszenia normalizacji
```sql
-- BŁĄD - powtarzanie danych
CREATE TABLE student_courses (
    student_id INT,
    student_name VARCHAR(100),    -- powtarza się dla każdego kursu
    course_id INT,
    course_name VARCHAR(100)      -- powtarza się dla każdego studenta
);

-- POPRAWNIE - znormalizowane
CREATE TABLE students (id, name);
CREATE TABLE courses (id, name);  
CREATE TABLE enrollments (student_id, course_id);
```

### ❌ Złe modelowanie relacji M:N
```sql
-- BŁĄD - próba M:N bez tabeli łączącej
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    course_ids INT[]  -- array to nie jest relacyjne!
);

-- POPRAWNIE
CREATE TABLE students (id, name);
CREATE TABLE courses (id, name);
CREATE TABLE student_courses (
    student_id INT REFERENCES students(id),
    course_id INT REFERENCES courses(id),
    PRIMARY KEY (student_id, course_id)
);
```

### ❌ Brak constraints
```sql
-- BŁĄD - brak walidacji
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    price DECIMAL(10,2),  -- może być ujemne!
    category VARCHAR(50)   -- może być puste!
);

-- POPRAWNIE
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    price DECIMAL(10,2) CHECK (price > 0),
    category VARCHAR(50) NOT NULL
);
```

## 📝 BŁĘDY ODPOWIEDZI USTNYCH

### ❌ Nieprecyzyjne definicje
**Pytanie:** "Co to 3NF?"
**ŹLE:** "To gdy tabela jest dobrze znormalizowana"
**DOBRZE:** "3NF to 2NF plus eliminacja zależności przechodnich - gdy atrybyt niebędący kluczem determinuje inny atrybut niebędący kluczem"

### ❌ Brak przykładów
**Pytanie:** "Co to deadlock?"
**ŹLE:** "To gdy transakcje się blokują"
**DOBRZE:** "Deadlock to gdy T1 blokuje zasób A i chce B, a T2 blokuje B i chce A - cykliczne oczekiwanie. System wykrywa i anuluje jedną transakcję"

### ❌ Mylenie pojęć
- **HAVING ≠ WHERE** (grupy vs wiersze)
- **INNER JOIN ≠ LEFT JOIN** (tylko pasujące vs wszystkie z lewej)
- **2NF ≠ 3NF** (zależności częściowe vs przechodnie)
- **PRIMARY KEY ≠ UNIQUE** (NOT NULL vs może NULL)

## ✍️ BŁĘDY PISANIA NA KARTCE

### ❌ Nieczytelne schematy
```
-- ŹLE
table1 -> table2

-- DOBRZE  
STUDENCI                KURSY
[id*] --------FK------> [id*]
imie                    nazwa
email                   ects

* = PRIMARY KEY
FK = FOREIGN KEY
```

### ❌ Niepoprawny SQL
```sql
-- BŁĘDY SKŁADNIOWE
SELECT name, FROM users;           -- przecinek przed FROM
SELECT * FROM users GROUP BY;     -- puste GROUP BY
UPDATE users SET name = Jan;       -- brak cudzysłowów
DELETE users WHERE id = 1;         -- brak FROM

-- POPRAWNIE
SELECT name FROM users;
SELECT department FROM users GROUP BY department;
UPDATE users SET name = 'Jan';
DELETE FROM users WHERE id = 1;
```

### ❌ Zapomnienie o kluczach
```sql
-- BŁĄD - brak kluczy w M:N
CREATE TABLE student_course (
    student_id INT,
    course_id INT
    -- brak PRIMARY KEY i FOREIGN KEY!
);

-- POPRAWNIE
CREATE TABLE student_course (
    student_id INT REFERENCES students(id),
    course_id INT REFERENCES courses(id),
    PRIMARY KEY (student_id, course_id)
);
```

## 🧠 MENTAL CHECKLIST

### Przed odpowiedzią sprawdź:
- [ ] Czy używam IS NULL zamiast = NULL?
- [ ] Czy wszystkie kolumny w SELECT są w GROUP BY lub agregowane?
- [ ] Czy używam HAVING dla warunków na grupach?
- [ ] Czy moje JOIN'y są explicit (nie comma-separated)?
- [ ] Czy FK mają indeksy?
- [ ] Czy handle'uję NULL properly?

### Przy projektowaniu sprawdź:
- [ ] Czy każda tabela ma PRIMARY KEY?
- [ ] Czy relacje M:N mają tabelę łączącą?  
- [ ] Czy są odpowiednie FOREIGN KEY constraints?
- [ ] Czy są CHECK constraints dla walidacji?
- [ ] Czy schemat jest znormalizowany (przynajmniej do 3NF)?

### Przy pisaniu SQL sprawdź:
- [ ] Przecinki w odpowiednich miejscach
- [ ] Cudzysłowy wokół stringów
- [ ] Średniki na końcu statements
- [ ] Poprawne nazwy tabel i kolumn
- [ ] Właściwą kolejność klauzul

## 🎯 MNEMONIC DEVICES

**ACID:** **A**nna **C**odziennie **I**dzie **D**o pracy
**JOIN:** **I**nner = **I**ntersection, **L**eft = **L**ewy kompletny
**3NF:** **T**rzy = **T**ransitive dependencies eliminated

---

**💡 PAMIĘTAJ:** Na egzaminie lepiej być precyzyjnym niż gadatliwym. Krótka, poprawna odpowiedź z przykładem > długie, nieprecyzyjne wyjaśnienie!