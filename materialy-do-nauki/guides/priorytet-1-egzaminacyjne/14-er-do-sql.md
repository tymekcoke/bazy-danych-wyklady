# Przenoszenie diagramu ER na SQL

## Proces mapowania ER → SQL

### Ogólny algorytm:
1. **Mapuj encje** → tabele
2. **Mapuj atrybuty** → kolumny  
3. **Mapuj związki** → klucze obce lub tabele łączące
4. **Dodaj ograniczenia** → PRIMARY KEY, FOREIGN KEY, CHECK
5. **Obsłuż specjalne przypadki** → dziedziczenie, encje słabe

## Mapowanie encji

### 1. **Encje regularne (silne)**
```
Diagram ER:
┌─────────────┐
│   STUDENT   │
├─────────────┤
│ id_studenta │ ← klucz główny
│ imie        │
│ nazwisko    │
│ data_ur     │
└─────────────┘
```

```sql
-- Mapowanie na SQL
CREATE TABLE studenci (
    id_studenta INT PRIMARY KEY,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    data_urodzenia DATE
);
```

### 2. **Encje słabe (weak entities)**
```
Diagram ER:
┌─────────────┐       ┌─────────────┐
│  PRACOWNIK  │──────▶│   DZIECKO   │ ← encja słaba
├─────────────┤       ├─────────────┤
│ id_prac     │       │ imie        │ ← klucz częściowy
│ imie        │       │ data_ur     │
└─────────────┘       └─────────────┘
```

```sql
-- Encja silna
CREATE TABLE pracownicy (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50) NOT NULL
);

-- Encja słaba - klucz złożony
CREATE TABLE dzieci (
    id_pracownika INT,              -- klucz obcy
    imie VARCHAR(50),               -- klucz częściowy
    data_urodzenia DATE,
    
    PRIMARY KEY (id_pracownika, imie),  -- klucz złożony
    FOREIGN KEY (id_pracownika) REFERENCES pracownicy(id_pracownika)
        ON DELETE CASCADE
);
```

## Mapowanie atrybutów

### 1. **Atrybuty proste**
```sql
-- Atrybut prosty → kolumna
imie VARCHAR(50)
wiek INT
pensja DECIMAL(10,2)
```

### 2. **Atrybuty złożone**
```
Diagram ER:
ADRES {ulica, miasto, kod_pocztowy}
```

```sql
-- Opcja 1: Rozłóż na osobne kolumny
CREATE TABLE klienci (
    id INT PRIMARY KEY,
    imie VARCHAR(50),
    adres_ulica VARCHAR(100),
    adres_miasto VARCHAR(50),
    adres_kod_pocztowy VARCHAR(10)
);

-- Opcja 2: Osobna tabela (jeśli kompleksowy)
CREATE TABLE adresy (
    id_adresu INT PRIMARY KEY,
    ulica VARCHAR(100),
    miasto VARCHAR(50),  
    kod_pocztowy VARCHAR(10)
);

CREATE TABLE klienci (
    id INT PRIMARY KEY,
    imie VARCHAR(50),
    id_adresu INT,
    FOREIGN KEY (id_adresu) REFERENCES adresy(id_adresu)
);
```

### 3. **Atrybuty wielowartościowe**
```
Diagram ER:
PRACOWNIK {telefony}  ← atrybut wielowartościowy
```

```sql
-- Osobna tabela dla atrybutu wielowartościowego
CREATE TABLE pracownicy (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50)
);

CREATE TABLE telefony_pracownikow (
    id_pracownika INT,
    numer_telefonu VARCHAR(15),
    
    PRIMARY KEY (id_pracownika, numer_telefonu),
    FOREIGN KEY (id_pracownika) REFERENCES pracownicy(id_pracownika)
        ON DELETE CASCADE
);
```

### 4. **Atrybuty pochodne**
```
Diagram ER:
PRACOWNIK {wiek} ← atrybut pochodny z data_urodzenia
```

```sql
-- Opcja 1: Nie przechowuj, obliczaj dynamicznie
CREATE TABLE pracownicy (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50),
    data_urodzenia DATE
    -- wiek nie przechowywany
);

-- Widok z obliczanym wiekiem
CREATE VIEW pracownicy_z_wiekiem AS
SELECT 
    *,
    EXTRACT(YEAR FROM AGE(data_urodzenia)) as wiek
FROM pracownicy;

-- Opcja 2: Przechowuj i aktualizuj triggerami
CREATE TABLE pracownicy (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50),
    data_urodzenia DATE,
    wiek INT  -- przechowywany
);
```

