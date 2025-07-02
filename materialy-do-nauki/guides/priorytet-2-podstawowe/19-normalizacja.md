# Normalizacja (1NF-BCNF) szczegółowo

## Cel normalizacji

**Normalizacja** to proces organizacji danych w relacyjnej bazie danych w celu **minimalizacji redundancji** i **unikania anomalii** podczas operacji INSERT, UPDATE i DELETE.

### Problemy przed normalizacją:
- **Redundancja** - te same dane w wielu miejscach
- **Anomalie aktualizacji** - niespójne zmiany
- **Anomalie wstawiania** - nie można dodać danych bez kontekstu
- **Anomalie usuwania** - utrata danych przy kasowaniu

## Zależności funkcyjne

### Definicja:
**Zależność funkcyjna X → Y** oznacza, że wartość X **jednoznacznie determinuje** wartość Y.

### Przykłady:
```
PESEL → {imię, nazwisko, data_urodzenia}
numer_konta → saldo
kod_produktu → {nazwa, cena, kategoria}
```

### Notacja:
```
A → B     (A determinuje B)
AB → C    (A i B razem determinują C)  
A → BC    (A determinuje B i C)
```

### Typy zależności:
```sql
-- Pełna zależność funkcyjna
{numer_studenta, kod_kursu} → ocena

-- Częściowa zależność funkcyjna  
numer_studenta → {imię, nazwisko}  -- z {numer_studenta, kod_kursu}

-- Zależność przechodnia
kod_kursu → kod_wydziału → nazwa_wydziału
```

## Pierwsza Postać Normalna (1NF)

### Definicja:
Tabela jest w **1NF**, jeśli:
1. **Wszystkie atrybuty są atomowe** (niepodzielne)
2. **Nie ma powtarzających się grup** atrybutów
3. **Każda komórka zawiera pojedynczą wartość**

### Przykład naruszenia 1NF:
```sql
-- ❌ NIE-1NF: Wielowartościowe atrybuty
CREATE TABLE pracownicy_zle (
    id INT,
    imie_nazwisko VARCHAR(100),    -- Nie atomowe!
    telefony VARCHAR(200),         -- Wiele wartości!
    umiejetnosci VARCHAR(500)      -- Lista umiejętności!
);

INSERT INTO pracownicy_zle VALUES 
(1, 'Jan Kowalski', '123-456-789, 987-654-321', 'Java, Python, SQL'),
(2, 'Anna Nowak', '555-123-456', 'C++, JavaScript, React');
```

### Normalizacja do 1NF:
```sql
-- ✅ 1NF: Atomowe wartości
CREATE TABLE pracownicy (
    id INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50)
);

CREATE TABLE telefony_pracownikow (
    id_pracownika INT,
    numer_telefonu VARCHAR(15),
    PRIMARY KEY (id_pracownika, numer_telefonu),
    FOREIGN KEY (id_pracownika) REFERENCES pracownicy(id)
);

CREATE TABLE umiejetnosci_pracownikow (
    id_pracownika INT,
    umiejetnosc VARCHAR(50),
    PRIMARY KEY (id_pracownika, umiejetnosc),
    FOREIGN KEY (id_pracownika) REFERENCES pracownicy(id)
);
```

### Inne naruszenia 1NF:
```sql
-- ❌ Powtarzające się grupy
CREATE TABLE zamowienia_zle (
    id_zamowienia INT,
    klient VARCHAR(100),
    produkt1 VARCHAR(100),
    ilosc1 INT,
    produkt2 VARCHAR(100),
    ilosc2 INT,
    produkt3 VARCHAR(100),
    ilosc3 INT
);

-- ✅ 1NF: Osobna tabela dla pozycji
CREATE TABLE zamowienia (
    id_zamowienia INT PRIMARY KEY,
    klient VARCHAR(100)
);

CREATE TABLE pozycje_zamowien (
    id_zamowienia INT,
    id_pozycji INT,
    produkt VARCHAR(100),
    ilosc INT,
    PRIMARY KEY (id_zamowienia, id_pozycji),
    FOREIGN KEY (id_zamowienia) REFERENCES zamowienia(id_zamowienia)
);
```

