# SQL DML zaawansowany - SELECT

## Definicja DML

**Data Manipulation Language (DML)** to podzbiór SQL służący do **manipulacji danymi** w bazach danych. Obejmuje operacje **SELECT, INSERT, UPDATE, DELETE**.

### Kluczowe cechy DML:
- **Praca z danymi** - nie ze strukturą
- **Transakcyjność** - operacje w transakcjach
- **Wydajność** - kluczowa dla aplikacji
- **Złożoność** - od prostych po bardzo zaawansowane zapytania

### Fokus tego guide'a:
Zaawansowane techniki **SELECT** - najbardziej złożonej i wszechstronnej operacji DML.

## Struktura SELECT - przypomnienie

### Kolejność klauzul:
```sql
SELECT [DISTINCT] kolumny
FROM tabele
[JOIN inne_tabele ON warunki]
[WHERE warunki_filtrowania]
[GROUP BY kolumny_grupowania]
[HAVING warunki_grup]
[ORDER BY kolumny_sortowania]
[LIMIT liczba_wierszy]
[OFFSET przesuniecie];
```

### Kolejność wykonywania (różna od pisania!):
```
1. FROM + JOINs     -- Określenie źródeł danych
2. WHERE           -- Filtrowanie wierszy
3. GROUP BY        -- Grupowanie
4. HAVING          -- Filtrowanie grup
5. SELECT          -- Projekcja kolumn
6. DISTINCT        -- Usunięcie duplikatów
7. ORDER BY        -- Sortowanie
8. LIMIT/OFFSET    -- Ograniczenie wyników
```

## Zaawansowane JOIN'y

### 1. **LATERAL JOIN (PostgreSQL)**

#### Definicja:
**LATERAL** pozwala na odniesienie się do kolumn z poprzednich tabel w FROM clause.

```sql
-- Problem: Chcemy top 3 zamówienia dla każdego klienta
-- Bez LATERAL (błędne):
SELECT k.nazwa, z.data_zamowienia, z.wartosc
FROM klienci k
JOIN (
    SELECT id_klienta, data_zamowienia, wartosc 
    FROM zamowienia 
    WHERE id_klienta = k.id_klienta  -- BŁĄD: k nie jest dostępne tutaj
    ORDER BY wartosc DESC 
    LIMIT 3
) top_z ON TRUE;

-- Z LATERAL (poprawne):
SELECT k.nazwa, top_z.data_zamowienia, top_z.wartosc
FROM klienci k
LEFT JOIN LATERAL (
    SELECT data_zamowienia, wartosc 
    FROM zamowienia z
    WHERE z.id_klienta = k.id_klienta  -- Teraz k jest dostępne!
    ORDER BY wartosc DESC 
    LIMIT 3
) top_z ON TRUE;
```

#### Praktyczne zastosowania LATERAL:
```sql
-- Top N per group
SELECT 
    d.nazwa as dzial,
    top_emp.imie,
    top_emp.pensja
FROM dzialy d
LEFT JOIN LATERAL (
    SELECT imie, pensja
    FROM pracownicy p
    WHERE p.id_dzialu = d.id_dzialu
    ORDER BY pensja DESC
    LIMIT 2
) top_emp ON TRUE;

-- Skorelowane funkcje
SELECT 
    k.nazwa,
    stats.total_orders,
    stats.avg_value
FROM klienci k
LEFT JOIN LATERAL (
    SELECT 
        COUNT(*) as total_orders,
        AVG(wartosc) as avg_value
    FROM zamowienia z
    WHERE z.id_klienta = k.id_klienta
) stats ON TRUE;
```

### 2. **Rekurencyjne CTE (Common Table Expressions)**

#### Składnia:
```sql
WITH RECURSIVE nazwa_cte AS (
    -- Anchor query (base case)
    SELECT ...
    
    UNION ALL
    
    -- Recursive query
    SELECT ...
    FROM nazwa_cte
    WHERE warunek_zakończenia
)
SELECT * FROM nazwa_cte;
```

