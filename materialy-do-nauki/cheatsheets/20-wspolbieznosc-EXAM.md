# 🔄 WSPÓŁBIEŻNOŚĆ - PROBLEMY I ROZWIĄZANIA - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Współbieżność w bazach danych to równoczesne wykonywanie wielu transakcji. Główne problemy to:

1. **Dirty Read** - czytanie niezcommitted danych
2. **Non-repeatable Read** - różne wyniki tego samego SELECT w transakcji
3. **Phantom Read** - pojawienie się nowych wierszy między odczytami
4. **Lost Update** - utrata aktualizacji przy równoczesnych zapisach

Rozwiązania: poziomy izolacji (READ COMMITTED, REPEATABLE READ, SERIALIZABLE), blokady, MVCC (Multi-Version Concurrency Control), timestamp ordering."

## ✍️ CO NAPISAĆ NA KARTCE

```
PROBLEMY WSPÓŁBIEŻNOŚCI:

1. DIRTY READ (brudny odczyt):
T1: W(X)=100 .... .... abort
T2: .... R(X)=100 .... commit  ← przeczytał wartość która zostanie cofnięta!

2. NON-REPEATABLE READ (niepowtarzalny odczyt):  
T1: R(X)=50 .... .... R(X)=150  ← różne wartości!
T2: .... .... W(X)=150 commit

3. PHANTOM READ (fantomowy odczyt):
T1: SELECT COUNT(*) FROM accounts WHERE balance > 1000; -- wynik: 5
    ... inne operacje ...
    SELECT COUNT(*) FROM accounts WHERE balance > 1000; -- wynik: 6!
T2: .... INSERT INTO accounts VALUES(999, 1500); commit

4. LOST UPDATE (utracona aktualizacja):
T1: R(X)=100, X=X+50, W(X)=150, commit
T2: R(X)=100, X=X+25, W(X)=125, commit  ← utracone +50 z T1!

ROZWIĄZANIA:

POZIOMY IZOLACJI:
• READ UNCOMMITTED - pozwala na dirty reads
• READ COMMITTED - zapobiega dirty reads  
• REPEATABLE READ - zapobiega dirty + non-repeatable reads
• SERIALIZABLE - zapobiega wszystkim problemom

MECHANIZMY KONTROLI:
• Two-Phase Locking (2PL) - blokady dwufazowe
• MVCC - wersjonowanie danych
• Timestamp Ordering - uporządkowanie czasowe
• Optimistic Concurrency Control - optymistyczna kontrola

BLOKADY:
• Shared Lock (S) - blokada odczytu
• Exclusive Lock (X) - blokada zapisu  
• Intent Locks (IS, IX) - blokady intencji
• Poziomy: row, page, table, database

MVCC (PostgreSQL):
• Każda transakcja widzi spójny snapshot
• Nie blokuje readers vs writers
• Używa xmin/xmax do wersjonowania
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- DEMONSTRACJA PROBLEMÓW WSPÓŁBIEŻNOŚCI

-- Przygotowanie danych testowych
CREATE TABLE konta_test (
    id_konta INT PRIMARY KEY,
    saldo DECIMAL(10,2),
    wlasciciel VARCHAR(100),
    ostatnia_operacja TIMESTAMP
);

INSERT INTO konta_test VALUES 
(1, 1000.00, 'Jan Kowalski', NOW()),
(2, 500.00, 'Anna Nowak', NOW()),
(3, 1500.00, 'Piotr Wiśniewski', NOW());

-- 1. DIRTY READ - demonstracja problemu

-- SESSION 1 (Terminal 1):
BEGIN ISOLATION LEVEL READ UNCOMMITTED;
UPDATE konta_test SET saldo = 2000 WHERE id_konta = 1;
-- NIE COMMIT jeszcze!
SELECT pg_sleep(10); -- czeka 10 sekund
ROLLBACK; -- cofnie zmiany!

-- SESSION 2 (Terminal 2, wykonaj w trakcie czekania Session 1):
BEGIN ISOLATION LEVEL READ UNCOMMITTED;
SELECT saldo FROM konta_test WHERE id_konta = 1; -- zobaczy 2000 (dirty!)
COMMIT;
-- Session 2 przeczytał wartość która zostanie cofnięta przez Session 1

-- ROZWIĄZANIE: READ COMMITTED lub wyższy
-- SESSION 2 z READ COMMITTED:
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT saldo FROM konta_test WHERE id_konta = 1; -- poczeka na Session 1 lub zobaczy stare dane
COMMIT;

-- 2. NON-REPEATABLE READ - demonstracja

-- SESSION 1:
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT saldo FROM konta_test WHERE id_konta = 1; -- pierwszy read
-- ... pauza na wykonanie Session 2 ...
SELECT saldo FROM konta_test WHERE id_konta = 1; -- drugi read - może być inna wartość!
COMMIT;

-- SESSION 2 (wykonaj między read'ami Session 1):
BEGIN;
UPDATE konta_test SET saldo = saldo + 100 WHERE id_konta = 1;
COMMIT;

-- ROZWIĄZANIE: REPEATABLE READ
-- SESSION 1 z REPEATABLE READ:
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT saldo FROM konta_test WHERE id_konta = 1; -- pierwszy read
-- ... Session 2 może zmienić dane ...
SELECT saldo FROM konta_test WHERE id_konta = 1; -- drugi read - ta sama wartość!
COMMIT;

-- 3. PHANTOM READ - demonstracja

-- SESSION 1:
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT COUNT(*) FROM konta_test WHERE saldo > 1000; -- pierwszy count
-- ... pauza ...
SELECT COUNT(*) FROM konta_test WHERE saldo > 1000; -- drugi count - może być więcej wierszy!
COMMIT;

-- SESSION 2 (wykonaj między count'ami):
BEGIN;
INSERT INTO konta_test VALUES (4, 1200.00, 'Nowy Klient', NOW());
COMMIT;

-- ROZWIĄZANIE: SERIALIZABLE
-- SESSION 1 z SERIALIZABLE:
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT COUNT(*) FROM konta_test WHERE saldo > 1000;
-- Session 2 nie może dodać nowego wiersza lub dostanie serialization error
SELECT COUNT(*) FROM konta_test WHERE saldo > 1000; -- taki sam wynik
COMMIT;

-- 4. LOST UPDATE - demonstracja i rozwiązanie

-- PROBLEM: Lost Update (bez blokad)
-- SESSION 1:
BEGIN;
SELECT saldo FROM konta_test WHERE id_konta = 1; -- odczytaj: 1000
-- oblicz nowe saldo: 1000 + 100 = 1100
-- ... pauza ...
UPDATE konta_test SET saldo = 1100 WHERE id_konta = 1; -- ustaw na 1100
COMMIT;

-- SESSION 2 (równolegle):
BEGIN;
SELECT saldo FROM konta_test WHERE id_konta = 1; -- też odczytaj: 1000
-- oblicz nowe saldo: 1000 + 50 = 1050  
UPDATE konta_test SET saldo = 1050 WHERE id_konta = 1; -- ustaw na 1050
COMMIT; -- UTRACONE +100 z Session 1!

-- ROZWIĄZANIE 1: SELECT FOR UPDATE (pesymistyczne blokowanie)
-- SESSION 1:
BEGIN;
SELECT saldo FROM konta_test WHERE id_konta = 1 FOR UPDATE; -- blokada exclusive
UPDATE konta_test SET saldo = saldo + 100 WHERE id_konta = 1;
COMMIT;

-- SESSION 2:
BEGIN;
SELECT saldo FROM konta_test WHERE id_konta = 1 FOR UPDATE; -- CZEKA na Session 1
UPDATE konta_test SET saldo = saldo + 50 WHERE id_konta = 1;
COMMIT; -- Wykona się po Session 1, zachowując obie zmiany

-- ROZWIĄZANIE 2: Optimistic Concurrency Control
CREATE TABLE konta_wersjonowane (
    id_konta INT PRIMARY KEY,
    saldo DECIMAL(10,2),
    wlasciciel VARCHAR(100),
    wersja INT DEFAULT 1
);

-- Funkcja bezpiecznej aktualizacji
CREATE OR REPLACE FUNCTION bezpieczna_aktualizacja_saldo(
    p_id_konta INT,
    p_stara_wersja INT,
    p_zmiana DECIMAL
) RETURNS BOOLEAN AS $$
DECLARE
    aktualna_wersja INT;
    wynik INT;
BEGIN
    -- Sprawdź aktualną wersję
    SELECT wersja INTO aktualna_wersja 
    FROM konta_wersjonowane 
    WHERE id_konta = p_id_konta;
    
    IF aktualna_wersja != p_stara_wersja THEN
        RAISE NOTICE 'Konflikt wersji: oczekiwana %, aktualna %', p_stara_wersja, aktualna_wersja;
        RETURN FALSE;
    END IF;
    
    -- Aktualizuj z zwiększeniem wersji
    UPDATE konta_wersjonowane 
    SET saldo = saldo + p_zmiana,
        wersja = wersja + 1
    WHERE id_konta = p_id_konta AND wersja = p_stara_wersja;
    
    GET DIAGNOSTICS wynik = ROW_COUNT;
    
    IF wynik = 1 THEN
        RAISE NOTICE 'Aktualizacja udana, nowa wersja: %', p_stara_wersja + 1;
        RETURN TRUE;
    ELSE
        RAISE NOTICE 'Aktualizacja nieudana - konflikt współbieżności';
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Test optimistic concurrency
INSERT INTO konta_wersjonowane VALUES (1, 1000.00, 'Test User', 1);

-- Session 1 i 2 odczytują wersję 1, ale tylko jedna aktualizacja się uda
SELECT bezpieczna_aktualizacja_saldo(1, 1, 100); -- sukces, wersja → 2
SELECT bezpieczna_aktualizacja_saldo(1, 1, 50);  -- błąd - wersja już 2!

-- 5. DEADLOCK - wykrywanie i rozwiązywanie

-- TWORZENIE DEADLOCK:
-- SESSION 1:
BEGIN;
UPDATE konta_test SET saldo = saldo + 10 WHERE id_konta = 1; -- blokuje konto 1
-- ... pauza ...
UPDATE konta_test SET saldo = saldo + 10 WHERE id_konta = 2; -- czeka na konto 2

-- SESSION 2:
BEGIN;
UPDATE konta_test SET saldo = saldo + 20 WHERE id_konta = 2; -- blokuje konto 2
UPDATE konta_test SET saldo = saldo + 20 WHERE id_konta = 1; -- DEADLOCK!

-- PostgreSQL automatycznie wykryje deadlock i przerwnie jedną transakcję

-- ZAPOBIEGANIE DEADLOCK - uporządkowane blokowanie:
CREATE OR REPLACE FUNCTION transfer_ordered(
    from_account INT,
    to_account INT,
    amount DECIMAL
) RETURNS VOID AS $$
DECLARE
    first_account INT;
    second_account INT;
BEGIN
    -- Zawsze blokuj konta w kolejności rosnącej ID
    IF from_account < to_account THEN
        first_account := from_account;
        second_account := to_account;
    ELSE
        first_account := to_account;
        second_account := from_account;
    END IF;
    
    -- Blokuj w uporządkowanej kolejności
    PERFORM saldo FROM konta_test WHERE id_konta = first_account FOR UPDATE;
    PERFORM saldo FROM konta_test WHERE id_konta = second_account FOR UPDATE;
    
    -- Teraz bezpieczne operacje
    UPDATE konta_test SET saldo = saldo - amount WHERE id_konta = from_account;
    UPDATE konta_test SET saldo = saldo + amount WHERE id_konta = to_account;
END;
$$ LANGUAGE plpgsql;

-- 6. MONITORING WSPÓŁBIEŻNOŚCI

-- Sprawdzenie aktualnych blokad
SELECT 
    l.locktype,
    l.database,
    l.relation::regclass as table_name,
    l.mode,
    l.granted,
    a.query,
    a.pid,
    a.state
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.database = (SELECT oid FROM pg_database WHERE datname = current_database())
ORDER BY l.granted DESC, l.pid;

-- Sprawdzenie długotrwałych transakcji
SELECT 
    pid,
    usename,
    state,
    now() - xact_start as transaction_age,
    now() - query_start as query_age,
    query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
AND state != 'idle'
ORDER BY xact_start;

-- Sprawdzenie blokujących się transakcji
WITH blocking_locks AS (
    SELECT 
        blocked_locks.pid AS blocked_pid,
        blocked_activity.usename AS blocked_user,
        blocking_locks.pid AS blocking_pid,
        blocking_activity.usename AS blocking_user,
        blocked_activity.query AS blocked_statement,
        blocking_activity.query AS blocking_statement
    FROM pg_catalog.pg_locks blocked_locks
    JOIN pg_catalog.pg_stat_activity blocked_activity 
        ON blocked_activity.pid = blocked_locks.pid
    JOIN pg_catalog.pg_locks blocking_locks 
        ON blocking_locks.locktype = blocked_locks.locktype
        AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
        AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
        AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
        AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
        AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
        AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
        AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
        AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
        AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
        AND blocking_locks.pid != blocked_locks.pid
    JOIN pg_catalog.pg_stat_activity blocking_activity 
        ON blocking_activity.pid = blocking_locks.pid
    WHERE NOT blocked_locks.granted
)
SELECT * FROM blocking_locks;

-- Statystyki deadlocków
SELECT 
    datname,
    deadlocks,
    temp_files,
    temp_bytes
FROM pg_stat_database 
WHERE datname = current_database();
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Dirty read = najgorszy problem, phantom read = najmniej krytyczny
2. **UWAGA**: REPEATABLE READ nie eliminuje phantom reads w niektórych DBMS
3. **BŁĄD**: Mylenie non-repeatable read z phantom read
4. **WAŻNE**: Lost update może wystąpić nawet na SERIALIZABLE bez blokad
5. **PUŁAPKA**: Wyższe poziomy izolacji = mniej współbieżności = więcej deadlocków

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Concurrency problems** - problemy współbieżności
- **Dirty/Non-repeatable/Phantom reads** - typy problemów odczytu
- **Lost update** - utracona aktualizacja
- **Isolation levels** - poziomy izolacji
- **MVCC** - Multi-Version Concurrency Control
- **Optimistic/Pessimistic locking** - optymistyczne/pesymistyczne blokowanie
- **Deadlock detection** - wykrywanie zakleszczenia
- **Lock escalation** - eskalacja blokad

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **07-poziomy-izolacji** - rozwiązania problemów współbieżności
- **18-transakcje-acid** - izolacja w ACID
- **10-blokady** - mechanizmy blokowania
- **09-zakleszczenia** - deadlock w współbieżności
- **03-protokol-dwufazowy** - kontrola współbieżności