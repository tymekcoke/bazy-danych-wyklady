# 🔐 POZIOMY IZOLACJI TRANSAKCJI - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Poziomy izolacji transakcji określają stopień izolacji między współbieżnymi transakcjami. Standard SQL definiuje 4 poziomy:

1. **READ UNCOMMITTED** - najniższy, pozwala na dirty reads
2. **READ COMMITTED** - zapobiega dirty reads, domyślny w PostgreSQL  
3. **REPEATABLE READ** - dodatkowo zapobiega non-repeatable reads
4. **SERIALIZABLE** - najwyższy, pełna izolacja, jakby transakcje były sekwencyjne

Wyższy poziom = więcej izolacji = mniej współbieżności = więcej blokad."

## ✍️ CO NAPISAĆ NA KARTCE

```
POZIOMY IZOLACJI - TABELA PROBLEMÓW

Poziom             | Dirty | Non-rep | Phantom | Wspólb | Wydajn
                   | Read  | Read    | Read    | ież-   | ość   
                   |       |         |         | ność   |       
-------------------|-------|---------|---------|--------|-------
READ UNCOMMITTED   |   ✗   |    ✗    |    ✗    |  MAX   |  MAX  
READ COMMITTED     |   ✓   |    ✗    |    ✗    | Wysoka | Wysoka
REPEATABLE READ    |   ✓   |    ✓    |    ✗    | Średnia| Średnia
SERIALIZABLE       |   ✓   |    ✓    |    ✓    |  MIN   |  MIN  

✓ = problem rozwiązany
✗ = problem może wystąpić

PROBLEMY:
• Dirty Read - czytanie niezcommitted danych
• Non-repeatable Read - różne wyniki tego samego SELECT  
• Phantom Read - pojawienie się nowych wierszy

IMPLEMENTACJA W PostgreSQL:
READ UNCOMMITTED = READ COMMITTED (PostgreSQL nie ma true dirty reads)
READ COMMITTED   = domyślny poziom
REPEATABLE READ  = snapshot isolation  
SERIALIZABLE     = serializable snapshot isolation (SSI)
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- USTAWIANIE POZIOMU IZOLACJI
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- operacje...
COMMIT;

-- lub w BEGIN
BEGIN ISOLATION LEVEL REPEATABLE READ;
-- operacje...
COMMIT;

-- PRZYKŁAD 1: DIRTY READ (tylko READ uncommitted)
-- Transakcja T1:
BEGIN ISOLATION LEVEL READ UNCOMMITTED;
SELECT saldo FROM konta WHERE id = 1;  -- może zobaczyć 150 (dirty)

-- Transakcja T2 (równolegle):
BEGIN;
UPDATE konta SET saldo = 150 WHERE id = 1;  -- jeszcze nie commit
-- T1 może przeczytać 150, ale T2 może zrobić ROLLBACK!
ROLLBACK;  -- dirty read w T1!

-- PRZYKŁAD 2: NON-REPEATABLE READ  
-- Transakcja T1:
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT saldo FROM konta WHERE id = 1;  -- pierwszy read: 100
-- ... inne operacje ...
SELECT saldo FROM konta WHERE id = 1;  -- drugi read: może być 200!
COMMIT;

-- Transakcja T2 (między read'ami T1):
BEGIN;
UPDATE konta SET saldo = 200 WHERE id = 1;
COMMIT;  -- zmieniło wartość między read'ami T1

-- PRZYKŁAD 3: PHANTOM READ
-- Transakcja T1:
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT COUNT(*) FROM konta WHERE saldo > 1000;  -- np. 5 wierszy
-- ... inne operacje ...  
SELECT COUNT(*) FROM konta WHERE saldo > 1000;  -- może być 6! (phantom)
COMMIT;

-- Transakcja T2 (między SELECT'ami T1):
BEGIN;  
INSERT INTO konta (id, saldo) VALUES (999, 1500);  -- nowy wiersz!
COMMIT;

-- PRZYKŁAD 4: SERIALIZABLE - pełna izolacja
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- PostgreSQL używa Serializable Snapshot Isolation (SSI)
-- Może rzucić serialization_failure error zamiast blokować
SELECT SUM(saldo) FROM konta;
UPDATE konta SET saldo = saldo * 1.05 WHERE typ = 'oszczednosciowe';
COMMIT;  -- może się nie udać z serialization error

-- PRAKTYCZNY PRZYKŁAD: Przelew międzykontowy
BEGIN ISOLATION LEVEL REPEATABLE READ;
-- Sprawdź saldo źródłowe
SELECT saldo FROM konta WHERE id = 1 FOR UPDATE;  -- blokada

-- Sprawdź czy wystarczy środków
IF (SELECT saldo FROM konta WHERE id = 1) >= 100 THEN
    -- Wykonaj przelew
    UPDATE konta SET saldo = saldo - 100 WHERE id = 1;
    UPDATE konta SET saldo = saldo + 100 WHERE id = 2;
    COMMIT;
ELSE
    ROLLBACK;
END IF;

-- MONITORING POZIOMÓW IZOLACJI
SHOW default_transaction_isolation;  -- poziom domyślny
SELECT current_setting('transaction_isolation');  -- aktualny poziom

-- DEADLOCK NA SERIALIZABLE
-- PostgreSQL rzuci serialization_failure zamiast deadlock
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- operacje mogące konfliktować...
EXCEPTION
    WHEN serialization_failure THEN
        ROLLBACK;
        -- retry transakcji
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: PostgreSQL nie ma prawdziwego READ UNCOMMITTED
2. **UWAGA**: REPEATABLE READ w PostgreSQL = Snapshot Isolation
3. **BŁĄD**: Mylenie poziomów izolacji z poziomami blokad (to różne rzeczy!)
4. **WAŻNE**: Wyższy poziom = mniej współbieżności = więcej deadlocków
5. **PUŁAPKA**: SERIALIZABLE może rzucać serialization_failure errors

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Isolation levels** - poziomy izolacji
- **Dirty read** - czytanie brudnych danych
- **Non-repeatable read** - niepowtarzalny odczyt
- **Phantom read** - fantomowy odczyt  
- **Snapshot isolation** - izolacja migawkowa
- **Serializable Snapshot Isolation (SSI)** - PostgreSQL SERIALIZABLE
- **Concurrency vs Isolation** - kompromis współbieżność/izolacja
- **Serialization failure** - błąd serializacji

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **18-transakcje-acid** - izolacja w ACID
- **20-wspolbieznosc** - problemy współbieżności
- **10-blokady** - mechanizmy blokowania
- **04-przebiegi-transakcji** - ścisłe przebiegi = READ COMMITTED+
- **03-protokol-dwufazowy** - implementacja izolacji