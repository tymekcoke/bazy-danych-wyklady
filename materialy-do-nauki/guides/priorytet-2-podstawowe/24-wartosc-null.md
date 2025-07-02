# Wartość NULL - obsługa i semantyka

## Definicja NULL

**NULL** to specjalna wartość w bazach danych reprezentująca **brak wartości** lub **nieznane dane**. To **nie** jest:
- Zero (0)
- Pusty string ('')
- Spacja (' ')
- False

### Semantyka NULL:
- **Nieznana wartość** - wartość istnieje, ale nie jest znana
- **Brak wartości** - wartość nie istnieje wcale
- **Nie ma zastosowania** - atrybut nie dotyczy tej encji

## Rodzaje NULL

### 1. **Unknown Value**
```sql
-- Pracownik ma numer telefonu, ale go nie znamy
INSERT INTO pracownicy (id, imie, nazwisko, telefon) 
VALUES (1, 'Jan', 'Kowalski', NULL);
```

### 2. **Missing Value**
```sql
-- Produkt nie ma kategorii (jeszcze nie przypisano)
INSERT INTO produkty (id, nazwa, kategoria, cena) 
VALUES (1, 'Nowy produkt', NULL, 99.99);
```

### 3. **Not Applicable**
```sql
-- Nieżonaty pracownik - nazwisko żony nie ma zastosowania
INSERT INTO pracownicy (id, imie, nazwisko, nazwisko_zony) 
VALUES (1, 'Jan', 'Kowalski', NULL);
```

## Logika trójwartościowa

### Wartości logiczne:
- **TRUE** - prawda
- **FALSE** - fałsz  
- **UNKNOWN** - nieznane (gdy NULL uczestniczy w porównaniu)

### Tabele prawdy:

#### AND:
```
TRUE  AND TRUE   = TRUE
TRUE  AND FALSE  = FALSE  
TRUE  AND UNKNOWN = UNKNOWN
FALSE AND TRUE   = FALSE
FALSE AND FALSE  = FALSE
FALSE AND UNKNOWN = FALSE
UNKNOWN AND TRUE   = UNKNOWN
UNKNOWN AND FALSE  = FALSE
UNKNOWN AND UNKNOWN = UNKNOWN
```

#### OR:
```
TRUE  OR TRUE   = TRUE
TRUE  OR FALSE  = TRUE
TRUE  OR UNKNOWN = TRUE  
FALSE OR TRUE   = TRUE
FALSE OR FALSE  = FALSE
FALSE OR UNKNOWN = UNKNOWN
UNKNOWN OR TRUE   = TRUE
UNKNOWN OR FALSE  = UNKNOWN
UNKNOWN OR UNKNOWN = UNKNOWN
```

#### NOT:
```
NOT TRUE    = FALSE
NOT FALSE   = TRUE
NOT UNKNOWN = UNKNOWN
```

## Porównania z NULL

### Podstawowa zasada:
**NULL nie jest równe niczemu, nawet innemu NULL!**

```sql
-- Wszystkie poniższe zwracają UNKNOWN (nie TRUE ani FALSE):
NULL = NULL      -- UNKNOWN
NULL = 5         -- UNKNOWN  
NULL <> 5        -- UNKNOWN
NULL > 10        -- UNKNOWN
5 + NULL         -- NULL
NULL AND TRUE    -- UNKNOWN
```

### Przykłady porównań:
```sql
CREATE TABLE test (id INT, wartosc INT);
INSERT INTO test VALUES 
(1, 10),
(2, NULL),
(3, 20),
(4, NULL);

-- ❌ To NIE znajdzie rekordów z NULL!
SELECT * FROM test WHERE wartosc = NULL;     -- 0 rekordów
SELECT * FROM test WHERE wartosc <> NULL;    -- 0 rekordów

-- ✅ Prawidłowe sprawdzanie NULL
SELECT * FROM test WHERE wartosc IS NULL;        -- id: 2, 4
SELECT * FROM test WHERE wartosc IS NOT NULL;    -- id: 1, 3
```

## Operatory do obsługi NULL

### 1. **IS NULL / IS NOT NULL**
```sql
-- Pracownicy bez telefonu
SELECT imie, nazwisko 
FROM pracownicy 
WHERE telefon IS NULL;

-- Pracownicy z telefonem
SELECT imie, nazwisko 
FROM pracownicy 
WHERE telefon IS NOT NULL;

-- Produkty bez kategorii LUB bez ceny
SELECT nazwa 
FROM produkty 
WHERE kategoria IS NULL OR cena IS NULL;
```

