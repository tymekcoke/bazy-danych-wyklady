# Znaczniki czasu dla transakcji

## Definicja

**Znaczniki czasu (timestamps)** to mechanizm kontroli współbieżności, który **przypisuje każdej transakcji unikalny znacznik czasowy** i używa go do **określania kolejności wykonywania** operacji oraz **rozwiązywania konfliktów**.

### Główne cechy:
- **Unikalność** - każda transakcja ma unikalny timestamp
- **Porządek** - timestamps określają kolejność logiczną
- **Brak blokad** - alternatywa dla protokołów blokowania
- **Determinizm** - przewidywalne rozwiązywanie konfliktów

## Rodzaje znaczników czasu

### 1. **System Clock Timestamps**
```sql
-- Przykład przypisania timestamp przy rozpoczęciu transakcji
BEGIN TRANSACTION;
-- timestamp = CURRENT_TIMESTAMP = '2024-03-15 14:30:25.123'

SELECT id, nazwa, ostatnia_modyfikacja 
FROM produkty 
WHERE id = 100;
-- Operacja ma timestamp transakcji
```

### 2. **Logical Timestamps (Lamport Timestamps)**
```
-- Sekwencyjny licznik globalny
T1: timestamp = 1001
T2: timestamp = 1002  
T3: timestamp = 1003
T4: timestamp = 1004
```

### 3. **Vector Clocks**
```
-- W systemach rozproszonych
Node A: [3, 1, 2]  -- [A_clock, B_clock, C_clock]
Node B: [2, 4, 1]
Node C: [1, 2, 5]
```

## Algorytmy oparte na timestamp

### 1. **Basic Timestamp Ordering (TO)**

#### Zasady:
- **TS(Ti)** - timestamp transakcji Ti
- **R-timestamp(X)** - timestamp ostatniej transakcji, która odczytała X
- **W-timestamp(X)** - timestamp ostatniej transakcji, która zapisała X

#### Reguły dla READ operacji:
```
Jeśli TS(Ti) < W-timestamp(X):
    → ROLLBACK Ti (próba odczytu "starej" wersji)
Inaczej:
    → Wykonaj READ
    → R-timestamp(X) = max(R-timestamp(X), TS(Ti))
```

#### Reguły dla WRITE operacji:
```
Jeśli TS(Ti) < R-timestamp(X):
    → ROLLBACK Ti (próba nadpisania "przeczytanych" danych)
Jeśli TS(Ti) < W-timestamp(X):
    → Ignore WRITE (Thomas Write Rule)
Inaczej:
    → Wykonaj WRITE
    → W-timestamp(X) = TS(Ti)
```

### Przykład Basic TO:
```
T1 (TS=10): R(A), W(A)
T2 (TS=20): R(A), W(B)
T3 (TS=15): W(A), R(B)

Wykonanie:
1. T1: R(A) → OK, R-ts(A) = 10
2. T1: W(A) → OK, W-ts(A) = 10  
3. T2: R(A) → OK (TS(T2)=20 > W-ts(A)=10), R-ts(A) = 20
4. T3: W(A) → ROLLBACK! (TS(T3)=15 < R-ts(A)=20)
```

### 2. **Conservative Timestamp Ordering**

#### Mechanizm:
- **Nie wykonuj operacji** dopóki nie masz pewności o kolejności
- **Czekaj** na potwierdzenie timestampów innych transakcji
- **Gwarantuje brak rollback'ów** ale może być wolniejszy

```sql
-- Pseudokod
PROCEDURE conservative_read(Ti, X):
    WAIT UNTIL (dla wszystkich aktywnych Tj: TS(Tj) < TS(Ti) lub Tj zakończone)
    IF TS(Ti) >= W-timestamp(X) THEN
        Wykonaj READ
        R-timestamp(X) = max(R-timestamp(X), TS(Ti))
    ELSE
        ROLLBACK Ti
```

### 3. **Multiversion Timestamp Ordering (MVTO)**

#### Koncepcja:
- **Przechowuj wiele wersji** każdego obiektu danych
- **Każda wersja ma timestamp** utworzenia
- **Transakcje czytają odpowiednią wersję** bez konfliktów

