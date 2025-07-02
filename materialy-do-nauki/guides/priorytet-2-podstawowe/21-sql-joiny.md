# SQL JOINy - wszystkie rodzaje

## Definicja JOIN

**JOIN** to operacja łączenia **danych z dwóch lub więcej tabel** na podstawie **związku między kolumnami** w tych tabelach.

### Cel JOIN'ów:
- **Normalizacja** - dane podzielone na wiele tabel
- **Rekombiancja** - łączenie danych dla zapytań
- **Relacyjny model** - związki między encjami

## Przykładowe tabele

### Dane testowe:
```sql
-- Tabela klientów
CREATE TABLE klienci (
    id_klienta INT PRIMARY KEY,
    nazwa VARCHAR(100),
    miasto VARCHAR(50)
);

INSERT INTO klienci VALUES 
(1, 'Firma ABC', 'Warszawa'),
(2, 'Firma XYZ', 'Kraków'),
(3, 'Firma QWE', 'Gdańsk'),
(4, 'Firma BNM', 'Wrocław');

-- Tabela zamówień
CREATE TABLE zamowienia (
    id_zamowienia INT PRIMARY KEY,
    id_klienta INT,
    data_zamowienia DATE,
    wartosc DECIMAL(10,2)
);

INSERT INTO zamowienia VALUES 
(101, 1, '2024-01-15', 1500.00),
(102, 1, '2024-02-20', 2300.00),
(103, 2, '2024-01-10', 890.00),
(104, 5, '2024-03-05', 1200.00),  -- Klient nie istnieje!
(105, NULL, '2024-03-10', 500.00); -- Brak klienta

-- Tabela produktów
CREATE TABLE produkty (
    id_produktu INT PRIMARY KEY,
    nazwa VARCHAR(100),
    cena DECIMAL(10,2)
);

INSERT INTO produkty VALUES 
(1, 'Laptop', 3000.00),
(2, 'Mysz', 50.00),
(3, 'Monitor', 800.00),
(4, 'Klawiatura', 150.00);

-- Tabela pozycji zamówień
CREATE TABLE pozycje_zamowien (
    id_zamowienia INT,
    id_produktu INT,
    ilosc INT,
    PRIMARY KEY (id_zamowienia, id_produktu)
);

INSERT INTO pozycje_zamowien VALUES 
(101, 1, 1),  -- Zamówienie 101: 1x Laptop
(101, 2, 2),  -- Zamówienie 101: 2x Mysz
(102, 3, 1),  -- Zamówienie 102: 1x Monitor
(103, 2, 5),  -- Zamówienie 103: 5x Mysz
(106, 1, 1);  -- Zamówienie nie istnieje!
```

## INNER JOIN

### Definicja:
**INNER JOIN** zwraca **tylko te rekordy**, które mają **pasujące wartości w obu tabelach**.

### Składnia:
```sql
SELECT kolumny
FROM tabela1 t1
INNER JOIN tabela2 t2 ON t1.klucz = t2.klucz;

-- Alternatywne składnie:
SELECT kolumny
FROM tabela1 t1
JOIN tabela2 t2 ON t1.klucz = t2.klucz;  -- INNER jest domyślne

SELECT kolumny  
FROM tabela1 t1, tabela2 t2
WHERE t1.klucz = t2.klucz;  -- Starszy styl
```

### Przykłady INNER JOIN:
```sql
-- Klienci z ich zamówieniami
SELECT 
    k.nazwa,
    z.id_zamowienia,
    z.data_zamowienia,
    z.wartosc
FROM klienci k
INNER JOIN zamowienia z ON k.id_klienta = z.id_klienta;

-- Wynik:
-- nazwa      | id_zamowienia | data_zamowienia | wartosc
-- Firma ABC  | 101          | 2024-01-15      | 1500.00
-- Firma ABC  | 102          | 2024-02-20      | 2300.00  
-- Firma XYZ  | 103          | 2024-01-10      | 890.00

-- Zauważ: 
-- - Firma QWE i Firma BNM nie mają zamówień → nie są w wyniku
-- - Zamówienia 104 i 105 nie mają klientów → nie są w wyniku
```

### INNER JOIN z wieloma tabelami:
```sql
-- Szczegóły zamówień z produktami
SELECT 
    k.nazwa as klient,
    z.id_zamowienia,
    p.nazwa as produkt,
    pz.ilosc,
    p.cena,
    (pz.ilosc * p.cena) as wartosc_pozycji
FROM klienci k
INNER JOIN zamowienia z ON k.id_klienta = z.id_klienta
INNER JOIN pozycje_zamowien pz ON z.id_zamowienia = pz.id_zamowienia
INNER JOIN produkty p ON pz.id_produktu = p.id_produktu
ORDER BY k.nazwa, z.id_zamowienia;
```

