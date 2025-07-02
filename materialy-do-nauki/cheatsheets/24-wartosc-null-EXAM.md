# ❓ WARTOŚĆ NULL - OBSŁUGA I SEMANTYKA - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"NULL w bazach danych reprezentuje brak wartości lub nieznaną wartość. Ważne właściwości:

1. **NULL ≠ 0 i NULL ≠ ''** - to nie jest zero ani pusty string
2. **Logika trójwartościowa** - operacje z NULL dają NULL, TRUE, FALSE
3. **IS NULL / IS NOT NULL** - jedyny sposób sprawdzenia NULL
4. **Agregacje** - funkcje agregujące ignorują NULL (oprócz COUNT(*))
5. **UNIQUE** - PostgreSQL pozwala na wiele NULL w kolumnie UNIQUE

NULL wprowadza złożoność w zapytania ale jest konieczny dla reprezentacji niepełnych danych."

## ✍️ CO NAPISAĆ NA KARTCE

```sql
WARTOŚĆ NULL - KLUCZOWE ZASADY:

LOGIKA TRÓJWARTOŚCIOWA:
TRUE AND NULL = NULL
FALSE AND NULL = FALSE  
NULL AND NULL = NULL

TRUE OR NULL = TRUE
FALSE OR NULL = NULL
NULL OR NULL = NULL

NOT NULL = NULL

PORÓWNANIA Z NULL:
NULL = NULL → NULL (nie TRUE!)
NULL != 5 → NULL  
NULL > 10 → NULL
5 + NULL → NULL
CONCAT('Hello', NULL) → NULL

SPRAWDZANIE NULL:
✓ column IS NULL
✓ column IS NOT NULL  
✗ column = NULL (zawsze FALSE!)
✗ column != NULL (zawsze FALSE!)

FUNKCJE AGREGUJĄCE:
COUNT(*) - liczy wszystkie wiersze (z NULL)
COUNT(column) - ignoruje NULL
SUM(column) - ignoruje NULL  
AVG(column) - ignoruje NULL
MIN/MAX(column) - ignoruje NULL

COALESCE(val1, val2, val3) - pierwszy NOT NULL
NULLIF(val1, val2) - NULL jeśli val1 = val2

UNIQUE CONSTRAINTS:
PostgreSQL: wiele NULL dozwolone w UNIQUE
MySQL: tylko jeden NULL w UNIQUE
SQL Standard: implementacja zależna

WHERE clause:
WHERE column = 5  -- nie znajdzie NULL
WHERE column IS NULL  -- znajdzie tylko NULL
WHERE column IS NOT NULL  -- pomija NULL

ORDER BY:
NULLS FIRST - NULL na początku  
NULLS LAST - NULL na końcu (domyślnie w PostgreSQL)

JOIN behavior:
NULL nie pasuje do NULL w JOIN ON condition
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- DEMONSTRACJA OBSŁUGI NULL

-- Tabela z różnymi typami NULL
CREATE TABLE pracownicy_null_test (
    id SERIAL PRIMARY KEY,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50),
    email VARCHAR(100) UNIQUE,  -- może być NULL
    telefon VARCHAR(20),
    pensja DECIMAL(10,2),
    data_urodzenia DATE,
    uwagi TEXT
);

-- Dane testowe z NULL
INSERT INTO pracownicy_null_test VALUES 
(1, 'Jan', 'Kowalski', 'jan@test.com', '123456789', 5000, '1980-01-15', 'Senior dev'),
(2, 'Anna', NULL, 'anna@test.com', NULL, 6000, '1985-03-10', NULL),
(3, 'Piotr', 'Nowak', NULL, '987654321', NULL, NULL, 'Junior dev'),
(4, 'Maria', 'Wiśniewska', NULL, NULL, 7000, '1982-07-20', NULL),
(5, 'Tomasz', NULL, 'tomasz@test.com', NULL, NULL, '1979-12-05', 'Consultant');

-- 1. SPRAWDZANIE NULL - poprawne i niepoprawne sposoby

-- ✓ POPRAWNIE - używaj IS NULL / IS NOT NULL
SELECT imie, nazwisko, email
FROM pracownicy_null_test
WHERE nazwisko IS NULL;

SELECT imie, nazwisko, pensja
FROM pracownicy_null_test  
WHERE pensja IS NOT NULL AND pensja > 5500;

-- ✗ NIEPOPRAWNIE - nigdy nie używaj = NULL
-- To zapytanie nie zwróci żadnych wyników nawet jeśli są NULL'e:
SELECT imie FROM pracownicy_null_test WHERE nazwisko = NULL;
SELECT imie FROM pracownicy_null_test WHERE nazwisko != NULL;

-- 2. LOGIKA TRÓJWARTOŚCIOWA w praktyce

-- Zapytanie z warunkiem złożonym
SELECT imie, pensja, telefon
FROM pracownicy_null_test
WHERE pensja > 5000 AND telefon IS NOT NULL;

-- Demonstracja AND z NULL
SELECT 
    imie,
    pensja,
    telefon,
    (pensja > 5000) as pensja_ok,
    (telefon IS NOT NULL) as ma_telefon,
    (pensja > 5000 AND telefon IS NOT NULL) as oba_warunki
FROM pracownicy_null_test;

-- OR z NULL
SELECT imie, email, telefon
FROM pracownicy_null_test
WHERE email IS NOT NULL OR telefon IS NOT NULL;

-- 3. FUNKCJE AGREGUJĄCE z NULL

-- COUNT różne zachowania
SELECT 
    COUNT(*) as wszystkie_wiersze,           -- 5
    COUNT(nazwisko) as ma_nazwisko,          -- 3 (ignoruje NULL)
    COUNT(email) as ma_email,                -- 3 (ignoruje NULL)  
    COUNT(pensja) as ma_pensje               -- 3 (ignoruje NULL)
FROM pracownicy_null_test;

-- SUM, AVG ignorują NULL
SELECT 
    SUM(pensja) as suma_pensji,              -- 18000 (5000+6000+7000)
    AVG(pensja) as srednia_pensja,           -- 6000 (nie 3600!)
    MIN(pensja) as min_pensja,               -- 5000
    MAX(pensja) as max_pensja                -- 7000
FROM pracownicy_null_test;

-- GROUP BY z NULL
SELECT 
    COALESCE(nazwisko, '(brak nazwiska)') as nazwisko_group,
    COUNT(*) as liczba,
    AVG(pensja) as srednia_pensja
FROM pracownicy_null_test
GROUP BY nazwisko;  -- NULL'e tworzą osobną grupę

-- 4. FUNKCJE DO OBSŁUGI NULL

-- COALESCE - pierwszy NOT NULL
SELECT 
    imie,
    COALESCE(nazwisko, '(nieznane)') as nazwisko_safe,
    COALESCE(email, 'brak@email.com') as email_safe,
    COALESCE(pensja, 0) as pensja_safe
FROM pracownicy_null_test;

-- NULLIF - zwraca NULL jeśli wartości równe
SELECT 
    imie,
    NULLIF(uwagi, '') as uwagi_clean,  -- zamienia pusty string na NULL
    NULLIF(pensja, 0) as pensja_nullif  -- zamienia 0 na NULL
FROM pracownicy_null_test;

-- CASE z NULL
SELECT 
    imie,
    CASE 
        WHEN nazwisko IS NULL THEN 'Brak nazwiska'
        WHEN LENGTH(nazwisko) < 5 THEN 'Krótkie nazwisko'
        ELSE 'Normalne nazwisko'
    END as status_nazwisko
FROM pracownicy_null_test;

-- 5. ORDER BY z NULL

-- Domyślne sortowanie (NULLS LAST w PostgreSQL)
SELECT imie, nazwisko, pensja
FROM pracownicy_null_test
ORDER BY pensja;

-- Explicit NULLS positioning
SELECT imie, nazwisko, pensja
FROM pracownicy_null_test
ORDER BY pensja NULLS FIRST;  -- NULL'e na początku

SELECT imie, nazwisko, pensja
FROM pracownicy_null_test  
ORDER BY pensja DESC NULLS LAST;  -- NULL'e na końcu

-- 6. JOIN z NULL

CREATE TABLE departamenty_test (
    id INT PRIMARY KEY,
    nazwa VARCHAR(50),
    kierownik_id INT  -- może być NULL
);

INSERT INTO departamenty_test VALUES 
(1, 'IT', 1),
(2, 'HR', NULL),  -- departament bez kierownika
(3, 'Finance', 99); -- kierownik nie istnieje w pracownicy

-- INNER JOIN - NULL nie pasuje do niczego
SELECT d.nazwa, p.imie as kierownik
FROM departamenty_test d
INNER JOIN pracownicy_null_test p ON d.kierownik_id = p.id;
-- Wynik: tylko departament IT

-- LEFT JOIN pokazuje NULL'e
SELECT d.nazwa, p.imie as kierownik
FROM departamenty_test d  
LEFT JOIN pracownicy_null_test p ON d.kierownik_id = p.id;
-- Wynik: wszystkie departamenty, HR i Finance z NULL kierownik

-- 7. UNIQUE CONSTRAINTS z NULL

-- W PostgreSQL można wiele NULL w UNIQUE
INSERT INTO pracownicy_null_test (imie, email) VALUES ('Test1', NULL);
INSERT INTO pracownicy_null_test (imie, email) VALUES ('Test2', NULL);  -- OK!

-- Ale nie można duplikatów NOT NULL
-- INSERT INTO pracownicy_null_test (imie, email) VALUES ('Test3', 'jan@test.com');  -- BŁĄD

-- 8. INDEKSY z NULL

-- Sprawdzenie czy NULL'e są w indeksie
CREATE INDEX idx_pensja ON pracownicy_null_test(pensja);

-- B-tree index zawiera NULL'e
EXPLAIN SELECT * FROM pracownicy_null_test WHERE pensja IS NULL;

-- Partial index bez NULL'ów
CREATE INDEX idx_pensja_not_null ON pracownicy_null_test(pensja) 
WHERE pensja IS NOT NULL;

-- 9. CONSTRAINTS z NULL

-- CHECK constraint z NULL
ALTER TABLE pracownicy_null_test 
ADD CONSTRAINT chk_pensja_pozytywna 
CHECK (pensja IS NULL OR pensja > 0);  -- NULL'e są dozwolone

-- NOT NULL constraint
ALTER TABLE pracownicy_null_test 
ALTER COLUMN imie SET NOT NULL;  -- już jest NOT NULL

-- Próba dodania NOT NULL do kolumny z NULL'ami
-- ALTER TABLE pracownicy_null_test ALTER COLUMN nazwisko SET NOT NULL;  -- BŁĄD

-- Najpierw uzupełnij NULL'e
UPDATE pracownicy_null_test 
SET nazwisko = 'Nieznane' 
WHERE nazwisko IS NULL;

-- Teraz można dodać NOT NULL
ALTER TABLE pracownicy_null_test ALTER COLUMN nazwisko SET NOT NULL;

-- 10. ZAAWANSOWANA OBSŁUGA NULL

-- Conditional aggregation z NULL
SELECT 
    COUNT(*) as wszyscy,
    COUNT(CASE WHEN pensja > 5500 THEN 1 END) as wysokie_pensje,
    COUNT(CASE WHEN pensja <= 5500 THEN 1 END) as niskie_pensje,
    COUNT(CASE WHEN pensja IS NULL THEN 1 END) as bez_pensji
FROM pracownicy_null_test;

-- String concatenation z NULL
SELECT 
    imie,
    nazwisko,
    imie || ' ' || nazwisko as pelne_imie_zle,  -- NULL jeśli nazwisko NULL
    CONCAT(imie, ' ', COALESCE(nazwisko, '')) as pelne_imie_ok
FROM pracownicy_null_test;

-- Array aggregation z NULL
SELECT array_agg(pensja) as wszystkie_pensje,         -- zawiera NULL'e
       array_agg(pensja) FILTER (WHERE pensja IS NOT NULL) as pensje_bez_null
FROM pracownicy_null_test;

-- 11. NULL w subqueries

-- EXISTS ignoruje NULL'e w wynikach
SELECT p.imie
FROM pracownicy_null_test p
WHERE EXISTS (
    SELECT telefon FROM pracownicy_null_test p2 
    WHERE p2.telefon = p.telefon  -- NULL = NULL daje NULL (FALSE)
);

-- IN z NULL może dawać nieoczekiwane wyniki
SELECT imie
FROM pracownicy_null_test
WHERE pensja IN (5000, 6000, NULL);  -- NULL w IN może prowadzić do problemów

-- Better approach with explicit NULL handling
SELECT imie
FROM pracownicy_null_test  
WHERE pensja IN (5000, 6000) OR pensja IS NULL;

-- 12. WINDOW FUNCTIONS z NULL

-- NULL'e w window functions
SELECT 
    imie,
    pensja,
    LAG(pensja) OVER (ORDER BY id) as poprzednia_pensja,
    LEAD(pensja) OVER (ORDER BY id) as nastepna_pensja,
    FIRST_VALUE(pensja) OVER (ORDER BY pensja NULLS LAST) as najnizsza_pensja
FROM pracownicy_null_test;

-- 13. PERFORMANCE IMPLICATIONS

-- NULL checks w WHERE są optymalizowane
EXPLAIN SELECT * FROM pracownicy_null_test WHERE pensja IS NULL;

-- Index usage z NULL
EXPLAIN SELECT * FROM pracownicy_null_test WHERE pensja IS NOT NULL;

-- 14. COMMON MISTAKES I SOLUTIONS

-- Mistake: sumowanie z NULL bez obsługi
SELECT SUM(pensja) as suma_zla FROM pracownicy_null_test;  -- ignoruje NULL'e

-- Better: explicit NULL handling  
SELECT SUM(COALESCE(pensja, 0)) as suma_lepsza FROM pracownicy_null_test;

-- Mistake: porównania z NULL
-- SELECT * FROM pracownicy_null_test WHERE pensja = NULL;  -- zawsze 0 wyników

-- Correct: IS NULL/IS NOT NULL
SELECT * FROM pracownicy_null_test WHERE pensja IS NULL;
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: NULL = NULL daje NULL (nie TRUE!)
2. **UWAGA**: COUNT(kolumna) vs COUNT(*) - różne zachowanie z NULL
3. **BŁĄD**: Używanie = NULL zamiast IS NULL
4. **WAŻNE**: Funkcje agregujące ignorują NULL (oprócz COUNT(*))
5. **PUŁAPKA**: UNIQUE w PostgreSQL pozwala na wiele NULL

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Three-valued logic** - logika trójwartościowa
- **IS NULL/IS NOT NULL** - sprawdzanie NULL
- **COALESCE/NULLIF** - funkcje obsługi NULL
- **NULL handling** - obsługa wartości NULL
- **Aggregate functions** - funkcje agregujące z NULL
- **NULLS FIRST/LAST** - pozycjonowanie NULL w sortowaniu
- **Outer joins** - zachowanie NULL w JOIN'ach
- **Missing values** - brakujące wartości

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **21-sql-joiny** - NULL w JOIN'ach
- **32-funkcje-agregujace** - agregacje z NULL
- **12-klucze-bazy-danych** - NULL w kluczach obcych
- **01-integralnosc** - constraints z NULL
- **30-sql-dml-zaawansowany** - zaawansowana obsługa NULL