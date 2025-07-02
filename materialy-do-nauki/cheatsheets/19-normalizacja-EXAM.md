# 📐 NORMALIZACJA (1NF-BCNF) - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Normalizacja to proces eliminacji redundancji przez rozkład tabel na mniejsze, logiczne jednostki. Główne postacie normalne:

1. **1NF** - atomowe wartości, brak powtarzających się grup
2. **2NF** - 1NF + każdy atrybut nieklucz zależy od całego klucza głównego
3. **3NF** - 2NF + brak zależności przechodnich (nieklucz→nieklucz)
4. **BCNF** - 3NF + każda zależność funkcyjna ma po lewej superklucz

Wyższa postać = mniej redundancji = mniej anomalii, ale więcej JOIN'ów."

## ✍️ CO NAPISAĆ NA KARTCE

```
POSTACIE NORMALNE - DEFINICJE I WARUNKI:

1NF (First Normal Form):
✓ Wszystkie atrybuty mają wartości atomowe
✓ Brak powtarzających się grup
✓ Każda komórka zawiera pojedynczą wartość

2NF (Second Normal Form):  
✓ Jest w 1NF
✓ Każdy atrybut nieklucz jest w pełni zależny funkcyjnie od klucza głównego
✓ Brak częściowych zależności od klucza złożonego

3NF (Third Normal Form):
✓ Jest w 2NF  
✓ Brak zależności przechodnich
✓ Żaden atrybut nieklucz nie zależy od innego atrybutu nieklucz

BCNF (Boyce-Codd Normal Form):
✓ Jest w 3NF
✓ Dla każdej zależności funkcyjnej X→Y: X jest superkluczem
✓ Eliminuje anomalie związane z nakładającymi się kluczami kandydującymi

PROCES NORMALIZACJI:
Tabela nieznormalizowana
    ↓ usuń wartości nieatomowe + powtarzające się grupy
1NF ↓ usuń częściowe zależności od klucza
2NF ↓ usuń zależności przechodnie  
3NF ↓ usuń zależności od nie-superkluczy
BCNF

PRZYKŁAD KROK PO KROK:
Tabela: zamowienia(nr_zam, data, id_kl, nazwa_kl, adres_kl, produkty, ceny)

PROBLEM: produkty="laptop,mysz", ceny="3000,50" - NIE 1NF!

1NF: Rozbić na wiersze:
zamowienia_1nf(nr_zam, data, id_kl, nazwa_kl, adres_kl, produkt, cena)

PROBLEM: nazwa_kl zależy tylko od id_kl, nie od całego klucza (nr_zam,produkt)

2NF: Wydzielić tabele:
zamowienia(nr_zam, data, id_kl)
klienci(id_kl, nazwa_kl, adres_kl)  
pozycje(nr_zam, produkt, cena)

PROBLEM: adres_kl może zależeć od miasta, kod_poczt→miasto

3NF/BCNF: Dalsze rozbicie jeśli potrzeba
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- DEMONSTRACJA PROCESU NORMALIZACJI

-- TABELA NIEZNORMALIZOWANA (0NF)
CREATE TABLE zamowienia_0nf (
    nr_zamowienia INT,
    data_zamowienia DATE,
    id_klienta INT,
    nazwa_klienta VARCHAR(100),
    adres_klienta TEXT,
    telefon_klienta VARCHAR(20),
    produkty TEXT,  -- "Laptop Dell,Mysz optyczna,Klawiatura"
    ceny TEXT,      -- "3500.00,50.00,120.00"
    ilosci TEXT     -- "1,2,1"
);

-- Przykładowe dane nieznormalizowane
INSERT INTO zamowienia_0nf VALUES 
(1, '2024-01-15', 100, 'Firma ABC', 'Warszawa ul. Główna 1', '123456789',
 'Laptop Dell,Mysz optyczna', '3500.00,50.00', '1,2'),
(2, '2024-01-16', 100, 'Firma ABC', 'Warszawa ul. Główna 1', '123456789',
 'Klawiatura', '120.00', '1'),
(3, '2024-01-17', 200, 'Firma XYZ', 'Kraków ul. Nowa 5', '987654321',
 'Laptop Dell,Monitor', '3500.00,800.00', '2,1');

-- PROBLEMY W 0NF:
-- ✗ Wartości nieatomowe (listy w kolumnach)
-- ✗ Redundancja danych klienta
-- ✗ Trudność zapytań (jak znaleźć wszystkie laptopy?)

-- KROK 1: NORMALIZACJA DO 1NF

-- Rozbicie wartości nieatomowych na osobne wiersze
CREATE TABLE zamowienia_1nf (
    nr_zamowienia INT,
    data_zamowienia DATE,
    id_klienta INT,
    nazwa_klienta VARCHAR(100),
    adres_klienta TEXT,
    telefon_klienta VARCHAR(20),
    produkt VARCHAR(100),
    cena DECIMAL(10,2),
    ilosc INT,
    PRIMARY KEY (nr_zamowienia, produkt)  -- klucz złożony
);

-- Wypełnienie danych w 1NF
INSERT INTO zamowienia_1nf VALUES 
(1, '2024-01-15', 100, 'Firma ABC', 'Warszawa ul. Główna 1', '123456789', 'Laptop Dell', 3500.00, 1),
(1, '2024-01-15', 100, 'Firma ABC', 'Warszawa ul. Główna 1', '123456789', 'Mysz optyczna', 50.00, 2),
(2, '2024-01-16', 100, 'Firma ABC', 'Warszawa ul. Główna 1', '123456789', 'Klawiatura', 120.00, 1),
(3, '2024-01-17', 200, 'Firma XYZ', 'Kraków ul. Nowa 5', '987654321', 'Laptop Dell', 3500.00, 2),
(3, '2024-01-17', 200, 'Firma XYZ', 'Kraków ul. Nowa 5', '987654321', 'Monitor', 800.00, 1);

-- ANALIZA 1NF - wykrycie zależności funkcyjnych:
-- nr_zamowienia → data_zamowienia, id_klienta
-- id_klienta → nazwa_klienta, adres_klienta, telefon_klienta
-- (nr_zamowienia, produkt) → cena, ilosc

-- PROBLEM W 1NF: Częściowe zależności!
-- nazwa_klienta zależy tylko od id_klienta, nie od całego klucza (nr_zamowienia, produkt)

-- KROK 2: NORMALIZACJA DO 2NF

-- Wydzielenie tabel eliminujących częściowe zależności
CREATE TABLE zamowienia_2nf (
    nr_zamowienia INT PRIMARY KEY,
    data_zamowienia DATE,
    id_klienta INT
);

CREATE TABLE klienci_2nf (
    id_klienta INT PRIMARY KEY,
    nazwa_klienta VARCHAR(100),
    adres_klienta TEXT,
    telefon_klienta VARCHAR(20)
);

CREATE TABLE pozycje_zamowienia_2nf (
    nr_zamowienia INT,
    produkt VARCHAR(100),
    cena DECIMAL(10,2),
    ilosc INT,
    PRIMARY KEY (nr_zamowienia, produkt),
    FOREIGN KEY (nr_zamowienia) REFERENCES zamowienia_2nf(nr_zamowienia)
);

-- Wypełnienie danych w 2NF
INSERT INTO zamowienia_2nf VALUES 
(1, '2024-01-15', 100),
(2, '2024-01-16', 100),
(3, '2024-01-17', 200);

INSERT INTO klienci_2nf VALUES 
(100, 'Firma ABC', 'Warszawa ul. Główna 1', '123456789'),
(200, 'Firma XYZ', 'Kraków ul. Nowa 5', '987654321');

INSERT INTO pozycje_zamowienia_2nf VALUES 
(1, 'Laptop Dell', 3500.00, 1),
(1, 'Mysz optyczna', 50.00, 2),
(2, 'Klawiatura', 120.00, 1),
(3, 'Laptop Dell', 3500.00, 2),
(3, 'Monitor', 800.00, 1);

-- ANALIZA 2NF - wykrycie zależności przechodnich:
-- Możliwe problemy: jeśli adres_klienta zawiera miasto i kod_pocztowy
-- I jeśli kod_pocztowy → miasto (zależność przechodnia)

-- KROK 3: ANALIZA ZALEŻNOŚCI PRZECHODNICH DLA 3NF

-- Załóżmy że adres ma strukturę: "miasto kod_pocztowy ulica"
-- I istnieje zależność: kod_pocztowy → miasto

-- Rozszerzenie klientów o szczegóły adresu
ALTER TABLE klienci_2nf ADD COLUMN miasto VARCHAR(50);
ALTER TABLE klienci_2nf ADD COLUMN kod_pocztowy VARCHAR(6);
ALTER TABLE klienci_2nf ADD COLUMN ulica VARCHAR(100);

UPDATE klienci_2nf SET 
    miasto = 'Warszawa', kod_pocztowy = '00-001', ulica = 'ul. Główna 1'
WHERE id_klienta = 100;

UPDATE klienci_2nf SET 
    miasto = 'Kraków', kod_pocztowy = '30-001', ulica = 'ul. Nowa 5'  
WHERE id_klienta = 200;

-- PROBLEM: kod_pocztowy → miasto (zależność przechodnia)

-- KROK 3: NORMALIZACJA DO 3NF

CREATE TABLE zamowienia_3nf (
    nr_zamowienia INT PRIMARY KEY,
    data_zamowienia DATE,
    id_klienta INT
);

CREATE TABLE klienci_3nf (
    id_klienta INT PRIMARY KEY,
    nazwa_klienta VARCHAR(100),
    telefon_klienta VARCHAR(20),
    kod_pocztowy VARCHAR(6),
    ulica VARCHAR(100)
);

CREATE TABLE kody_pocztowe_3nf (
    kod_pocztowy VARCHAR(6) PRIMARY KEY,
    miasto VARCHAR(50)
);

CREATE TABLE pozycje_zamowienia_3nf (
    nr_zamowienia INT,
    id_produktu INT,
    cena_w_momencie_sprzedazy DECIMAL(10,2),
    ilosc INT,
    PRIMARY KEY (nr_zamowienia, id_produktu)
);

CREATE TABLE produkty_3nf (
    id_produktu INT PRIMARY KEY,
    nazwa VARCHAR(100),
    cena_aktualna DECIMAL(10,2)
);

-- KROK 4: SPRAWDZENIE BCNF

-- Załóżmy że mamy tabelę z nakładającymi się kluczami kandydującymi:
CREATE TABLE nauczyciele_przedmioty (
    nauczyciel VARCHAR(50),
    przedmiot VARCHAR(50),
    sala VARCHAR(20),
    PRIMARY KEY (nauczyciel, przedmiot)
);

-- Zależności funkcyjne:
-- (nauczyciel, przedmiot) → sala
-- sala → przedmiot  (każda sala dedykowana jednemu przedmiotowi)

-- PROBLEM BCNF: sala → przedmiot, ale sala nie jest superkluczem!

-- NORMALIZACJA DO BCNF:
CREATE TABLE sale_bcnf (
    sala VARCHAR(20) PRIMARY KEY,
    przedmiot VARCHAR(50)
);

CREATE TABLE przydzialy_bcnf (
    nauczyciel VARCHAR(50),
    sala VARCHAR(20),
    PRIMARY KEY (nauczyciel, sala),
    FOREIGN KEY (sala) REFERENCES sale_bcnf(sala)
);

-- FUNKCJE POMOCNICZE DO ANALIZY NORMALIZACJI

-- Znajdowanie potencjalnych zależności funkcyjnych
CREATE OR REPLACE FUNCTION znajdz_potencjalne_fd(
    tabela_name TEXT,
    kolumna_determinant TEXT,
    kolumna_dependent TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    sql_query TEXT;
    violation_count INT;
BEGIN
    -- Sprawdź czy X → Y (dla każdej wartości X istnieje tylko jedna wartość Y)
    sql_query := format(
        'SELECT COUNT(*) FROM (
            SELECT %I, COUNT(DISTINCT %I) as distinct_vals 
            FROM %I 
            GROUP BY %I 
            HAVING COUNT(DISTINCT %I) > 1
        ) violations',
        kolumna_determinant, kolumna_dependent, tabela_name,
        kolumna_determinant, kolumna_dependent
    );
    
    EXECUTE sql_query INTO violation_count;
    
    IF violation_count = 0 THEN
        RAISE NOTICE 'Możliwa zależność funkcyjna: % → %', kolumna_determinant, kolumna_dependent;
        RETURN TRUE;
    ELSE
        RAISE NOTICE 'Brak zależności funkcyjnej: % → %', kolumna_determinant, kolumna_dependent;
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Test na danych
SELECT znajdz_potencjalne_fd('klienci_2nf', 'id_klienta', 'nazwa_klienta');
SELECT znajdz_potencjalne_fd('pozycje_zamowienia_2nf', 'produkt', 'cena');

-- Sprawdzenie redundancji
CREATE OR REPLACE FUNCTION sprawdz_redundancje(tabela_name TEXT)
RETURNS TABLE(kolumna TEXT, powtorzen INT, procent_redundancji NUMERIC) AS $$
BEGIN
    RETURN QUERY EXECUTE format('
        SELECT 
            column_name::TEXT,
            COUNT(*) - COUNT(DISTINCT %I) as powtorzen,
            ROUND(100.0 * (COUNT(*) - COUNT(DISTINCT %I)) / COUNT(*), 2) as procent
        FROM %I, information_schema.columns 
        WHERE table_name = %L
        GROUP BY column_name
        HAVING COUNT(*) - COUNT(DISTINCT %I) > 0
        ORDER BY powtorzen DESC',
        tabela_name, tabela_name, tabela_name, tabela_name, tabela_name
    );
END;
$$ LANGUAGE plpgsql;

-- Sprawdzenie redundancji w tabeli nieznormalizowanej
SELECT * FROM sprawdz_redundancje('zamowienia_1nf');
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: 2NF dotyczy tylko tabel z kluczem złożonym
2. **UWAGA**: 3NF eliminuje zależności przechodnie (nieklucz→nieklucz)
3. **BŁĄD**: Myślenie że BCNF zawsze jest osiągalna bez straty informacji
4. **WAŻNE**: Każda wyższa postać zawiera warunki poprzednich
5. **PUŁAPKA**: Normalizacja może obniżyć wydajność (więcej JOIN'ów)

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Normal forms** - postacie normalne
- **Functional dependency** - zależność funkcyjna
- **Partial dependency** - częściowa zależność
- **Transitive dependency** - zależność przechodnia
- **Candidate key/Superkey** - klucz kandydujący/superklucz
- **Lossless decomposition** - dekompozycja bezstratna
- **Redundancy elimination** - eliminacja redundancji
- **Atomic values** - wartości atomowe

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **27-zaleznosci-funkcyjne** - podstawa normalizacji
- **05-twierdzenie-heatha** - bezstratna dekompozycja
- **15-redundancja** - eliminacja przez normalizację
- **28-normalizacja-zaawansowana** - 4NF, 5NF
- **12-klucze-bazy-danych** - klucze w normalizacji