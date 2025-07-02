# 👁️ PERSPEKTYWY (VIEWS) - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekunds)

"Widok (View) to wirtualna tabela będąca zapisaną definicją zapytania SQL. Nie przechowuje danych fizycznie, tylko definicję. Rodzaje:

1. **Simple Views** - oparte na jednej tabeli, często updatable
2. **Complex Views** - JOIN'y, agregacje, zwykle read-only
3. **Materialized Views** - fizycznie przechowywane dane, wymagają odświeżania

Zastosowania: bezpieczeństwo (ukrywanie kolumn), uproszczenie zapytań, abstrakcja, kontrola dostępu. Widoki są wykonywane za każdym razem gdy są używane."

## ✍️ CO NAPISAĆ NA KARTCE

```sql
WIDOKI (VIEWS) - DEFINICJA I TYPY:

-- TWORZENIE WIDOKU
CREATE VIEW nazwa_widoku AS
SELECT kolumny
FROM tabele
WHERE warunki;

-- TYPY WIDOKÓW:

1. SIMPLE VIEW (prosty):
CREATE VIEW aktywni_pracownicy AS
SELECT id, imie, nazwisko, pensja
FROM pracownicy  
WHERE aktywny = TRUE;
• Jedna tabela
• Bez GROUP BY, DISTINCT, funkcji agregujących
• Często UPDATABLE (INSERT, UPDATE, DELETE)

2. COMPLEX VIEW (złożony):
CREATE VIEW raport_sprzedazy AS
SELECT d.nazwa, COUNT(p.id) as liczba_pracownikow, AVG(p.pensja) as srednia
FROM departamenty d
LEFT JOIN pracownicy p ON d.id = p.id_departamentu
GROUP BY d.id, d.nazwa;
• Wielotabelowy (JOIN)
• GROUP BY, agregacje, DISTINCT
• READ ONLY (nie można modyfikować)

3. MATERIALIZED VIEW (zmaterializowany):
CREATE MATERIALIZED VIEW mv_statystyki AS
SELECT ... FROM ... GROUP BY ...;
REFRESH MATERIALIZED VIEW mv_statystyki;
• Fizycznie przechowywane dane
• Szybsze odczyty
• Wymagają odświeżania

ZASTOSOWANIA:
✓ Bezpieczeństwo - ukrywanie wrażliwych danych
✓ Uproszczenie - abstrakcja nad złożonymi zapytaniami  
✓ Kontrola dostępu - różne widoki dla różnych ról
✓ Backward compatibility - ukrywanie zmian w strukturze

OGRANICZENIA UPDATABLE VIEWS:
✗ GROUP BY, HAVING, DISTINCT
✗ Funkcje agregujące (SUM, COUNT, etc.)
✗ UNION, INTERSECT, EXCEPT  
✗ Subqueries w SELECT
✗ Więcej niż jedna tabela (bez INSTEAD OF triggers)

WITH CHECK OPTION:
CREATE VIEW widok WITH CHECK OPTION AS SELECT ... WHERE warunek;
• Zapobiega INSERT/UPDATE które naruszają warunek WHERE widoku
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- PRZYGOTOWANIE DANYCH TESTOWYCH

CREATE TABLE departamenty (
    id_departamentu SERIAL PRIMARY KEY,
    nazwa VARCHAR(100) NOT NULL,
    budzet DECIMAL(12,2),
    kierownik_id INT
);

CREATE TABLE pracownicy (
    id_pracownika SERIAL PRIMARY KEY,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    pensja DECIMAL(10,2),
    data_zatrudnienia DATE DEFAULT CURRENT_DATE,
    id_departamentu INT,
    aktywny BOOLEAN DEFAULT TRUE,
    pesel VARCHAR(11),  -- wrażliwe dane
    
    FOREIGN KEY (id_departamentu) REFERENCES departamenty(id_departamentu)
);

CREATE TABLE projekty (
    id_projektu SERIAL PRIMARY KEY,
    nazwa VARCHAR(100),
    deadline DATE,
    budzet DECIMAL(12,2),
    id_departamentu INT
);

-- Dane testowe
INSERT INTO departamenty VALUES 
(1, 'IT', 500000, NULL),
(2, 'HR', 200000, NULL),
(3, 'Finanse', 300000, NULL);

INSERT INTO pracownicy VALUES 
(1, 'Jan', 'Kowalski', 'jan@firma.com', 8000, '2020-01-15', 1, TRUE, '80010112345'),
(2, 'Anna', 'Nowak', 'anna@firma.com', 7500, '2021-03-10', 1, TRUE, '85020223456'),
(3, 'Piotr', 'Wiśniewski', 'piotr@firma.com', 6000, '2019-06-20', 2, TRUE, '90030334567'),
(4, 'Maria', 'Kowalczyk', 'maria@firma.com', 9000, '2018-09-12', 3, FALSE, '75040445678');

-- 1. SIMPLE VIEWS - podstawowe widoki

-- Widok bezpieczeństwa - ukrywa wrażliwe dane
CREATE VIEW pracownicy_publiczny AS
SELECT 
    id_pracownika,
    imie,
    nazwisko,
    email,
    id_departamentu,
    data_zatrudnienia
FROM pracownicy
WHERE aktywny = TRUE;
-- Ukrywa: pensja, pesel, nieaktywnych pracowników

-- Widok aktywnych pracowników z pensją (dla HR)
CREATE VIEW hr_pracownicy AS
SELECT 
    id_pracownika,
    imie,
    nazwisko,
    email,
    pensja,
    data_zatrudnienia,
    id_departamentu
FROM pracownicy
WHERE aktywny = TRUE;

-- Test updatable view
INSERT INTO hr_pracownicy (imie, nazwisko, email, pensja, id_departamentu)
VALUES ('Tomasz', 'Nowicki', 'tomasz@firma.com', 7000, 1);

UPDATE hr_pracownicy 
SET pensja = 7200 
WHERE email = 'tomasz@firma.com';

-- 2. COMPLEX VIEWS - widoki analityczne

-- Raport departamentów
CREATE VIEW raport_departamentow AS
SELECT 
    d.nazwa as departament,
    d.budzet as budzet_departamentu,
    COUNT(p.id_pracownika) as liczba_pracownikow,
    COALESCE(AVG(p.pensja), 0) as srednia_pensja,
    COALESCE(SUM(p.pensja), 0) as suma_pensji,
    d.budzet - COALESCE(SUM(p.pensja) * 12, 0) as pozostaly_budzet
FROM departamenty d
LEFT JOIN pracownicy p ON d.id_departamentu = p.id_departamentu 
                      AND p.aktywny = TRUE
GROUP BY d.id_departamentu, d.nazwa, d.budzet;

-- Widok szczegółowy pracownik-departament
CREATE VIEW pracownik_departament AS
SELECT 
    p.imie || ' ' || p.nazwisko as pelne_imie,
    p.email,
    p.pensja,
    d.nazwa as departament,
    d.budzet as budzet_dept,
    ROUND(p.pensja * 12.0 / d.budzet * 100, 2) as procent_budzetu,
    EXTRACT(YEAR FROM AGE(p.data_zatrudnienia)) as lata_pracy
FROM pracownicy p
JOIN departamenty d ON p.id_departamentu = d.id_departamentu
WHERE p.aktywny = TRUE;

-- 3. WIDOKI Z WITH CHECK OPTION

-- Widok pracowników IT z kontrolą
CREATE VIEW it_pracownicy AS
SELECT *
FROM pracownicy
WHERE id_departamentu = 1 AND aktywny = TRUE
WITH CHECK OPTION;

-- To się uda:
INSERT INTO it_pracownicy (imie, nazwisko, email, pensja, id_departamentu, aktywny)
VALUES ('Jakub', 'Kowalski', 'jakub@firma.com', 6500, 1, TRUE);

-- To się nie uda (narusza warunek WHERE):
-- INSERT INTO it_pracownicy (imie, nazwisko, email, pensja, id_departamentu)
-- VALUES ('Adam', 'Nowak', 'adam@firma.com', 6000, 2);  -- błąd: nie IT

-- 4. INSTEAD OF TRIGGERS dla complex views

-- Complex view nie jest updatable domyślnie
-- Możemy dodać INSTEAD OF trigger

CREATE OR REPLACE FUNCTION aktualizuj_raport_departamentow()
RETURNS TRIGGER AS $$
BEGIN
    -- Aktualizuj budżet departamentu
    IF OLD.budzet_departamentu != NEW.budzet_departamentu THEN
        UPDATE departamenty 
        SET budzet = NEW.budzet_departamentu
        WHERE nazwa = NEW.departament;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_update_raport_departamentow
    INSTEAD OF UPDATE ON raport_departamentow
    FOR EACH ROW
    EXECUTE FUNCTION aktualizuj_raport_departamentow();

-- Teraz można "aktualizować" complex view:
UPDATE raport_departamentow 
SET budzet_departamentu = 600000 
WHERE departament = 'IT';

-- 5. MATERIALIZED VIEWS

-- Materialized view dla kosztownych obliczeń
CREATE MATERIALIZED VIEW mv_analiza_pensji AS
SELECT 
    d.nazwa as departament,
    COUNT(*) as liczba_pracownikow,
    AVG(p.pensja) as srednia_pensja,
    MIN(p.pensja) as min_pensja,
    MAX(p.pensja) as max_pensja,
    STDDEV(p.pensja) as odchylenie_std,
    -- Percentile calculations (kosztowne)
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY p.pensja) as q1,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY p.pensja) as mediana,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY p.pensja) as q3
FROM pracownicy p
JOIN departamenty d ON p.id_departamentu = d.id_departamentu
WHERE p.aktywny = TRUE
GROUP BY d.id_departamentu, d.nazwa;

-- Odświeżanie materialized view
REFRESH MATERIALIZED VIEW mv_analiza_pensji;

-- Concurrent refresh (nie blokuje odczytów)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_analiza_pensji;

-- Indeks na materialized view dla wydajności
CREATE INDEX idx_mv_analiza_departament ON mv_analiza_pensji(departament);

-- 6. RECURSIVE VIEWS (PostgreSQL)

-- Dodanie hierarchii organizacyjnej
ALTER TABLE pracownicy ADD COLUMN manager_id INT;
UPDATE pracownicy SET manager_id = 1 WHERE id_pracownika IN (2, 3);
UPDATE pracownicy SET manager_id = 2 WHERE id_pracownika = 4;

-- Recursive view dla hierarchii
CREATE RECURSIVE VIEW hierarchia_organizacyjna AS
    -- Base case: top managers (bez managera)
    SELECT 
        id_pracownika,
        imie,
        nazwisko,
        manager_id,
        0 as poziom,
        imie || ' ' || nazwisko as sciezka
    FROM pracownicy
    WHERE manager_id IS NULL AND aktywny = TRUE
    
    UNION ALL
    
    -- Recursive case: podwładni
    SELECT 
        p.id_pracownika,
        p.imie,
        p.nazwisko,
        p.manager_id,
        h.poziom + 1,
        h.sciezka || ' -> ' || p.imie || ' ' || p.nazwisko
    FROM pracownicy p
    JOIN hierarchia_organizacyjna h ON p.manager_id = h.id_pracownika
    WHERE p.aktywny = TRUE;

-- 7. SECURITY VIEWS - kontrola dostępu

-- View dla różnych ról
-- Rola: employee - widzi tylko swoje dane
CREATE VIEW moje_dane AS
SELECT 
    imie,
    nazwisko,
    email,
    pensja,
    data_zatrudnienia
FROM pracownicy
WHERE email = current_setting('app.current_user_email')
AND aktywny = TRUE;

-- Rola: manager - widzi swój departament
CREATE VIEW moj_departament AS
SELECT 
    p.imie,
    p.nazwisko,
    p.email,
    p.pensja,
    p.data_zatrudnienia
FROM pracownicy p
JOIN pracownicy manager ON p.id_departamentu = manager.id_departamentu
WHERE manager.email = current_setting('app.current_user_email')
AND p.aktywny = TRUE;

-- 8. MONITORING I ZARZĄDZANIE WIDOKAMI

-- Lista wszystkich widoków
SELECT 
    schemaname,
    viewname,
    definition
FROM pg_views
WHERE schemaname = 'public'
ORDER BY viewname;

-- Sprawdzenie czy widok jest updatable
SELECT 
    table_name,
    is_updatable,
    is_insertable_into
FROM information_schema.views
WHERE table_schema = 'public'
ORDER BY table_name;

-- Znajdowanie widoków używających konkretną tabelę
SELECT DISTINCT
    schemaname,
    viewname
FROM pg_views
WHERE definition LIKE '%pracownicy%'
ORDER BY viewname;

-- Dependency tracking - które widoki zależą od tabeli
SELECT DISTINCT
    dependent_ns.nspname as dependent_schema,
    dependent_view.relname as dependent_view,
    source_ns.nspname as source_schema,
    source_table.relname as source_table
FROM pg_depend 
JOIN pg_rewrite ON pg_depend.objid = pg_rewrite.oid
JOIN pg_class as dependent_view ON pg_rewrite.ev_class = dependent_view.oid
JOIN pg_class as source_table ON pg_depend.refobjid = source_table.oid 
JOIN pg_namespace dependent_ns ON dependent_ns.oid = dependent_view.relnamespace
JOIN pg_namespace source_ns ON source_ns.oid = source_table.relnamespace
WHERE source_table.relname = 'pracownicy'
AND dependent_view.relkind = 'v';

-- 9. PERFORMANCE CONSIDERATIONS

-- View execution plan
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM raport_departamentow
WHERE liczba_pracownikow > 2;

-- Porównanie view vs materialized view
-- Regular view (executed each time)
\timing on
SELECT COUNT(*) FROM raport_departamentow;

-- Materialized view (pre-calculated)
SELECT COUNT(*) FROM mv_analiza_pensji;

-- 10. DROP I ALTER VIEWS

-- Usuwanie widoku
DROP VIEW IF EXISTS it_pracownicy;

-- Recreate view (ALTER VIEW ma ograniczenia)
CREATE OR REPLACE VIEW hr_pracownicy AS
SELECT 
    id_pracownika,
    imie,
    nazwisko,
    email,
    pensja,
    data_zatrudnienia,
    id_departamentu,
    'HR VIEW' as source  -- dodana kolumna
FROM pracownicy
WHERE aktywny = TRUE;

-- Drop materialized view
DROP MATERIALIZED VIEW IF EXISTS mv_analiza_pensji;
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Views nie przechowują danych, tylko definicję zapytania
2. **UWAGA**: Complex views (z JOIN, GROUP BY) zwykle nie są updatable
3. **BŁĄD**: Zapominanie o REFRESH dla materialized views
4. **WAŻNE**: WITH CHECK OPTION sprawdza warunki przy INSERT/UPDATE
5. **PUŁAPKA**: Views mogą być wolne jeśli bazują na złożonych zapytaniach

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Virtual table** - tabela wirtualna
- **View definition** - definicja widoku
- **Updatable views** - widoki modyfikowalne
- **Materialized views** - zmaterializowane widoki
- **WITH CHECK OPTION** - opcja sprawdzania warunków
- **INSTEAD OF triggers** - triggery zamiast operacji
- **Security views** - widoki bezpieczeństwa
- **Query rewriting** - przepisywanie zapytań

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **11-widoki-vs-tabele-tymczasowe** - porównanie z tabelami tymczasowymi
- **39-bezpieczenstwo-baz** - security views
- **42-optymalizacja-wydajnosci** - materialized views dla wydajności
- **06-triggery** - INSTEAD OF triggers
- **21-sql-joiny** - complex views z JOIN'ami