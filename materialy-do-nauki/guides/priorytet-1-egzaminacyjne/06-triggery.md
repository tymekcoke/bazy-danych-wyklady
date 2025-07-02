# Triggery (Wyzwalacze)

## Definicja

**Trigger (wyzwalacz)** to specjalna procedura składowana, która **automatycznie wykonuje się** w odpowiedzi na określone zdarzenia w bazie danych.

### Kluczowe cechy:
- **Automatyczne uruchamianie** - nie wywołuje się ich ręcznie
- **Powiązane ze zdarzeniami** - INSERT, UPDATE, DELETE
- **Niewidoczne dla aplikacji** - działają w tle
- **Nie można ich bezpośrednio wywołać** - tylko przez zdarzenia

## Do czego służą triggery?

### 1. **Utrzymanie integralności danych**
```sql
-- Sprawdzanie warunków biznesowych
-- Automatyczne walidacje
-- Kontrola zakresu wartości
```

### 2. **Automatyzacja zadań**
```sql
-- Automatyczne obliczenia
-- Aktualizacja powiązanych tabel
-- Generowanie kluczy
```

### 3. **Audyt i logowanie**
```sql
-- Rejestrowanie zmian
-- Śledzenie kto i kiedy zmienił dane
-- Historia operacji
```

### 4. **Utrzymanie danych pochodnych**
```sql
-- Aktualizacja agregatów
-- Synchronizacja tabel
-- Kalkulacja wartości pochodnych
```

### 5. **Archiwizacja danych**
```sql
-- Przenoszenie starych rekordów
-- Backup automatyczny
-- Czyszczenie danych
```

## Rodzaje triggerów

### Według momentu wykonania:

#### 🔴 **BEFORE Triggers** (przed operacją)
- Wykonują się **przed** INSERT/UPDATE/DELETE
- Mogą **modyfikować** dane przed zapisem
- Mogą **przerwać** operację (RETURN NULL)

#### 🟢 **AFTER Triggers** (po operacji)  
- Wykonują się **po** INSERT/UPDATE/DELETE
- **Nie mogą** modyfikować danych operacji
- Używane do logowania, audytu, akcji dodatkowych

### Według operacji:
- **INSERT triggers** - przy wstawianiu rekordów
- **UPDATE triggers** - przy modyfikacji rekordów  
- **DELETE triggers** - przy usuwaniu rekordów

### Według zakresu:
- **FOR EACH ROW** - uruchamia się dla każdego rekordu osobno
- **FOR EACH STATEMENT** - uruchamia się raz na całą operację

## Składnia tworzenia triggerów

### Krok 1: Utworzenie funkcji triggera
```sql
CREATE OR REPLACE FUNCTION nazwa_funkcji()
RETURNS TRIGGER AS $$
BEGIN
    -- Logika triggera
    
    -- Dla BEFORE triggerów:
    RETURN NEW;  -- kontynuuj operację
    RETURN NULL; -- przerwij operację
    
    -- Dla AFTER triggerów:
    RETURN NULL; -- zawsze NULL
END;
$$ LANGUAGE plpgsql;
```

### Krok 2: Utworzenie triggera
```sql
CREATE TRIGGER nazwa_triggera
    BEFORE/AFTER INSERT/UPDATE/DELETE
    ON nazwa_tabeli
    FOR EACH ROW/STATEMENT
    EXECUTE FUNCTION nazwa_funkcji();
```

## Przykłady praktyczne

### Przykład 1: Automatyczne timestampy
```sql
-- Funkcja triggera
CREATE OR REPLACE FUNCTION aktualizuj_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.data_modyfikacji = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
CREATE TRIGGER trigger_timestamp
    BEFORE UPDATE ON produkty
    FOR EACH ROW
    EXECUTE FUNCTION aktualizuj_timestamp();
```

### Przykład 2: Audyt zmian
```sql
-- Tabela audytu
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    tabela VARCHAR(50),
    operacja VARCHAR(10),
    uzytkownik VARCHAR(50),
    timestamp TIMESTAMP DEFAULT NOW(),
    stare_dane JSONB,
    nowe_dane JSONB
);

-- Funkcja audytu
CREATE OR REPLACE FUNCTION audit_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (tabela, operacja, uzytkownik, stare_dane)
        VALUES (TG_TABLE_NAME, TG_OP, USER, row_to_json(OLD));
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (tabela, operacja, uzytkownik, stare_dane, nowe_dane)
        VALUES (TG_TABLE_NAME, TG_OP, USER, row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (tabela, operacja, uzytkownik, nowe_dane)
        VALUES (TG_TABLE_NAME, TG_OP, USER, row_to_json(NEW));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger audytu
CREATE TRIGGER audit_pracownicy
    AFTER INSERT OR UPDATE OR DELETE ON pracownicy
    FOR EACH ROW
    EXECUTE FUNCTION audit_changes();
```

