# Podzapytania SQL - subqueries

## Definicja podzapytań

**Podzapytanie (subquery)** to **zapytanie SQL umieszczone wewnątrz innego zapytania SQL**. Podzapytanie może występować w różnych klauzulach: SELECT, FROM, WHERE, HAVING.

### Kluczowe cechy:
- **Zagnieżdżenie** - zapytanie w zapytaniu  
- **Kontekst** - może być niezależne lub skorelowane
- **Zwracane wartości** - skalar, pojedynczy wiersz, wiele wierszy, tabela
- **Wykonywanie** - może być wykonane raz lub wiele razy

### Alternatywne nazwy:
- **Subquery** - ang. termin
- **Inner query** - zapytanie wewnętrzne
- **Nested query** - zapytanie zagnieżdżone

## Typy podzapytań według umiejscowienia

### 1. **Podzapytania w SELECT**

#### Skalarne podzapytania:
```sql
-- Dodanie średniej pensji do każdego pracownika
SELECT 
    imie,
    nazwisko,
    pensja,
    (SELECT AVG(pensja) FROM pracownicy) as srednia_pensja,
    pensja - (SELECT AVG(pensja) FROM pracownicy) as roznica_od_sredniej
FROM pracownicy;

-- Liczba zamówień dla każdego klienta
SELECT 
    k.imie,
    k.nazwisko,
    (SELECT COUNT(*) 
     FROM zamowienia z 
     WHERE z.id_klienta = k.id_klienta) as liczba_zamowien
FROM klienci k;
```

#### Pułapki skalarnych podzapytań:
```sql
-- ❌ BŁĄD: Subquery zwraca więcej niż jedną wartość
SELECT 
    imie,
    (SELECT pensja FROM pracownicy WHERE dzial = 'IT')  -- Błąd jeśli >1 wynik!
FROM pracownicy;

-- ✅ POPRAWKA: Użyj funkcji agregującej
SELECT 
    imie,
    (SELECT MAX(pensja) FROM pracownicy WHERE dzial = 'IT') as max_pensja_it
FROM pracownicy;

-- ✅ ALTERNATYWA: Użyj LIMIT
SELECT 
    imie,
    (SELECT pensja FROM pracownicy WHERE dzial = 'IT' LIMIT 1) as pensja_it
FROM pracownicy;
```

### 2. **Podzapytania w FROM (Derived Tables)**

#### Tabele pochodne:
```sql
-- Agregacja przed głównym zapytaniem
SELECT 
    stats.dzial,
    stats.avg_pensja,
    p.imie,
    p.nazwisko,
    p.pensja
FROM (
    SELECT dzial, AVG(pensja) as avg_pensja
    FROM pracownicy 
    GROUP BY dzial
) stats
JOIN pracownicy p ON stats.dzial = p.dzial
WHERE p.pensja > stats.avg_pensja;

-- Ranking w podtabeli
SELECT 
    ranked.imie,
    ranked.nazwisko, 
    ranked.pensja,
    ranked.ranking
FROM (
    SELECT 
        imie,
        nazwisko,
        pensja,
        RANK() OVER (ORDER BY pensja DESC) as ranking
    FROM pracownicy
) ranked
WHERE ranked.ranking <= 10;
```

#### WITH clause (CTE - Common Table Expressions):
```sql
-- Czytelniejsza alternatywa dla derived tables
WITH pensje_stats AS (
    SELECT dzial, AVG(pensja) as avg_pensja
    FROM pracownicy 
    GROUP BY dzial
),
high_earners AS (
    SELECT p.imie, p.nazwisko, p.pensja, p.dzial
    FROM pracownicy p
    JOIN pensje_stats ps ON p.dzial = ps.dzial
    WHERE p.pensja > ps.avg_pensja
)
SELECT imie, nazwisko, pensja
FROM high_earners
ORDER BY pensja DESC;
```

### 3. **Podzapytania w WHERE**

#### Podstawowe porównania:
```sql
-- Pracownicy z pensją powyżej średniej
SELECT imie, nazwisko, pensja
FROM pracownicy
WHERE pensja > (SELECT AVG(pensja) FROM pracownicy);

-- Najstarszy pracownik w każdym dziale
SELECT imie, nazwisko, data_urodzenia, dzial
FROM pracownicy p1
WHERE data_urodzenia = (
    SELECT MIN(data_urodzenia)
    FROM pracownicy p2
    WHERE p2.dzial = p1.dzial
);
```

