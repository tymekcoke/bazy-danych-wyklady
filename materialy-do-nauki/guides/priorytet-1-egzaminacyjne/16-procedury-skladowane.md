# Procedury składowane

## Definicja

**Procedura składowana** to **nazwany blok kodu SQL**, który jest **przechowywany w bazie danych** i może być **wielokrotnie wywoływany** przez aplikacje lub innych użytkowników.

### Charakterystyka:
- **Precompiled** - skompilowane i zoptymalizowane przez SZBD
- **Reusable** - można wywoływać wielokrotnie
- **Centralized** - logika biznesowa w bazie danych
- **Secure** - kontrolowany dostęp do danych

## Składnia tworzenia procedur

### PostgreSQL (PL/pgSQL):
```sql
CREATE OR REPLACE FUNCTION nazwa_procedury(
    parametr1 typ1,
    parametr2 typ2 DEFAULT wartość_domyślna
)
RETURNS typ_zwracany AS $$
DECLARE
    -- deklaracje zmiennych lokalnych
    zmienna1 typ1;
    zmienna2 typ2 := wartość_początkowa;
BEGIN
    -- ciało procedury
    -- logika biznesowa
    
    RETURN wynik;  -- dla funkcji
    
EXCEPTION
    WHEN exception_type THEN
        -- obsługa błędów
        RAISE NOTICE 'Błąd: %', SQLERRM;
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

### MySQL:
```sql
DELIMITER $$

CREATE PROCEDURE nazwa_procedury(
    IN param1 INT,
    OUT param2 VARCHAR(100),
    INOUT param3 DECIMAL(10,2)
)
BEGIN
    DECLARE zmienna1 INT DEFAULT 0;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
    BEGIN
        -- obsługa błędów
        ROLLBACK;
    END;
    
    START TRANSACTION;
    
    -- logika procedury
    
    COMMIT;
END$$

DELIMITER ;
```

### SQL Server:
```sql
CREATE PROCEDURE nazwa_procedury
    @param1 INT,
    @param2 VARCHAR(100) = 'default_value',
    @param3 DECIMAL(10,2) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @zmienna1 INT;
    
    BEGIN TRY
        BEGIN TRANSACTION;
        
        -- logika procedury
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
```

## Typy parametrów

### 1. **IN Parameters** (wejściowe)
```sql
-- PostgreSQL
CREATE OR REPLACE FUNCTION oblicz_bonus(
    pensja DECIMAL(10,2),
    procent DECIMAL(5,2) DEFAULT 10.0
)
RETURNS DECIMAL(10,2) AS $$
BEGIN
    RETURN pensja * procent / 100;
END;
$$ LANGUAGE plpgsql;

-- Wywołanie
SELECT oblicz_bonus(5000, 15.0);  -- = 750
SELECT oblicz_bonus(5000);        -- = 500 (domyślny 10%)
```

### 2. **OUT Parameters** (wyjściowe)
```sql
-- MySQL
DELIMITER $$
CREATE PROCEDURE pobierz_statystyki_klienta(
    IN klient_id INT,
    OUT liczba_zamowien INT,
    OUT suma_wydatkow DECIMAL(15,2)
)
BEGIN
    SELECT COUNT(*), COALESCE(SUM(wartosc), 0)
    INTO liczba_zamowien, suma_wydatkow
    FROM zamowienia
    WHERE id_klienta = klient_id;
END$$
DELIMITER ;

-- Wywołanie
CALL pobierz_statystyki_klienta(123, @liczba, @suma);
SELECT @liczba, @suma;
```

### 3. **INOUT Parameters** (wejściowo-wyjściowe)
```sql
-- Procedura aktualizująca wartość
DELIMITER $$
CREATE PROCEDURE podwoj_wartosc(
    INOUT wartosc INT
)
BEGIN
    SET wartosc = wartosc * 2;
END$$
DELIMITER ;

-- Wywołanie
SET @liczba = 5;
CALL podwoj_wartosc(@liczba);
SELECT @liczba;  -- = 10
```

## Przykłady praktyczne

### Przykład 1: Transfer pieniędzy
```sql
CREATE OR REPLACE FUNCTION transfer_pieniedzy(
    konto_zrodlowe INT,
    konto_docelowe INT,
    kwota DECIMAL(15,2)
)
RETURNS BOOLEAN AS $$
DECLARE
    saldo_zrodlowe DECIMAL(15,2);
