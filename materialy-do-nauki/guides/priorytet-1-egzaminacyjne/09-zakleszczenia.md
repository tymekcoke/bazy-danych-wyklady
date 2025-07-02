# Zakleszczenia (Deadlocks)

## Definicja

**Zakleszczenie (deadlock)** to sytuacja, w której **dwa lub więcej procesów/transakcji wzajemnie się blokują**, czekając na zasoby zajęte przez siebie nawzajem, co prowadzi do **nieskończonego oczekiwania**.

### Kluczowe cechy:
- **Wzajemne blokowanie** - każdy proces czeka na inny
- **Cykliczna zależność** - A czeka na B, B czeka na A
- **Niemożność postępu** - żaden proces nie może kontynuować
- **Automatyczne wykrywanie** - SZBD musi interweniować

## Przykład klasyczny

### Scenariusz zakleszania:
```
Transakcja T1:                 Transakcja T2:
1. LOCK(A)                     
                               2. LOCK(B)
3. Czeka na LOCK(B) ←←←←←←←←←← 4. Czeka na LOCK(A)

Wynik: T1 czeka na T2, T2 czeka na T1 = DEADLOCK!
```

### Przykład z transferem pieniędzy:
```sql
-- Transakcja T1: Transfer z konta A na konto B
BEGIN;
    UPDATE konta SET saldo = saldo - 100 WHERE id = 'A';  -- LOCK(A)
    -- WAIT... inne operacje
    UPDATE konta SET saldo = saldo + 100 WHERE id = 'B';  -- Czeka na LOCK(B)
COMMIT;

-- Transakcja T2: Transfer z konta B na konto A (równocześnie)
BEGIN;
    UPDATE konta SET saldo = saldo - 50 WHERE id = 'B';   -- LOCK(B)  
    -- WAIT... inne operacje
    UPDATE konta SET saldo = saldo + 50 WHERE id = 'A';   -- Czeka na LOCK(A)
COMMIT;

-- Rezultat: DEADLOCK!
```

## Warunki Coffmana (4 warunki deadlock'a)

### Wszystkie 4 muszą być spełnione równocześnie:

#### 1. 🔒 **Mutual Exclusion (wzajemne wykluczanie)**
- Zasoby nie mogą być dzielone
- Jeden proces = jeden zasób w danym momencie

#### 2. 🤏 **Hold and Wait (trzymaj i czekaj)**
- Proces trzyma przynajmniej jeden zasób
- I równocześnie czeka na inne zasoby

#### 3. 🚫 **No Preemption (brak wywłaszczania)**
- Zasobów nie można odebrać siłą
- Proces musi je zwolnić dobrowolnie

#### 4. 🔄 **Circular Wait (cykliczne oczekiwanie)**
- Istnieje cykl procesów czekających na siebie
- P1 → P2 → P3 → ... → P1

## Wykrywanie zakleszczeń

### Graf oczekiwania (Wait-for Graph)
```
Węzły = Transakcje
Krawędzie = "Czeka na"

Deadlock = Cykl w grafie

Przykład:
T1 → T2 → T3 → T1  (cykl = deadlock!)
```

### Algorytm wykrywania:
1. **Buduj graf oczekiwania** w czasie rzeczywistym
2. **Sprawdzaj cykle** okresowo lub po każdej blokadzie
3. **Wykryj deadlock** gdy znajdziesz cykl
4. **Wybierz ofiarę** - transakcję do wycofania

## Rozwiązania zakleszczeń

### 1. 🕵️ **Wykrywanie i rozwiązywanie (Detection & Recovery)**

#### Mechanizm:
- **Pozwól na deadlock** - niech się zdarzy
- **Wykryj automatycznie** - graf oczekiwania, cykle
- **Wybierz ofiarę** - najmłodsza/najtańsza transakcja
- **Wycofaj wybraną transakcję** - ROLLBACK

#### Implementacja w PostgreSQL:
```sql
-- PostgreSQL automatycznie wykrywa deadlocki
-- Timeout: deadlock_timeout (domyślnie 1s)
-- Wybiera "najłatwiejszą" transakcję do wycofania

-- Przykład błędu:
ERROR: deadlock detected
DETAIL: Process 12345 waits for ShareLock on transaction 67890;
blocked by process 54321.
HINT: See server log for query details.
```

### 2. 🚫 **Zapobieganie (Prevention)**

#### Eliminacja warunku Hold and Wait:
```sql
-- Metoda: Zażądaj wszystkich blokad na początku
BEGIN;
    LOCK TABLE konta IN EXCLUSIVE MODE;  -- Wszystkie blokady od razu
    UPDATE konta SET saldo = saldo - 100 WHERE id = 'A';
    UPDATE konta SET saldo = saldo + 100 WHERE id = 'B';
COMMIT;
```

#### Eliminacja warunku Circular Wait:
```sql
-- Metoda: Uporządkowanie zasobów (zawsze blokuj w tej samej kolejności)
BEGIN;
    -- Zawsze blokuj konta w porządku alfabetycznym
    UPDATE konta SET saldo = saldo - 100 WHERE id = 'A';  -- Najpierw A
    UPDATE konta SET saldo = saldo + 100 WHERE id = 'B';  -- Potem B
COMMIT;

-- Wszystkie transakcje muszą używać tej samej kolejności!
```

### 3. 🔮 **Unikanie (Avoidance)**

#### Banker's Algorithm:
- **Sprawdź czy operacja jest bezpieczna** przed wykonaniem
- **Symuluj przydział zasobów** - czy system pozostanie w stanie bezpiecznym?
- **Odłóż operację** jeśli może prowadzić do deadlock'a

