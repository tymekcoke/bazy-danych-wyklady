# 🔒 BLOKADY W BAZACH DANYCH - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Blokady to mechanizm kontroli współbieżności, który zapewnia izolację transakcji przez ograniczenie dostępu do zasobów. Główne rodzaje to:

1. **Shared Lock (S)** - blokada czytania, wielu może czytać jednocześnie
2. **Exclusive Lock (X)** - blokada zapisu, tylko jedna transakcja ma dostęp
3. **Intent Locks** - IS, IX, SIX - sygnalizują zamiar blokowania na niższym poziomie

Blokady działają na różnych poziomach: wiersz, strona, tabela, baza danych. Kolizje powstają gdy transakcje próbują uzyskać niekompatybilne blokady na tym samym zasobie."

## ✍️ CO NAPISAĆ NA KARTCE

```
RODZAJE BLOKAD I KOMPATYBILNOŚĆ:

       | S  | X  | IS | IX | SIX |
-------|----|----|----|----|-----|
S      | ✓  | ✗  | ✓  | ✗  | ✗   |
X      | ✗  | ✗  | ✗  | ✗  | ✗   |  
IS     | ✓  | ✗  | ✓  | ✓  | ✓   |
IX     | ✗  | ✗  | ✓  | ✓  | ✗   |
SIX    | ✗  | ✗  | ✓  | ✗  | ✗   |

✓ = kompatybilne (może współistnieć)
✗ = niekompatybilne (jedna musi czekać)

OPIS BLOKAD:
S (Shared)     - czytanie, wielu może mieć jednocześnie
X (Exclusive)  - zapis, tylko jedna transakcja  
IS (Intent S)  - zamiar blokady S na poziomie niższym
IX (Intent X)  - zamiar blokady X na poziomie niższym
SIX (S+IX)     - shared + intent exclusive

POZIOMY BLOKOWANIA:
DATABASE → SCHEMA → TABLE → PAGE → ROW

PRZYKŁAD HIERARCHII:
T1: TABLE-IX → ROW-X(wiersz 5)
T2: TABLE-IS → ROW-S(wiersz 10) ✓ OK
T3: TABLE-X → ✗ CZEKA (konflikt z TABLE-IX)

KOLIZJE:
Read-Write: T1(S) vs T2(X) → T2 czeka
Write-Write: T1(X) vs T2(X) → T2 czeka  
Write-Read: T1(X) vs T2(S) → T2 czeka
Read-Read: T1(S) vs T2(S) → OK jednocześnie
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- EXPLICIT LOCKING W PostgreSQL

-- 1. BLOKADY WIERSZY (row-level)
BEGIN;
-- Shared lock na wierszu (może być wielu czytelników)
SELECT * FROM pracownicy WHERE id = 1 FOR SHARE;

-- Exclusive lock na wierszu (tylko jedna transakcja)  
SELECT * FROM pracownicy WHERE id = 1 FOR UPDATE;

-- Lock z timeout
SELECT * FROM pracownicy WHERE id = 1 FOR UPDATE NOWAIT;  -- błąd jeśli zajęte
SELECT * FROM pracownicy WHERE id = 1 FOR UPDATE SKIP LOCKED;  -- pomija zajęte

COMMIT;

-- 2. BLOKADY TABEL (table-level)  
BEGIN;
-- Różne tryby blokad tabel
LOCK TABLE pracownicy IN ACCESS SHARE MODE;        -- najsłabsza, dla SELECT
LOCK TABLE pracownicy IN ROW SHARE MODE;           -- dla SELECT FOR UPDATE
LOCK TABLE pracownicy IN ROW EXCLUSIVE MODE;       -- dla INSERT/UPDATE/DELETE  
LOCK TABLE pracownicy IN SHARE UPDATE EXCLUSIVE;   -- dla VACUUM, ANALYZE
LOCK TABLE pracownicy IN SHARE MODE;               -- dla CREATE INDEX
LOCK TABLE pracownicy IN SHARE ROW EXCLUSIVE;      -- rzadko używana
LOCK TABLE pracownicy IN EXCLUSIVE MODE;           -- blokuje wszystko oprócz SELECT
LOCK TABLE pracownicy IN ACCESS EXCLUSIVE MODE;    -- najsilniejsza, DDL

COMMIT;

-- 3. PRAKTYCZNY PRZYKŁAD - operacje bankowe
CREATE TABLE konta (
    id_konta INT PRIMARY KEY,
    saldo DECIMAL(10,2),
    wlasciciel VARCHAR(100)
);

-- Bezpieczny przelew z explicit locking
BEGIN;
    -- Zablokuj oba konta w uporządkowanej kolejności (deadlock prevention)  
    SELECT saldo FROM konta WHERE id_konta = 
        LEAST(100, 200) FOR UPDATE;  -- mniejsze ID pierwsze
    SELECT saldo FROM konta WHERE id_konta = 
        GREATEST(100, 200) FOR UPDATE;  -- większe ID drugie
    
    -- Sprawdź czy wystarczy środków
    IF (SELECT saldo FROM konta WHERE id_konta = 100) >= 500 THEN
        -- Wykonaj przelew
        UPDATE konta SET saldo = saldo - 500 WHERE id_konta = 100;
        UPDATE konta SET saldo = saldo + 500 WHERE id_konta = 200;
        COMMIT;
    ELSE
        ROLLBACK;
    END IF;

-- 4. MONITORING BLOKAD
-- Sprawdzenie aktualnych blokad w systemie
SELECT 
    l.locktype,
    l.database,
    l.relation::regclass AS table_name,
    l.page,
    l.tuple,
    l.mode,
    l.granted,
    a.query,
    a.query_start,
    a.pid
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE a.datname = current_database()
ORDER BY l.granted, l.pid;

-- Sprawdzenie blokujących się transakcji
WITH blocking_locks AS (
    SELECT DISTINCT
        bl.pid as blocked_pid,
        a.query as blocked_query,
        kl.pid as blocking_pid,
        ka.query as blocking_query
    FROM pg_catalog.pg_locks bl
    JOIN pg_catalog.pg_stat_activity a ON bl.pid = a.pid
    JOIN pg_catalog.pg_locks kl ON kl.transactionid = bl.transactionid
    JOIN pg_catalog.pg_stat_activity ka ON kl.pid = ka.pid
    WHERE NOT bl.granted AND kl.granted
)
SELECT * FROM blocking_locks;

-- 5. LOCK ESCALATION SIMULATION (PostgreSQL nie ma auto-escalation)
-- Ale można symulować:
BEGIN;
-- Wiele row locks może być droższe niż table lock
DECLARE
    row_count INT;
BEGIN
    SELECT COUNT(*) INTO row_count 
    FROM informacje_pracownikow WHERE departament = 'IT';
    
    IF row_count > 1000 THEN
        -- Za dużo wierszy - użyj table lock
        LOCK TABLE informacje_pracownikow IN SHARE MODE;
        SELECT * FROM informacje_pracownikow WHERE departament = 'IT';
    ELSE
        -- Mało wierszy - użyj row locks
        SELECT * FROM informacje_pracownikow 
        WHERE departament = 'IT' FOR SHARE;
    END IF;
END;
COMMIT;

-- 6. DEADLOCK PRZEZ BLOKADY - przykład do unikania
-- ZŁE - może powodować deadlock:
-- Transaction T1:
BEGIN;
LOCK TABLE tabela_A IN EXCLUSIVE MODE;
LOCK TABLE tabela_B IN EXCLUSIVE MODE;  -- może czekać na T2
COMMIT;

-- Transaction T2:  
BEGIN;
LOCK TABLE tabela_B IN EXCLUSIVE MODE;
LOCK TABLE tabela_A IN EXCLUSIVE MODE;  -- może czekać na T1 → DEADLOCK!
COMMIT;

-- DOBRE - uporządkowane blokowanie:
-- Zawsze blokuj tabele w alphabetical order
BEGIN;
LOCK TABLE tabela_A IN EXCLUSIVE MODE;  -- A przed B
LOCK TABLE tabela_B IN EXCLUSIVE MODE;
COMMIT;
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Shared locks są kompatybilne między sobą, exclusive nie
2. **UWAGA**: Intent locks sygnalizują zamiar, nie blokują bezpośrednio  
3. **BŁĄD**: Zapominanie o hierarchii - intent lock na tabeli, actual lock na wierszu
4. **WAŻNE**: PostgreSQL domyślnie używa MVCC, nie zawsze potrzeba explicit locks
5. **PUŁAPKA**: FOR UPDATE NOWAIT rzuca błąd natychmiast, nie czeka

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Shared/Exclusive locks** - blokady współdzielone/wyłączne
- **Intent locks** - blokady intencji (IS, IX, SIX)
- **Lock compatibility matrix** - macierz kompatybilności
- **Row-level locking** - blokady na poziomie wierszy
- **Table-level locking** - blokady na poziomie tabel
- **Lock escalation** - eskalacja blokad
- **MVCC** - Multi-Version Concurrency Control
- **Lock hierarchy** - hierarchia blokad

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **09-zakleszczenia** - deadlock przez blokady
- **03-protokol-dwufazowy** - 2PL używa blokad
- **07-poziomy-izolacji** - implementacja przez blokady
- **18-transakcje-acid** - izolacja przez blokady
- **20-wspolbieznosc** - kontrola współbieżności