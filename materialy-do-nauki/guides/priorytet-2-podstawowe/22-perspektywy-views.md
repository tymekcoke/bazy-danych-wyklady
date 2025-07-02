# Perspektywy (Views) - zastosowania

## Definicja

**Perspektywa (widok, view)** to **nazwane zapytanie SQL** przechowywane w bazie danych, które działa jak **wirtualna tabela**. Nie przechowuje fizycznie danych, ale **generuje je dynamicznie** przy każdym wywołaniu.

### Kluczowe cechy:
- **Wirtualna natura** - tylko definicja zapytania
- **Dynamiczne dane** - zawsze aktualne
- **Nazwana** - może być używana jak tabela
- **Bezpieczeństwo** - kontrola dostępu do danych

### Składnia podstawowa:
```sql
CREATE VIEW nazwa_widoku AS
SELECT kolumny
FROM tabele
WHERE warunki;

-- Użycie widoku
SELECT * FROM nazwa_widoku;

-- Usunięcie widoku
DROP VIEW nazwa_widoku;
```

## Zastosowania perspektyw

### 1. **Uproszczenie skomplikowanych zapytań**

#### Problem: Złożone JOIN'y powtarzane wielokrotnie
```sql
-- Zamiast pisać za każdym razem:
SELECT 
    k.nazwa as klient,
    z.id_zamowienia,
    z.data_zamowienia,
    p.nazwa as produkt,
    pz.ilosc,
    p.cena,
    (pz.ilosc * p.cena) as wartosc
FROM klienci k
JOIN zamowienia z ON k.id_klienta = z.id_klienta
JOIN pozycje_zamowien pz ON z.id_zamowienia = pz.id_zamowienia
JOIN produkty p ON pz.id_produktu = p.id_produktu;
```

#### Rozwiązanie: View
```sql
-- Utwórz widok
CREATE VIEW szczegoly_zamowien AS
SELECT 
    k.id_klienta,
    k.nazwa as klient,
    z.id_zamowienia,
    z.data_zamowienia,
    p.id_produktu,
    p.nazwa as produkt,
    pz.ilosc,
    p.cena,
    (pz.ilosc * p.cena) as wartosc
FROM klienci k
JOIN zamowienia z ON k.id_klienta = z.id_klienta
JOIN pozycje_zamowien pz ON z.id_zamowienia = pz.id_zamowienia
JOIN produkty p ON pz.id_produktu = p.id_produktu;

-- Teraz proste użycie:
SELECT * FROM szczegoly_zamowien WHERE klient = 'Firma ABC';
SELECT produkt, SUM(wartosc) FROM szczegoly_zamowien GROUP BY produkt;
SELECT * FROM szczegoly_zamowien WHERE data_zamowienia >= '2024-01-01';
```

### 2. **Bezpieczeństwo i kontrola dostępu**

#### Ukrywanie wrażliwych kolumn:
```sql
-- Tabela z danymi wrażliwymi
CREATE TABLE pracownicy (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    pesel VARCHAR(11),           -- Wrażliwe!
    pensja DECIMAL(10,2),        -- Wrażliwe!
    numer_konta VARCHAR(26),     -- Wrażliwe!
    email VARCHAR(100),
    telefon VARCHAR(15),
    dzial VARCHAR(50)
);

-- Widok publiczny dla HR
CREATE VIEW pracownicy_hr AS
SELECT 
    id_pracownika,
    imie,
    nazwisko,
    email,
    telefon,
    dzial
FROM pracownicy;

-- Widok dla księgowości
CREATE VIEW pracownicy_ksiegowosc AS
SELECT 
    id_pracownika,
    imie,
    nazwisko,
    pensja,
    numer_konta
FROM pracownicy;

-- Nadaj uprawnienia
GRANT SELECT ON pracownicy_hr TO role_hr;
GRANT SELECT ON pracownicy_ksiegowosc TO role_ksiegowosc;
-- NIE dawaj dostępu do tabeli pracownicy!
```