#### EXISTS:
```sql
-- Klienci którzy złożyli zamówienia
SELECT k.imie, k.nazwisko
FROM klienci k
WHERE EXISTS (
    SELECT 1  -- Zawartość SELECT nie ma znaczenia
    FROM zamowienia z
    WHERE z.id_klienta = k.id_klienta
);

-- Klienci którzy NIE złożyli zamówień
SELECT k.imie, k.nazwisko
FROM klienci k
WHERE NOT EXISTS (
    SELECT 1
    FROM zamowienia z
    WHERE z.id_klienta = k.id_klienta
);

-- Produkty które nie są w żadnym zamówieniu
SELECT p.nazwa, p.cena
FROM produkty p
WHERE NOT EXISTS (
    SELECT 1
    FROM pozycje_zamowien pz
    WHERE pz.id_produktu = p.id_produktu
);
```

#### IN i NOT IN:
```sql
-- Pracownicy w określonych działach
SELECT imie, nazwisko, dzial
FROM pracownicy
WHERE dzial IN ('IT', 'HR', 'Marketing');

-- Z podzapytaniem
SELECT imie, nazwisko, dzial
FROM pracownicy
WHERE dzial IN (
    SELECT nazwa_dzialu
    FROM dzialy
    WHERE budzet > 100000
);

-- ⚠️ UWAGA na NULL z NOT IN:
SELECT imie, nazwisko
FROM pracownicy
WHERE id_dzialu NOT IN (
    SELECT id_dzialu
    FROM dzialy
    WHERE aktywny = TRUE
    AND id_dzialu IS NOT NULL  -- Konieczne!
);
```

#### Operatory ALL, ANY, SOME:
```sql
-- Produkty droższe niż WSZYSTKIE produkty podstawowe
SELECT nazwa, cena
FROM produkty
WHERE cena > ALL (
    SELECT cena
    FROM produkty
    WHERE kategoria = 'podstawowa'
    AND cena IS NOT NULL
);

-- Produkty droższe niż KTÓRYKÓLWIEK produkt premium
SELECT nazwa, cena
FROM produkty
WHERE cena > ANY (
    SELECT cena
    FROM produkty
    WHERE kategoria = 'premium'
    AND cena IS NOT NULL
);

-- SOME jest synonimem ANY
SELECT nazwa, cena
FROM produkty
WHERE cena > SOME (
    SELECT cena
    FROM produkty
    WHERE kategoria = 'premium'
);
```

### 4. **Podzapytania w HAVING**

```sql
-- Działy z średnią pensją powyżej średniej całkowitej
SELECT 
    dzial,
    AVG(pensja) as srednia_dzialu
FROM pracownicy
GROUP BY dzial
HAVING AVG(pensja) > (
    SELECT AVG(pensja)
    FROM pracownicy
);

-- Klienci z liczbą zamówień powyżej średniej
SELECT 
    id_klienta,
    COUNT(*) as liczba_zamowien
FROM zamowienia
GROUP BY id_klienta
HAVING COUNT(*) > (
    SELECT AVG(order_count)
    FROM (
        SELECT COUNT(*) as order_count
        FROM zamowienia
        GROUP BY id_klienta
    ) counts
);
```

## Typy podzapytań według zależności

### 1. **Podzapytania niezależne (Uncorrelated)**

#### Charakterystyka:
- **Wykonywane raz** na początku
- **Nie zależą** od wartości z zapytania głównego
- **Można je wykonać osobno**

```sql
-- Przykład niezależnego podzapytania
SELECT imie, nazwisko, pensja
FROM pracownicy
WHERE pensja > (
    SELECT AVG(pensja)    -- Wykonane tylko raz
    FROM pracownicy
);

-- Można to rozbić na części:
-- 1. SELECT AVG(pensja) FROM pracownicy;  → np. 5000
-- 2. SELECT imie, nazwisko, pensja FROM pracownicy WHERE pensja > 5000;
```

