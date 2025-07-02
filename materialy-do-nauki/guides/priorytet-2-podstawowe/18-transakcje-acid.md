# Transakcje + właściwości ACID

## Definicja transakcji

**Transakcja** to **logiczna jednostka pracy** składająca się z jednej lub więcej operacji na bazie danych, która jest wykonywana jako **niepodzielna całość**.

### Kluczowe cechy:
- **Niepodzielność** - albo wszystkie operacje się udają, albo żadna
- **Spójność** - baza danych pozostaje w spójnym stanie
- **Izolacja** - transakcje nie wpływają na siebie nawzajem
- **Trwałość** - zatwierdzone zmiany są permanentne

### Składnia podstawowa:
```sql
-- Rozpoczęcie transakcji
BEGIN;
START TRANSACTION;

-- Operacje w transakcji
INSERT INTO konta (id, saldo) VALUES (1, 1000);
UPDATE konta SET saldo = saldo - 100 WHERE id = 1;
UPDATE konta SET saldo = saldo + 100 WHERE id = 2;

-- Zatwierdzenie lub wycofanie
COMMIT;    -- Zatwierdź zmiany
ROLLBACK;  -- Wycofaj zmiany
```

## Właściwości ACID

### A - **Atomicity (Atomowość)**

#### Definicja:
Transakcja jest **niepodzielna** - albo wszystkie operacje w niej zawarte są wykonane pomyślnie, albo żadna z nich nie jest wykonana.

#### Przykład transferu pieniędzy:
```sql
BEGIN;
    -- Operacja 1: Odejmij z konta źródłowego
    UPDATE konta SET saldo = saldo - 500 WHERE id = 101;
    
    -- Operacja 2: Dodaj do konta docelowego  
    UPDATE konta SET saldo = saldo + 500 WHERE id = 102;
    
    -- Jeśli KTÓRAKOLWIEK operacja się nie powiedzie → ROLLBACK całości
    -- Jeśli OBE się udadzą → COMMIT całości
COMMIT;

-- Atomowość gwarantuje:
-- - Albo oba konta są zaktualizowane
-- - Albo żadne konto nie jest zmienione
-- NIGDY sytuacja: jedno konto zmienione, drugie nie
```

#### Naruszenie atomowości (przykład błędny):
```sql
-- ❌ BEZ TRANSAKCJI - brak atomowości!
UPDATE konta SET saldo = saldo - 500 WHERE id = 101;  -- Udało się
-- CRASH systemu tutaj!
UPDATE konta SET saldo = saldo + 500 WHERE id = 102;  -- Nie wykonane

-- Wynik: Pieniądze znikły! (konto 101: -500, konto 102: bez zmian)
```

### C - **Consistency (Spójność)**

#### Definicja:
Transakcja prowadzi bazę danych z **jednego spójnego stanu do innego spójnego stanu**, zachowując wszystkie reguły integralności.

#### Przykład reguł spójności:
```sql
-- Reguła 1: Saldo konta nie może być ujemne
ALTER TABLE konta ADD CONSTRAINT saldo_nieujemne CHECK (saldo >= 0);

-- Reguła 2: Suma wszystkich sald musi się zgadzać
CREATE TABLE stan_banku (
    id INT PRIMARY KEY DEFAULT 1,
    suma_sald DECIMAL(15,2) NOT NULL,
    CHECK (id = 1)  -- Tylko jeden rekord
);

-- Spójność zapewniana przez transakcję
BEGIN;
    DECLARE saldo_przed DECIMAL(15,2);
    DECLARE saldo_po DECIMAL(15,2);
    
    -- Sprawdź stan przed
    SELECT saldo INTO saldo_przed FROM konta WHERE id = 101;
    
    -- Transfer
    UPDATE konta SET saldo = saldo - 200 WHERE id = 101;
    UPDATE konta SET saldo = saldo + 200 WHERE id = 102;
    
    -- Sprawdź czy reguły są zachowane
    SELECT saldo INTO saldo_po FROM konta WHERE id = 101;
    
    IF saldo_po < 0 THEN
        ROLLBACK;  -- Naruszona reguła integralności
    END IF;
    
    -- Aktualizuj stan banku
    UPDATE stan_banku SET suma_sald = (SELECT SUM(saldo) FROM konta);
COMMIT;
```

