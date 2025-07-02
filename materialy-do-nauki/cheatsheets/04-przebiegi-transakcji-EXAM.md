# 🔄 PRZEBIEGI TRANSAKCJI - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekunds)

"Przebiegi transakcji to kolejność wykonywania operacji z różnych transakcji w systemie współbieżnym. Rozróżniamy trzy rodzaje:

1. **Przebieg odtwarzalny (Recoverable)** - transakcja commituje dopiero po commit wszystkich transakcji, z których czytała
2. **Przebieg bezkaskadowy (Cascadeless/ACA)** - transakcja czyta tylko committed dane
3. **Przebieg ścisły (Strict)** - transakcja czyta i pisze tylko committed dane

Każdy ścisły jest bezkaskadowy, każdy bezkaskadowy jest odtwarzalny."

## ✍️ CO NAPISAĆ NA KARTCE

```
HIERARCHIA PRZEBIEGÓW:

Wszystkie przebiegi
    ↓
Serializowalne ⊂ Odtwarzalne (Recoverable)
                      ↓
                 Bezkaskadowe (ACA - Avoid Cascading Abort)
                      ↓  
                 Ścisłe (Strict)

DEFINICJE:

1. ODTWARZALNY (Recoverable):
   Jeśli Ti czyta z Tj, to commit(Tj) < commit(Ti)
   
2. BEZKASKADOWY (ACA):  
   Ti czyta X tylko po commit(Tj) gdzie Tj ostatnio pisało X
   
3. ŚCISŁY (Strict):
   Ti czyta/pisze X tylko po commit(Tj) gdzie Tj pisało X

PRZYKŁAD:
T1: W(X) .... .... commit
T2: .... R(X) .... commit  ← odtwarzalny, bezkaskadowy, ścisły

T1: W(X) .... commit ....
T2: .... R(X) commit ....  ← odtwarzalny, bezkaskadowy, ścisły

T1: W(X) .... .... commit  
T2: .... R(X) commit ....  ← odtwarzalny, NIE bezkaskadowy
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- PRZYKŁAD NIEODTWARZALNEGO PRZEBIEGU
-- T1: W(X) = 100, commit
-- T2: R(X) = 100, commit  
-- T3: R(X) = 100, ale T1 robi abort - PROBLEM!

-- Transakcja T1
BEGIN;
UPDATE konta SET saldo = 100 WHERE id = 1;  -- W(X) = 100
-- ... inne operacje ...
ROLLBACK;  -- abort po tym jak T2 już przeczytała X

-- Transakcja T2 (równolegle)
BEGIN;
SELECT saldo FROM konta WHERE id = 1;  -- R(X) = 100 (dirty read!)
-- T2 przeczytała wartość która zostanie cofnięta
COMMIT;  -- T2 commituje przed T1 - NIEODTWARZALNE

-- POPRAWKA: PRZEBIEG ODTWARZALNY
-- T2 musi poczekać z commit aż T1 się zakończy

-- PRZYKŁAD BEZKASKADOWEGO (ACA)
-- T1 musi commit przed czytaniem przez T2

-- Transakcja T1  
BEGIN;
UPDATE konta SET saldo = 100 WHERE id = 1;  -- W(X)
COMMIT;  -- commit przed czytaniem przez T2

-- Transakcja T2
BEGIN;
SELECT saldo FROM konta WHERE id = 1;  -- R(X) po commit T1
-- ... operacje ...
COMMIT;

-- PRZYKŁAD ŚCISŁEGO PRZEBIEGU
-- Izolacja READ COMMITTED zapewnia ścisłość

SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN;
-- wszystkie reads widzą tylko committed dane
-- wszystkie writes są chronione przed innymi transakcjami
SELECT * FROM konta WHERE id = 1;  -- widzi tylko committed
UPDATE konta SET saldo = saldo + 100 WHERE id = 1;  -- chronione
COMMIT;
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Odtwarzalny ≠ serializowalny (to różne pojęcia!)
2. **PAMIĘTAĆ**: Ścisły ⊂ Bezkaskadowy ⊂ Odtwarzalny (inclusion)
3. **UWAGA**: W odtwarzalnym może być cascade abort (lawinowe cofanie)
4. **BŁĄD**: Mylenie z poziomami izolacji (to inna klasyfikacja)
5. **WAŻNE**: Przebieg może być odtwarzalny ale nieserializowalny

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Recoverable schedule** - przebieg odtwarzalny
- **Cascadeless/ACA** - bezkaskadowy  
- **Strict schedule** - przebieg ścisły
- **Dirty read** - czytanie niezcommitted danych
- **Cascading abort** - lawinowe cofanie
- **Schedule hierarchy** - hierarchia przebiegów
- **Commit order** - kolejność commitowania
- **Dependency** - zależność między transakcjami

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **18-transakcje-acid** - izolacja i atomowość
- **07-poziomy-izolacji** - READ COMMITTED i ścisłość  
- **20-wspolbieznosc** - problemy współbieżności
- **03-protokol-dwufazowy** - mechanizm zapewniający ścisłość
- **09-zakleszczenia** - konflikty w przebiegach