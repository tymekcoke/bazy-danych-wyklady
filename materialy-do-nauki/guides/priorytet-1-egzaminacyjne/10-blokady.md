# Blokady - rodzaje, kolizje i zastosowania

## Definicja

**Blokada (lock)** to mechanizm kontroli dostępu do zasobów w bazie danych, który **zapewnia integralność danych** podczas współbieżnego wykonywania transakcji.

### Cel blokad:
- **Zapewnić spójność** danych
- **Kontrolować dostęp** do zasobów
- **Zapobiegać konfliktom** między transakcjami
- **Implementować poziomy izolacji**

## Rodzaje blokad

### 1. 🔒 **Blokady podstawowe**

#### **Shared Lock (S) - Blokada współdzielona**
- **Pozwala na odczyt** przez wiele transakcji
- **Blokuje zapis** - żadna transakcja nie może modyfikować
- **Kompatybilna** z innymi blokadami S
- **Niekompatybilna** z blokadami X

```sql
-- Przykład blokady shared
SELECT * FROM konta WHERE id = 1 FOR SHARE;
-- lub starszy syntax:
SELECT * FROM konta WHERE id = 1 LOCK IN SHARE MODE;
```

#### **Exclusive Lock (X) - Blokada wyłączna**
- **Pozwala tylko jednej transakcji** na dostęp
- **Blokuje wszystkie inne** transakcje (odczyt i zapis)
- **Niekompatybilna** z wszystkimi innymi blokadami
- **Używana przy modyfikacji** danych

```sql
-- Przykład blokady exclusive
SELECT * FROM konta WHERE id = 1 FOR UPDATE;

-- Automatycznie przy UPDATE/DELETE
UPDATE konta SET saldo = saldo - 100 WHERE id = 1;  -- X lock
```

### 2. 📊 **Granularność blokad**

#### **Blokada wiersza (Row-level)**
- **Najdrobniejsza granularność**
- Blokuje pojedynczy rekord
- **Maksymalna współbieżność**
- Używana domyślnie w PostgreSQL, MySQL InnoDB

```sql
-- Blokuje tylko jeden wiersz
UPDATE pracownicy SET pensja = 5000 WHERE id = 123;
```

#### **Blokada strony (Page-level)**
- Blokuje **stronę danych** (zwykle 4KB-8KB)
- **Kompromis** między wydajnością a współbieżnością
- Używana w starszych wersjach SQL Server

#### **Blokada tabeli (Table-level)**
- Blokuje **całą tabelę**
- **Najmniejsza współbieżność**
- **Największa wydajność** dla operacji masowych
- Używana w MySQL MyISAM

```sql
-- Explicit table lock
LOCK TABLE pracownicy IN EXCLUSIVE MODE;
UPDATE pracownicy SET pensja = pensja * 1.1;  -- Podwyżka dla wszystkich
UNLOCK TABLES;
```

#### **Blokada kolumny (Column-level)**
- **Teoretycznie możliwa** - bardzo rzadko implementowana
- **Zbyt duży overhead** w praktyce

### 3. 🎯 **Blokady specjalne**

#### **Intent Locks (Blokady intencji)**
- **IS (Intent Shared)** - zamiar założenia S na niższym poziomie
- **IX (Intent Exclusive)** - zamiar założenia X na niższym poziomie
- **SIX (Shared Intent Exclusive)** - S na tym poziomie + IX na niższym

```
Hierarchia:
Database
  ↓ Intent locks
Table  
  ↓ Intent locks
Page
  ↓ Actual locks
Row
```

#### **Schema Locks (Blokady schematu)**
- **Sch-S (Schema Stability)** - zapobiega zmianom struktury
- **Sch-M (Schema Modification)** - wyłączna zmiana struktury

```sql
-- Schema modification lock
ALTER TABLE pracownicy ADD COLUMN telefon VARCHAR(15);  -- Sch-M
```

#### **Bulk Update Locks (BU)**
- Używane podczas masowych operacji
- **Kompatybilne z S i BU**
- **Niekompatybilne z X i IX**

## Macierz kompatybilności blokad

|     | S | X | IS | IX | SIX |
|-----|---|---|----|----|-----|
| **S**   | ✅ | ❌ | ✅  | ❌  | ❌   |
| **X**   | ❌ | ❌ | ❌  | ❌  | ❌   |
| **IS**  | ✅ | ❌ | ✅  | ✅  | ✅   |
| **IX**  | ❌ | ❌ | ✅  | ✅  | ❌   |
| **SIX** | ❌ | ❌ | ✅  | ❌  | ❌   |

### Interpretacja:
- ✅ **Kompatybilne** - mogą współistnieć
- ❌ **Niekompatybilne** - jedna transakcja musi czekać

## Kolizje blokad

