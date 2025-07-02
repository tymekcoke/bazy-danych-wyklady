# SQL DDL - CREATE, ALTER, DROP

## Definicja DDL

**Data Definition Language (DDL)** to **podzbiór SQL** służący do **definiowania i modyfikowania struktury** bazy danych, w tym tabel, indeksów, ograniczeń, schematów i innych obiektów.

### Kluczowe cechy DDL:
- **Struktura, nie dane** - operuje na schematach, nie na zawartości
- **Autocommit** - większość operacji DDL jest automatycznie commitowana
- **Uprawnienia** - wymagane specjalne uprawnienia (CREATE, ALTER, DROP)
- **Transakcyjność** - różnie obsługiwana w różnych SZBD

### Główne polecenia DDL:
```sql
CREATE    -- Tworzenie obiektów
ALTER     -- Modyfikacja istniejących obiektów  
DROP      -- Usuwanie obiektów
TRUNCATE  -- Szybkie usuwanie wszystkich danych z tabeli
COMMENT   -- Dodawanie komentarzy
RENAME    -- Zmiana nazw obiektów
```

## CREATE - Tworzenie obiektów

### 1. **CREATE DATABASE/SCHEMA**

#### PostgreSQL:
```sql
-- Tworzenie bazy danych
CREATE DATABASE sklep_internetowy
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'pl_PL.UTF-8'
    LC_CTYPE = 'pl_PL.UTF-8'
    TABLESPACE = pg_default
    CONNECTION_LIMIT = 100;

-- Tworzenie schematu
CREATE SCHEMA IF NOT EXISTS sprzedaz 
    AUTHORIZATION admin;

CREATE SCHEMA AUTHORIZATION user_schema;  -- Schema o nazwie użytkownika
```

#### MySQL:
```sql
-- Tworzenie bazy danych
CREATE DATABASE sklep_internetowy
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- MySQL nie ma schematów - DATABASE = SCHEMA
CREATE SCHEMA sklep_internetowy;  -- Równoważne z CREATE DATABASE
```

#### SQL Server:
```sql
-- Tworzenie bazy danych
CREATE DATABASE sklep_internetowy
ON (
    NAME = 'sklep_data',
    FILENAME = 'C:\Data\sklep.mdf',
    SIZE = 100MB,
    MAXSIZE = 1GB,
    FILEGROWTH = 10MB
)
LOG ON (
    NAME = 'sklep_log',
    FILENAME = 'C:\Data\sklep.ldf',
    SIZE = 10MB,
    FILEGROWTH = 10%
);

-- Tworzenie schematu
CREATE SCHEMA sprzedaz AUTHORIZATION dbo;
```

### 2. **CREATE TABLE**

#### Składnia podstawowa:
```sql
CREATE TABLE [IF NOT EXISTS] nazwa_tabeli (
    kolumna1 typ_danych [ograniczenia],
    kolumna2 typ_danych [ograniczenia],
    ...,
    [ograniczenia_tabelowe]
);
```

#### Przykład kompletny:
```sql
CREATE TABLE klienci (
    id_klienta SERIAL PRIMARY KEY,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefon VARCHAR(15),
    data_rejestracji DATE DEFAULT CURRENT_DATE,
    aktywny BOOLEAN DEFAULT TRUE,
    wiek INTEGER CHECK (wiek >= 18 AND wiek <= 120),
    
    CONSTRAINT uk_email UNIQUE (email),
    CONSTRAINT chk_telefon CHECK (telefon ~ '^\d{3}-\d{3}-\d{3}$')
);
```

#### Typy danych w różnych SZBD:

