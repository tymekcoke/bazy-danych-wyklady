# 🔒 PROTOKÓŁ DWUFAZOWY (2PL) - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Protokół dwufazowy to algorytm kontroli współbieżności składający się z dwóch faz:

1. **Faza rozrostu (Growing Phase)** - transakcja może tylko nabywać nowe blokady, nie może ich zwalniać
2. **Faza kurczenia (Shrinking Phase)** - transakcja może tylko zwalniać blokady, nie może nabywać nowych

Protokół ten gwarantuje serializowalność przez zapobieganie cyklom w grafie czekania, ale może prowadzić do zakleszczenia. Nie rozwiązuje problemu phantom reads."

## ✍️ CO NAPISAĆ NA KARTCE

```
PROTOKÓŁ DWUFAZOWY (2PL)

Transakcja T1:
lock(A) → read(A) → lock(B) → write(A) → unlock(A) → write(B) → unlock(B)
   ↑                    ↑                     ↑                      ↑
   |← FAZA ROZROSTU →|  punkt zamknięcia   |← FAZA KURCZENIA →|

WŁAŚCIWOŚCI:
✓ Gwarantuje serializowalność  
✓ Zapobiega dirty reads, non-repeatable reads
⚠️ Może powodować deadlock
⚠️ Nie rozwiązuje phantom reads
⚠️ Może obniżać współbieżność

WARIANTY:
- Basic 2PL (pokazany wyżej)
- Conservative 2PL (wszystkie blokady na początku)  
- Strict 2PL (zwolnienie blokad dopiero przy COMMIT)
- Rigorous 2PL (zwolnienie wszystkich blokad przy COMMIT)
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- Przykład Basic 2PL w PostgreSQL
BEGIN;
    -- FAZA ROZROSTU - nabywanie blokad
    LOCK TABLE konta IN EXCLUSIVE MODE;  -- blokada tabeli
    
    SELECT saldo FROM konta WHERE id = 1 FOR UPDATE;  -- blokada wiersza
    SELECT saldo FROM konta WHERE id = 2 FOR UPDATE;  -- druga blokada
    
    -- Punkt zamknięcia - koniec fazy rozrostu
    
    -- FAZA KURCZENIA - operacje i zwalnianie blokad
    UPDATE konta SET saldo = saldo - 100 WHERE id = 1;
    UPDATE konta SET saldo = saldo + 100 WHERE id = 2;
    
COMMIT;  -- zwolnienie wszystkich blokad

-- Przykład Strict 2PL (PostgreSQL domyślnie)
BEGIN;
    -- Wszystkie blokady w fazie rozrostu
    SELECT * FROM konta WHERE id = 1 FOR UPDATE;
    SELECT * FROM konta WHERE id = 2 FOR UPDATE;
    
    -- Operacje
    UPDATE konta SET saldo = saldo - 100 WHERE id = 1;
    UPDATE konta SET saldo = saldo + 100 WHERE id = 2;
    
    -- Blokady zwalniane dopiero przy COMMIT (Strict 2PL)
COMMIT;

-- Deadlock w 2PL - przykład problemu
-- Transakcja T1:
BEGIN;
LOCK TABLE tabela_A IN EXCLUSIVE MODE;  -- T1 blokuje A
-- ... czeka na blokadę B ...
LOCK TABLE tabela_B IN EXCLUSIVE MODE;  -- może nie uzyskać jeśli T2 ma B

-- Transakcja T2 (równolegle):
BEGIN;  
LOCK TABLE tabela_B IN EXCLUSIVE MODE;  -- T2 blokuje B
-- ... czeka na blokadę A ...
LOCK TABLE tabela_A IN EXCLUSIVE MODE;  -- deadlock!
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **NIE mylić** 2PL (Two-Phase Locking) z 2PC (Two-Phase Commit)
2. **PAMIĘTAĆ**: Po pierwszym unlock nie można już robić lock
3. **WAŻNE**: Punkt zamknięcia = pierwsza operacja unlock
4. **UWAGA**: 2PL nie zapobiega phantom reads (potrzeba predicate locking)
5. **BŁĄD**: Mówiąc "dwie fazy transakcji" zamiast "dwie fazy blokowania"

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Two-Phase Locking (2PL)** - protokół dwufazowy
- **Growing Phase** - faza rozrostu
- **Shrinking Phase** - faza kurczenia  
- **Lock point** - punkt zamknięcia
- **Serializability** - serializowalność
- **Deadlock** - zakleszczenie
- **Strict 2PL** - rygorystyczny 2PL
- **Conservative 2PL** - konserwatywny 2PL
- **Concurrency control** - kontrola współbieżności

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **10-blokady** - mechanizmy blokowania
- **09-zakleszczenia** - deadlock w 2PL
- **07-poziomy-izolacji** - związek z izolacją
- **18-transakcje-acid** - izolacja transakcji
- **20-wspolbieznosc** - problemy współbieżności