#### Rodzaje ograniczeń spójności:
```sql
-- Ograniczenia encji
ALTER TABLE pracownicy ADD CONSTRAINT pk_pracownik PRIMARY KEY (id);

-- Ograniczenia referencyjne  
ALTER TABLE zamowienia ADD CONSTRAINT fk_klient 
    FOREIGN KEY (id_klienta) REFERENCES klienci(id);

-- Ograniczenia domeny
ALTER TABLE produkty ADD CONSTRAINT cena_dodatnia CHECK (cena > 0);

-- Ograniczenia biznesowe
ALTER TABLE pracownicy ADD CONSTRAINT pensja_w_zakresie 
    CHECK (pensja BETWEEN 2000 AND 50000);
```

### I - **Isolation (Izolacja)**

#### Definicja:
**Współbieżne transakcje** nie wpływają na siebie nawzajem - każda transakcja jest wykonywana tak, jakby była jedyną działającą w systemie.

#### Poziomy izolacji (powtórzenie z guide'a 07):
```sql
-- READ UNCOMMITTED - najniższa izolacja
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

-- READ COMMITTED - domyślna w większości SZBD
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- REPEATABLE READ - powtarzalne odczyty
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- SERIALIZABLE - najwyższa izolacja
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

#### Przykład problemu bez izolacji:
```sql
-- Transakcja 1
BEGIN;
    SELECT saldo FROM konta WHERE id = 101;  -- wynik: 1000
    -- ... obliczenia ...
    UPDATE konta SET saldo = 900 WHERE id = 101;  -- -100
COMMIT;

-- Transakcja 2 (równolegle)
BEGIN;
    SELECT saldo FROM konta WHERE id = 101;  -- wynik: 1000 (stara wartość!)
    -- ... obliczenia ...
    UPDATE konta SET saldo = 800 WHERE id = 101;  -- -200
COMMIT;

-- Problem: Druga transakcja nie wie o zmianach pierwszej!
-- Zamiast saldo = 700 (1000-100-200), otrzymujemy saldo = 800
```

#### Prawidłowa izolacja:
```sql
-- Transakcja 1
BEGIN;
    SELECT saldo FROM konta WHERE id = 101 FOR UPDATE;  -- Blokada
    UPDATE konta SET saldo = saldo - 100 WHERE id = 101;
COMMIT;

-- Transakcja 2 musi czekać na zakończenie Transakcji 1
BEGIN;
    SELECT saldo FROM konta WHERE id = 101 FOR UPDATE;  -- Czeka...
    UPDATE konta SET saldo = saldo - 200 WHERE id = 101;  -- Po odblokowaniu
COMMIT;
```

### D - **Durability (Trwałość)**

#### Definicja:
Po **COMMIT** transakcji, jej skutki są **trwale zapisane** w bazie danych i przetrwają awarie systemu.

#### Mechanizmy zapewniające trwałość:

##### 1. **Write-Ahead Logging (WAL)**
```sql
-- Sekwencja zapisu:
1. Zapisz LOG RECORD do pliku dziennika (WAL)
2. Zapisz DATA PAGES do bazy danych
3. Potwierdź COMMIT użytkownikowi

-- Struktura log record:
[TRANSACTION_ID] [OPERATION] [TABLE] [OLD_VALUE] [NEW_VALUE] [TIMESTAMP]
```

##### 2. **Checkpoints**
```sql
-- PostgreSQL checkpoint
CHECKPOINT;

-- Okresowe checkpointy
-- Zapisują wszystkie zmienione strony z pamięci na dysk
-- Umożliwiają skrócenie czasu recovery
```

##### 3. **Recovery po awarii**
```sql
-- REDO: Odtwórz zatwierdzone transakcje
FOR each log_record WHERE transaction_status = 'COMMITTED':
    Apply changes from log_record

-- UNDO: Wycofaj niezatwierdzone transakcje  
FOR each log_record WHERE transaction_status = 'ACTIVE':
    Reverse changes from log_record
```

#### Przykład utraty trwałości (błędny):
```sql
-- ❌ Aplikacja bez dbania o trwałość
BEGIN;
    INSERT INTO zamowienia VALUES (1, 'Laptop', 3000);
COMMIT;  -- Użytkownik dostaje potwierdzenie

-- CRASH serwera przed zapisem na dysk
-- Zamówienie ginie! Naruszenie trwałości
```

#### Prawidłowa trwałość:
```sql
-- ✅ System z WAL
BEGIN;
    INSERT INTO zamowienia VALUES (1, 'Laptop', 3000);
    -- 1. Zapisz do WAL log: "INSERT zamowienia (1, 'Laptop', 3000)"
    -- 2. Periodically flush WAL to disk
COMMIT;  -- 3. COMMIT tylko po zapisaniu WAL na dysk

-- Po crash: system odczyta WAL i odtworzy transakcję
```

## Stany transakcji

### Diagram stanów:
```
ACTIVE → PARTIALLY_COMMITTED → COMMITTED
  ↓              ↓
