# 🔗 SQL JOINY - WSZYSTKIE RODZAJE - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"JOIN to operacja łączenia danych z dwóch lub więcej tabel na podstawie związku między kolumnami. Główne rodzaje:

1. **INNER JOIN** - tylko dopasowane rekordy z obu tabel
2. **LEFT JOIN** - wszystkie z lewej + dopasowane z prawej
3. **RIGHT JOIN** - wszystkie z prawej + dopasowane z lewej  
4. **FULL OUTER JOIN** - wszystkie rekordy z obu tabel
5. **CROSS JOIN** - iloczyn kartezjański wszystkich kombinacji
6. **SELF JOIN** - łączenie tabeli z samą sobą

Każdy JOIN może mieć warunek ON lub USING, NATURAL JOIN łączy automatycznie po kolumnach o tych samych nazwach."

## ✍️ CO NAPISAĆ NA KARTCE

```sql
TYPY JOIN'ÓW I ICH ZASTOSOWANIA:

-- INNER JOIN - przecięcie
SELECT k.nazwa, z.data_zamowienia
FROM klienci k INNER JOIN zamowienia z ON k.id = z.id_klienta;
• Zwraca: tylko klientów którzy mają zamówienia
• Użycie: gdy potrzebujemy dopasowane dane z obu tabel

-- LEFT JOIN (LEFT OUTER JOIN) - wszystkie z lewej
SELECT k.nazwa, z.data_zamowienia  
FROM klienci k LEFT JOIN zamowienia z ON k.id = z.id_klienta;
• Zwraca: wszystkich klientów + ich zamówienia (NULL jeśli brak)
• Użycie: lista wszystkich klientów + informacja o zamówieniach

-- RIGHT JOIN (RIGHT OUTER JOIN) - wszystkie z prawej
SELECT k.nazwa, z.data_zamowienia
FROM klienci k RIGHT JOIN zamowienia z ON k.id = z.id_klienta;
• Zwraca: wszystkie zamówienia + klientów (NULL jeśli klient usunięty)
• Użycie: rzadko, można zastąpić LEFT JOIN

-- FULL OUTER JOIN - suma wszystkich
SELECT k.nazwa, z.data_zamowienia
FROM klienci k FULL OUTER JOIN zamowienia z ON k.id = z.id_klienta;
• Zwraca: wszystkich klientów + wszystkie zamówienia
• Użycie: analiza kompletności danych

-- CROSS JOIN - iloczyn kartezjański  
SELECT k.nazwa, p.nazwa
FROM klienci k CROSS JOIN produkty p;
• Zwraca: każdy klient z każdym produktem
• Użycie: generowanie kombinacji, testy

-- SELF JOIN - tabela z samą sobą
SELECT p1.nazwa as pracownik, p2.nazwa as manager
FROM pracownicy p1 JOIN pracownicy p2 ON p1.manager_id = p2.id;
• Zwraca: hierarchie, struktury drzewiaste
• Użycie: organizacje, kategorie, struktury parent-child

SKŁADNIA:
FROM tabela1 [INNER|LEFT|RIGHT|FULL] JOIN tabela2 
  ON warunek
  
FROM tabela1 JOIN tabela2 USING (kolumna)

FROM tabela1 NATURAL JOIN tabela2
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- PRZYGOTOWANIE DANYCH TESTOWYCH

CREATE TABLE klienci (
    id_klienta INT PRIMARY KEY,
    nazwa VARCHAR(100),
    miasto VARCHAR(50),
    aktywny BOOLEAN DEFAULT TRUE
);

CREATE TABLE zamowienia (
    id_zamowienia INT PRIMARY KEY,
    id_klienta INT,
    data_zamowienia DATE,
    kwota DECIMAL(10,2),
    status VARCHAR(20)
);

CREATE TABLE produkty (
    id_produktu INT PRIMARY KEY,
    nazwa VARCHAR(100),
    cena DECIMAL(10,2),
    kategoria VARCHAR(50)
);

CREATE TABLE pozycje_zamowienia (
    id_zamowienia INT,
    id_produktu INT,
    ilosc INT,
    PRIMARY KEY (id_zamowienia, id_produktu)
);

-- Dane testowe
INSERT INTO klienci VALUES 
(1, 'Firma ABC', 'Warszawa', TRUE),
(2, 'Firma XYZ', 'Kraków', TRUE),
(3, 'Firma QWE', 'Gdańsk', FALSE),
(4, 'Firma RTY', 'Wrocław', TRUE);

INSERT INTO zamowienia VALUES 
(101, 1, '2024-01-15', 1500.00, 'zakonczone'),
(102, 1, '2024-01-20', 800.00, 'w_realizacji'),
(103, 2, '2024-01-18', 1200.00, 'zakonczone'),
(104, NULL, '2024-01-22', 500.00, 'anonimowe'); -- zamówienie bez klienta

INSERT INTO produkty VALUES 
(201, 'Laptop', 3000.00, 'Elektronika'),
(202, 'Mysz', 50.00, 'Elektronika'),
(203, 'Klawiatura', 120.00, 'Elektronika'),
(204, 'Monitor', 800.00, 'Elektronika');

INSERT INTO pozycje_zamowienia VALUES 
(101, 201, 1), (101, 202, 2),
(102, 203, 1), (102, 204, 1),
(103, 201, 1), (103, 203, 1);

-- 1. INNER JOIN - tylko dopasowane rekordy

-- Podstawowy INNER JOIN
SELECT k.nazwa as klient, z.id_zamowienia, z.kwota
FROM klienci k 
INNER JOIN zamowienia z ON k.id_klienta = z.id_klienta;
-- Wynik: 3 wiersze (zamówienia 101,102,103 z klientami)

-- Wielotabelowy INNER JOIN
SELECT 
    k.nazwa as klient,
    z.id_zamowienia,
    p.nazwa as produkt,
    pz.ilosc,
    (p.cena * pz.ilosc) as wartosc_pozycji
FROM klienci k
INNER JOIN zamowienia z ON k.id_klienta = z.id_klienta
INNER JOIN pozycje_zamowienia pz ON z.id_zamowienia = pz.id_zamowienia  
INNER JOIN produkty p ON pz.id_produktu = p.id_produktu
ORDER BY k.nazwa, z.id_zamowienia;

-- 2. LEFT JOIN - wszystkie z lewej tabeli

-- Wszyscy klienci + ich zamówienia (jeśli mają)
SELECT 
    k.nazwa as klient,
    k.miasto,
    z.id_zamowienia,
    z.kwota,
    z.status
FROM klienci k
LEFT JOIN zamowienia z ON k.id_klienta = z.id_klienta
ORDER BY k.nazwa;
-- Wynik: 4 klientów, "Firma RTY" ma NULL w kolumnach zamówienia

-- Znajdowanie klientów bez zamówień
SELECT k.nazwa, k.miasto
FROM klienci k
LEFT JOIN zamowienia z ON k.id_klienta = z.id_klienta
WHERE z.id_klienta IS NULL;
-- Wynik: klienci którzy nie złożyli zamówień

-- 3. RIGHT JOIN - wszystkie z prawej tabeli

-- Wszystkie zamówienia + klienci (jeśli przypisani)
SELECT 
    z.id_zamowienia,
    z.kwota,
    z.status,
    k.nazwa as klient,
    k.miasto
FROM klienci k
RIGHT JOIN zamowienia z ON k.id_klienta = z.id_klienta
ORDER BY z.id_zamowienia;
-- Wynik: 4 zamówienia, zamówienie 104 ma NULL w danych klienta

-- 4. FULL OUTER JOIN - wszystkie rekordy

-- Kompletny obraz klientów i zamówień
SELECT 
    COALESCE(k.nazwa, 'NIEZNANY KLIENT') as klient,
    COALESCE(z.id_zamowienia::TEXT, 'BRAK ZAMÓWIEŃ') as zamowienie,
    z.kwota
FROM klienci k
FULL OUTER JOIN zamowienia z ON k.id_klienta = z.id_klienta
ORDER BY k.nazwa NULLS LAST, z.id_zamowienia;
-- Wynik: wszyscy klienci + wszystkie zamówienia

-- 5. CROSS JOIN - iloczyn kartezjański

-- Wszystkie kombinacje klientów i produktów
SELECT 
    k.nazwa as klient,
    p.nazwa as produkt,
    p.cena
FROM klienci k
CROSS JOIN produkty p
WHERE k.aktywny = TRUE  -- filtrowanie po CROSS JOIN
ORDER BY k.nazwa, p.nazwa;
-- Wynik: 3 aktywnych klientów × 4 produkty = 12 wierszy

-- Praktyczne użycie CROSS JOIN - generowanie raportów
SELECT 
    k.nazwa as klient,
    kat.kategoria,
    COALESCE(stat.liczba_zamowien, 0) as liczba_zamowien
FROM klienci k
CROSS JOIN (SELECT DISTINCT kategoria FROM produkty) kat
LEFT JOIN (
    SELECT 
        z.id_klienta,
        p.kategoria,
        COUNT(*) as liczba_zamowien
    FROM zamowienia z
    JOIN pozycje_zamowienia pz ON z.id_zamowienia = pz.id_zamowienia
    JOIN produkty p ON pz.id_produktu = p.id_produktu
    GROUP BY z.id_klienta, p.kategoria
) stat ON k.id_klienta = stat.id_klienta AND kat.kategoria = stat.kategoria
ORDER BY k.nazwa, kat.kategoria;

-- 6. SELF JOIN - tabela z samą sobą

-- Rozszerzenie tabeli klientów o strukturę hierarchiczną
ALTER TABLE klienci ADD COLUMN parent_klient_id INT;
UPDATE klienci SET parent_klient_id = 1 WHERE id_klienta = 2; -- Firma XYZ jest "oddziałem" ABC

-- Hierarchia klient-oddział
SELECT 
    k1.nazwa as klient_glowny,
    k2.nazwa as oddzial,
    k2.miasto as miasto_oddzialu
FROM klienci k1
INNER JOIN klienci k2 ON k1.id_klienta = k2.parent_klient_id;

-- Wszyscy klienci + ewentualne oddziały
SELECT 
    k1.nazwa as klient,
    k1.miasto,
    k2.nazwa as oddzial
FROM klienci k1
LEFT JOIN klienci k2 ON k1.id_klienta = k2.parent_klient_id
ORDER BY k1.nazwa;

-- 7. ZAAWANSOWANE TECHNIKI JOIN

-- Multiple JOIN conditions
SELECT k.nazwa, z.id_zamowienia, z.kwota
FROM klienci k
JOIN zamowienia z ON k.id_klienta = z.id_klienta 
                 AND z.kwota > 1000
                 AND z.status = 'zakonczone';

-- JOIN z subquery
SELECT 
    k.nazwa,
    duze_zamowienia.liczba_duzych_zamowien
FROM klienci k
JOIN (
    SELECT 
        id_klienta,
        COUNT(*) as liczba_duzych_zamowien
    FROM zamowienia 
    WHERE kwota > 1000
    GROUP BY id_klienta
) duze_zamowienia ON k.id_klienta = duze_zamowienia.id_klienta;

-- LATERAL JOIN (PostgreSQL) - correlated subquery w FROM
SELECT 
    k.nazwa,
    ostatnie_zamowienia.data_zamowienia,
    ostatnie_zamowienia.kwota
FROM klienci k
JOIN LATERAL (
    SELECT data_zamowienia, kwota
    FROM zamowienia z
    WHERE z.id_klienta = k.id_klienta
    ORDER BY data_zamowienia DESC
    LIMIT 3
) ostatnie_zamowienia ON TRUE;

-- 8. USING vs ON vs NATURAL

-- USING - gdy kolumny mają te same nazwy
CREATE VIEW zamowienia_v AS 
SELECT id_zamowienia, id_klienta as id, kwota FROM zamowienia;

SELECT k.nazwa, zv.kwota
FROM klienci k
JOIN zamowienia_v zv USING (id);  -- łączy po k.id_klienta = zv.id

-- NATURAL JOIN - automatyczne łączenie po wszystkich wspólnych kolumnach  
SELECT k.nazwa, z.kwota
FROM klienci k
NATURAL JOIN zamowienia z;  -- łączy po id_klienta automatycznie

-- 9. PERFORMANCE OPTIMIZATION

-- Użycie EXISTS zamiast JOIN dla sprawdzenia istnienia
-- ZAMIAST:
SELECT DISTINCT k.nazwa
FROM klienci k
JOIN zamowienia z ON k.id_klienta = z.id_klienta;

-- LEPIEJ:
SELECT k.nazwa  
FROM klienci k
WHERE EXISTS (
    SELECT 1 FROM zamowienia z WHERE z.id_klienta = k.id_klienta
);

-- Anti-join - klienci bez zamówień (wydajniej niż LEFT JOIN + IS NULL)
SELECT k.nazwa
FROM klienci k  
WHERE NOT EXISTS (
    SELECT 1 FROM zamowienia z WHERE z.id_klienta = k.id_klienta
);

-- 10. ANALIZA PLANÓW WYKONANIA

EXPLAIN (ANALYZE, BUFFERS)
SELECT k.nazwa, COUNT(z.id_zamowienia) as liczba_zamowien
FROM klienci k
LEFT JOIN zamowienia z ON k.id_klienta = z.id_klienta
GROUP BY k.id_klienta, k.nazwa
ORDER BY liczba_zamowien DESC;
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: LEFT JOIN ≠ RIGHT JOIN (kolejność tabel ma znaczenie)
2. **UWAGA**: INNER JOIN eliminuje wiersze bez dopasowania z obu stron
3. **BŁĄD**: Zapominanie o NULL'ach w OUTER JOIN'ach
4. **WAŻNE**: CROSS JOIN bez WHERE może tworzyć ogromne wyniki
5. **PUŁAPKA**: NATURAL JOIN może łączyć po niechcianych kolumnach

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Inner/Outer joins** - złączenia wewnętrzne/zewnętrzne
- **Cartesian product** - iloczyn kartezjański
- **Join condition** - warunek łączenia
- **NULL handling** - obsługa wartości NULL
- **Self join** - samo-złączenie
- **Natural join** - złączenie naturalne
- **Anti-join** - anty-złączenie
- **Semi-join** - pół-złączenie

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **08-natural-join** - szczegóły Natural Join
- **12-klucze-bazy-danych** - klucze obce w JOIN'ach
- **24-wartosc-null** - NULL w JOIN'ach
- **30-sql-dml-zaawansowany** - zaawansowane zapytania z JOIN
- **42-optymalizacja-wydajnosci** - optymalizacja JOIN'ów