## LEFT OUTER JOIN (LEFT JOIN)

### Definicja:
**LEFT JOIN** zwraca **wszystkie rekordy z lewej tabeli** oraz **pasujące rekordy z prawej tabeli**. Jeśli nie ma pasującego rekordu po prawej stronie, wartości są **NULL**.

### Przykład LEFT JOIN:
```sql
-- Wszyscy klienci i ich zamówienia (także ci bez zamówień)
SELECT 
    k.nazwa,
    z.id_zamowienia,
    z.data_zamowienia,
    z.wartosc
FROM klienci k
LEFT JOIN zamowienia z ON k.id_klienta = z.id_klienta
ORDER BY k.nazwa;

-- Wynik:
-- nazwa      | id_zamowienia | data_zamowienia | wartosc
-- Firma ABC  | 101          | 2024-01-15      | 1500.00
-- Firma ABC  | 102          | 2024-02-20      | 2300.00
-- Firma BNM  | NULL         | NULL            | NULL     ← Brak zamówień
-- Firma QWE  | NULL         | NULL            | NULL     ← Brak zamówień  
-- Firma XYZ  | 103          | 2024-01-10      | 890.00
```

### Znajdowanie rekordów bez powiązań:
```sql
-- Klienci którzy nie złożyli żadnych zamówień
SELECT k.nazwa
FROM klienci k
LEFT JOIN zamowienia z ON k.id_klienta = z.id_klienta
WHERE z.id_klienta IS NULL;

-- Wynik: Firma QWE, Firma BNM
```

### LEFT JOIN z agregacją:
```sql
-- Liczba zamówień dla każdego klienta
SELECT 
    k.nazwa,
    COUNT(z.id_zamowienia) as liczba_zamowien,
    COALESCE(SUM(z.wartosc), 0) as suma_zamowien
FROM klienci k
LEFT JOIN zamowienia z ON k.id_klienta = z.id_klienta
GROUP BY k.id_klienta, k.nazwa
ORDER BY suma_zamowien DESC;
```

## RIGHT OUTER JOIN (RIGHT JOIN)

### Definicja:
**RIGHT JOIN** zwraca **wszystkie rekordy z prawej tabeli** oraz **pasujące rekordy z lewej tabeli**. To **odwrotność LEFT JOIN**.

### Przykład RIGHT JOIN:
```sql
-- Wszystkie zamówienia i ich klienci (także zamówienia bez klientów)
SELECT 
    k.nazwa,
    z.id_zamowienia,
    z.data_zamowienia,
    z.wartosc
FROM klienci k
RIGHT JOIN zamowienia z ON k.id_klienta = z.id_klienta
ORDER BY z.id_zamowienia;

-- Wynik:
-- nazwa      | id_zamowienia | data_zamowienia | wartosc
-- Firma ABC  | 101          | 2024-01-15      | 1500.00
-- Firma ABC  | 102          | 2024-02-20      | 2300.00
-- Firma XYZ  | 103          | 2024-01-10      | 890.00
-- NULL       | 104          | 2024-03-05      | 1200.00  ← Klient nie istnieje
-- NULL       | 105          | 2024-03-10      | 500.00   ← Brak klienta
```

### Uwaga praktyczna:
RIGHT JOIN jest **rzadko używany** - zwykle przepisuje się go jako LEFT JOIN zamieniając kolejność tabel:
```sql
-- Te zapytania są równoważne:
SELECT * FROM klienci k RIGHT JOIN zamowienia z ON k.id_klienta = z.id_klienta;
SELECT * FROM zamowienia z LEFT JOIN klienci k ON z.id_klienta = k.id_klienta;
```

## FULL OUTER JOIN (FULL JOIN)

### Definicja:
**FULL JOIN** zwraca **wszystkie rekordy z obu tabel**. Gdy nie ma pasującego rekordu, wartości są **NULL**.

### Przykład FULL JOIN:
```sql
-- PostgreSQL, SQL Server
SELECT 
    k.nazwa,
    z.id_zamowienia,
    z.data_zamowienia,
    z.wartosc
FROM klienci k
FULL OUTER JOIN zamowienia z ON k.id_klienta = z.id_klienta
ORDER BY k.nazwa, z.id_zamowienia;

-- Wynik (wszystkie klienci + wszystkie zamówienia):
-- nazwa      | id_zamowienia | data_zamowienia | wartosc
-- Firma ABC  | 101          | 2024-01-15      | 1500.00
-- Firma ABC  | 102          | 2024-02-20      | 2300.00
-- Firma BNM  | NULL         | NULL            | NULL     ← Klient bez zamówień
-- Firma QWE  | NULL         | NULL            | NULL     ← Klient bez zamówień
-- Firma XYZ  | 103          | 2024-01-10      | 890.00
-- NULL       | 104          | 2024-03-05      | 1200.00  ← Zamówienie bez klienta
-- NULL       | 105          | 2024-03-10      | 500.00   ← Zamówienie bez klienta
```