##### PostgreSQL:
```sql
CREATE TABLE typy_postgresql (
    -- Numeryczne
    id SERIAL,                           -- AUTO_INCREMENT
    big_id BIGSERIAL,                    -- BIGINT AUTO_INCREMENT
    cena NUMERIC(10,2),                  -- Dokładne liczby dziesiętne
    koszt DECIMAL(15,4),                 -- Alias dla NUMERIC
    waga REAL,                           -- Single precision float
    precyzja DOUBLE PRECISION,           -- Double precision float
    ilosc INTEGER,                       -- 32-bit integer
    duza_ilosc BIGINT,                   -- 64-bit integer
    mala_ilosc SMALLINT,                 -- 16-bit integer
    
    -- Tekstowe
    kod CHAR(5),                         -- Stała długość
    nazwa VARCHAR(100),                  -- Zmienna długość
    opis TEXT,                           -- Nieograniczona długość
    
    -- Data i czas
    data_utworzenia DATE,                -- Tylko data
    czas_utworzenia TIME,                -- Tylko czas
    timestamp_utworzenia TIMESTAMP,      -- Data + czas
    timestamp_z_zona TIMESTAMPTZ,        -- Z timezone
    
    -- Logiczne
    aktywny BOOLEAN,                     -- TRUE/FALSE/NULL
    
    -- JSON
    metadane JSON,                       -- JSON data
    strukturalne JSONB,                  -- Binary JSON (wydajniejsze)
    
    -- Arrays (PostgreSQL specific)
    tagi TEXT[],                         -- Array tekstów
    liczby INTEGER[],                    -- Array liczb
    
    -- UUID
    uuid_kolumna UUID,                   -- Universally Unique Identifier
    
    -- Geometryczne (PostGIS extension)
    lokalizacja POINT,                   -- Współrzędne
    obszar POLYGON                       -- Wielokąt
);
```

##### MySQL:
```sql
CREATE TABLE typy_mysql (
    -- Numeryczne
    id INT AUTO_INCREMENT PRIMARY KEY,
    big_id BIGINT AUTO_INCREMENT,
    cena DECIMAL(10,2),
    koszt NUMERIC(15,4),
    waga FLOAT,
    precyzja DOUBLE,
    ilosc INT,
    duza_ilosc BIGINT,
    mala_ilosc SMALLINT,
    bardzo_mala TINYINT,
    
    -- Tekstowe
    kod CHAR(5),
    nazwa VARCHAR(100),
    opis TEXT,
    dlugi_opis LONGTEXT,
    sredni_opis MEDIUMTEXT,
    krotki_opis TINYTEXT,
    
    -- Binarne
    obrazek BLOB,
    duzy_plik LONGBLOB,
    
    -- Data i czas
    data_utworzenia DATE,
    czas_utworzenia TIME,
    timestamp_utworzenia DATETIME,
    timestamp_auto TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rok YEAR,
    
    -- Enumeracje
    status ENUM('aktywny', 'nieaktywny', 'zawieszony'),
    uprawnienia SET('read', 'write', 'admin'),
    
    -- JSON (MySQL 5.7+)
    metadane JSON
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

##### SQL Server:
```sql
CREATE TABLE typy_sqlserver (
    -- Numeryczne
    id INT IDENTITY(1,1) PRIMARY KEY,
    big_id BIGINT,
    cena MONEY,                          -- Currency
    mala_cena SMALLMONEY,
    koszt DECIMAL(15,4),
    waga FLOAT,
    precyzja REAL,
    ilosc INT,
    
    -- Tekstowe
    kod NCHAR(5),                        -- Unicode fixed
    nazwa NVARCHAR(100),                 -- Unicode variable
    opis NVARCHAR(MAX),                  -- Large unicode
    stary_tekst VARCHAR(100),            -- Non-unicode
    
    -- Binarne
    obrazek VARBINARY(MAX),
    hash_binary BINARY(16),
    
    -- Data i czas
    data_utworzenia DATE,
    czas_utworzenia TIME,
    timestamp_utworzenia DATETIME2,      -- High precision
    timestamp_stary DATETIME,            -- Legacy
    timestamp_offset DATETIMEOFFSET,     -- With timezone
    
    -- Unikalne dla SQL Server
    xml_data XML,                        -- Native XML
    hierarchia HIERARCHYID,              -- Hierarchical data
    geografia GEOGRAPHY,                 -- Geographic data
    geometria GEOMETRY,                  -- Geometric data
    guid_kolumna UNIQUEIDENTIFIER        -- GUID
);
```

#### Ograniczenia kolumn:
```sql
CREATE TABLE przykład_ograniczen (
    id INTEGER,
    
    -- PRIMARY KEY
    id_pk INTEGER PRIMARY KEY,
    id_pk_named INTEGER CONSTRAINT pk_id PRIMARY KEY,
    
    -- NOT NULL
    wymagane VARCHAR(50) NOT NULL,
    
    -- UNIQUE
    unikalny VARCHAR(100) UNIQUE,
    unikalny_named VARCHAR(100) CONSTRAINT uk_nazwa UNIQUE,
    
    -- CHECK
    wiek INTEGER CHECK (wiek >= 0),
    plec CHAR(1) CHECK (plec IN ('M', 'K')),
    email VARCHAR(100) CHECK (email LIKE '%@%'),
    
    -- DEFAULT
    data_utworzenia DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'aktywny',
    licznik INTEGER DEFAULT 0,
    
    -- FOREIGN KEY
    kategoria_id INTEGER REFERENCES kategorie(id),
    klient_id INTEGER CONSTRAINT fk_klient 
        REFERENCES klienci(id) ON DELETE CASCADE,
    
    -- Złożone ograniczenia
    CONSTRAINT pk_composite PRIMARY KEY (id, kategoria_id),
    CONSTRAINT uk_composite UNIQUE (email, telefon),
    CONSTRAINT chk_data_range CHECK (data_rozpoczecia <= data_zakonczenia)
);
```

### 3. **CREATE INDEX**

#### Indeksy podstawowe:
```sql
-- Indeks zwykły
CREATE INDEX idx_nazwisko ON pracownicy(nazwisko);