#### Przykład - hierarchia organizacyjna:
```sql
-- Struktura danych
CREATE TABLE pracownicy (
    id INTEGER PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    id_szefa INTEGER REFERENCES pracownicy(id)
);

-- Znajdź wszystkich podwładnych managera o ID = 1
WITH RECURSIVE hierarchia AS (
    -- Anchor: sam manager
    SELECT id, imie, nazwisko, id_szefa, 0 as poziom
    FROM pracownicy
    WHERE id = 1
    
    UNION ALL
    
    -- Recursive: podwładni na kolejnych poziomach
    SELECT p.id, p.imie, p.nazwisko, p.id_szefa, h.poziom + 1
    FROM pracownicy p
    JOIN hierarchia h ON p.id_szefa = h.id
    WHERE h.poziom < 10  -- Zabezpieczenie przed nieskończoną rekurencją
)
SELECT 
    REPEAT('  ', poziom) || imie || ' ' || nazwisko as struktura_org,
    poziom
FROM hierarchia
ORDER BY poziom, nazwisko;
```

#### Przykład - graf zależności:
```sql
-- Znajdź wszystkie komponenty zależne od komponentu A
WITH RECURSIVE zaleznosci AS (
    -- Anchor: komponent startowy
    SELECT id_komponentu, nazwa, 0 as poziom_zaleznosci
    FROM komponenty
    WHERE nazwa = 'Komponent A'
    
    UNION ALL
    
    -- Recursive: komponenty zależne
    SELECT k.id_komponentu, k.nazwa, z.poziom_zaleznosci + 1
    FROM komponenty k
    JOIN zalezy_od zal ON k.id_komponentu = zal.id_zaleznego
    JOIN zaleznosci z ON zal.id_od_czego = z.id_komponentu
    WHERE z.poziom_zaleznosci < 20
)
SELECT nazwa, poziom_zaleznosci
FROM zaleznosci
ORDER BY poziom_zaleznosci, nazwa;
```

### 3. **VALUES jako źródło danych**

```sql
-- VALUES jako tabela tymczasowa
SELECT *
FROM (VALUES 
    ('Jan', 'Kowalski', 25),
    ('Anna', 'Nowak', 30),
    ('Piotr', 'Wiśniewski', 28)
) AS people(imie, nazwisko, wiek);

-- JOIN z VALUES
SELECT p.imie, p.nazwisko, k.nazwa_kategorii
FROM (VALUES 
    (1, 'Premium'),
    (2, 'Standard'), 
    (3, 'Basic')
) AS k(id, nazwa_kategorii)
JOIN pracownicy p ON p.kategoria_id = k.id;

-- Pivot z VALUES
SELECT 
    miesiac,
    SUM(CASE WHEN kategoria = 'A' THEN wartosc ELSE 0 END) as kat_a,
    SUM(CASE WHEN kategoria = 'B' THEN wartosc ELSE 0 END) as kat_b
FROM sprzedaz s
CROSS JOIN (VALUES ('A'), ('B')) AS kat(kategoria)
GROUP BY miesiac;
```

## Funkcje okienkowe (Window Functions)

### 1. **Podstawy funkcji okienkowych**

#### Składnia:
```sql
function() OVER (
    [PARTITION BY kolumny]
    [ORDER BY kolumny [ASC|DESC]]
    [ROWS|RANGE BETWEEN start AND end]
)
```

#### Ranking functions:
```sql
SELECT 
    imie,
    nazwisko,
    pensja,
    dzial,
    
    -- Ranking (1, 2, 2, 4)
    RANK() OVER (ORDER BY pensja DESC) as ranking,
    
    -- Dense ranking (1, 2, 2, 3)  
    DENSE_RANK() OVER (ORDER BY pensja DESC) as dense_ranking,
    
    -- Row number (1, 2, 3, 4)
    ROW_NUMBER() OVER (ORDER BY pensja DESC) as row_num,
    
    -- Ranking w obrębie działu
    RANK() OVER (PARTITION BY dzial ORDER BY pensja DESC) as ranking_w_dziale,
    
    -- Percentyl
    PERCENT_RANK() OVER (ORDER BY pensja) as percentyl,
    
    -- Ntile - podział na kwartyle
    NTILE(4) OVER (ORDER BY pensja) as kwartyl
    
FROM pracownicy;
```

