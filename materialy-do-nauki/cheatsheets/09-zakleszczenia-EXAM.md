# 🔄 ZAKLESZCZENIA (DEADLOCK) - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Zakleszczenie to sytuacja, gdy dwie lub więcej transakcji wzajemnie na siebie czekają i żadna nie może kontynuować wykonania. Powstaje gdy spełnione są cztery warunki Coffmana:

1. **Mutual exclusion** - zasoby są używane wyłącznie
2. **Hold and wait** - transakcja trzyma zasoby i czeka na inne  
3. **No preemption** - zasobów nie można przymusowo odebrać
4. **Circular wait** - cykliczne czekanie między transakcjami

Rozwiązania to: wykrywanie i przerywanie, zapobieganie przez uporządkowanie dostępu, lub timeout."

## ✍️ CO NAPISAĆ NA KARTCE

```
DEADLOCK - WARUNKI COFFMANA (wszystkie 4 muszą być spełnione):

1. MUTUAL EXCLUSION - zasoby używane wyłącznie
2. HOLD AND WAIT - trzymanie zasobów + czekanie na inne  
3. NO PREEMPTION - brak przymusowego odbierania zasobów
4. CIRCULAR WAIT - cykliczne czekanie T1→T2→T1

PRZYKŁAD DEADLOCK:
T1: lock(A) → czeka na lock(B)
T2: lock(B) → czeka na lock(A)
Graf czekania: T1 → T2 → T1 (cykl!)

ROZWIĄZANIA:

1. WYKRYWANIE I PRZERYWANIE:
   - Monitor śledzi graf czekania
   - Gdy wykryje cykl → przerywa jedną transakcję
   - PostgreSQL: automatyczne wykrywanie + deadlock_timeout

2. ZAPOBIEGANIE - uporządkowanie zasobów:
   - Zawsze blokować w tej samej kolejności (np. id_tabeli ASC)
   - Wait-Die: stara transakcja czeka, młoda umiera
   - Wound-Wait: stara rani młodą, młoda czeka na starą

3. TIMEOUT:
   - Przerwanie transakcji po określonym czasie
   - lock_timeout w PostgreSQL

PRZYKŁAD ZAPOBIEGANIA:
Zamiast: T1: lock(konto_5), lock(konto_2)
         T2: lock(konto_2), lock(konto_5)
Zawsze:  lock(konto_2), potem lock(konto_5)
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- PRZYKŁAD POWSTAWANIA DEADLOCK

-- Transakcja T1:
BEGIN;
UPDATE konta SET saldo = saldo - 100 WHERE id_konta = 1;  -- blokada konta 1
-- ... pauza ...
UPDATE konta SET saldo = saldo + 100 WHERE id_konta = 2;  -- czeka na konto 2
COMMIT;

-- Transakcja T2 (równolegle):
BEGIN;  
UPDATE konta SET saldo = saldo - 50 WHERE id_konta = 2;   -- blokada konta 2
-- ... pauza ...
UPDATE konta SET saldo = saldo + 50 WHERE id_konta = 1;   -- czeka na konto 1
COMMIT;
-- DEADLOCK! T1 czeka na T2, T2 czeka na T1

-- ROZWIĄZANIE 1: Uporządkowanie dostępu do zasobów
CREATE OR REPLACE FUNCTION transfer_between_accounts(
    from_account INT, 
    to_account INT, 
    amount DECIMAL(10,2)
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
    
    -- Blokowanie w uporządkowanej kolejności
    PERFORM * FROM konta WHERE id_konta = first_account FOR UPDATE;
    PERFORM * FROM konta WHERE id_konta = second_account FOR UPDATE;
    
    -- Teraz bezpieczne aktualizacje
    UPDATE konta SET saldo = saldo - amount WHERE id_konta = from_account;
    UPDATE konta SET saldo = saldo + amount WHERE id_konta = to_account;
END;
$$ LANGUAGE plpgsql;

-- ROZWIĄZANIE 2: Timeout i retry
CREATE OR REPLACE FUNCTION safe_transfer(
    from_account INT,
    to_account INT, 
    amount DECIMAL(10,2),
    max_retries INT DEFAULT 3
) RETURNS BOOLEAN AS $$
DECLARE
    retry_count INT := 0;
BEGIN
    LOOP
        BEGIN
            -- Ustaw timeout dla blokad
            SET lock_timeout = '2s';
            
            -- Wykonaj transfer
            UPDATE konta SET saldo = saldo - amount WHERE id_konta = from_account;
            UPDATE konta SET saldo = saldo + amount WHERE id_konta = to_account;
            
            RETURN TRUE;  -- sukces
            
        EXCEPTION
            WHEN lock_not_available THEN
                retry_count := retry_count + 1;
                IF retry_count >= max_retries THEN
                    RETURN FALSE;  -- za dużo prób
                END IF;
                -- Czekaj losowo i spróbuj ponownie
                PERFORM pg_sleep(random() * 0.1);
                
            WHEN deadlock_detected THEN
                retry_count := retry_count + 1;
                IF retry_count >= max_retries THEN
                    RETURN FALSE;
                END IF;
                -- Czekaj losowo i spróbuj ponownie  
                PERFORM pg_sleep(random() * 0.1);
        END;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- KONFIGURACJA DEADLOCK DETECTION W PostgreSQL
-- postgresql.conf:
SET deadlock_timeout = '1s';        -- jak szybko wykrywać deadlock
SET lock_timeout = '30s';           -- timeout dla pojedynczej blokady
SET statement_timeout = '60s';      -- timeout dla całego statement

-- MONITORING DEADLOCK
-- Włączenie logowania deadlocków
SET log_lock_waits = on;
SET log_statement = 'all';

-- Sprawdzenie aktualnych blokad
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS current_statement_in_blocking_process
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity 
    ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
JOIN pg_catalog.pg_stat_activity blocking_activity 
    ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- PRZYKŁAD WAIT-DIE ALGORITHM (konceptualny)
-- Starsza transakcja (mniejszy timestamp) czeka
-- Młodsza transakcja umiera i jest restartowana
BEGIN;
-- timestamp = 100 (stara transakcja)
LOCK TABLE tabela_A;
-- próbuje zablokować tabela_B zajętą przez transakcję z timestamp = 200
-- → czeka (stara czeka na młodą)

BEGIN;  
-- timestamp = 200 (młoda transakcja)  
LOCK TABLE tabela_B;
-- próbuje zablokować tabela_A zajętą przez transakcję z timestamp = 100
-- → umiera i restart (młoda umiera gdy czeka na starą)
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Wszystkie 4 warunki Coffmana muszą być spełnione jednocześnie
2. **UWAGA**: Deadlock ≠ starvation (to różne problemy!)
3. **BŁĄD**: Mylenie deadlock detection z deadlock prevention
4. **WAŻNE**: PostgreSQL automatycznie wykrywa i przerywa deadlocki
5. **PUŁAPKA**: Timeout nie rozwiązuje deadlock, tylko go przerywa

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Coffman conditions** - warunki Coffmana
- **Circular wait** - cykliczne czekanie
- **Wait-for graph** - graf czekania
- **Deadlock detection** - wykrywanie zakleszczenia
- **Resource ordering** - uporządkowanie zasobów
- **Timeout** - przekroczenie czasu
- **Rollback and retry** - cofnij i powtórz
- **Lock escalation** - eskalacja blokad

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **10-blokady** - mechanizmy blokowania
- **03-protokol-dwufazowy** - 2PL może powodować deadlock
- **07-poziomy-izolacji** - wyższe poziomy = więcej deadlocków
- **18-transakcje-acid** - atomowość przy deadlock
- **20-wspolbieznosc** - konkurencja o zasoby