## Mapowanie związków

### 1. **Związek 1:1 (jeden do jednego)**

#### Opcja A: Klucz obcy w jednej tabeli
```
OSOBA ↔ PASZPORT (1:1)
```

```sql
CREATE TABLE osoby (
    id_osoby INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50)
);

CREATE TABLE paszporty (
    numer_paszportu VARCHAR(20) PRIMARY KEY,
    data_wydania DATE,
    id_osoby INT UNIQUE,  -- UNIQUE zapewnia 1:1
    
    FOREIGN KEY (id_osoby) REFERENCES osoby(id_osoby)
);
```

#### Opcja B: Połącz tabele w jedną
```sql
CREATE TABLE osoby_paszporty (
    id_osoby INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    numer_paszportu VARCHAR(20) UNIQUE,
    data_wydania_paszportu DATE
);
```

### 2. **Związek 1:N (jeden do wielu)**
```
KLIENT ↔ ZAMÓWIENIE (1:N)
```

```sql
CREATE TABLE klienci (
    id_klienta INT PRIMARY KEY,
    nazwa VARCHAR(100)
);

CREATE TABLE zamowienia (
    id_zamowienia INT PRIMARY KEY,
    data_zamowienia DATE,
    id_klienta INT,  -- klucz obcy po stronie "wielu"
    
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta)
);
```

### 3. **Związek M:N (wiele do wielu)**
```
STUDENT ↔ KURS (M:N)
```

```sql
CREATE TABLE studenci (
    id_studenta INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50)
);

CREATE TABLE kursy (
    id_kursu INT PRIMARY KEY,
    nazwa VARCHAR(100),
    ects INT
);

-- Tabela łącząca (junction table)
CREATE TABLE zapiski (
    id_studenta INT,
    id_kursu INT,
    data_zapisu DATE,
    ocena DECIMAL(3,2),
    
    PRIMARY KEY (id_studenta, id_kursu),
    FOREIGN KEY (id_studenta) REFERENCES studenci(id_studenta),
    FOREIGN KEY (id_kursu) REFERENCES kursy(id_kursu)
);
```

### 4. **Związek z atrybutami**
```
PRACOWNIK ─── PROJEKT
         │
    [od_daty, stanowisko]  ← atrybuty związku
```

```sql
CREATE TABLE pracownicy (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50)
);

CREATE TABLE projekty (
    id_projektu INT PRIMARY KEY,
    nazwa VARCHAR(100)
);

-- Tabela dla związku z atrybutami
CREATE TABLE pracownicy_projekty (
    id_pracownika INT,
    id_projektu INT,
    od_daty DATE,           -- atrybut związku
    stanowisko VARCHAR(50), -- atrybut związku
    
    PRIMARY KEY (id_pracownika, id_projektu),
    FOREIGN KEY (id_pracownika) REFERENCES pracownicy(id_pracownika),
    FOREIGN KEY (id_projektu) REFERENCES projekty(id_projektu)
);
```

## Mapowanie związków n-arnych

### Związek trójstronny (ternary)
```
DOSTAWCA ─── DOSTARCZA ─── PRODUKT
              │
           MAGAZYN
```

```sql
CREATE TABLE dostawcy (
    id_dostawcy INT PRIMARY KEY,
    nazwa VARCHAR(100)
);

CREATE TABLE produkty (
    id_produktu INT PRIMARY KEY,
    nazwa VARCHAR(100)
);

CREATE TABLE magazyny (
    id_magazynu INT PRIMARY KEY,
    lokalizacja VARCHAR(100)
);

-- Tabela dla związku 3-stronnego
CREATE TABLE dostawy (
    id_dostawcy INT,
    id_produktu INT,
    id_magazynu INT,
    data_dostawy DATE,
    ilosc INT,
    
    PRIMARY KEY (id_dostawcy, id_produktu, id_magazynu),
    FOREIGN KEY (id_dostawcy) REFERENCES dostawcy(id_dostawcy),
    FOREIGN KEY (id_produktu) REFERENCES produkty(id_produktu),
    FOREIGN KEY (id_magazynu) REFERENCES magazyny(id_magazynu)
);
```