```
Obiekt A:
- A₁ (W-ts=5, R-ts=15)   ← wersja utworzona przez T₅
- A₂ (W-ts=12, R-ts=18)  ← wersja utworzona przez T₁₂  
- A₃ (W-ts=20, R-ts=20)  ← wersja utworzona przez T₂₀

T₁₆ chce czytać A:
→ Wybierz najnowszą wersję gdzie W-ts ≤ 16
→ Czyta A₂ (W-ts=12)
```

#### Algorytm MVTO READ:
```
PROCEDURE mvto_read(Ti, X):
    Znajdź wersję Xj gdzie:
        W-timestamp(Xj) ≤ TS(Ti) < W-timestamp(Xj+1)
    
    R-timestamp(Xj) = max(R-timestamp(Xj), TS(Ti))
    RETURN value(Xj)
```

#### Algorytm MVTO WRITE:
```
PROCEDURE mvto_write(Ti, X):
    Znajdź wersję Xj gdzie: W-timestamp(Xj) ≤ TS(Ti)
    
    IF R-timestamp(Xj) > TS(Ti) THEN
        ROLLBACK Ti  -- ktoś już przeczytał nowszą wersję
    ELSE
        Utwórz nową wersję Xi
        W-timestamp(Xi) = TS(Ti)
        R-timestamp(Xi) = TS(Ti)
```

## Implementacja praktyczna

### 1. **Timestamp w PostgreSQL**
```sql
-- Tabela z timestampami wersji
CREATE TABLE produkty (
    id INT PRIMARY KEY,
    nazwa VARCHAR(100),
    cena DECIMAL(10,2),
    wersja_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_transaction BIGINT DEFAULT txid_current()
);

-- Optimistic locking z timestamp
CREATE OR REPLACE FUNCTION aktualizuj_produkt_safe(
    p_id INT,
    p_nazwa VARCHAR(100),
    p_cena DECIMAL(10,2),
    p_expected_timestamp TIMESTAMP
)
RETURNS BOOLEAN AS $$
DECLARE
    current_ts TIMESTAMP;
BEGIN
    -- Sprawdź aktualny timestamp
    SELECT wersja_timestamp INTO current_ts
    FROM produkty
    WHERE id = p_id;
    
    -- Sprawdź czy dane się nie zmieniły
    IF current_ts != p_expected_timestamp THEN
        RAISE NOTICE 'Konflikt wersji! Oczekiwany: %, Aktualny: %', 
                     p_expected_timestamp, current_ts;
        RETURN FALSE;
    END IF;
    
    -- Aktualizuj z nowym timestamp
    UPDATE produkty 
    SET nazwa = p_nazwa,
        cena = p_cena,
        wersja_timestamp = CURRENT_TIMESTAMP,
        created_by_transaction = txid_current()
    WHERE id = p_id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
```

### 2. **Multiversion control**
```sql
-- Tabela z wersjami historycznymi
CREATE TABLE produkty_historia (
    id INT,
    nazwa VARCHAR(100),
    cena DECIMAL(10,2),
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    transaction_id BIGINT,
    
    PRIMARY KEY (id, valid_from)
);

-- Trigger dla automatycznego tworzenia wersji
CREATE OR REPLACE FUNCTION create_product_version()
RETURNS TRIGGER AS $$
BEGIN
    -- Zakończ poprzednią wersję
    UPDATE produkty_historia 
    SET valid_to = CURRENT_TIMESTAMP
    WHERE id = OLD.id AND valid_to IS NULL;
    
    -- Utwórz nową wersję
    INSERT INTO produkty_historia (id, nazwa, cena, valid_from, transaction_id)
    VALUES (NEW.id, NEW.nazwa, NEW.cena, CURRENT_TIMESTAMP, txid_current());
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER produkty_versioning
    AFTER UPDATE ON produkty
    FOR EACH ROW
    EXECUTE FUNCTION create_product_version();
```