## Druga Postać Normalna (2NF)

### Definicja:
Tabela jest w **2NF**, jeśli:
1. **Jest w 1NF**
2. **Każdy atrybut niekluczowy** jest w pełni zależny funkcyjnie od **całego klucza głównego**

### Problem z 2NF - częściowe zależności:
```sql
-- ❌ NIE-2NF: Częściowe zależności
CREATE TABLE oceny_zle (
    numer_studenta INT,
    kod_kursu VARCHAR(10),
    ocena DECIMAL(3,2),
    imie_studenta VARCHAR(50),      -- Zależy tylko od numer_studenta!
    nazwisko_studenta VARCHAR(50),  -- Zależy tylko od numer_studenta!
    nazwa_kursu VARCHAR(100),       -- Zależy tylko od kod_kursu!
    ects INT,                       -- Zależy tylko od kod_kursu!
    
    PRIMARY KEY (numer_studenta, kod_kursu)
);

-- Zależności funkcyjne:
-- numer_studenta → {imie_studenta, nazwisko_studenta}  ← CZĘŚCIOWA!
-- kod_kursu → {nazwa_kursu, ects}                      ← CZĘŚCIOWA!
-- {numer_studenta, kod_kursu} → ocena                  ← PEŁNA
```

### Problemy z powyższą tabelą:
```sql
-- Anomalia wstawiania: Nie można dodać studenta bez kursu
INSERT INTO oceny_zle (numer_studenta, imie_studenta, nazwisko_studenta)
VALUES (123, 'Jan', 'Kowalski');  -- ERROR: Brak kod_kursu!

-- Anomalia usuwania: Usunięcie ostatniego kursu = utrata danych studenta
DELETE FROM oceny_zle WHERE kod_kursu = 'MAT101';  -- Utrata danych o studentach!

-- Anomalia aktualizacji: Zmiana nazwiska w wielu miejscach
UPDATE oceny_zle SET nazwisko_studenta = 'Kowalska' 
WHERE numer_studenta = 123;  -- Trzeba aktualizować wiele rekordów
```

### Normalizacja do 2NF:
```sql
-- ✅ 2NF: Eliminacja częściowych zależności
CREATE TABLE studenci (
    numer_studenta INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50)
);

CREATE TABLE kursy (
    kod_kursu VARCHAR(10) PRIMARY KEY,
    nazwa_kursu VARCHAR(100),
    ects INT
);

CREATE TABLE oceny (
    numer_studenta INT,
    kod_kursu VARCHAR(10),
    ocena DECIMAL(3,2),
    
    PRIMARY KEY (numer_studenta, kod_kursu),
    FOREIGN KEY (numer_studenta) REFERENCES studenci(numer_studenta),
    FOREIGN KEY (kod_kursu) REFERENCES kursy(kod_kursu)
);
```

## Trzecia Postać Normalna (3NF)

### Definicja:
Tabela jest w **3NF**, jeśli:
1. **Jest w 2NF**
2. **Nie ma zależności przechodnich** - każdy atrybut niekluczowy zależy **bezpośrednio** od klucza głównego

### Problem z 3NF - zależności przechodnie:
```sql
-- ❌ NIE-3NF: Zależności przechodnie
CREATE TABLE pracownicy_zle (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    id_dzialu INT,
    nazwa_dzialu VARCHAR(100),       -- Zależność przechodnia!
    kierownik_dzialu VARCHAR(100),   -- Zależność przechodnia!
    budzet_dzialu DECIMAL(15,2)      -- Zależność przechodnia!
);

-- Zależności funkcyjne:
-- id_pracownika → id_dzialu                                    ← BEZPOŚREDNIA
-- id_dzialu → {nazwa_dzialu, kierownik_dzialu, budzet_dzialu}  ← BEZPOŚREDNIA
-- id_pracownika → {nazwa_dzialu, kierownik_dzialu, budzet_dzialu} ← PRZECHODNIA!
```

