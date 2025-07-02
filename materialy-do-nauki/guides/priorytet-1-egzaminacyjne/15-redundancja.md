# Redundancja danych

## Definicja

**Redundancja danych** to sytuacja, w której **te same informacje są przechowywane w więcej niż jednym miejscu** w bazie danych.

### Rodzaje redundancji:
- **Kontrolowana** - świadomie wprowadzona dla optymalizacji
- **Niekontrolowana** - przypadkowa, wynikająca ze złego projektu
- **Częściowa** - tylko część danych się powtarza
- **Pełna** - całkowite duplikowanie informacji

## Przykłady redundancji

### Przykład 1: Redundancja w denormalizowanej tabeli
```sql
-- Tabela z redundancją
CREATE TABLE zamowienia_szczegoly (
    id_zamowienia INT,
    klient_nazwa VARCHAR(100),    -- Redundancja!
    klient_adres VARCHAR(200),    -- Redundancja!
    klient_telefon VARCHAR(15),   -- Redundancja!
    produkt_nazwa VARCHAR(100),   -- Redundancja!
    produkt_cena DECIMAL(10,2),   -- Redundancja!
    ilosc INT,
    data_zamowienia DATE
);

-- Dane w tabeli:
| id_zam | klient_nazwa | klient_adres    | produkt_nazwa | produkt_cena | ilosc |
|--------|-------------|------------------|---------------|-------------|-------|
| 1      | Jan Kowalski| ul. Kwiatowa 5   | Laptop Dell   | 3000.00     | 1     |
| 1      | Jan Kowalski| ul. Kwiatowa 5   | Mysz          | 50.00       | 2     |
| 2      | Jan Kowalski| ul. Kwiatowa 5   | Laptop Dell   | 3000.00     | 1     |

-- Dane klienta i produktu powtarzają się!
```

### Przykład 2: Znormalizowana struktura (bez redundancji)
```sql
CREATE TABLE klienci (
    id_klienta INT PRIMARY KEY,
    nazwa VARCHAR(100),
    adres VARCHAR(200),
    telefon VARCHAR(15)
);

CREATE TABLE produkty (
    id_produktu INT PRIMARY KEY,
    nazwa VARCHAR(100),
    cena DECIMAL(10,2)
);

CREATE TABLE zamowienia (
    id_zamowienia INT PRIMARY KEY,
    id_klienta INT,
    data_zamowienia DATE,
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta)
);

CREATE TABLE pozycje_zamowien (
    id_zamowienia INT,
    id_produktu INT,
    ilosc INT,
    PRIMARY KEY (id_zamowienia, id_produktu),
    FOREIGN KEY (id_zamowienia) REFERENCES zamowienia(id_zamowienia),
    FOREIGN KEY (id_produktu) REFERENCES produkty(id_produktu)
);
```

## Problemy redundancji (Anomalie)

### 1. **Anomalia aktualizacji (Update Anomaly)**
```sql
-- Problem: Zmiana adresu klienta
UPDATE zamowienia_szczegoly 
SET klient_adres = 'ul. Nowa 10' 
WHERE klient_nazwa = 'Jan Kowalski';

-- Ryzyko: Można nie zaktualizować wszystkich wystąpień
-- Skutek: Niespójne dane - jeden klient z różnymi adresami
```

### 2. **Anomalia wstawiania (Insert Anomaly)**
```sql
-- Problem: Dodanie nowego produktu
-- Nie można dodać produktu bez zamówienia!
INSERT INTO zamowienia_szczegoly (produkt_nazwa, produkt_cena) 
VALUES ('Nowy tablet', 1500.00);
-- ERROR: Brakuje wymaganych kolumn zamówienia

-- Skutek: Nie można przechować produktu bez kontekstu zamówienia
```

### 3. **Anomalia usuwania (Delete Anomaly)**
```sql
-- Problem: Usunięcie ostatniego zamówienia dla produktu
DELETE FROM zamowienia_szczegoly 
WHERE id_zamowienia = 5;

-- Skutek: Utrata informacji o produkcie (jeśli to było jedyne zamówienie)
```

## Kontrolowana redundancja