-- Indeks unikalny
CREATE UNIQUE INDEX idx_email ON klienci(email);

-- Indeks złożony
CREATE INDEX idx_imie_nazwisko ON pracownicy(imie, nazwisko);

-- Indeks z warunkiem (PostgreSQL)
CREATE INDEX idx_aktywni ON klienci(nazwisko) WHERE aktywny = TRUE;

-- Indeks funkcyjny
CREATE INDEX idx_upper_email ON klienci(UPPER(email));

-- Indeks z sortowaniem
CREATE INDEX idx_data_desc ON zamowienia(data_zamowienia DESC);
```

#### Typy indeksów w PostgreSQL:
```sql
-- B-tree (domyślny)
CREATE INDEX idx_btree ON tabela(kolumna);

-- Hash (dla równości)
CREATE INDEX idx_hash ON tabela USING HASH(kolumna);

-- GIN (dla pełnotekstowego wyszukiwania)
CREATE INDEX idx_gin ON tabela USING GIN(kolumna_tsvector);

-- GiST (dla danych geometrycznych)
CREATE INDEX idx_gist ON tabela USING GIST(kolumna_geometry);

-- BRIN (dla bardzo dużych tabel)
CREATE INDEX idx_brin ON duza_tabela USING BRIN(timestamp_kolumna);
```

#### Indeksy w MySQL:
```sql
-- Indeks zwykły
CREATE INDEX idx_nazwisko ON pracownicy(nazwisko);

-- Indeks pełnotekstowy
CREATE FULLTEXT INDEX idx_fulltext ON artykuly(tytul, tresc);

-- Indeks spatial (dla danych geograficznych)
CREATE SPATIAL INDEX idx_spatial ON lokacje(wspolrzedne);

-- Indeks z prefiksem
CREATE INDEX idx_prefix ON tabela(dluga_kolumna(10));
```

### 4. **CREATE VIEW**

#### Widoki podstawowe:
```sql
-- Widok prosty
CREATE VIEW aktywni_klienci AS
SELECT id_klienta, imie, nazwisko, email
FROM klienci
WHERE aktywny = TRUE;