### Problemy z zależnościami przechodnimi:
```sql
-- Anomalia aktualizacji: Zmiana nazwy działu w wielu miejscach
UPDATE pracownicy_zle SET nazwa_dzialu = 'IT Support'
WHERE id_dzialu = 10;  -- Trzeba zaktualizować wszystkich pracowników działu

-- Anomalia wstawiania: Nie można dodać działu bez pracownika
INSERT INTO pracownicy_zle (nazwa_dzialu, kierownik_dzialu, budzet_dzialu)
VALUES ('Marketing', 'Jan Kowalski', 50000);  -- ERROR: Brak id_pracownika!

-- Anomalia usuwania: Usunięcie ostatniego pracownika = utrata danych działu
DELETE FROM pracownicy_zle WHERE id_dzialu = 15;  -- Utrata informacji o dziale!
```

### Normalizacja do 3NF:
```sql
-- ✅ 3NF: Eliminacja zależności przechodnich
CREATE TABLE dzialy (
    id_dzialu INT PRIMARY KEY,
    nazwa_dzialu VARCHAR(100),
    kierownik_dzialu VARCHAR(100),
    budzet_dzialu DECIMAL(15,2)
);

CREATE TABLE pracownicy (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    id_dzialu INT,
    
    FOREIGN KEY (id_dzialu) REFERENCES dzialy(id_dzialu)
);
```

## Postać Normalna Boyce'a-Codda (BCNF)

### Definicja:
Tabela jest w **BCNF**, jeśli:
1. **Jest w 3NF**
2. **Każdy determinant jest kluczem kandydującym**

### Różnica między 3NF a BCNF:
```sql
-- Przykład 3NF ale NIE-BCNF
CREATE TABLE harmonogram (
    student VARCHAR(50),
    kurs VARCHAR(50),
    instruktor VARCHAR(50),
    
    PRIMARY KEY (student, kurs)
);

-- Zależności funkcyjne:
-- {student, kurs} → instruktor        ← Klucz kandydujący → atrybut (OK)
-- instruktor → kurs                   ← Determinant NIE jest kluczem! (PROBLEM)

-- Problem: instruktor determinuje kurs, ale nie jest kluczem kandydującym
```

### Problemy z naruszeniem BCNF:
```sql
-- Dane przykładowe:
INSERT INTO harmonogram VALUES 
('Jan', 'Matematyka', 'Dr. Smith'),
('Anna', 'Matematyka', 'Dr. Smith'),
('Piotr', 'Fizyka', 'Dr. Brown');

-- Anomalia aktualizacji: Dr. Smith zmienia kurs z Matematyki na Algebrę
UPDATE harmonogram SET kurs = 'Algebra' WHERE instruktor = 'Dr. Smith';
-- Problem: Trzeba pamiętać o aktualizacji WSZYSTKICH rekordów

-- Anomalia wstawiania: Nie można dodać instruktora bez studenta
INSERT INTO harmonogram (instruktor, kurs) VALUES ('Dr. White', 'Chemia');
-- ERROR: Brak student w kluczu głównym!
```

### Normalizacja do BCNF:
```sql
-- ✅ BCNF: Każdy determinant jest kluczem
CREATE TABLE instruktorzy_kursy (
    instruktor VARCHAR(50) PRIMARY KEY,
    kurs VARCHAR(50)
);

CREATE TABLE studenci_kursy (
    student VARCHAR(50),
    kurs VARCHAR(50),
    
    PRIMARY KEY (student, kurs),
    FOREIGN KEY (kurs) REFERENCES instruktorzy_kursy(kurs)
);

-- Teraz: instruktor → kurs (instruktor jest kluczem głównym w swojej tabeli)
```