#### Filtrowanie wierszy (Row-Level Security):
```sql
-- Widok dla managera - tylko jego zespół
CREATE VIEW moj_zespol AS
SELECT 
    id_pracownika,
    imie,
    nazwisko,
    email,
    pensja
FROM pracownicy
WHERE id_szefa = USER_ID();  -- Tylko podwładni aktualnego użytkownika

-- Widok dla działu - tylko pracownicy tego działu
CREATE VIEW pracownicy_dzialu AS
SELECT 
    id_pracownika,
    imie,
    nazwisko,
    email
FROM pracownicy p
JOIN uzytkownicy u ON u.dzial = p.dzial
WHERE u.login = USER();
```

### 3. **Agregacja i raportowanie**

#### Często używane kalkulacje:
```sql
-- Widok z agregatami sprzedaży
CREATE VIEW sprzedaz_miesięczna AS
SELECT 
    EXTRACT(YEAR FROM z.data_zamowienia) as rok,
    EXTRACT(MONTH FROM z.data_zamowienia) as miesiac,
    COUNT(DISTINCT z.id_zamowienia) as liczba_zamowien,
    COUNT(DISTINCT z.id_klienta) as liczba_klientow,
    SUM(pz.ilosc * p.cena) as suma_sprzedazy,
    AVG(pz.ilosc * p.cena) as srednia_wartosc_pozycji
FROM zamowienia z
JOIN pozycje_zamowien pz ON z.id_zamowienia = pz.id_zamowienia
JOIN produkty p ON pz.id_produktu = p.id_produktu
GROUP BY 
    EXTRACT(YEAR FROM z.data_zamowienia),
    EXTRACT(MONTH FROM z.data_zamowienia);

-- Użycie:
SELECT * FROM sprzedaz_miesięczna WHERE rok = 2024;
SELECT AVG(suma_sprzedazy) FROM sprzedaz_miesięczna;
```

#### Ranking i statystyki:
```sql
-- Top klienci
CREATE VIEW top_klienci AS
SELECT 
    k.id_klienta,
    k.nazwa,
    COUNT(z.id_zamowienia) as liczba_zamowien,
    SUM(pz.ilosc * p.cena) as suma_zakupow,
    AVG(pz.ilosc * p.cena) as srednia_zakupu,
    ROW_NUMBER() OVER (ORDER BY SUM(pz.ilosc * p.cena) DESC) as ranking
FROM klienci k
JOIN zamowienia z ON k.id_klienta = z.id_klienta
JOIN pozycje_zamowien pz ON z.id_zamowienia = pz.id_zamowienia
JOIN produkty p ON pz.id_produktu = p.id_produktu
GROUP BY k.id_klienta, k.nazwa;

-- Top 10 klientów
SELECT * FROM top_klienci WHERE ranking <= 10;
```

### 4. **Kompatybilność wsteczna**

#### Po zmianie struktury tabeli:
```sql
-- Stara struktura
CREATE TABLE klienci_stara (
    id INT,
    nazwa_firmy VARCHAR(100),
    kontakt VARCHAR(100)  -- imię i nazwisko w jednej kolumnie
);

-- Nowa struktura
CREATE TABLE klienci_nowa (
    id INT,
    nazwa_firmy VARCHAR(100),
    imie_kontaktu VARCHAR(50),
    nazwisko_kontaktu VARCHAR(50)
);

-- Widok zachowujący starą strukturę
CREATE VIEW klienci AS
SELECT 
    id,
    nazwa_firmy,
    CONCAT(imie_kontaktu, ' ', nazwisko_kontaktu) as kontakt
FROM klienci_nowa;

-- Stare aplikacje dalej działają!
SELECT * FROM klienci WHERE kontakt LIKE '%Kowalski%';
```

### 5. **Denormalizacja dla wydajności**