BEGIN
    -- Sprawdź saldo konta źródłowego
    SELECT saldo INTO saldo_zrodlowe
    FROM konta
    WHERE id_konta = konto_zrodlowe
    FOR UPDATE;  -- Blokada dla transakcji
    
    -- Sprawdź czy jest wystarczająco środków
    IF saldo_zrodlowe < kwota THEN
        RAISE EXCEPTION 'Niewystarczające środki na koncie %', konto_zrodlowe;
    END IF;
    
    -- Sprawdź czy konto docelowe istnieje
    IF NOT EXISTS (SELECT 1 FROM konta WHERE id_konta = konto_docelowe) THEN
        RAISE EXCEPTION 'Konto docelowe % nie istnieje', konto_docelowe;
    END IF;
    
    -- Wykonaj transfer
    UPDATE konta SET saldo = saldo - kwota WHERE id_konta = konto_zrodlowe;
    UPDATE konta SET saldo = saldo + kwota WHERE id_konta = konto_docelowe;
    
    -- Zapisz historię transakcji
    INSERT INTO historia_transakcji (konto_zrodlowe, konto_docelowe, kwota, data_transakcji)
    VALUES (konto_zrodlowe, konto_docelowe, kwota, CURRENT_TIMESTAMP);
    
    RETURN TRUE;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Błąd transferu: %', SQLERRM;
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Wywołanie w transakcji
BEGIN;
    SELECT transfer_pieniedzy(101, 102, 500.00);
COMMIT;
```

### Przykład 2: Zarządzanie stanami magazynowymi
```sql
CREATE OR REPLACE FUNCTION aktualizuj_stan_magazynowy(
    produkt_id INT,
    zmiana_ilosci INT,
    operacja VARCHAR(10)  -- 'DODAJ', 'ODEJMIJ'
)
RETURNS TABLE(nowy_stan INT, status VARCHAR(50)) AS $$
DECLARE
    aktualny_stan INT;
    minimalny_stan INT;
BEGIN
    -- Pobierz aktualny stan i minimum
    SELECT stan_magazynowy, stan_minimalny 
    INTO aktualny_stan, minimalny_stan
    FROM produkty
    WHERE id_produktu = produkt_id
    FOR UPDATE;
    
    IF NOT FOUND THEN
        RETURN QUERY SELECT 0, 'BŁĄD: Produkt nie istnieje'::VARCHAR(50);
        RETURN;
    END IF;
    
    -- Oblicz nowy stan
    IF operacja = 'DODAJ' THEN
        aktualny_stan := aktualny_stan + zmiana_ilosci;
    ELSIF operacja = 'ODEJMIJ' THEN
        IF aktualny_stan < zmiana_ilosci THEN
            RETURN QUERY SELECT aktualny_stan, 'BŁĄD: Niewystarczający stan'::VARCHAR(50);
            RETURN;
        END IF;
        aktualny_stan := aktualny_stan - zmiana_ilosci;
    ELSE
        RETURN QUERY SELECT aktualny_stan, 'BŁĄD: Nieprawidłowa operacja'::VARCHAR(50);
        RETURN;
    END IF;
    
    -- Aktualizuj stan
    UPDATE produkty 
    SET stan_magazynowy = aktualny_stan,
        data_ostatniej_zmiany = CURRENT_TIMESTAMP
    WHERE id_produktu = produkt_id;
    
    -- Sprawdź czy stan nie spadł poniżej minimum
    IF aktualny_stan <= minimalny_stan THEN
        -- Dodaj do listy do zamówienia
        INSERT INTO produkty_do_zamowienia (id_produktu, data_dodania)
        VALUES (produkt_id, CURRENT_TIMESTAMP)
        ON CONFLICT (id_produktu) DO NOTHING;
        
        RETURN QUERY SELECT aktualny_stan, 'OSTRZEŻENIE: Niski stan'::VARCHAR(50);
    ELSE
        RETURN QUERY SELECT aktualny_stan, 'OK'::VARCHAR(50);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Wywołanie
