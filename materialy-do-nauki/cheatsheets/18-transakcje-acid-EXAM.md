# ⚛️ TRANSAKCJE I WŁAŚCIWOŚCI ACID - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Transakcja to logiczna jednostka pracy składająca się z jednej lub więcej operacji bazodanowych, które muszą być wykonane atomowo. Właściwości ACID to:

1. **Atomicity (Atomowość)** - wszystko albo nic, transakcja jest niepodzielna
2. **Consistency (Spójność)** - transakcja przeprowadza bazę ze stanu spójnego do spójnego
3. **Isolation (Izolacja)** - współbieżne transakcje nie wpływają na siebie nawzajem
4. **Durability (Trwałość)** - zatwierdzone zmiany są permanentne, nawet po awarii

ACID zapewnia niezawodność systemu bazodanowego w środowisku współbieżnym."

## ✍️ CO NAPISAĆ NA KARTCE

```sql
WŁAŚCIWOŚCI ACID:

A - ATOMICITY (Atomowość):
• Transakcja = niepodzielna jednostka
• Wszystkie operacje albo wszystkie się udają, albo wszystkie cofnięte
• COMMIT - zatwierdź wszystko
• ROLLBACK - cofnij wszystko
• Mechanizm: Transaction Log, Undo/Redo Log

C - CONSISTENCY (Spójność):
• Zachowanie constraints i reguł biznesowych
• Przejście ze stanu spójnego do spójnego
• Sprawdzanie: CHECK constraints, Foreign Keys, Triggers
• Naruszenie spójności → automatyczny ROLLBACK

I - ISOLATION (Izolacja):
• Współbieżne transakcje nie zakłócają się nawzajem
• Poziomy izolacji: READ UNCOMMITTED, READ COMMITTED, 
  REPEATABLE READ, SERIALIZABLE
• Mechanizmy: Locking, MVCC, Timestamp Ordering

D - DURABILITY (Trwałość):
• Zatwierdzone zmiany przetrwają awarie systemu
• Write-Ahead Logging (WAL)
• Flush to disk przed COMMIT
• Recovery po awarii z logów

PRZYKŁAD TRANSAKCJI:
BEGIN;
  UPDATE konta SET saldo = saldo - 100 WHERE id = 1;
  UPDATE konta SET saldo = saldo + 100 WHERE id = 2;
  -- Jeśli błąd w którymkolwiek UPDATE → ROLLBACK całości
COMMIT; -- Atomowo zatwierdź obie operacje

STANY TRANSAKCJI:
ACTIVE → PARTIALLY COMMITTED → COMMITTED
       ↘ FAILED → ABORTED
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- DEMONSTRACJA WŁAŚCIWOŚCI ACID

-- Przygotowanie tabel testowych
CREATE TABLE konta (
    id_konta INT PRIMARY KEY,
    nazwa_wlasciciela VARCHAR(100),
    saldo DECIMAL(10,2) NOT NULL CHECK (saldo >= 0), -- constraint spójności
    data_utworzenia DATE DEFAULT CURRENT_DATE
);

CREATE TABLE historia_transakcji (
    id_transakcji SERIAL PRIMARY KEY,
    id_konta_zrodlowego INT,
    id_konta_docelowego INT,
    kwota DECIMAL(10,2),
    timestamp_operacji TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20)
);

INSERT INTO konta VALUES 
(1, 'Jan Kowalski', 1000.00),
(2, 'Anna Nowak', 500.00),
(3, 'Piotr Wiśniewski', 0.00);

-- 1. ATOMICITY - przykład sukcesu i niepowodzenia

-- SUKCES - wszystkie operacje się udają
BEGIN;
    -- Przelew 100 PLN z konta 1 na konto 2
    UPDATE konta SET saldo = saldo - 100 WHERE id_konta = 1;
    UPDATE konta SET saldo = saldo + 100 WHERE id_konta = 2;
    
    -- Log operacji
    INSERT INTO historia_transakcji (id_konta_zrodlowego, id_konta_docelowego, kwota, status)
    VALUES (1, 2, 100, 'SUCCESS');
    
COMMIT; -- Atomowo zatwierdź wszystkie 3 operacje

-- NIEPOWODZENIE - błąd powoduje cofnięcie wszystkiego
BEGIN;
    -- Próba przelewu większej kwoty niż saldo
    UPDATE konta SET saldo = saldo - 2000 WHERE id_konta = 1; -- Narusza CHECK constraint
    UPDATE konta SET saldo = saldo + 2000 WHERE id_konta = 2;
    
    INSERT INTO historia_transakcji (id_konta_zrodlowego, id_konta_docelowego, kwota, status)
    VALUES (1, 2, 2000, 'FAILED');
    
COMMIT; -- Nie dojdzie do wykonania - automatyczny ROLLBACK

-- Sprawdzenie - salda nie zmieniły się
SELECT * FROM konta;

-- 2. CONSISTENCY - sprawdzanie spójności

-- Funkcja sprawdzająca spójność systemu
CREATE OR REPLACE FUNCTION sprawdz_spojonosc_systemu()
RETURNS BOOLEAN AS $$
DECLARE
    ujemne_salda INT;
    orphaned_transakcje INT;
BEGIN
    -- Sprawdź czy nie ma ujemnych sald
    SELECT COUNT(*) INTO ujemne_salda
    FROM konta WHERE saldo < 0;
    
    -- Sprawdź czy wszystkie transakcje mają istniejące konta
    SELECT COUNT(*) INTO orphaned_transakcje
    FROM historia_transakcji ht
    LEFT JOIN konta k1 ON ht.id_konta_zrodlowego = k1.id_konta
    LEFT JOIN konta k2 ON ht.id_konta_docelowego = k2.id_konta
    WHERE k1.id_konta IS NULL OR k2.id_konta IS NULL;
    
    IF ujemne_salda > 0 THEN
        RAISE NOTICE 'NIESPÓJNOŚĆ: % kont z ujemnym saldem', ujemne_salda;
        RETURN FALSE;
    END IF;
    
    IF orphaned_transakcje > 0 THEN
        RAISE NOTICE 'NIESPÓJNOŚĆ: % transakcji bez istniejących kont', orphaned_transakcje;
        RETURN FALSE;
    END IF;
    
    RAISE NOTICE 'System jest spójny';
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Test spójności
SELECT sprawdz_spojonosc_systemu();

-- Transakcja z automatycznym sprawdzeniem spójności
CREATE OR REPLACE FUNCTION bezpieczny_przelew(
    p_id_zrodlowego INT,
    p_id_docelowego INT,
    p_kwota DECIMAL
) RETURNS BOOLEAN AS $$
DECLARE
    saldo_zrodlowe DECIMAL;
BEGIN
    -- Sprawdź saldo przed operacją
    SELECT saldo INTO saldo_zrodlowe FROM konta WHERE id_konta = p_id_zrodlowego;
    
    IF saldo_zrodlowe IS NULL THEN
        RAISE EXCEPTION 'Konto źródłowe % nie istnieje', p_id_zrodlowego;
    END IF;
    
    IF saldo_zrodlowe < p_kwota THEN
        RAISE EXCEPTION 'Niewystarczające środki: % < %', saldo_zrodlowe, p_kwota;
    END IF;
    
    -- Wykonaj przelew
    UPDATE konta SET saldo = saldo - p_kwota WHERE id_konta = p_id_zrodlowego;
    UPDATE konta SET saldo = saldo + p_kwota WHERE id_konta = p_id_docelowego;
    
    -- Sprawdź spójność po operacji
    IF NOT sprawdz_spojonosc_systemu() THEN
        RAISE EXCEPTION 'Operacja naruszyła spójność systemu';
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 3. ISOLATION - demonstracja poziomów izolacji

-- Sprawdzenie bieżącego poziomu izolacji
SHOW default_transaction_isolation;

-- Test READ COMMITTED (domyślny w PostgreSQL)
-- Terminal 1:
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT saldo FROM konta WHERE id_konta = 1; -- np. 900
-- ... pauza ...
SELECT saldo FROM konta WHERE id_konta = 1; -- może być inne (non-repeatable read)

-- Terminal 2 (równolegle):
BEGIN;
UPDATE konta SET saldo = saldo + 50 WHERE id_konta = 1;
COMMIT; -- zmienia saldo między read'ami w Terminal 1

-- Test REPEATABLE READ
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT saldo FROM konta WHERE id_konta = 1; -- np. 950
-- ... inne operacje ...
SELECT saldo FROM konta WHERE id_konta = 1; -- to samo 950 (repeatable)

-- 4. DURABILITY - symulacja odzyskiwania po awarii

-- Włączenie logowania WAL (domyślnie włączone)
SHOW wal_level; -- powinno być replica lub wyżej

-- Funkcja symulująca "awarię" i odzyskiwanie
CREATE OR REPLACE FUNCTION symuluj_awarie_i_recovery()
RETURNS TEXT AS $$
BEGIN
    -- Zapisz stan przed "awarią"
    CREATE TEMP TABLE stan_przed_awaria AS
    SELECT * FROM konta;
    
    -- Wykonaj transakcję
    BEGIN;
        UPDATE konta SET saldo = saldo + 1000 WHERE id_konta = 1;
        INSERT INTO historia_transakcji (id_konta_zrodlowego, kwota, status)
        VALUES (NULL, 1000, 'BONUS_AWARIA_TEST');
    COMMIT;
    
    -- "Awaria" - ale dane są już na dysku (DURABILITY)
    -- W rzeczywistości PostgreSQL używa WAL do recovery
    
    -- Sprawdź czy zmiany przetrwały
    IF EXISTS(SELECT 1 FROM historia_transakcji WHERE status = 'BONUS_AWARIA_TEST') THEN
        RETURN 'DURABILITY OK - transakcja przetrwała symulowaną awarię';
    ELSE
        RETURN 'DURABILITY FAILED - transakcja utracona';
    END IF;
END;
$$ LANGUAGE plpgsql;

SELECT symuluj_awarie_i_recovery();

-- 5. ZAAWANSOWANE CECHY TRANSAKCJI

-- Savepoints (nested transactions)
BEGIN;
    UPDATE konta SET saldo = saldo - 50 WHERE id_konta = 1;
    
    SAVEPOINT punkt_kontrolny;
    
    -- Operacja która może się nie udać
    UPDATE konta SET saldo = saldo - 10000 WHERE id_konta = 2; -- może naruszać constraint
    
    -- Jeśli błąd, cofnij tylko do savepoint
    ROLLBACK TO punkt_kontrolny;
    
    -- Kontynuuj z punktu kontrolnego
    UPDATE konta SET saldo = saldo + 25 WHERE id_konta = 2;
    
COMMIT; -- Zatwierdź całość minus operacje cofnięte do savepoint

-- Read-only transakcja
BEGIN READ ONLY;
    SELECT * FROM konta; -- OK
    -- UPDATE konta SET saldo = 0; -- BŁĄD - tylko odczyt
COMMIT;

-- Deferrable constraints (sprawdzane na końcu transakcji)
ALTER TABLE historia_transakcji 
ADD CONSTRAINT fk_konto_zrodlowe 
FOREIGN KEY (id_konta_zrodlowego) REFERENCES konta(id_konta)
DEFERRABLE INITIALLY DEFERRED;

-- Teraz constraint sprawdzany przy COMMIT, nie przy każdym INSERT

-- 6. MONITORING TRANSAKCJI

-- Aktywne transakcje
SELECT 
    pid,
    usename,
    state,
    query_start,
    now() - query_start as duration,
    query
FROM pg_stat_activity
WHERE state != 'idle' AND query != '<IDLE>';

-- Długotrwałe transakcje (potencjalny problem)
SELECT 
    pid,
    usename,
    state,
    now() - xact_start as transaction_duration,
    query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
AND now() - xact_start > interval '1 minute'
ORDER BY xact_start;

-- Statystyki transakcji w bazie
SELECT 
    datname,
    xact_commit,
    xact_rollback,
    round(100.0 * xact_rollback / (xact_commit + xact_rollback), 2) as rollback_rate
FROM pg_stat_database
WHERE datname = current_database();
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: ACID to właściwości, nie mechanizmy implementacji
2. **UWAGA**: Spójność to więcej niż constraints - także reguły biznesowe
3. **BŁĄD**: Myślenie że izolacja = brak współbieżności
4. **WAŻNE**: Durability wymaga physical write to disk, nie tylko memory
5. **PUŁAPKA**: Auto-commit może ukrywać problemy z atomowością

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **ACID properties** - właściwości ACID
- **Atomicity** - atomowość (all-or-nothing)
- **Consistency** - spójność danych
- **Isolation levels** - poziomy izolacji
- **Durability** - trwałość zmian
- **Write-Ahead Logging (WAL)** - wyprzedzające logowanie
- **Transaction states** - stany transakcji
- **Commit/Rollback** - zatwierdzenie/cofnięcie
- **Savepoints** - punkty kontrolne

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **07-poziomy-izolacji** - szczegóły izolacji
- **20-wspolbieznosc** - problemy współbieżności
- **03-protokol-dwufazowy** - implementacja izolacji
- **09-zakleszczenia** - konflikty w transakcjach
- **01-integralnosc** - spójność danych