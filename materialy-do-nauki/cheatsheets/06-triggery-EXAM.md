# ⚡ TRIGGERY - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Trigger to specjalna procedura składowana, która jest automatycznie wykonywana (wywoływana) w odpowiedzi na określone zdarzenia w bazie danych. Triggery dzielą się na:

1. **BEFORE** - wykonywane przed operacją (INSERT/UPDATE/DELETE)
2. **AFTER** - wykonywane po operacji  
3. **INSTEAD OF** - zastępują operację (tylko w widokach)

Triggery są używane do automatycznego sprawdzania integralności, audytowania zmian, automatycznych obliczeń i synchronizacji danych między tabelami."

## ✍️ CO NAPISAĆ NA KARTCE

```sql
-- SKŁADNIA TRIGGERA
CREATE [OR REPLACE] TRIGGER nazwa_triggera
    {BEFORE | AFTER | INSTEAD OF} {INSERT | UPDATE | DELETE}
    ON nazwa_tabeli
    [FOR EACH ROW | FOR EACH STATEMENT]
    [WHEN (warunek)]
EXECUTE FUNCTION nazwa_funkcji();

-- PRZYKŁAD BEFORE TRIGGER
CREATE OR REPLACE FUNCTION aktualizuj_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.data_modyfikacji = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_aktualizuj_timestamp
    BEFORE UPDATE ON pracownicy
    FOR EACH ROW
    EXECUTE FUNCTION aktualizuj_timestamp();

-- PRZYKŁAD AFTER TRIGGER (audit)
CREATE OR REPLACE FUNCTION audit_pracownicy()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (tabela, operacja, stare_wartosci, nowe_wartosci, timestamp)
    VALUES ('pracownicy', TG_OP, row_to_json(OLD), row_to_json(NEW), NOW());
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_audit_pracownicy
    AFTER INSERT OR UPDATE OR DELETE ON pracownicy
    FOR EACH ROW
    EXECUTE FUNCTION audit_pracownicy();

-- ZMIENNE SPECJALNE W TRIGGERACH:
-- NEW - nowy rekord (INSERT, UPDATE)
-- OLD - stary rekord (UPDATE, DELETE) 
-- TG_OP - typ operacji ('INSERT', 'UPDATE', 'DELETE')
-- TG_TABLE_NAME - nazwa tabeli
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- KOMPLEKSNY PRZYKŁAD: System zamówień z automatyczną aktualizacją stanów

-- Tabela zamówień
CREATE TABLE zamowienia (
    id_zamowienia INT PRIMARY KEY,
    id_klienta INT,
    kwota_total DECIMAL(10,2) DEFAULT 0,
    data_utworzenia TIMESTAMP DEFAULT NOW(),
    data_modyfikacji TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'nowe'
);

-- Tabela pozycji zamówienia  
CREATE TABLE pozycje_zamowienia (
    id_pozycji INT PRIMARY KEY,
    id_zamowienia INT,
    id_produktu INT,
    ilosc INT,
    cena_jednostkowa DECIMAL(10,2),
    FOREIGN KEY (id_zamowienia) REFERENCES zamowienia(id_zamowienia)
);

-- TRIGGER 1: Aktualizacja kwoty zamówienia po dodaniu pozycji
CREATE OR REPLACE FUNCTION aktualizuj_kwote_zamowienia()
RETURNS TRIGGER AS $$
BEGIN
    -- Przelicz kwotę całkowitą zamówienia
    UPDATE zamowienia 
    SET kwota_total = (
        SELECT COALESCE(SUM(ilosc * cena_jednostkowa), 0)
        FROM pozycje_zamowienia 
        WHERE id_zamowienia = COALESCE(NEW.id_zamowienia, OLD.id_zamowienia)
    ),
    data_modyfikacji = NOW()
    WHERE id_zamowienia = COALESCE(NEW.id_zamowienia, OLD.id_zamowienia);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_aktualizuj_kwote
    AFTER INSERT OR UPDATE OR DELETE ON pozycje_zamowienia
    FOR EACH ROW
    EXECUTE FUNCTION aktualizuj_kwote_zamowienia();

-- TRIGGER 2: Walidacja przed wstawieniem (BEFORE)
CREATE OR REPLACE FUNCTION waliduj_pozycje()
RETURNS TRIGGER AS $$
BEGIN
    -- Sprawdź czy ilość jest dodatnia
    IF NEW.ilosc <= 0 THEN
        RAISE EXCEPTION 'Ilość musi być większa od 0';
    END IF;
    
    -- Sprawdź czy cena jest dodatnia
    IF NEW.cena_jednostkowa <= 0 THEN
        RAISE EXCEPTION 'Cena musi być większa od 0';
    END IF;
    
    -- Automatycznie ustaw datę modyfikacji
    NEW.data_utworzenia = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_waliduj_pozycje
    BEFORE INSERT OR UPDATE ON pozycje_zamowienia
    FOR EACH ROW
    EXECUTE FUNCTION waliduj_pozycje();

-- TRIGGER 3: INSTEAD OF dla widoku (złożone operacje)
CREATE VIEW widok_zamowienia AS
SELECT z.id_zamowienia, z.kwota_total, z.status,
       COUNT(p.id_pozycji) as liczba_pozycji
FROM zamowienia z
LEFT JOIN pozycje_zamowienia p ON z.id_zamowienia = p.id_zamowienia
GROUP BY z.id_zamowienia, z.kwota_total, z.status;

CREATE OR REPLACE FUNCTION usun_przez_widok()
RETURNS TRIGGER AS $$
BEGIN
    -- Usuń pozycje (trigger automatycznie zaktualizuje kwotę)
    DELETE FROM pozycje_zamowienia WHERE id_zamowienia = OLD.id_zamowienia;
    -- Usuń zamówienie
    DELETE FROM zamowienia WHERE id_zamowienia = OLD.id_zamowienia;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_usun_przez_widok
    INSTEAD OF DELETE ON widok_zamowienia
    FOR EACH ROW
    EXECUTE FUNCTION usun_przez_widok();
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: BEFORE może modyfikować NEW, AFTER nie może
2. **UWAGA**: W DELETE nie ma NEW, w INSERT nie ma OLD
3. **BŁĄD**: Zapominanie o RETURN NEW/OLD w funkcji triggera
4. **WAŻNE**: Triggery mogą wywoływać inne triggery (kaskada)
5. **PUŁAPKA**: Nieskończone pętle w triggerach (trigger wywoła sam siebie)

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **BEFORE/AFTER/INSTEAD OF** - typy triggerów
- **FOR EACH ROW** - trigger wierszowy
- **FOR EACH STATEMENT** - trigger instrukcyjny
- **NEW/OLD** - rekordy w triggerze
- **TG_OP** - typ operacji
- **RAISE EXCEPTION** - wyrzucanie błędów
- **Cascading triggers** - kaskadowe triggery
- **Audit trail** - ślad audytowy

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **35-rules-vs-triggery** - porównanie z regułami
- **01-integralnosc** - sprawdzanie integralności
- **33-plpgsql-podstawy** - język funkcji triggerów
- **34-funkcje-uzytkownika** - funkcje wywołane przez triggery
- **16-procedury-skladowane** - automatyzacja procesów