SELECT * FROM aktualizuj_stan_magazynowy(15, 10, 'ODEJMIJ');
```

### Przykład 3: Raportowanie sprzedaży
```sql
CREATE OR REPLACE FUNCTION raport_sprzedazy_miesiecy(
    rok INT,
    miesiac INT DEFAULT NULL
)
RETURNS TABLE(
    miesiac_roku INT,
    liczba_zamowien BIGINT,
    suma_sprzedazy DECIMAL(15,2),
    srednia_wartosc_zamowienia DECIMAL(15,2),
    najpopularniejszy_produkt TEXT
) AS $$
DECLARE
    data_od DATE;
    data_do DATE;
BEGIN
    -- Określ zakres dat
    IF miesiac IS NULL THEN
        -- Cały rok
        data_od := DATE(rok || '-01-01');
        data_do := DATE(rok || '-12-31');
    ELSE
        -- Konkretny miesiąc
        data_od := DATE(rok || '-' || LPAD(miesiac::TEXT, 2, '0') || '-01');
        data_do := DATE(data_od + INTERVAL '1 month - 1 day');
    END IF;
    
    RETURN QUERY
    WITH sprzedaz_szczegoly AS (
        SELECT 
            EXTRACT(MONTH FROM z.data_zamowienia) as m,
            z.id_zamowienia,
            z.wartosc_zamowienia,
            pz.id_produktu,
            pz.ilosc,
            p.nazwa as nazwa_produktu
        FROM zamowienia z
        JOIN pozycje_zamowien pz ON z.id_zamowienia = pz.id_zamowienia
        JOIN produkty p ON pz.id_produktu = p.id_produktu
        WHERE z.data_zamowienia BETWEEN data_od AND data_do
    ),
    produkty_popularnosc AS (
        SELECT 
            m,
            nazwa_produktu,
            SUM(ilosc) as total_sprzedane,
            ROW_NUMBER() OVER (PARTITION BY m ORDER BY SUM(ilosc) DESC) as rn
        FROM sprzedaz_szczegoly
        GROUP BY m, nazwa_produktu
    )
    SELECT 
        ss.m::INT,
        COUNT(DISTINCT ss.id_zamowienia),
        SUM(ss.wartosc_zamowienia),
        AVG(ss.wartosc_zamowienia),
        pp.nazwa_produktu
    FROM sprzedaz_szczegoly ss
    LEFT JOIN produkty_popularnosc pp ON ss.m = pp.m AND pp.rn = 1
    GROUP BY ss.m, pp.nazwa_produktu
    ORDER BY ss.m;
END;
$$ LANGUAGE plpgsql;

-- Wywołanie
SELECT * FROM raport_sprzedazy_miesiecy(2024);      -- Cały rok
SELECT * FROM raport_sprzedazy_miesiecy(2024, 3);   -- Marzec 2024
```

## Struktury kontrolne

### 1. **Warunki IF-THEN-ELSE**
```sql
CREATE OR REPLACE FUNCTION oceń_wyniki(punkty INT)
RETURNS VARCHAR(20) AS $$
BEGIN
    IF punkty >= 90 THEN
        RETURN 'Celujący';
    ELSIF punkty >= 80 THEN
        RETURN 'Bardzo dobry';
    ELSIF punkty >= 70 THEN
        RETURN 'Dobry';
    ELSIF punkty >= 60 THEN
        RETURN 'Dostateczny';
    ELSIF punkty >= 50 THEN
        RETURN 'Dopuszczający';
    ELSE
        RETURN 'Niedostateczny';
    END IF;
END;
$$ LANGUAGE plpgsql;
```

### 2. **Pętle LOOP**
```sql
CREATE OR REPLACE FUNCTION oblicz_silnie(n INT)
RETURNS BIGINT AS $$
DECLARE
    wynik BIGINT := 1;
    i INT := 1;
BEGIN
    IF n < 0 THEN
        RETURN NULL;
    END IF;
    
    LOOP
        EXIT WHEN i > n;
        wynik := wynik * i;
        i := i + 1;
    END LOOP;
    
    RETURN wynik;