## Mapowanie dziedziczenia

### 1. **Strategia jednej tabeli (Single Table)**
```
POJAZD
├── SAMOCHÓD {nr_rejestracyjny}
└── ROWER {typ_ramy}
```

```sql
CREATE TABLE pojazdy (
    id_pojazdu INT PRIMARY KEY,
    typ_pojazdu VARCHAR(20) NOT NULL,  -- 'SAMOCHOD' lub 'ROWER'
    marka VARCHAR(50),
    model VARCHAR(50),
    
    -- Atrybuty specyficzne dla samochodów
    nr_rejestracyjny VARCHAR(10),
    
    -- Atrybuty specyficzne dla rowerów  
    typ_ramy VARCHAR(20),
    
    CHECK (
        (typ_pojazdu = 'SAMOCHOD' AND nr_rejestracyjny IS NOT NULL) OR
        (typ_pojazdu = 'ROWER' AND typ_ramy IS NOT NULL)
    )
);
```

### 2. **Strategia tabeli na klasę (Table per Class)**
```sql
-- Tabela nadklasy
CREATE TABLE pojazdy (
    id_pojazdu INT PRIMARY KEY,
    marka VARCHAR(50),
    model VARCHAR(50)
);

-- Tabele podklas
CREATE TABLE samochody (
    id_pojazdu INT PRIMARY KEY,
    nr_rejestracyjny VARCHAR(10) NOT NULL,
    
    FOREIGN KEY (id_pojazdu) REFERENCES pojazdy(id_pojazdu)
);

CREATE TABLE rowery (
    id_pojazdu INT PRIMARY KEY,
    typ_ramy VARCHAR(20) NOT NULL,
    
    FOREIGN KEY (id_pojazdu) REFERENCES pojazdy(id_pojazdu)
);
```

### 3. **Strategia tabeli na podklasę (Table per Subclass)**
```sql
-- Każda podklasa ma własną tabelę z wszystkimi atrybutami
CREATE TABLE samochody (
    id_pojazdu INT PRIMARY KEY,
    marka VARCHAR(50),
    model VARCHAR(50),
    nr_rejestracyjny VARCHAR(10) NOT NULL
);

CREATE TABLE rowery (
    id_pojazdu INT PRIMARY KEY,
    marka VARCHAR(50),
    model VARCHAR(50),
    typ_ramy VARCHAR(20) NOT NULL
);
```

## Mapowanie ograniczeń

### 1. **Ograniczenia uczestnictwa**
```
PRACOWNIK ───┤ DZIAL  (każdy pracownik MUSI mieć dział)
```

```sql
CREATE TABLE dzialy (
    id_dzialu INT PRIMARY KEY,
    nazwa VARCHAR(100)
);

CREATE TABLE pracownicy (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50),
    id_dzialu INT NOT NULL,  -- NOT NULL = obowiązkowe uczestnictwo
    
    FOREIGN KEY (id_dzialu) REFERENCES dzialy(id_dzialu)
);
```

### 2. **Ograniczenia kardynalności**
```sql
-- Maksymalnie 5 kursów na studenta
CREATE TABLE zapiski (
    id_studenta INT,
    id_kursu INT,
    PRIMARY KEY (id_studenta, id_kursu),
    
    -- Ograniczenie przez trigger lub constraint
    CONSTRAINT max_kursy_check CHECK (
        (SELECT COUNT(*) FROM zapiski z WHERE z.id_studenta = id_studenta) <= 5
    )
);
```

### 3. **Ograniczenia specjalizacji**
```sql
-- Pokrywające (covering) - każdy pojazd musi być samochodem LUB rowerem
ALTER TABLE pojazdy ADD CONSTRAINT covering_check 
CHECK (typ_pojazdu IN ('SAMOCHOD', 'ROWER'));

-- Rozłączne (disjoint) - pojazd nie może być jednocześnie samochodem I rowerem
-- Zapewnione przez typ_pojazdu = single value
```

## Przykład kompletnego mapowania