### 3. **Snapshot isolation simulation**
```sql
-- Funkcja do odczytu danych na określony moment
CREATE OR REPLACE FUNCTION produkty_snapshot(snapshot_time TIMESTAMP)
RETURNS TABLE(id INT, nazwa VARCHAR(100), cena DECIMAL(10,2)) AS $$
BEGIN
    RETURN QUERY
    SELECT h.id, h.nazwa, h.cena
    FROM produkty_historia h
    WHERE h.valid_from <= snapshot_time
      AND (h.valid_to IS NULL OR h.valid_to > snapshot_time);
END;
$$ LANGUAGE plpgsql;

-- Użycie
SELECT * FROM produkty_snapshot('2024-03-15 14:00:00');
```

## Protokoły Wait-Die i Wound-Wait

### 1. **Wait-Die Protocol**
```
Zasada: "Młodsze transakcje umierają, starsze czekają"

IF TS(Ti) < TS(Tj) THEN
    Ti czeka na Tj  -- starsza czeka na młodszą
ELSE
    Ti umiera       -- młodsza umiera
```

#### Przykład Wait-Die:
```
T1 (TS=10) chce blokadę na X, ale X jest zablokowany przez T2 (TS=20)
→ T1 jest starszy (10 < 20) → T1 CZEKA

T2 (TS=20) chce blokadę na Y, ale Y jest zablokowany przez T1 (TS=10)  
→ T2 jest młodszy (20 > 10) → T2 UMIERA (ROLLBACK)
```

### 2. **Wound-Wait Protocol**
```
Zasada: "Starsze transakcje ranią młodsze, młodsze czekają na starsze"

IF TS(Ti) < TS(Tj) THEN
    Ti rani Tj      -- starsza rani młodszą (Tj rollback)
ELSE  
    Ti czeka na Tj  -- młodsza czeka na starszą
```

#### Przykład Wound-Wait:
```
T1 (TS=10) chce blokadę na X, ale X jest zablokowany przez T2 (TS=20)
→ T1 jest starszy (10 < 20) → T1 RANI T2 (T2 rollback)

T2 (TS=20) chce blokadę na Y, ale Y jest zablokowany przez T1 (TS=10)
→ T2 jest młodszy (20 > 10) → T2 CZEKA
```

## Zalety i wady algorytmów timestamp

### ✅ **Zalety:**
1. **Brak deadlock'ów** - nie ma cyklicznych zależności
2. **Determinizm** - przewidywalne zachowanie
3. **Sprawiedliwość** - starsze transakcje mają priorytet
4. **Prostota** - łatwe do zrozumienia reguły
5. **Distributed friendly** - działają w systemach rozproszonych

### ❌ **Wady:**
1. **Rollback overhead** - częste wycofywanie transakcji
2. **Starvation możliwa** - młode transakcje mogą być często wycofywane
3. **Clock synchronization** - problem w systemach rozproszonych
4. **Storage overhead** - multiversion wymaga więcej miejsca
5. **Complex recovery** - odtwarzanie po awarii może być skomplikowane

## Porównanie z innymi metodami

### Timestamp vs 2PL (Two-Phase Locking):

| Aspekt | Timestamp Ordering | 2PL |
|--------|-------------------|-----|
| **Deadlock** | Niemożliwy | Możliwy |
| **Rollbacks** | Częste | Rzadkie |
| **Concurrency** | Wyższa | Niższa |
| **Overhead** | Storage (MVTO) | Locking |
| **Predictability** | Wysoka | Średnia |

### Przykład porównawczy:
```
Scenariusz: T1(TS=10): R(A), W(B)  T2(TS=20): R(B), W(A)

Timestamp Ordering:
1. T1: R(A) → OK
2. T2: R(B) → OK  
3. T1: W(B) → OK
4. T2: W(A) → OK
Wynik: Oba wykonane, serializable jako T1→T2

2PL:
1. T1: R(A) → Shared lock(A)
2. T2: R(B) → Shared lock(B)
3. T1: W(B) → Czeka na exclusive lock(B)
4. T2: W(A) → Czeka na exclusive lock(A)
Wynik: DEADLOCK!
```

## Zastosowania praktyczne