END;
$$ LANGUAGE plpgsql;
```

### 3. **Pętle FOR**
```sql
CREATE OR REPLACE FUNCTION generuj_fibonacci(limit_val INT)
RETURNS TABLE(pozycja INT, wartosc BIGINT) AS $$
DECLARE
    a BIGINT := 0;
    b BIGINT := 1;
    temp BIGINT;
BEGIN
    FOR i IN 1..limit_val LOOP
        pozycja := i;
        wartosc := a;
        RETURN NEXT;
        
        temp := a + b;
        a := b;
        b := temp;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Wywołanie
SELECT * FROM generuj_fibonacci(10);
```

### 4. **Pętle WHILE**
```sql
CREATE OR REPLACE FUNCTION potega_przez_petla(podstawa INT, wykladnik INT)
RETURNS BIGINT AS $$
DECLARE
    wynik BIGINT := 1;
    licznik INT := 0;
BEGIN
    WHILE licznik < wykladnik LOOP
        wynik := wynik * podstawa;
        licznik := licznik + 1;
    END LOOP;
    
    RETURN wynik;
END;
$$ LANGUAGE plpgsql;
```

## Kursory

### Definicja i użycie:
```sql
CREATE OR REPLACE FUNCTION przetworz_duze_dane()
RETURNS VOID AS $$
DECLARE
    kursor_pracownik CURSOR FOR 
        SELECT id_pracownika, pensja FROM pracownicy 
        WHERE aktywny = true
        ORDER BY id_pracownika;
    
    rekord_pracownik RECORD;
    nowa_pensja DECIMAL(10,2);
BEGIN
    -- Otwórz kursor
    OPEN kursor_pracownik;
    
    LOOP
        -- Pobierz następny rekord
        FETCH kursor_pracownik INTO rekord_pracownik;
        
        -- Sprawdź czy są jeszcze rekordy
        EXIT WHEN NOT FOUND;
        
        -- Przetwórz rekord
        IF rekord_pracownik.pensja < 3000 THEN
            nowa_pensja := rekord_pracownik.pensja * 1.10;  -- 10% podwyżki
        ELSIF rekord_pracownik.pensja < 5000 THEN
            nowa_pensja := rekord_pracownik.pensja * 1.05;  -- 5% podwyżki
        ELSE
            nowa_pensja := rekord_pracownik.pensja * 1.02;  -- 2% podwyżki
        END IF;
        
        -- Aktualizuj dane
        UPDATE pracownicy 
        SET pensja = nowa_pensja,
            data_ostatniej_podwyzki = CURRENT_DATE
        WHERE id_pracownika = rekord_pracownik.id_pracownika;
        
        -- Loguj operację
        INSERT INTO log_podwyzek (id_pracownika, stara_pensja, nowa_pensja, data_zmiany)
        VALUES (rekord_pracownik.id_pracownika, rekord_pracownik.pensja, nowa_pensja, CURRENT_TIMESTAMP);
    END LOOP;
    
    -- Zamknij kursor
    CLOSE kursor_pracownik;
    
    RAISE NOTICE 'Zakończono przetwarzanie podwyżek';
END;
$$ LANGUAGE plpgsql;
```

## Obsługa błędów

### Exception handling:
```sql
CREATE OR REPLACE FUNCTION bezpieczny_transfer(
    konto_z INT,
    konto_do INT,
    kwota DECIMAL(15,2)
)
RETURNS TEXT AS $$
DECLARE
    error_message TEXT;