### 2. **COALESCE** - pierwsza nie-NULL wartość
```sql
-- Wyświetl telefon, jeśli brak to "Brak numeru"
SELECT 
    imie,
    nazwisko,
    COALESCE(telefon, 'Brak numeru') as kontakt
FROM pracownicy;

-- Cena efektywna: użyj ceny promocyjnej, jeśli brak to zwykłą
SELECT 
    nazwa,
    cena,
    cena_promocyjna,
    COALESCE(cena_promocyjna, cena) as cena_efektywna
FROM produkty;

-- Wiele alternatyw
SELECT 
    COALESCE(telefon_kom, telefon_dom, telefon_biuro, 'Brak kontaktu') as kontakt
FROM kontakty;
```

### 3. **NULLIF** - zwróć NULL jeśli równe
```sql
-- Jeśli rabat = 0, pokaż NULL zamiast 0
SELECT 
    nazwa,
    cena,
    NULLIF(rabat, 0) as rabat_rzeczywisty
FROM produkty;

-- Zapobiegnij dzieleniu przez zero
SELECT 
    sprzedaz,
    zwroty,
    sprzedaz / NULLIF(zwroty, 0) as wskaznik
FROM statystyki;
```

### 4. **ISNULL / NVL** (zależne od SZBD)
```sql
-- SQL Server
SELECT imie, ISNULL(telefon, 'Brak') FROM pracownicy;

-- Oracle
SELECT imie, NVL(telefon, 'Brak') FROM pracownicy;

-- MySQL
SELECT imie, IFNULL(telefon, 'Brak') FROM pracownicy;
```

## NULL w operacjach arytmetycznych

### Zasada: NULL + cokolwiek = NULL
```sql
SELECT 
    5 + NULL,           -- NULL
    10 - NULL,          -- NULL
    NULL * 3,           -- NULL
    NULL / 2,           -- NULL
    NULL % 5;           -- NULL

-- Przykład praktyczny
CREATE TABLE zamowienia (
    id INT,
    cena_netto DECIMAL(10,2),
    vat DECIMAL(10,2)
);

INSERT INTO zamowienia VALUES 
(1, 100.00, 23.00),
(2, 200.00, NULL),    -- Brak VAT
(3, NULL, 23.00);     -- Brak ceny netto

-- Problem: Obliczanie ceny brutto
SELECT 
    id,
    cena_netto,
    vat,
    cena_netto + vat as cena_brutto  -- NULL jeśli którakolwiek NULL!
FROM zamowienia;

-- Wynik:
-- 1 | 100.00 | 23.00 | 123.00
-- 2 | 200.00 | NULL  | NULL     ← Problem!
-- 3 | NULL   | 23.00 | NULL     ← Problem!

-- Rozwiązanie z COALESCE
SELECT 
    id,
    cena_netto,
    vat,
    COALESCE(cena_netto, 0) + COALESCE(vat, 0) as cena_brutto
FROM zamowienia;

-- Wynik:
-- 1 | 100.00 | 23.00 | 123.00
-- 2 | 200.00 | NULL  | 200.00   ← VAT = 0
-- 3 | NULL   | 23.00 | 23.00    ← Cena netto = 0
```

## NULL w funkcjach agregujących

### Zachowanie funkcji:
```sql
CREATE TABLE dane (id INT, wartosc INT);
INSERT INTO dane VALUES 
(1, 10), (2, 20), (3, NULL), (4, 30), (5, NULL);

-- Funkcje agregujące IGNORUJĄ NULL (oprócz COUNT(*))
SELECT 
    COUNT(*),           -- 5 (wszystkie rekordy)
    COUNT(wartosc),     -- 3 (tylko nie-NULL)
    SUM(wartosc),       -- 60 (10+20+30, ignoruje NULL)
    AVG(wartosc),       -- 20 (60/3, nie 60/5!)
    MIN(wartosc),       -- 10 (ignoruje NULL)
    MAX(wartosc);       -- 30 (ignoruje NULL)
```