#### Aggregate functions jako window functions:
```sql
SELECT 
    data_zamowienia,
    wartosc,
    
    -- Running total (suma narastająca)
    SUM(wartosc) OVER (ORDER BY data_zamowienia) as suma_narastajaca,
    
    -- Moving average (średnia ruchoma z ostatnich 7 dni)
    AVG(wartosc) OVER (
        ORDER BY data_zamowienia 
        RANGE BETWEEN '6 days' PRECEDING AND CURRENT ROW
    ) as srednia_7_dni,
    
    -- Procent od sumy całkowitej
    wartosc / SUM(wartosc) OVER () * 100 as procent_sumy,
    
    -- Różnica od średniej w miesiącu
    wartosc - AVG(wartosc) OVER (
        PARTITION BY EXTRACT(YEAR FROM data_zamowienia),
                     EXTRACT(MONTH FROM data_zamowienia)
    ) as roznica_od_sredniej_miesiecznej

FROM zamowienia;
```

### 2. **Offset functions**

```sql
SELECT 
    data_zamowienia,
    wartosc,
    
    -- Poprzednia wartość
    LAG(wartosc, 1) OVER (ORDER BY data_zamowienia) as poprzednia_wartosc,
    
    -- Następna wartość  
    LEAD(wartosc, 1) OVER (ORDER BY data_zamowienia) as nastepna_wartosc,
    
    -- Pierwsza wartość w oknie
    FIRST_VALUE(wartosc) OVER (
        ORDER BY data_zamowienia 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as pierwsza_w_roku,
    
    -- Ostatnia wartość w oknie
    LAST_VALUE(wartosc) OVER (
        ORDER BY data_zamowienia 
        ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
    ) as ostatnia_w_roku,
    
    -- n-ta wartość
    NTH_VALUE(wartosc, 3) OVER (
        ORDER BY wartosc DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as trzecia_najwyzsza

FROM zamowienia
WHERE EXTRACT(YEAR FROM data_zamowienia) = 2024;
```

### 3. **Zaawansowane okna**

#### Frame clauses:
```sql
-- ROWS vs RANGE
SELECT 
    data_zamowienia,
    wartosc,
    
    -- ROWS - 3 fizyczne wiersze przed i po
    AVG(wartosc) OVER (
        ORDER BY data_zamowienia
        ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING
    ) as avg_rows,
    
    -- RANGE - wartości w zakresie dat
    AVG(wartosc) OVER (
        ORDER BY data_zamowienia
        RANGE BETWEEN '3 days' PRECEDING AND '3 days' FOLLOWING
    ) as avg_range

FROM zamowienia;
```

#### Named windows:
```sql
SELECT 
    imie,
    nazwisko, 
    pensja,
    dzial,
    
    RANK() OVER w as ranking_pensji,
    DENSE_RANK() OVER w as dense_ranking_pensji,
    AVG(pensja) OVER w as srednia_pensja_dzialu
    
FROM pracownicy
WINDOW w AS (PARTITION BY dzial ORDER BY pensja DESC);
```

## Zaawansowane podzapytania

### 1. **Skorelowane podzapytania**

```sql
-- Pracownicy z ponadprzeciętną pensją w swoim dziale
SELECT imie, nazwisko, pensja, dzial
FROM pracownicy p1
WHERE pensja > (
    SELECT AVG(pensja)
    FROM pracownicy p2
    WHERE p2.dzial = p1.dzial  -- Korelacja!
);

-- Klienci z zamówieniami powyżej średniej wartości
SELECT DISTINCT k.imie, k.nazwisko
FROM klienci k
WHERE EXISTS (
    SELECT 1
    FROM zamowienia z
    WHERE z.id_klienta = k.id_klienta
      AND z.wartosc > (
          SELECT AVG(wartosc)
          FROM zamowienia z2
          WHERE z2.id_klienta = k.id_klienta
      )
);
```

### 2. **EXISTS vs IN vs JOIN**

