# Współbieżność - problemy i rozwiązania

## Definicja współbieżności

**Współbieżność** w bazach danych oznacza sytuację, w której **wiele transakcji jest wykonywanych jednocześnie** w systemie, współdzieląc te same zasoby (tabele, rekordy, bloki danych).

### Cele współbieżności:
- **Zwiększenie wydajności** - wykorzystanie czasu oczekiwania I/O
- **Lepsza responsywność** - krótsze czasy odpowiedzi
- **Większa przepustowość** - więcej transakcji na sekundę
- **Optymalne wykorzystanie zasobów** - CPU, pamięć, dyski

## Problemy współbieżności

### 1. 🧹 **Dirty Read (Brudny odczyt)**

#### Definicja:
Transakcja **odczytuje dane zmienione** przez inną transakcję, która **jeszcze nie została zatwierdzona**.

#### Przykład:
```sql
-- Transakcja T1
BEGIN;
    UPDATE konta SET saldo = 1500 WHERE id = 1;  -- Było 1000
    -- T1 jeszcze nie COMMIT
    
-- Transakcja T2 (równolegle)
BEGIN;
    SELECT saldo FROM konta WHERE id = 1;  -- Odczytuje 1500!
    -- T2 bazuje na niezatwierdzonych danych
COMMIT;

-- T1 w międzyczasie
ROLLBACK;  -- Saldo wraca do 1000!

-- Problem: T2 odczytało "brudne" dane (1500), które nie zostały zatwierdzone
```

#### Skutki:
- **Nieprawidłowe kalkulacje** oparte na błędnych danych
- **Niespójne raporty** - różne wyniki w zależności od momentu odczytu
- **Błędne decyzje biznesowe** - oparte na danych które mogą zniknąć

### 2. 🔄 **Non-Repeatable Read (Niepowtarzalny odczyt)**

#### Definicja:
**Ten sam odczyt** wykonany **dwukrotnie w tej samej transakcji** daje **różne wyniki**.

#### Przykład:
```sql
-- Transakcja T1
BEGIN;
    SELECT saldo FROM konta WHERE id = 1;  -- Wynik: 1000
    
    -- W międzyczasie T2:
    -- UPDATE konta SET saldo = 1200 WHERE id = 1; COMMIT;
    
    SELECT saldo FROM konta WHERE id = 1;  -- Wynik: 1200 (różny!)
COMMIT;

-- Problem: Ta sama instrukcja SELECT dała różne wyniki w jednej transakcji
```

#### Przypadki użycia problemowego:
```sql
-- Obliczanie odsetek
BEGIN;
    saldo1 := SELECT saldo FROM konta WHERE id = 1;  -- 1000
    -- ... skomplikowane obliczenia ...
    saldo2 := SELECT saldo FROM konta WHERE id = 1;  -- 1200 (ktoś wpłacił)
    
    -- Odsetki obliczone na podstawie saldo1, ale sprawdzenie na saldo2
    IF saldo2 >= minimum THEN
        UPDATE konta SET saldo = saldo + odsetki;  -- Błędne odsetki!
    END IF;
COMMIT;
```

### 3. 👻 **Phantom Read (Fantom)**

#### Definicja:
**Nowe rekordy** pojawiają się (lub znikają) między **kolejnymi wykonaniami tego samego zapytania** w transakcji.

#### Przykład:
```sql
-- Transakcja T1
BEGIN;
    SELECT COUNT(*) FROM zamowienia WHERE data = '2024-03-15';  -- Wynik: 5
    
    -- W międzyczasie T2:
    -- INSERT INTO zamowienia VALUES (..., '2024-03-15'); COMMIT;
    
    SELECT COUNT(*) FROM zamowienia WHERE data = '2024-03-15';  -- Wynik: 6 (fantom!)
COMMIT;

-- Problem: Pojawił się nowy rekord (fantom) spełniający warunek
```

#### Przykład z aggregates:
```sql
-- Raport finansowy
BEGIN;
    suma1 := SELECT SUM(kwota) FROM transakcje WHERE data = CURRENT_DATE;  -- 10000
    max1 := SELECT MAX(kwota) FROM transakcje WHERE data = CURRENT_DATE;   -- 5000
    
    -- Ktoś dodaje transakcję na 8000
    
    suma2 := SELECT SUM(kwota) FROM transakcje WHERE data = CURRENT_DATE;  -- 18000
    max2 := SELECT MAX(kwota) FROM transakcje WHERE data = CURRENT_DATE;   -- 8000
    
    -- Raport niespójny: suma się zmieniła, maksimum też!
COMMIT;
```

### 4. 💥 **Lost Update (Utracona aktualizacja)**

#### Definicja:
**Zmiany jednej transakcji** są **nadpisywane przez drugą transakcję**, prowadząc do utraty danych.