FAILED ←    ABORTED
```

### Opis stanów:
```sql
-- ACTIVE - transakcja w trakcie wykonywania
BEGIN;
    SELECT * FROM konta;  -- Stan: ACTIVE
    
-- PARTIALLY_COMMITTED - wszystkie operacje wykonane, czeka na COMMIT
    UPDATE konta SET saldo = 1000;  -- Ostatnia operacja
    -- Stan: PARTIALLY_COMMITTED
    
-- COMMITTED - transakcja zatwierdzona
COMMIT;  -- Stan: COMMITTED

-- FAILED - wystąpił błąd
BEGIN;
    UPDATE konta SET saldo = -100;  -- Naruszenie CHECK constraint
    -- Stan: FAILED (automatycznie)
    
-- ABORTED - transakcja wycofana
ROLLBACK;  -- Stan: ABORTED
```

## Typy transakcji

### 1. **Flat Transactions** (płaskie)
```sql
-- Prosta transakcja bez zagnieżdżeń
BEGIN;
    INSERT INTO klienci VALUES (1, 'Jan Kowalski');
    INSERT INTO zamowienia VALUES (1, 1, '2024-03-15');
    UPDATE produkty SET stan = stan - 1 WHERE id = 5;
COMMIT;
```

### 2. **Nested Transactions** (zagnieżdżone)
```sql
-- PostgreSQL Savepoints (podobne do nested)
BEGIN;
    INSERT INTO zamowienia VALUES (1, 1, '2024-03-15');
    
    SAVEPOINT sp1;
        INSERT INTO pozycje VALUES (1, 1, 2);  -- Może się nie udać
        INSERT INTO pozycje VALUES (1, 2, 1);
    -- Jeśli błąd w pozycjach:
    ROLLBACK TO sp1;  -- Cofnij tylko pozycje, zostaw zamówienie
    
    INSERT INTO historia VALUES (1, 'Zamówienie utworzone');
COMMIT;  -- Zatwierdź całość
```

### 3. **Distributed Transactions** (rozproszone)
```sql
-- Two-Phase Commit (2PC)
-- Faza 1: PREPARE
PREPARE TRANSACTION 'tx_001';  -- Na wszystkich węzłach

-- Faza 2: COMMIT lub ABORT
COMMIT PREPARED 'tx_001';      -- Jeśli wszystkie OK
-- lub
ROLLBACK PREPARED 'tx_001';    -- Jeśli któryś failed
```

## Implementacja w różnych SZBD

### PostgreSQL:
```sql
-- Automatyczny autocommit OFF
BEGIN;
    -- operacje
COMMIT;

-- Explicit autocommit control
SET autocommit = off;
-- każda operacja wymaga explicit COMMIT

-- Read-only transactions
BEGIN READ ONLY;
    SELECT * FROM produkty;
COMMIT;
```

### MySQL:
```sql
-- Autocommit domyślnie ON
SET autocommit = 0;  -- Wyłącz

START TRANSACTION;
    -- operacje
COMMIT;

-- Transaction characteristics
START TRANSACTION READ ONLY, ISOLATION LEVEL SERIALIZABLE;
```

### SQL Server:
```sql
-- Implicit transactions
SET IMPLICIT_TRANSACTIONS ON;
-- Każda DML statement rozpoczyna transakcję

BEGIN TRANSACTION;
    -- operacje
COMMIT TRANSACTION;

-- Named transactions
BEGIN TRANSACTION my_transaction;
    -- operacje
COMMIT TRANSACTION my_transaction;
```

## Monitoring transakcji

### PostgreSQL:
```sql
-- Aktywne transakcje
SELECT 
    pid,
    state,
    query_start,
    state_change,
    query
FROM pg_stat_activity 
WHERE state IN ('active', 'idle in transaction');

-- Długo trwające transakcje
SELECT 
    pid,
    now() - query_start AS duration,
    query
FROM pg_stat_activity 
WHERE state = 'active' 
  AND now() - query_start > interval '5 minutes';

-- Blokady transakcji
SELECT * FROM pg_locks WHERE NOT granted;
```

### MySQL:
```sql
-- Aktywne transakcje (InnoDB)
SELECT * FROM information_schema.INNODB_TRX;

-- Blokady
SELECT * FROM information_schema.INNODB_LOCKS;
SELECT * FROM information_schema.INNODB_LOCK_WAITS;

