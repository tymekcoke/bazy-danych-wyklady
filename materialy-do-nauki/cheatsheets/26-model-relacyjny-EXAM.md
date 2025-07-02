# 🔗 MODEL RELACYJNY - PODSTAWY TEORETYCZNE - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Model relacyjny to formalny model danych oparty na teorii zbiorów i logice matematycznej. Kluczowe pojęcia:

1. **Relacja** - zbiór krotek o tym samym schemacie (tabela)
2. **Krotka** - uporządkowana lista wartości (wiersz)
3. **Atrybut** - kolumna relacji z określoną domeną
4. **Domena** - zbiór możliwych wartości atrybutu
5. **Klucz** - zbiór atrybutów jednoznacznie identyfikujący krotkę

Właściwości: atomowość wartości, unikalność krotek, brak uporządkowania krotek i atrybutów. Model relacyjny jest podstawą SQL i większości współczesnych DBMS."

## ✍️ CO NAPISAĆ NA KARTCE

```
MODEL RELACYJNY - DEFINICJE FORMALNE:

DOMENA (D):
• Zbiór możliwych wartości dla atrybutu
• D₁ = {1, 2, 3, ..., 999999} (ID)
• D₂ = {string o długości ≤ 50} (imię)
• D₃ = {TRUE, FALSE} (boolean)

SCHEMAT RELACJI R(A₁:D₁, A₂:D₂, ..., Aₙ:Dₙ):
• R - nazwa relacji
• Aᵢ - atrybuty (kolumny)
• Dᵢ - domeny atrybutów
• Przykład: STUDENT(id:INT, imie:VARCHAR, wiek:INT)

RELACJA r:
• r ⊆ D₁ × D₂ × ... × Dₙ (podzbiór iloczynu kartezjańskiego domen)
• Zbiór krotek o tym samym schemacie
• r = {⟨1, 'Jan', 20⟩, ⟨2, 'Anna', 22⟩}

KROTKA t:
• t ∈ r (krotka należy do relacji)
• t = ⟨v₁, v₂, ..., vₙ⟩ gdzie vᵢ ∈ Dᵢ
• t[Aᵢ] - wartość atrybutu Aᵢ w krotce t

KLUCZ KANDYDUJĄCY K:
• K ⊆ {A₁, A₂, ..., Aₙ} (podzbiór atrybutów)
• ∀t₁,t₂ ∈ r: t₁ ≠ t₂ ⟹ t₁[K] ≠ t₂[K] (unikalność)
• Minimal: brak właściwego podzbioru z tą właściwością

KLUCZ GŁÓWNY:
• Jeden wybrany klucz kandydujący
• Nie może zawierać NULL

KLUCZ OBCY:
• Zbiór atrybutów odwołujący się do klucza głównego innej relacji
• Integralność referencyjna: wartości muszą istnieć w tabeli referencyjnej

WŁAŚCIWOŚCI MODELU RELACYJNEGO:
1. Atomowość wartości (1NF)
2. Unikalność krotek (no duplicates)  
3. Brak uporządkowania krotek
4. Brak uporządkowania atrybutów
5. Każda krotka ma tę samą strukturę

OGRANICZENIA INTEGRALNOŚCI:
• Domain constraints - wartości z właściwych domen
• Key constraints - unikalność kluczy
• Entity integrity - klucz główny NOT NULL
• Referential integrity - klucze obce
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- DEMONSTRACJA FORMALNYCH POJĘĆ MODELU RELACYJNEGO

-- 1. DEFINICJA DOMEN

-- Domeny jako typy danych w PostgreSQL
CREATE DOMAIN dom_id AS INTEGER CHECK (VALUE > 0);
CREATE DOMAIN dom_imie AS VARCHAR(50) CHECK (VALUE ~ '^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$');
CREATE DOMAIN dom_email AS VARCHAR(100) CHECK (VALUE ~ '^[^@]+@[^@]+\.[^@]+$');
CREATE DOMAIN dom_wiek AS INTEGER CHECK (VALUE BETWEEN 0 AND 150);
CREATE DOMAIN dom_pensja AS DECIMAL(10,2) CHECK (VALUE >= 0);

-- 2. SCHEMATY RELACJI z domenami

-- Schemat relacji STUDENT(id:dom_id, imie:dom_imie, email:dom_email, wiek:dom_wiek)
CREATE TABLE studenci (
    id_studenta dom_id PRIMARY KEY,
    imie dom_imie NOT NULL,
    nazwisko dom_imie NOT NULL,
    email dom_email UNIQUE,
    wiek dom_wiek,
    data_urodzenia DATE
);

-- Schemat relacji PRZEDMIOT(kod:VARCHAR(10), nazwa:VARCHAR(100), ects:INTEGER)
CREATE TABLE przedmioty (
    kod_przedmiotu VARCHAR(10) PRIMARY KEY CHECK (kod_przedmiotu ~ '^[A-Z]{2,4}[0-9]{3}$'),
    nazwa VARCHAR(100) NOT NULL,
    ects INTEGER CHECK (ects BETWEEN 1 AND 30),
    semestr INTEGER CHECK (semestr BETWEEN 1 AND 10)
);

-- Schemat relacji OCENA z kluczem złożonym
CREATE TABLE oceny (
    id_studenta dom_id,
    kod_przedmiotu VARCHAR(10),
    wartosc DECIMAL(3,1) CHECK (wartosc IN (2.0, 3.0, 3.5, 4.0, 4.5, 5.0)),
    data_wystawienia DATE DEFAULT CURRENT_DATE,
    
    -- Klucz główny złożony
    PRIMARY KEY (id_studenta, kod_przedmiotu),
    
    -- Klucze obce (integralność referencyjna)
    FOREIGN KEY (id_studenta) REFERENCES studenci(id_studenta),
    FOREIGN KEY (kod_przedmiotu) REFERENCES przedmioty(kod_przedmiotu)
);

-- 3. PRZYKŁAD RELACJI (zbiorów krotek)

-- Relacja studenci
INSERT INTO studenci VALUES 
(1, 'Jan', 'Kowalski', 'jan.kowalski@student.uw.edu.pl', 20, '2004-03-15'),
(2, 'Anna', 'Nowak', 'anna.nowak@student.uw.edu.pl', 22, '2002-07-22'),
(3, 'Piotr', 'Wiśniewski', 'piotr.wisniewski@student.uw.edu.pl', 21, '2003-11-08');

-- Relacja przedmioty  
INSERT INTO przedmioty VALUES 
('BD001', 'Bazy Danych', 6, 4),
('MAT201', 'Matematyka Dyskretna', 4, 2),
('PRG101', 'Programowanie Obiektowe', 5, 3);

-- Relacja oceny (związek M:N)
INSERT INTO oceny VALUES 
(1, 'BD001', 4.5, '2024-01-15'),
(1, 'MAT201', 3.5, '2024-01-10'),
(2, 'BD001', 5.0, '2024-01-15'),
(2, 'PRG101', 4.0, '2024-01-12'),
(3, 'MAT201', 3.0, '2024-01-10');

-- 4. ANALIZA KLUCZY KANDYDUJĄCYCH

-- Funkcja sprawdzająca czy zbiór atrybutów jest kluczem kandydującym
CREATE OR REPLACE FUNCTION sprawdz_klucz_kandydujacy(
    tabela_name TEXT,
    atrybuty TEXT[]
) RETURNS BOOLEAN AS $$
DECLARE
    sql_query TEXT;
    total_rows INTEGER;
    unique_combinations INTEGER;
BEGIN
    -- Sprawdź liczbę wierszy w tabeli
    EXECUTE format('SELECT COUNT(*) FROM %I', tabela_name) INTO total_rows;
    
    -- Sprawdź liczbę unikalnych kombinacji dla podanych atrybutów
    sql_query := format(
        'SELECT COUNT(DISTINCT (%s)) FROM %I',
        array_to_string(atrybuty, ', '),
        tabela_name
    );
    EXECUTE sql_query INTO unique_combinations;
    
    -- Klucz kandydujący: liczba unikalnych kombinacji = liczba wierszy
    IF total_rows = unique_combinations THEN
        RAISE NOTICE 'Atrybuty % tworzą klucz kandydujący w tabeli %', atrybuty, tabela_name;
        RETURN TRUE;
    ELSE
        RAISE NOTICE 'Atrybuty % NIE tworzą klucza kandydującego w tabeli %', atrybuty, tabela_name;
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Testowanie kluczy kandydujących
SELECT sprawdz_klucz_kandydujacy('studenci', ARRAY['id_studenta']);  -- TRUE
SELECT sprawdz_klucz_kandydujacy('studenci', ARRAY['email']);        -- TRUE  
SELECT sprawdz_klucz_kandydujacy('studenci', ARRAY['imie']);         -- FALSE
SELECT sprawdz_klucz_kandydujacy('oceny', ARRAY['id_studenta', 'kod_przedmiotu']); -- TRUE

-- 5. WŁAŚCIWOŚCI RELACJI - testowanie

-- Test unikalności krotek (właściwość relacji)
-- Próba wstawienia duplikatu - powinno się nie udać
-- INSERT INTO studenci VALUES (1, 'Jan', 'Kowalski', 'jan@test.com', 20, '2004-03-15'); -- BŁĄD

-- Test atomowości wartości (1NF)
-- Zabronione w modelu relacyjnym:
-- CREATE TABLE zla_tabela (id INT, telefony TEXT[]); -- arrays = not atomic

-- 6. OPERACJE NA RELACJACH (algebra relacji w SQL)

-- Projekcja π (wybór kolumn)
SELECT imie, nazwisko FROM studenci;  -- π_{imie,nazwisko}(studenci)

-- Selekcja σ (wybór wierszy)
SELECT * FROM studenci WHERE wiek > 20;  -- σ_{wiek>20}(studenci)

-- Złączenie ⋈ (join)
SELECT s.imie, s.nazwisko, o.wartosc, p.nazwa
FROM studenci s
JOIN oceny o ON s.id_studenta = o.id_studenta
JOIN przedmioty p ON o.kod_przedmiotu = p.kod_przedmiotu;

-- Iloczyn kartezjański × (cross join)
SELECT s.imie, p.nazwa
FROM studenci s CROSS JOIN przedmioty p;

-- 7. INTEGRALNOŚĆ REFERENCYJNA

-- Przykład naruszenia integralności referencyjnej
-- INSERT INTO oceny VALUES (999, 'BD001', 5.0); -- BŁĄD: student nie istnieje

-- Testowanie akcji przy naruszeniu integralności
CREATE TABLE tmp_studenci AS SELECT * FROM studenci;
CREATE TABLE tmp_oceny (
    id_studenta INTEGER,
    kod_przedmiotu VARCHAR(10),
    wartosc DECIMAL(3,1),
    
    FOREIGN KEY (id_studenta) REFERENCES tmp_studenci(id_studenta)
        ON DELETE CASCADE  -- usunięcie studenta usuwa jego oceny
        ON UPDATE CASCADE  -- zmiana ID studenta aktualizuje oceny
);

-- 8. SUPERKLUCZĘ I KLUCZĘ MINIMALNE

-- Superklucz: każdy zbiór atrybutów zawierający klucz kandydujący
-- W tabeli studenci:
-- {id_studenta} - klucz kandydujący (minimalny)
-- {id_studenta, imie} - superklucz (nieminimalny)
-- {id_studenta, imie, nazwisko} - superklucz (nieminimalny)

-- Funkcja sprawdzająca minimalność klucza
CREATE OR REPLACE FUNCTION sprawdz_minimalnosc_klucza(
    tabela_name TEXT,
    atrybuty TEXT[]
) RETURNS BOOLEAN AS $$
DECLARE
    atrybut TEXT;
    reduced_attrs TEXT[];
BEGIN
    -- Sprawdź czy każdy podzbiór właściwy nie jest kluczem
    FOREACH atrybut IN ARRAY atrybuty LOOP
        -- Utwórz tablicę bez bieżącego atrybutu
        reduced_attrs := array_remove(atrybuty, atrybut);
        
        -- Jeśli podzbiór jest pusty, pomiń
        IF array_length(reduced_attrs, 1) IS NULL THEN
            CONTINUE;
        END IF;
        
        -- Sprawdź czy redukcja nadal jest kluczem
        IF sprawdz_klucz_kandydujacy(tabela_name, reduced_attrs) THEN
            RAISE NOTICE 'Klucz % nie jest minimalny - podzbiór % też jest kluczem', atrybuty, reduced_attrs;
            RETURN FALSE;
        END IF;
    END LOOP;
    
    RAISE NOTICE 'Klucz % jest minimalny', atrybuty;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Test minimalności
SELECT sprawdz_minimalnosc_klucza('studenci', ARRAY['id_studenta']);  -- TRUE
SELECT sprawdz_minimalnosc_klucza('studenci', ARRAY['id_studenta', 'imie']);  -- FALSE

-- 9. NORMALIZACJA w kontekście modelu relacyjnego

-- Relacja nieznormalizowana (narusza 1NF - wartości nieatomowe)
CREATE TABLE zla_relacja (
    student_id INTEGER,
    student_name VARCHAR(100),
    courses_grades TEXT  -- "BD001:4.5,MAT201:3.5" - nie atomowe!
);

-- Poprawna relacja w 1NF (wartości atomowe)
-- Już mamy: studenci, przedmioty, oceny

-- 10. OGRANICZENIA INTEGRALNOŚCI jako predykaty logiczne

-- Domain constraint: ∀t ∈ studenci: t[wiek] ∈ [0..150]
-- Key constraint: ∀t₁,t₂ ∈ studenci: t₁ ≠ t₂ ⇒ t₁[id_studenta] ≠ t₂[id_studenta]
-- Entity integrity: ∀t ∈ studenci: t[id_studenta] ≠ NULL
-- Referential integrity: ∀t ∈ oceny: ∃s ∈ studenci: t[id_studenta] = s[id_studenta]

-- Sprawdzanie integralności przez zapytania
-- Sprawdź integralność referencyjną
SELECT o.id_studenta, o.kod_przedmiotu
FROM oceny o
LEFT JOIN studenci s ON o.id_studenta = s.id_studenta
WHERE s.id_studenta IS NULL;  -- Powinno być puste

-- Sprawdź unikalność klucza głównego
SELECT id_studenta, COUNT(*)
FROM studenci
GROUP BY id_studenta
HAVING COUNT(*) > 1;  -- Powinno być puste

-- 11. METADATA O SCHEMACIE RELACYJNYM

-- Informacje o domenach/typach
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'studenci'
ORDER BY ordinal_position;

-- Informacje o kluczach
SELECT 
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.table_name = 'studenci';

-- Informacje o kluczach obcych
SELECT 
    kcu.column_name as foreign_key_column,
    ccu.table_name as referenced_table,
    ccu.column_name as referenced_column
FROM information_schema.key_column_usage kcu
JOIN information_schema.constraint_column_usage ccu
    ON kcu.constraint_name = ccu.constraint_name
WHERE kcu.table_name = 'oceny'
AND kcu.constraint_name LIKE '%fkey%';

-- 12. ZAMKNIĘCIE ALGEBRAICZNE

-- Model relacyjny jest zamknięty algebraicznie:
-- wynik operacji na relacjach to też relacja

-- Przykład: wynik JOIN'a to relacja
CREATE VIEW studenci_oceny AS
SELECT s.imie, s.nazwisko, o.wartosc, p.nazwa
FROM studenci s
JOIN oceny o ON s.id_studenta = o.id_studenta  
JOIN przedmioty p ON o.kod_przedmiotu = p.kod_przedmiotu;

-- Ta nowa relacja ma swój schemat i można na niej wykonywać operacje
SELECT AVG(wartosc) FROM studenci_oceny WHERE imie = 'Jan';
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Relacja = zbiór krotek (nie uporządkowana lista)
2. **UWAGA**: Klucz kandydujący musi być minimalny (superklucz może nie być)
3. **BŁĄD**: Mylenie domeny z typem danych (domena to zbiór wartości)
4. **WAŻNE**: Model relacyjny wymaga atomowości wartości (1NF)
5. **PUŁAPKA**: NULL nie należy do żadnej domeny (specjalna wartość)

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Relation/Tuple/Attribute** - relacja/krotka/atrybut
- **Domain** - domena atrybutu
- **Candidate/Primary key** - klucz kandydujący/główny
- **Foreign key** - klucz obcy
- **Referential integrity** - integralność referencyjna
- **Entity integrity** - integralność encji
- **Atomic values** - wartości atomowe
- **Relational schema** - schemat relacyjny

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **25-model-er** - przekształcenie ER → relacyjny
- **12-klucze-bazy-danych** - implementacja kluczy
- **01-integralnosc** - ograniczenia integralności
- **19-normalizacja** - normalizacja w modelu relacyjnym
- **23-algebra-relacji** - operacje na relacjach