### Pułapka z AVG:
```sql
-- Czy te są równoważne?
SELECT AVG(pensja) FROM pracownicy;                    -- Średnia z nie-NULL
SELECT SUM(pensja) / COUNT(*) FROM pracownicy;        -- Średnia ze wszystkich

-- NIE! Jeśli są NULL-e:
-- AVG ignoruje NULL: SUM(nie-NULL) / COUNT(nie-NULL)
-- Drugie: SUM(nie-NULL) / COUNT(wszystkich)
```

### Agregacja z NULL handling:
```sql
-- Zliczanie NULL-i
SELECT 
    COUNT(*) as wszystkie,
    COUNT(telefon) as z_telefonem,
    COUNT(*) - COUNT(telefon) as bez_telefonu
FROM pracownicy;

-- Średnia z uwzględnieniem NULL jako 0
SELECT 
    AVG(COALESCE(pensja, 0)) as srednia_z_zerami,
    AVG(pensja) as srednia_bez_null
FROM pracownicy;
```

## NULL w klauzulach WHERE

### Filtrowanie a NULL:
```sql
-- Uwaga: WHERE eliminuje UNKNOWN!
SELECT * FROM produkty WHERE cena > 100;      -- Nie obejmuje NULL
SELECT * FROM produkty WHERE cena <= 100;     -- Nie obejmuje NULL  
SELECT * FROM produkty WHERE cena <> 100;     -- Nie obejmuje NULL

-- Aby uwzględnić NULL:
SELECT * FROM produkty 
WHERE cena > 100 OR cena IS NULL;

-- Negacja z NULL
SELECT * FROM produkty WHERE NOT (cena > 100);
-- To NIE jest równoważne z:
SELECT * FROM produkty WHERE cena <= 100;
-- Pierwsze uwzględnia NULL (NOT UNKNOWN = UNKNOWN → zostaje)
```

### Przykład praktyczny:
```sql
-- Znajdź produkty które NIE kosztują 100
SELECT * FROM produkty WHERE cena <> 100;        -- Pominięte NULL
SELECT * FROM produkty WHERE COALESCE(cena, -1) <> 100;  -- Z NULL

-- Logika biznesowa: NULL = "darmowy" 
SELECT * FROM produkty 
WHERE COALESCE(cena, 0) <> 100;
```

## NULL w JOIN'ach

### NULL w warunkich JOIN:
```sql
CREATE TABLE klienci (id INT, nazwa VARCHAR(100), region_id INT);
CREATE TABLE regiony (id INT, nazwa VARCHAR(100));

INSERT INTO klienci VALUES 
(1, 'Firma A', 1),
(2, 'Firma B', NULL),    -- Brak regionu
(3, 'Firma C', 3);

INSERT INTO regiony VALUES 
(1, 'Północ'), (2, 'Południe'), (3, 'Wschód');

-- INNER JOIN pomija NULL
SELECT k.nazwa, r.nazwa 
FROM klienci k 
JOIN regiony r ON k.region_id = r.id;
-- Wynik: Firma A-Północ, Firma C-Wschód (Firma B pominięta)

-- LEFT JOIN zachowuje NULL
SELECT k.nazwa, r.nazwa 
FROM klienci k 
LEFT JOIN regiony r ON k.region_id = r.id;
-- Wynik: Firma A-Północ, Firma B-NULL, Firma C-Wschód
```

### Self-JOIN z NULL:
```sql
CREATE TABLE pracownicy (
    id INT, 
    imie VARCHAR(50), 
    szef_id INT
);

INSERT INTO pracownicy VALUES 
(1, 'Dyrektor', NULL),     -- Brak szefa
(2, 'Manager', 1),
(3, 'Pracownik', 2);

-- Hierarchia z szefami
SELECT 
    p.imie as pracownik,
    s.imie as szef
FROM pracownicy p
LEFT JOIN pracownicy s ON p.szef_id = s.id;
-- Wynik: Dyrektor-NULL, Manager-Dyrektor, Pracownik-Manager
```

## NULL w DISTINCT i GROUP BY

### DISTINCT traktuje NULL jako jedną wartość:
```sql
CREATE TABLE test (wartosc INT);
INSERT INTO test VALUES (1), (2), (NULL), (NULL), (1), (NULL);

SELECT DISTINCT wartosc FROM test;
-- Wynik: 1, 2, NULL (tylko jeden NULL)
```

