# Widoki vs Tabele tymczasowe

## Widoki (Views)

### Definicja
**Widok (perspektywa)** to **logiczny widok na dane** - wirtualna tabela zdefiniowana przez zapytanie SQL, która nie przechowuje fizycznie danych.

### Składnia:
```sql
CREATE VIEW nazwa_widoku AS
SELECT kolumny
FROM tabele  
WHERE warunki;
```

### Charakterystyka widoków:
- **Wirtualne** - nie zajmują miejsca na dysku
- **Dynamiczne** - zawsze aktualne dane z tabel bazowych
- **Logiczne** - istnieją tylko jako definicja zapytania
- **Bezpieczne** - kontrola dostępu do danych

### Przykład widoku:
```sql
CREATE VIEW pracownicy_it AS
SELECT id, imie, nazwisko, pensja, data_zatrudnienia
FROM pracownicy 
WHERE dzial = 'IT' AND aktywny = true;

-- Użycie
SELECT * FROM pracownicy_it WHERE pensja > 5000;
```

## Tabele tymczasowe

### Definicja
**Tabela tymczasowa** to **fizyczna tabela** przechowująca dane tymczasowo, która jest **automatycznie usuwana** po zakończeniu sesji lub transakcji.

### Rodzaje:

#### **Session-level (lokalne)**
```sql
-- PostgreSQL
CREATE TEMPORARY TABLE temp_obliczenia (
    id INT,
    wynik DECIMAL(10,2)
);

-- SQL Server  
CREATE TABLE #temp_obliczenia (
    id INT,
    wynik DECIMAL(10,2)
);
```

#### **Transaction-level**
```sql
-- MySQL
CREATE TEMPORARY TABLE temp_raport (
    kategoria VARCHAR(50),
    suma DECIMAL(15,2)
);
```

### Charakterystyka tabel tymczasowych:
- **Fizyczne** - zajmują miejsce na dysku/w pamięci
- **Izolowane** - widoczne tylko dla sesji/transakcji
- **Modyfikowalne** - INSERT, UPDATE, DELETE
- **Tymczasowe** - automatyczne usuwanie

## Porównanie szczegółowe

| Aspekt | Widoki (Views) | Tabele tymczasowe |
|--------|----------------|-------------------|
| **Przechowywanie** | Logiczne (tylko definicja) | Fizyczne (dane na dysku) |
| **Miejsce na dysku** | Brak | Zajmuje miejsce |
| **Aktualność danych** | Zawsze aktualne | Snapshot w momencie utworzenia |
| **Wydajność odczytu** | Zależy od zapytania bazowego | Szybka (dane gotowe) |
| **Modyfikowalność** | Ograniczona | Pełna (INSERT/UPDATE/DELETE) |
| **Trwałość** | Permanentna definicja | Tymczasowa |
| **Widoczność** | Dla wszystkich użytkowników | Tylko dla sesji |
| **Pamięć** | Minimalna | Może być znaczna |
| **Indeksy** | Dziedziczone z tabel bazowych | Można tworzyć własne |

## Zastosowania widoków

### 1. **Bezpieczeństwo i kontrola dostępu**
```sql
-- Ukryj wrażliwe kolumny
CREATE VIEW klienci_publiczne AS
SELECT id, nazwa, miasto, telefon
FROM klienci;  -- Bez numeru PESEL, adresu

GRANT SELECT ON klienci_publiczne TO user_helpdesk;
```

### 2. **Uproszczenie złożonych zapytań**
```sql
-- Zamiast złożonego JOIN za każdym razem
CREATE VIEW zamowienia_szczegoly AS
SELECT 
    z.id as zamowienie_id,
    k.nazwa as klient,
    p.nazwa as produkt,
    zi.ilosc,
    zi.cena,
    zi.ilosc * zi.cena as wartosc
FROM zamowienia z
JOIN klienci k ON z.id_klienta = k.id
JOIN zamowienia_items zi ON z.id = zi.id_zamowienia
JOIN produkty p ON zi.id_produktu = p.id;
```

### 3. **Agregacje i raportowanie**
```sql
CREATE VIEW sprzedaz_miesięczna AS
SELECT 
    EXTRACT(YEAR FROM data_zamowienia) as rok,
    EXTRACT(MONTH FROM data_zamowienia) as miesiac,
    COUNT(*) as liczba_zamowien,
    SUM(wartosc) as suma_sprzedazy
FROM zamowienia
GROUP BY EXTRACT(YEAR FROM data_zamowienia), EXTRACT(MONTH FROM data_zamowienia);
```