#### Płaskie widoki dla raportowania:
```sql
-- Widok denormalizowany dla raportów
CREATE VIEW raport_sprzedazy AS
SELECT 
    z.id_zamowienia,
    z.data_zamowienia,
    k.nazwa as klient,
    k.miasto as miasto_klienta,
    k.kategoria as kategoria_klienta,
    p.nazwa as produkt,
    p.kategoria as kategoria_produktu,
    p.dostawca,
    pz.ilosc,
    p.cena_zakupu,
    p.cena_sprzedazy,
    (pz.ilosc * p.cena_sprzedazy) as przychod,
    (pz.ilosc * p.cena_zakupu) as koszt,
    (pz.ilosc * (p.cena_sprzedazy - p.cena_zakupu)) as zysk
FROM zamowienia z
JOIN klienci k ON z.id_klienta = k.id_klienta
JOIN pozycje_zamowien pz ON z.id_zamowienia = pz.id_zamowienia
JOIN produkty p ON pz.id_produktu = p.id_produktu;

-- Łatwe raportowanie
SELECT 
    kategoria_produktu,
    SUM(przychod) as suma_przychod,
    SUM(zysk) as suma_zysk
FROM raport_sprzedazy
WHERE data_zamowienia >= '2024-01-01'
GROUP BY kategoria_produktu;
```

### 6. **Business Logic w bazie danych**

#### Kalkulacje biznesowe:
```sql
-- Widok z logiką rabatów
CREATE VIEW zamowienia_z_rabatem AS
SELECT 
    z.id_zamowienia,
    z.id_klienta,
    z.data_zamowienia,
    SUM(pz.ilosc * p.cena) as wartosc_brutto,
    CASE 
        WHEN SUM(pz.ilosc * p.cena) >= 10000 THEN 0.15  -- 15% rabat
        WHEN SUM(pz.ilosc * p.cena) >= 5000 THEN 0.10   -- 10% rabat
        WHEN SUM(pz.ilosc * p.cena) >= 1000 THEN 0.05   -- 5% rabat
        ELSE 0.0
    END as procent_rabatu,
    SUM(pz.ilosc * p.cena) * (1 - CASE 
        WHEN SUM(pz.ilosc * p.cena) >= 10000 THEN 0.15
        WHEN SUM(pz.ilosc * p.cena) >= 5000 THEN 0.10
        WHEN SUM(pz.ilosc * p.cena) >= 1000 THEN 0.05
        ELSE 0.0
    END) as wartosc_po_rabacie
FROM zamowienia z
JOIN pozycje_zamowien pz ON z.id_zamowienia = pz.id_zamowienia
JOIN produkty p ON pz.id_produktu = p.id_produktu
GROUP BY z.id_zamowienia, z.id_klienta, z.data_zamowienia;
```

### 7. **Integration Views**

#### Łączenie danych z różnych źródeł:
```sql
-- Widok łączący dane lokalne z zewnętrznymi
CREATE VIEW kompletne_dane_klienta AS
SELECT 
    k.id_klienta,
    k.nazwa,
    k.adres_lokalny,
    ext.adres_urzędowy,
    ext.nip,
    ext.regon,
    stats.liczba_zamowien,
    stats.suma_zakupow
FROM klienci k
LEFT JOIN external_registry ext ON k.nip = ext.nip
LEFT JOIN (
    SELECT 
        id_klienta,
        COUNT(*) as liczba_zamowien,
        SUM(wartosc) as suma_zakupow
    FROM zamowienia
    GROUP BY id_klienta
) stats ON k.id_klienta = stats.id_klienta;
```

## Modyfikowalne perspektywy

### Warunki modyfikowalności:
1. **Jedna tabela bazowa**
2. **Brak DISTINCT, GROUP BY, HAVING**
3. **Brak funkcji agregujących**
4. **Brak UNION, INTERSECT, EXCEPT**
5. **Wszystkie klucze główne w widoku**

### Przykład modyfikowalnego widoku:
```sql
-- Modyfikowalny widok
CREATE VIEW pracownicy_aktywni AS
SELECT 
    id_pracownika,
    imie,
    nazwisko,
    email,
    dzial
FROM pracownicy
WHERE status = 'AKTYWNY';

-- Można wykonywać operacje DML
INSERT INTO pracownicy_aktywni (imie, nazwisko, email, dzial)
VALUES ('Jan', 'Kowalski', 'jan@firma.pl', 'IT');

UPDATE pracownicy_aktywni 
SET email = 'nowy.email@firma.pl' 
WHERE id_pracownika = 123;

DELETE FROM pracownicy_aktywni WHERE id_pracownika = 456;
```