### 1. **Read-Write Conflict**
```sql
-- T1: Czyta dane
SELECT saldo FROM konta WHERE id = 1;  -- S lock

-- T2: Próbuje modyfikować (musi czekać)
UPDATE konta SET saldo = 2000 WHERE id = 1;  -- Czeka na X lock
```

### 2. **Write-Write Conflict**
```sql
-- T1: Modyfikuje dane  
UPDATE konta SET saldo = saldo - 100 WHERE id = 1;  -- X lock

-- T2: Próbuje też modyfikować (musi czekać)
UPDATE konta SET saldo = saldo + 50 WHERE id = 1;   -- Czeka na X lock
```

### 3. **Write-Read Conflict**
```sql
-- T1: Modyfikuje dane
UPDATE konta SET saldo = saldo - 100 WHERE id = 1;  -- X lock

-- T2: Próbuje czytać (musi czekać w SERIALIZABLE)
SELECT saldo FROM konta WHERE id = 1;  -- Czeka na S lock
```

## Strategie blokowania

### 1. **Pesymistyczne blokowanie**
- **Blokuj od razu** przy pierwszym dostępie
- **Trzymaj blokady** do końca transakcji
- **Zapobiega konfliktom** ale ogranicza współbieżność

```sql
-- Pesymistyczne - blokuj od razu
BEGIN;
    SELECT saldo FROM konta WHERE id = 1 FOR UPDATE;  -- X lock natychmiast
    -- Długie obliczenia...
    UPDATE konta SET saldo = nowa_wartosc WHERE id = 1;
COMMIT;
```

### 2. **Optymistyczne blokowanie**
- **Nie blokuj** podczas odczytu
- **Sprawdź konflikty** przed zapisem
- **Wycofaj transakcję** jeśli dane się zmieniły

```sql
-- Optymistyczne - sprawdź wersję
BEGIN;
    SELECT saldo, version FROM konta WHERE id = 1;  -- Bez blokady
    -- Obliczenia...
    UPDATE konta 
    SET saldo = nowa_wartosc, version = version + 1 
    WHERE id = 1 AND version = stara_wersja;  -- Sprawdź wersję
    
    IF @@ROWCOUNT = 0 THEN
        ROLLBACK;  -- Konflikt - ktoś zmienił dane
    END IF;
COMMIT;
```

## Eskalacja blokad

### Mechanizm eskalacji:
```
Row locks → Page locks → Table locks
```

### Kiedy następuje eskalacja:
- **Zbyt wiele blokad wiersza** (np. > 5000)
- **Brak pamięci** na struktury blokad
- **Operacje masowe** (BULK INSERT)

### Przykład:
```sql
-- Zaczyna od row locks
UPDATE pracownicy SET pensja = pensja * 1.1 WHERE dzial = 'IT';

-- Jeśli > 5000 wierszy → eskalacja do table lock
-- Cała tabela pracownicy zablokowana!
```

### Kontrola eskalacji:
```sql
-- SQL Server - wyłącz eskalację
ALTER TABLE pracownicy SET (LOCK_ESCALATION = DISABLE);

-- PostgreSQL - kontroluj batch size
UPDATE pracownicy SET pensja = pensja * 1.1 
WHERE id IN (SELECT id FROM pracownicy WHERE dzial = 'IT' LIMIT 1000);
```

## Rodzaje blokad według zastosowania

### 1. **Key Locks (Blokady kluczy)**
- **Key lock** - blokada konkretnego klucza
- **Key-range lock** - blokada zakresu kluczy
- **Gap lock** - blokada "dziur" między kluczami

```sql
-- InnoDB gap locks
SELECT * FROM produkty WHERE cena BETWEEN 100 AND 200 FOR UPDATE;
-- Blokuje nie tylko istniejące produkty, ale i "gap" dla nowych
```

### 2. **Phantom Prevention Locks**
- **Zapobiegają phantom reads**
- **Blokują predykaty** zamiast konkretnych rekordów
- **Używane w SERIALIZABLE**

```sql
-- Blokuje predykat "wiek > 30"
SELECT * FROM pracownicy WHERE wiek > 30;  -- W SERIALIZABLE
-- Nikt nie może dodać pracownika z wiek > 30
```

## Explicit locking w SQL

### PostgreSQL:
```sql
-- Row-level locks
SELECT * FROM table FOR UPDATE;           -- Exclusive
SELECT * FROM table FOR NO KEY UPDATE;    -- Exclusive bez foreign keys
SELECT * FROM table FOR SHARE;            -- Shared  
SELECT * FROM table FOR KEY SHARE;        -- Shared tylko klucze

-- Table-level locks
LOCK TABLE table IN ACCESS SHARE MODE;         -- Najsłabsza
LOCK TABLE table IN ROW SHARE MODE;
LOCK TABLE table IN ROW EXCLUSIVE MODE;
LOCK TABLE table IN SHARE UPDATE EXCLUSIVE MODE;
LOCK TABLE table IN SHARE MODE;
LOCK TABLE table IN SHARE ROW EXCLUSIVE MODE;
LOCK TABLE table IN EXCLUSIVE MODE;
LOCK TABLE table IN ACCESS EXCLUSIVE MODE;     -- Najsilniejsza
```

