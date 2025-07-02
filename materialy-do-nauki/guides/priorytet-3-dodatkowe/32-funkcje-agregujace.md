# Funkcje agregujące i GROUP BY

## Definicja funkcji agregujących

**Funkcje agregujące** to funkcje SQL, które **operują na zbiorach wierszy** i zwracają **pojedynczą wartość** będącą wynikiem obliczeń na całym zbiorze.

### Kluczowe cechy:
- **Zbiorcze działanie** - operują na wielu wierszach jednocześnie
- **Jeden wynik** - zwracają pojedynczą wartość dla grupy
- **Ignorują NULL** - większość funkcji pomija wartości NULL
- **Używane z GROUP BY** - do tworzenia grup

### Podstawowe funkcje:
```sql
COUNT()    -- Liczba wierszy/wartości
SUM()      -- Suma wartości
AVG()      -- Średnia arytmetyczna  
MIN()      -- Wartość minimalna
MAX()      -- Wartość maksymalna
```

## Podstawowe funkcje agregujące

### 1. **COUNT - liczenie**

#### Wersje COUNT:
```sql
-- COUNT(*) - liczy wszystkie wiersze (włącznie z NULL)
SELECT COUNT(*) as total_rows
FROM pracownicy;

-- COUNT(kolumna) - liczy nie-NULL wartości
SELECT COUNT(telefon) as pracownicy_z_telefonem
FROM pracownicy;

-- COUNT(DISTINCT kolumna) - liczy unikalne nie-NULL wartości
SELECT COUNT(DISTINCT dzial) as liczba_dzialow
FROM pracownicy;

-- Porównanie różnych COUNT
SELECT 
    COUNT(*) as wszystkie_wiersze,
    COUNT(telefon) as z_numerem_telefonu,
    COUNT(DISTINCT dzial) as unikalne_dzialy,
    COUNT(*) - COUNT(telefon) as bez_telefonu
FROM pracownicy;
```

#### Praktyczne zastosowania COUNT:
```sql
-- Zliczanie z warunkami przez CASE
SELECT 
    COUNT(CASE WHEN pensja > 5000 THEN 1 END) as wysokie_pensje,
    COUNT(CASE WHEN pensja <= 5000 THEN 1 END) as niskie_pensje,
    COUNT(CASE WHEN dzial = 'IT' THEN 1 END) as pracownicy_it
FROM pracownicy;

-- Conditional counting (PostgreSQL)
SELECT 
    COUNT(*) FILTER (WHERE pensja > 5000) as wysokie_pensje,
    COUNT(*) FILTER (WHERE dzial = 'IT') as pracownicy_it
FROM pracownicy;
```

### 2. **SUM - sumowanie**

```sql
-- Podstawowe sumowanie
SELECT 
    SUM(pensja) as suma_pensji,
    SUM(DISTINCT pensja) as suma_unikalnych_pensji
FROM pracownicy;

-- SUM z warunkami
SELECT 
    SUM(CASE WHEN dzial = 'IT' THEN pensja ELSE 0 END) as suma_pensji_it,
    SUM(CASE WHEN wiek > 30 THEN 1 ELSE 0 END) as liczba_starszych,
    SUM(COALESCE(premia, 0)) as suma_premii  -- NULL traktowane jako 0
FROM pracownicy;

-- SUM dla analiz finansowych
SELECT 
    SUM(kwota) as przychod_total,
    SUM(CASE WHEN typ = 'income' THEN kwota ELSE 0 END) as przychody,
    SUM(CASE WHEN typ = 'expense' THEN kwota ELSE 0 END) as wydatki,
    SUM(CASE WHEN typ = 'income' THEN kwota ELSE -kwota END) as saldo
FROM transakcje;
```

### 3. **AVG - średnia**

