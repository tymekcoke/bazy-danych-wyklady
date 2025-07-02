# ➡️ ZALEŻNOŚCI FUNKCYJNE - TEORIA I ZASTOSOWANIA - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekunds)

"Zależność funkcyjna X → Y oznacza, że wartości atrybutów X jednoznacznie determinują wartości atrybutów Y. Innymi słowy, dla każdej wartości X istnieje dokładnie jedna wartość Y.

Kluczowe pojęcia:
1. **Trywialna** - Y ⊆ X (np. {A,B} → A)
2. **Pełna** - nie można usunąć żadnego atrybutu z X  
3. **Przechodnia** - X → Y i Y → Z implikuje X → Z
4. **Domknięcie** - wszystkie atrybuty wynikające z X

Zależności funkcyjne są podstawą normalizacji i identyfikacji kluczy."

## ✍️ CO NAPISAĆ NA KARTCE

```
ZALEŻNOŚCI FUNKCYJNE (FD) - DEFINICJE:

DEFINICJA FORMALNA:
X → Y (X determinuje Y) ⟺
∀t₁,t₂ ∈ r: t₁[X] = t₂[X] ⟹ t₁[Y] = t₂[Y]

PRZYKŁADY:
student_id → {imie, nazwisko, data_urodzenia}
pesel → {imie, nazwisko, data_urodzenia, adres}
{student_id, przedmiot_id} → ocena

TYPY ZALEŻNOŚCI:

1. TRYWIALNA: Y ⊆ X
   {A,B} → A  ✓ (zawsze prawdziwa)
   {A,B} → {A,B}  ✓ (zawsze prawdziwa)

2. NIETRYWIALNA: Y ⊄ X  
   A → B gdzie B ∉ X

3. PEŁNA: X → Y i ∄X' ⊂ X: X' → Y
   {student_id, przedmiot} → ocena (pełna)
   {student_id, przedmiot} → student_imie (niepełna, bo student_id → student_imie)

4. PRZECHODNIA: X → Y ∧ Y → Z ⟹ X → Z
   student_id → wydział_id → nazwa_wydziału
   ⟹ student_id → nazwa_wydziału

AKSJOMATY ARMSTRONGA:
A1. Refleksywność: Y ⊆ X ⟹ X → Y
A2. Augmentacja: X → Y ⟹ XZ → YZ  
A3. Przechodniość: X → Y ∧ Y → Z ⟹ X → Z

POCHODNE REGUŁY:
R1. Union: X → Y ∧ X → Z ⟹ X → YZ
R2. Decomposition: X → YZ ⟹ X → Y ∧ X → Z
R3. Pseudoprzechodniość: X → Y ∧ WY → Z ⟹ WX → Z

DOMKNIĘCIE X⁺:
Zbiór wszystkich atrybutów determinowanych przez X
Algorytm:
1. result := X
2. while (result się zmienia) do
3.   for each FD: A → B in F do
4.     if A ⊆ result then result := result ∪ B
5. return result

KLUCZ KANDYDUJĄCY:
K jest kluczem ⟺ K⁺ = R (wszystkie atrybuty)
                ∧ ∄K' ⊂ K: (K')⁺ = R (minimalny)
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- DEMONSTRACJA ZALEŻNOŚCI FUNKCYJNYCH

-- Tabela testowa z różnymi zależnościami funkcyjnymi
CREATE TABLE student_przedmiot_fd (
    student_id INT,
    pesel VARCHAR(11),
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    data_urodzenia DATE,
    adres TEXT,
    przedmiot_id INT,
    nazwa_przedmiotu VARCHAR(100),
    prowadzacy_id INT,
    nazwisko_prowadzacego VARCHAR(50),
    ocena DECIMAL(3,1),
    data_egzaminu DATE,
    sala VARCHAR(10)
);

-- Dane testowe pokazujące zależności funkcyjne
INSERT INTO student_przedmiot_fd VALUES 
(1, '90010112345', 'Jan', 'Kowalski', '1990-01-01', 'Warszawa ul. A 1', 101, 'Bazy Danych', 201, 'Nowak', 4.5, '2024-01-15', 'A101'),
(1, '90010112345', 'Jan', 'Kowalski', '1990-01-01', 'Warszawa ul. A 1', 102, 'Algorytmy', 202, 'Wiśniewski', 4.0, '2024-01-18', 'B205'),
(2, '91020223456', 'Anna', 'Nowakowa', '1991-02-02', 'Kraków ul. B 2', 101, 'Bazy Danych', 201, 'Nowak', 5.0, '2024-01-15', 'A101'),
(2, '91020223456', 'Anna', 'Nowakowa', '1991-02-02', 'Kraków ul. B 2', 103, 'Matematyka', 203, 'Kowalczyk', 3.5, '2024-01-20', 'C301'),
(3, '92030334567', 'Piotr', 'Zieliński', '1992-03-03', 'Gdańsk ul. C 3', 102, 'Algorytmy', 202, 'Wiśniewski', 4.5, '2024-01-18', 'B205');

-- 1. IDENTYFIKACJA ZALEŻNOŚCI FUNKCYJNYCH

-- Funkcja sprawdzająca czy X → Y
CREATE OR REPLACE FUNCTION sprawdz_fd(
    tabela_name TEXT,
    determinant TEXT[],
    dependent TEXT[]
) RETURNS BOOLEAN AS $$
DECLARE
    sql_query TEXT;
    violation_count INT;
BEGIN
    -- Sprawdź czy istnieją wiersze z tymi samymi wartościami X ale różnymi Y
    sql_query := format(
        'SELECT COUNT(*) FROM (
            SELECT %s, COUNT(DISTINCT (%s)) as distinct_vals
            FROM %I
            GROUP BY %s
            HAVING COUNT(DISTINCT (%s)) > 1
        ) violations',
        array_to_string(determinant, ', '),
        array_to_string(dependent, ', '),
        tabela_name,
        array_to_string(determinant, ', '),
        array_to_string(dependent, ', ')
    );
    
    EXECUTE sql_query INTO violation_count;
    
    IF violation_count = 0 THEN
        RAISE NOTICE 'FD: % → % HOLDS', determinant, dependent;
        RETURN TRUE;
    ELSE
        RAISE NOTICE 'FD: % → % DOES NOT HOLD (%s violations)', determinant, dependent, violation_count;
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Test zależności funkcyjnych
SELECT sprawdz_fd('student_przedmiot_fd', ARRAY['student_id'], ARRAY['imie', 'nazwisko']);  -- TRUE
SELECT sprawdz_fd('student_przedmiot_fd', ARRAY['pesel'], ARRAY['student_id']);  -- TRUE
SELECT sprawdz_fd('student_przedmiot_fd', ARRAY['przedmiot_id'], ARRAY['nazwa_przedmiotu']);  -- TRUE
SELECT sprawdz_fd('student_przedmiot_fd', ARRAY['prowadzacy_id'], ARRAY['nazwisko_prowadzacego']);  -- TRUE
SELECT sprawdz_fd('student_przedmiot_fd', ARRAY['student_id', 'przedmiot_id'], ARRAY['ocena']);  -- TRUE
SELECT sprawdz_fd('student_przedmiot_fd', ARRAY['data_egzaminu', 'sala'], ARRAY['przedmiot_id']);  -- TRUE
SELECT sprawdz_fd('student_przedmiot_fd', ARRAY['imie'], ARRAY['nazwisko']);  -- FALSE

-- 2. IMPLEMENTACJA DOMKNIĘCIA (CLOSURE)

CREATE OR REPLACE FUNCTION closure_fd(
    attributes TEXT[],
    functional_dependencies TEXT[][],  -- Array of [determinant, dependent] pairs
    all_attributes TEXT[]
) RETURNS TEXT[] AS $$
DECLARE
    result TEXT[];
    changed BOOLEAN;
    fd TEXT[];
    determinant_attrs TEXT[];
    dependent_attrs TEXT[];
BEGIN
    result := attributes;
    
    LOOP
        changed := FALSE;
        
        -- Sprawdź każdą zależność funkcyjną
        FOREACH fd SLICE 1 IN ARRAY functional_dependencies LOOP
            determinant_attrs := string_to_array(fd[1], ',');
            dependent_attrs := string_to_array(fd[2], ',');
            
            -- Jeśli determinant jest podzbiorem result, dodaj dependent
            IF determinant_attrs <@ result AND NOT (dependent_attrs <@ result) THEN
                result := array(SELECT DISTINCT unnest(result || dependent_attrs));
                changed := TRUE;
            END IF;
        END LOOP;
        
        EXIT WHEN NOT changed;
    END LOOP;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Test domknięcia
-- FDs: student_id → {imie,nazwisko}, pesel → student_id, przedmiot_id → nazwa_przedmiotu
SELECT closure_fd(
    ARRAY['student_id'],  -- początkowy zbiór
    ARRAY[
        ARRAY['student_id', 'imie,nazwisko,data_urodzenia,adres'],
        ARRAY['pesel', 'student_id'],
        ARRAY['przedmiot_id', 'nazwa_przedmiotu,prowadzacy_id'],
        ARRAY['prowadzacy_id', 'nazwisko_prowadzacego'],
        ARRAY['student_id,przedmiot_id', 'ocena,data_egzaminu'],
        ARRAY['data_egzaminu,sala', 'przedmiot_id']
    ],
    ARRAY['student_id','pesel','imie','nazwisko','data_urodzenia','adres','przedmiot_id','nazwa_przedmiotu','prowadzacy_id','nazwisko_prowadzacego','ocena','data_egzaminu','sala']
);

-- 3. ZNAJDOWANIE KLUCZY KANDYDUJĄCYCH

CREATE OR REPLACE FUNCTION find_candidate_keys(
    all_attributes TEXT[],
    functional_dependencies TEXT[][]
) RETURNS TEXT[][] AS $$
DECLARE
    candidate_keys TEXT[][];
    subset TEXT[];
    closure_result TEXT[];
    is_minimal BOOLEAN;
    smaller_subset TEXT[];
BEGIN
    candidate_keys := ARRAY[]::TEXT[][];
    
    -- Generuj wszystkie niepuste podzbiory atrybutów (uproszczona wersja)
    -- W praktyce używa się bardziej efektywnych algorytmów
    
    -- Sprawdź pojedyncze atrybuty
    FOR i IN 1..array_length(all_attributes, 1) LOOP
        subset := ARRAY[all_attributes[i]];
        closure_result := closure_fd(subset, functional_dependencies, all_attributes);
        
        IF array_length(closure_result, 1) = array_length(all_attributes, 1) AND
           closure_result @> all_attributes THEN
            candidate_keys := candidate_keys || ARRAY[subset];
        END IF;
    END LOOP;
    
    -- Sprawdź pary atrybutów (jeśli nie znaleziono pojedynczych kluczy)
    IF array_length(candidate_keys, 1) = 0 THEN
        FOR i IN 1..array_length(all_attributes, 1) LOOP
            FOR j IN i+1..array_length(all_attributes, 1) LOOP
                subset := ARRAY[all_attributes[i], all_attributes[j]];
                closure_result := closure_fd(subset, functional_dependencies, all_attributes);
                
                IF array_length(closure_result, 1) = array_length(all_attributes, 1) AND
                   closure_result @> all_attributes THEN
                    candidate_keys := candidate_keys || ARRAY[subset];
                END IF;
            END LOOP;
        END LOOP;
    END IF;
    
    RETURN candidate_keys;
END;
$$ LANGUAGE plpgsql;

-- 4. DEMONSTRACJA AKSJOMATÓW ARMSTRONGA

-- A1. Refleksywność: Y ⊆ X ⟹ X → Y
-- {student_id, imie} → student_id (zawsze prawda)
SELECT sprawdz_fd('student_przedmiot_fd', ARRAY['student_id', 'imie'], ARRAY['student_id']);

-- A2. Augmentacja: X → Y ⟹ XZ → YZ
-- student_id → imie ⟹ {student_id, przedmiot_id} → {imie, przedmiot_id}
SELECT sprawdz_fd('student_przedmiot_fd', ARRAY['student_id'], ARRAY['imie']);
SELECT sprawdz_fd('student_przedmiot_fd', ARRAY['student_id', 'przedmiot_id'], ARRAY['imie', 'przedmiot_id']);

-- A3. Przechodniość: X → Y ∧ Y → Z ⟹ X → Z
-- pesel → student_id ∧ student_id → imie ⟹ pesel → imie
SELECT sprawdz_fd('student_przedmiot_fd', ARRAY['pesel'], ARRAY['student_id']);
SELECT sprawdz_fd('student_przedmiot_fd', ARRAY['student_id'], ARRAY['imie']);
SELECT sprawdz_fd('student_przedmiot_fd', ARRAY['pesel'], ARRAY['imie']);  -- wynika z przechodniości

-- 5. WYKRYWANIE REDUNDANCJI PRZEZ FD

-- Funkcja znajdująca redundantne atrybuty
CREATE OR REPLACE FUNCTION znajdz_redundantne_atrybuty(
    tabela_name TEXT,
    funkcyjne_zaleznosci TEXT[][]
) RETURNS TABLE(atrybut TEXT, determinowany_przez TEXT[]) AS $$
DECLARE
    attr TEXT;
    determinants TEXT[];
    closure_result TEXT[];
BEGIN
    -- Sprawdź każdy atrybut czy nie jest determinowany przez inne
    FOR attr IN 
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = tabela_name
    LOOP
        -- Znajdź atrybuty które determinują ten atrybut
        FOR i IN 1..array_length(funkcyjne_zaleznosci, 1) LOOP
            IF attr = ANY(string_to_array(funkcyjne_zaleznosci[i][2], ',')) THEN
                determinants := string_to_array(funkcyjne_zaleznosci[i][1], ',');
                RETURN QUERY SELECT attr, determinants;
            END IF;
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 6. NORMALIZACJA OPARTA NA FD

-- Tworzenie tabel znormalizowanych na podstawie FD

-- 1. Tabela studenci (student_id → {pesel, imie, nazwisko, data_urodzenia, adres})
CREATE TABLE studenci_normalized AS
SELECT DISTINCT student_id, pesel, imie, nazwisko, data_urodzenia, adres
FROM student_przedmiot_fd;

ALTER TABLE studenci_normalized ADD PRIMARY KEY (student_id);

-- 2. Tabela przedmioty (przedmiot_id → {nazwa_przedmiotu, prowadzacy_id})
CREATE TABLE przedmioty_normalized AS
SELECT DISTINCT przedmiot_id, nazwa_przedmiotu, prowadzacy_id
FROM student_przedmiot_fd;

ALTER TABLE przedmioty_normalized ADD PRIMARY KEY (przedmiot_id);

-- 3. Tabela prowadzący (prowadzacy_id → nazwisko_prowadzacego)
CREATE TABLE prowadzacy_normalized AS
SELECT DISTINCT prowadzacy_id, nazwisko_prowadzacego
FROM student_przedmiot_fd;

ALTER TABLE prowadzacy_normalized ADD PRIMARY KEY (prowadzacy_id);

-- 4. Tabela oceny ({student_id, przedmiot_id} → {ocena, data_egzaminu, sala})
CREATE TABLE oceny_normalized AS
SELECT DISTINCT student_id, przedmiot_id, ocena, data_egzaminu, sala
FROM student_przedmiot_fd;

ALTER TABLE oceny_normalized ADD PRIMARY KEY (student_id, przedmiot_id);

-- Dodanie kluczy obcych
ALTER TABLE przedmioty_normalized 
ADD FOREIGN KEY (prowadzacy_id) REFERENCES prowadzacy_normalized(prowadzacy_id);

ALTER TABLE oceny_normalized 
ADD FOREIGN KEY (student_id) REFERENCES studenci_normalized(student_id),
ADD FOREIGN KEY (przedmiot_id) REFERENCES przedmioty_normalized(przedmiot_id);

-- 7. MINIMALNA PRZYKRYWA (MINIMAL COVER)

-- Funkcja redukująca zbiór FD do minimalnej przykrywy
CREATE OR REPLACE FUNCTION minimal_cover(
    functional_dependencies TEXT[][]
) RETURNS TEXT[][] AS $$
DECLARE
    result TEXT[][];
    fd TEXT[];
    reduced_left TEXT[];
    attr TEXT;
    temp_fds TEXT[][];
BEGIN
    result := functional_dependencies;
    
    -- Krok 1: Rozbij prawą stronę na pojedyncze atrybuty
    -- (uproszczenie - zakładamy że już są rozbite)
    
    -- Krok 2: Usuń redundantne atrybuty z lewej strony
    FOR i IN 1..array_length(result, 1) LOOP
        reduced_left := string_to_array(result[i][1], ',');
        
        FOREACH attr IN ARRAY reduced_left LOOP
            -- Sprawdź czy można usunąć attr z lewej strony
            temp_fds := result;
            temp_fds[i][1] := array_to_string(array_remove(reduced_left, attr), ',');
            
            -- Jeśli nadal można wydedukować oryginalną FD, usuń attr
            -- (uproszczenie algorytmu)
        END LOOP;
    END LOOP;
    
    -- Krok 3: Usuń redundantne FD
    -- (uproszczenie - pominięte dla czytelności)
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 8. ANALIZA ZŁOŻONYCH PRZYPADKÓW

-- Przypadek z zależnościami przechodnimi
CREATE TABLE przechodnie_fd (
    student_id INT,
    kierunek_id INT,
    nazwa_kierunku VARCHAR(100),
    wydzial_id INT,
    nazwa_wydzialu VARCHAR(100)
);

INSERT INTO przechodnie_fd VALUES 
(1, 10, 'Informatyka', 1, 'Wydział MIM'),
(2, 10, 'Informatyka', 1, 'Wydział MIM'),
(3, 20, 'Matematyka', 1, 'Wydział MIM'),
(4, 30, 'Fizyka', 2, 'Wydział Fizyki');

-- FD: student_id → kierunek_id → {nazwa_kierunku, wydzial_id} → nazwa_wydzialu
-- Zależności przechodnie: student_id → kierunek_id → wydzial_id → nazwa_wydzialu

SELECT sprawdz_fd('przechodnie_fd', ARRAY['student_id'], ARRAY['kierunek_id']);
SELECT sprawdz_fd('przechodnie_fd', ARRAY['kierunek_id'], ARRAY['nazwa_kierunku', 'wydzial_id']);
SELECT sprawdz_fd('przechodnie_fd', ARRAY['wydzial_id'], ARRAY['nazwa_wydzialu']);
-- Wynikająca z przechodniości:
SELECT sprawdz_fd('przechodnie_fd', ARRAY['student_id'], ARRAY['nazwa_wydzialu']);

-- 9. MONITORING I WALIDACJA FD W RUNTIME

-- Trigger sprawdzający zachowanie FD przy INSERT/UPDATE
CREATE OR REPLACE FUNCTION validate_fd_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Sprawdź czy student_id → imie jest zachowane
    IF EXISTS (
        SELECT 1 FROM student_przedmiot_fd 
        WHERE student_id = NEW.student_id 
        AND imie != NEW.imie
    ) THEN
        RAISE EXCEPTION 'Naruszenie FD: student_id → imie';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_validate_fd
    BEFORE INSERT OR UPDATE ON student_przedmiot_fd
    FOR EACH ROW
    EXECUTE FUNCTION validate_fd_trigger();
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: X → Y nie oznacza Y → X (nie jest symetryczne)
2. **UWAGA**: Zależność trywialna (Y ⊆ X) jest zawsze prawdziwa
3. **BŁĄD**: Mylenie zależności pełnej z niepełnej (częściowej)
4. **WAŻNE**: Domknięcie X+ zawiera X (refleksywność)
5. **PUŁAPKA**: Klucz kandydujący musi być minimalny i jednoznacznie determinować wszystkie atrybuty

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Functional dependency** - zależność funkcyjna
- **Armstrong's axioms** - aksjomaty Armstronga
- **Closure** - domknięcie
- **Trivial/Non-trivial** - trywialna/nietrywialna
- **Full/Partial dependency** - zależność pełna/częściowa  
- **Transitive dependency** - zależność przechodnia
- **Minimal cover** - minimalna przykrywa
- **Candidate key** - klucz kandydujący

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **19-normalizacja** - FD jako podstawa normalizacji
- **05-twierdzenie-heatha** - dekompozycja a FD
- **26-model-relacyjny** - FD w modelu relacyjnym
- **12-klucze-bazy-danych** - identyfikacja kluczy przez FD
- **28-normalizacja-zaawansowana** - MVD i JD