-- Widok z JOIN
CREATE VIEW zamowienia_szczegoly AS
SELECT 
    z.id_zamowienia,
    z.data_zamowienia,
    k.imie,
    k.nazwisko,
    z.wartosc_total
FROM zamowienia z
JOIN klienci k ON z.id_klienta = k.id_klienta;

-- Widok z agregacją
CREATE VIEW statystyki_klientow AS
SELECT 
    k.id_klienta,
    k.imie,
    k.nazwisko,
    COUNT(z.id_zamowienia) as liczba_zamowien,
    COALESCE(SUM(z.wartosc_total), 0) as suma_zamowien
FROM klienci k
LEFT JOIN zamowienia z ON k.id_klienta = z.id_klienta
GROUP BY k.id_klienta, k.imie, k.nazwisko;
```

#### Materialized Views (PostgreSQL):
```sql
-- Materialized view
CREATE MATERIALIZED VIEW mv_miesięczne_statystyki AS
SELECT 
    EXTRACT(YEAR FROM data_zamowienia) as rok,
    EXTRACT(MONTH FROM data_zamowienia) as miesiac,
    COUNT(*) as liczba_zamowien,
    SUM(wartosc_total) as suma_sprzedazy
FROM zamowienia
GROUP BY EXTRACT(YEAR FROM data_zamowienia), EXTRACT(MONTH FROM data_zamowienia)
WITH DATA;

-- Odświeżanie
REFRESH MATERIALIZED VIEW mv_miesięczne_statystyki;

-- Odświeżanie bez blokowania
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_miesięczne_statystyki;
```

## ALTER - Modyfikacja obiektów

### 1. **ALTER TABLE**

#### Dodawanie kolumn:
```sql
-- Dodanie prostej kolumny
ALTER TABLE klienci ADD COLUMN wiek INTEGER;

-- Dodanie kolumny z ograniczeniami
ALTER TABLE klienci ADD COLUMN 
    telefon_komorkowy VARCHAR(15) CHECK (telefon_komorkowy ~ '^\d{3}-\d{3}-\d{3}$');

-- Dodanie kolumny z wartością domyślną
ALTER TABLE produkty ADD COLUMN 
    data_dodania DATE DEFAULT CURRENT_DATE NOT NULL;

-- Dodanie kilku kolumn naraz
ALTER TABLE zamowienia 
    ADD COLUMN status VARCHAR(20) DEFAULT 'nowe',
    ADD COLUMN priorytet INTEGER DEFAULT 1;
```

#### Modyfikacja kolumn:
```sql
-- PostgreSQL
ALTER TABLE klienci ALTER COLUMN email TYPE VARCHAR(200);
ALTER TABLE klienci ALTER COLUMN aktywny SET DEFAULT FALSE;
ALTER TABLE klienci ALTER COLUMN aktywny DROP DEFAULT;
ALTER TABLE klienci ALTER COLUMN imie SET NOT NULL;
ALTER TABLE klienci ALTER COLUMN telefon DROP NOT NULL;

-- MySQL
ALTER TABLE klienci MODIFY COLUMN email VARCHAR(200) NOT NULL;
ALTER TABLE klienci ALTER COLUMN aktywny SET DEFAULT FALSE;

-- SQL Server  
ALTER TABLE klienci ALTER COLUMN email VARCHAR(200) NOT NULL;
```

#### Usuwanie kolumn:
```sql
-- Usunięcie pojedynczej kolumny
ALTER TABLE klienci DROP COLUMN telefon;

-- Usunięcie kilku kolumn (PostgreSQL)
ALTER TABLE klienci 
    DROP COLUMN telefon,
    DROP COLUMN fax;

