# 🎯 SQL DML ZAAWANSOWANY - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekunds)

"SQL DML zaawansowany obejmuje skomplikowane operacje manipulacji danymi:

1. **CTE (Common Table Expressions)** - zapytania rekurencyjne i organizacja kodu
2. **Window Functions** - analityka bez GROUP BY
3. **MERGE/UPSERT** - operacje warunkowe INSERT/UPDATE
4. **Subqueries** - skorelowane i nieskorelowane podzapytania
5. **LATERAL joins** - dependent joins w PostgreSQL
6. **Bulk operations** - masowe operacje z optymalizacją

Te techniki umożliwiają rozwiązywanie złożonych problemów analitycznych i ETL z zachowaniem wydajności."

## ✍️ CO NAPISAĆ NA KARTCE

```sql
SQL DML ZAAWANSOWANY - KLUCZOWE TECHNIKI:

CTE (Common Table Expressions):
WITH nazwa AS (SELECT ...) 
SELECT * FROM nazwa;

RECURSIVE CTE:
WITH RECURSIVE nazwa AS (
  SELECT ... -- base case
  UNION ALL
  SELECT ... FROM nazwa WHERE ... -- recursive
)

WINDOW FUNCTIONS:
ROW_NUMBER() OVER (PARTITION BY col ORDER BY col)
RANK(), DENSE_RANK(), LAG(), LEAD()
SUM() OVER (PARTITION BY ... ORDER BY ...)

LATERAL JOINS (PostgreSQL):
SELECT * FROM table1 t1,
LATERAL (SELECT * FROM table2 WHERE col = t1.col) t2;

SUBQUERIES:
• EXISTS/NOT EXISTS - sprawdzenie istnienia
• IN/NOT IN - przynależność do zbioru  
• ANY/ALL - porównania z podzbiorem
• Skorelowane vs nieskorelowane

MERGE/UPSERT:
INSERT ... ON CONFLICT (col) DO UPDATE SET ...;
MERGE INTO target USING source ON condition
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...;

BULK OPERATIONS:
INSERT INTO ... SELECT FROM ...;
UPDATE ... FROM another_table WHERE ...;
DELETE FROM ... USING another_table WHERE ...;

CONDITIONAL LOGIC:
CASE WHEN ... THEN ... ELSE ... END
COALESCE(val1, val2, val3)
NULLIF(val1, val2)

ANALYTIC FUNCTIONS:
FIRST_VALUE(), LAST_VALUE()
NTH_VALUE(expr, n)
PERCENT_RANK(), CUME_DIST()
NTILE(n) -- podział na kwantyle
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- KOMPLEKSOWE PRZYKŁADY SQL DML ZAAWANSOWANY

-- Przygotowanie danych testowych
CREATE TABLE sprzedaz (
    id SERIAL PRIMARY KEY,
    sprzedawca_id INT,
    data_sprzedazy DATE,
    kwota DECIMAL(10,2),
    region VARCHAR(50),
    produkt VARCHAR(50)
);

INSERT INTO sprzedaz VALUES
(1, 101, '2024-01-15', 1500.00, 'Północ', 'Laptop'),
(2, 102, '2024-01-16', 800.00, 'Południe', 'Tablet'),
(3, 101, '2024-01-17', 2200.00, 'Północ', 'Desktop'),
(4, 103, '2024-01-18', 1200.00, 'Wschód', 'Laptop'),
(5, 102, '2024-01-19', 950.00, 'Południe', 'Laptop'),
(6, 101, '2024-01-20', 1800.00, 'Północ', 'Monitor'),
(7, 104, '2024-01-21', 650.00, 'Zachód', 'Tablet'),
(8, 103, '2024-01-22', 1400.00, 'Wschód', 'Desktop'),
(9, 102, '2024-01-23', 750.00, 'Południe', 'Monitor'),
(10, 105, '2024-01-24', 1100.00, 'Północ', 'Laptop');

-- 1. CTE (Common Table Expressions) - PODSTAWOWE

-- Prosta CTE dla czytelności
WITH wysokie_sprzedaze AS (
    SELECT sprzedawca_id, kwota, data_sprzedazy
    FROM sprzedaz 
    WHERE kwota > 1000
)
SELECT sprzedawca_id, COUNT(*) as liczba_wysokich_sprzedazy, AVG(kwota) as srednia
FROM wysokie_sprzedaze
GROUP BY sprzedawca_id;

-- Multiple CTE
WITH 
    statystyki_regionalne AS (
        SELECT region, COUNT(*) as liczba_sprzedazy, SUM(kwota) as suma_kwot
        FROM sprzedaz
        GROUP BY region
    ),
    najlepszy_region AS (
        SELECT region, suma_kwot,
               RANK() OVER (ORDER BY suma_kwot DESC) as ranking
        FROM statystyki_regionalne
    )
SELECT region, suma_kwot, ranking
FROM najlepszy_region
WHERE ranking <= 2;

-- 2. RECURSIVE CTE - HIERARCHIE I SEKWENCJE

-- Tabela organizacyjna (hierarchia)
CREATE TABLE pracownicy_org (
    id INT PRIMARY KEY,
    imie VARCHAR(50),
    przelozony_id INT REFERENCES pracownicy_org(id)
);

INSERT INTO pracownicy_org VALUES
(1, 'CEO', NULL),
(2, 'Dyrektor Sprzedaży', 1),
(3, 'Dyrektor IT', 1),
(4, 'Manager Zespołu A', 2),
(5, 'Manager Zespołu B', 2),
(6, 'Programista Senior', 3),
(7, 'Sprzedawca A1', 4),
(8, 'Sprzedawca A2', 4),
(9, 'Sprzedawca B1', 5),
(10, 'Programista Junior', 6);

-- Recursive CTE - cała hierarchia od CEO
WITH RECURSIVE hierarchia AS (
    -- Base case: CEO (bez przełożonego)
    SELECT id, imie, przelozony_id, 0 as poziom, 
           CAST(imie AS TEXT) as sciezka
    FROM pracownicy_org 
    WHERE przelozony_id IS NULL
    
    UNION ALL
    
    -- Recursive case: podwładni
    SELECT p.id, p.imie, p.przelozony_id, h.poziom + 1,
           h.sciezka || ' -> ' || p.imie
    FROM pracownicy_org p
    JOIN hierarchia h ON p.przelozony_id = h.id
)
SELECT poziom, REPEAT('  ', poziom) || imie as struktura_org, sciezka
FROM hierarchia
ORDER BY poziom, imie;

-- Recursive CTE - generowanie sekwencji dat
WITH RECURSIVE serie_dat AS (
    SELECT DATE '2024-01-01' as data
    UNION ALL
    SELECT data + INTERVAL '1 day'
    FROM serie_dat
    WHERE data < DATE '2024-01-31'
)
SELECT 
    data,
    EXTRACT(DOW FROM data) as dzien_tygodnia,
    CASE WHEN EXTRACT(DOW FROM data) IN (0,6) THEN 'Weekend' ELSE 'Dzień roboczy' END as typ_dnia
FROM serie_dat;

-- 3. WINDOW FUNCTIONS - ANALITYKA

-- Ranking sprzedawców w każdym regionie
SELECT 
    sprzedawca_id,
    region,
    kwota,
    data_sprzedazy,
    -- Different ranking functions
    ROW_NUMBER() OVER (PARTITION BY region ORDER BY kwota DESC) as row_num,
    RANK() OVER (PARTITION BY region ORDER BY kwota DESC) as rank_pos,
    DENSE_RANK() OVER (PARTITION BY region ORDER BY kwota DESC) as dense_rank_pos,
    PERCENT_RANK() OVER (PARTITION BY region ORDER BY kwota) as percentile
FROM sprzedaz;

-- Running totals i moving averages
SELECT 
    data_sprzedazy,
    sprzedawca_id,
    kwota,
    -- Running total
    SUM(kwota) OVER (
        PARTITION BY sprzedawca_id 
        ORDER BY data_sprzedazy 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as running_total,
    -- Moving average (3-day window)
    AVG(kwota) OVER (
        PARTITION BY sprzedawca_id 
        ORDER BY data_sprzedazy 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as moving_avg_3day,
    -- Previous and next values
    LAG(kwota, 1) OVER (PARTITION BY sprzedawca_id ORDER BY data_sprzedazy) as prev_kwota,
    LEAD(kwota, 1) OVER (PARTITION BY sprzedawca_id ORDER BY data_sprzedazy) as next_kwota
FROM sprzedaz
ORDER BY sprzedawca_id, data_sprzedazy;

-- Quartiles i percentile analysis
SELECT 
    sprzedawca_id,
    kwota,
    NTILE(4) OVER (ORDER BY kwota) as quartile,
    FIRST_VALUE(kwota) OVER (ORDER BY kwota ROWS UNBOUNDED PRECEDING) as min_kwota,
    LAST_VALUE(kwota) OVER (ORDER BY kwota ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) as max_kwota,
    NTH_VALUE(kwota, 2) OVER (ORDER BY kwota ROWS UNBOUNDED PRECEDING) as second_lowest
FROM sprzedaz;

-- 4. SUBQUERIES - ZAAWANSOWANE ZASTOSOWANIA

-- EXISTS - sprzedawcy którzy sprzedali w więcej niż jednym regionie
SELECT DISTINCT s1.sprzedawca_id
FROM sprzedaz s1
WHERE EXISTS (
    SELECT 1 FROM sprzedaz s2 
    WHERE s2.sprzedawca_id = s1.sprzedawca_id 
    AND s2.region != s1.region
);

-- Skorelowane subquery - sprzedawcy z ponadprzeciętną sprzedażą w regionie
SELECT sprzedawca_id, region, kwota
FROM sprzedaz s1
WHERE kwota > (
    SELECT AVG(kwota) 
    FROM sprzedaz s2 
    WHERE s2.region = s1.region
);

-- ANY/ALL - sprzedawcy lepsi niż wszyscy z regionu 'Zachód'
SELECT sprzedawca_id, region, kwota
FROM sprzedaz
WHERE kwota > ALL (
    SELECT kwota FROM sprzedaz WHERE region = 'Zachód'
);

-- Complex subquery with multiple levels
SELECT 
    region,
    sprzedawca_id,
    kwota,
    (SELECT COUNT(*) FROM sprzedaz s2 WHERE s2.region = s1.region) as sprzedaze_w_regionie,
    (SELECT AVG(kwota) FROM sprzedaz s2 WHERE s2.sprzedawca_id = s1.sprzedawca_id) as avg_sprzedawcy
FROM sprzedaz s1
WHERE sprzedawca_id IN (
    SELECT sprzedawca_id 
    FROM sprzedaz 
    GROUP BY sprzedawca_id 
    HAVING COUNT(*) >= 2
);

-- 5. LATERAL JOINS (PostgreSQL specific)

-- Tabela produktów dla każdego sprzedawcy
SELECT 
    sprzedawca_id,
    top_products.produkt,
    top_products.max_kwota
FROM (SELECT DISTINCT sprzedawca_id FROM sprzedaz) s,
LATERAL (
    SELECT produkt, MAX(kwota) as max_kwota
    FROM sprzedaz s2
    WHERE s2.sprzedawca_id = s.sprzedawca_id
    GROUP BY produkt
    ORDER BY max_kwota DESC
    LIMIT 2
) top_products;

-- Complex LATERAL with multiple functions
SELECT 
    s.sprzedawca_id,
    stats.total_sprzedaz,
    stats.avg_kwota,
    recent.ostatnia_sprzedaz,
    recent.ostatni_produkt
FROM (SELECT DISTINCT sprzedawca_id FROM sprzedaz) s,
LATERAL (
    SELECT 
        SUM(kwota) as total_sprzedaz,
        AVG(kwota) as avg_kwota,
        COUNT(*) as liczba_transakcji
    FROM sprzedaz s2 
    WHERE s2.sprzedawca_id = s.sprzedawca_id
) stats,
LATERAL (
    SELECT data_sprzedazy as ostatnia_sprzedaz, produkt as ostatni_produkt
    FROM sprzedaz s3
    WHERE s3.sprzedawca_id = s.sprzedawca_id
    ORDER BY data_sprzedazy DESC
    LIMIT 1
) recent;

-- 6. MERGE i UPSERT OPERATIONS

-- Tabela docelowa dla merge
CREATE TABLE quota_sprzedawcow (
    sprzedawca_id INT PRIMARY KEY,
    quota_miesieczna DECIMAL(10,2),
    osiagnieta_kwota DECIMAL(10,2) DEFAULT 0,
    ostatnia_aktualizacja TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO quota_sprzedawcow (sprzedawca_id, quota_miesieczna) VALUES
(101, 5000), (102, 4000), (103, 4500), (104, 3500);

-- UPSERT using ON CONFLICT (PostgreSQL)
INSERT INTO quota_sprzedawcow (sprzedawca_id, quota_miesieczna, osiagnieta_kwota)
SELECT 
    sprzedawca_id,
    5000 as quota_miesieczna,
    SUM(kwota) as osiagnieta_kwota
FROM sprzedaz
GROUP BY sprzedawca_id
ON CONFLICT (sprzedawca_id) 
DO UPDATE SET 
    osiagnieta_kwota = EXCLUDED.osiagnieta_kwota,
    ostatnia_aktualizacja = CURRENT_TIMESTAMP;

-- Conditional UPSERT with complex logic
INSERT INTO quota_sprzedawcow AS target (sprzedawca_id, quota_miesieczna, osiagnieta_kwota)
SELECT 
    sprzedawca_id,
    CASE 
        WHEN SUM(kwota) > 3000 THEN 6000
        WHEN SUM(kwota) > 2000 THEN 5000
        ELSE 4000
    END as quota_miesieczna,
    SUM(kwota) as osiagnieta_kwota
FROM sprzedaz
GROUP BY sprzedawca_id
ON CONFLICT (sprzedawca_id)
DO UPDATE SET
    quota_miesieczna = CASE 
        WHEN EXCLUDED.osiagnieta_kwota > target.osiagnieta_kwota 
        THEN EXCLUDED.quota_miesieczna
        ELSE target.quota_miesieczna
    END,
    osiagnieta_kwota = GREATEST(target.osiagnieta_kwota, EXCLUDED.osiagnieta_kwota),
    ostatnia_aktualizacja = CURRENT_TIMESTAMP;

-- 7. BULK OPERATIONS z optymalizacją

-- Bulk update z JOIN
UPDATE quota_sprzedawcow 
SET osiagnieta_kwota = subq.total_kwota,
    ostatnia_aktualizacja = CURRENT_TIMESTAMP
FROM (
    SELECT sprzedawca_id, SUM(kwota) as total_kwota
    FROM sprzedaz
    WHERE data_sprzedazy >= DATE '2024-01-01'
    GROUP BY sprzedawca_id
) subq
WHERE quota_sprzedawcow.sprzedawca_id = subq.sprzedawca_id;

-- Bulk INSERT with SELECT
CREATE TABLE sprzedaz_summary (
    region VARCHAR(50),
    miesiac DATE,
    total_sprzedaz DECIMAL(12,2),
    liczba_transakcji INT,
    avg_wartosc_transakcji DECIMAL(10,2)
);

INSERT INTO sprzedaz_summary
SELECT 
    region,
    DATE_TRUNC('month', data_sprzedazy) as miesiac,
    SUM(kwota) as total_sprzedaz,
    COUNT(*) as liczba_transakcji,
    AVG(kwota) as avg_wartosc_transakcji
FROM sprzedaz
GROUP BY region, DATE_TRUNC('month', data_sprzedazy);

-- Conditional bulk delete
DELETE FROM sprzedaz 
WHERE id IN (
    SELECT s1.id
    FROM sprzedaz s1
    WHERE EXISTS (
        SELECT 1 FROM sprzedaz s2
        WHERE s2.sprzedawca_id = s1.sprzedawca_id
        AND s2.data_sprzedazy = s1.data_sprzedazy
        AND s2.id > s1.id  -- Keep only the latest duplicate
    )
);

-- 8. ZAAWANSOWANE CASE EXPRESSIONS

-- Complex conditional logic
SELECT 
    sprzedawca_id,
    kwota,
    region,
    CASE 
        WHEN kwota > 2000 THEN 'Wysoka'
        WHEN kwota > 1000 THEN 'Średnia'
        ELSE 'Niska'
    END as kategoria_sprzedazy,
    
    CASE region
        WHEN 'Północ' THEN kwota * 1.1  -- 10% bonus
        WHEN 'Południe' THEN kwota * 1.05  -- 5% bonus
        ELSE kwota
    END as kwota_z_bonusem,
    
    -- Nested CASE
    CASE 
        WHEN region IN ('Północ', 'Południe') THEN
            CASE 
                WHEN kwota > 1500 THEN 'Premium Nord/Sud'
                ELSE 'Standard Nord/Sud'
            END
        ELSE 
            CASE
                WHEN kwota > 1200 THEN 'Premium Other'
                ELSE 'Standard Other'
            END
    END as segment_klienta
FROM sprzedaz;

-- 9. PIVOT i UNPIVOT operations (manual implementation)

-- Pivot - regiony jako kolumny
SELECT 
    sprzedawca_id,
    SUM(CASE WHEN region = 'Północ' THEN kwota ELSE 0 END) as polnoc,
    SUM(CASE WHEN region = 'Południe' THEN kwota ELSE 0 END) as poludnie,
    SUM(CASE WHEN region = 'Wschód' THEN kwota ELSE 0 END) as wschod,
    SUM(CASE WHEN region = 'Zachód' THEN kwota ELSE 0 END) as zachod,
    SUM(kwota) as total
FROM sprzedaz
GROUP BY sprzedawca_id;

-- Unpivot simulation using UNION ALL
WITH pivot_data AS (
    SELECT 
        sprzedawca_id,
        SUM(CASE WHEN region = 'Północ' THEN kwota ELSE 0 END) as polnoc,
        SUM(CASE WHEN region = 'Południe' THEN kwota ELSE 0 END) as poludnie,
        SUM(CASE WHEN region = 'Wschód' THEN kwota ELSE 0 END) as wschod,
        SUM(CASE WHEN region = 'Zachód' THEN kwota ELSE 0 END) as zachod
    FROM sprzedaz
    GROUP BY sprzedawca_id
)
SELECT sprzedawca_id, 'Północ' as region, polnoc as kwota FROM pivot_data WHERE polnoc > 0
UNION ALL
SELECT sprzedawca_id, 'Południe' as region, poludnie as kwota FROM pivot_data WHERE poludnie > 0
UNION ALL
SELECT sprzedawca_id, 'Wschód' as region, wschod as kwota FROM pivot_data WHERE wschod > 0
UNION ALL
SELECT sprzedawca_id, 'Zachód' as region, zachod as kwota FROM pivot_data WHERE zachod > 0;

-- 10. PERFORMANCE OPTIMIZED QUERIES

-- Using DISTINCT ON instead of GROUP BY for better performance
SELECT DISTINCT ON (sprzedawca_id) 
    sprzedawca_id, 
    data_sprzedazy, 
    kwota, 
    produkt
FROM sprzedaz
ORDER BY sprzedawca_id, kwota DESC;  -- Największa sprzedaż każdego sprzedawcy

-- Optimized pagination with OFFSET/LIMIT alternative
WITH numbered_results AS (
    SELECT *, ROW_NUMBER() OVER (ORDER BY data_sprzedazy DESC) as rn
    FROM sprzedaz
    WHERE kwota > 1000
)
SELECT * FROM numbered_results 
WHERE rn BETWEEN 11 AND 20;  -- Page 2 (items 11-20)

-- Batch processing with LIMIT
DO $$
DECLARE
    batch_size INT := 100;
    processed INT := 0;
BEGIN
    LOOP
        UPDATE sprzedaz 
        SET kwota = kwota * 1.1
        WHERE id IN (
            SELECT id FROM sprzedaz 
            WHERE kwota < 1000 
            AND NOT EXISTS (
                SELECT 1 FROM sprzedaz_summary ss 
                WHERE ss.region = sprzedaz.region
            )
            LIMIT batch_size
        );
        
        GET DIAGNOSTICS processed = ROW_COUNT;
        EXIT WHEN processed = 0;
        
        RAISE NOTICE 'Processed % rows', processed;
        COMMIT;
    END LOOP;
END $$;
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Window functions nie redukują liczby wierszy (w przeciwieństwie do GROUP BY)
2. **UWAGA**: Recursive CTE może prowadzić do nieskończoności - zawsze dodaj warunek stopu
3. **BŁĄD**: LATERAL joins działają tylko w PostgreSQL, nie w standardowym SQL
4. **WAŻNE**: EXISTS może być szybszy niż IN dla dużych zbiorów
5. **PUŁAPKA**: CTE są obliczane dla każdego użycia - rozważ materialized CTE

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Common Table Expressions (CTE)** - wspólne wyrażenia tabelowe
- **Window functions** - funkcje okienkowe
- **Recursive queries** - zapytania rekurencyjne
- **Correlated subqueries** - skorelowane podzapytania
- **LATERAL joins** - dependent joins
- **UPSERT operations** - operacje INSERT/UPDATE
- **Bulk operations** - operacje masowe
- **Analytical functions** - funkcje analityczne

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **21-sql-joiny** - LATERAL jako rozszerzenie JOIN
- **32-funkcje-agregujace** - window functions vs GROUP BY
- **31-subqueries** - zaawansowane podzapytania
- **42-optymalizacja-wydajnosci** - optymalizacja złożonych zapytań
- **29-sql-ddl-zaawansowany** - struktury wspierające zaawansowane DML