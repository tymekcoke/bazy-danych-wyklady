# 🔄 PRZENOSZENIE DIAGRAMU ER NA SQL - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekunds)

"Przenoszenie diagramu ER na SQL to systematyczny proces przekształcania konceptualnego modelu danych na fizyczną strukturę bazy. Główne kroki:

1. **Encje** → tabele z primary key
2. **Atrybuty** → kolumny z odpowiednimi typami danych
3. **Związki 1:1** → foreign key z UNIQUE lub łączenie tabel
4. **Związki 1:N** → foreign key po stronie 'N'
5. **Związki M:N** → tabela łącząca z composite key
6. **Atrybuty związków** → kolumny w tabeli łączącej
7. **Generalizacja/specjalizacja** → dziedziczenie tabel lub łączenie"

## ✍️ CO NAPISAĆ NA KARTCE

```
ZASADY PRZEKSZTAŁCANIA ER → SQL:

1. ENCJE → TABELE
   - Każda encja = osobna tabela
   - Nazwa encji = nazwa tabeli  
   - Dodaj PRIMARY KEY (jeśli nie ma natural key)

2. ATRYBUTY → KOLUMNY
   - Proste atrybuty → kolumny
   - Atrybuty wielowartościowe → osobna tabela
   - Atrybuty złożone → dekompozycja na kolumny
   - Atrybuty pochodne → kolumny obliczeniowe lub widoki

3. ZWIĄZKI 1:1 → FOREIGN KEY + UNIQUE
   Student ——————— Legitymacja
   
   CREATE TABLE studenci (id INT PRIMARY KEY, ...);
   CREATE TABLE legitymacje (
       id INT PRIMARY KEY,
       id_studenta INT UNIQUE,  -- UNIQUE dla 1:1!
       FOREIGN KEY (id_studenta) REFERENCES studenci(id)
   );

4. ZWIĄZKI 1:N → FOREIGN KEY  
   Klient ——————< Zamówienie
   
   CREATE TABLE klienci (id INT PRIMARY KEY, ...);
   CREATE TABLE zamowienia (
       id INT PRIMARY KEY,
       id_klienta INT,  -- foreign key po stronie "N"
       FOREIGN KEY (id_klienta) REFERENCES klienci(id)
   );

5. ZWIĄZKI M:N → TABELA ŁĄCZĄCA
   Student >——————< Przedmiot
   
   CREATE TABLE studenci (id INT PRIMARY KEY, ...);
   CREATE TABLE przedmioty (id INT PRIMARY KEY, ...);
   CREATE TABLE student_przedmiot (
       id_studenta INT,
       id_przedmiotu INT,
       ocena INT,  -- atrybut związku
       PRIMARY KEY (id_studenta, id_przedmiotu),
       FOREIGN KEY (id_studenta) REFERENCES studenci(id),
       FOREIGN KEY (id_przedmiotu) REFERENCES przedmioty(id)
   );

6. SŁABE ENCJE → FOREIGN KEY + COMPOSITE KEY
   Zamówienie ——————< Pozycja_zamówienia (weak entity)
   
   CREATE TABLE pozycje_zamowienia (
       id_zamowienia INT,
       nr_pozycji INT,
       produkt VARCHAR(100),
       PRIMARY KEY (id_zamowienia, nr_pozycji),  -- composite
       FOREIGN KEY (id_zamowienia) REFERENCES zamowienia(id)
   );
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- KOMPLEKSNY PRZYKŁAD: SYSTEM BIBLIOTEKI

-- DIAGRAM ER (konceptualny):
-- CZYTELNIK ——————< WYPOŻYCZENIE >——————— KSIĄŻKA
-- KSIĄŻKA ——————< EGZEMPLARZ
-- AUTOR >——————< KSIĄŻKA (M:N)
-- KSIĄŻKA ——————— WYDAWNICTWO (N:1)

-- 1. ENCJE GŁÓWNE → TABELE

-- Encja CZYTELNIK
CREATE TABLE czytelnicy (
    id_czytelnika SERIAL PRIMARY KEY,
    nr_karty VARCHAR(20) UNIQUE NOT NULL,  -- natural key
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    data_urodzenia DATE,
    aktywny BOOLEAN DEFAULT TRUE
);

-- Encja WYDAWNICTWO  
CREATE TABLE wydawnictwa (
    id_wydawnictwa SERIAL PRIMARY KEY,
    nazwa VARCHAR(100) NOT NULL,
    adres TEXT,
    telefon VARCHAR(20)
);

-- Encja AUTOR
CREATE TABLE autorzy (
    id_autora SERIAL PRIMARY KEY,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    narodowosc VARCHAR(50),
    data_urodzenia DATE,
    data_smierci DATE
);

-- Encja KSIĄŻKA (z związkiem N:1 do WYDAWNICTWO)
CREATE TABLE ksiazki (
    id_ksiazki SERIAL PRIMARY KEY,
    isbn VARCHAR(13) UNIQUE,
    tytul VARCHAR(200) NOT NULL,
    rok_wydania INT,
    liczba_stron INT,
    id_wydawnictwa INT,  -- Foreign key do wydawnictwa
    
    FOREIGN KEY (id_wydawnictwa) REFERENCES wydawnictwa(id_wydawnictwa)
        ON DELETE SET NULL  -- można usunąć wydawnictwo
        ON UPDATE CASCADE
);

-- 2. ZWIĄZEK M:N → TABELA ŁĄCZĄCA

-- AUTOR >——————< KSIĄŻKA (M:N z atrybutem)
CREATE TABLE autor_ksiazka (
    id_autora INT,
    id_ksiazki INT,
    rola VARCHAR(50) DEFAULT 'autor',  -- atrybut związku (autor/współautor/tłumacz)
    
    PRIMARY KEY (id_autora, id_ksiazki),
    FOREIGN KEY (id_autora) REFERENCES autorzy(id_autora)
        ON DELETE CASCADE,  -- usuń związek gdy autor usunięty
    FOREIGN KEY (id_ksiazki) REFERENCES ksiazki(id_ksiazki)
        ON DELETE CASCADE   -- usuń związek gdy książka usunięta
);

-- 3. SŁABA ENCJA → COMPOSITE KEY

-- EGZEMPLARZ (słaba encja zależna od KSIĄŻKA)
CREATE TABLE egzemplarze (
    id_ksiazki INT,
    nr_egzemplarza INT,
    stan VARCHAR(20) DEFAULT 'dobry',  -- dobry/zniszczony/utracony
    data_nabycia DATE DEFAULT CURRENT_DATE,
    cena_nabycia DECIMAL(8,2),
    
    -- Composite primary key (książka + numer egzemplarza)
    PRIMARY KEY (id_ksiazki, nr_egzemplarza),
    FOREIGN KEY (id_ksiazki) REFERENCES ksiazki(id_ksiazki)
        ON DELETE CASCADE  -- usuń egzemplarze gdy książka usunięta
);

-- 4. ZWIĄZEK TRÓJSTRONNY → TABELA ŁĄCZĄCA

-- WYPOŻYCZENIE (CZYTELNIK + EGZEMPLARZ + BIBLIOTEKARZ)
CREATE TABLE wypozyczenia (
    id_wypozyczenia SERIAL PRIMARY KEY,  -- surrogate key dla wygody
    id_czytelnika INT NOT NULL,
    id_ksiazki INT NOT NULL,
    nr_egzemplarza INT NOT NULL,
    id_bibliotekarza INT,
    data_wypozyczenia DATE DEFAULT CURRENT_DATE,
    data_zwrotu_planowana DATE NOT NULL,
    data_zwrotu_faktyczna DATE,
    kara DECIMAL(6,2) DEFAULT 0,
    
    -- Foreign keys
    FOREIGN KEY (id_czytelnika) REFERENCES czytelnicy(id_czytelnika),
    FOREIGN KEY (id_ksiazki, nr_egzemplarza) 
        REFERENCES egzemplarze(id_ksiazki, nr_egzemplarza),
    FOREIGN KEY (id_bibliotekarza) REFERENCES pracownicy(id_pracownika),
    
    -- Constraint: nie można wypożyczyć tego samego egzemplarza dwa razy
    UNIQUE (id_ksiazki, nr_egzemplarza, data_zwrotu_faktyczna) 
        DEFERRABLE INITIALLY DEFERRED
);

-- 5. ATRYBUTY SPECJALNE

-- Atrybuty wielowartościowe → osobna tabela
CREATE TABLE kategorie_ksiazek (
    id_ksiazki INT,
    kategoria VARCHAR(50),
    
    PRIMARY KEY (id_ksiazki, kategoria),
    FOREIGN KEY (id_ksiazki) REFERENCES ksiazki(id_ksiazki)
        ON DELETE CASCADE
);

-- Atrybuty złożone → dekompozycja
-- Adres jako atrybut złożony → osobne kolumny
ALTER TABLE czytelnicy ADD COLUMN 
    adres_ulica VARCHAR(100),
    adres_nr_domu VARCHAR(10),
    adres_kod_pocztowy VARCHAR(6),
    adres_miasto VARCHAR(50);

-- Atrybuty pochodne → computed columns lub views
CREATE VIEW statystyki_czytelnikow AS
SELECT 
    c.id_czytelnika,
    c.imie,
    c.nazwisko,
    COUNT(w.id_wypozyczenia) as liczba_wypozyczen,
    COALESCE(SUM(w.kara), 0) as suma_kar,
    MAX(w.data_wypozyczenia) as ostatnie_wypozyczenie,
    -- Wiek jako atrybut pochodny
    EXTRACT(YEAR FROM AGE(c.data_urodzenia)) as wiek
FROM czytelnicy c
LEFT JOIN wypozyczenia w ON c.id_czytelnika = w.id_czytelnika
GROUP BY c.id_czytelnika, c.imie, c.nazwisko, c.data_urodzenia;

-- 6. GENERALIZACJA/SPECJALIZACJA

-- Opcja A: Table per hierarchy (jedna tabela)
CREATE TABLE pracownicy (
    id_pracownika SERIAL PRIMARY KEY,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    typ_pracownika VARCHAR(20) NOT NULL,  -- 'bibliotekarz', 'admin', 'kierownik'
    
    -- Atrybuty specyficzne dla bibliotekarza
    specjalizacja VARCHAR(50),  -- NULL dla innych typów
    
    -- Atrybuty specyficzne dla kierownika  
    budzet_dzialu DECIMAL(10,2),  -- NULL dla innych typów
    
    CHECK (typ_pracownika IN ('bibliotekarz', 'admin', 'kierownik'))
);

-- Opcja B: Table per subclass (osobne tabele)
CREATE TABLE pracownicy_base (
    id_pracownika SERIAL PRIMARY KEY,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL
);

CREATE TABLE bibliotekarze (
    id_pracownika INT PRIMARY KEY,
    specjalizacja VARCHAR(50),
    FOREIGN KEY (id_pracownika) REFERENCES pracownicy_base(id_pracownika)
);

CREATE TABLE kierownicy (
    id_pracownika INT PRIMARY KEY,  
    budzet_dzialu DECIMAL(10,2),
    FOREIGN KEY (id_pracownika) REFERENCES pracownicy_base(id_pracownika)
);

-- 7. DODATKOWE CONSTRAINTS Z DIAGRAMU ER

-- Business rules jako constraints
ALTER TABLE wypozyczenia ADD CONSTRAINT chk_daty_wypozyczenia
    CHECK (data_zwrotu_planowana > data_wypozyczenia);

ALTER TABLE wypozyczenia ADD CONSTRAINT chk_zwrot_faktyczny  
    CHECK (data_zwrotu_faktyczna IS NULL OR data_zwrotu_faktyczna >= data_wypozyczenia);

-- Maksymalne wypożyczenia na czytelnika
CREATE OR REPLACE FUNCTION sprawdz_limit_wypozyczen()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT COUNT(*) FROM wypozyczenia 
        WHERE id_czytelnika = NEW.id_czytelnika 
        AND data_zwrotu_faktyczna IS NULL) >= 5 THEN
        RAISE EXCEPTION 'Czytelnik może wypożyczyć maksymalnie 5 książek';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_limit_wypozyczen
    BEFORE INSERT ON wypozyczenia
    FOR EACH ROW  
    EXECUTE FUNCTION sprawdz_limit_wypozyczen();
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Związki 1:1 wymagają UNIQUE na foreign key
2. **UWAGA**: Związki M:N zawsze wymagają tabeli łączącej
3. **BŁĄD**: Zapominanie o composite key w słabych encjach
4. **WAŻNE**: Atrybuty związków idą do tabeli łączącej
5. **PUŁAPKA**: Generalizacja może być implementowana na różne sposoby

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Entity mapping** - mapowanie encji
- **Relationship mapping** - mapowanie związków
- **Weak entity** - słaba encja
- **Composite key** - klucz złożony
- **Junction table** - tabela łącząca
- **Foreign key** - klucz obcy  
- **Generalization/Specialization** - generalizacja/specjalizacja
- **Derived attributes** - atrybuty pochodne
- **Multivalued attributes** - atrybuty wielowartościowe

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **25-model-er** - tworzenie diagramów ER
- **12-klucze-bazy-danych** - implementacja kluczy
- **01-integralnosc** - constraints i integralność
- **02-relacje-1-1** - implementacja związków 1:1
- **29-sql-ddl** - składnia CREATE TABLE