### GROUP BY traktuje NULL-e jako jedną grupę:
```sql
SELECT 
    kategoria, 
    COUNT(*) as liczba
FROM produkty 
GROUP BY kategoria;

-- Wynik:
-- Elektronika | 5
-- Odzież      | 3  
-- NULL        | 2  ← Wszystkie NULL w jednej grupie
```

## NULL w ORDER BY

### Pozycjonowanie NULL:
```sql
-- PostgreSQL, SQL Server: NULL na końcu przy ASC
SELECT * FROM produkty ORDER BY cena ASC;
-- 10, 20, 50, 100, NULL, NULL

-- Oracle, MySQL: NULL na początku przy ASC  
SELECT * FROM produkty ORDER BY cena ASC;
-- NULL, NULL, 10, 20, 50, 100

-- Kontrolowanie pozycji NULL
SELECT * FROM produkty ORDER BY cena ASC NULLS FIRST;   -- PostgreSQL
SELECT * FROM produkty ORDER BY cena ASC NULLS LAST;    -- PostgreSQL

-- Uniwersalne rozwiązanie
SELECT * FROM produkty ORDER BY 
    CASE WHEN cena IS NULL THEN 1 ELSE 0 END,  -- NULL na końcu
    cena ASC;
```

## Ograniczenia i NULL

### NOT NULL constraint:
```sql
CREATE TABLE produkty (
    id INT PRIMARY KEY,
    nazwa VARCHAR(100) NOT NULL,     -- Wymagane
    cena DECIMAL(10,2),              -- Opcjonalne (może być NULL)
    kategoria_id INT NOT NULL        -- Wymagane
);

-- ❌ Błąd
INSERT INTO produkty (id, cena) VALUES (1, 99.99);  -- Brak nazwa

-- ✅ OK
INSERT INTO produkty (id, nazwa, cena) VALUES (1, 'Produkt', 99.99);
```

### CHECK constraints z NULL:
```sql
-- Constraint który pozwala na NULL
ALTER TABLE produkty ADD CONSTRAINT cena_dodatnia 
CHECK (cena IS NULL OR cena > 0);

-- NULL przechodzi przez CHECK (UNKNOWN traktowane jako przeszło)
INSERT INTO produkty (id, nazwa, cena) VALUES (1, 'Test', NULL);  -- OK

-- Constraint który wymaga wartości
ALTER TABLE produkty ADD CONSTRAINT cena_wymagana
CHECK (cena IS NOT NULL AND cena > 0);
```

### UNIQUE constraint z NULL:
```sql
CREATE TABLE kontakty (
    id INT PRIMARY KEY,
    email VARCHAR(100) UNIQUE,  -- UNIQUE pozwala na wiele NULL!
    telefon VARCHAR(15) UNIQUE
);

-- ✅ Wszystkie OK - wiele NULL jest dozwolone
INSERT INTO kontakty VALUES (1, 'jan@email.com', NULL);
INSERT INTO kontakty VALUES (2, NULL, '123-456-789');  
INSERT INTO kontakty VALUES (3, NULL, NULL);           -- OK!
INSERT INTO kontakty VALUES (4, NULL, NULL);           -- OK!

-- ❌ Błąd - duplikat nie-NULL wartości
INSERT INTO kontakty VALUES (5, 'jan@email.com', '999-888-777');
```

## Funkcje do pracy z NULL

### 1. **Sprawdzanie NULL w różnych SZBD:**
```sql
-- Standardowe SQL
WHERE kolumna IS NULL
WHERE kolumna IS NOT NULL

-- PostgreSQL - dodatkowe operatory
WHERE kolumna ISNULL                    -- Równoważne IS NULL
WHERE kolumna NOTNULL                   -- Równoważne IS NOT NULL

-- SQL Server - funkcje
WHERE ISNULL(kolumna, 0) = 0           -- Sprawdza czy NULL
WHERE LEN(kolumna) IS NULL             -- Sprytne dla VARCHAR
```

### 2. **Porównania NULL-safe:**
```sql
-- PostgreSQL - IS DISTINCT FROM
SELECT * FROM test 
WHERE kolumna1 IS DISTINCT FROM kolumna2;     -- TRUE jeśli różne (uwzględnia NULL)

SELECT * FROM test 
WHERE kolumna1 IS NOT DISTINCT FROM kolumna2; -- TRUE jeśli identyczne (uwzględnia NULL)

-- MySQL - NULL-safe equals
SELECT * FROM test WHERE kolumna1 <=> kolumna2;  -- TRUE nawet dla NULL = NULL

-- Uniwersalne rozwiązanie
SELECT * FROM test 
WHERE (kolumna1 = kolumna2) 
   OR (kolumna1 IS NULL AND kolumna2 IS NULL);
```