### FULL JOIN w MySQL (emulacja):
```sql
-- MySQL nie ma FULL JOIN - można emulować:
SELECT k.nazwa, z.id_zamowienia, z.data_zamowienia, z.wartosc
FROM klienci k LEFT JOIN zamowienia z ON k.id_klienta = z.id_klienta
UNION
SELECT k.nazwa, z.id_zamowienia, z.data_zamowienia, z.wartosc  
FROM klienci k RIGHT JOIN zamowienia z ON k.id_klienta = z.id_klienta
WHERE k.id_klienta IS NULL;
```

## CROSS JOIN (Cartesian Product)

### Definicja:
**CROSS JOIN** zwraca **iloczyn kartezjański** - każdy rekord z pierwszej tabeli jest łączony z każdym rekordem z drugiej tabeli.

### Składnia:
```sql
SELECT kolumny
FROM tabela1
CROSS JOIN tabela2;

-- Alternatywnie:
SELECT kolumny
FROM tabela1, tabela2;  -- Bez WHERE
```

### Przykład CROSS JOIN:
```sql
-- Każdy klient z każdym produktem
SELECT 
    k.nazwa as klient,
    p.nazwa as produkt,
    p.cena
FROM klienci k
CROSS JOIN produkty p
ORDER BY k.nazwa, p.nazwa;

-- Wynik (4 klientów × 4 produkty = 16 rekordów):
-- klient     | produkt     | cena
-- Firma ABC  | Klawiatura  | 150.00
-- Firma ABC  | Laptop      | 3000.00
-- Firma ABC  | Monitor     | 800.00
-- Firma ABC  | Mysz        | 50.00
-- Firma BNM  | Klawiatura  | 150.00
-- ...        | ...         | ...
```

### Praktyczne zastosowania CROSS JOIN:
```sql
-- Kalendarz - każdy dzień z każdą kategorią
WITH dni AS (
    SELECT generate_series('2024-01-01'::date, '2024-01-31'::date, '1 day') as data
),
kategorie AS (
    SELECT unnest(ARRAY['Elektronika', 'Odzież', 'Książki']) as kategoria
)
SELECT d.data, k.kategoria
FROM dni d CROSS JOIN kategorie k
ORDER BY d.data, k.kategoria;

-- Tabela mnożenia
SELECT 
    a.liczba * b.liczba as iloczyn
FROM (SELECT generate_series(1, 10) as liczba) a
CROSS JOIN (SELECT generate_series(1, 10) as liczba) b;
```

## NATURAL JOIN

### Definicja:
**NATURAL JOIN** automatycznie łączy tabele **na podstawie kolumn o identycznych nazwach**.

### Przykład NATURAL JOIN:
```sql
-- Zakładając że obie tabele mają kolumnę 'id_klienta'
SELECT *
FROM klienci
NATURAL JOIN zamowienia;

-- Równoważne z:
SELECT *
FROM klienci k
JOIN zamowienia z ON k.id_klienta = z.id_klienta;
```

### Problemy z NATURAL JOIN:
```sql
-- ⚠️ Niebezpieczne - może łączyć po niepożądanych kolumnach
-- Jeśli obie tabele mają kolumny: id_klienta, data_utworzenia
-- NATURAL JOIN połączy po OBIE kolumny!

-- Bezpieczniej jest być explicit:
SELECT *
FROM klienci k
JOIN zamowienia z USING (id_klienta);  -- Tylko po id_klienta
```

## SELF JOIN

### Definicja:
**SELF JOIN** to łączenie **tabeli samej ze sobą**, używając aliasów.