### Diagram ER: System biblioteczny
```
AUTOR ──── NAPISAL ──── KSIĄŻKA ──── EGZEMPLARZ
│                           │            │
│                           │            │
CZYTELNIK ──── WYPOŻYCZENIE ─────────────┘
```

### Mapowanie na SQL:
```sql
-- Encje podstawowe
CREATE TABLE autorzy (
    id_autora INT PRIMARY KEY,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    data_urodzenia DATE
);

CREATE TABLE ksiazki (
    id_ksiazki INT PRIMARY KEY,
    tytul VARCHAR(200) NOT NULL,
    isbn VARCHAR(13) UNIQUE,
    rok_wydania INT,
    liczba_stron INT
);

CREATE TABLE czytelnicy (
    id_czytelnika INT PRIMARY KEY,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    nr_karty VARCHAR(20) UNIQUE NOT NULL,
    data_urodzenia DATE
);

CREATE TABLE egzemplarze (
    id_egzemplarza INT PRIMARY KEY,
    id_ksiazki INT NOT NULL,
    sygnatura VARCHAR(50) UNIQUE NOT NULL,
    stan VARCHAR(20) DEFAULT 'DOBRY',
    
    FOREIGN KEY (id_ksiazki) REFERENCES ksiazki(id_ksiazki)
);

-- Związki M:N i 1:N
CREATE TABLE autorzy_ksiazek (
    id_autora INT,
    id_ksiazki INT,
    rola VARCHAR(50) DEFAULT 'AUTOR',  -- atrybut związku
    
    PRIMARY KEY (id_autora, id_ksiazki),
    FOREIGN KEY (id_autora) REFERENCES autorzy(id_autora),
    FOREIGN KEY (id_ksiazki) REFERENCES ksiazki(id_ksiazki)
);

CREATE TABLE wypozyczenia (
    id_wypozyczenia INT PRIMARY KEY,
    id_czytelnika INT NOT NULL,
    id_egzemplarza INT NOT NULL,
    data_wypozyczenia DATE NOT NULL DEFAULT CURRENT_DATE,
    data_planowego_zwrotu DATE NOT NULL,
    data_faktycznego_zwrotu DATE,
    
    FOREIGN KEY (id_czytelnika) REFERENCES czytelnicy(id_czytelnika),
    FOREIGN KEY (id_egzemplarza) REFERENCES egzemplarze(id_egzemplarza),
    
    -- Ograniczenia biznesowe
    CHECK (data_planowego_zwrotu > data_wypozyczenia),
    CHECK (data_faktycznego_zwrotu IS NULL OR data_faktycznego_zwrotu >= data_wypozyczenia)
);

-- Indeksy dla wydajności
CREATE INDEX idx_wypozyczenia_czytelnik ON wypozyczenia(id_czytelnika);
CREATE INDEX idx_wypozyczenia_egzemplarz ON wypozyczenia(id_egzemplarza);
CREATE INDEX idx_egzemplarze_ksiazka ON egzemplarze(id_ksiazki);
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**
1. **Konsystentne nazewnictwo** - liczba mnoga dla tabel, id_tabeli dla kluczy
2. **Normalizacja** - stosuj zasady normalizacji
3. **Indeksy** - na klucze obce i często używane kolumny
4. **Ograniczenia** - używaj CHECK, NOT NULL, UNIQUE
5. **Dokumentacja** - komentarze w SQL

### ❌ **Częste błędy:**
1. **Brak kluczy obcych** - utrata integralności referencyjnej
2. **Złe mapowanie M:N** - próba umieszczenia w jednej tabeli
3. **Ignorowanie encji słabych** - nieprawidłowe klucze
4. **Brak ograniczeń** - możliwość wprowadzenia błędnych danych
5. **Nadmierna denormalizacja** - utrata elastyczności

## Pułapki egzaminacyjne

### 1. **Encje słabe**
- Klucz główny = klucz obcy + klucz częściowy
- Cascade delete zwykle wymagane

### 2. **Związki M:N**
- Zawsze wymagają tabeli łączącej
- Klucz główny = kombinacja kluczy obcych

### 3. **Atrybuty wielowartościowe**
- Nigdy jako kolumny w głównej tabeli
- Zawsze osobna tabela

### 4. **Dziedziczenie**
- Wiele strategii mapowania
- Wybór zależy od przypadku użycia