```sql
-- Znajdź klientów którzy złożyli zamówienia

-- 1. EXISTS (najczęściej najwydajniejsze)
SELECT k.imie, k.nazwisko
FROM klienci k
WHERE EXISTS (
    SELECT 1  -- Nie ma znaczenia co tu jest
    FROM zamowienia z
    WHERE z.id_klienta = k.id_klienta
);

-- 2. IN (może być problematyczne z NULL)
SELECT k.imie, k.nazwisko
FROM klienci k
WHERE k.id_klienta IN (
    SELECT z.id_klienta
    FROM zamowienia z
    WHERE z.id_klienta IS NOT NULL  -- Konieczne!
);

-- 3. JOIN (może zwrócić duplikaty)
SELECT DISTINCT k.imie, k.nazwisko
FROM klienci k
INNER JOIN zamowienia z ON k.id_klienta = z.id_klienta;

-- 4. Znajdź klientów BEZ zamówień
-- EXISTS (najlepsze)
SELECT k.imie, k.nazwisko
FROM klienci k
WHERE NOT EXISTS (
    SELECT 1
    FROM zamowienia z
    WHERE z.id_klienta = k.id_klienta
);

-- LEFT JOIN (alternatywa)
SELECT k.imie, k.nazwisko
FROM klienci k
LEFT JOIN zamowienia z ON k.id_klienta = z.id_klienta
WHERE z.id_klienta IS NULL;
```

### 3. **ALL, ANY, SOME**

```sql
-- Produkty droższe niż WSZYSTKIE produkty w kategorii 'Basic'
SELECT nazwa, cena
FROM produkty
WHERE cena > ALL (
    SELECT cena
    FROM produkty
    WHERE kategoria = 'Basic'
      AND cena IS NOT NULL
);

-- Produkty droższe niż KTÓRYKOLWIEK produkt w kategorii 'Premium'
SELECT nazwa, cena
FROM produkty
WHERE cena > ANY (
    SELECT cena
    FROM produkty
    WHERE kategoria = 'Premium'
      AND cena IS NOT NULL
);

-- SOME jest synonimem ANY
SELECT nazwa, cena
FROM produkty
WHERE cena > SOME (
    SELECT cena
    FROM produkty
    WHERE kategoria = 'Premium'
);

-- Równoważne alternatywy:
-- > ALL ≡ > MAX
-- > ANY ≡ > MIN
-- < ALL ≡ < MIN  
-- < ANY ≡ < MAX
```

## Zaawansowane GROUP BY

### 1. **GROUPING SETS**

```sql
-- Zamiast pisać wiele zapytań z UNION
-- Sprzedaż z różnymi poziomami agregacji
SELECT 
    rok,
    miesiac,
    kategoria,
    SUM(sprzedaz) as suma_sprzedazy
FROM dane_sprzedazy
GROUP BY GROUPING SETS (
    (rok, miesiac, kategoria),  -- Szczegółowo
    (rok, miesiac),             -- Per miesiąc
    (rok, kategoria),           -- Per kategoria w roku
    (rok),                      -- Per rok
    ()                          -- Suma całkowita
)
ORDER BY rok, miesiac, kategoria;
```

### 2. **ROLLUP**

```sql
-- ROLLUP - hierarchiczne agregacje (od szczegółu do ogółu)
SELECT 
    rok,
    miesiac,
    dzien,
    SUM(sprzedaz) as suma
FROM dane_sprzedazy
GROUP BY ROLLUP (rok, miesiac, dzien)
ORDER BY rok, miesiac, dzien;

-- Generuje grupy:
-- (rok, miesiac, dzien)  - najszczegółowiej
-- (rok, miesiac)         - suma per miesiąc
-- (rok)                  - suma per rok  
-- ()                     - suma całkowita

-- Można kontrolować poziomy
GROUP BY rok, ROLLUP (miesiac, dzien);  -- Zawsze grupuj po roku
```

### 3. **CUBE**

```sql
-- CUBE - wszystkie możliwe kombinacje wymiarów
SELECT 
    region,
    kategoria_produktu,
    kanal_sprzedazy,
    SUM(sprzedaz) as suma
FROM dane_sprzedazy
GROUP BY CUBE (region, kategoria_produktu, kanal_sprzedazy);

-- Generuje 2³ = 8 kombinacji:
-- (region, kategoria, kanal)     -- Wszystkie wymiary
-- (region, kategoria)            -- Bez kanału
-- (region, kanal)                -- Bez kategorii
-- (kategoria, kanal)             -- Bez regionu
-- (region)                       -- Tylko region
-- (kategoria)                    -- Tylko kategoria
-- (kanal)                        -- Tylko kanał
-- ()                             -- Suma całkowita
```