### Przykład - struktura organizacyjna:
```sql
-- Tabela pracowników z hierarchią
CREATE TABLE pracownicy (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    id_szefa INT,
    FOREIGN KEY (id_szefa) REFERENCES pracownicy(id_pracownika)
);

INSERT INTO pracownicy VALUES 
(1, 'Jan', 'Kowalski', NULL),    -- Prezes
(2, 'Anna', 'Nowak', 1),         -- Podwładny prezesa
(3, 'Piotr', 'Wiśniewski', 1),   -- Podwładny prezesa
(4, 'Maria', 'Kowalczyk', 2),    -- Podwładny Anny
(5, 'Tomasz', 'Lewandowski', 2); -- Podwładny Anny

-- SELF JOIN - pracownicy z ich szefami
SELECT 
    p.imie + ' ' + p.nazwisko as pracownik,
    s.imie + ' ' + s.nazwisko as szef
FROM pracownicy p
LEFT JOIN pracownicy s ON p.id_szefa = s.id_pracownika
ORDER BY p.id_pracownika;

-- Wynik:
-- pracownik         | szef
-- Jan Kowalski      | NULL          (Prezes)
-- Anna Nowak        | Jan Kowalski
-- Piotr Wiśniewski  | Jan Kowalski  
-- Maria Kowalczyk   | Anna Nowak
-- Tomasz Lewandowski| Anna Nowak
```

### SELF JOIN - znajdowanie par:
```sql
-- Produkty w podobnej cenie (różnica max 100 zł)
SELECT 
    p1.nazwa as produkt1,
    p1.cena as cena1,
    p2.nazwa as produkt2,
    p2.cena as cena2,
    ABS(p1.cena - p2.cena) as roznica
FROM produkty p1
JOIN produkty p2 ON p1.id_produktu < p2.id_produktu  -- Unikaj duplikatów
WHERE ABS(p1.cena - p2.cena) <= 100
ORDER BY roznica;
```

## Zaawansowane techniki JOIN

### 1. **Multiple JOIN conditions**
```sql
-- JOIN z wieloma warunkami
SELECT *
FROM zamowienia z
JOIN pozycje_zamowien pz ON z.id_zamowienia = pz.id_zamowienia
    AND z.wartosc > 1000  -- Dodatkowy warunek
JOIN produkty p ON pz.id_produktu = p.id_produktu
    AND p.cena > 100;     -- Dodatkowy warunek
```

### 2. **Non-equi JOIN**
```sql
-- JOIN z warunkiem innym niż równość
SELECT 
    k.nazwa,
    r.kategoria_rabatu,
    r.procent_rabatu
FROM klienci k
JOIN rabaty r ON k.wartosc_roczna BETWEEN r.min_wartosc AND r.max_wartosc;
```

### 3. **JOIN z subcuery**
```sql
-- JOIN z podzapytaniem
SELECT 
    k.nazwa,
    najlepsze.max_wartosc
FROM klienci k
JOIN (
    SELECT 
        id_klienta,
        MAX(wartosc) as max_wartosc
    FROM zamowienia
    GROUP BY id_klienta
) najlepsze ON k.id_klienta = najlepsze.id_klienta
WHERE najlepsze.max_wartosc > 2000;
```

### 4. **UPDATE/DELETE z JOIN**
```sql
-- UPDATE z JOIN (PostgreSQL)
UPDATE produkty 
SET cena = cena * 0.9
FROM kategorie k
WHERE produkty.id_kategorii = k.id_kategorii
  AND k.nazwa = 'Wyprzedaż';

-- DELETE z JOIN (PostgreSQL)
DELETE FROM pozycje_zamowien
USING zamowienia z
WHERE pozycje_zamowien.id_zamowienia = z.id_zamowienia
  AND z.data_zamowienia < '2024-01-01';

-- MySQL/SQL Server syntax:
UPDATE produkty p
JOIN kategorie k ON p.id_kategorii = k.id_kategorii
SET p.cena = p.cena * 0.9
WHERE k.nazwa = 'Wyprzedaż';
```

## Optymalizacja JOIN'ów

### 1. **Indeksy na kolumnach JOIN**
```sql
-- Indeksy na klucze obce
CREATE INDEX idx_zamowienia_klient ON zamowienia(id_klienta);
CREATE INDEX idx_pozycje_zamowienie ON pozycje_zamowien(id_zamowienia);
CREATE INDEX idx_pozycje_produkt ON pozycje_zamowien(id_produktu);
```

### 2. **Kolejność tabel w JOIN**
```sql
-- Zaczynaj od najmniejszej tabeli
-- ✅ LEPIEJ
SELECT *
FROM kategorie k  -- 10 rekordów
JOIN produkty p ON k.id_kategorii = p.id_kategorii  -- 1000 rekordów
JOIN pozycje_zamowien pz ON p.id_produktu = pz.id_produktu;  -- 100000 rekordów

-- ❌ GORZEJ  
SELECT *
FROM pozycje_zamowien pz  -- 100000 rekordów (start)
JOIN produkty p ON pz.id_produktu = p.id_produktu
JOIN kategorie k ON p.id_kategorii = k.id_kategorii;
```