```sql
-- Podstawowa średnia
SELECT AVG(pensja) as srednia_pensja
FROM pracownicy;

-- ⚠️ UWAGA: AVG ignoruje NULL w mianowniku!
SELECT 
    AVG(pensja) as avg_ignoruje_null,
    SUM(pensja) / COUNT(*) as avg_z_nullami_jako_zero,
    SUM(COALESCE(pensja, 0)) / COUNT(*) as avg_null_jako_zero
FROM pracownicy;

-- Średnia ważona
SELECT 
    SUM(ocena * waga) / SUM(waga) as srednia_wazona
FROM oceny_studentow;

-- Średnia z wykluczeniem ekstremów (trimmed mean)
SELECT AVG(pensja) as trimmed_mean
FROM (
    SELECT pensja
    FROM pracownicy
    WHERE pensja BETWEEN (
        SELECT PERCENTILE_CONT(0.1) WITHIN GROUP (ORDER BY pensja) FROM pracownicy
    ) AND (
        SELECT PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY pensja) FROM pracownicy
    )
) trimmed_data;
```

### 4. **MIN i MAX**

```sql
-- Podstawowe MIN/MAX
SELECT 
    MIN(pensja) as min_pensja,
    MAX(pensja) as max_pensja,
    MAX(data_zatrudnienia) as ostatnie_zatrudnienie,
    MIN(data_urodzenia) as najstarszy_pracownik
FROM pracownicy;

-- MIN/MAX z tekstami (porządek alfabetyczny)
SELECT 
    MIN(nazwisko) as alfabetycznie_pierwszy,
    MAX(nazwisko) as alfabetycznie_ostatni
FROM pracownicy;

-- MIN/MAX z datami
SELECT 
    MIN(data_zamowienia) as pierwsze_zamowienie,
    MAX(data_zamowienia) as ostatnie_zamowienie,
    MAX(data_zamowienia) - MIN(data_zamowienia) as okres_dzialania
FROM zamowienia;

-- Znajdowanie rekordów z wartościami MIN/MAX
SELECT p1.*
FROM pracownicy p1
WHERE p1.pensja = (SELECT MAX(pensja) FROM pracownicy p2 WHERE p2.dzial = p1.dzial);
```

## GROUP BY - grupowanie danych

### 1. **Podstawy GROUP BY**

#### Składnia:
```sql
SELECT 
    kolumny_grupujace,
    funkcje_agregujace
FROM tabela
WHERE warunki_przed_grupowaniem
GROUP BY kolumny_grupujace
HAVING warunki_po_grupowaniu
ORDER BY kolumny_sortowania;
```

#### Zasady GROUP BY:
```sql
-- Wszystkie kolumny w SELECT (oprócz agregujących) muszą być w GROUP BY
SELECT 
    dzial,
    AVG(pensja) as srednia_pensja
FROM pracownicy
GROUP BY dzial;

-- ❌ BŁĄD: imie nie jest w GROUP BY ani nie jest funkcją agregującą
SELECT 
    dzial,
    imie,           -- BŁĄD!
    AVG(pensja)
FROM pracownicy
GROUP BY dzial;

-- ✅ POPRAWNIE: wszystkie nie-agregujące kolumny w GROUP BY
SELECT 
    dzial,
    stanowisko,
    AVG(pensja) as srednia_pensja
FROM pracownicy
GROUP BY dzial, stanowisko;
```

### 2. **Przykłady praktyczne GROUP BY**

#### Analiza sprzedaży:
```sql
-- Sprzedaż per miesiąc
SELECT 
    EXTRACT(YEAR FROM data_zamowienia) as rok,
    EXTRACT(MONTH FROM data_zamowienia) as miesiac,
    COUNT(*) as liczba_zamowien,
    SUM(wartosc) as suma_sprzedazy,
    AVG(wartosc) as srednia_wartosc_zamowienia,
    MIN(wartosc) as min_zamowienie,
    MAX(wartosc) as max_zamowienie
FROM zamowienia
GROUP BY 
    EXTRACT(YEAR FROM data_zamowienia),
    EXTRACT(MONTH FROM data_zamowienia)
ORDER BY rok, miesiac;
```