### 4. **Kompatybilność wsteczna**
```sql
-- Stary widok po zmianie struktury tabeli
CREATE VIEW klienci_old AS
SELECT 
    id,
    CONCAT(imie, ' ', nazwisko) as nazwa,  -- Połączone z dwóch kolumn
    miasto
FROM klienci_new;
```

### 5. **Denormalizacja dla wydajności**
```sql
CREATE MATERIALIZED VIEW produkty_z_kategoriami AS
SELECT 
    p.*,
    k.nazwa as kategoria_nazwa,
    k.opis as kategoria_opis
FROM produkty p
JOIN kategorie k ON p.id_kategorii = k.id;

-- Odświeżanie materialized view
REFRESH MATERIALIZED VIEW produkty_z_kategoriami;
```

## Zastosowania tabel tymczasowych

### 1. **Przetwarzanie wsadowe**
```sql
-- ETL process
CREATE TEMPORARY TABLE staging_sprzedaz AS
SELECT * FROM raw_sales_data WHERE data >= '2024-01-01';

-- Transformacje
UPDATE staging_sprzedaz SET cena = cena * 1.23 WHERE kraj = 'PL';  -- VAT

-- Load do tabeli docelowej
INSERT INTO sprzedaz_historia SELECT * FROM staging_sprzedaz;
```

### 2. **Złożone obliczenia**
```sql
CREATE TEMPORARY TABLE temp_analiza (
    id_produktu INT,
    sprzedaz_q1 DECIMAL(15,2),
    sprzedaz_q2 DECIMAL(15,2),
    trend VARCHAR(20)
);

-- Multi-step analysis
INSERT INTO temp_analiza (id_produktu, sprzedaz_q1)
SELECT id_produktu, SUM(wartosc) 
FROM sprzedaz 
WHERE kwartal = 1 
GROUP BY id_produktu;

UPDATE temp_analiza SET sprzedaz_q2 = (
    SELECT SUM(wartosc) FROM sprzedaz s 
    WHERE s.id_produktu = temp_analiza.id_produktu AND kwartal = 2
);

UPDATE temp_analiza 
SET trend = CASE 
    WHEN sprzedaz_q2 > sprzedaz_q1 THEN 'ROSNĄCY'
    ELSE 'MALEJĄCY'
END;
```

### 3. **Optymalizacja zapytań**
```sql
-- Zamiast powtarzania podzapytania
CREATE TEMPORARY TABLE high_value_customers AS
SELECT id_klienta
FROM zamowienia
GROUP BY id_klienta
HAVING SUM(wartosc) > 10000;

-- Użyj w różnych zapytaniях
SELECT * FROM klienci WHERE id IN (SELECT id_klienta FROM high_value_customers);
SELECT * FROM rabaty WHERE id_klienta IN (SELECT id_klienta FROM high_value_customers);
```

### 4. **Backup i migracje**
```sql
-- Backup przed zmianami
CREATE TEMPORARY TABLE backup_produkty AS
SELECT * FROM produkty WHERE kategoria = 'ELEKTRONIKA';

-- Ryzykowne operacje
UPDATE produkty SET cena = cena * 0.5 WHERE kategoria = 'ELEKTRONIKA';

-- Rollback if needed
DELETE FROM produkty WHERE kategoria = 'ELEKTRONIKA';
INSERT INTO produkty SELECT * FROM backup_produkty;
```

## Widoki modyfikowalne (Updatable Views)

### Warunki modyfikowalności:
- **Jeden FROM** - tylko jedna tabela bazowa
- **Brak DISTINCT, GROUP BY, HAVING**
- **Brak funkcji agregujących**
- **Brak UNION, INTERSECT, EXCEPT**
- **Wszystkie klucze główne** w widoku

### Przykład modyfikowalnego widoku:
```sql
CREATE VIEW pracownicy_aktywni AS
SELECT id, imie, nazwisko, pensja, dzial
FROM pracownicy 
WHERE aktywny = true;

-- Możliwe operacje
INSERT INTO pracownicy_aktywni (imie, nazwisko, pensja, dzial) 
VALUES ('Jan', 'Kowalski', 5000, 'IT');

UPDATE pracownicy_aktywni SET pensja = 5500 WHERE id = 123;

DELETE FROM pracownicy_aktywni WHERE id = 456;
```