#### Przykład klasyczny:
```sql
-- Transakcja T1
BEGIN;
    saldo := SELECT saldo FROM konta WHERE id = 1;  -- 1000
    saldo := saldo - 100;  -- 900
    
-- Transakcja T2 (równolegle)
BEGIN;
    saldo := SELECT saldo FROM konta WHERE id = 1;  -- 1000 (stara wartość!)
    saldo := saldo + 200;  -- 1200

-- T1 kończy pierwsza
    UPDATE konta SET saldo = 900 WHERE id = 1;
COMMIT;

-- T2 kończy druga  
    UPDATE konta SET saldo = 1200 WHERE id = 1;  -- Nadpisuje T1!
COMMIT;

-- Wynik: saldo = 1200, ale powinno być 1100 (1000 - 100 + 200)
-- Utracona aktualizacja T1!
```

#### Lost Update w aplikacjach web:
```php
// User 1 edytuje profil
$user = SELECT * FROM users WHERE id = 123;  // version = 5
// User modyfikuje dane...
UPDATE users SET name = 'Jan', version = 6 WHERE id = 123 AND version = 5;

// User 2 edytuje profil (równolegle)  
$user = SELECT * FROM users WHERE id = 123;  // version = 5 (stara!)
// User modyfikuje inne dane...
UPDATE users SET email = 'new@email.com', version = 6 WHERE id = 123 AND version = 5;

// Jedna z aktualizacji zostanie utracona!
```

### 5. 🔄 **Write Skew**

#### Definicja:
**Dwie transakcje** odczytują te same dane i na tej podstawie **zapisują różne obiekty**, naruszając ograniczenia biznesowe.

#### Przykład - system dyżurów:
```sql
-- Warunek biznesowy: Zawsze muszą być co najmniej 2 lekarze na dyżurze

-- Transakcja T1 (Dr. Smith kończy dyżur)
BEGIN;
    liczba := SELECT COUNT(*) FROM dyzury WHERE aktywny = true;  -- 3 lekarzy
    IF liczba > 2 THEN
        UPDATE dyzury SET aktywny = false WHERE lekarz = 'Dr. Smith';
    END IF;
    
-- Transakcja T2 (Dr. Brown kończy dyżur, równolegle)  
BEGIN;
    liczba := SELECT COUNT(*) FROM dyzury WHERE aktywny = true;  -- 3 lekarzy
    IF liczba > 2 THEN
        UPDATE dyzury SET aktywny = false WHERE lekarz = 'Dr. Brown';
    END IF;

-- Obie transakcje COMMIT
-- Wynik: 1 lekarz na dyżurze (naruszenie zasady biznesowej!)
```

## Rozwiązania problemów współbieżności

### 1. **Poziomy izolacji transakcji**

#### READ UNCOMMITTED
```sql
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
-- Pozwala: Dirty Read, Non-Repeatable Read, Phantom Read, Lost Update
-- Najwyższa współbieżność, najniższa spójność
```

#### READ COMMITTED (domyślny w większości SZBD)
```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- Blokuje: Dirty Read
-- Pozwala: Non-Repeatable Read, Phantom Read
-- Dobry kompromis wydajność/spójność
```

#### REPEATABLE READ
```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- Blokuje: Dirty Read, Non-Repeatable Read
-- Pozwala: Phantom Read
-- Wyższa spójność, niższa współbieżność
```

#### SERIALIZABLE
```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- Blokuje: Wszystkie problemy współbieżności
-- Najwyższa spójność, najniższa współbieżność
```

### 2. **Blokady (Locking)**

#### Shared Locks (S)
```sql
-- Blokada współdzielona - wiele transakcji może czytać
SELECT * FROM konta WHERE id = 1 FOR SHARE;
-- Inne transakcje mogą czytać, ale nie mogą pisać
```

#### Exclusive Locks (X)
```sql
-- Blokada wyłączna - tylko jedna transakcja ma dostęp
SELECT * FROM konta WHERE id = 1 FOR UPDATE;
-- Inne transakcje nie mogą ani czytać, ani pisać
```

#### Przykład z blokadami:
```sql
-- Bezpieczny transfer z blokadami
BEGIN;
    -- Zablokuj oba konta w uporządkowanej kolejności (unikanie deadlock)
    SELECT saldo FROM konta WHERE id = 101 FOR UPDATE;  -- X lock
    SELECT saldo FROM konta WHERE id = 102 FOR UPDATE;  -- X lock
    
    -- Teraz bezpiecznie wykonaj transfer
    UPDATE konta SET saldo = saldo - 500 WHERE id = 101;
    UPDATE konta SET saldo = saldo + 500 WHERE id = 102;
COMMIT;  -- Zwolnij blokady
```