#### Analiza klientów:
```sql
-- Segmentacja klientów według aktywności
SELECT 
    CASE 
        WHEN COUNT(*) >= 10 THEN 'VIP'
        WHEN COUNT(*) >= 5 THEN 'Aktywny'
        WHEN COUNT(*) >= 1 THEN 'Sporadyczny'
        ELSE 'Nieaktywny'
    END as segment,
    COUNT(DISTINCT id_klienta) as liczba_klientow,
    AVG(total_wartosc) as srednia_wartosc
FROM (
    SELECT 
        id_klienta,
        COUNT(*) as liczba_zamowien,
        SUM(wartosc) as total_wartosc
    FROM zamowienia
    GROUP BY id_klienta
) klient_stats
GROUP BY 
    CASE 
        WHEN COUNT(*) >= 10 THEN 'VIP'
        WHEN COUNT(*) >= 5 THEN 'Aktywny'
        WHEN COUNT(*) >= 1 THEN 'Sporadyczny'
        ELSE 'Nieaktywny'
    END;
```

### 3. **GROUP BY z warunkami**

#### HAVING - filtrowanie grup:
```sql
-- Działy z więcej niż 5 pracownikami i średnią pensją > 4000
SELECT 
    dzial,
    COUNT(*) as liczba_pracownikow,
    AVG(pensja) as srednia_pensja
FROM pracownicy
GROUP BY dzial
HAVING COUNT(*) > 5 
   AND AVG(pensja) > 4000
ORDER BY srednia_pensja DESC;

-- HAVING z podzapytaniami
SELECT 
    dzial,
    AVG(pensja) as srednia_pensja
FROM pracownicy
GROUP BY dzial
HAVING AVG(pensja) > (
    SELECT AVG(pensja) * 1.1
    FROM pracownicy
);  -- Działy z pensją 10% powyżej średniej
```

#### WHERE vs HAVING:
```sql
-- WHERE: filtruje wiersze PRZED grupowaniem
-- HAVING: filtruje grupy PO grupowaniu

SELECT 
    dzial,
    COUNT(*) as liczba_starszych_pracownikow,
    AVG(pensja) as srednia_pensja
FROM pracownicy
WHERE wiek > 30                    -- WHERE: tylko starsi pracownicy
GROUP BY dzial
HAVING COUNT(*) > 2;               -- HAVING: tylko działy z >2 starszymi
```

## Zaawansowane funkcje agregujące

### 1. **Funkcje statystyczne**

#### PostgreSQL:
```sql
SELECT 
    dzial,
    COUNT(*) as n,
    AVG(pensja) as srednia,
    STDDEV(pensja) as odchylenie_standardowe,
    VARIANCE(pensja) as wariancja,
    
    -- Percentyle
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY pensja) as q1,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pensja) as mediana,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY pensja) as q3,
    
    -- Miary rozkładu
    MODE() WITHIN GROUP (ORDER BY stanowisko) as najpopularniejsze_stanowisko
FROM pracownicy
GROUP BY dzial;
```

#### SQL Server:
```sql
SELECT 
    dzial,
    COUNT(*) as n,
    AVG(pensja) as srednia,
    STDEV(pensja) as odchylenie_standardowe,
    VAR(pensja) as wariancja,
    
    -- Percentyle
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pensja) 
        OVER (PARTITION BY dzial) as mediana
FROM pracownicy;
```

### 2. **String aggregation**

#### PostgreSQL:
```sql
-- STRING_AGG - konkatenacja wartości w grupie
SELECT 
    dzial,
    COUNT(*) as liczba_pracownikow,
    STRING_AGG(imie || ' ' || nazwisko, ', ' ORDER BY nazwisko) as lista_pracownikow,
    STRING_AGG(DISTINCT stanowisko, ', ') as stanowiska_w_dziale
FROM pracownicy
GROUP BY dzial;

-- Przykład wyniku:
-- IT | 5 | Jan Kowalski, Anna Nowak, Piotr Wiśniewski | Developer, Senior Developer, Team Lead
```