### 4. **GROUPING function**

```sql
-- GROUPING() - identyfikuje które kolumny są agregowane
SELECT 
    CASE GROUPING(region) 
        WHEN 1 THEN 'WSZYSTKIE REGIONY'
        ELSE region 
    END as region,
    
    CASE GROUPING(kategoria)
        WHEN 1 THEN 'WSZYSTKIE KATEGORIE'  
        ELSE kategoria
    END as kategoria,
    
    SUM(sprzedaz) as suma,
    
    -- Identyfikator typu agregacji
    CASE 
        WHEN GROUPING(region) = 0 AND GROUPING(kategoria) = 0 THEN 'Szczegóły'
        WHEN GROUPING(region) = 1 AND GROUPING(kategoria) = 0 THEN 'Per kategoria'
        WHEN GROUPING(region) = 0 AND GROUPING(kategoria) = 1 THEN 'Per region'
        ELSE 'Suma całkowita'
    END as typ_agregacji

FROM dane_sprzedazy
GROUP BY CUBE (region, kategoria)
ORDER BY GROUPING(region), region, GROUPING(kategoria), kategoria;
```

## Zaawansowane operacje na zbiorach

### 1. **UNION, INTERSECT, EXCEPT z modyfikatorami**

```sql
-- UNION ALL - zachowuje duplikaty (szybsze)
SELECT imie, nazwisko FROM pracownicy
UNION ALL
SELECT imie, nazwisko FROM klienci;

-- UNION DISTINCT - usuwa duplikaty (domyślne UNION)
SELECT imie, nazwisko FROM pracownicy
UNION DISTINCT
SELECT imie, nazwisko FROM klienci;

-- INTERSECT - część wspólna
SELECT email FROM pracownicy
INTERSECT 
SELECT email FROM klienci;

-- EXCEPT (lub MINUS w Oracle) - różnica zbiorów
SELECT email FROM klienci
EXCEPT
SELECT email FROM newsletter_unsubscribed;
```

### 2. **Złożone operacje zbiorowe**

```sql
-- Kombinacja operacji (pamiętaj o nawiasach!)
(
    SELECT produkt_id FROM bestsellery_2023
    UNION
    SELECT produkt_id FROM bestsellery_2024
)
EXCEPT
(
    SELECT produkt_id FROM produkty_wycofane
);

-- Priorities - nawiasy zmieniają kolejność
SELECT produkt_id FROM kategoria_a
UNION
(
    SELECT produkt_id FROM kategoria_b
    INTERSECT
    SELECT produkt_id FROM produkty_premium
);
```

## Zaawansowane sortowanie i limitowanie

### 1. **Złożone ORDER BY**

```sql
-- Sortowanie z CASE
SELECT imie, nazwisko, pensja, dzial
FROM pracownicy
ORDER BY 
    CASE dzial
        WHEN 'Management' THEN 1
        WHEN 'IT' THEN 2
        WHEN 'HR' THEN 3
        ELSE 4
    END,
    pensja DESC,
    nazwisko;

-- Sortowanie z funkcjami
SELECT nazwa_produktu, cena
FROM produkty
ORDER BY 
    LENGTH(nazwa_produktu) DESC,    -- Najdłuższe nazwy najpierw
    cena ASC NULLS LAST;            -- NULL na końcu

-- Sortowanie z wyrażeniami regularnymi (PostgreSQL)
SELECT email
FROM klienci
ORDER BY 
    SUBSTRING(email FROM '@(.*)$'),  -- Domena email
    email;
```

### 2. **LIMIT i OFFSET - paginacja**