### 3. **Zaawansowane funkcje:**
```sql
-- PostgreSQL - NULLIF i GREATEST/LEAST
SELECT 
    NULLIF(division, 0),                    -- NULL jeśli 0
    GREATEST(val1, val2, val3),             -- Ignoruje NULL
    LEAST(val1, val2, val3);                -- Ignoruje NULL

-- SQL Server - IIF z NULL
SELECT IIF(kolumna IS NULL, 'Brak', kolumna) FROM test;

-- Oracle - NVL2 
SELECT NVL2(kolumna, 'Ma wartość', 'NULL') FROM test;
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**
1. **Explicit NULL handling** - zawsze myśl o NULL
2. **COALESCE dla defaultów** - zamiast pozostawiania NULL
3. **IS NULL/IS NOT NULL** - nigdy = NULL
4. **NOT NULL constraints** - gdzie sensowne
5. **Dokumentuj semantykę** - co oznacza NULL w kontekście

### ❌ **Złe praktyki:**
1. **= NULL comparisons** - zawsze zwraca UNKNOWN
2. **Ignorowanie NULL w obliczeniach** - niespodziewane wyniki
3. **Mylenie NULL z zerami/pustymi stringami**
4. **Brak obsługi NULL w aplikacji**
5. **Założenie że agregacje uwzględniają NULL**

## Przykłady problemów i rozwiązań

### Problem 1: Raportowanie z NULL
```sql
-- ❌ Problem
SELECT 
    kategoria,
    AVG(cena) as srednia_cena
FROM produkty
GROUP BY kategoria;
-- NULL kategoria może zniekształcić wyniki

-- ✅ Rozwiązanie
SELECT 
    COALESCE(kategoria, 'Nieokreślona') as kategoria,
    AVG(cena) as srednia_cena,
    COUNT(*) as liczba_produktow,
    COUNT(cena) as produkty_z_cena
FROM produkty
GROUP BY kategoria;
```

### Problem 2: Wyszukiwanie z NULL
```sql
-- ❌ Problem - nie znajdzie NULL
SELECT * FROM klienci 
WHERE region_id IN (1, 2, 3);  -- Pomija NULL

-- ✅ Rozwiązanie
SELECT * FROM klienci 
WHERE region_id IN (1, 2, 3) OR region_id IS NULL;

-- Lub lepiej z COALESCE
SELECT * FROM klienci 
WHERE COALESCE(region_id, -1) IN (1, 2, 3, -1);
```

### Problem 3: Złączenia z NULL
```sql
-- ❌ Problem - LEFT JOIN nie zawsze wystarczy
SELECT k.nazwa, r.nazwa as region
FROM klienci k
LEFT JOIN regiony r ON k.region_id = r.id;

-- ✅ Rozwiązanie - obsługa NULL
SELECT 
    k.nazwa,
    COALESCE(r.nazwa, 'Brak regionu') as region,
    CASE 
        WHEN k.region_id IS NULL THEN 'Nie przypisano'
        WHEN r.id IS NULL THEN 'Błędny region'  
        ELSE r.nazwa
    END as status_regionu
FROM klienci k
LEFT JOIN regiony r ON k.region_id = r.id;
```

## Pułapki egzaminacyjne

### 1. **NULL ≠ wszystko**
- NULL = NULL → UNKNOWN (nie TRUE!)
- NULL = 5 → UNKNOWN  
- Tylko IS NULL zwraca TRUE/FALSE

### 2. **Logika trójwartościowa**
- TRUE, FALSE, UNKNOWN
- WHERE eliminuje UNKNOWN wyniki
- NOT UNKNOWN = UNKNOWN

### 3. **Agregacje i NULL**
- COUNT(*) liczy wszystkie
- COUNT(kolumna) liczy nie-NULL
- AVG ignoruje NULL w mianowniku

### 4. **JOIN i NULL**
- INNER JOIN pomija NULL w kluczach
- OUTER JOIN zachowuje NULL
- NULL nie pasuje do NULL w JOIN condition