#### MySQL:
```sql
-- GROUP_CONCAT
SELECT 
    dzial,
    GROUP_CONCAT(
        CONCAT(imie, ' ', nazwisko) 
        ORDER BY nazwisko 
        SEPARATOR ', '
    ) as lista_pracownikow
FROM pracownicy
GROUP BY dzial;
```

#### SQL Server:
```sql
-- STRING_AGG (SQL Server 2017+)
SELECT 
    dzial,
    STRING_AGG(imie + ' ' + nazwisko, ', ') WITHIN GROUP (ORDER BY nazwisko) as lista_pracownikow
FROM pracownicy
GROUP BY dzial;

-- Starsze wersje - FOR XML PATH
SELECT 
    dzial,
    STUFF((
        SELECT ', ' + imie + ' ' + nazwisko
        FROM pracownicy p2
        WHERE p2.dzial = p1.dzial
        ORDER BY nazwisko
        FOR XML PATH('')
    ), 1, 2, '') as lista_pracownikow
FROM pracownicy p1
GROUP BY dzial;
```

### 3. **Array aggregation (PostgreSQL)**

```sql
-- ARRAY_AGG - tworzenie tablic
SELECT 
    dzial,
    ARRAY_AGG(imie ORDER BY imie) as imiona,
    ARRAY_AGG(DISTINCT stanowisko) as stanowiska,
    ARRAY_AGG(pensja ORDER BY pensja DESC) as pensje_malejaco
FROM pracownicy
GROUP BY dzial;

-- Użycie z funkcjami tablicowymi
SELECT 
    dzial,
    ARRAY_AGG(pensja) as wszystkie_pensje,
    ARRAY_LENGTH(ARRAY_AGG(pensja), 1) as liczba_pensji,
    (ARRAY_AGG(pensja ORDER BY pensja DESC))[1] as najwyzsza_pensja
FROM pracownicy
GROUP BY dzial;
```

## Zaawansowane grupowanie

### 1. **ROLLUP**

```sql
-- ROLLUP - hierarchiczne podsumowania
SELECT 
    region,
    miesiac,
    produkt,
    SUM(sprzedaz) as suma
FROM dane_sprzedazy
GROUP BY ROLLUP (region, miesiac, produkt)
ORDER BY region, miesiac, produkt;

-- Generuje grupy:
-- (region, miesiac, produkt)  - szczegółowo
-- (region, miesiac, NULL)     - suma per region+miesiac
-- (region, NULL, NULL)        - suma per region  
-- (NULL, NULL, NULL)          - suma całkowita
```

### 2. **CUBE**

```sql
-- CUBE - wszystkie możliwe kombinacje
SELECT 
    region,
    kategoria,
    SUM(sprzedaz) as suma
FROM dane_sprzedazy
GROUP BY CUBE (region, kategoria);

-- Generuje grupy:
-- (region, kategoria)    - szczegółowo
-- (region, NULL)         - suma per region
-- (NULL, kategoria)      - suma per kategoria
-- (NULL, NULL)           - suma całkowita
```

### 3. **GROUPING SETS**

```sql
-- GROUPING SETS - custom kombinacje grup
SELECT 
    rok,
    miesiac,
    dzien,
    SUM(sprzedaz) as suma
FROM dane_sprzedazy
GROUP BY GROUPING SETS (
    (rok, miesiac, dzien),  -- dzienny
    (rok, miesiac),         -- miesięczny
    (rok),                  -- roczny
    ()                      -- total
);

-- Równoważne z UNION ALL:
SELECT rok, miesiac, dzien, SUM(sprzedaz) FROM dane_sprzedazy GROUP BY rok, miesiac, dzien
UNION ALL
SELECT rok, miesiac, NULL, SUM(sprzedaz) FROM dane_sprzedazy GROUP BY rok, miesiac  
UNION ALL
SELECT rok, NULL, NULL, SUM(sprzedaz) FROM dane_sprzedazy GROUP BY rok
UNION ALL
SELECT NULL, NULL, NULL, SUM(sprzedaz) FROM dane_sprzedazy;
```