```sql
-- Podstawowa paginacja
SELECT id, nazwa, cena
FROM produkty
ORDER BY id
LIMIT 20 OFFSET 40;  -- Strona 3 (0-based), 20 per page

-- Top N per group z LIMIT
SELECT DISTINCT dzial
FROM (
    SELECT dzial, imie, nazwisko,
           ROW_NUMBER() OVER (PARTITION BY dzial ORDER BY pensja DESC) as rn
    FROM pracownicy
) ranked
WHERE rn <= 3;  -- Top 3 w każdym dziale

-- FETCH FIRST (standard SQL)
SELECT *
FROM zamowienia
ORDER BY data_zamowienia DESC
FETCH FIRST 10 ROWS ONLY;

-- Alternatywy dla różnych SZBD:
-- PostgreSQL: LIMIT n OFFSET m
-- SQL Server: TOP n, OFFSET m ROWS FETCH NEXT n ROWS ONLY
-- MySQL: LIMIT m, n
-- Oracle: ROWNUM, FETCH FIRST
```

### 3. **Sampling - próbkowanie danych**

```sql
-- PostgreSQL - TABLESAMPLE
SELECT *
FROM duza_tabela 
TABLESAMPLE BERNOULLI(1);  -- 1% losowa próbka

SELECT *
FROM duza_tabela
TABLESAMPLE SYSTEM(5);     -- 5% próbka (szybsza, mniej losowa)

-- Random sampling z ORDER BY RANDOM()
SELECT *
FROM produkty
ORDER BY RANDOM()
LIMIT 100;  -- 100 losowych produktów

-- Stratified sampling
SELECT *
FROM (
    SELECT *, 
           ROW_NUMBER() OVER (PARTITION BY kategoria ORDER BY RANDOM()) as rn
    FROM produkty
) sampled
WHERE rn <= 10;  -- 10 losowych z każdej kategorii
```

## Optymalizacja zaawansowanych zapytań

### 1. **Analiza planów wykonania**

```sql
-- PostgreSQL
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT k.nazwa, COUNT(z.id)
FROM klienci k
LEFT JOIN zamowienia z ON k.id = z.id_klienta
GROUP BY k.id, k.nazwa
HAVING COUNT(z.id) > 5;

-- MySQL  
EXPLAIN FORMAT=JSON
SELECT k.nazwa, COUNT(z.id)
FROM klienci k
LEFT JOIN zamowienia z ON k.id = z.id_klienta
GROUP BY k.id, k.nazwa
HAVING COUNT(z.id) > 5;

-- SQL Server
SET STATISTICS IO ON;
SET STATISTICS TIME ON;
-- zapytanie
```

### 2. **Indeksy dla zaawansowanych zapytań**

```sql
-- Indeks pokrywający dla GROUP BY
CREATE INDEX idx_zamowienia_covering 
ON zamowienia(id_klienta, status) 
INCLUDE (wartosc, data_zamowienia);

-- Indeks częściowy
CREATE INDEX idx_aktywne_drog_produkty 
ON produkty(kategoria, cena) 
WHERE aktywny = TRUE AND cena > 100;

-- Indeks funkcyjny
CREATE INDEX idx_upper_email 
ON klienci(UPPER(email));

-- Indeks dla sortowania
CREATE INDEX idx_multi_sort 
ON zamowienia(status ASC, data_zamowienia DESC, wartosc ASC);
```

### 3. **Rewrite strategies**

```sql
-- 1. Zamiana EXISTS na JOIN
-- Wolno:
SELECT k.nazwa
FROM klienci k
WHERE EXISTS (
    SELECT 1 FROM zamowienia z WHERE z.id_klienta = k.id
      AND z.status = 'completed'
);

-- Szybciej:
SELECT DISTINCT k.nazwa
FROM klienci k
INNER JOIN zamowienia z ON k.id = z.id_klienta
WHERE z.status = 'completed';

-- 2. Zamiana skorelowanych podzapytań na window functions
-- Wolno:
SELECT 
    imie, nazwisko, pensja,
    (SELECT AVG(pensja) FROM pracownicy p2 WHERE p2.dzial = p1.dzial) as avg_pensja
FROM pracownicy p1;

-- Szybciej:
SELECT 
    imie, nazwisko, pensja,
    AVG(pensja) OVER (PARTITION BY dzial) as avg_pensja
FROM pracownicy;

-- 3. Early filtering
-- Wolno:
SELECT k.nazwa, z.wartosc
FROM klienci k
JOIN zamowienia z ON k.id = z.id_klienta
WHERE z.data_zamowienia >= '2024-01-01';

-- Szybciej:
SELECT k.nazwa, z.wartosc  
FROM klienci k
JOIN (
    SELECT id_klienta, wartosc
    FROM zamowienia 
    WHERE data_zamowienia >= '2024-01-01'
) z ON k.id = z.id_klienta;
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**

#### 1. **Czytelność zapytań**
```sql
-- Używaj aliasów
SELECT 
    k.imie,
    k.nazwisko,
    COUNT(z.id) as liczba_zamowien