#### Optymalizacja:
```sql
-- Podzapytanie niezależne można często zastąpić JOIN'em
-- Original:
SELECT p1.imie, p1.nazwisko
FROM pracownicy p1
WHERE p1.pensja > (
    SELECT AVG(p2.pensja)
    FROM pracownicy p2
);

-- Optimized:
SELECT p1.imie, p1.nazwisko
FROM pracownicy p1
CROSS JOIN (
    SELECT AVG(pensja) as avg_pensja
    FROM pracownicy
) avg_data
WHERE p1.pensja > avg_data.avg_pensja;
```

### 2. **Podzapytania skorelowane (Correlated)**

#### Charakterystyka:
- **Wykonywane wielokrotnie** - dla każdego wiersza głównego zapytania
- **Zależą** od wartości z zapytania głównego
- **Nie można ich wykonać osobno**

```sql
-- Pracownicy z pensją powyżej średniej w swoim dziale
SELECT p1.imie, p1.nazwisko, p1.pensja, p1.dzial
FROM pracownicy p1
WHERE p1.pensja > (
    SELECT AVG(p2.pensja)
    FROM pracownicy p2
    WHERE p2.dzial = p1.dzial  -- KORELACJA!
);

-- To podzapytanie wykonuje się osobno dla każdego działu
```

#### Optymalizacja skorelowanych podzapytań:
```sql
-- Zamiast skorelowanego subquery
SELECT p1.imie, p1.nazwisko, p1.pensja
FROM pracownicy p1
WHERE p1.pensja > (
    SELECT AVG(p2.pensja)
    FROM pracownicy p2
    WHERE p2.dzial = p1.dzial
);

-- Użyj window function (szybciej!)
SELECT imie, nazwisko, pensja
FROM (
    SELECT 
        imie, 
        nazwisko, 
        pensja,
        AVG(pensja) OVER (PARTITION BY dzial) as avg_pensja_dzial
    FROM pracownicy
) ranked
WHERE pensja > avg_pensja_dzial;
```

## Zaawansowane zastosowania podzapytań

### 1. **Top N per group**

#### Problem:
Znaleźć N najlepszych elementów w każdej grupie.

#### Rozwiązanie z podzapytaniem:
```sql
-- 3 najlepiej zarabiających w każdym dziale
SELECT p1.imie, p1.nazwisko, p1.pensja, p1.dzial
FROM pracownicy p1
WHERE (
    SELECT COUNT(*)
    FROM pracownicy p2
    WHERE p2.dzial = p1.dzial
      AND p2.pensja >= p1.pensja
) <= 3
ORDER BY p1.dzial, p1.pensja DESC;

-- Alternatywa z window functions (lepiej wydajnościowo):
SELECT imie, nazwisko, pensja, dzial
FROM (
    SELECT 
        imie, nazwisko, pensja, dzial,
        ROW_NUMBER() OVER (PARTITION BY dzial ORDER BY pensja DESC) as rn
    FROM pracownicy
) ranked
WHERE rn <= 3;
```

### 2. **Rekurencyjne hierarchie z podzapytaniami**

```sql
-- Znajdź wszystkich podwładnych konkretnego managera (bez CTE)
-- Poziom 1: bezpośredni podwładni
SELECT p1.imie, p1.nazwisko, 1 as poziom
FROM pracownicy p1
WHERE p1.id_szefa = 100  -- ID managera

UNION ALL

-- Poziom 2: podwładni podwładnych
SELECT p2.imie, p2.nazwisko, 2 as poziom
FROM pracownicy p2
WHERE p2.id_szefa IN (
    SELECT p1.id
    FROM pracownicy p1
    WHERE p1.id_szefa = 100
)

UNION ALL

-- Poziom 3: itd...
-- (Ograniczone do konkretnej liczby poziomów)
```

### 3. **Running totals z podzapytaniami**

```sql
-- Suma narastająca zamówień (bez window functions)
SELECT 
    z1.data_zamowienia,
    z1.wartosc,
    (
        SELECT SUM(z2.wartosc)
        FROM zamowienia z2
        WHERE z2.data_zamowienia <= z1.data_zamowienia
    ) as suma_narastajaca
FROM zamowienia z1
ORDER BY z1.data_zamowienia;

-- Nowoczesna alternatywa (znacznie szybsza):
SELECT 
    data_zamowienia,
    wartosc,
    SUM(wartosc) OVER (ORDER BY data_zamowienia) as suma_narastajaca
FROM zamowienia
ORDER BY data_zamowienia;
```

