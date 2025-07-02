# Klucze w bazach danych - główny, kandydujący, obcy + NULL

## Klucz główny (Primary Key)

### Definicja
**Klucz główny** to kolumna lub zestaw kolumn, które **jednoznacznie identyfikują** każdy rekord w tabeli.

### Właściwości klucza głównego:
- **Unikalność** - żadne dwa rekordy nie mogą mieć identycznych wartości
- **NOT NULL** - nie może zawierać wartości NULL
- **Niezmienialność** - wartość nie powinna się zmieniać
- **Minimalna** - nie zawiera zbędnych kolumn

### Składnia:
```sql
-- Jednokolumnowy klucz główny
CREATE TABLE studenci (
    id_studenta INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50)
);

-- Wielokolumnowy klucz główny (klucz złożony)
CREATE TABLE oceny (
    id_studenta INT,
    id_przedmiotu INT,
    ocena INT,
    PRIMARY KEY (id_studenta, id_przedmiotu)
);

-- Dodanie klucza głównego do istniejącej tabeli
ALTER TABLE produkty ADD PRIMARY KEY (id_produktu);
```

### Ograniczenia klucza głównego:
- **Jedna na tabelę** - każda tabela może mieć tylko jeden klucz główny
- **Nie może być NULL** - wszystkie kolumny klucza głównego muszą mieć wartość
- **Automatyczny indeks** - system tworzy unikalny indeks
- **Referencje** - może być używany jako cel dla kluczy obcych

## Klucz kandydujący (Candidate Key)

### Definicja
**Klucz kandydujący** to kolumna lub zestaw kolumn, które **mogłyby służyć** jako klucz główny.

### Właściwości:
- **Unikalność** - żadne duplikaty
- **Minimalna** - usunięcie którejkolwiek kolumny niszczy unikalność
- **Niezmienialność** - wartości są stabilne

### Przykład:
```sql
CREATE TABLE pracownicy (
    id_pracownika INT,        -- Klucz kandydujący #1
    numer_pesel CHAR(11),     -- Klucz kandydujący #2  
    email VARCHAR(100),       -- Klucz kandydujący #3
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    
    PRIMARY KEY (id_pracownika),  -- Wybrany klucz główny
    UNIQUE (numer_pesel),         -- Inne klucze kandydujące jako UNIQUE
    UNIQUE (email)
);
```

### Superklucz vs Klucz kandydujący:
- **Superklucz**: Dowolny zestaw kolumn zawierający klucz kandydujący
- **Klucz kandydujący**: Minimalny superklucz (nie można usunąć żadnej kolumny)

```sql
-- Przykład różnicy
-- Tabela: studenci (id, numer_indeksu, imie, nazwisko)

-- Superklucze:
{id}                           -- Klucz kandydujący
{numer_indeksu}               -- Klucz kandydujący  
{id, imie}                    -- Superklucz (nie minimalny)
{numer_indeksu, nazwisko}     -- Superklucz (nie minimalny)
{id, numer_indeksu, imie}     -- Superklucz (nie minimalny)
```

## Klucz alternatywny (Alternate Key)

### Definicja
**Klucz alternatywny** to klucz kandydujący, który **nie został wybrany** jako klucz główny.

### Implementacja:
```sql
CREATE TABLE klienci (
    id_klienta INT PRIMARY KEY,           -- Klucz główny
    nip CHAR(10) UNIQUE NOT NULL,         -- Klucz alternatywny
    regon CHAR(9) UNIQUE,                 -- Klucz alternatywny (może być NULL)
    nazwa VARCHAR(200)
);
```

## Klucz obcy (Foreign Key)

### Definicja
**Klucz obcy** to kolumna lub zestaw kolumn, które **odwołują się** do klucza głównego w innej tabeli (lub tej samej).

### Składnia:
```sql
CREATE TABLE zamowienia (
    id_zamowienia INT PRIMARY KEY,
    id_klienta INT,
    data_zamowienia DATE,
    
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta)
);

-- Alternatywna składnia
CREATE TABLE zamowienia (
    id_zamowienia INT PRIMARY KEY,
    id_klienta INT REFERENCES klienci(id_klienta),
    data_zamowienia DATE
);
```

### Opcje integralności referencyjnej:
```sql
CREATE TABLE zamowienia (
    id_zamowienia INT PRIMARY KEY,
    id_klienta INT,
    
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta)
        ON DELETE CASCADE        -- Usuń zamówienia gdy usuniesz klienta
        ON UPDATE CASCADE        -- Aktualizuj id_klienta gdy zmieni się w tabeli klienci
);

-- Inne opcje:
-- ON DELETE RESTRICT      -- Blokuj usuwanie klienta jeśli ma zamówienia
-- ON DELETE SET NULL      -- Ustaw id_klienta na NULL
-- ON DELETE SET DEFAULT   -- Ustaw id_klienta na wartość domyślną
-- ON DELETE NO ACTION     -- Sprawdź integralność na końcu transakcji
```