### 1. **Distributed databases**
```sql
-- Distributed timestamp w systemie replikacji
CREATE TABLE distributed_transactions (
    global_timestamp BIGINT,
    node_id INT,
    local_timestamp TIMESTAMP,
    transaction_id UUID,
    
    PRIMARY KEY (global_timestamp, node_id)
);

-- Synchronizacja czasów między węzłami
CREATE OR REPLACE FUNCTION sync_global_clock()
RETURNS BIGINT AS $$
DECLARE
    max_known_ts BIGINT;
    local_ts BIGINT;
BEGIN
    -- Pobierz maksymalny znany timestamp z sieci
    SELECT COALESCE(MAX(global_timestamp), 0) INTO max_known_ts
    FROM distributed_transactions;
    
    -- Wygeneruj nowy timestamp większy niż wszystkie znane
    local_ts := EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000000;
    
    RETURN GREATEST(max_known_ts + 1, local_ts);
END;
$$ LANGUAGE plpgsql;
```

### 2. **Version control systems**
```sql
-- System kontroli wersji dokumentów
CREATE TABLE dokumenty_wersje (
    id_dokumentu INT,
    numer_wersji INT,
    timestamp_utworzenia TIMESTAMP,
    timestamp_zatwierdzenia TIMESTAMP,
    autor_id INT,
    tresc TEXT,
    parent_version INT,
    
    PRIMARY KEY (id_dokumentu, numer_wersji)
);

-- Merge conflict resolution based on timestamps
CREATE OR REPLACE FUNCTION merge_dokumenty(
    doc_id INT,
    version_a INT,
    version_b INT
)
RETURNS INT AS $$  -- returns new version number
DECLARE
    ts_a TIMESTAMP;
    ts_b TIMESTAMP;
    new_version INT;
BEGIN
    -- Pobierz timestampy wersji
    SELECT timestamp_zatwierdzenia INTO ts_a 
    FROM dokumenty_wersje 
    WHERE id_dokumentu = doc_id AND numer_wersji = version_a;
    
    SELECT timestamp_zatwierdzenia INTO ts_b
    FROM dokumenty_wersje 
    WHERE id_dokumentu = doc_id AND numer_wersji = version_b;
    
    -- Nowsza wersja wygrywa
    IF ts_a > ts_b THEN
        new_version := version_a;
    ELSE
        new_version := version_b;
    END IF;
    
    RETURN new_version;
END;
$$ LANGUAGE plpgsql;
```

## Monitoring i debugging

### 1. **Timestamp conflicts tracking**
```sql
-- Tabela logowania konfliktów
CREATE TABLE timestamp_conflicts (
    conflict_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_id_1 BIGINT,
    transaction_id_2 BIGINT,
    timestamp_1 TIMESTAMP,
    timestamp_2 TIMESTAMP,
    resource_name VARCHAR(100),
    conflict_type VARCHAR(20), -- 'READ_WRITE', 'WRITE_WRITE'
    resolution VARCHAR(20)     -- 'T1_ROLLBACK', 'T2_ROLLBACK', 'WAIT'
);

-- Statystyki konfliktów
CREATE VIEW konflikt_stats AS
SELECT 
    DATE_TRUNC('hour', conflict_time) as godzina,
    conflict_type,
    COUNT(*) as liczba_konfliktow,
    COUNT(DISTINCT transaction_id_1) + COUNT(DISTINCT transaction_id_2) as transakcje_dotknięte
FROM timestamp_conflicts
GROUP BY DATE_TRUNC('hour', conflict_time), conflict_type
ORDER BY godzina DESC;
```

## Pułapki egzaminacyjne

### 1. **Reguły Basic TO**
- READ: sprawdź W-timestamp
- WRITE: sprawdź R-timestamp i W-timestamp
- Thomas Write Rule: ignoruj zapis jeśli jest "stary"

### 2. **Wait-Die vs Wound-Wait**
- **Wait-Die**: Młodsi umierają, starsi czekają
- **Wound-Wait**: Starsi ranią młodszych, młodsi czekają

### 3. **MVTO**
- Każda transakcja czyta "swoją" wersję danych
- Nowe wersje tworzone przy zapisie
- Garbage collection starych wersji

### 4. **Zalety/Wady**
- **Brak deadlock'ów** ale **więcej rollback'ów**
- **Sprawiedliwość** dla starszych transakcji
- **Synchronizacja zegarów** w systemach rozproszonych