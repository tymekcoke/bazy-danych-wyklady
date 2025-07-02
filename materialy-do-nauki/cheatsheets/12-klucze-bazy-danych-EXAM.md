# 🗝️ KLUCZE BAZY DANYCH - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Klucze to atrybuty lub zestawy atrybutów służące do identyfikacji i łączenia rekordów:

1. **Klucz główny (Primary Key)** - unikalnie identyfikuje każdy rekord, nie może być NULL
2. **Klucz kandydujący (Candidate Key)** - potencjalny klucz główny, każdy jest unikalny i not null
3. **Klucz obcy (Foreign Key)** - odwołuje się do klucza głównego innej tabeli, może być NULL
4. **Klucz złożony (Composite Key)** - składa się z wielu atrybutów

Wartość NULL w kluczu obcym oznacza brak powiązania, ale w kluczu głównym NULL jest zabroniony."

## ✍️ CO NAPISAĆ NA KARTCE

```sql
-- RODZAJE KLUCZY I ICH WŁAŚCIWOŚCI

-- 1. KLUCZ GŁÓWNY (PRIMARY KEY)
CREATE TABLE studenci (
    id_studenta INT PRIMARY KEY,  -- automatycznie NOT NULL + UNIQUE
    nr_indeksu VARCHAR(10) UNIQUE NOT NULL,  -- candidate key
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE     -- candidate key (może być NULL)
);

-- 2. KLUCZ ZŁOŻONY (COMPOSITE PRIMARY KEY)  
CREATE TABLE oceny (
    id_studenta INT,
    kod_przedmiotu VARCHAR(10),
    ocena INT,
    data_wystawienia DATE,
    PRIMARY KEY (id_studenta, kod_przedmiotu),  -- klucz złożony
    FOREIGN KEY (id_studenta) REFERENCES studenci(id_studenta)
);

-- 3. KLUCZ OBCY (FOREIGN KEY) Z RÓŻNYMI OPCJAMI
CREATE TABLE zamowienia (
    id_zamowienia INT PRIMARY KEY,
    id_klienta INT,  -- może być NULL (zamówienie anonimowe)
    kwota DECIMAL(10,2),
    
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta)
        ON DELETE SET NULL      -- NULL gdy klient usunięty
        ON UPDATE CASCADE       -- aktualizuj gdy ID klienta się zmieni
);

-- WŁAŚCIWOŚCI NULL W KLUCZACH:

PRIMARY KEY:
- NIGDY NULL ✗
- Zawsze UNIQUE ✓
- Tylko jeden na tabelę ✓

CANDIDATE KEY:  
- Może być NULL ✓ (ale nie powinien dla kandydata)
- Zawsze UNIQUE ✓
- Może być wiele na tabelę ✓

FOREIGN KEY:
- Może być NULL ✓ (brak powiązania)
- Nie musi być UNIQUE ✗
- Może być wiele na tabelę ✓

UNIQUE KEY:
- Może być NULL ✓ (ale tylko raz w PostgreSQL)
- Zawsze UNIQUE ✓
- Może być wiele na tabelę ✓
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- KOMPLEKSNY PRZYKŁAD SYSTEMU KLUCZY

-- Tabela klientów z candidate keys
CREATE TABLE klienci (
    id_klienta SERIAL PRIMARY KEY,           -- klucz główny (surrogate)
    pesel VARCHAR(11) UNIQUE NOT NULL,       -- candidate key (natural)  
    email VARCHAR(100) UNIQUE NOT NULL,      -- candidate key
    nip VARCHAR(13) UNIQUE,                  -- candidate key (może NULL dla osób fizycznych)
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    telefon VARCHAR(15) UNIQUE               -- candidate key (może NULL)
);

-- Tabela produktów
CREATE TABLE produkty (
    id_produktu SERIAL PRIMARY KEY,
    kod_produktu VARCHAR(20) UNIQUE NOT NULL,  -- natural key
    nazwa VARCHAR(100) NOT NULL,
    cena DECIMAL(10,2) NOT NULL CHECK (cena > 0)
);

-- Tabela zamówień z foreign keys
CREATE TABLE zamowienia (
    id_zamowienia SERIAL PRIMARY KEY,
    numer_zamowienia VARCHAR(20) UNIQUE NOT NULL,  -- candidate key dla użytkowników
    id_klienta INT,                                 -- foreign key (może NULL)
    data_zamowienia DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'nowe',
    
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta)
        ON DELETE SET NULL      -- klient usunięty → zamówienie zostaje ale bez powiązania
        ON UPDATE CASCADE       -- ID klienta zmienione → aktualizuj w zamówieniu
);

-- Tabela pozycji z composite key i multiple foreign keys
CREATE TABLE pozycje_zamowienia (
    id_zamowienia INT,
    id_produktu INT,
    ilosc INT NOT NULL CHECK (ilosc > 0),
    cena_jednostkowa DECIMAL(10,2) NOT NULL,
    
    -- Composite primary key
    PRIMARY KEY (id_zamowienia, id_produktu),
    
    -- Multiple foreign keys
    FOREIGN KEY (id_zamowienia) REFERENCES zamowienia(id_zamowienia)
        ON DELETE CASCADE,      -- zamówienie usunięte → usuń pozycje
    FOREIGN KEY (id_produktu) REFERENCES produkty(id_produktu)
        ON DELETE RESTRICT      -- nie można usunąć produktu jeśli jest w zamówieniu
);

-- PRZYKŁADY OBSŁUGI NULL W FOREIGN KEY

-- Wstawienie zamówienia bez klienta (anonimowe)
INSERT INTO zamowienia (numer_zamowienia, id_klienta) 
VALUES ('ZAM-2024-001', NULL);  -- NULL = brak powiązania z klientem

-- Wstawienie zamówienia z klientem  
INSERT INTO zamowienia (numer_zamowienia, id_klienta)
VALUES ('ZAM-2024-002', 1);     -- powiązane z klientem ID=1

-- Sprawdzenie powiązań (uwaga na NULL!)
SELECT z.numer_zamowienia, 
       COALESCE(k.imie || ' ' || k.nazwisko, 'ANONIMOWY') as klient
FROM zamowienia z
LEFT JOIN klienci k ON z.id_klienta = k.id_klienta;

-- PRZYKŁAD PROBLEMÓW Z NULL W UNIQUE

-- PostgreSQL: NULL nie łamie UNIQUE (może być wiele NULL)
CREATE TABLE test_unique (
    id SERIAL PRIMARY KEY,
    wartosc VARCHAR(50) UNIQUE  -- może być wiele NULL
);

INSERT INTO test_unique (wartosc) VALUES (NULL);  -- OK
INSERT INTO test_unique (wartosc) VALUES (NULL);  -- OK - drugie NULL
INSERT INTO test_unique (wartosc) VALUES ('ABC'); -- OK
INSERT INTO test_unique (wartosc) VALUES ('ABC'); -- BŁĄD - duplikat

-- PARTIAL UNIQUE INDEX (unique tylko dla nie-NULL)
CREATE UNIQUE INDEX idx_partial_unique 
ON test_unique (wartosc) 
WHERE wartosc IS NOT NULL;

-- SPRAWDZANIE INTEGRALNOŚCI KLUCZY

-- 1. Orphaned records (rekordy bez rodzica)
SELECT z.id_zamowienia, z.numer_zamowienia
FROM zamowienia z
LEFT JOIN klienci k ON z.id_klienta = k.id_klienta  
WHERE z.id_klienta IS NOT NULL AND k.id_klienta IS NULL;

-- 2. Duplicate candidate keys
SELECT pesel, COUNT(*)
FROM klienci
GROUP BY pesel
HAVING COUNT(*) > 1;

-- 3. Foreign key violations przed dodaniem constraint
SELECT DISTINCT pz.id_produktu
FROM pozycje_zamowienia pz
LEFT JOIN produkty p ON pz.id_produktu = p.id_produktu
WHERE p.id_produktu IS NULL;

-- AUTOMATYCZNE GENEROWANIE KLUCZY

-- SERIAL (PostgreSQL sposób)
CREATE TABLE tabela1 (
    id SERIAL PRIMARY KEY,  -- automatyczny increment
    nazwa VARCHAR(100)
);

-- IDENTITY (SQL Standard)  
CREATE TABLE tabela2 (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nazwa VARCHAR(100)
);

-- UUID jako klucz (dla systemów rozproszonych)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE TABLE tabela3 (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nazwa VARCHAR(100)
);

-- NATURAL vs SURROGATE KEYS

-- Natural key (znaczący biznesowo)
CREATE TABLE kraje (
    kod_iso VARCHAR(2) PRIMARY KEY,  -- PL, US, DE - natural key
    nazwa VARCHAR(100) NOT NULL
);

-- Surrogate key (sztuczny, bez znaczenia biznesowego)  
CREATE TABLE osoby (
    id SERIAL PRIMARY KEY,           -- surrogate key
    pesel VARCHAR(11) UNIQUE NOT NULL,  -- natural key jako candidate
    imie VARCHAR(50),
    nazwisko VARCHAR(50)
);
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Primary key = NOT NULL + UNIQUE automatycznie
2. **UWAGA**: Foreign key może być NULL (oznacza brak powiązania)
3. **BŁĄD**: Mylenie candidate key z alternate key (to synonimy)
4. **WAŻNE**: W PostgreSQL UNIQUE pozwala na wiele wartości NULL
5. **PUŁAPKA**: Composite key = wszystkie kolumny razem muszą być unikalne

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Primary key** - klucz główny
- **Foreign key** - klucz obcy  
- **Candidate key** - klucz kandydujący
- **Composite key** - klucz złożony
- **Natural vs Surrogate key** - klucz naturalny vs sztuczny
- **Referential integrity** - integralność referencyjna
- **ON DELETE CASCADE/RESTRICT** - akcje przy usuwaniu
- **Orphaned records** - rekordy osierocone

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **01-integralnosc** - integralność encji i referencyjna
- **02-relacje-1-1** - klucze obce w relacjach 1:1
- **14-er-do-sql** - implementacja kluczy z diagramu ER
- **19-normalizacja** - klucze w normalizacji
- **25-model-er** - identyfikacja kluczy w modelu ER