### Klucz obcy odnoszący się do tej samej tabeli:
```sql
CREATE TABLE pracownicy (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50),
    id_szefa INT,
    
    FOREIGN KEY (id_szefa) REFERENCES pracownicy(id_pracownika)
);
```

## Wartości NULL w kluczach

### Klucz główny i NULL
```sql
-- ❌ NIEDOZWOLONE - klucz główny nie może być NULL
INSERT INTO studenci (id_studenta, imie) VALUES (NULL, 'Jan');
-- ERROR: null value in column "id_studenta" violates not-null constraint
```

### Klucz kandydujący i NULL
```sql
-- Zależy od implementacji UNIQUE constraint
CREATE TABLE produkty (
    id INT PRIMARY KEY,
    kod_kreskowy VARCHAR(13) UNIQUE,  -- Może być NULL
    nazwa VARCHAR(100)
);

-- ✅ DOZWOLONE - jeden NULL w kolumnie UNIQUE
INSERT INTO produkty (id, nazwa) VALUES (1, 'Produkt bez kodu');
INSERT INTO produkty (id, nazwa) VALUES (2, 'Inny produkt bez kodu');

-- Niektóre SZBD pozwalają na wiele NULL w UNIQUE, inne nie
```

### Klucz obcy i NULL
```sql
-- ✅ DOZWOLONE - klucz obcy może być NULL
CREATE TABLE zamowienia (
    id INT PRIMARY KEY,
    id_klienta INT,  -- Może być NULL (zamówienie bez przypisanego klienta)
    
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta)
);

INSERT INTO zamowienia (id, id_klienta) VALUES (1, NULL);  -- OK
```

### Złożony klucz obcy i NULL
```sql
CREATE TABLE szczegoly_zamowienia (
    id INT PRIMARY KEY,
    id_zamowienia INT,
    id_produktu INT,
    
    FOREIGN KEY (id_zamowienia, id_produktu) REFERENCES pozycje(zam_id, prod_id)
);

-- Jeśli KTÓRAKOLWIEK kolumna klucza obcego jest NULL, 
-- cały klucz obcy jest traktowany jako NULL (nie sprawdzany)
INSERT INTO szczegoly_zamowienia VALUES (1, NULL, 5);  -- OK, nie sprawdza referencji
INSERT INTO szczegoly_zamowienia VALUES (2, 10, NULL); -- OK, nie sprawdza referencji
```

## Przykłady praktyczne

### Przykład 1: E-commerce
```sql
-- Tabela kategorii
CREATE TABLE kategorie (
    id_kategorii INT PRIMARY KEY,
    nazwa VARCHAR(100) UNIQUE NOT NULL,  -- Klucz alternatywny
    opis TEXT
);

-- Tabela produktów
CREATE TABLE produkty (
    id_produktu INT PRIMARY KEY,                    -- Klucz główny
    kod_ean VARCHAR(13) UNIQUE,                     -- Klucz alternatywny (może być NULL)
    nazwa VARCHAR(200) NOT NULL,
    id_kategorii INT,                               -- Klucz obcy
    
    FOREIGN KEY (id_kategorii) REFERENCES kategorie(id_kategorii)
        ON DELETE SET NULL   -- Produkt może istnieć bez kategorii
        ON UPDATE CASCADE    -- Aktualizuj automatycznie
);

-- Tabela klientów
CREATE TABLE klienci (
    id_klienta INT PRIMARY KEY,                     -- Klucz główny
    email VARCHAR(100) UNIQUE NOT NULL,             -- Klucz alternatywny
    nip CHAR(10) UNIQUE,                           -- Klucz alternatywny (NULL dla osób fizycznych)
    nazwa VARCHAR(200) NOT NULL
);

-- Tabela zamówień z złożonym kluczem obcym
CREATE TABLE zamowienia (
    id_zamowienia INT PRIMARY KEY,
    numer_zamowienia VARCHAR(20) UNIQUE NOT NULL,   -- Klucz alternatywny
    id_klienta INT NOT NULL,                        -- Klucz obcy (NOT NULL - wymagany)
    data_zamowienia DATE DEFAULT CURRENT_DATE,
    
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta)
        ON DELETE RESTRICT   -- Nie można usunąć klienta z zamówieniami
);
```