-- Usunięcie z sprawdzeniem
ALTER TABLE klienci DROP COLUMN IF EXISTS stara_kolumna;

-- Usunięcie CASCADE (usuwa też zależności)
ALTER TABLE klienci DROP COLUMN adres CASCADE;
```

#### Zmiana nazw:
```sql
-- PostgreSQL
ALTER TABLE klienci RENAME COLUMN imie TO first_name;
ALTER TABLE stara_nazwa RENAME TO nowa_nazwa;

-- MySQL
ALTER TABLE klienci CHANGE imie first_name VARCHAR(50);
ALTER TABLE stara_nazwa RENAME TO nowa_nazwa;

-- SQL Server
EXEC sp_rename 'klienci.imie', 'first_name', 'COLUMN';
EXEC sp_rename 'stara_nazwa', 'nowa_nazwa';
```

### 2. **ALTER TABLE - Ograniczenia**

#### Dodawanie ograniczeń:
```sql
-- PRIMARY KEY
ALTER TABLE klienci ADD CONSTRAINT pk_klienci PRIMARY KEY (id_klienta);

-- FOREIGN KEY
ALTER TABLE zamowienia ADD CONSTRAINT fk_klient 
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta) 
    ON DELETE CASCADE ON UPDATE CASCADE;

-- UNIQUE
ALTER TABLE klienci ADD CONSTRAINT uk_email UNIQUE (email);

-- CHECK
ALTER TABLE produkty ADD CONSTRAINT chk_cena 
    CHECK (cena > 0);

-- DEFAULT (w różny sposób w różnych SZBD)
ALTER TABLE klienci ALTER COLUMN data_rejestracji SET DEFAULT CURRENT_DATE;
```

#### Usuwanie ograniczeń:
```sql
-- Usunięcie po nazwie
ALTER TABLE klienci DROP CONSTRAINT uk_email;
ALTER TABLE zamowienia DROP CONSTRAINT fk_klient;

-- Usunięcie typu ograniczenia  
ALTER TABLE klienci DROP PRIMARY KEY;  -- MySQL
ALTER TABLE klienci DROP CONSTRAINT klienci_pkey;  -- PostgreSQL

-- Sprawdzenie przed usunięciem
ALTER TABLE klienci DROP CONSTRAINT IF EXISTS uk_email;
```

### 3. **ALTER INDEX**

```sql
-- PostgreSQL
ALTER INDEX idx_nazwisko RENAME TO idx_last_name;

-- Rebuild indeksu (SQL Server)
ALTER INDEX idx_nazwisko ON klienci REBUILD;

-- Reorganizacja indeksu (SQL Server)  
ALTER INDEX idx_nazwisko ON klienci REORGANIZE;

-- Wyłączenie indeksu (SQL Server)
ALTER INDEX idx_nazwisko ON klienci DISABLE;
```

### 4. **ALTER VIEW**

```sql
-- PostgreSQL - zastąpienie definicji
CREATE OR REPLACE VIEW aktywni_klienci AS
SELECT id_klienta, imie, nazwisko, email, telefon
FROM klienci
WHERE aktywny = TRUE;

-- SQL Server
ALTER VIEW aktywni_klienci AS
SELECT id_klienta, imie, nazwisko, email, telefon
FROM klienci
WHERE aktywny = TRUE;
```

## DROP - Usuwanie obiektów

### 1. **DROP DATABASE/SCHEMA**

```sql
-- PostgreSQL
DROP DATABASE IF EXISTS stara_baza;
DROP SCHEMA IF EXISTS stary_schemat CASCADE;

-- MySQL
DROP DATABASE IF EXISTS stara_baza;
DROP SCHEMA IF EXISTS stary_schemat;

-- SQL Server
DROP DATABASE stara_baza;
```

### 2. **DROP TABLE**

```sql
-- Podstawowe usuwanie
DROP TABLE klienci;

-- Z zabezpieczeniem
DROP TABLE IF EXISTS klienci;