#### Timestamp-based schemes:

##### Wait-Die:
```
Jeśli T1 (starszy) czeka na T2 (młodszy):
    T1 czeka (wait)
Jeśli T1 (młodszy) czeka na T2 (starszy):  
    T1 umiera (die) - ROLLBACK
```

##### Wound-Wait:
```
Jeśli T1 (starszy) czeka na T2 (młodszy):
    T2 umiera (wound) - T1 "rani" T2  
Jeśli T1 (młodszy) czeka na T2 (starszy):
    T1 czeka (wait)
```

## Strategie minimalizacji deadlock'ów

### 1. **Uporządkowanie dostępu do zasobów**
```sql
-- ✅ DOBRZE: Zawsze w tej samej kolejności
UPDATE tabela1 WHERE id = 1;  -- Najpierw tabela1
UPDATE tabela2 WHERE id = 1;  -- Potem tabela2

-- ❌ ŹLE: Różne kolejności w różnych transakcjach  
-- T1: tabela1 → tabela2
-- T2: tabela2 → tabela1  (potencjalny deadlock!)
```

### 2. **Krótkie transakcje**
```sql
-- ✅ DOBRZE: Krótka transakcja
BEGIN;
    UPDATE konta SET saldo = saldo - 100 WHERE id = 1;
    UPDATE konta SET saldo = saldo + 100 WHERE id = 2;
COMMIT;

-- ❌ ŹLE: Długa transakcja z pauzami
BEGIN;
    UPDATE konta SET saldo = saldo - 100 WHERE id = 1;
    -- Długie obliczenia, czekanie na user input...
    UPDATE konta SET saldo = saldo + 100 WHERE id = 2;
COMMIT;
```

### 3. **Odpowiedni poziom izolacji**
```sql
-- Czasem niższy poziom izolacji = mniej blokad = mniej deadlock'ów
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;  -- Zamiast SERIALIZABLE
```

### 4. **Indeksy i optymalizacja**
```sql
-- Dobré indeksy = szybsze operacje = krótsze blokady
CREATE INDEX idx_konta_id ON konta(id);

-- Sprawdź plan zapytania
EXPLAIN ANALYZE SELECT * FROM konta WHERE id = 1;
```

## Timeouty i recovery

### Lock timeout:
```sql
-- PostgreSQL: statement_timeout
SET statement_timeout = '30s';

-- MySQL: innodb_lock_wait_timeout  
SET innodb_lock_wait_timeout = 10;

-- SQL Server: LOCK_TIMEOUT
SET LOCK_TIMEOUT 10000;  -- 10 sekund
```

### Retry logic w aplikacji:
```python
def transfer_money(from_account, to_account, amount):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with transaction():
                # Transfer logic
                break
        except DeadlockDetected:
            if attempt == max_retries - 1:
                raise
            time.sleep(random.uniform(0.1, 0.5))  # Random backoff
```

## Monitoring deadlock'ów

### PostgreSQL:
```sql
-- Włącz logowanie deadlock'ów
SET log_lock_waits = on;
SET deadlock_timeout = '1s';

-- Sprawdź aktywne blokady
SELECT * FROM pg_locks WHERE NOT granted;

-- Historia deadlock'ów w logach
tail -f /var/log/postgresql/postgresql.log | grep deadlock
```

### Zapytanie o blokady:
```sql
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
```

## Przykłady praktyczne

### Przykład 1: E-commerce (deadlock w zamówieniach)
```sql
-- Problematyczne: różne kolejności aktualizacji
-- T1: aktualizuj produkt → aktualizuj magazyn
-- T2: aktualizuj magazyn → aktualizuj produkt

-- Rozwiązanie: uporządkowana kolejność
BEGIN;
    -- Zawsze najpierw produkty (mniejsze ID), potem magazyn (większe ID)
    UPDATE produkty SET ilosc_sprzedana = ilosc_sprzedana + 1 WHERE id = @product_id;
    UPDATE magazyn SET ilosc_dostepna = ilosc_dostepna - 1 WHERE id = @warehouse_id;
COMMIT;
```

### Przykład 2: System bankowy
```sql
-- Unikanie deadlock'ów w transferach
CREATE OR REPLACE FUNCTION transfer_money(
    from_account_id INT,
    to_account_id INT, 
    amount DECIMAL
) RETURNS VOID AS $$
DECLARE
    first_id INT := LEAST(from_account_id, to_account_id);
    second_id INT := GREATEST(from_account_id, to_account_id);
BEGIN
    -- Zawsze blokuj konta w porządku rosnącym ID
    PERFORM * FROM konta WHERE id = first_id FOR UPDATE;
    PERFORM * FROM konta WHERE id = second_id FOR UPDATE;
    
    -- Teraz bezpiecznie wykonuj transfer
    UPDATE konta SET saldo = saldo - amount WHERE id = from_account_id;
    UPDATE konta SET saldo = saldo + amount WHERE id = to_account_id;
END;
$$ LANGUAGE plpgsql;
```

## Pułapki egzaminacyjne

### 1. **4 warunki Coffmana**
- Wszystkie 4 muszą być spełnione równocześnie
- Eliminacja któregokolwiek = brak deadlock'a

### 2. **Graf oczekiwania**  
- Cykl w grafie = deadlock
- Brak cyklu = brak deadlock'a

### 3. **Wait-Die vs Wound-Wait**
- Wait-Die: młodsi umierają
- Wound-Wait: starsi ranią młodszych

### 4. **Rozwiązania**
- Wykrywanie = pozwól i napraw
- Zapobieganie = eliminuj warunki
- Unikanie = sprawdzaj przed wykonaniem