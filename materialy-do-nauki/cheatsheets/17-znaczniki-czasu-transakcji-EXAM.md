# ⏰ ZNACZNIKI CZASU TRANSAKCJI - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekunds)

"Znaczniki czasu transakcji (timestamp ordering) to metoda kontroli współbieżności, gdzie każda transakcja otrzymuje unikalny timestamp i operacje są wykonywane zgodnie z kolejnością tych znaczników.

Zasady:
1. **Transakcja starsza** (mniejszy timestamp) ma priorytet nad młodszą
2. **Write-timestamp** - kiedy ostatnio pisano do obiektu  
3. **Read-timestamp** - kiedy ostatnio czytano z obiektu
4. **Reguły dostępu**: starsza transakcja może czytać/pisać, młodsza może być odrzucona

Algorytmy: Basic Timestamp Ordering, Thomas Write Rule, Multiversion Timestamp Ordering."

## ✍️ CO NAPISAĆ NA KARTCE

```
TIMESTAMP ORDERING (TO) - ZASADY:

KAŻDA TRANSAKCJA OTRZYMUJE TIMESTAMP (TS):
- TS(Ti) < TS(Tj) → Ti jest starsza niż Tj
- Timestamp może być: system clock, logiczny licznik, hybrid

KAŻDY OBIEKT MA:
- R-TS(X) - timestamp ostatniego czytania X
- W-TS(X) - timestamp ostatniego pisania X

BASIC TIMESTAMP ORDERING RULES:

1. READ OPERATION - Ti chce czytać X:
   IF TS(Ti) < W-TS(X) THEN
       ABORT Ti  -- młodsza transakcja próbuje czytać po pisaniu przez starszą
   ELSE
       ALLOW READ
       R-TS(X) = max(R-TS(X), TS(Ti))

2. WRITE OPERATION - Ti chce pisać X:
   IF TS(Ti) < R-TS(X) OR TS(Ti) < W-TS(X) THEN
       ABORT Ti  -- młodsza próbuje pisać po czytaniu/pisaniu przez starszą
   ELSE  
       ALLOW WRITE
       W-TS(X) = TS(Ti)

PRZYKŁAD:
T1: TS=10, T2: TS=20, T3: TS=30

Obiekt X: R-TS(X)=0, W-TS(X)=0

1. T1 read(X)  → OK, R-TS(X)=10
2. T2 write(X) → OK, W-TS(X)=20
3. T1 write(X) → ABORT! (TS(T1)=10 < W-TS(X)=20)

THOMAS WRITE RULE - optymalizacja:
Jeśli TS(Ti) < W-TS(X) to ignoruj write (nie abort)
- "Późniejsza transakcja już nadpisała" 

MULTIVERSION TO:
- Każdy write tworzy nową wersję obiektu
- Read czyta najnowszą wersję starszą niż jego TS
- Rzadziej abortuje transakcje
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- SYMULACJA TIMESTAMP ORDERING W PostgreSQL
-- (PostgreSQL używa MVCC, ale możemy zasymulować TO)

-- Tabela do śledzenia timestampów obiektów
CREATE TABLE object_timestamps (
    object_name VARCHAR(50) PRIMARY KEY,
    read_timestamp BIGINT DEFAULT 0,
    write_timestamp BIGINT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Tabela do śledzenia transakcji
CREATE TABLE transaction_log (
    transaction_id BIGINT PRIMARY KEY,
    start_time TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'ACTIVE',  -- ACTIVE, COMMITTED, ABORTED
    timestamp_value BIGINT
);

-- Funkcja generująca timestamp dla transakcji
CREATE OR REPLACE FUNCTION get_transaction_timestamp()
RETURNS BIGINT AS $$
DECLARE
    new_ts BIGINT;
BEGIN
    -- Używamy microseconds od epoch jako timestamp
    SELECT EXTRACT(EPOCH FROM NOW() AT TIME ZONE 'UTC') * 1000000 INTO new_ts;
    RETURN new_ts;
END;
$$ LANGUAGE plpgsql;

-- Funkcja rozpoczynająca transakcję z timestamp
CREATE OR REPLACE FUNCTION start_timestamped_transaction(trans_id BIGINT)
RETURNS BIGINT AS $$
DECLARE
    trans_ts BIGINT;
BEGIN
    trans_ts := get_transaction_timestamp();
    
    INSERT INTO transaction_log (transaction_id, timestamp_value)
    VALUES (trans_id, trans_ts);
    
    RAISE NOTICE 'Transakcja % rozpoczęta z timestamp %', trans_id, trans_ts;
    RETURN trans_ts;
END;
$$ LANGUAGE plpgsql;

-- Funkcja sprawdzająca czy read jest dozwolony (Basic TO)
CREATE OR REPLACE FUNCTION can_read_object(
    trans_id BIGINT,
    object_name VARCHAR(50)
) RETURNS BOOLEAN AS $$
DECLARE
    trans_ts BIGINT;
    write_ts BIGINT;
BEGIN
    -- Pobierz timestamp transakcji
    SELECT timestamp_value INTO trans_ts
    FROM transaction_log
    WHERE transaction_id = trans_id AND status = 'ACTIVE';
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Transakcja % nie istnieje lub nie jest aktywna', trans_id;
    END IF;
    
    -- Pobierz write timestamp obiektu
    SELECT write_timestamp INTO write_ts
    FROM object_timestamps
    WHERE object_name = can_read_object.object_name;
    
    -- Jeśli obiekt nie istnieje, utwórz go
    IF NOT FOUND THEN
        INSERT INTO object_timestamps (object_name) VALUES (can_read_object.object_name);
        write_ts := 0;
    END IF;
    
    -- REGUŁA: TS(Ti) >= W-TS(X)
    IF trans_ts < write_ts THEN
        RAISE NOTICE 'READ REJECTED: T% (ts=%) próbuje czytać X po write przez T(ts=%)', 
                     trans_id, trans_ts, write_ts;
        RETURN FALSE;
    ELSE
        RAISE NOTICE 'READ ALLOWED: T% (ts=%) czyta X', trans_id, trans_ts;
        RETURN TRUE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Funkcja wykonująca read z aktualizacją R-TS
CREATE OR REPLACE FUNCTION read_object(
    trans_id BIGINT,
    object_name VARCHAR(50)
) RETURNS BOOLEAN AS $$
DECLARE
    trans_ts BIGINT;
    current_read_ts BIGINT;
BEGIN
    -- Sprawdź czy read jest dozwolony
    IF NOT can_read_object(trans_id, object_name) THEN
        -- Abort transakcji
        UPDATE transaction_log 
        SET status = 'ABORTED' 
        WHERE transaction_id = trans_id;
        
        RAISE EXCEPTION 'Transakcja % abortowana - read conflict', trans_id;
    END IF;
    
    -- Pobierz timestamp transakcji
    SELECT timestamp_value INTO trans_ts
    FROM transaction_log
    WHERE transaction_id = trans_id;
    
    -- Aktualizuj R-TS(X) = max(R-TS(X), TS(Ti))
    UPDATE object_timestamps
    SET read_timestamp = GREATEST(read_timestamp, trans_ts),
        last_updated = NOW()
    WHERE object_name = read_object.object_name;
    
    RAISE NOTICE 'READ COMPLETED: T% przeczytała X, R-TS(X) = %', trans_id, trans_ts;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Funkcja sprawdzająca czy write jest dozwolony
CREATE OR REPLACE FUNCTION can_write_object(
    trans_id BIGINT,
    object_name VARCHAR(50)
) RETURNS BOOLEAN AS $$
DECLARE
    trans_ts BIGINT;
    read_ts BIGINT;
    write_ts BIGINT;
BEGIN
    -- Pobierz timestamp transakcji
    SELECT timestamp_value INTO trans_ts
    FROM transaction_log
    WHERE transaction_id = trans_id AND status = 'ACTIVE';
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Transakcja % nie istnieje lub nie jest aktywna', trans_id;
    END IF;
    
    -- Pobierz timestamps obiektu
    SELECT read_timestamp, write_timestamp INTO read_ts, write_ts
    FROM object_timestamps
    WHERE object_name = can_write_object.object_name;
    
    -- Jeśli obiekt nie istnieje, utwórz go
    IF NOT FOUND THEN
        INSERT INTO object_timestamps (object_name) VALUES (can_write_object.object_name);
        read_ts := 0;
        write_ts := 0;
    END IF;
    
    -- REGUŁA: TS(Ti) >= R-TS(X) AND TS(Ti) >= W-TS(X)
    IF trans_ts < read_ts THEN
        RAISE NOTICE 'WRITE REJECTED: T% (ts=%) próbuje pisać X po read przez T(ts=%)', 
                     trans_id, trans_ts, read_ts;
        RETURN FALSE;
    ELSIF trans_ts < write_ts THEN
        RAISE NOTICE 'WRITE REJECTED: T% (ts=%) próbuje pisać X po write przez T(ts=%)', 
                     trans_id, trans_ts, write_ts;
        RETURN FALSE;
    ELSE
        RAISE NOTICE 'WRITE ALLOWED: T% (ts=%) pisze X', trans_id, trans_ts;
        RETURN TRUE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Funkcja wykonująca write z aktualizacją W-TS
CREATE OR REPLACE FUNCTION write_object(
    trans_id BIGINT,
    object_name VARCHAR(50)
) RETURNS BOOLEAN AS $$
DECLARE
    trans_ts BIGINT;
BEGIN
    -- Sprawdź czy write jest dozwolony
    IF NOT can_write_object(trans_id, object_name) THEN
        -- Abort transakcji
        UPDATE transaction_log 
        SET status = 'ABORTED' 
        WHERE transaction_id = trans_id;
        
        RAISE EXCEPTION 'Transakcja % abortowana - write conflict', trans_id;
    END IF;
    
    -- Pobierz timestamp transakcji
    SELECT timestamp_value INTO trans_ts
    FROM transaction_log
    WHERE transaction_id = trans_id;
    
    -- Aktualizuj W-TS(X) = TS(Ti)
    UPDATE object_timestamps
    SET write_timestamp = trans_ts,
        last_updated = NOW()
    WHERE object_name = write_object.object_name;
    
    RAISE NOTICE 'WRITE COMPLETED: T% zapisała X, W-TS(X) = %', trans_id, trans_ts;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- THOMAS WRITE RULE - optymalizacja
CREATE OR REPLACE FUNCTION write_object_thomas_rule(
    trans_id BIGINT,
    object_name VARCHAR(50)
) RETURNS BOOLEAN AS $$
DECLARE
    trans_ts BIGINT;
    read_ts BIGINT;
    write_ts BIGINT;
BEGIN
    SELECT timestamp_value INTO trans_ts
    FROM transaction_log
    WHERE transaction_id = trans_id AND status = 'ACTIVE';
    
    SELECT read_timestamp, write_timestamp INTO read_ts, write_ts
    FROM object_timestamps
    WHERE object_name = write_object_thomas_rule.object_name;
    
    IF NOT FOUND THEN
        INSERT INTO object_timestamps (object_name) VALUES (write_object_thomas_rule.object_name);
        read_ts := 0;
        write_ts := 0;
    END IF;
    
    -- Sprawdź konflikt z read
    IF trans_ts < read_ts THEN
        UPDATE transaction_log SET status = 'ABORTED' WHERE transaction_id = trans_id;
        RAISE EXCEPTION 'Transakcja % abortowana - read conflict', trans_id;
    END IF;
    
    -- THOMAS RULE: jeśli TS(Ti) < W-TS(X) to ignoruj write
    IF trans_ts < write_ts THEN
        RAISE NOTICE 'WRITE IGNORED (Thomas Rule): T% (ts=%) - nowsza wersja już istnieje (ts=%)', 
                     trans_id, trans_ts, write_ts;
        RETURN TRUE;  -- Nie abort, tylko ignoruj
    END IF;
    
    -- Normalny write
    UPDATE object_timestamps
    SET write_timestamp = trans_ts,
        last_updated = NOW()
    WHERE object_name = write_object_thomas_rule.object_name;
    
    RAISE NOTICE 'WRITE COMPLETED (Thomas Rule): T% zapisała X, W-TS(X) = %', trans_id, trans_ts;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- PRZYKŁAD UŻYCIA - symulacja konfliktu

-- Cleanup
DELETE FROM object_timestamps;
DELETE FROM transaction_log;

-- Rozpocznij transakcje z różnymi timestamp
SELECT start_timestamped_transaction(1);  -- T1 - starsza
SELECT pg_sleep(0.01);  -- małe opóźnienie dla różnych timestamp
SELECT start_timestamped_transaction(2);  -- T2 - młodsza

-- Scenariusz prowadzący do abortu
SELECT read_object(1, 'AccountA');   -- T1 czyta A
SELECT write_object(2, 'AccountA');  -- T2 pisze A  
SELECT write_object(1, 'AccountA');  -- T1 próbuje pisać A → ABORT!

-- Sprawdź stan
SELECT * FROM transaction_log ORDER BY transaction_id;
SELECT * FROM object_timestamps;

-- MONITORING I STATYSTYKI
CREATE VIEW timestamp_ordering_stats AS
SELECT 
    COUNT(*) as total_transactions,
    COUNT(*) FILTER (WHERE status = 'COMMITTED') as committed,
    COUNT(*) FILTER (WHERE status = 'ABORTED') as aborted,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'ABORTED') / COUNT(*), 2) as abort_rate
FROM transaction_log;

SELECT * FROM timestamp_ordering_stats;
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Timestamp określa kolejność logiczną, nie fizyczną
2. **UWAGA**: Basic TO może dużo abortować, Thomas Rule optymalizuje
3. **BŁĄD**: Mylenie timestamp ordering z 2PL (to różne metody)
4. **WAŻNE**: MVCC w PostgreSQL to evolution timestamp ordering
5. **PUŁAPKA**: Starvation młodszych transakcji przy dużym obciążeniu

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Timestamp ordering (TO)** - uporządkowanie przez znaczniki czasu
- **Read/Write timestamp** - znaczniki czytania/pisania
- **Basic timestamp ordering** - podstawowe TO
- **Thomas Write Rule** - reguła Thomasa
- **Multiversion TO** - wielowersyjne TO
- **Logical clock** - zegar logiczny
- **Conflict detection** - wykrywanie konfliktów
- **Transaction abort** - przerwanie transakcji

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **20-wspolbieznosc** - kontrola współbieżności
- **03-protokol-dwufazowy** - alternatywna metoda kontroli
- **07-poziomy-izolacji** - implementacja izolacji
- **18-transakcje-acid** - atomowość i izolacja
- **04-przebiegi-transakcji** - serializowalność