### 3. **Multiversion Concurrency Control (MVCC)**

#### Mechanizm:
- **Każda transakcja** widzi **snapshot danych** z momentu rozpoczęcia
- **Write operations** tworzą **nowe wersje** rekordów
- **Old versions** pozostają dostępne dla innych transakcji

#### Przykład MVCC:
```sql
-- PostgreSQL MVCC w akcji
-- T1: 
BEGIN;  -- timestamp: 100
    SELECT saldo FROM konta WHERE id = 1;  -- Widzi wersję z ts ≤ 100

-- T2:
BEGIN;  -- timestamp: 101  
    UPDATE konta SET saldo = 2000 WHERE id = 1;  -- Tworzy wersję z ts = 101
COMMIT;

-- T1 (kontynuacja):
    SELECT saldo FROM konta WHERE id = 1;  -- Wciąż widzi starą wersję (ts ≤ 100)
COMMIT;

-- T3:
BEGIN;  -- timestamp: 102
    SELECT saldo FROM konta WHERE id = 1;  -- Widzi nową wersję (ts = 101)
```

#### Zalety MVCC:
- **Readers nie blokują writers** i odwrotnie
- **Consistent snapshots** - brak non-repeatable reads
- **No deadlocks** z read-only queries

### 4. **Optimistic Concurrency Control**

#### Mechanizm:
1. **Czytaj bez blokad**
2. **Wykonuj zmiany lokalnie**
3. **Sprawdź konflikty** przed zapisem
4. **Commit lub Abort** w zależności od wyniku

#### Implementacja z version numbers:
```sql
-- Tabela z version column
CREATE TABLE produkty (
    id INT PRIMARY KEY,
    nazwa VARCHAR(100),
    cena DECIMAL(10,2),
    version INT DEFAULT 1
);

-- Optimistic update
UPDATE produkty 
SET nazwa = 'Nowa nazwa', 
    cena = 199.99,
    version = version + 1
WHERE id = 123 
  AND version = 5;  -- Sprawdź czy wersja się nie zmieniła

-- Jeśli @@ROWCOUNT = 0 → konflikt! Ktoś zmienił dane
```

#### Implementacja z timestamp:
```sql
CREATE TABLE dokumenty (
    id INT PRIMARY KEY,
    tresc TEXT,
    ostatnia_modyfikacja TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sprawdź timestamp przed zapisem
DECLARE last_modified TIMESTAMP;
SELECT ostatnia_modyfikacja INTO last_modified 
FROM dokumenty WHERE id = 456;

-- Jeśli last_modified ≠ expected_timestamp → konflikt!
IF last_modified = expected_timestamp THEN
    UPDATE dokumenty 
    SET tresc = 'Nowa treść',
        ostatnia_modyfikacja = CURRENT_TIMESTAMP
    WHERE id = 456;
ELSE
    RAISE EXCEPTION 'Dokument został zmieniony przez innego użytkownika';
END IF;
```

### 5. **Semantic Locks**

#### Mechanizm:
Blokady na **poziomie logiki biznesowej** zamiast na poziomie danych.

#### Przykład:
```sql
-- Tabela semantic locks
CREATE TABLE business_locks (
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    lock_holder VARCHAR(100),
    acquired_at TIMESTAMP,
    
    PRIMARY KEY (resource_type, resource_id)
);

-- Acquire semantic lock
INSERT INTO business_locks VALUES 
('ACCOUNT_TRANSFER', '101-102', 'transaction_xyz', CURRENT_TIMESTAMP);

-- Perform business operation
-- Transfer between accounts 101 and 102

-- Release semantic lock  
DELETE FROM business_locks 
WHERE resource_type = 'ACCOUNT_TRANSFER' 
  AND resource_id = '101-102' 
  AND lock_holder = 'transaction_xyz';
```

## Strategie zapobiegania problemom

### 1. **Ordered Locking** (przeciw deadlock)
```sql
-- Zawsze blokuj zasoby w tej samej kolejności
CREATE OR REPLACE FUNCTION transfer_funds(acc1 INT, acc2 INT, amount DECIMAL)
RETURNS VOID AS $$
DECLARE
    first_acc INT := LEAST(acc1, acc2);
    second_acc INT := GREATEST(acc1, acc2);
BEGIN
    -- Blokuj zawsze w porządku rosnącym ID
    PERFORM saldo FROM konta WHERE id = first_acc FOR UPDATE;
    PERFORM saldo FROM konta WHERE id = second_acc FOR UPDATE;
    
    -- Transfer logic
    UPDATE konta SET saldo = saldo - amount WHERE id = acc1;
    UPDATE konta SET saldo = saldo + amount WHERE id = acc2;
END;
$$ LANGUAGE plpgsql;
```