FROM klienci k
LEFT JOIN zamowienia z ON k.id = z.id_klienta
GROUP BY k.id, k.imie, k.nazwisko;

-- Formatuj złożone zapytania
WITH high_value_customers AS (
    SELECT id_klienta, SUM(wartosc) as total_value
    FROM zamowienia
    WHERE data_zamowienia >= '2024-01-01'
    GROUP BY id_klienta
    HAVING SUM(wartosc) > 10000
)
SELECT 
    k.imie,
    k.nazwisko,
    hvc.total_value
FROM high_value_customers hvc
JOIN klienci k ON hvc.id_klienta = k.id;
```

#### 2. **Wydajność**
```sql
-- Używaj EXISTS zamiast IN z podkwerendami
WHERE EXISTS (SELECT 1 FROM ...) -- Lepiej niż IN

-- Unikaj SELECT * w produkcji
SELECT k.imie, k.email FROM klienci k;  -- Nie SELECT *

-- Używaj LIMIT dla exploracji danych
SELECT * FROM duza_tabela LIMIT 100;
```

#### 3. **Obsługa NULL**
```sql
-- Zawsze myśl o NULL w agregacjach
SELECT 
    AVG(COALESCE(ocena, 0)) as srednia_z_zerami,
    AVG(ocena) as srednia_bez_null
FROM recenzje;

-- NULL-safe porównania
WHERE (kolumna = 'wartość' OR kolumna IS NULL);
```

### ❌ **Złe praktyki:**

#### 1. **Problemy wydajnościowe**
```sql
-- ❌ Funkcje w WHERE (uniemożliwiają użycie indeksów)
WHERE UPPER(email) = 'USER@EXAMPLE.COM';

-- ✅ Lepiej
WHERE email = 'user@example.com';  -- + indeks funkcyjny jeśli potrzebny

-- ❌ Skorelowane podzapytania w SELECT
SELECT id, (SELECT COUNT(*) FROM orders WHERE customer_id = c.id)
FROM customers c;

-- ✅ Lepiej
SELECT c.id, COUNT(o.id)
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id;
```

#### 2. **Logiczne błędy**
```sql
-- ❌ Pomijanie DISTINCT w JOIN
SELECT k.nazwa
FROM klienci k
JOIN zamowienia z ON k.id = z.id_klienta;  -- Duplikaty!

-- ✅ Lepiej
SELECT DISTINCT k.nazwa FROM klienci k
JOIN zamowienia z ON k.id = z.id_klienta;

-- ❌ Błędne użycie GROUP BY z HAVING
SELECT dzial FROM pracownicy GROUP BY dzial HAVING pensja > 5000;  -- BŁĄD

-- ✅ Poprawnie
SELECT dzial FROM pracownicy WHERE pensja > 5000 GROUP BY dzial;
```

## Pułapki egzaminacyjne

### 1. **Kolejność wykonywania vs pisania**
```
Pisanie: SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY
Wykonywanie: FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY
```

### 2. **NULL w agregacjach**
```
COUNT(*): liczy wszystkie wiersze
COUNT(kolumna): liczy tylko nie-NULL
AVG(): ignoruje NULL w mianowniku
```

### 3. **HAVING vs WHERE**
```
WHERE: filtruje wiersze przed grupowaniem
HAVING: filtruje grupy po grupowaniu
WHERE nie może używać alias'ów z SELECT
```

### 4. **Funkcje okienkowe vs GROUP BY**
```
Window functions: zwracają wszystkie wiersze
GROUP BY: zwraca po jednym wierszu na grupę
Window functions mogą używać ORDER BY
```