### 1. **Denormalizacja dla wydajności**
```sql
-- Tabela zamówień z redundantną sumą (optymalizacja)
CREATE TABLE zamowienia (
    id_zamowienia INT PRIMARY KEY,
    id_klienta INT,
    data_zamowienia DATE,
    suma_zamowienia DECIMAL(15,2),  -- Redundancja kontrolowana!
    
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta)
);

CREATE TABLE pozycje_zamowien (
    id_zamowienia INT,
    id_produktu INT,
    ilosc INT,
    cena_jednostkowa DECIMAL(10,2), -- Redundancja - kopia z produkty.cena
    
    PRIMARY KEY (id_zamowienia, id_produktu)
);

-- Korzyść: Szybkie zapytania o sumę bez liczenia
SELECT suma_zamowienia FROM zamowienia WHERE id_zamowienia = 123;

-- Zamiast:
SELECT SUM(ilosc * cena_jednostkowa) 
FROM pozycje_zamowien 
WHERE id_zamowienia = 123;
```

### 2. **Materialized Views**
```sql
-- Redundancja poprzez zmaterializowany widok
CREATE MATERIALIZED VIEW sprzedaz_miesięczna AS
SELECT 
    EXTRACT(YEAR FROM data_zamowienia) as rok,
    EXTRACT(MONTH FROM data_zamowienia) as miesiac,
    COUNT(*) as liczba_zamowien,
    SUM(suma_zamowienia) as obroty
FROM zamowienia
GROUP BY EXTRACT(YEAR FROM data_zamowienia), EXTRACT(MONTH FROM data_zamowienia);

-- Dane są duplikowane, ale kontrolowane
REFRESH MATERIALIZED VIEW sprzedaz_miesięczna;
```

### 3. **Cachowanie danych**
```sql
-- Tabela statystyk (redundantne dane dla wydajności)
CREATE TABLE statystyki_klientow (
    id_klienta INT PRIMARY KEY,
    liczba_zamowien INT,
    suma_wydatkow DECIMAL(15,2),
    data_ostatniego_zamowienia DATE,
    ostatnia_aktualizacja TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta)
);

-- Aktualizacja przez triggery lub scheduled job
```

## Zarządzanie redundancją

### 1. **Triggery dla spójności**
```sql
-- Automatyczna aktualizacja redundantnych danych
CREATE OR REPLACE FUNCTION aktualizuj_sume_zamowienia()
RETURNS TRIGGER AS $$
BEGIN
    -- Aktualizuj sumę w tabeli zamówień
    UPDATE zamowienia 
    SET suma_zamowienia = (
        SELECT COALESCE(SUM(ilosc * cena_jednostkowa), 0)
        FROM pozycje_zamowien 
        WHERE id_zamowienia = NEW.id_zamowienia
    )
    WHERE id_zamowienia = NEW.id_zamowienia;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_suma_zamowienia
    AFTER INSERT OR UPDATE OR DELETE ON pozycje_zamowien
    FOR EACH ROW
    EXECUTE FUNCTION aktualizuj_sume_zamowienia();
```

### 2. **Procedury spójności danych**
```sql
-- Procedura sprawdzająca spójność redundantnych danych
CREATE OR REPLACE FUNCTION sprawdz_spojnosc_sum()
RETURNS TABLE(id_zamowienia INT, suma_obliczona DECIMAL, suma_zapisana DECIMAL) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        z.id_zamowienia,
        COALESCE(SUM(pz.ilosc * pz.cena_jednostkowa), 0) as suma_obliczona,
        z.suma_zamowienia as suma_zapisana
    FROM zamowienia z
    LEFT JOIN pozycje_zamowien pz ON z.id_zamowienia = pz.id_zamowienia
    GROUP BY z.id_zamowienia, z.suma_zamowienia
    HAVING COALESCE(SUM(pz.ilosc * pz.cena_jednostkowa), 0) != z.suma_zamowienia;
END;
$$ LANGUAGE plpgsql;

-- Użycie:
SELECT * FROM sprawdz_spojnosc_sum();
```