### INSTEAD OF Triggers dla widoków:
```sql
CREATE TRIGGER instead_of_insert_view
INSTEAD OF INSERT ON complex_view
FOR EACH ROW
EXECUTE FUNCTION handle_view_insert();
```

## Materialized Views

### Definicja:
**Materialized View** = widok + fizyczne przechowywanie danych

```sql
-- PostgreSQL
CREATE MATERIALIZED VIEW mv_sprzedaz_summary AS
SELECT 
    region,
    DATE_TRUNC('month', data_sprzedazy) as miesiac,
    SUM(wartosc) as suma,
    COUNT(*) as liczba_transakcji
FROM sprzedaz
GROUP BY region, DATE_TRUNC('month', data_sprzedazy);

-- Indeksy na materialized view
CREATE INDEX idx_mv_region_miesiac ON mv_sprzedaz_summary (region, miesiac);

-- Odświeżanie
REFRESH MATERIALIZED VIEW mv_sprzedaz_summary;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_sprzedaz_summary;  -- Bez blokowania
```

## Common Table Expressions (CTE) vs Temporary Tables

### CTE - tymczasowe w ramach zapytania:
```sql
WITH temp_calculations AS (
    SELECT 
        id_produktu,
        AVG(cena) as srednia_cena
    FROM sprzedaz
    GROUP BY id_produktu
)
SELECT p.nazwa, tc.srednia_cena
FROM produkty p
JOIN temp_calculations tc ON p.id = tc.id_produktu;
```

### Temporary Table - tymczasowe w ramach sesji:
```sql
CREATE TEMPORARY TABLE temp_calculations AS
SELECT id_produktu, AVG(cena) as srednia_cena
FROM sprzedaz
GROUP BY id_produktu;

-- Można używać wielokrotnie
SELECT * FROM temp_calculations WHERE srednia_cena > 100;
SELECT * FROM temp_calculations WHERE id_produktu IN (1,2,3);
```

## Wydajność

### Widoki:
- **Zawsze aktualne** - każde użycie = wykonanie zapytania bazowego
- **Brak dodatkowego I/O** dla samego widoku
- **Optymalizator może** zoptymalizować łączone zapytania

### Tabele tymczasowe:
- **Szybki dostęp** - dane już przetworzone
- **Dodatkowy I/O** do tworzenia i usuwania
- **Możliwość indeksowania** - dodatkowa optymalizacja

### Materialized Views:
- **Najszybszy odczyt** - pre-computed results
- **Opóźniona aktualność** - trzeba odświeżać
- **Najwięcej miejsca** na dysku

## Najlepsze praktyki

### Kiedy używać widoków:
- **Bezpieczeństwo** - ukrywanie kolumn/wierszy
- **Uproszczenie** - często używane JOIN'y
- **Małe zmiany danych** - zawsze aktualne
- **Tylko odczyt** - brak modyfikacji

### Kiedy używać tabel tymczasowych:
- **Złożone transformacje** - multi-step processing
- **Duże ilości danych** - optymalizacja wydajności
- **Modyfikacje** - potrzebujesz INSERT/UPDATE/DELETE
- **Intermediate results** - pośrednie wyniki

### Kiedy używać materialized views:
- **Duże agregacje** - kosztowne obliczenia
- **Rzadkie zmiany** - dane się często nie zmieniają
- **Często czytane** - powtarzalne zapytania
- **Akceptowalna opóźniona aktualność**

## Pułapki egzaminacyjne

### 1. **Trwałość**
- Widoki: definicja permanentna, dane wirtualne
- Temp tables: dane fizyczne, istnienie tymczasowe

### 2. **Modyfikowalność**
- Widoki: tylko pod pewnymi warunkami
- Temp tables: zawsze modyfikowalne

### 3. **Aktualność**
- Widoki: zawsze aktualne (live data)
- Temp tables: snapshot w momencie utworzenia

### 4. **Wydajność**
- Views: może być wolne (re-execution)
- Temp tables: szybkie odczyty, kosztowne tworzenie
- Materialized views: najszybsze, ale nieaktualne