-- Status transakcji
SHOW ENGINE INNODB STATUS;
```

## Optymalizacja transakcji

### 1. **Krótkie transakcje**
```sql
-- ❌ ŹLE - długa transakcja
BEGIN;
    SELECT * FROM duza_tabela;  -- Długo trwa
    -- ... obliczenia w aplikacji (5 minut) ...
    UPDATE wyniki SET wartosc = 123;
COMMIT;

-- ✅ DOBRZE - krótka transakcja
-- Obliczenia poza transakcją
wynik = oblicz_wartosc();

BEGIN;
    UPDATE wyniki SET wartosc = wynik;
COMMIT;
```

### 2. **Batch processing**
```sql
-- ❌ ŹLE - jedna transakcja dla wszystkich
BEGIN;
    FOR i IN 1..1000000 LOOP
        INSERT INTO logs VALUES (i, 'data');
    END LOOP;
COMMIT;  -- Bardzo duża transakcja

-- ✅ DOBRZE - batch'e
FOR batch IN 0..999 LOOP
    BEGIN;
        FOR i IN (batch*1000 + 1)..(batch*1000 + 1000) LOOP
            INSERT INTO logs VALUES (i, 'data');
        END LOOP;
    COMMIT;
END LOOP;
```

### 3. **Read-only optimization**
```sql
-- Dla zapytań tylko do odczytu
BEGIN READ ONLY;
    SELECT COUNT(*) FROM orders WHERE date > '2024-01-01';
    SELECT AVG(price) FROM products;
COMMIT;

-- Korzyści:
-- - Brak conflict'ów z write transactions
-- - Możliwość snapshot reads
-- - Lepsza wydajność
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**
1. **Krótkie transakcje** - minimalizuj czas trzymania blokad
2. **Explicit boundaries** - zawsze używaj BEGIN/COMMIT
3. **Error handling** - obsługuj ROLLBACK przy błędach
4. **Read-only gdy można** - dla queries bez zmian
5. **Batch large operations** - dziel duże operacje

### ❌ **Złe praktyki:**
1. **User interaction w transakcji** - czekanie na użytkownika
2. **Długie obliczenia** - w środku transakcji
3. **Brak error handling** - nie obsługiwanie błędów
4. **Nested transactions** - bez savepoints
5. **Autocommit confusion** - nie wiedzenie jaki tryb

## Przykłady praktyczne

### Transfer z pełną obsługą:
```sql
CREATE OR REPLACE FUNCTION safe_transfer(
    from_account INT,
    to_account INT,
    amount DECIMAL(15,2)
)
RETURNS TEXT AS $$
DECLARE
    from_balance DECIMAL(15,2);
BEGIN
    -- Walidacja parametrów
    IF amount <= 0 THEN
        RETURN 'ERROR: Amount must be positive';
    END IF;
    
    -- Sprawdź saldo (z blokadą)
    SELECT balance INTO from_balance 
    FROM accounts 
    WHERE id = from_account 
    FOR UPDATE;
    
    IF NOT FOUND THEN
        RETURN 'ERROR: Source account not found';
    END IF;
    
    IF from_balance < amount THEN
        RETURN 'ERROR: Insufficient funds';
    END IF;
    
    -- Sprawdź konto docelowe
    IF NOT EXISTS (SELECT 1 FROM accounts WHERE id = to_account) THEN
        RETURN 'ERROR: Destination account not found';
    END IF;
    
    -- Wykonaj transfer
    UPDATE accounts SET balance = balance - amount WHERE id = from_account;
    UPDATE accounts SET balance = balance + amount WHERE id = to_account;
    
    -- Log transakcji
    INSERT INTO transfer_log (from_acc, to_acc, amount, transfer_date)
    VALUES (from_account, to_account, amount, CURRENT_TIMESTAMP);
    
    RETURN 'SUCCESS: Transfer completed';
    
EXCEPTION
    WHEN OTHERS THEN
        -- Automatyczny ROLLBACK przy wyjątku
        RETURN 'ERROR: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Wywołanie w transakcji
BEGIN;
    SELECT safe_transfer(101, 102, 500.00);
COMMIT;
```

## Pułapki egzaminacyjne

### 1. **ACID Properties**
- **A**tomicity: Wszystko albo nic
- **C**onsistency: Zachowanie reguł integralności
- **I**solation: Niezależność transakcji
- **D**urability: Trwałość po COMMIT

### 2. **Stany transakcji**
- Active → Partially Committed → Committed
- Active → Failed → Aborted

### 3. **Autocommit vs Manual**
- Autocommit ON: każda operacja = transakcja
- Autocommit OFF: manual BEGIN/COMMIT

### 4. **Savepoints**
- Częściowy rollback w transakcji
- Nie zastępują pełnych transakcji