### 4. **Gap analysis - znajdowanie luk**

```sql
-- Znajdź brakujące ID w sekwencji
WITH RECURSIVE liczby AS (
    SELECT 1 as n
    UNION ALL
    SELECT n + 1
    FROM liczby
    WHERE n < (SELECT MAX(id) FROM produkty)
)
SELECT n as brakujace_id
FROM liczby
WHERE n NOT IN (SELECT id FROM produkty WHERE id IS NOT NULL);

-- Alternatywa z podzapytaniem:
SELECT t1.id + 1 as start_gap,
       (SELECT MIN(t3.id) - 1 
        FROM produkty t3 
        WHERE t3.id > t1.id) as end_gap
FROM produkty t1
WHERE NOT EXISTS (
    SELECT 1 
    FROM produkty t2 
    WHERE t2.id = t1.id + 1
)
AND t1.id < (SELECT MAX(id) FROM produkty);
```

## Wydajność podzapytań

### 1. **Analiza kosztów**

#### Sposób analizowania:
```sql
-- PostgreSQL
EXPLAIN (ANALYZE, BUFFERS) 
SELECT p1.imie
FROM pracownicy p1
WHERE p1.pensja > (
    SELECT AVG(p2.pensja) 
    FROM pracownicy p2 
    WHERE p2.dzial = p1.dzial
);

-- Szukaj:
-- - SubPlan/InitPlan nodes
-- - Liczba wykonań (loops)
-- - Czas wykonania
```

#### Typowe problemy wydajnościowe:
```sql
-- ❌ PROBLEM: Skorelowane subquery w SELECT
SELECT 
    k.imie,
    (SELECT COUNT(*) FROM zamowienia z WHERE z.id_klienta = k.id) as cnt
FROM klienci k;
-- Wykonuje subquery dla każdego klienta!

-- ✅ ROZWIĄZANIE: LEFT JOIN z GROUP BY
SELECT 
    k.imie,
    COALESCE(z.cnt, 0) as cnt
FROM klienci k
LEFT JOIN (
    SELECT id_klienta, COUNT(*) as cnt
    FROM zamowienia
    GROUP BY id_klienta
) z ON k.id = z.id_klienta;
```

### 2. **Strategie optymalizacji**

#### 1. Zamiana na JOIN:
```sql
-- Wolno: EXISTS
SELECT k.imie
FROM klienci k
WHERE EXISTS (
    SELECT 1 FROM zamowienia z WHERE z.id_klienta = k.id
);

-- Szybciej: INNER JOIN
SELECT DISTINCT k.imie
FROM klienci k
INNER JOIN zamowienia z ON k.id = z.id_klienta;
```

#### 2. Materialization:
```sql
-- Wolno: Powtarzające się podzapytanie
SELECT p1.imie
FROM pracownicy p1
WHERE p1.pensja > (SELECT AVG(pensja) FROM pracownicy)
   OR p1.pensja < (SELECT AVG(pensja) FROM pracownicy) * 0.5;

-- Szybciej: Materialized subquery
WITH avg_pensja AS (
    SELECT AVG(pensja) as avg_val FROM pracownicy
)
SELECT p1.imie
FROM pracownicy p1, avg_pensja
WHERE p1.pensja > avg_val OR p1.pensja < avg_val * 0.5;
```

#### 3. Early filtering:
```sql
-- Wolno: Filtruj po JOIN
SELECT p.imie
FROM pracownicy p
JOIN dzialy d ON p.id_dzialu = d.id
WHERE d.lokalizacja = 'Warszawa'
  AND p.pensja > 5000;

-- Szybciej: Pre-filter w subquery
SELECT p.imie
FROM (
    SELECT imie, id_dzialu 
    FROM pracownicy 
    WHERE pensja > 5000  -- Filter early!
) p
JOIN dzialy d ON p.id_dzialu = d.id
WHERE d.lokalizacja = 'Warszawa';
```

## Zaawansowane przykłady

### 1. **Pivot z podzapytaniami**