### Przykład 2: System HR
```sql
-- Struktura organizacyjna z self-reference
CREATE TABLE dzialy (
    id_dzialu INT PRIMARY KEY,
    nazwa VARCHAR(100) UNIQUE NOT NULL,
    id_dzialu_nadrzednego INT,                      -- Self-reference, może być NULL
    
    FOREIGN KEY (id_dzialu_nadrzednego) REFERENCES dzialy(id_dzialu)
        ON DELETE SET NULL   -- Dzial może zostać bez rodzica
);

-- Pracownicy z wieloma kluczami
CREATE TABLE pracownicy (
    id_pracownika INT PRIMARY KEY,                  -- Klucz główny
    numer_pesel CHAR(11) UNIQUE NOT NULL,          -- Klucz alternatywny
    email VARCHAR(100) UNIQUE NOT NULL,            -- Klucz alternatywny
    numer_telefonu VARCHAR(15) UNIQUE,             -- Klucz alternatywny (może być NULL)
    
    id_dzialu INT,                                 -- Klucz obcy (może być NULL)
    id_szefa INT,                                  -- Self-reference (może być NULL)
    
    FOREIGN KEY (id_dzialu) REFERENCES dzialy(id_dzialu)
        ON DELETE SET NULL,
    FOREIGN KEY (id_szefa) REFERENCES pracownicy(id_pracownika)
        ON DELETE SET NULL
);
```

## Sprawdzanie kluczy w systemie

### PostgreSQL:
```sql
-- Klucze główne
SELECT tc.table_name, kc.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kc 
  ON tc.constraint_name = kc.constraint_name
WHERE tc.constraint_type = 'PRIMARY KEY';

-- Klucze obce
SELECT 
    tc.table_name,
    kc.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kc
  ON tc.constraint_name = kc.constraint_name
JOIN information_schema.constraint_column_usage ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';

-- Ograniczenia UNIQUE
SELECT tc.table_name, kc.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kc
  ON tc.constraint_name = kc.constraint_name  
WHERE tc.constraint_type = 'UNIQUE';
```

## Optymalizacja i indeksy

### Automatyczne indeksy:
```sql
-- Klucz główny automatycznie tworzy unikalny indeks
CREATE TABLE test (id INT PRIMARY KEY);
-- Równoważne z:
CREATE TABLE test (id INT);
ALTER TABLE test ADD PRIMARY KEY (id);
-- System tworzy: UNIQUE INDEX test_pkey ON test (id);

-- Klucze obce nie tworzą automatycznie indeksów!
CREATE INDEX idx_zamowienia_klienta ON zamowienia (id_klienta);  -- Ręcznie!
```

### Indeksy composite keys:
```sql
-- Złożony klucz główny
CREATE TABLE sprzedaz (
    id_produktu INT,
    data_sprzedazy DATE,
    ilosc INT,
    PRIMARY KEY (id_produktu, data_sprzedazy)  -- Indeks na (id_produktu, data_sprzedazy)
);

-- Może być przydatny dodatkowy indeks w odwrotnej kolejności
CREATE INDEX idx_sprzedaz_data_produkt ON sprzedaz (data_sprzedazy, id_produktu);
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**
1. **Surrogate keys** - używaj sztucznych kluczy głównych (AUTO_INCREMENT/SERIAL)
2. **Stable keys** - unikaj kluczy głównych, które się zmieniają
3. **Index foreign keys** - ręcznie twórz indeksy na klucze obce
4. **Naming conventions** - spójne nazwy (id_tabeli)
5. **Minimal keys** - używaj najmniejszej liczby kolumn

### ❌ **Złe praktyki:**
1. **Natural keys as primary** - unikaj kluczy biznesowych jako głównych
2. **Composite keys gdy niepotrzebne** - komplikują zapytania
3. **Missing foreign key indexes** - powolne JOIN'y
4. **Nullable foreign keys bez uzasadnienia** - może wskazywać na błąd w projekcie

## Pułapki egzaminacyjne

### 1. **NULL w kluczach**
- **Klucz główny**: NIGDY nie może być NULL
- **Klucz obcy**: MOŻE być NULL
- **UNIQUE constraint**: Zwykle może mieć jeden NULL (zależy od SZBD)

### 2. **Różnice między kluczami**
- **Kandydujący**: Wszystkie możliwe klucze główne
- **Główny**: Wybrany klucz kandydujący  
- **Alternatywny**: Niewybrany klucz kandydujący
- **Obcy**: Referencja do klucza głównego w innej tabeli

### 3. **Composite foreign keys**
- Jeśli JAKAKOLWIEK kolumna jest NULL, cały klucz jest NULL
- Nie sprawdza się integralności referencyjnej

### 4. **Referential integrity options**
- CASCADE: Propaguj zmiany
- RESTRICT: Blokuj operację  
- SET NULL: Ustaw NULL
- SET DEFAULT: Ustaw wartość domyślną
- NO ACTION: Sprawdź na końcu transakcji