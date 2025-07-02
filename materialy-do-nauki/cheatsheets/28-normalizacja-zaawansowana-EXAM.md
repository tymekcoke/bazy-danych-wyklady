# 🎯 NORMALIZACJA ZAAWANSOWANA - 4NF i 5NF - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Normalizacja zaawansowana to dalsze formy normalne wykraczające poza 3NF/BCNF:

1. **4NF (Czwarta Forma Normalna)** - eliminuje wielowartościowe zależności (MVD)
2. **5NF (Piąta Forma Normalna/PJNF)** - eliminuje zależności złączeniowe (JD)

Wielowartościowa zależność X →→ Y oznacza, że wartości Y są niezależne od innych atrybutów przy stałym X. Zależność złączeniowa JD wymaga, że relacja jest równa złączeniu swoich projekcji.

Te formy normalne rozwiązują anomalie związane z niezależnymi grupami wartości i skomplikowanymi zależnościami."

## ✍️ CO NAPISAĆ NA KARTCE

```
4NF i 5NF - DEFINICJE I ZASTOSOWANIA:

WIELOWARTOŚCIOWA ZALEŻNOŚĆ (MVD):
X →→ Y w relacji R oznacza:
• Dla każdej wartości X istnieje zbiór wartości Y
• Wartości Y są niezależne od pozostałych atrybutów Z
• Jeśli mamy krotki (x,y₁,z₁) i (x,y₂,z₂), 
  to muszą istnieć (x,y₁,z₂) i (x,y₂,z₁)

PRZYKŁAD MVD:
STUDENT_HOBBY_JĘZYK(student, hobby, język)
• Jan ma hobby: piłka, tenis
• Jan zna języki: angielski, niemiecki  
• To daje 4 krotki: (Jan,piłka,ang), (Jan,piłka,niem),
                    (Jan,tenis,ang), (Jan,tenis,niem)
• MVD: student →→ hobby, student →→ język

4NF DEFINICJA:
Relacja jest w 4NF jeśli:
• Jest w BCNF
• Nie zawiera nietrywianych MVD
  (lub wszystkie atrybuty są w lewej stronie MVD)

ZALEŻNOŚĆ ZŁĄCZENIOWA (JD):
JD: ⋈{R₁, R₂, ..., Rₙ} oznacza:
• Relacja R = R₁ ⋈ R₂ ⋈ ... ⋈ Rₙ  
• Gdzie Rᵢ to projekcje relacji R

5NF/PJNF DEFINICJA:
Relacja jest w 5NF jeśli:
• Jest w 4NF
• Każda zależność złączeniowa wynika z kluczy kandydujących

ALGORYTM NORMALIZACJI do 4NF:
1. Znajdź wszystkie MVD
2. Dla każdej nietrywialne MVD X →→ Y:
   - Podziel relację na R₁(X,Y) i R₂(X,Z)
   - gdzie Z = wszystkie atrybuty - X - Y
3. Powtarzaj dla każdej wynikowej relacji

PRZYKŁAD DEKOMPOZYCJI 4NF:
STUDENT_HOBBY_JĘZYK(student, hobby, język)
MVD: student →→ hobby, student →→ język

Dekompozycja:
R₁: STUDENT_HOBBY(student, hobby)
R₂: STUDENT_JĘZYK(student, język)

Obie tabele w 4NF, bezstratna dekompozycja.
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- DEMONSTRACJA NORMALIZACJI 4NF i 5NF

-- 1. PRZYKŁAD NARUSZENIA 4NF - WIELOWARTOŚCIOWE ZALEŻNOŚCI

-- Tabela naruszająca 4NF
CREATE TABLE student_hobby_jezyk_3nf (
    student_id INT,
    student_imie VARCHAR(50),
    hobby VARCHAR(50),
    jezyk VARCHAR(50),
    PRIMARY KEY (student_id, hobby, jezyk)
);

-- Dane pokazujące MVD
INSERT INTO student_hobby_jezyk_3nf VALUES 
-- Jan: hobby=piłka,tenis; języki=angielski,niemiecki
(1, 'Jan', 'piłka nożna', 'angielski'),
(1, 'Jan', 'piłka nożna', 'niemiecki'),
(1, 'Jan', 'tenis', 'angielski'),
(1, 'Jan', 'tenis', 'niemiecki'),

-- Anna: hobby=czytanie,pływanie; języki=angielski,francuski,hiszpański  
(2, 'Anna', 'czytanie', 'angielski'),
(2, 'Anna', 'czytanie', 'francuski'), 
(2, 'Anna', 'czytanie', 'hiszpański'),
(2, 'Anna', 'pływanie', 'angielski'),
(2, 'Anna', 'pływanie', 'francuski'),
(2, 'Anna', 'pływanie', 'hiszpański'),

-- Piotr: hobby=gry; języki=angielski
(3, 'Piotr', 'gry komputerowe', 'angielski');

-- Problem: redundancja - imię powtarza się niepotrzebnie
-- MVD: student_id →→ hobby, student_id →→ jezyk

-- 2. FUNKCJA SPRAWDZAJĄCA MVD

CREATE OR REPLACE FUNCTION sprawdz_mvd(
    tabela_name TEXT,
    x_attrs TEXT[],
    y_attrs TEXT[],
    z_attrs TEXT[]
) RETURNS BOOLEAN AS $$
DECLARE
    sql_query TEXT;
    violation_count INT;
BEGIN
    -- Sprawdź czy dla każdej kombinacji (x,y1,z1) i (x,y2,z2)
    -- istnieją krotki (x,y1,z2) i (x,y2,z1)
    sql_query := format('
        SELECT COUNT(*) FROM (
            SELECT DISTINCT %s as x_vals, %s as y_vals, %s as z_vals 
            FROM %I
        ) t1
        CROSS JOIN (
            SELECT DISTINCT %s as x_vals, %s as y_vals, %s as z_vals 
            FROM %I  
        ) t2
        WHERE t1.x_vals = t2.x_vals
        AND NOT EXISTS (
            SELECT 1 FROM %I t3 
            WHERE (%s) = t1.x_vals 
            AND (%s) = t1.y_vals 
            AND (%s) = t2.z_vals
        )',
        array_to_string(x_attrs, ','),
        array_to_string(y_attrs, ','), 
        array_to_string(z_attrs, ','),
        tabela_name,
        array_to_string(x_attrs, ','),
        array_to_string(y_attrs, ','),
        array_to_string(z_attrs, ','),
        tabela_name,
        tabela_name,
        array_to_string(x_attrs, ','),
        array_to_string(y_attrs, ','),
        array_to_string(z_attrs, ',')
    );
    
    EXECUTE sql_query INTO violation_count;
    
    IF violation_count = 0 THEN
        RAISE NOTICE 'MVD: % →→ % HOLDS', x_attrs, y_attrs;
        RETURN TRUE;
    ELSE
        RAISE NOTICE 'MVD: % →→ % DOES NOT HOLD (%s violations)', x_attrs, y_attrs, violation_count;
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Test MVD
SELECT sprawdz_mvd(
    'student_hobby_jezyk_3nf',
    ARRAY['student_id'],
    ARRAY['hobby'], 
    ARRAY['jezyk']
);

-- 3. NORMALIZACJA DO 4NF - DEKOMPOZYCJA

-- Tabela studentów (basic info)
CREATE TABLE studenci_4nf (
    student_id INT PRIMARY KEY,
    imie VARCHAR(50) NOT NULL
);

INSERT INTO studenci_4nf VALUES 
(1, 'Jan'),
(2, 'Anna'), 
(3, 'Piotr');

-- Dekompozycja MVD: student_id →→ hobby
CREATE TABLE student_hobby_4nf (
    student_id INT,
    hobby VARCHAR(50),
    PRIMARY KEY (student_id, hobby),
    FOREIGN KEY (student_id) REFERENCES studenci_4nf(student_id)
);

INSERT INTO student_hobby_4nf VALUES
(1, 'piłka nożna'),
(1, 'tenis'),
(2, 'czytanie'),
(2, 'pływanie'),
(3, 'gry komputerowe');

-- Dekompozycja MVD: student_id →→ jezyk  
CREATE TABLE student_jezyk_4nf (
    student_id INT,
    jezyk VARCHAR(50),
    poziom VARCHAR(20) DEFAULT 'podstawowy',
    PRIMARY KEY (student_id, jezyk),
    FOREIGN KEY (student_id) REFERENCES studenci_4nf(student_id)
);

INSERT INTO student_jezyk_4nf VALUES
(1, 'angielski', 'średniozaawansowany'),
(1, 'niemiecki', 'podstawowy'),
(2, 'angielski', 'zaawansowany'),
(2, 'francuski', 'średniozaawansowany'),
(2, 'hiszpański', 'podstawowy'),
(3, 'angielski', 'podstawowy');

-- 4. WERYFIKACJA BEZSTRATNOŚCI DEKOMPOZYCJI

-- Rekonstrukcja oryginalnej relacji przez JOIN
CREATE VIEW student_hobby_jezyk_rekonstrukcja AS
SELECT 
    s.student_id,
    s.imie,
    h.hobby,
    j.jezyk
FROM studenci_4nf s
JOIN student_hobby_4nf h ON s.student_id = h.student_id
JOIN student_jezyk_4nf j ON s.student_id = j.student_id;

-- Porównanie z oryginalną tabelą
SELECT 'Oryginalna' as wersja, COUNT(*) as liczba_krotek 
FROM student_hobby_jezyk_3nf
UNION ALL
SELECT 'Rekonstrukcja' as wersja, COUNT(*) as liczba_krotek
FROM student_hobby_jezyk_rekonstrukcja;

-- 5. PRZYKŁAD 5NF - ZALEŻNOŚCI ZŁĄCZENIOWE

-- Scenariusz: Firma, Produkt, Przedstawiciel
-- JD: Firma sprzedaje Produkty przez Przedstawicieli
CREATE TABLE firma_produkt_przedstawiciel_4nf (
    firma VARCHAR(50),
    produkt VARCHAR(50), 
    przedstawiciel VARCHAR(50),
    PRIMARY KEY (firma, produkt, przedstawiciel)
);

-- Dane z potencjalną JD
INSERT INTO firma_produkt_przedstawiciel_4nf VALUES
-- Firma A sprzedaje P1,P2 przez R1,R2
('Firma A', 'Produkt 1', 'Przedstawiciel 1'),
('Firma A', 'Produkt 1', 'Przedstawiciel 2'),
('Firma A', 'Produkt 2', 'Przedstawiciel 1'),
('Firma A', 'Produkt 2', 'Przedstawiciel 2'),

-- Firma B sprzedaje P1,P3 przez R2,R3  
('Firma B', 'Produkt 1', 'Przedstawiciel 2'),
('Firma B', 'Produkt 1', 'Przedstawiciel 3'),
('Firma B', 'Produkt 3', 'Przedstawiciel 2'),
('Firma B', 'Produkt 3', 'Przedstawiciel 3');

-- Możliwa dekompozycja do 5NF:
CREATE TABLE firma_produkt (
    firma VARCHAR(50),
    produkt VARCHAR(50),
    PRIMARY KEY (firma, produkt)
);

CREATE TABLE firma_przedstawiciel (
    firma VARCHAR(50),
    przedstawiciel VARCHAR(50),
    PRIMARY KEY (firma, przedstawiciel)  
);

CREATE TABLE produkt_przedstawiciel (
    produkt VARCHAR(50),
    przedstawiciel VARCHAR(50),
    PRIMARY KEY (produkt, przedstawiciel)
);

-- Wypełnienie dekompozycji
INSERT INTO firma_produkt 
SELECT DISTINCT firma, produkt FROM firma_produkt_przedstawiciel_4nf;

INSERT INTO firma_przedstawiciel
SELECT DISTINCT firma, przedstawiciel FROM firma_produkt_przedstawiciel_4nf;

INSERT INTO produkt_przedstawiciel  
SELECT DISTINCT produkt, przedstawiciel FROM firma_produkt_przedstawiciel_4nf;

-- 6. SPRAWDZENIE ZALEŻNOŚCI ZŁĄCZENIOWEJ

-- Rekonstrukcja przez JOIN trzech tabel
CREATE VIEW rekonstrukcja_5nf AS
SELECT fp.firma, fp.produkt, fr.przedstawiciel
FROM firma_produkt fp
JOIN firma_przedstawiciel fr ON fp.firma = fr.firma
JOIN produkt_przedstawiciel pr ON fp.produkt = pr.produkt 
    AND fr.przedstawiciel = pr.przedstawiciel;

-- Porównanie - czy JD zachodzi?
SELECT 'Oryginalna 4NF' as wersja, COUNT(*) as krotki
FROM firma_produkt_przedstawiciel_4nf
UNION ALL
SELECT 'Rekonstrukcja 5NF' as wersja, COUNT(*) as krotki  
FROM rekonstrukcja_5nf;

-- Sprawdzenie czy są identyczne
SELECT 'Różnica' as test, COUNT(*) as liczba_różnic
FROM (
    SELECT firma, produkt, przedstawiciel FROM firma_produkt_przedstawiciel_4nf
    EXCEPT 
    SELECT firma, produkt, przedstawiciel FROM rekonstrukcja_5nf
) roznice;

-- 7. ALGORYTM NORMALIZACJI - AUTOMATYZACJA

CREATE OR REPLACE FUNCTION znajdz_mvd_candidates(
    tabela_name TEXT
) RETURNS TABLE(
    determinant TEXT[],
    dependent TEXT[],
    remaining TEXT[]
) AS $$
DECLARE
    all_columns TEXT[];
    col1 TEXT;
    col2 TEXT;
    other_cols TEXT[];
BEGIN
    -- Pobierz wszystkie kolumny tabeli
    SELECT array_agg(column_name ORDER BY ordinal_position)
    INTO all_columns
    FROM information_schema.columns
    WHERE table_name = tabela_name;
    
    -- Sprawdź różne kombinacje MVD (uproszczona wersja)
    FOREACH col1 IN ARRAY all_columns LOOP
        FOREACH col2 IN ARRAY all_columns LOOP
            IF col1 != col2 THEN
                other_cols := array_remove(array_remove(all_columns, col1), col2);
                
                -- Sprawdź czy col1 →→ col2
                IF sprawdz_mvd(tabela_name, ARRAY[col1], ARRAY[col2], other_cols) THEN
                    determinant := ARRAY[col1];
                    dependent := ARRAY[col2]; 
                    remaining := other_cols;
                    RETURN NEXT;
                END IF;
            END IF;
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 8. PRAKTYCZNE ZASTOSOWANIA

-- Analiza redundancji w oryginalnej tabeli
SELECT 
    student_imie,
    COUNT(*) as liczba_krotek,
    COUNT(DISTINCT hobby) as liczba_hobby,
    COUNT(DISTINCT jezyk) as liczba_jezykow,
    COUNT(DISTINCT hobby) * COUNT(DISTINCT jezyk) as oczekiwane_krotki
FROM student_hobby_jezyk_3nf
GROUP BY student_id, student_imie;

-- Po normalizacji - brak redundancji
SELECT 
    s.imie,
    COUNT(h.hobby) as hobby_count,
    COUNT(j.jezyk) as jezyk_count,
    'Normalizacja 4NF' as status
FROM studenci_4nf s
LEFT JOIN student_hobby_4nf h ON s.student_id = h.student_id
LEFT JOIN student_jezyk_4nf j ON s.student_id = j.student_id  
GROUP BY s.student_id, s.imie;

-- 9. ANOMALIE I ICH ROZWIĄZANIE

-- Insert anomalia przed normalizacją:
-- Aby dodać nowe hobby dla Jana, trzeba dodać N krotek (dla każdego języka)
-- INSERT INTO student_hobby_jezyk_3nf VALUES 
-- (1, 'Jan', 'szachy', 'angielski'),
-- (1, 'Jan', 'szachy', 'niemiecki'); -- Musimy pamiętać o wszystkich językach!

-- Po normalizacji - jedna krotka:
INSERT INTO student_hobby_4nf VALUES (1, 'szachy');

-- Update anomalia przed normalizacją:
-- Zmiana imienia wymaga update wielu krotek
-- UPDATE student_hobby_jezyk_3nf SET student_imie = 'Jan Kowalski' WHERE student_id = 1;

-- Po normalizacji - jeden update:
UPDATE studenci_4nf SET imie = 'Jan Kowalski' WHERE student_id = 1;

-- 10. MONITORING ZGODNOŚCI Z 4NF/5NF

-- Trigger sprawdzający spójność przy INSERT
CREATE OR REPLACE FUNCTION validate_4nf_consistency()
RETURNS TRIGGER AS $$
BEGIN
    -- Sprawdź czy dodawanie nowego hobby nie narusza MVD
    -- (uproszczona implementacja)
    
    -- Jeśli student ma już języki, sprawdź spójność
    IF EXISTS (SELECT 1 FROM student_jezyk_4nf WHERE student_id = NEW.student_id) THEN
        -- Weryfikacja czy nie ma niespójności w danych
        RAISE NOTICE 'Dodano hobby dla studenta z istniejącymi językami - sprawdź spójność';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_4nf_consistency
    AFTER INSERT ON student_hobby_4nf
    FOR EACH ROW
    EXECUTE FUNCTION validate_4nf_consistency();

-- 11. ANALIZA WYDAJNOŚCI NORMALIZACJI

-- Porównanie liczby krotek
SELECT 
    'Przed normalizacją' as stan,
    (SELECT COUNT(*) FROM student_hobby_jezyk_3nf) as krotki,
    'Jedna tabela' as struktura
UNION ALL
SELECT 
    'Po normalizacji 4NF' as stan,
    (SELECT COUNT(*) FROM studenci_4nf) + 
    (SELECT COUNT(*) FROM student_hobby_4nf) + 
    (SELECT COUNT(*) FROM student_jezyk_4nf) as krotki,
    'Trzy tabele' as struktura;

-- Test wydajności JOIN vs denormalizacja
EXPLAIN ANALYZE
SELECT s.imie, h.hobby, j.jezyk
FROM studenci_4nf s
JOIN student_hobby_4nf h ON s.student_id = h.student_id
JOIN student_jezyk_4nf j ON s.student_id = j.student_id
WHERE s.student_id = 1;

-- vs

EXPLAIN ANALYZE  
SELECT student_imie, hobby, jezyk
FROM student_hobby_jezyk_3nf
WHERE student_id = 1;
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: MVD X →→ Y nie oznacza FD X → Y
2. **UWAGA**: 4NF może wymagać więcej JOIN'ów w zapytaniach
3. **BŁĄD**: Mylenie MVD z zwykłymi zależnościami funkcyjnymi
4. **WAŻNE**: Nie wszystkie relacje wymagają normalizacji do 4NF/5NF
5. **PUŁAPKA**: JD może prowadzić do nadmiernej dekompozycji

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Multivalued dependency (MVD)** - wielowartościowa zależność
- **Join dependency (JD)** - zależność złączeniowa  
- **Fourth/Fifth Normal Form** - czwarta/piąta forma normalna
- **Lossless decomposition** - bezstratna dekompozycja
- **Independent attributes** - niezależne atrybuty
- **PJNF** - Project-Join Normal Form
- **Redundancy elimination** - eliminacja redundancji
- **Advanced normalization** - zaawansowana normalizacja

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **19-normalizacja** - podstawowe formy normalne
- **27-zaleznosci-funkcyjne** - FD vs MVD
- **05-twierdzenie-heatha** - dekompozycja relacji
- **26-model-relacyjny** - teoria relacji
- **42-optymalizacja-wydajnosci** - koszt normalizacji