### 4. **GROUPING function**

```sql
-- GROUPING() - identyfikuje które kolumny są NULL przez grupowanie
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
    
    CASE 
        WHEN GROUPING(region) = 0 AND GROUPING(kategoria) = 0 THEN 'Szczegóły'
        WHEN GROUPING(region) = 1 AND GROUPING(kategoria) = 0 THEN 'Per kategoria'
        WHEN GROUPING(region) = 0 AND GROUPING(kategoria) = 1 THEN 'Per region'
        ELSE 'Suma całkowita'
    END as typ_raportu
    
FROM dane_sprzedazy
GROUP BY CUBE (region, kategoria)
ORDER BY GROUPING(region), region, GROUPING(kategoria), kategoria;
```

## Funkcje agregujące jako funkcje okienkowe

### 1. **Running aggregates**

```sql
-- Suma narastająca
SELECT 
    data_zamowienia,
    wartosc,
    SUM(wartosc) OVER (ORDER BY data_zamowienia) as suma_narastajaca,
    AVG(wartosc) OVER (ORDER BY data_zamowienia) as srednia_narastajaca,
    COUNT(*) OVER (ORDER BY data_zamowienia) as liczba_narastajaca
FROM zamowienia
ORDER BY data_zamowienia;
```

### 2. **Moving aggregates**

```sql
-- Średnia ruchoma z ostatnich 7 dni
SELECT 
    data_zamowienia,
    wartosc,
    AVG(wartosc) OVER (
        ORDER BY data_zamowienia 
        RANGE BETWEEN '6 days' PRECEDING AND CURRENT ROW
    ) as srednia_7_dni,
    
    -- Suma z ostatnich 3 zamówień
    SUM(wartosc) OVER (
        ORDER BY data_zamowienia 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as suma_3_ostatnie
FROM zamowienia;
```

### 3. **Partitioned aggregates**

```sql
-- Agregaty w obrębie partycji
SELECT 
    imie,
    nazwisko,
    dzial,
    pensja,
    
    -- Funkcje agregujące per dział
    AVG(pensja) OVER (PARTITION BY dzial) as srednia_pensja_dzialu,
    SUM(pensja) OVER (PARTITION BY dzial) as suma_pensji_dzialu,
    COUNT(*) OVER (PARTITION BY dzial) as liczba_w_dziale,
    
    -- Procent pensji w dziale
    pensja / SUM(pensja) OVER (PARTITION BY dzial) * 100 as procent_pensji_dzialu,
    
    -- Ranking w dziale
    RANK() OVER (PARTITION BY dzial ORDER BY pensja DESC) as ranking_w_dziale
FROM pracownicy;
```

## Optymalizacja agregacji

### 1. **Indeksy dla GROUP BY**

```sql
-- Indeks wspierający grupowanie
CREATE INDEX idx_sprzedaz_data_kategoria ON sprzedaz(data_sprzedazy, kategoria);

-- Query korzystający z indeksu
SELECT 
    EXTRACT(MONTH FROM data_sprzedazy) as miesiac,
    kategoria,
    SUM(wartosc) as suma
FROM sprzedaz
WHERE data_sprzedazy >= '2024-01-01'
GROUP BY EXTRACT(MONTH FROM data_sprzedazy), kategoria;

-- Indeks pokrywający (covering index)
CREATE INDEX idx_zamowienia_covering ON zamowienia(id_klienta) INCLUDE (wartosc, data_zamowienia);
```

### 2. **Materialized views dla agregacji**