```sql
-- Pivot: miesięczna sprzedaż jako kolumny
SELECT 
    kategoria,
    (SELECT SUM(wartosc) FROM sprzedaz s WHERE s.kategoria = p.kategoria AND EXTRACT(MONTH FROM data) = 1) as sty,
    (SELECT SUM(wartosc) FROM sprzedaz s WHERE s.kategoria = p.kategoria AND EXTRACT(MONTH FROM data) = 2) as lut,
    (SELECT SUM(wartosc) FROM sprzedaz s WHERE s.kategoria = p.kategoria AND EXTRACT(MONTH FROM data) = 3) as mar
FROM (SELECT DISTINCT kategoria FROM sprzedaz) p;

-- Nowocześniej z CASE:
SELECT 
    kategoria,
    SUM(CASE WHEN EXTRACT(MONTH FROM data) = 1 THEN wartosc ELSE 0 END) as sty,
    SUM(CASE WHEN EXTRACT(MONTH FROM data) = 2 THEN wartosc ELSE 0 END) as lut,
    SUM(CASE WHEN EXTRACT(MONTH FROM data) = 3 THEN wartosc ELSE 0 END) as mar
FROM sprzedaz
GROUP BY kategoria;
```

### 2. **Ranking z ties**

```sql
-- Znajdź wszystkich pracowników z najwyższą pensją w każdym dziale
SELECT imie, nazwisko, pensja, dzial
FROM pracownicy p1
WHERE pensja = (
    SELECT MAX(pensja)
    FROM pracownicy p2
    WHERE p2.dzial = p1.dzial
);

-- Lub z window function:
SELECT imie, nazwisko, pensja, dzial
FROM (
    SELECT 
        imie, nazwisko, pensja, dzial,
        RANK() OVER (PARTITION BY dzial ORDER BY pensja DESC) as rnk
    FROM pracownicy
) ranked
WHERE rnk = 1;
```

### 3. **Conditional aggregation**

```sql
-- Porównanie sprzedaży rok do roku
SELECT 
    produkty.nazwa,
    (SELECT SUM(wartosc) 
     FROM sprzedaz s 
     WHERE s.id_produktu = produkty.id 
       AND EXTRACT(YEAR FROM s.data) = 2023) as sprzedaz_2023,
    (SELECT SUM(wartosc) 
     FROM sprzedaz s 
     WHERE s.id_produktu = produkty.id 
       AND EXTRACT(YEAR FROM s.data) = 2024) as sprzedaz_2024
FROM produkty;

-- Efektywniej:
SELECT 
    p.nazwa,
    SUM(CASE WHEN EXTRACT(YEAR FROM s.data) = 2023 THEN s.wartosc ELSE 0 END) as sprzedaz_2023,
    SUM(CASE WHEN EXTRACT(YEAR FROM s.data) = 2024 THEN s.wartosc ELSE 0 END) as sprzedaz_2024
FROM produkty p
LEFT JOIN sprzedaz s ON p.id = s.id_produktu
WHERE EXTRACT(YEAR FROM s.data) IN (2023, 2024) OR s.data IS NULL
GROUP BY p.id, p.nazwa;
```

## Ograniczenia i pułapki

### 1. **NULL w podzapytaniach**

```sql
-- ⚠️ PUŁAPKA: NOT IN z NULL
SELECT imie FROM pracownicy
WHERE id_dzialu NOT IN (
    SELECT id_dzialu FROM dzialy WHERE aktywny = FALSE
);
-- Jeśli ANY id_dzialu jest NULL, wynik będzie pusty!

-- ✅ BEZPIECZNE rozwiązanie:
SELECT imie FROM pracownicy
WHERE id_dzialu NOT IN (
    SELECT id_dzialu FROM dzialy 
    WHERE aktywny = FALSE AND id_dzialu IS NOT NULL
);

-- ✅ ALTERNATYWA z NOT EXISTS:
SELECT imie FROM pracownicy p
WHERE NOT EXISTS (
    SELECT 1 FROM dzialy d 
    WHERE d.id_dzialu = p.id_dzialu AND d.aktywny = FALSE
);
```

### 2. **Limity zagnieżdżenia**