### MySQL:
```sql
-- Row locks
SELECT * FROM table WHERE id = 1 FOR UPDATE;        -- Exclusive
SELECT * FROM table WHERE id = 1 LOCK IN SHARE MODE; -- Shared

-- Table locks  
LOCK TABLES table READ;    -- Shared table lock
LOCK TABLES table WRITE;   -- Exclusive table lock
UNLOCK TABLES;
```

## Monitoring blokad

### PostgreSQL:
```sql
-- Aktualne blokady
SELECT 
    locktype, 
    database, 
    relation::regclass, 
    page, 
    tuple, 
    pid, 
    mode, 
    granted 
FROM pg_locks;

-- Oczekujące blokady
SELECT * FROM pg_locks WHERE NOT granted;

-- Blokujące vs blokowane
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocking_locks.pid AS blocking_pid,
    blocked_activity.query AS blocked_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_locks blocking_locks ON (
    blocking_locks.locktype = blocked_locks.locktype 
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
)
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
WHERE NOT blocked_locks.granted AND blocking_locks.granted;
```

### MySQL:
```sql
-- Informacje o blokadach
SHOW ENGINE INNODB STATUS;

-- Oczekujące transakcje
SELECT * FROM information_schema.INNODB_TRX;

-- Blokady
SELECT * FROM information_schema.INNODB_LOCKS;

-- Oczekiwania
SELECT * FROM information_schema.INNODB_LOCK_WAITS;
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**
1. **Krótkie transakcje** - minimalizuj czas trzymania blokad
2. **Uporządkowany dostęp** - zawsze w tej samej kolejności
3. **Odpowiednia granularność** - row-level gdy możliwe
4. **Indeksy** - blokuj tylko potrzebne rekordy
5. **Batch processing** - dziel duże operacje

### ❌ **Złe praktyki:**
1. **Długie transakcje** - długo trzymają blokady
2. **Manual table locks** - bez potrzeby
3. **Brak indeksów** - blokady całych tabel
4. **User interaction** w transakcjach - czekanie na użytkownika
5. **Ignorowanie deadlock'ów** - brak retry logic

## Przykłady praktyczne

### Przykład 1: Bezpieczny transfer
```sql
-- Uporządkowany dostęp zapobiega deadlock'om
CREATE OR REPLACE FUNCTION transfer_funds(
    from_id INT, 
    to_id INT, 
    amount DECIMAL
) 
RETURNS VOID AS $$
DECLARE
    first_id INT := LEAST(from_id, to_id);
    second_id INT := GREATEST(from_id, to_id);
BEGIN
    -- Blokuj konta w uporządkowanej kolejności
    PERFORM saldo FROM konta WHERE id = first_id FOR UPDATE;
    PERFORM saldo FROM konta WHERE id = second_id FOR UPDATE;
    
    -- Bezpieczny transfer
    UPDATE konta SET saldo = saldo - amount WHERE id = from_id;
    UPDATE konta SET saldo = saldo + amount WHERE id = to_id;
END;
$$ LANGUAGE plpgsql;
```

### Przykład 2: Obsługa inventory
```sql
-- Optymistyczne blokowanie z retry
DECLARE @retry_count INT = 3;

WHILE @retry_count > 0
BEGIN TRY
    BEGIN TRANSACTION;
    
    SELECT @current_stock = quantity, @version = version_stamp
    FROM inventory 
    WHERE product_id = @product_id;
    
    IF @current_stock >= @requested_qty
    BEGIN
        UPDATE inventory 
        SET quantity = quantity - @requested_qty,
            version_stamp = @version + 1
        WHERE product_id = @product_id 
        AND version_stamp = @version;
        
        IF @@ROWCOUNT = 0
            THROW 50001, 'Optimistic lock failed', 1;
    END
    
    COMMIT TRANSACTION;
    BREAK;  -- Success
END TRY
BEGIN CATCH
    ROLLBACK TRANSACTION;
    SET @retry_count = @retry_count - 1;
    WAITFOR DELAY '00:00:01';  -- Wait before retry
END CATCH
```

## Pułapki egzaminacyjne

### 1. **Macierz kompatybilności**
- S + S = ✅ (kompatybilne)
- S + X = ❌ (niekompatybilne)  
- X + cokolwiek = ❌ (wyłączny!)

### 2. **Granularność vs Współbieżność**
- Row locks = wysoka współbieżność, duży overhead
- Table locks = niska współbieżność, mały overhead

### 3. **Eskalacja blokad**
- Automatyczny mechanizm oszczędzania pamięci
- Może drastycznie zmniejszyć współbieżność

### 4. **Typy kolizji**
- Read-Write, Write-Write, Write-Read
- Różne strategie w różnych poziomach izolacji