### Przypadek gdy 3NF ≠ BCNF:
```sql
-- 3NF ale nie BCNF
CREATE TABLE rezerwacje (
    sala VARCHAR(20),
    czas VARCHAR(20),
    wykładowca VARCHAR(50),
    
    PRIMARY KEY (sala, czas)
);

-- Zależności:
-- {sala, czas} → wykładowca     (każda sala o danym czasie ma jednego wykładowcę)
-- wykładowca → czas             (każdy wykładowca ma stały czas zajęć)

-- Problem: wykładowca nie jest kluczem kandydującym, ale determinuje czas
```

## Algorytm normalizacji

### Krok 1: Analiza zależności funkcyjnych
```
Znajdź wszystkie zależności funkcyjne w tabeli:
- A → B
- C → D  
- AB → E
etc.
```

### Krok 2: Identyfikacja kluczy kandydujących
```
Znajdź wszystkie klucze kandydujące:
- Minimalne zestawy atrybutów determinujące wszystkie inne
```

### Krok 3: Sprawdź postaci normalne
```
1NF: Czy wszystkie atrybuty są atomowe?
2NF: Czy są częściowe zależności od klucza?
3NF: Czy są zależności przechodnie?
BCNF: Czy każdy determinant jest kluczem kandydującym?
```

### Krok 4: Dekompozycja
```
Dla każdej zależności naruszającej postać normalną:
- Utwórz nową tabelę z determinantem jako kluczem głównym
- Przenieś zależne atrybuty do nowej tabeli
- Zostaw klucz obcy w oryginalnej tabeli
```

## Przykład kompleksowy - sklep internetowy

### Tabela przed normalizacją:
```sql
-- ❌ Denormalizowana tabela
CREATE TABLE zamowienia_szczegoly (
    id_zamowienia INT,
    data_zamowienia DATE,
    id_klienta INT,
    imie_klienta VARCHAR(50),
    nazwisko_klienta VARCHAR(50),
    email_klienta VARCHAR(100),
    adres_klienta VARCHAR(200),
    id_produktu INT,
    nazwa_produktu VARCHAR(100),
    kategoria_produktu VARCHAR(50),
    cena_produktu DECIMAL(10,2),
    id_dostawcy INT,
    nazwa_dostawcy VARCHAR(100),
    telefon_dostawcy VARCHAR(15),
    ilosc INT,
    
    PRIMARY KEY (id_zamowienia, id_produktu)
);
```

### Zależności funkcyjne:
```
id_zamowienia → {data_zamowienia, id_klienta}
id_klienta → {imie_klienta, nazwisko_klienta, email_klienta, adres_klienta}
id_produktu → {nazwa_produktu, kategoria_produktu, cena_produktu, id_dostawcy}
id_dostawcy → {nazwa_dostawcy, telefon_dostawcy}
{id_zamowienia, id_produktu} → ilosc
```

### Normalizacja krok po kroku:

#### 1NF: ✅ Już spełniona - wszystkie atrybuty atomowe

#### 2NF: Eliminacja częściowych zależności
```sql
-- Częściowe zależności od {id_zamowienia, id_produktu}:
-- id_zamowienia → {data_zamowienia, id_klienta, imie_klienta, ...}
-- id_produktu → {nazwa_produktu, kategoria_produktu, ...}

CREATE TABLE zamowienia (
    id_zamowienia INT PRIMARY KEY,
    data_zamowienia DATE,
    id_klienta INT,
    imie_klienta VARCHAR(50),
    nazwisko_klienta VARCHAR(50),
    email_klienta VARCHAR(100),
    adres_klienta VARCHAR(200)
);

CREATE TABLE produkty (
    id_produktu INT PRIMARY KEY,
    nazwa_produktu VARCHAR(100),
    kategoria_produktu VARCHAR(50),
    cena_produktu DECIMAL(10,2),
    id_dostawcy INT,
    nazwa_dostawcy VARCHAR(100),
    telefon_dostawcy VARCHAR(15)
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

#### 3NF: Eliminacja zależności przechodnich
```sql
-- W tabeli zamowienia:
-- id_klienta → {imie_klienta, nazwisko_klienta, email_klienta, adres_klienta}

-- W tabeli produkty:
-- id_dostawcy → {nazwa_dostawcy, telefon_dostawcy}