### 3. **Batch synchronization**
```sql
-- Okresowa synchronizacja danych
CREATE OR REPLACE FUNCTION synchronizuj_statystyki_klientow()
RETURNS VOID AS $$
BEGIN
    -- Aktualizuj statystyki dla wszystkich klientów
    INSERT INTO statystyki_klientow (id_klienta, liczba_zamowien, suma_wydatkow, data_ostatniego_zamowienia)
    SELECT 
        k.id_klienta,
        COUNT(z.id_zamowienia),
        COALESCE(SUM(z.suma_zamowienia), 0),
        MAX(z.data_zamowienia)
    FROM klienci k
    LEFT JOIN zamowienia z ON k.id_klienta = z.id_klienta
    GROUP BY k.id_klienta
    ON CONFLICT (id_klienta) DO UPDATE SET
        liczba_zamowien = EXCLUDED.liczba_zamowien,
        suma_wydatkow = EXCLUDED.suma_wydatkow,
        data_ostatniego_zamowienia = EXCLUDED.data_ostatniego_zamowienia,
        ostatnia_aktualizacja = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Zaplanuj uruchomienie co godzinę
-- Przez cron job lub scheduled task
```

## Strategie minimalizacji redundancji

### 1. **Normalizacja**
```sql
-- 1NF: Atomowe wartości
-- ❌ ŹLE
CREATE TABLE pracownicy (
    id INT,
    imie_nazwisko VARCHAR(100),  -- Nie atomowe!
    telefony VARCHAR(200)        -- Wielowartościowe!
);

-- ✅ DOBRZE
CREATE TABLE pracownicy (
    id INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50)
);

CREATE TABLE telefony_pracownikow (
    id_pracownika INT,
    numer VARCHAR(15),
    PRIMARY KEY (id_pracownika, numer),
    FOREIGN KEY (id_pracownika) REFERENCES pracownicy(id)
);
```

### 2. **Proper Foreign Keys**
```sql
-- Użyj kluczy obcych zamiast duplikowania danych
-- ❌ ŹLE
CREATE TABLE zamowienia (
    id INT PRIMARY KEY,
    klient_imie VARCHAR(50),     -- Redundancja!
    klient_nazwisko VARCHAR(50), -- Redundancja!
    klient_email VARCHAR(100)    -- Redundancja!
);

-- ✅ DOBRZE  
CREATE TABLE zamowienia (
    id INT PRIMARY KEY,
    id_klienta INT,
    FOREIGN KEY (id_klienta) REFERENCES klienci(id)
);
```

### 3. **Computed Columns / Views**
```sql
-- Zamiast przechowywać obliczone wartości, używaj widoków
CREATE VIEW zamowienia_szczegoly AS
SELECT 
    z.id_zamowienia,
    z.data_zamowienia,
    k.nazwa as klient_nazwa,
    k.adres as klient_adres,
    SUM(pz.ilosc * pz.cena_jednostkowa) as suma_zamowienia
FROM zamowienia z
JOIN klienci k ON z.id_klienta = k.id_klienta
JOIN pozycje_zamowien pz ON z.id_zamowienia = pz.id_zamowienia
GROUP BY z.id_zamowienia, z.data_zamowienia, k.nazwa, k.adres;
```

## Kiedy akceptować redundancję

### ✅ **Uzasadnione przypadki:**
1. **Wydajność krytyczna** - często wykonywane zapytania
2. **Dane historyczne** - snapshot w czasie
3. **Reporting/Analytics** - agregacje dla raportów
4. **Denormalizacja OLAP** - dla analiz danych
5. **Cached computations** - kosztowne obliczenia

### ❌ **Nieuzasadnione przypadki:**
1. **Brak znajomości normalizacji** - błędy projektowe
2. **Leniwe projektowanie** - kopiowanie zamiast związków
3. **Przedwczesna optymalizacja** - optymalizacja bez potrzeby
4. **Brak kontroli** - redundancja bez mechanizmów spójności

## Monitorowanie redundancji