### 2. **Application-level Coordination**
```sql
-- Connection pooling z session affinity
-- Wszystkie operacje na koncie X zawsze przez to samo połączenie

-- Application locks
SELECT pg_advisory_lock(12345);  -- PostgreSQL advisory lock
-- Critical section
SELECT pg_advisory_unlock(12345);
```

### 3. **Batch Processing**
```sql
-- Zamiast real-time updates, batch processing
CREATE TABLE pending_updates (
    id SERIAL PRIMARY KEY,
    account_id INT,
    amount DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Batch job co minutę
DO $$
DECLARE
    update_record RECORD;
BEGIN
    FOR update_record IN 
        SELECT account_id, SUM(amount) as total_change
        FROM pending_updates 
        WHERE processed = false
        GROUP BY account_id
    LOOP
        UPDATE accounts 
        SET balance = balance + update_record.total_change
        WHERE id = update_record.account_id;
        
        UPDATE pending_updates 
        SET processed = true 
        WHERE account_id = update_record.account_id;
    END LOOP;
END;
$$;
```

## Monitoring współbieżności

### PostgreSQL:
```sql
-- Aktywne blokady
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- Statystyki deadlock'ów
SELECT deadlocks FROM pg_stat_database WHERE datname = current_database();
```

### MySQL:
```sql
-- InnoDB status
SHOW ENGINE INNODB STATUS;

-- Aktualne blokady
SELECT * FROM information_schema.INNODB_LOCKS;
SELECT * FROM information_schema.INNODB_LOCK_WAITS;

-- Performance schema  
SELECT * FROM performance_schema.metadata_locks;
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**
1. **Krótkie transakcje** - minimalizuj czas trzymania blokad
2. **Consistent ordering** - zawsze blokuj w tej samej kolejności
3. **Appropriate isolation level** - nie wyższy niż potrzebny
4. **Connection pooling** - unikaj connection thrashing
5. **Monitoring** - śledź blokady i deadlock'i

### ❌ **Złe praktyki:**
1. **User interaction** w transakcjach - nigdy nie czekaj na użytkownika
2. **Long-running transactions** - blokowanie zasobów na długo
3. **Nested transactions** bez savepoints
4. **Inconsistent locking order** - przepis na deadlock'i
5. **Ignoring isolation levels** - nie zastanawianie się nad konsekwencjami

## Przykłady praktyczne

### E-commerce inventory:
```sql
-- Problem: Overselling produktów
CREATE OR REPLACE FUNCTION reserve_product(
    p_product_id INT,
    p_quantity INT
)
RETURNS BOOLEAN AS $$
DECLARE
    available_qty INT;
BEGIN
    -- Pessimistic lock
    SELECT quantity INTO available_qty
    FROM inventory 
    WHERE product_id = p_product_id
    FOR UPDATE;
    
    IF available_qty >= p_quantity THEN
        UPDATE inventory 
        SET quantity = quantity - p_quantity,
            reserved = reserved + p_quantity
        WHERE product_id = p_product_id;
        
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

### Banking system:
```sql
-- Prevent overdrafts with proper isolation
CREATE OR REPLACE FUNCTION withdraw_funds(
    p_account_id INT,
    p_amount DECIMAL(15,2)
)
RETURNS TEXT AS $$
DECLARE
    current_balance DECIMAL(15,2);
    min_balance DECIMAL(15,2) := 0;
BEGIN
    -- Serializable isolation for critical operation
    SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
    
    SELECT balance INTO current_balance
    FROM accounts 
    WHERE id = p_account_id
    FOR UPDATE;
    
    IF current_balance >= (p_amount + min_balance) THEN
        UPDATE accounts 
        SET balance = balance - p_amount
        WHERE id = p_account_id;
        
        RETURN 'SUCCESS';
    ELSE
        RETURN 'INSUFFICIENT_FUNDS';
    END IF;
END;
$$ LANGUAGE plpgsql;
```

## Pułapki egzaminacyjne

### 1. **Rodzaje problemów**
- **Dirty Read**: Odczyt uncommitted danych
- **Non-Repeatable**: Różne wyniki tego samego SELECT
- **Phantom**: Nowe rekordy w zapytaniu
- **Lost Update**: Nadpisanie zmian

### 2. **Poziomy izolacji vs problemy**
- READ UNCOMMITTED: Wszystkie problemy możliwe
- READ COMMITTED: Brak dirty reads
- REPEATABLE READ: Brak dirty + non-repeatable
- SERIALIZABLE: Brak wszystkich problemów

### 3. **MVCC vs Locking**
- MVCC: Readers nie blokują writers
- Locking: Readers mogą blokować writers (zależnie od typu)

### 4. **Optimistic vs Pessimistic**
- Optimistic: Sprawdź konflikty przed commit
- Pessimistic: Zablokuj zasoby od razu