### INSTEAD OF triggers dla niemodyfikowalnych widoków:
```sql
-- Niemodyfikowalny widok (GROUP BY)
CREATE VIEW sprzedaz_dzienna AS
SELECT 
    DATE(data_zamowienia) as data,
    COUNT(*) as liczba_zamowien,
    SUM(wartosc) as suma_sprzedazy
FROM zamowienia
GROUP BY DATE(data_zamowienia);

-- Trigger INSTEAD OF dla INSERT
CREATE OR REPLACE FUNCTION sprzedaz_dzienna_insert()
RETURNS TRIGGER AS $$
BEGIN
    -- Dodaj zamówienie zamiast do widoku
    INSERT INTO zamowienia (data_zamowienia, wartosc, id_klienta)
    VALUES (NEW.data, NEW.suma_sprzedazy, 1); -- Domyślny klient
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER instead_of_insert_sprzedaz_dzienna
    INSTEAD OF INSERT ON sprzedaz_dzienna
    FOR EACH ROW
    EXECUTE FUNCTION sprzedaz_dzienna_insert();
```

## Materialized Views

### Definicja:
**Materialized View** to perspektywa, której **wyniki są fizycznie przechowywane** na dysku i **okresowo odświeżane**.

### PostgreSQL Materialized Views:
```sql
-- Tworzenie materialized view
CREATE MATERIALIZED VIEW mv_sprzedaz_summary AS
SELECT 
    p.kategoria,
    DATE_TRUNC('month', z.data_zamowienia) as miesiac,
    COUNT(DISTINCT z.id_zamowienia) as liczba_zamowien,
    SUM(pz.ilosc * p.cena) as suma_sprzedazy
FROM zamowienia z
JOIN pozycje_zamowien pz ON z.id_zamowienia = pz.id_zamowienia
JOIN produkty p ON pz.id_produktu = p.id_produktu
GROUP BY p.kategoria, DATE_TRUNC('month', z.data_zamowienia)
WITH DATA;

-- Indeksy na materialized view
CREATE INDEX idx_mv_kategoria_miesiac 
ON mv_sprzedaz_summary (kategoria, miesiac);

-- Odświeżanie
REFRESH MATERIALIZED VIEW mv_sprzedaz_summary;

-- Odświeżanie bez blokowania (concurrent)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_sprzedaz_summary;

-- Usunięcie
DROP MATERIALIZED VIEW mv_sprzedaz_summary;
```

### Kiedy używać Materialized Views:
- **Kosztowne zapytania** wykonywane często
- **Dane się rzadko zmieniają**
- **Raportowanie** - akceptowalna opóźniona aktualność
- **Data warehousing** - agregaty dla analiz

## Zarządzanie perspektywami

### Metadata o widokach:
```sql
-- PostgreSQL
SELECT 
    schemaname,
    viewname,
    definition
FROM pg_views
WHERE schemaname = 'public';

-- MySQL
SELECT 
    table_name,
    view_definition
FROM information_schema.views
WHERE table_schema = 'mydb';

-- SQL Server
SELECT 
    name,
    definition
FROM sys.views v
JOIN sys.sql_modules m ON v.object_id = m.object_id;
```

### Zależności widoków:
```sql
-- PostgreSQL - znajdź tabele używane przez widok
SELECT DISTINCT
    cl.relname as table_name
FROM pg_depend d
JOIN pg_rewrite r ON d.objid = r.oid
JOIN pg_class cl ON d.refobjid = cl.oid
WHERE d.classid = 'pg_rewrite'::regclass
AND r.ev_class = 'my_view'::regclass;
```

### Aktualizacja definicji widoku:
```sql
-- Zmiana definicji widoku
CREATE OR REPLACE VIEW szczegoly_zamowien AS
SELECT 
    k.nazwa as klient,
    z.id_zamowienia,
    z.data_zamowienia,
    p.nazwa as produkt,
    pz.ilosc,
    p.cena,
    (pz.ilosc * p.cena) as wartosc,
    CASE 
        WHEN p.kategoria = 'Premium' THEN 'VIP'
        ELSE 'Standard'
    END as typ_zamowienia  -- Nowa kolumna
FROM klienci k
JOIN zamowienia z ON k.id_klienta = z.id_klienta
JOIN pozycje_zamowien pz ON z.id_zamowienia = pz.id_zamowienia
JOIN produkty p ON pz.id_produktu = p.id_produktu;
```