### 3. **Filtrowanie przed JOIN**
```sql
-- Filtruj wcześnie
SELECT *
FROM (SELECT * FROM zamowienia WHERE data_zamowienia >= '2024-01-01') z
JOIN klienci k ON z.id_klienta = k.id_klienta;

-- Zamiast filtrować po JOIN:
SELECT *
FROM zamowienia z
JOIN klienci k ON z.id_klienta = k.id_klienta
WHERE z.data_zamowienia >= '2024-01-01';
```

## Najczęstsze błędy

### 1. **Cartesian Product przez pomyłkę**
```sql
-- ❌ BŁĄD - brak ON clause
SELECT *
FROM klienci k
JOIN zamowienia z;  -- Brakuje ON condition!

-- Wynik: każdy klient × każde zamówienie = explosion!
```

### 2. **NULL handling w JOIN**
```sql
-- ⚠️ UWAGA - NULL nie matchuje z NULL w JOIN
CREATE TABLE test1 (id INT, val INT);
CREATE TABLE test2 (id INT, val INT);

INSERT INTO test1 VALUES (1, NULL);
INSERT INTO test2 VALUES (1, NULL);

-- To NIE zadziała jak oczekujesz:
SELECT * FROM test1 t1 JOIN test2 t2 ON t1.val = t2.val;
-- Wynik: puste (NULL != NULL)

-- Poprawnie:
SELECT * FROM test1 t1 
JOIN test2 t2 ON t1.val = t2.val 
   OR (t1.val IS NULL AND t2.val IS NULL);
```

### 3. **Duplicate columns w NATURAL JOIN**
```sql
-- ❌ Problem z NATURAL JOIN
-- Jeśli tabele mają więcej wspólnych kolumn niż oczekiwane
SELECT * FROM klienci NATURAL JOIN zamowienia;
-- Może łączyć po nieoczekiwanych kolumnach!

-- ✅ Bezpieczniej:
SELECT * FROM klienci k JOIN zamowienia z USING (id_klienta);
```

## Analiza planów wykonania

### PostgreSQL:
```sql
EXPLAIN (ANALYZE, BUFFERS) 
SELECT k.nazwa, COUNT(z.id_zamowienia)
FROM klienci k
LEFT JOIN zamowienia z ON k.id_klienta = z.id_klienta
GROUP BY k.id_klienta, k.nazwa;

-- Szukaj:
-- - Nested Loop vs Hash Join vs Merge Join
-- - Index Scan vs Seq Scan
-- - Buffers hit ratio
```

### MySQL:
```sql
EXPLAIN FORMAT=JSON
SELECT k.nazwa, COUNT(z.id_zamowienia)
FROM klienci k
LEFT JOIN zamowienia z ON k.id_klienta = z.id_klienta
GROUP BY k.id_klienta, k.nazwa;

-- Sprawdź:
-- - type: const, eq_ref, ref, range, index, ALL
-- - key: which index is used
-- - rows: estimated rows processed
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**
1. **Używaj aliasów** - krótkich i znaczących
2. **Explicit JOIN syntax** - unikaj implicit joins
3. **Indeksuj klucze obce** - zawsze!
4. **Filtruj wcześnie** - WHERE przed JOIN gdy możliwe
5. **EXPLAIN plans** - sprawdzaj wydajność

### ❌ **Złe praktyki:**
1. **Implicit joins** - FROM t1, t2 WHERE t1.id = t2.id
2. **NATURAL JOIN** w produkcji - zbyt ryzykowne
3. **Brak indeksów** na kolumnach JOIN
4. **Cartesian products** - zawsze sprawdzaj warunki
5. **Ignorowanie NULL** - pamiętaj o LEFT JOIN semantics

## Pułapki egzaminacyjne

### 1. **Różnice między JOIN'ami**
- **INNER**: Tylko pasujące rekordy
- **LEFT**: Wszystkie z lewej + pasujące z prawej
- **RIGHT**: Wszystkie z prawej + pasujące z lewej  
- **FULL**: Wszystkie z obu stron

### 2. **NULL w wynikach**
- LEFT/RIGHT/FULL JOIN mogą zwracać NULL
- INNER JOIN nigdy nie zwraca NULL z warunków JOIN

### 3. **CROSS JOIN**
- Iloczyn kartezjański: n × m rekordów
- Rzadko używany celowo

### 4. **Performance**
- Indeksy na kolumnach JOIN są kluczowe
- Kolejność tabel może mieć znaczenie
- Filtrowanie wcześnie = lepsza wydajność