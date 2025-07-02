# ⚙️ PROCEDURY SKŁADOWANE - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekunds)

"Procedury składowane to precompilowane bloki kodu SQL przechowywane w bazie danych, które można wywoływać z aplikacji. Zalety:

1. **Wydajność** - prekompilacja, cache planów wykonania
2. **Bezpieczeństwo** - enkapsulacja logiki, ochrona przed SQL injection
3. **Centralizacja** - logika biznesowa w jednym miejscu
4. **Kontrola dostępu** - uprawnienia na poziomie procedur

Wady: trudność debugowania, vendor lock-in, ograniczona przenośność. W PostgreSQL używa się funkcji zamiast procedur (do wersji 11)."

## ✍️ CO NAPISAĆ NA KARTCE

```sql
-- SKŁADNIA PROCEDURY/FUNKCJI W PostgreSQL

-- FUNKCJA (przed PostgreSQL 11)
CREATE OR REPLACE FUNCTION nazwa_funkcji(parametry)
RETURNS typ_zwracany AS $$
DECLARE
    -- zmienne lokalne
BEGIN
    -- kod procedury
    RETURN wartość;
END;
$$ LANGUAGE plpgsql;

-- PROCEDURA (PostgreSQL 11+)
CREATE OR REPLACE PROCEDURE nazwa_procedury(parametry)
AS $$
DECLARE
    -- zmienne lokalne  
BEGIN
    -- kod procedury
    -- BRAK RETURN (procedury nic nie zwracają)
END;
$$ LANGUAGE plpgsql;

-- WYWOŁANIE
SELECT nazwa_funkcji(argumenty);  -- funkcja
CALL nazwa_procedury(argumenty);  -- procedura

-- PRZYKŁAD PROSTEJ FUNKCJI
CREATE OR REPLACE FUNCTION oblicz_podatek(kwota DECIMAL)
RETURNS DECIMAL AS $$
BEGIN
    RETURN kwota * 0.23;  -- VAT 23%
END;
$$ LANGUAGE plpgsql;

-- UŻYCIE
SELECT oblicz_podatek(1000);  -- zwraca 230

-- TYPY PARAMETRÓW:
IN     - parametr wejściowy (domyślny)
OUT    - parametr wyjściowy  
INOUT  - parametr wejściowo-wyjściowy

-- FUNKCJE TYPU:
- SCALAR functions (zwracają jedną wartość)
- TABLE functions (zwracają zestaw wierszy)
- AGGREGATE functions (własne funkcje agregujące)
- WINDOW functions (funkcje okna)

ZALETY PROCEDUR:
✓ Wydajność (prekompilacja, cache)
✓ Bezpieczeństwo (SQL injection protection)
✓ Centralizacja logiki biznesowej
✓ Kontrola dostępu
✓ Transakcje atomowe
✓ Mniej transferu danych

WADY PROCEDUR:
✗ Vendor lock-in
✗ Trudność debugowania
✗ Ograniczona przenośność
✗ Trudność wersjonowania
✗ Obciążenie serwera bazy
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- KOMPLEKSNE PRZYKŁADY PROCEDUR I FUNKCJI

-- 1. FUNKCJA SCALAR - zwraca jedną wartość
CREATE OR REPLACE FUNCTION sprawdz_dostepnosc_produktu(
    p_id_produktu INT
) RETURNS INTEGER AS $$
DECLARE
    dostepna_ilosc INTEGER;
BEGIN
    SELECT stan_magazynowy INTO dostepna_ilosc
    FROM produkty 
    WHERE id_produktu = p_id_produktu;
    
    IF dostepna_ilosc IS NULL THEN
        RAISE EXCEPTION 'Produkt o ID % nie istnieje', p_id_produktu;
    END IF;
    
    RETURN dostepna_ilosc;
END;
$$ LANGUAGE plpgsql;

-- Użycie funkcji scalar
SELECT 
    p.nazwa,
    sprawdz_dostepnosc_produktu(p.id_produktu) as dostepny_stan
FROM produkty p
WHERE p.aktywny = true;

-- 2. FUNKCJA TABLE - zwraca zestaw wierszy
CREATE OR REPLACE FUNCTION raport_sprzedazy_klienta(
    p_id_klienta INT,
    p_data_od DATE DEFAULT '2024-01-01',
    p_data_do DATE DEFAULT CURRENT_DATE
) RETURNS TABLE (
    numer_zamowienia VARCHAR,
    data_zamowienia DATE,
    nazwa_produktu VARCHAR,
    ilosc INTEGER,
    cena_jednostkowa DECIMAL,
    wartosc_pozycji DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        z.numer_zamowienia,
        z.data_zamowienia,
        p.nazwa,
        pz.ilosc,
        pz.cena_w_momencie_sprzedazy,
        (pz.ilosc * pz.cena_w_momencie_sprzedazy) as wartosc
    FROM zamowienia z
    JOIN pozycje_zamowienia pz ON z.id_zamowienia = pz.id_zamowienia
    JOIN produkty p ON pz.id_produktu = p.id_produktu
    WHERE z.id_klienta = p_id_klienta
    AND z.data_zamowienia BETWEEN p_data_od AND p_data_do
    ORDER BY z.data_zamowienia DESC, p.nazwa;
END;
$$ LANGUAGE plpgsql;

-- Użycie funkcji table
SELECT * FROM raport_sprzedazy_klienta(100, '2024-01-01', '2024-12-31');

-- 3. PROCEDURA Z TRANSAKCJĄ (PostgreSQL 11+)
CREATE OR REPLACE PROCEDURE wykonaj_przelew_miedzybankowy(
    p_id_konta_zrodlowego INT,
    p_id_konta_docelowego INT, 
    p_kwota DECIMAL,
    p_tytul VARCHAR DEFAULT 'Przelew'
)
AS $$
DECLARE
    saldo_zrodlowe DECIMAL;
    nazwa_konta_zrodlowego VARCHAR;
    nazwa_konta_docelowego VARCHAR;
BEGIN
    -- Sprawdź czy konta istnieją
    SELECT saldo, nazwa_wlasciciela INTO saldo_zrodlowe, nazwa_konta_zrodlowego
    FROM konta WHERE id_konta = p_id_konta_zrodlowego;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Konto źródłowe % nie istnieje', p_id_konta_zrodlowego;
    END IF;
    
    SELECT nazwa_wlasciciela INTO nazwa_konta_docelowego
    FROM konta WHERE id_konta = p_id_konta_docelowego;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Konto docelowe % nie istnieje', p_id_konta_docelowego;
    END IF;
    
    -- Sprawdź saldo
    IF saldo_zrodlowe < p_kwota THEN
        RAISE EXCEPTION 'Niewystarczające środki. Saldo: %, wymagane: %', 
                        saldo_zrodlowe, p_kwota;
    END IF;
    
    -- Wykonaj przelew (atomowo)
    UPDATE konta 
    SET saldo = saldo - p_kwota,
        data_ostatniej_operacji = CURRENT_TIMESTAMP
    WHERE id_konta = p_id_konta_zrodlowego;
    
    UPDATE konta
    SET saldo = saldo + p_kwota,
        data_ostatniej_operacji = CURRENT_TIMESTAMP  
    WHERE id_konta = p_id_konta_docelowego;
    
    -- Log operacji
    INSERT INTO historia_operacji (
        id_konta, typ_operacji, kwota, saldo_po_operacji, opis
    ) VALUES 
    (p_id_konta_zrodlowego, 'PRZELEW_WYCHODZACY', -p_kwota, 
     saldo_zrodlowe - p_kwota, p_tytul),
    (p_id_konta_docelowego, 'PRZELEW_PRZYCHODZACY', p_kwota,
     (SELECT saldo FROM konta WHERE id_konta = p_id_konta_docelowego), p_tytul);
    
    -- Sukces
    RAISE NOTICE 'Przelew wykonany: % PLN z konta % na konto %', 
                 p_kwota, nazwa_konta_zrodlowego, nazwa_konta_docelowego;
    
    COMMIT;  -- Potwierdź transakcję
    
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;  -- Cofnij w przypadku błędu
        RAISE;     -- Przekaż błąd wyżej
END;
$$ LANGUAGE plpgsql;

-- Wywołanie procedury
CALL wykonaj_przelew_miedzybankowy(1001, 1002, 500.00, 'Za faktury');

-- 4. FUNKCJA AGREGUJĄCA (custom aggregate)
CREATE OR REPLACE FUNCTION geometric_mean_state(state DECIMAL[], value DECIMAL)
RETURNS DECIMAL[] AS $$
BEGIN
    IF state IS NULL THEN
        RETURN ARRAY[value, 1];  -- [product, count]
    ELSE
        RETURN ARRAY[state[1] * value, state[2] + 1];
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION geometric_mean_final(state DECIMAL[])
RETURNS DECIMAL AS $$
BEGIN
    IF state IS NULL OR state[2] = 0 THEN
        RETURN NULL;
    ELSE
        RETURN power(state[1], 1.0 / state[2]);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Stworzenie aggregate function
CREATE AGGREGATE geometric_mean(DECIMAL) (
    SFUNC = geometric_mean_state,
    STYPE = DECIMAL[],
    FINALFUNC = geometric_mean_final
);

-- Użycie custom aggregate
SELECT 
    kategoria,
    AVG(cena) as srednia_arytmetyczna,
    geometric_mean(cena) as srednia_geometryczna
FROM produkty 
GROUP BY kategoria;

-- 5. FUNKCJA Z OBSŁUGĄ BŁĘDÓW I LOGOWANIEM
CREATE OR REPLACE FUNCTION bezpieczna_aktualizacja_ceny(
    p_id_produktu INT,
    p_nowa_cena DECIMAL,
    p_uzytkownik VARCHAR DEFAULT USER
) RETURNS BOOLEAN AS $$
DECLARE
    stara_cena DECIMAL;
    nazwa_produktu VARCHAR;
BEGIN
    -- Walidacja danych wejściowych
    IF p_nowa_cena <= 0 THEN
        RAISE EXCEPTION 'Cena musi być większa od 0, podano: %', p_nowa_cena;
    END IF;
    
    -- Pobranie aktualnych danych
    SELECT cena, nazwa INTO stara_cena, nazwa_produktu
    FROM produkty 
    WHERE id_produktu = p_id_produktu;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Produkt o ID % nie istnieje', p_id_produktu;
    END IF;
    
    -- Sprawdzenie czy zmiana nie jest za duża (business rule)
    IF ABS(p_nowa_cena - stara_cena) / stara_cena > 0.5 THEN
        RAISE EXCEPTION 'Zbyt duża zmiana ceny: % → %. Maksymalna zmiana: 50%%', 
                        stara_cena, p_nowa_cena;
    END IF;
    
    -- Aktualizacja
    UPDATE produkty 
    SET cena = p_nowa_cena,
        data_ostatniej_zmiany = CURRENT_TIMESTAMP,
        zmienione_przez = p_uzytkownik
    WHERE id_produktu = p_id_produktu;
    
    -- Audit log
    INSERT INTO audit_zmian_cen (
        id_produktu, nazwa_produktu, stara_cena, nowa_cena, 
        uzytkownik, timestamp
    ) VALUES (
        p_id_produktu, nazwa_produktu, stara_cena, p_nowa_cena,
        p_uzytkownik, CURRENT_TIMESTAMP
    );
    
    RAISE NOTICE 'Cena produktu "%" zmieniona z % na %', 
                 nazwa_produktu, stara_cena, p_nowa_cena;
    
    RETURN TRUE;
    
EXCEPTION
    WHEN OTHERS THEN
        -- Log błędu
        INSERT INTO error_log (error_message, function_name, parameters, timestamp)
        VALUES (SQLERRM, 'bezpieczna_aktualizacja_ceny', 
                format('id:%s, cena:%s, user:%s', p_id_produktu, p_nowa_cena, p_uzytkownik),
                CURRENT_TIMESTAMP);
        
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- 6. UPRAWNNIENIA DO PROCEDUR
-- Tworzenie roli dla aplikacji
CREATE ROLE app_user WITH LOGIN PASSWORD 'secure_password';

-- Nadanie uprawnień tylko do procedur (nie bezpośrednio do tabel)
GRANT EXECUTE ON FUNCTION sprawdz_dostepnosc_produktu(INT) TO app_user;
GRANT EXECUTE ON FUNCTION raport_sprzedazy_klienta(INT, DATE, DATE) TO app_user;
GRANT EXECUTE ON PROCEDURE wykonaj_przelew_miedzybankowy(INT, INT, DECIMAL, VARCHAR) TO app_user;

-- Odebranie bezpośredniego dostępu do tabel
REVOKE ALL ON TABLE konta FROM app_user;
REVOKE ALL ON TABLE produkty FROM app_user;

-- Teraz aplikacja może tylko wywoływać procedury, nie manipulować tabelami bezpośrednio
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: W PostgreSQL przed v11 były tylko funkcje, nie procedury
2. **UWAGA**: Funkcje muszą mieć RETURN, procedury nie
3. **BŁĄD**: Mylenie funkcji scalar z table (różne sposoby wywołania)
4. **WAŻNE**: Procedury mogą zarządzać transakcjami (COMMIT/ROLLBACK)
5. **PUŁAPKA**: Vendor lock-in - procedury nie są przenośne między DBMS

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Stored procedures/functions** - procedury/funkcje składowane
- **Precompiled code** - prekompilowany kod
- **PL/pgSQL** - język proceduralny PostgreSQL
- **Scalar/Table functions** - funkcje skalarne/tabelaryczne
- **Transaction management** - zarządzanie transakcjami
- **Exception handling** - obsługa wyjątków
- **Security encapsulation** - enkapsulacja bezpieczeństwa
- **Vendor lock-in** - uzależnienie od dostawcy

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **33-plpgsql-podstawy** - język procedur w PostgreSQL
- **34-funkcje-uzytkownika** - szczegóły funkcji użytkownika
- **06-triggery** - funkcje wywołane przez triggery
- **13-sql-injection** - ochrona przez procedury
- **18-transakcje-acid** - transakcje w procedurach