```sql
-- PostgreSQL materialized view
CREATE MATERIALIZED VIEW mv_monthly_sales AS
SELECT 
    EXTRACT(YEAR FROM data_zamowienia) as rok,
    EXTRACT(MONTH FROM data_zamowienia) as miesiac,
    COUNT(*) as liczba_zamowien,
    SUM(wartosc) as suma_sprzedazy,
    AVG(wartosc) as srednia_wartosc
FROM zamowienia
GROUP BY 
    EXTRACT(YEAR FROM data_zamowienia),
    EXTRACT(MONTH FROM data_zamowienia);

-- Tworzenie indeksu na materialized view
CREATE INDEX idx_mv_monthly_sales ON mv_monthly_sales(rok, miesiac);

-- Odświeżanie (can be automated)
REFRESH MATERIALIZED VIEW mv_monthly_sales;
```

### 3. **Partial aggregation**

```sql
-- Dla bardzo dużych tabel - agregacja etapowa
WITH partial_aggregates AS (
    SELECT 
        date_trunc('day', data_zamowienia) as dzien,
        SUM(wartosc) as daily_sum,
        COUNT(*) as daily_count
    FROM zamowienia
    WHERE data_zamowienia >= '2024-01-01'
    GROUP BY date_trunc('day', data_zamowienia)
)
SELECT 
    date_trunc('month', dzien) as miesiac,
    SUM(daily_sum) as suma_miesiezna,
    SUM(daily_count) as liczba_zamowien_miesieczna
FROM partial_aggregates
GROUP BY date_trunc('month', dzien);
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**

#### 1. **Czytelność i semantyka**
```sql
-- Używaj opisowych aliasów
SELECT 
    dzial,
    COUNT(*) as liczba_pracownikow,
    AVG(pensja) as srednia_pensja,
    MIN(data_zatrudnienia) as najwczesniejsze_zatrudnienie
FROM pracownicy
GROUP BY dzial;

-- Formatuj złożone GROUP BY
SELECT 
    EXTRACT(YEAR FROM data_zamowienia) as rok,
    EXTRACT(QUARTER FROM data_zamowienia) as kwartal,
    region,
    SUM(wartosc) as suma_sprzedazy
FROM zamowienia
GROUP BY 
    EXTRACT(YEAR FROM data_zamowienia),
    EXTRACT(QUARTER FROM data_zamowienia),
    region
ORDER BY rok, kwartal, region;
```

#### 2. **Obsługa NULL**
```sql
-- Świadome obsługiwanie NULL
SELECT 
    COALESCE(dzial, 'Nieokreślony') as dzial,
    COUNT(*) as liczba_pracownikow,
    COUNT(telefon) as z_numerem_telefonu,
    AVG(COALESCE(premia, 0)) as srednia_premia_z_zerami,
    AVG(premia) as srednia_premia_bez_null
FROM pracownicy
GROUP BY dzial;
```

#### 3. **Wydajność**
```sql
-- Pre-filtering przed agregacją
SELECT 
    dzial,
    AVG(pensja) as srednia_pensja
FROM pracownicy
WHERE data_zatrudnienia >= '2020-01-01'  -- Filter early
GROUP BY dzial
HAVING COUNT(*) >= 5;  -- Filter groups

-- Używaj indeksów wspierających agregację
-- CREATE INDEX idx_pracownicy_dzial_pensja ON pracownicy(dzial, pensja);
```

### ❌ **Złe praktyki:**

#### 1. **Błędy logiczne**
```sql
-- ❌ BŁĄD: kolumna nie w GROUP BY
SELECT dzial, imie, AVG(pensja)  -- imie musi być w GROUP BY!
FROM pracownicy
GROUP BY dzial;

-- ❌ BŁĄD: agregacja w WHERE zamiast HAVING
SELECT dzial, COUNT(*)
FROM pracownicy
WHERE COUNT(*) > 5  -- Błąd! Użyj HAVING
GROUP BY dzial;