-- CASCADE - usuwa też obiekty zależne
DROP TABLE klienci CASCADE;

-- RESTRICT - nie usuwa jeśli są zależności (domyślne)
DROP TABLE klienci RESTRICT;

-- Usunięcie wielu tabel
DROP TABLE tabela1, tabela2, tabela3;
```

### 3. **DROP INDEX**

```sql
-- PostgreSQL
DROP INDEX idx_nazwisko;
DROP INDEX IF EXISTS idx_nazwisko;
DROP INDEX CONCURRENTLY idx_duzy_indeks;  -- Bez blokowania

-- MySQL
DROP INDEX idx_nazwisko ON klienci;

-- SQL Server
DROP INDEX idx_nazwisko ON klienci;
```

### 4. **DROP VIEW**

```sql
-- Usunięcie widoku
DROP VIEW aktywni_klienci;
DROP VIEW IF EXISTS aktywni_klienci;

-- Cascade dla widoków zależnych
DROP VIEW widok_nadrzedny CASCADE;

-- Materialized view (PostgreSQL)
DROP MATERIALIZED VIEW mv_statystyki;
```

## TRUNCATE - Szybkie czyszczenie

### Różnice TRUNCATE vs DELETE:

```sql
-- TRUNCATE - szybkie, resetuje AUTO_INCREMENT, nie loguje wierszy
TRUNCATE TABLE logi;
TRUNCATE TABLE zamowienia RESTART IDENTITY;  -- PostgreSQL
TRUNCATE TABLE zamowienia RESTART IDENTITY CASCADE;  -- Z kluczami obcymi

-- DELETE - wolniejsze, nie resetuje AUTO_INCREMENT, pełne logowanie
DELETE FROM logi;

-- Porównanie wydajności:
-- TRUNCATE: O(1) - niezależne od rozmiaru tabeli
-- DELETE: O(n) - zależne od liczby wierszy
```

### Ograniczenia TRUNCATE:
```sql
-- Nie można użyć TRUNCATE gdy:
-- 1. Tabela ma klucze obce wskazujące na nią
-- 2. Tabela uczestniczy w replikacji (niektóre SZBD)
-- 3. Tabela ma triggery (niektóre SZBD)

-- Rozwiązanie - tymczasowe wyłączenie ograniczeń:
SET FOREIGN_KEY_CHECKS = 0;  -- MySQL
TRUNCATE TABLE parent_table;
SET FOREIGN_KEY_CHECKS = 1;
```

## Zaawansowane operacje DDL

### 1. **Partycjonowanie tabel**

#### PostgreSQL - partycjonowanie zakresowe:
```sql
-- Tabela główna
CREATE TABLE sprzedaz (
    id SERIAL,
    data_sprzedazy DATE NOT NULL,
    kwota NUMERIC(10,2),
    klient_id INTEGER
) PARTITION BY RANGE (data_sprzedazy);

-- Partycje
CREATE TABLE sprzedaz_2023_q1 PARTITION OF sprzedaz
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');

CREATE TABLE sprzedaz_2023_q2 PARTITION OF sprzedaz
    FOR VALUES FROM ('2023-04-01') TO ('2023-07-01');