### 1. **Sprawdzanie duplikatów**
```sql
-- Znajdź duplikaty w tabeli
SELECT nazwa, adres, telefon, COUNT(*)
FROM klienci
GROUP BY nazwa, adres, telefon
HAVING COUNT(*) > 1;

-- Znajdź potencjalnie redundantne dane
SELECT 
    t1.id as id1,
    t2.id as id2,
    t1.nazwa,
    t1.adres
FROM klienci t1
JOIN klienci t2 ON t1.nazwa = t2.nazwa AND t1.id < t2.id;
```

### 2. **Analiza rozmiaru tabel**
```sql
-- PostgreSQL - rozmiary tabel
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY size_bytes DESC;
```

### 3. **Sprawdzanie spójności**
```sql
-- Znajdź niespójności w redundantnych danych
SELECT z.id_zamowienia, 
       z.suma_zamowienia as zapisana_suma,
       calculated.obliczona_suma
FROM zamowienia z
JOIN (
    SELECT id_zamowienia, SUM(ilosc * cena_jednostkowa) as obliczona_suma
    FROM pozycje_zamowien
    GROUP BY id_zamowienia
) calculated ON z.id_zamowienia = calculated.id_zamowienia
WHERE ABS(z.suma_zamowienia - calculated.obliczona_suma) > 0.01;
```

## Narzędzia do zarządzania redundancją

### 1. **Database Constraints**
```sql
-- Ograniczenia sprawdzające spójność
ALTER TABLE zamowienia ADD CONSTRAINT check_suma_dodatnia
CHECK (suma_zamowienia >= 0);

-- Trigger sprawdzający spójność
CREATE CONSTRAINT TRIGGER check_suma_consistency
    AFTER INSERT OR UPDATE ON pozycje_zamowien
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW EXECUTE FUNCTION sprawdz_sume_zamowienia();
```

### 2. **ETL Processes**
```sql
-- Proces ETL dla aktualizacji redundantnych danych
CREATE OR REPLACE FUNCTION etl_aktualizuj_redundancje()
RETURNS VOID AS $$
BEGIN
    -- 1. Aktualizuj statystyki
    REFRESH MATERIALIZED VIEW sprzedaz_miesięczna;
    
    -- 2. Synchronizuj cache
    PERFORM synchronizuj_statystyki_klientow();
    
    -- 3. Sprawdź spójność
    IF EXISTS (SELECT 1 FROM sprawdz_spojnosc_sum()) THEN
        RAISE WARNING 'Znaleziono niespójności w sumach zamówień';
    END IF;
    
    -- 4. Log operacji
    INSERT INTO log_etl (operacja, data_wykonania, status)
    VALUES ('aktualizacja_redundancji', CURRENT_TIMESTAMP, 'SUCCESS');
END;
$$ LANGUAGE plpgsql;
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**
1. **Dokumentuj redundancję** - gdzie i dlaczego
2. **Automatyzuj synchronizację** - triggery, procedury
3. **Monitoruj spójność** - regularne sprawdzenia
4. **Wersjonuj dane** - trackuj zmiany redundantnych danych
5. **Testuj mechanizmy** - upewnij się że synchronizacja działa

### ❌ **Złe praktyki:**
1. **Redundancja bez kontroli** - brak mechanizmów spójności
2. **Nadmierna denormalizacja** - wszystko w jednej tabeli
3. **Ignorowanie anomalii** - nie obsługuj problemów redundancji
4. **Brak dokumentacji** - nikt nie wie co jest redundantne
5. **Manualna synchronizacja** - poleganie na działaniach ręcznych

## Pułapki egzaminacyjne

### 1. **Anomalie danych**
- **Update**: Niespójne zmiany
- **Insert**: Niemożność dodania bez kontekstu
- **Delete**: Utrata informacji

### 2. **Kontrolowana vs niekontrolowana**
- **Kontrolowana**: Świadoma, z mechanizmami spójności
- **Niekontrolowana**: Przypadkowa, problematyczna

### 3. **Normalizacja vs denormalizacja**
- **Normalizacja**: Eliminuje redundancję, może obniżyć wydajność
- **Denormalizacja**: Zwiększa redundancję, może poprawić wydajność

### 4. **Mechanizmy spójności**
- **Triggery**: Automatyczne, w czasie rzeczywistym
- **Constraints**: Strukturalne ograniczenia
- **ETL**: Batch processing, okresowa synchronizacja