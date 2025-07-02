# Poziomy izolacji transakcji

## Definicja

**Poziom izolacji** określa, w jakim stopniu **transakcje są odizolowane** od siebie nawzajem podczas współbieżnego wykonywania.

### Dlaczego są potrzebne?
- **Kompromis** między spójnością a wydajnością
- **Kontrola** nad problemami współbieżności
- **Elastyczność** dostosowania do potrzeb aplikacji

## Problemy współbieżności

### 1. 🧹 **Dirty Read (Brudny odczyt)**
Odczytanie **niezcommitowanych** danych z innej transakcji.

```
T1: W(A, 100)
T2:           R(A) → odczytuje 100 (niezcommitowane!)
T1:                ROLLBACK → A wraca do poprzedniej wartości
```

### 2. 🔄 **Non-Repeatable Read (Niepowtarzalny odczyt)**
**Różne wyniki** tego samego zapytania w jednej transakcji.

```
T1: R(A) → 50
T2:         W(A, 100) COMMIT
T1:                         R(A) → 100 (inna wartość!)
```

### 3. 👻 **Phantom Read (Fantom)**
**Nowe rekordy** pojawiają się między kolejnymi zapytaniami.

```
T1: SELECT COUNT(*) FROM pracownicy WHERE wiek > 30 → 5
T2:                                    INSERT pracownik (wiek=35) COMMIT
T1:                                                              SELECT COUNT(*) → 6 (fantom!)
```

### 4. 💥 **Lost Update (Utracona aktualizacja)**
**Nadpisanie** zmian z innej transakcji.

```
T1: R(A, 100)
T2:          R(A, 100)
T1:                   W(A, 150) COMMIT
T2:                                   W(A, 200) COMMIT → utrata zmian T1!
```

## Standardowe poziomy izolacji SQL

### 1. 🔴 **READ UNCOMMITTED** (najniższy)

#### Definicja:
Transakcja może odczytać **niezcommitowane zmiany** innych transakcji.

#### Problemy, które występują:
- ✅ **Dirty Read** - TAK
- ✅ **Non-Repeatable Read** - TAK  
- ✅ **Phantom Read** - TAK
- ✅ **Lost Update** - TAK

#### Kiedy używać:
- **Raportowanie przybliżone** - gdy dokładność nie jest krytyczna
- **Systemy analityczne** - gdzie najważniejsza jest szybkość
- **Rzadko w praktyce** - zbyt niebezpieczny

```sql
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
BEGIN;
    SELECT * FROM konta; -- może odczytać niezcommitowane dane
COMMIT;
```

---

### 2. 🟡 **READ COMMITTED** (domyślny w większości SZBD)

#### Definicja:
Transakcja odczytuje tylko **commitowane dane**, ale między odczytami dane mogą się zmienić.

#### Problemy, które występują:
- ❌ **Dirty Read** - NIE (blokowane)
- ✅ **Non-Repeatable Read** - TAK
- ✅ **Phantom Read** - TAK
- ❌ **Lost Update** - NIE (zwykle)

#### Mechanizm:
- **Blokady odczytu** zwalniane natychmiast po odczycie
- **Blokady zapisu** trzymane do końca transakcji

```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN;
    SELECT * FROM konta WHERE id = 1; → 1000
    -- Inna transakcja może zmienić i commitować
    SELECT * FROM konta WHERE id = 1; → 1500 (różny wynik!)
COMMIT;
```

---

### 3. 🟠 **REPEATABLE READ**

#### Definicja:
Gwarantuje, że **powtórzenie tego samego odczytu** da ten sam wynik, ale mogą pojawić się nowe rekordy.

#### Problemy, które występują:
- ❌ **Dirty Read** - NIE
- ❌ **Non-Repeatable Read** - NIE (blokowane)
- ✅ **Phantom Read** - TAK (tylko nowe rekordy)
- ❌ **Lost Update** - NIE

#### Mechanizm:
- **Blokady odczytu** trzymane do końca transakcji
- **Snapshot** danych na początku transakcji

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN;
    SELECT * FROM pracownicy WHERE wiek > 30; → 5 rekordów
    -- Inna transakcja dodaje nowego pracownika (wiek=35)
    SELECT * FROM pracownicy WHERE wiek > 30; → 6 rekordów (fantom!)
COMMIT;
```

---

### 4. 🟢 **SERIALIZABLE** (najwyższy)

#### Definicja:
**Pełna izolacja** - transakcje wykonują się tak, jakby były **sekwencyjne**.

#### Problemy, które występują:
- ❌ **Dirty Read** - NIE
- ❌ **Non-Repeatable Read** - NIE  
- ❌ **Phantom Read** - NIE
- ❌ **Lost Update** - NIE

#### Mechanizm:
- **Range locks** - blokowanie zakresów
- **Predicate locks** - blokowanie warunków
- **Serialization conflicts** - wykrywanie konfliktów

```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN;
    SELECT * FROM pracownicy WHERE wiek > 30; → zawsze ten sam wynik
    -- Żadna inna transakcja nie może dodać/zmienić rekordów spełniających warunek