BEGIN
    -- Sprawdzenia wstępne
    IF kwota <= 0 THEN
        RAISE EXCEPTION 'Kwota musi być większa od zera';
    END IF;
    
    -- Rozpocznij transakcję
    BEGIN
        -- Transfer logic here
        UPDATE konta SET saldo = saldo - kwota WHERE id = konto_z;
        UPDATE konta SET saldo = saldo + kwota WHERE id = konto_do;
        
        RETURN 'Transfer zakończony pomyślnie';
        
    EXCEPTION
        WHEN check_violation THEN
            error_message := 'Naruszenie ograniczenia: ' || SQLERRM;
            RAISE NOTICE '%', error_message;
            RETURN error_message;
            
        WHEN foreign_key_violation THEN
            error_message := 'Nieprawidłowy numer konta: ' || SQLERRM;
            RAISE NOTICE '%', error_message;
            RETURN error_message;
            
        WHEN numeric_value_out_of_range THEN
            error_message := 'Wartość poza zakresem: ' || SQLERRM;
            RAISE NOTICE '%', error_message;
            RETURN error_message;
            
        WHEN OTHERS THEN
            error_message := 'Nieoczekiwany błąd: ' || SQLERRM;
            RAISE NOTICE '%', error_message;
            RETURN error_message;
    END;
END;
$$ LANGUAGE plpgsql;
```

## Zalety i wady procedur składowanych

### ✅ **Zalety:**
1. **Wydajność** - precompiled, szybsze wykonanie
2. **Bezpieczeństwo** - kontrolowany dostęp do danych  
3. **Centralizacja logiki** - business rules w jednym miejscu
4. **Redukcja ruchu sieciowego** - mniej SQL przesyłanego
5. **Atomowość** - operacje w transakcjach
6. **Reużywalność** - można wywoływać z różnych aplikacji

### ❌ **Wady:**
1. **Vendor lock-in** - różne składnie w różnych SZBD
2. **Trudność debugowania** - ograniczone narzędzia
3. **Kontrola wersji** - trudne w systemach VCS
4. **Skalowanie** - obciążenie serwera bazy danych
5. **Testowanie** - trudniejsze unit testing
6. **Deployment** - skomplikowany proces wdrażania

## Najlepsze praktyki

### ✅ **Dobre praktyki:**
1. **Nazewnictwo** - opisowe nazwy funkcji/procedur
2. **Parametry** - używaj znaczących nazw parametrów
3. **Dokumentacja** - komentarze opisujące cel i parametry
4. **Obsługa błędów** - zawsze obsługuj wyjątki
5. **Transakcje** - właściwe zarządzanie transakcjami
6. **Logowanie** - rejestruj ważne operacje

### ❌ **Złe praktyki:**
1. **Zbyt duże procedury** - trudne w utrzymaniu
2. **Brak obsługi błędów** - procedury mogą się crashować
3. **Hardkodowane wartości** - brak parametryzacji
4. **Brak dokumentacji** - nikt nie wie jak używać
5. **SQL injection** - brak walidacji parametrów
6. **Brak testów** - niesprawdzone procedury

## Wywołanie procedur z aplikacji

### PHP:
```php
$pdo = new PDO($dsn, $username, $password);

// Wywołanie funkcji
$stmt = $pdo->prepare("SELECT transfer_pieniedzy(?, ?, ?)");
$stmt->execute([101, 102, 500.00]);
$result = $stmt->fetch();

// Wywołanie procedury z OUT parametrami (MySQL)
$stmt = $pdo->prepare("CALL pobierz_statystyki_klienta(?, @liczba, @suma)");
$stmt->execute([123]);

$stmt = $pdo->query("SELECT @liczba, @suma");
$result = $stmt->fetch();
```

### Java:
```java
CallableStatement stmt = connection.prepareCall("{call pobierz_statystyki_klienta(?, ?, ?)}");
stmt.setInt(1, 123);
stmt.registerOutParameter(2, Types.INTEGER);
stmt.registerOutParameter(3, Types.DECIMAL);
stmt.execute();

int liczbaZamowien = stmt.getInt(2);
BigDecimal sumaWydatkow = stmt.getBigDecimal(3);
```

## Pułapki egzaminacyjne

### 1. **Różnice między SZBD**
- PostgreSQL: functions z RETURNS
- MySQL: procedures z IN/OUT/INOUT
- SQL Server: procedures z OUTPUT parameters

### 2. **Parametry**
- IN: tylko wejście
- OUT: tylko wyjście  
- INOUT: wejście i wyjście

### 3. **Obsługa błędów**
- Zawsze używaj EXCEPTION blocks
- Różne typy wyjątków w różnych SZBD

### 4. **Transakcje**
- Procedury mogą kontrolować transakcje
- Rollback w przypadku błędów