CREATE TABLE klienci (
    id_klienta INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    email VARCHAR(100),
    adres VARCHAR(200)
);

CREATE TABLE dostawcy (
    id_dostawcy INT PRIMARY KEY,
    nazwa VARCHAR(100),
    telefon VARCHAR(15)
);

CREATE TABLE zamowienia (
    id_zamowienia INT PRIMARY KEY,
    data_zamowienia DATE,
    id_klienta INT,
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta)
);

CREATE TABLE produkty (
    id_produktu INT PRIMARY KEY,
    nazwa VARCHAR(100),
    kategoria VARCHAR(50),
    cena DECIMAL(10,2),
    id_dostawcy INT,
    FOREIGN KEY (id_dostawcy) REFERENCES dostawcy(id_dostawcy)
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

#### BCNF: ✅ Już spełniona - wszystkie determinanty są kluczami

## Zalety i wady normalizacji

### ✅ **Zalety:**
1. **Eliminacja redundancji** - dane nie się powtarzają
2. **Brak anomalii** - spójne operacje INSERT/UPDATE/DELETE
3. **Oszczędność miejsca** - mniej duplikatów
4. **Łatwość utrzymania** - zmiany w jednym miejscu
5. **Elastyczność** - łatwe dodawanie nowych danych

### ❌ **Wady:**
1. **Więcej tabel** - skomplikowana struktura
2. **Złożone zapytania** - więcej JOIN'ów
3. **Gorsza wydajność** - dodatkowe koszty łączenia
4. **Trudniejsze raportowanie** - trzeba łączyć wiele tabel

## Kiedy denormalizować?

### Uzasadnione przypadki:
```sql
-- Data warehouse / OLAP
CREATE TABLE sprzedaz_agregaty (
    rok INT,
    miesiac INT,
    kategoria VARCHAR(50),
    suma_sprzedazy DECIMAL(15,2),
    liczba_transakcji INT,
    srednia_wartosc DECIMAL(10,2)  -- Redundantne, ale przydatne
);

-- Często używane JOIN'y
CREATE TABLE zamowienia_denorm (
    id_zamowienia INT,
    data_zamowienia DATE,
    klient_nazwa VARCHAR(100),     -- Denormalizacja dla wydajności
    klient_email VARCHAR(100),     -- Często używane razem
    suma_zamowienia DECIMAL(15,2)  -- Obliczane, ale często potrzebne
);
```

## Narzędzia do normalizacji

### Sprawdzenie zależności funkcyjnych:
```sql
-- Znajdź potencjalne zależności funkcyjne
SELECT 
    a.kategoria,
    COUNT(DISTINCT a.dostawca) as liczba_dostawcow
FROM produkty a
GROUP BY a.kategoria
HAVING COUNT(DISTINCT a.dostawca) = 1;
-- Jeśli zawsze 1 → może być zależność kategoria → dostawca
```

### Sprawdzenie kluczy kandydujących:
```sql
-- Sprawdź czy kombinacja atrybutów jest unikalną
SELECT 
    student, kurs, COUNT(*)
FROM oceny
GROUP BY student, kurs
HAVING COUNT(*) > 1;
-- Jeśli pusty wynik → {student, kurs} może być kluczem
```

## Pułapki egzaminacyjne

### 1. **Definicje postaci normalnych**
- **1NF**: Atomowe wartości
- **2NF**: Brak częściowych zależności
- **3NF**: Brak zależności przechodnich  
- **BCNF**: Każdy determinant to klucz kandydujący

### 2. **Częściowa vs pełna zależność**
- **Częściowa**: Część klucza głównego determinuje atrybut
- **Pełna**: Cały klucz główny determinuje atrybut

### 3. **Zależność przechodnia**
- A → B → C, ale A nie → C bezpośrednio
- Eliminowana przez wydzielenie tabeli dla B → C

### 4. **BCNF vs 3NF**
- **3NF**: Wystarczająca dla większości przypadków
- **BCNF**: Bardziej rygorystyczna, czasem wymaga utraty zależności