## Performance i optymalizacja

### 1. **Indeksy na tabelach bazowych**
```sql
-- Widok często filtruje po dacie
CREATE VIEW zamowienia_ostatni_rok AS
SELECT * FROM zamowienia 
WHERE data_zamowienia >= CURRENT_DATE - INTERVAL '1 year';

-- Potrzebny indeks
CREATE INDEX idx_zamowienia_data ON zamowienia(data_zamowienia);
```

### 2. **Query optimization przez optimizer**
```sql
-- Optimizer może przepisać:
SELECT * FROM szczegoly_zamowien WHERE klient = 'Firma ABC';

-- Na:
SELECT k.nazwa, z.id_zamowienia, ...
FROM klienci k
JOIN zamowienia z ON k.id_klienta = z.id_klienta
JOIN pozycje_zamowien pz ON z.id_zamowienia = pz.id_zamowienia
JOIN produkty p ON pz.id_produktu = p.id_produktu
WHERE k.nazwa = 'Firma ABC';  -- Filtr przeniesiony do tabeli bazowej
```

### 3. **View expansion planning**
```sql
-- Sprawdź plan wykonania
EXPLAIN (ANALYZE, BUFFERS)
SELECT kategoria_produktu, SUM(wartosc)
FROM szczegoly_zamowien
WHERE data_zamowienia >= '2024-01-01'
GROUP BY kategoria_produktu;
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**
1. **Meaningful names** - opisowe nazwy widoków
2. **Documentation** - komentarze opisujące cel
3. **Security** - używaj do kontroli dostępu
4. **Simplification** - ukrywaj złożoność
5. **Consistent interface** - stabilne API dla aplikacji

### ❌ **Złe praktyki:**
1. **Too many layers** - widoki na widokach na widokach
2. **Performance ignorance** - nie sprawdzanie planów wykonania
3. **Overly complex views** - zbyt skomplikowane definicje
4. **No indexing strategy** - brak indeksów na tabelach bazowych
5. **Materialized views** bez strategii odświeżania

## Przykłady zaawansowane

### Multi-database view (PostgreSQL):
```sql
-- Widok łączący dane z różnych baz
CREATE VIEW global_sales AS
SELECT 'EUROPE' as region, * FROM europe_db.sales
UNION ALL
SELECT 'AMERICA' as region, * FROM america_db.sales
UNION ALL  
SELECT 'ASIA' as region, * FROM asia_db.sales;
```

### Recursive view:
```sql
-- Hierarchia organizacyjna
CREATE VIEW org_hierarchy AS
WITH RECURSIVE hierarchy AS (
    -- Anchor: top level managers
    SELECT id_pracownika, imie, nazwisko, id_szefa, 1 as poziom
    FROM pracownicy
    WHERE id_szefa IS NULL
    
    UNION ALL
    
    -- Recursive: subordinates
    SELECT p.id_pracownika, p.imie, p.nazwisko, p.id_szefa, h.poziom + 1
    FROM pracownicy p
    JOIN hierarchy h ON p.id_szefa = h.id_pracownika
)
SELECT * FROM hierarchy;
```

## Pułapki egzaminacyjne

### 1. **View vs Table**
- **View**: Wirtualna, definicja zapytania
- **Table**: Fizyczna, przechowuje dane

### 2. **Modyfikowalność**
- **Proste views**: Można INSERT/UPDATE/DELETE
- **Complex views**: Tylko SELECT (lub INSTEAD OF triggers)

### 3. **Performance**
- **Views**: Wykonują query za każdym razem
- **Materialized Views**: Przechowują wyniki

### 4. **Security**
- **Views** mogą ograniczać dostęp do kolumn/wierszy
- **Nie zastępują** proper authentication/authorization