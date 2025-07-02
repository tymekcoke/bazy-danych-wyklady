# 🔄 REDUNDANCJA DANYCH - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekunds)

"Redundancja danych to zjawisko duplikowania tych samych informacji w różnych miejscach bazy danych. Może być:

1. **Niekontrolowana (zła)** - prowadzi do anomalii: insert, update, delete
2. **Kontrolowana (dobra)** - świadoma duplikacja dla wydajności (denormalizacja)

Anomalie to: niemożność dodania danych bez dodatkowych informacji (insert), niespójność po aktualizacji (update), utrata informacji przy usuwaniu (delete). Rozwiązanie: normalizacja eliminuje złą redundancję przez rozbicie na logiczne tabele."

## ✍️ CO NAPISAĆ NA KARTCE

```
TYPY REDUNDANCJI I ANOMALII:

TABELA NIEZNORMALIZOWANA (ZŁA REDUNDANCJA):
studenci_przedmioty:
| id_stud | imie  | nazwisko | adres      | przedmiot | ocena | prowadzacy |
|---------|-------|----------|------------|-----------|-------|------------|
| 1       | Jan   | Kowalski | Warszawa   | Bazy      | 5     | Dr Smith   |
| 1       | Jan   | Kowalski | Warszawa   | Java      | 4     | Prof Jones |
| 2       | Anna  | Nowak    | Kraków     | Bazy      | 5     | Dr Smith   |

PROBLEMY (ANOMALIE):

1. INSERT ANOMALY:
   - Nie można dodać przedmiotu bez studenta
   - Nie można dodać studenta bez przedmiotu
   
2. UPDATE ANOMALY:  
   - Zmiana adresu studenta → trzeba aktualizować wiele wierszy
   - Ryzyko niespójności (część zaktualizowana, część nie)
   
3. DELETE ANOMALY:
   - Usunięcie ostatniego studenta z przedmiotu → utrata info o prowadzącym
   - Usunięcie przedmiotu studenta → może utrata danych studenta

ROZWIĄZANIE - NORMALIZACJA:

studenci:               przedmioty:              oceny:
| id | imie | adres |   | kod | nazwa | prowadz | | id_stud | kod | ocena |
|----|------|-------|   |-----|-------|---------|  |---------|-----|-------|
| 1  | Jan  | Wwa   |   | BZ  | Bazy  | Dr S    |  | 1       | BZ  | 5     |
| 2  | Anna | Krak  |   | JV  | Java  | Prof J  |  | 1       | JV  | 4     |

ANOMALIE WYELIMINOWANE:
✓ Można dodać studenta bez przedmiotu
✓ Można dodać przedmiot bez studenta  
✓ Zmiana adresu → jedna aktualizacja
✓ Usunięcie oceny → nie traci się danych podstawowych

KONTROLOWANA REDUNDANCJA (DOBRA):
- Kolumny pochodne dla wydajności
- Materialized views
- Cache'owanie obliczeń
- Denormalizacja w data warehouse
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- DEMONSTRACJA ANOMALII I ICH ROZWIĄZANIA

-- 1. TABELA Z REDUNDANCJĄ (ZŁA PRAKTYKA)
CREATE TABLE zamowienia_zla_redundancja (
    id_zamowienia INT,
    data_zamowienia DATE,
    
    -- Dane klienta (REDUNDANCJA!)
    id_klienta INT,
    nazwa_klienta VARCHAR(100),
    adres_klienta TEXT,
    telefon_klienta VARCHAR(20),
    
    -- Dane produktu (REDUNDANCJA!)  
    id_produktu INT,
    nazwa_produktu VARCHAR(100),
    cena_produktu DECIMAL(10,2),
    kategoria_produktu VARCHAR(50),
    
    ilosc INT,
    PRIMARY KEY (id_zamowienia, id_produktu)
);

-- Przykładowe dane z redundancją
INSERT INTO zamowienia_zla_redundancja VALUES
(1, '2024-01-15', 100, 'Firma ABC', 'Warszawa ul. Główna 1', '123456789', 
 200, 'Laptop Dell', 3500.00, 'Elektronika', 1),
(1, '2024-01-15', 100, 'Firma ABC', 'Warszawa ul. Główna 1', '123456789',
 201, 'Mysz optyczna', 50.00, 'Elektronika', 2),
(2, '2024-01-16', 100, 'Firma ABC', 'Warszawa ul. Główna 1', '123456789',
 200, 'Laptop Dell', 3500.00, 'Elektronika', 1);

-- DEMONSTRACJA ANOMALII:

-- INSERT ANOMALY - nie można dodać klienta bez zamówienia
-- INSERT INTO zamowienia_zla_redundancja (id_klienta, nazwa_klienta, adres_klienta)
-- VALUES (101, 'Nowa Firma', 'Kraków ul. Nowa 5');  -- BŁĄD! Brakuje danych zamówienia

-- UPDATE ANOMALY - zmiana adresu klienta
UPDATE zamowienia_zla_redundancja 
SET adres_klienta = 'Warszawa ul. Nowa 5'
WHERE id_klienta = 100;
-- Trzeba pamiętać o aktualizacji WSZYSTKICH wierszy tego klienta!

-- DELETE ANOMALY - usunięcie ostatniego zamówienia produktu
DELETE FROM zamowienia_zla_redundancja 
WHERE id_produktu = 201;
-- Utrata informacji o produkcie (nazwa, cena, kategoria)

-- 2. ROZWIĄZANIE - NORMALIZACJA

-- Tabela klientów (bez redundancji)
CREATE TABLE klienci (
    id_klienta SERIAL PRIMARY KEY,
    nazwa VARCHAR(100) NOT NULL,
    adres TEXT,
    telefon VARCHAR(20)
);

-- Tabela produktów (bez redundancji)
CREATE TABLE produkty (
    id_produktu SERIAL PRIMARY KEY,
    nazwa VARCHAR(100) NOT NULL,
    cena DECIMAL(10,2) NOT NULL,
    kategoria VARCHAR(50)
);

-- Tabela zamówień (bez redundancji danych klienta/produktu)
CREATE TABLE zamowienia (
    id_zamowienia SERIAL PRIMARY KEY,
    id_klienta INT NOT NULL,
    data_zamowienia DATE DEFAULT CURRENT_DATE,
    
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta)
);

-- Tabela pozycji zamówienia (związek M:N bez redundancji)
CREATE TABLE pozycje_zamowienia (
    id_zamowienia INT,
    id_produktu INT,
    ilosc INT NOT NULL,
    cena_w_momencie_sprzedazy DECIMAL(10,2), -- snapshot ceny
    
    PRIMARY KEY (id_zamowienia, id_produktu),
    FOREIGN KEY (id_zamowienia) REFERENCES zamowienia(id_zamowienia),
    FOREIGN KEY (id_produktu) REFERENCES produkty(id_produktu)
);

-- Wypełnienie danych (każda informacja w jednym miejscu)
INSERT INTO klienci VALUES (100, 'Firma ABC', 'Warszawa ul. Główna 1', '123456789');
INSERT INTO produkty VALUES 
(200, 'Laptop Dell', 3500.00, 'Elektronika'),
(201, 'Mysz optyczna', 50.00, 'Elektronika');

INSERT INTO zamowienia VALUES (1, 100, '2024-01-15'), (2, 100, '2024-01-16');
INSERT INTO pozycje_zamowienia VALUES 
(1, 200, 1, 3500.00),
(1, 201, 2, 50.00),
(2, 200, 1, 3500.00);

-- TERAZ ANOMALIE SĄ ROZWIĄZANE:

-- ✅ INSERT: można dodać klienta bez zamówienia
INSERT INTO klienci VALUES (101, 'Nowa Firma', 'Kraków ul. Nowa 5', '987654321');

-- ✅ INSERT: można dodać produkt bez zamówienia  
INSERT INTO produkty VALUES (202, 'Klawiatura', 120.00, 'Elektronika');

-- ✅ UPDATE: zmiana adresu klienta w jednym miejscu
UPDATE klienci SET adres = 'Warszawa ul. Nowa 5' WHERE id_klienta = 100;

-- ✅ DELETE: usunięcie pozycji nie traci danych o produkcie
DELETE FROM pozycje_zamowienia WHERE id_produktu = 201;
-- Produkt nadal istnieje w tabeli produkty

-- 3. KONTROLOWANA REDUNDANCJA (dla wydajności)

-- Kolumna pochodna - suma zamówienia (denormalizacja)
ALTER TABLE zamowienia ADD COLUMN kwota_total DECIMAL(12,2);

-- Trigger do automatycznego przeliczania
CREATE OR REPLACE FUNCTION aktualizuj_kwote_zamowienia()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE zamowienia 
    SET kwota_total = (
        SELECT COALESCE(SUM(ilosc * cena_w_momencie_sprzedazy), 0)
        FROM pozycje_zamowienia
        WHERE id_zamowienia = COALESCE(NEW.id_zamowienia, OLD.id_zamowienia)
    )
    WHERE id_zamowienia = COALESCE(NEW.id_zamowienia, OLD.id_zamowienia);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_aktualizuj_kwote
    AFTER INSERT OR UPDATE OR DELETE ON pozycje_zamowienia
    FOR EACH ROW
    EXECUTE FUNCTION aktualizuj_kwote_zamowienia();

-- Materialized view dla raportów (kontrolowana redundancja)
CREATE MATERIALIZED VIEW sprzedaz_miesiac AS
SELECT 
    EXTRACT(YEAR FROM z.data_zamowienia) as rok,
    EXTRACT(MONTH FROM z.data_zamowienia) as miesiac,
    p.kategoria,
    COUNT(DISTINCT z.id_zamowienia) as liczba_zamowien,
    SUM(pz.ilosc * pz.cena_w_momencie_sprzedazy) as suma_sprzedazy
FROM zamowienia z
JOIN pozycje_zamowienia pz ON z.id_zamowienia = pz.id_zamowienia
JOIN produkty p ON pz.id_produktu = p.id_produktu
GROUP BY EXTRACT(YEAR FROM z.data_zamowienia),
         EXTRACT(MONTH FROM z.data_zamowienia),
         p.kategoria;

-- Odświeżanie co noc
REFRESH MATERIALIZED VIEW sprzedaz_miesiac;

-- 4. WYKRYWANIE REDUNDANCJI

-- Query do znajdowania potencjalnych duplikatów
SELECT 
    id_klienta,
    nazwa,
    COUNT(*) as liczba_duplikatow
FROM klienci 
GROUP BY id_klienta, nazwa
HAVING COUNT(*) > 1;

-- Sprawdzenie czy dane są znormalizowane
-- (czy można odtworzyć oryginalne dane przez JOIN)
SELECT 
    z.id_zamowienia,
    z.data_zamowienia,
    k.nazwa as nazwa_klienta,
    k.adres as adres_klienta,
    p.nazwa as nazwa_produktu,
    p.cena as cena_produktu,
    pz.ilosc
FROM zamowienia z
JOIN klienci k ON z.id_klienta = k.id_klienta
JOIN pozycje_zamowienia pz ON z.id_zamowienia = pz.id_zamowienia
JOIN produkty p ON pz.id_produktu = p.id_produktu
ORDER BY z.id_zamowienia, p.id_produktu;
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Redundancja ≠ zawsze zła (może być kontrolowana)
2. **UWAGA**: Anomalie występują razem - jeśli jedna, to prawdopodobnie wszystkie
3. **BŁĄD**: Myślenie że normalizacja zawsze poprawia wydajność
4. **WAŻNE**: Kolumny pochodne to kontrolowana redundancja
5. **PUŁAPKA**: Materialized views wymagają odświeżania aby być aktualne

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Data redundancy** - redundancja danych
- **Insert/Update/Delete anomalies** - anomalie wstawiania/aktualizacji/usuwania
- **Normalization** - normalizacja
- **Denormalization** - denormalizacja
- **Controlled redundancy** - kontrolowana redundancja
- **Derived attributes** - atrybuty pochodne
- **Materialized views** - zmaterializowane widoki
- **Data consistency** - spójność danych

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **19-normalizacja** - eliminacja redundancji przez normalizację
- **27-zaleznosci-funkcyjne** - podstawa identyfikacji redundancji
- **42-optymalizacja-wydajnosci** - kontrolowana redundancja dla wydajności
- **22-perspektywy-views** - materialized views
- **01-integralnosc** - spójność danych