```sql
-- Większość SZBD ma limity głębokości zagnieżdżenia (32-255 poziomów)
-- Unikaj nadmiernego zagnieżdżania:

-- ❌ Trudne do czytania i debugowania:
SELECT *
FROM tabela1
WHERE col1 IN (
    SELECT col2 FROM tabela2
    WHERE col3 > (
        SELECT AVG(col4) FROM tabela3
        WHERE col5 IN (
            SELECT col6 FROM tabela4
            WHERE col7 = 'value'
        )
    )
);

-- ✅ Lepiej z CTE:
WITH avg_values AS (
    SELECT AVG(col4) as avg_col4
    FROM tabela3
    WHERE col5 IN (SELECT col6 FROM tabela4 WHERE col7 = 'value')
),
filtered_tabela2 AS (
    SELECT col2
    FROM tabela2, avg_values
    WHERE col3 > avg_col4
)
SELECT *
FROM tabela1
WHERE col1 IN (SELECT col2 FROM filtered_tabela2);
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**

#### 1. **Czytelność**
```sql
-- Używaj wcięć i formatowania
SELECT p1.imie, p1.nazwisko
FROM pracownicy p1
WHERE p1.pensja > (
    SELECT AVG(p2.pensja)
    FROM pracownicy p2
    WHERE p2.dzial = p1.dzial
);

-- Używaj CTE dla złożonych przypadków
WITH department_averages AS (
    SELECT dzial, AVG(pensja) as avg_pensja
    FROM pracownicy
    GROUP BY dzial
)
SELECT p.imie, p.nazwisko
FROM pracownicy p
JOIN department_averages da ON p.dzial = da.dzial
WHERE p.pensja > da.avg_pensja;
```

#### 2. **Wydajność**
```sql
-- Preferuj EXISTS nad IN dla dużych zbiorów
WHERE EXISTS (SELECT 1 FROM ...) -- Lepiej niż IN

-- Używaj LIMIT w subqueries gdzie to możliwe
WHERE id IN (SELECT id FROM large_table LIMIT 1000);

-- Materialized subqueries dla powtarzających się obliczeń
WITH expensive_calc AS (SELECT expensive_function())
SELECT ... FROM table1, expensive_calc
UNION ALL
SELECT ... FROM table2, expensive_calc;
```

#### 3. **Bezpieczeństwo NULL**
```sql
-- Zawsze sprawdzaj NULL w NOT IN
WHERE col NOT IN (SELECT val FROM tab WHERE val IS NOT NULL);

-- Używaj COALESCE dla skalarnych subqueries
SELECT COALESCE(
    (SELECT max_val FROM subtable WHERE condition), 
    0
) as result;
```

### ❌ **Złe praktyki:**

```sql
-- ❌ Nieefektywne skorelowane subquery w SELECT
SELECT id, (SELECT COUNT(*) FROM orders WHERE customer_id = c.id)
FROM customers c;

-- ❌ Ignorowanie NULL w NOT IN
WHERE id NOT IN (SELECT foreign_id FROM other_table);

-- ❌ Nadmierne zagnieżdżanie
SELECT * FROM t1 WHERE c1 IN (SELECT c2 FROM t2 WHERE c3 IN (...));

-- ❌ Powtarzające się subqueries
WHERE val > (SELECT AVG(x) FROM tab) AND val < (SELECT AVG(x) FROM tab) * 2;
```

## Pułapki egzaminacyjne

### 1. **Typy podzapytań**
```
Skalarne: zwracają jedną wartość
Wierszowe: zwracają jeden wiersz
Tabelowe: zwracają wiele wierszy/kolumn
```

### 2. **Skorelowane vs niezależne**
```
Niezależne: wykonywane raz
Skorelowane: wykonywane dla każdego wiersza głównego zapytania
```

### 3. **EXISTS vs IN**
```
EXISTS: szybsze dla dużych zbiorów, bezpieczne z NULL
IN: może być problematyczne z NULL, często wolniejsze
```

### 4. **ALL vs ANY**
```
> ALL: większe niż WSZYSTKIE (> MAX)
> ANY: większe niż KTÓREKOLWIEK (> MIN)
< ALL: mniejsze niż WSZYSTKIE (< MIN)
< ANY: mniejsze niż KTÓREKOLWIEK (< MAX)
```