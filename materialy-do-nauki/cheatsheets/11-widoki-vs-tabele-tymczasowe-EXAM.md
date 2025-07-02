# 📊 WIDOKI VS TABELE TYMCZASOWE - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekunds)

"Widoki i tabele tymczasowe to różne mechanizmy pracy z danymi:

**Widoki** to wirtualne tabele - zapisane zapytania SQL, które są wykonywane za każdym razem. Nie przechowują danych, tylko definicję zapytania.

**Tabele tymczasowe** to prawdziwe tabele istniejące tylko w sesji lub transakcji, które fizycznie przechowują dane.

Główne różnice: widoki są dynamiczne i zawsze aktualne, tabele tymczasowe są statyczne ale szybsze do odczytu powtarzalnego."

## ✍️ CO NAPISAĆ NA KARTCE

```
PORÓWNANIE WIDOKÓW I TABEL TYMCZASOWYCH:

ASPEKT          | WIDOKI           | TABELE TYMCZASOWE
----------------|------------------|-------------------
Przechowywanie  | Tylko definicja  | Rzeczywiste dane
Aktualność      | Zawsze aktualne  | Snapshot w czasie
Wydajność       | Wolniejsze       | Szybsze (cached)
Pamięć          | Brak overhead    | Zużywa pamięć/dysk
Czas życia      | Permanentne      | Sesja/transakcja
Indexy          | Nie można        | Można dodawać
Modyfikacje     | Ograniczone      | Pełne DML
Współdzielenie  | Widoczne globalnie| Tylko w sesji

KIEDY UŻYWAĆ:

WIDOKI:
✓ Dane muszą być zawsze aktualne
✓ Abstrakcja nad złożonymi zapytaniami  
✓ Kontrola dostępu (security views)
✓ Oszczędność miejsca
✓ Simplifikacja dla użytkowników

TABELE TYMCZASOWE:
✓ Złożone obliczenia wieloetapowe
✓ Buforowanie wyników kosztownych zapytań
✓ Przetwarzanie batch'owe
✓ Potrzeba indeksów na wynikach
✓ Wielokrotne odczyty tych samych danych

MATERIALIZED VIEWS (hybrida):
✓ Szybkość tabel + automatyczne odświeżanie
✓ Dane cache'owane ale można odświeżyć
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- PRZYKŁAD 1: ZWYKŁE WIDOKI

-- Widok dla podsumowania sprzedaży
CREATE VIEW widok_sprzedaz_miesiac AS
SELECT 
    EXTRACT(YEAR FROM data_zamowienia) as rok,
    EXTRACT(MONTH FROM data_zamowienia) as miesiac,
    COUNT(*) as liczba_zamowien,
    SUM(kwota) as suma_sprzedazy,
    AVG(kwota) as srednia_wartosc
FROM zamowienia 
WHERE status = 'zakonczone'
GROUP BY EXTRACT(YEAR FROM data_zamowienia), 
         EXTRACT(MONTH FROM data_zamowienia);

-- Użycie widoku (zawsze aktualne dane)
SELECT * FROM widok_sprzedaz_miesiac 
WHERE rok = 2024 AND suma_sprzedazy > 10000;

-- Widok bezpieczeństwa (ukrywa wrażliwe dane)
CREATE VIEW widok_pracownicy_publiczny AS
SELECT 
    id_pracownika,
    imie,
    nazwisko, 
    departament,
    stanowisko
    -- ukrywamy: pensja, PESEL, adres
FROM pracownicy
WHERE aktywny = true;

-- PRZYKŁAD 2: TABELE TYMCZASOWE

-- Tabela tymczasowa dla sesji (LOCAL TEMPORARY)
CREATE TEMPORARY TABLE temp_analiza_sprzedazy (
    rok INT,
    miesiac INT,
    kategoria_produktu VARCHAR(50),
    suma_sprzedazy DECIMAL(12,2),
    liczba_transakcji INT
);

-- Wypełnienie danymi (kosztowne zapytanie wykonane raz)
INSERT INTO temp_analiza_sprzedazy
SELECT 
    EXTRACT(YEAR FROM z.data_zamowienia),
    EXTRACT(MONTH FROM z.data_zamowienia),
    p.kategoria,
    SUM(zp.ilosc * zp.cena_jednostkowa),
    COUNT(DISTINCT z.id_zamowienia)
FROM zamowienia z
JOIN zamowienia_produkty zp ON z.id_zamowienia = zp.id_zamowienia
JOIN produkty p ON zp.id_produktu = p.id_produktu
WHERE z.data_zamowienia >= '2024-01-01'
GROUP BY EXTRACT(YEAR FROM z.data_zamowienia),
         EXTRACT(MONTH FROM z.data_zamowienia),
         p.kategoria;

-- Dodanie indeksu dla szybkich zapytań
CREATE INDEX idx_temp_rok_miesiac ON temp_analiza_sprzedazy(rok, miesiac);

-- Wielokrotne szybkie zapytania na danych cached
SELECT kategoria_produktu, SUM(suma_sprzedazy)
FROM temp_analiza_sprzedazy
WHERE rok = 2024 AND miesiac BETWEEN 6 AND 8
GROUP BY kategoria_produktu;

-- PRZYKŁAD 3: MATERIALIZED VIEWS (najlepsze z obu światów)

-- Materialized view z danymi cache'owanymi
CREATE MATERIALIZED VIEW mv_raport_sprzedazy AS
SELECT 
    d.nazwa as departament,
    p.kategoria,
    DATE_TRUNC('month', z.data_zamowienia) as miesiac,
    COUNT(*) as liczba_zamowien,
    SUM(zp.ilosc * zp.cena_jednostkowa) as przychod,
    AVG(zp.ilosc * zp.cena_jednostkowa) as srednia_wartosc
FROM zamowienia z
JOIN zamowienia_produkty zp ON z.id_zamowienia = zp.id_zamowienia  
JOIN produkty p ON zp.id_produktu = p.id_produktu
JOIN pracownicy pr ON z.id_sprzedawcy = pr.id_pracownika
JOIN departamenty d ON pr.id_departamentu = d.id_departamentu
GROUP BY d.nazwa, p.kategoria, DATE_TRUNC('month', z.data_zamowienia);

-- Indeks na materialized view
CREATE INDEX idx_mv_raport_miesiac ON mv_raport_sprzedazy(miesiac);

-- Odświeżanie danych (można automatyzować)
REFRESH MATERIALIZED VIEW mv_raport_sprzedazy;

-- Concurrent refresh (nie blokuje zapytań)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_raport_sprzedazy;

-- PRZYKŁAD 4: PORÓWNANIE WYDAJNOŚCI

-- Zapytanie przez widok (wykonywane za każdym razem)
EXPLAIN ANALYZE
SELECT departament, SUM(przychod)
FROM widok_kompleksowy_raport  -- złożone JOIN'y wykonywane zawsze
WHERE miesiac >= '2024-01-01'
GROUP BY departament;

-- To samo przez tabelę tymczasową (dane już obliczone)
EXPLAIN ANALYZE  
SELECT departament, SUM(przychod)
FROM temp_raport  -- dane już w pamięci
WHERE miesiac >= '2024-01-01'
GROUP BY departament;

-- PRZYKŁAD 5: CTE vs TEMP TABLE dla wieloetapowych obliczeń

-- Wielokrotne użycie CTE (może być nieefektywne)
WITH expensive_calculation AS (
    SELECT /* kosztowne zapytanie */ 
)
SELECT * FROM expensive_calculation WHERE condition1
UNION ALL
SELECT * FROM expensive_calculation WHERE condition2  -- ponowne wykonanie!
UNION ALL  
SELECT * FROM expensive_calculation WHERE condition3; -- i jeszcze raz!

-- Lepiej użyć temp table:
CREATE TEMPORARY TABLE temp_expensive_result AS
SELECT /* kosztowne zapytanie - wykonane raz */;

SELECT * FROM temp_expensive_result WHERE condition1
UNION ALL
SELECT * FROM temp_expensive_result WHERE condition2  -- szybkie
UNION ALL
SELECT * FROM temp_expensive_result WHERE condition3; -- szybkie

-- Cleanup (automatyczne przy końcu sesji)
DROP TABLE temp_expensive_result;
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Widoki nie przechowują danych, tylko definicję zapytania
2. **UWAGA**: Tabele tymczasowe znikają po zakończeniu sesji/transakcji
3. **BŁĄD**: Mylenie widoków z materialized views (to różne rzeczy!)
4. **WAŻNE**: Indeksy można tworzyć tylko na tabelach/materialized views
5. **PUŁAPKA**: Widoki mogą być wolne jeśli bazują na złożonych zapytaniach

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Virtual table** - tabela wirtualna (widok)
- **Temporary table** - tabela tymczasowa
- **Materialized view** - zmaterializowany widok
- **Query definition** - definicja zapytania
- **Session-scoped** - zasięg sesji
- **Data caching** - cache'owanie danych
- **Refresh strategy** - strategia odświeżania
- **Security view** - widok bezpieczeństwa

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **22-perspektywy-views** - szczegóły o widokach
- **30-sql-dml-zaawansowany** - złożone zapytania w widokach
- **42-optymalizacja-wydajnosci** - kiedy używać temp tables
- **39-bezpieczenstwo-baz** - security views
- **32-funkcje-agregujace** - agregacje w widokach