-- Partycja domyślna
CREATE TABLE sprzedaz_default PARTITION OF sprzedaz DEFAULT;
```

#### MySQL - partycjonowanie:
```sql
CREATE TABLE sprzedaz (
    id INT AUTO_INCREMENT,
    data_sprzedazy DATE NOT NULL,
    kwota DECIMAL(10,2),
    klient_id INT,
    PRIMARY KEY (id, data_sprzedazy)
) 
PARTITION BY RANGE (YEAR(data_sprzedazy)) (
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

### 2. **Tablespaces**

#### PostgreSQL:
```sql
-- Tworzenie tablespace
CREATE TABLESPACE fast_storage LOCATION '/mnt/ssd/postgres_data';

-- Użycie tablespace
CREATE TABLE duza_tabela (
    id SERIAL PRIMARY KEY,
    dane TEXT
) TABLESPACE fast_storage;

-- Przeniesienie tabeli
ALTER TABLE duza_tabela SET TABLESPACE fast_storage;
```

### 3. **Sekwencje**

#### PostgreSQL:
```sql
-- Tworzenie sekwencji
CREATE SEQUENCE seq_klient_id
    START WITH 1000
    INCREMENT BY 1
    MINVALUE 1000
    MAXVALUE 9999999
    CACHE 10;

-- Użycie w tabeli
CREATE TABLE klienci (
    id INTEGER DEFAULT nextval('seq_klient_id') PRIMARY KEY,
    imie VARCHAR(50)
);

-- Zarządzanie sekwencją
SELECT setval('seq_klient_id', 5000);  -- Ustaw wartość
SELECT currval('seq_klient_id');       -- Aktualna wartość
SELECT nextval('seq_klient_id');       -- Następna wartość

-- Modyfikacja sekwencji
ALTER SEQUENCE seq_klient_id RESTART WITH 1000;
ALTER SEQUENCE seq_klient_id INCREMENT BY 2;
```

### 4. **Typy użytkownika**

#### PostgreSQL:
```sql
-- Typ wyliczeniowy
CREATE TYPE status_zamowienia AS ENUM (
    'nowe', 'w_realizacji', 'wysłane', 'dostarczone', 'anulowane'
);

-- Typ złożony
CREATE TYPE adres AS (
    ulica VARCHAR(100),
    numer VARCHAR(10),
    kod_pocztowy VARCHAR(6),
    miasto VARCHAR(50)
);

-- Użycie
CREATE TABLE klienci (
    id SERIAL PRIMARY KEY,
    imie VARCHAR(50),
    adres_klienta adres,
    status status_zamowienia DEFAULT 'nowe'
);
```

## Najlepsze praktyki DDL

### ✅ **Dobre praktyki:**

#### 1. **Nazewnictwo**
```sql
-- Konsekwentne nazwy
CREATE TABLE klienci (          -- liczba mnoga dla tabel
    id_klienta SERIAL,          -- id_ prefix dla kluczy
    data_utworzenia DATE,       -- snake_case
    
    CONSTRAINT pk_klienci PRIMARY KEY (id_klienta),         -- pk_ prefix
    CONSTRAINT uk_klienci_email UNIQUE (email),             -- uk_ prefix  
    CONSTRAINT fk_klienci_kategoria FOREIGN KEY (...)       -- fk_ prefix
);

-- Indeksy z opisowymi nazwami
CREATE INDEX idx_klienci_nazwisko_imie ON klienci(nazwisko, imie);
CREATE INDEX idx_zamowienia_data_status ON zamowienia(data_zamowienia, status);
```

#### 2. **Bezpieczeństwo**
```sql
-- Zawsze używaj IF EXISTS/IF NOT EXISTS
CREATE TABLE IF NOT EXISTS nowa_tabela (...);
DROP INDEX IF EXISTS stary_indeks;

-- Sprawdzaj zależności przed DROP
-- Używaj RESTRICT zamiast CASCADE gdy to możliwe
DROP TABLE klienci RESTRICT;
```

#### 3. **Wydajność**
```sql
-- Odpowiednie typy danych
CREATE TABLE produkty (
    id SERIAL PRIMARY KEY,
    kod VARCHAR(20) NOT NULL,           -- Nie TEXT dla krótkich kodów
    cena NUMERIC(10,2) NOT NULL,        -- Nie FLOAT dla pieniędzy
    opis TEXT,                          -- TEXT dla długich opisów
    aktywny BOOLEAN DEFAULT TRUE        -- BOOLEAN, nie VARCHAR(1)
);

-- Indeksy na klucze obce
CREATE INDEX idx_zamowienia_klient ON zamowienia(id_klienta);
CREATE INDEX idx_pozycje_produkt ON pozycje_zamowien(id_produktu);
```

#### 4. **Dokumentacja**
```sql
-- Komentarze dla tabel i kolumn
CREATE TABLE klienci (
    id_klienta SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL
);

COMMENT ON TABLE klienci IS 'Tabela przechowująca dane klientów sklepu';
COMMENT ON COLUMN klienci.email IS 'Adres email klienta - używany do logowania';
```

### ❌ **Złe praktyki:**

#### 1. **Nieprawidłowe typy danych**
```sql
-- ❌ ŹLE
CREATE TABLE produkty (
    id VARCHAR(50),              -- Text dla numerycznego ID
    cena VARCHAR(20),           -- Text dla kwot pieniężnych
    data_dodania VARCHAR(30),   -- Text dla dat
    aktywny VARCHAR(10)         -- Text dla boolean
);

-- ✅ DOBRZE  
CREATE TABLE produkty (
    id SERIAL PRIMARY KEY,
    cena NUMERIC(10,2) NOT NULL,
    data_dodania DATE DEFAULT CURRENT_DATE,
    aktywny BOOLEAN DEFAULT TRUE
);
```

#### 2. **Brak ograniczeń**
```sql
-- ❌ ŹLE - brak walidacji
CREATE TABLE klienci (
    id INTEGER,
    email VARCHAR(100),
    wiek INTEGER
);

-- ✅ DOBRZE - z walidacją
CREATE TABLE klienci (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL CHECK (email LIKE '%@%'),
    wiek INTEGER CHECK (wiek >= 0 AND wiek <= 150)
);
```

#### 3. **Nadmierne użycie CASCADE**
```sql
-- ❌ NIEBEZPIECZNE
DROP TABLE klienci CASCADE;  -- Może usunąć więcej niż oczekiwane

-- ✅ BEZPIECZNIEJ
-- Sprawdź zależności przed usunięciem
SELECT * FROM information_schema.referential_constraints 
WHERE referenced_table_name = 'klienci';

DROP TABLE klienci RESTRICT;  -- Fail jeśli są zależności
```

## Monitoring i maintenance DDL

### 1. **Informacje o strukturze**
```sql
-- PostgreSQL
SELECT table_name, column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public';

-- Informacje o indeksach
SELECT indexname, tablename, indexdef 
FROM pg_indexes 
WHERE schemaname = 'public';

-- MySQL
DESCRIBE tabela;
SHOW CREATE TABLE tabela;
SHOW INDEXES FROM tabela;

-- SQL Server
SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'tabela';
```

### 2. **Monitoring rozmiaru**
```sql
-- PostgreSQL - rozmiary tabel
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- MySQL - rozmiary tabel
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.tables 
WHERE table_schema = 'database_name'
ORDER BY size_mb DESC;
```

## Pułapki egzaminacyjne

### 1. **Różnice między SZBD**
```
AUTO_INCREMENT: MySQL
SERIAL: PostgreSQL  
IDENTITY: SQL Server

IF NOT EXISTS: PostgreSQL, MySQL
Nie ma w: SQL Server (sprawdź sys.tables)
```

### 2. **Kolejność operacji**
```
1. Zawsze najpierw DROP dependent objects
2. Potem DROP main objects
3. CREATE w odwrotnej kolejności

DROP INDEX → DROP TABLE → DROP SCHEMA → DROP DATABASE
```

### 3. **Transakcyjność DDL**
```
PostgreSQL: DDL w transakcjach (można ROLLBACK)
MySQL: Autocommit DDL (nie można ROLLBACK)
SQL Server: DDL w transakcjach (można ROLLBACK)
```

### 4. **CASCADE vs RESTRICT**
```
CASCADE: Usuwa obiekty zależne (niebezpieczne)
RESTRICT: Fail jeśli są zależności (bezpieczne)
Domyślnie: RESTRICT (w większości SZBD)
```