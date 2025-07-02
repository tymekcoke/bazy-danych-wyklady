# 🔧 SQL DDL ZAAWANSOWANY - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"SQL DDL zaawansowany obejmuje kompleksowe zarządzanie strukturą bazy danych:

1. **ALTER TABLE** - modyfikacja istniejących tabel (kolumny, constraints, indeksy)
2. **CREATE/DROP** - zarządzanie obiektami DB (widoki, sekwencje, funkcje)
3. **CONSTRAINTS** - ograniczenia integralności (CHECK, UNIQUE, FOREIGN KEY)
4. **INDEKSY** - różne typy indeksów dla optymalizacji
5. **SCHEMATY** - organizacja obiektów w przestrzenie nazw
6. **SEQUENCES** - generatory unikalnych wartości

DDL zaawansowany umożliwia precyzyjne kształtowanie struktury bazy danych z zachowaniem wydajności i integralności."

## ✍️ CO NAPISAĆ NA KARTCE

```sql
SQL DDL ZAAWANSOWANY - KLUCZOWE OPERACJE:

ALTER TABLE - MODYFIKACJA STRUKTURY:
• ADD COLUMN - dodanie kolumny
• DROP COLUMN - usunięcie kolumny  
• ALTER COLUMN - zmiana typu/constraints
• ADD CONSTRAINT - dodanie ograniczenia
• DROP CONSTRAINT - usunięcie ograniczenia
• RENAME - zmiana nazwy tabeli/kolumny

PRZYKŁADY ALTER TABLE:
ALTER TABLE pracownicy 
ADD COLUMN telefon VARCHAR(20),
ADD CONSTRAINT chk_pensja CHECK (pensja > 0),
ALTER COLUMN email SET NOT NULL;

TYPY INDEKSÓW:
• B-tree (domyślny) - równość, zakresy
• Hash - tylko równość
• GiST - geometria, full-text
• GIN - arrays, JSONB, full-text
• BRIN - bardzo duże tabele chronologiczne
• Partial - z warunkiem WHERE
• Functional - na wyrażeniach

CREATE INDEX idx_name ON table(column);
CREATE UNIQUE INDEX idx_unique ON table(col);
CREATE INDEX idx_partial ON table(col) WHERE condition;

CONSTRAINTS ZAAWANSOWANE:
• CHECK - walidacja wartości
• UNIQUE - unikalność (NULL dozwolone)
• FOREIGN KEY - integralność referencyjna
• PRIMARY KEY - klucz główny  
• EXCLUSION - wykluczanie nakładających się wartości

SCHEMATY I ORGANIZACJA:
CREATE SCHEMA nazwa;
SET search_path TO schema1, schema2, public;
CREATE TABLE schema.tabela (...);

SEQUENCES:
CREATE SEQUENCE seq_name START 1 INCREMENT 1;
SELECT nextval('seq_name');
SELECT currval('seq_name');
ALTER SEQUENCE seq_name RESTART WITH 100;

VIEWS I MATERIALIZED VIEWS:
CREATE VIEW v_name AS SELECT ...;
CREATE MATERIALIZED VIEW mv_name AS SELECT ...;
REFRESH MATERIALIZED VIEW mv_name;

PARTITIONING:
CREATE TABLE parent (...) PARTITION BY RANGE(date);
CREATE TABLE child PARTITION OF parent 
FOR VALUES FROM ('2024-01-01') TO ('2024-12-31');
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- KOMPLEKSOWY PRZYKŁAD SQL DDL ZAAWANSOWANY

-- 1. TWORZENIE SCHEMATU I PODSTAWOWYCH STRUKTUR

-- Schemat dla systemu HR
CREATE SCHEMA hr;
CREATE SCHEMA finance;

-- Ustawienie ścieżki wyszukiwania
SET search_path TO hr, finance, public;

-- 2. TABELE Z ZAAWANSOWANYMI CONSTRAINTS

-- Tabela pracowników z różnymi ograniczeniami
CREATE TABLE hr.pracownicy (
    id SERIAL PRIMARY KEY,
    pesel VARCHAR(11) UNIQUE NOT NULL,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    telefon VARCHAR(20),
    data_urodzenia DATE,
    data_zatrudnienia DATE DEFAULT CURRENT_DATE,
    pensja DECIMAL(10,2),
    bonus DECIMAL(10,2) DEFAULT 0,
    aktywny BOOLEAN DEFAULT TRUE,
    
    -- CHECK constraints
    CONSTRAINT chk_pesel_format 
        CHECK (pesel ~ '^[0-9]{11}$'),
    CONSTRAINT chk_email_format 
        CHECK (email ~ '^[^@]+@[^@]+\.[^@]+$'),
    CONSTRAINT chk_pensja_pozytywna 
        CHECK (pensja > 0),
    CONSTRAINT chk_bonus_nieujemny 
        CHECK (bonus >= 0),
    CONSTRAINT chk_data_urodzenia 
        CHECK (data_urodzenia > '1900-01-01' AND data_urodzenia < CURRENT_DATE),
    CONSTRAINT chk_data_zatrudnienia
        CHECK (data_zatrudnienia >= data_urodzenia + INTERVAL '16 years'),
    CONSTRAINT chk_wiek_emerytalny
        CHECK (EXTRACT(YEAR FROM AGE(data_urodzenia)) < 67)
);

-- Tabela departamentów
CREATE TABLE hr.departamenty (
    id SERIAL PRIMARY KEY,
    nazwa VARCHAR(100) UNIQUE NOT NULL,
    kod VARCHAR(10) UNIQUE NOT NULL,
    budzet DECIMAL(12,2),
    kierownik_id INT,
    
    CONSTRAINT chk_kod_format 
        CHECK (kod ~ '^[A-Z]{2,5}$'),
    CONSTRAINT chk_budzet_pozytywny 
        CHECK (budzet > 0)
);

-- 3. MODYFIKACJE STRUKTURY TABEL

-- Dodanie kolumny departament do pracowników
ALTER TABLE hr.pracownicy 
ADD COLUMN departament_id INT;

-- Dodanie klucza obcego
ALTER TABLE hr.pracownicy
ADD CONSTRAINT fk_pracownik_departament
    FOREIGN KEY (departament_id) REFERENCES hr.departamenty(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE;

-- Dodanie klucza obcego kierownik w departamentach
ALTER TABLE hr.departamenty
ADD CONSTRAINT fk_departament_kierownik
    FOREIGN KEY (kierownik_id) REFERENCES hr.pracownicy(id)
    ON DELETE SET NULL;

-- Modyfikacja istniejącej kolumny
ALTER TABLE hr.pracownicy 
ALTER COLUMN email SET NOT NULL;

-- Dodanie nowego constraint
ALTER TABLE hr.pracownicy
ADD CONSTRAINT chk_pensja_vs_bonus
    CHECK (bonus <= pensja * 0.5);

-- 4. SEKWENCJE I GENERATORY

-- Własna sekwencja dla numerów pracowników
CREATE SEQUENCE hr.seq_nr_pracownika 
    START WITH 1000 
    INCREMENT BY 1 
    MINVALUE 1000 
    MAXVALUE 999999 
    CACHE 10;

-- Dodanie kolumny z sekwencją
ALTER TABLE hr.pracownicy 
ADD COLUMN nr_pracownika INT UNIQUE DEFAULT nextval('hr.seq_nr_pracownika');

-- Sekwencja dla kodów departamentów
CREATE SEQUENCE hr.seq_departament_id
    START WITH 10
    INCREMENT BY 10;

-- 5. RÓŻNE TYPY INDEKSÓW

-- B-tree index (domyślny) - dla wyszukiwania po nazwisku
CREATE INDEX idx_pracownicy_nazwisko ON hr.pracownicy(nazwisko);

-- Złożony indeks
CREATE INDEX idx_pracownicy_dept_pensja ON hr.pracownicy(departament_id, pensja DESC);

-- Partial index - tylko aktywni pracownicy
CREATE INDEX idx_pracownicy_aktywni_email 
ON hr.pracownicy(email) 
WHERE aktywny = TRUE;

-- Functional index - wyszukiwanie case-insensitive
CREATE INDEX idx_pracownicy_nazwisko_lower 
ON hr.pracownicy(LOWER(nazwisko));

-- Unique index z warunkiem
CREATE UNIQUE INDEX idx_departament_kierownik_aktywny
ON hr.departamenty(kierownik_id)
WHERE kierownik_id IS NOT NULL;

-- 6. HASH INDEX (dla równości)
CREATE INDEX idx_pracownicy_pesel_hash 
ON hr.pracownicy USING HASH(pesel);

-- 7. ZAAWANSOWANE TYPY DANYCH I INDEKSY

-- Tabela z zaawansowanymi typami
CREATE TABLE hr.dokumenty (
    id SERIAL PRIMARY KEY,
    pracownik_id INT REFERENCES hr.pracownicy(id),
    nazwa VARCHAR(200),
    tresc TEXT,
    metadane JSONB,
    tagi TEXT[],
    data_utworzenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Full-text search vector
    search_vector tsvector
);

-- GIN index dla JSONB
CREATE INDEX idx_dokumenty_metadane_gin 
ON hr.dokumenty USING GIN(metadane);

-- GIN index dla arrays
CREATE INDEX idx_dokumenty_tagi_gin 
ON hr.dokumenty USING GIN(tagi);

-- GIN index dla full-text search
CREATE INDEX idx_dokumenty_search_gin 
ON hr.dokumenty USING GIN(search_vector);

-- 8. TRIGGERY DLA UTRZYMANIA INDEKSÓW

-- Trigger automatycznie aktualizujący search_vector
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('polish', COALESCE(NEW.nazwa, '')), 'A') ||
        setweight(to_tsvector('polish', COALESCE(NEW.tresc, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_update_search_vector
    BEFORE INSERT OR UPDATE ON hr.dokumenty
    FOR EACH ROW
    EXECUTE FUNCTION update_search_vector();

-- 9. WIDOKI I MATERIALIZED VIEWS

-- Widok z informacjami o pracownikach i departamentach
CREATE VIEW hr.v_pracownicy_full AS
SELECT 
    p.id,
    p.nr_pracownika,
    p.imie,
    p.nazwisko,
    p.email,
    p.pensja,
    p.bonus,
    p.pensja + p.bonus as wynagrodzenie_calkowite,
    d.nazwa as departament,
    d.kod as kod_departamentu,
    EXTRACT(YEAR FROM AGE(p.data_urodzenia)) as wiek,
    EXTRACT(YEAR FROM AGE(p.data_zatrudnienia)) as staz
FROM hr.pracownicy p
LEFT JOIN hr.departamenty d ON p.departament_id = d.id
WHERE p.aktywny = TRUE;

-- Materialized view z statystykami departamentów
CREATE MATERIALIZED VIEW hr.mv_statystyki_departamentow AS
SELECT 
    d.id,
    d.nazwa,
    d.kod,
    COUNT(p.id) as liczba_pracownikow,
    AVG(p.pensja) as srednia_pensja,
    SUM(p.pensja + p.bonus) as suma_wynagrodzen,
    MIN(p.data_zatrudnienia) as najstarszy_pracownik,
    MAX(p.data_zatrudnienia) as najnowszy_pracownik
FROM hr.departamenty d
LEFT JOIN hr.pracownicy p ON d.id = p.departament_id AND p.aktywny = TRUE
GROUP BY d.id, d.nazwa, d.kod;

-- Index na materialized view
CREATE INDEX idx_mv_stat_dept_nazwa ON hr.mv_statystyki_departamentow(nazwa);

-- 10. PARTYCJONOWANIE TABEL

-- Tabela z partycjonowaniem po dacie
CREATE TABLE hr.historia_wynagrodzen (
    id SERIAL,
    pracownik_id INT NOT NULL,
    stara_pensja DECIMAL(10,2),
    nowa_pensja DECIMAL(10,2),
    data_zmiany DATE NOT NULL,
    powod VARCHAR(200),
    zatwierdzone_przez INT
) PARTITION BY RANGE (data_zmiany);

-- Partycje dla różnych lat
CREATE TABLE hr.historia_wynagrodzen_2023 
PARTITION OF hr.historia_wynagrodzen
FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE hr.historia_wynagrodzen_2024
PARTITION OF hr.historia_wynagrodzen  
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE hr.historia_wynagrodzen_2025
PARTITION OF hr.historia_wynagrodzen
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Indeksy na partycjach
CREATE INDEX idx_hist_wyn_2024_pracownik 
ON hr.historia_wynagrodzen_2024(pracownik_id);

-- 11. DOMENY I TYPY UŻYTKOWNIKA

-- Definicja domeny dla PESEL
CREATE DOMAIN typ_pesel AS VARCHAR(11)
    CHECK (VALUE ~ '^[0-9]{11}$');

-- Definicja domeny dla email
CREATE DOMAIN typ_email AS VARCHAR(100)
    CHECK (VALUE ~ '^[^@]+@[^@]+\.[^@]+$');

-- Typ wyliczeniowy dla statusu pracownika
CREATE TYPE status_pracownika AS ENUM (
    'aktywny', 'nieaktywny', 'urlop', 'zwolnienie_lekarskie', 'wypowiedony'
);

-- Modyfikacja tabeli o nowe typy
ALTER TABLE hr.pracownicy 
ADD COLUMN pesel_nowy typ_pesel,
ADD COLUMN email_nowy typ_email,
ADD COLUMN status status_pracownika DEFAULT 'aktywny';

-- 12. CONSTRAINTS Z ODROCZONYM SPRAWDZANIEM

-- Dodanie deferrable constraint dla wzajemnych referencji
ALTER TABLE hr.departamenty
DROP CONSTRAINT fk_departament_kierownik;

ALTER TABLE hr.departamenty
ADD CONSTRAINT fk_departament_kierownik
    FOREIGN KEY (kierownik_id) REFERENCES hr.pracownicy(id)
    DEFERRABLE INITIALLY DEFERRED;

-- 13. EXCLUSION CONSTRAINTS

-- Tabela z constraint wykluczającym nakładające się okresy
CREATE TABLE hr.urlopy (
    id SERIAL PRIMARY KEY,
    pracownik_id INT REFERENCES hr.pracownicy(id),
    data_rozpoczecia DATE NOT NULL,
    data_zakonczenia DATE NOT NULL,
    typ VARCHAR(50),
    
    CONSTRAINT chk_urlop_daty 
        CHECK (data_zakonczenia > data_rozpoczecia),
    
    -- Exclusion constraint - pracownik nie może mieć nakładających się urlopów
    EXCLUDE USING gist (
        pracownik_id WITH =,
        daterange(data_rozpoczecia, data_zakonczenia, '[]') WITH &&
    )
);

-- 14. FUNKCJE I PROCEDURY DDL

-- Funkcja do automatycznego tworzenia partycji
CREATE OR REPLACE FUNCTION create_monthly_partition(
    table_name TEXT,
    year_month DATE
) RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    partition_name := table_name || '_' || to_char(year_month, 'YYYY_MM');
    start_date := date_trunc('month', year_month);
    end_date := start_date + INTERVAL '1 month';
    
    EXECUTE format('
        CREATE TABLE IF NOT EXISTS %I 
        PARTITION OF %I
        FOR VALUES FROM (%L) TO (%L)',
        partition_name, table_name, start_date, end_date
    );
    
    RAISE NOTICE 'Created partition: %', partition_name;
END;
$$ LANGUAGE plpgsql;

-- Użycie funkcji
SELECT create_monthly_partition('hr.historia_wynagrodzen', '2024-06-01');

-- 15. MONITORING I UTRZYMANIE

-- Analiza wykorzystania indeksów
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;

-- Sprawdzenie rozmiaru tabel i indeksów
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - 
                   pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables 
WHERE schemaname = 'hr'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 16. BACKUP I RESTORE STRUKTUR

-- Backup tylko struktury (bez danych)
-- pg_dump -s -n hr mydb > hr_schema_backup.sql

-- Backup z danymi
-- pg_dump -n hr mydb > hr_full_backup.sql

-- 17. BEZPIECZEŃSTWO DDL

-- Revoke domyślnych uprawnień
REVOKE ALL ON SCHEMA hr FROM public;

-- Grant selektywnych uprawnień
GRANT USAGE ON SCHEMA hr TO hr_users;
GRANT SELECT ON ALL TABLES IN SCHEMA hr TO hr_readonly;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA hr TO hr_users;
GRANT ALL ON ALL TABLES IN SCHEMA hr TO hr_admin;

-- 18. PRZYKŁAD KOMPLETNEJ PROCEDURY DEPLOYMENTU

CREATE OR REPLACE FUNCTION deploy_hr_changes()
RETURNS VOID AS $$
BEGIN
    -- Begin transaction
    BEGIN
        -- 1. Dodaj nowe kolumny
        ALTER TABLE hr.pracownicy ADD COLUMN IF NOT EXISTS ostatnia_ocena DATE;
        
        -- 2. Utwórz nowe indeksy
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pracownicy_ostatnia_ocena 
        ON hr.pracownicy(ostatnia_ocena) WHERE ostatnia_ocena IS NOT NULL;
        
        -- 3. Odśwież materialized views
        REFRESH MATERIALIZED VIEW hr.mv_statystyki_departamentow;
        
        -- 4. Utwórz nowe partycje jeśli potrzebne
        PERFORM create_monthly_partition('hr.historia_wynagrodzen', CURRENT_DATE);
        
        RAISE NOTICE 'Deployment completed successfully';
        
    EXCEPTION WHEN OTHERS THEN
        RAISE EXCEPTION 'Deployment failed: %', SQLERRM;
    END;
END;
$$ LANGUAGE plpgsql;

-- Wykonanie deploymentu
SELECT deploy_hr_changes();
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: ALTER TABLE może blokować tabelę podczas modyfikacji
2. **UWAGA**: DROP COLUMN usuwa dane bezpowrotnie
3. **BŁĄD**: Nie wszystkie zmiany typu kolumny są możliwe bez konwersji
4. **WAŻNE**: UNIQUE constraint pozwala na NULL w PostgreSQL
5. **PUŁAPKA**: Constraints są sprawdzane przy każdej modyfikacji

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **ALTER TABLE** - modyfikacja struktury tabeli
- **Constraints** - ograniczenia integralności
- **Index types** - typy indeksów (B-tree, GIN, GiST)
- **Partitioning** - partycjonowanie tabel
- **Materialized views** - zmaterializowane widoki
- **Sequences** - sekwencje generatorów
- **Schemas** - schematy bazy danych
- **DDL optimization** - optymalizacja DDL

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **01-integralnosc** - constraints i ograniczenia
- **12-klucze-bazy-danych** - implementacja kluczy
- **42-optymalizacja-wydajnosci** - indeksy i wydajność
- **39-bezpieczenstwo-baz-danych** - uprawnienia DDL
- **40-backup-i-recovery** - backup struktur