### Przykład 3: Walidacja danych
```sql
-- Sprawdzanie zakresu wynagrodzenia
CREATE OR REPLACE FUNCTION sprawdz_wynagrodzenie()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.wynagrodzenie < 0 THEN
        RAISE EXCEPTION 'Wynagrodzenie nie może być ujemne';
    END IF;
    
    IF NEW.wynagrodzenie > 50000 THEN
        RAISE EXCEPTION 'Wynagrodzenie przekracza maksymalną wartość';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_salary
    BEFORE INSERT OR UPDATE ON pracownicy
    FOR EACH ROW
    EXECUTE FUNCTION sprawdz_wynagrodzenie();
```

### Przykład 4: Aktualizacja agregatów
```sql
-- Aktualizacja liczby zamówień klienta
CREATE OR REPLACE FUNCTION aktualizuj_liczbe_zamowien()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE klienci 
        SET liczba_zamowien = liczba_zamowien + 1
        WHERE id = NEW.id_klienta;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE klienci 
        SET liczba_zamowien = liczba_zamowien - 1
        WHERE id = OLD.id_klienta;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_order_count
    AFTER INSERT OR DELETE ON zamowienia
    FOR EACH ROW
    EXECUTE FUNCTION aktualizuj_liczbe_zamowien();
```

## Zmienne specjalne w triggerach

### **NEW** i **OLD**
- **NEW** - nowy rekord (INSERT, UPDATE)
- **OLD** - stary rekord (UPDATE, DELETE)
- **NULL** - gdy nie ma sensu (OLD przy INSERT, NEW przy DELETE)

### **TG_OP** - typ operacji
- **'INSERT'** - wstawianie
- **'UPDATE'** - aktualizacja  
- **'DELETE'** - usuwanie

### **TG_TABLE_NAME** - nazwa tabeli
- Przydatne dla uniwersalnych triggerów

### **TG_WHEN** - moment wykonania
- **'BEFORE'** lub **'AFTER'**

## Zarządzanie triggerami

### Wyłączanie/włączanie
```sql
-- Wyłącz trigger
ALTER TABLE pracownicy DISABLE TRIGGER trigger_timestamp;

-- Włącz trigger
ALTER TABLE pracownicy ENABLE TRIGGER trigger_timestamp;

-- Wyłącz wszystkie triggery na tabeli
ALTER TABLE pracownicy DISABLE TRIGGER ALL;
```

### Usuwanie triggerów
```sql
DROP TRIGGER trigger_timestamp ON pracownicy;
DROP FUNCTION aktualizuj_timestamp();
```

### Podgląd triggerów
```sql
-- Lista triggerów
SELECT * FROM information_schema.triggers 
WHERE event_object_table = 'pracownicy';

-- Szczegóły triggerów w PostgreSQL
SELECT * FROM pg_trigger;
```

## Zalety triggerów

### ✅ **Plusy:**
1. **Automatyzacja** - nie trzeba pamiętać o wywołaniu
2. **Spójność** - zawsze wykonują się
3. **Centralizacja logiki** - w jednym miejscu
4. **Bezpieczeństwo** - nie można ich ominąć
5. **Wydajność** - wykonują się na serwerze

## Wady triggerów

### ❌ **Minusy:**
1. **Ukryta logika** - trudna do debugowania
2. **Wydajność** - dodatkowy overhead
3. **Złożoność** - trudne w utrzymaniu
4. **Kaskadowe triggery** - mogą się wywoływać wzajemnie
5. **Problemy z migracją** - trudne do przeniesienia

## Najlepsze praktyki

### ✅ **Dobre praktyki:**
1. **Dokumentuj triggery** - opisuj co robią
2. **Unikaj złożonych operacji** - zachowaj prostotę
3. **Obsługuj błędy** - używaj TRY/CATCH
4. **Testuj dokładnie** - sprawdzaj wszystkie scenariusze
5. **Monitoruj wydajność** - sprawdzaj wpływ na system

### ❌ **Czego unikać:**
1. **Długich operacji** - triggery blokują transakcje
2. **Wywołań zewnętrznych** - API, pliki, sieć
3. **Rekurencji** - triggery wywołujące siebie
4. **Zbyt wielu triggerów** - skomplikowana logika
5. **Triggerów na dużych tabelach** - problemy z wydajnością

## Pułapki egzaminacyjne

### 1. **Różnica BEFORE vs AFTER**
- **BEFORE** może modyfikować dane i przerwać operację
- **AFTER** służy do akcji dodatkowych, nie może modyfikować

### 2. **RETURN w triggerach**
- **BEFORE**: RETURN NEW (kontynuuj) / NULL (przerwij)
- **AFTER**: Zawsze RETURN NULL

### 3. **FOR EACH ROW vs FOR EACH STATEMENT**
- **ROW**: Jeden trigger na rekord
- **STATEMENT**: Jeden trigger na całą operację

### 4. **Dostępność NEW/OLD**
- **INSERT**: NEW dostępne, OLD = NULL
- **UPDATE**: NEW i OLD dostępne
- **DELETE**: OLD dostępne, NEW = NULL