-- ❌ BŁĄD: nie uwzględnianie NULL
SELECT AVG(premia) FROM pracownicy;  -- Ignoruje NULL w mianowniku!
```

#### 2. **Problemy wydajnościowe**
```sql
-- ❌ ŹLE: agregacja na nieindeksowanych kolumnach
SELECT UPPER(nazwisko), COUNT(*)
FROM pracownicy
GROUP BY UPPER(nazwisko);  -- Niemożliwość użycia indeksu

-- ❌ ŹLE: powtarzające się agregacje
SELECT 
    dzial,
    (SELECT AVG(pensja) FROM pracownicy p2 WHERE p2.dzial = p1.dzial) as avg1,
    (SELECT AVG(pensja) FROM pracownicy p2 WHERE p2.dzial = p1.dzial) as avg2
FROM pracownicy p1;
```

## Przykłady zaawansowane

### 1. **Analiza kohort**

```sql
-- Analiza retencji klientów per miesiąc rejestracji
WITH customer_cohorts AS (
    SELECT 
        k.id_klienta,
        DATE_TRUNC('month', k.data_rejestracji) as miesiąc_rejestracji,
        DATE_TRUNC('month', z.data_zamowienia) as miesiąc_zamowienia,
        EXTRACT(MONTH FROM AGE(z.data_zamowienia, k.data_rejestracji)) as miesiac_od_rejestracji
    FROM klienci k
    LEFT JOIN zamowienia z ON k.id_klienta = z.id_klienta
)
SELECT 
    miesiąc_rejestracji,
    miesiac_od_rejestracji,
    COUNT(DISTINCT id_klienta) as aktywni_klienci
FROM customer_cohorts
WHERE miesiac_od_rejestracji IS NOT NULL
GROUP BY miesiąc_rejestracji, miesiac_od_rejestracji
ORDER BY miesiąc_rejestracji, miesiac_od_rejestracji;
```

### 2. **Analiza ABC (Pareto)**

```sql
-- Klasyfikacja produktów według zasady Pareto (80/20)
WITH product_sales AS (
    SELECT 
        p.id_produktu,
        p.nazwa,
        SUM(pz.ilosc * p.cena) as suma_sprzedazy
    FROM produkty p
    JOIN pozycje_zamowien pz ON p.id_produktu = pz.id_produktu
    GROUP BY p.id_produktu, p.nazwa
),
ranked_products AS (
    SELECT 
        *,
        SUM(suma_sprzedazy) OVER () as total_sales,
        SUM(suma_sprzedazy) OVER (ORDER BY suma_sprzedazy DESC) as cumulative_sales,
        ROW_NUMBER() OVER (ORDER BY suma_sprzedazy DESC) as ranking
    FROM product_sales
)
SELECT 
    nazwa,
    suma_sprzedazy,
    cumulative_sales / total_sales * 100 as cumulative_percent,
    CASE 
        WHEN cumulative_sales / total_sales <= 0.8 THEN 'A'
        WHEN cumulative_sales / total_sales <= 0.95 THEN 'B'
        ELSE 'C'
    END as kategoria_abc
FROM ranked_products
ORDER BY ranking;
```

## Pułapki egzaminacyjne

### 1. **GROUP BY vs aggregate functions**
```
Bez GROUP BY: agregacja całej tabeli → 1 wiersz
Z GROUP BY: agregacja per grupa → n wierszy (gdzie n = liczba grup)
```

### 2. **NULL w agregacjach**
```
COUNT(*): liczy wszystkie wiersze (z NULL)
COUNT(kolumna): liczy tylko nie-NULL
SUM/AVG/MIN/MAX: ignorują NULL
```

### 3. **HAVING vs WHERE**
```
WHERE: filtruje wiersze przed grupowaniem
HAVING: filtruje grupy po grupowaniu
HAVING może używać funkcji agregujących, WHERE nie
```

### 4. **Kolumny w SELECT z GROUP BY**
```
Wszystkie kolumny w SELECT (oprócz agregujących) 
muszą być w GROUP BY

Wyjątek: funkcjonalnie zależne kolumny (klucz główny)
```