COMMIT;
```

## Tabela porównawcza

| Poziom izolacji | Dirty Read | Non-Repeatable | Phantom | Lost Update | Wydajność |
|----------------|------------|----------------|---------|-------------|-----------|
| **READ UNCOMMITTED** | ✅ TAK | ✅ TAK | ✅ TAK | ✅ TAK | 🚀 Najlepsza |
| **READ COMMITTED** | ❌ NIE | ✅ TAK | ✅ TAK | ❌ NIE | 🏃 Dobra |
| **REPEATABLE READ** | ❌ NIE | ❌ NIE | ✅ TAK | ❌ NIE | 🚶 Średnia |
| **SERIALIZABLE** | ❌ NIE | ❌ NIE | ❌ NIE | ❌ NIE | 🐌 Najgorsza |

## Implementacja w różnych SZBD

### PostgreSQL:
- **Domyślny**: READ COMMITTED
- **Dostępne**: READ COMMITTED, REPEATABLE READ, SERIALIZABLE
- **Brak**: READ UNCOMMITTED (działa jak READ committed)

### MySQL (InnoDB):
- **Domyślny**: REPEATABLE READ
- **Dostępne**: Wszystkie 4 poziomy

### Oracle:
- **Domyślny**: READ COMMITTED  
- **Dostępne**: READ COMMITTED, SERIALIZABLE
- **Używa MVCC** (Multi-Version Concurrency Control)

### SQL Server:
- **Domyślny**: READ COMMITTED
- **Dostępne**: Wszystkie 4 poziomy + dodatkowe

## Ustawianie poziomu izolacji

### Dla całej sesji:
```sql
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```

### Dla konkretnej transakcji:
```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN;
    -- operacje w transakcji
COMMIT;
```

### Sprawdzenie aktualnego poziomu:
```sql
-- PostgreSQL
SHOW transaction_isolation;

-- MySQL  
SELECT @@transaction_isolation;

-- SQL Server
SELECT transaction_isolation_level FROM sys.dm_exec_sessions;
```

## Przykłady praktyczne

### Przykład 1: Problemy z READ COMMITTED
```sql
-- Transakcja T1 (transfer pieniędzy)
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN;
    SELECT saldo FROM konta WHERE id = 1; → 1000
    -- T2 może tutaj zmienić saldo na 500
    UPDATE konta SET saldo = saldo - 200 WHERE id = 1; → saldo = 300 (błąd!)
COMMIT;
```

### Przykład 2: Bezpieczny transfer z REPEATABLE READ
```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN;
    SELECT saldo FROM konta WHERE id = 1; → 1000
    -- Saldo pozostanie 1000 przez całą transakcję
    UPDATE konta SET saldo = saldo - 200 WHERE id = 1; → saldo = 800 (poprawnie)
COMMIT;
```

### Przykład 3: Phantom read z REPEATABLE READ
```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN;
    SELECT COUNT(*) FROM zamowienia WHERE data = '2024-01-01'; → 5
    -- Inna transakcja dodaje zamówienie na tę datę
    SELECT COUNT(*) FROM zamowienia WHERE data = '2024-01-01'; → 6 (fantom!)
COMMIT;
```

## Wybór poziomu izolacji

### **READ COMMITTED** - gdy:
- Aplikacje webowe z dużą współbieżnością
- Operacje krótkotrwałe
- Dirty reads są niedopuszczalne

### **REPEATABLE READ** - gdy:
- Raportowanie wymagające spójności
- Obliczenia finansowe
- Operacje na agregatach

### **SERIALIZABLE** - gdy:
- Operacje krytyczne (bankowość)
- Pełna spójność jest wymagana
- Małe obciążenie systemu

## Pułapki egzaminacyjne

### 1. **Mylenie poziomów**
- READ COMMITTED ≠ REPEATABLE READ
- Phantom reads występują w REPEATABLE READ!

### 2. **Domyślne poziomy**
- PostgreSQL: READ COMMITTED (nie REPEATABLE READ!)
- MySQL: REPEATABLE READ (nie READ COMMITTED!)

### 3. **Lost Update**
- Może występować nawet w READ COMMITTED
- Wymaga specjalnych technik (SELECT FOR UPDATE)

### 4. **Wydajność vs Spójność**
- Wyższy poziom = większa spójność = gorsza wydajność
- Serializable może powodować deadlock'i