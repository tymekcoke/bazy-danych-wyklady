# Przebiegi transakcji - odtwarzalne, bezkaskadowe i ścisłe

## Definicje podstawowe

### Przebieg (Schedule)
**Przebieg** to uporządkowana sekwencja operacji pochodzących z różnych transakcji wykonywanych współbieżnie w systemie.

### Szeregowalnść (Serializability)
Przebieg jest **szeregowalny**, jeśli daje taki sam efekt jak jakiś przebieg szeregowy (sekwencyjny) tych samych transakcji.

## Rodzaje przebiegów

### 1. 🔄 **Przebieg odtwarzalny (Recoverable Schedule)**

#### Definicja:
Przebieg jest **odtwarzalny**, jeśli dla każdej pary transakcji Ti i Tj:
- **Jeśli Tj odczytuje wartość zapisaną przez Ti, to Ti musi wykonać COMMIT przed COMMIT transakcji Tj**

#### Przykład odtwarzalnego przebiegu:
```
T1: W(A)     COMMIT
T2:     R(A)        COMMIT
```
✅ **Odtwarzalny** - T1 commituje przed T2

#### Przykład NIE-odtwarzalnego przebiegu:
```
T1: W(A)           ROLLBACK
T2:     R(A) COMMIT
```
❌ **Nieodtwarzalny** - T2 commitowało dane od T1, które zostały wycofane

#### Zalety:
- **Możliwość wycofania** - system może bezpiecznie wycofać transakcje
- **Spójność danych** - brak commitowania "brudnych" danych

#### Wady:
- **Ograniczona współbieżność** - transakcje muszą czekać na commit
- **Możliwe kaskadowe wycofania** - wycofanie jednej transakcji może spowodować wycofanie innych

---

### 2. 🚫 **Przebieg bezkaskadowy (Cascadeless Schedule)**

#### Definicja:
Przebieg jest **bezkaskadowy**, jeśli żadna transakcja nie odczytuje wartości zapisanych przez niecommitowane transakcje.

**Zasada**: Transakcja może odczytać wartość X tylko wtedy, gdy ostatnia transakcja, która zapisała X, już wykonała COMMIT.

#### Przykład bezkaskadowego przebiegu:
```
T1: W(A)     COMMIT
T2:              R(A) W(B) COMMIT
T3:                           R(B) COMMIT
```
✅ **Bezkaskadowy** - każda transakcja odczytuje tylko committowane dane

#### Przykład NIE-bezkaskadowego przebiegu:
```
T1: W(A)
T2:     R(A) W(B)     COMMIT
T3:              R(B)        COMMIT
T1:                            ROLLBACK
```
❌ **Kaskadowy** - wycofanie T1 wymaga wycofania T2, które wymaga wycofania T3

#### Zalety:
- **Brak kaskadowych wycofań** - wycofanie jednej transakcji nie wpływa na inne
- **Prostsze zarządzanie** - łatwiejsze utrzymanie spójności
- **Lepsza wydajność** - brak kosztownych operacji kaskadowego wycofania

#### Wady:
- **Mniejsza współbieżność** - więcej ograniczeń na odczyty
- **Dłuższe oczekiwanie** - transakcje czekają na commit innych

---

### 3. 🔒 **Przebieg ścisły (Strict Schedule)**

#### Definicja:
Przebieg jest **ścisły**, jeśli żadna transakcja nie odczytuje ani nie zapisuje wartości napisanych przez niecommitowane transakcje.

**Zasada**: Transakcja może odczytać lub zapisać wartość X tylko wtedy, gdy ostatnia transakcja, która zapisała X, już wykonała COMMIT lub ROLLBACK.

#### Przykład ścisłego przebiegu:
```
T1: W(A)     COMMIT
T2:              R(A) W(A) COMMIT
T3:                           W(A) COMMIT
```
✅ **Ścisły** - żadna transakcja nie dotyka niecommitowanych danych

#### Przykład NIE-ścisłego przebiegu:
```
T1: W(A)
T2:     W(A) COMMIT  ← T2 nadpisuje niecommitowaną wartość T1
T1:              ROLLBACK
```
❌ **Nieścisły** - T2 nadpisuje niecommitowane dane T1

#### Zalety:
- **Maksymalna bezpieczeństwo** - najbardziej restrykcyjny
- **Proste wycofywanie** - transakcja może być łatwo wycofana
- **Brak dirty reads i dirty writes**
- **Łatwe odtwarzanie** po awarii

#### Wady:
- **Najmniejsza współbieżność** - najbardziej ograniczający
- **Długie blokady** - transakcje trzymają blokady do COMMIT/ROLLBACK

---

## Hierarchia przebiegów

```
Wszystkie przebiegi
    ↓
Przebiegi odtwarzalne (Recoverable)
    ↓  
Przebiegi bezkaskadowe (Cascadeless) 
    ↓
Przebiegi ścisłe (Strict)
    ↓
Przebiegi szeregowe (Serial)
```

**Relacja**: Ścisły ⊆ Bezkaskadowy ⊆ Odtwarzalny

## Praktyczne zastosowania

### W systemach DBMS:
- **PostgreSQL**: Domyślnie używa przebiegów ścisłych (Strict 2PL)
- **MySQL InnoDB**: Również przebiegi ścisłe
- **Oracle**: Używa wielowersyjności + ścisłe przebiegi

### Poziomy izolacji a rodzaje przebiegów:
- **SERIALIZABLE**: Gwarantuje przebiegi szeregowe
- **REPEATABLE READ**: Zwykle przebiegi ścisłe
- **READ COMMITTED**: Przebiegi bezkaskadowe
- **READ UNCOMMITTED**: Może pozwalać na nieodtwarzalne

## Przykłady egzaminacyjne

### Przykład 1: Klasyfikuj przebieg
```
T1: R(X) W(X)           COMMIT
T2:           R(X) W(Y)        COMMIT  
T3:                     R(Y)          COMMIT
```

**Analiza**:
- **Odtwarzalny**: ✅ Tak (T2 commituje przed T3, T1 przed T2)
- **Bezkaskadowy**: ✅ Tak (wszyscy odczytują committowane dane)
- **Ścisły**: ✅ Tak (nikt nie dotyka niecommitowanych danych)

### Przykład 2: Klasyfikuj przebieg
```
T1: W(X)
T2:     R(X) W(Y) COMMIT
T1:                    COMMIT
T3:                           R(Y) COMMIT
```

**Analiza**:
- **Odtwarzalny**: ✅ Tak (T1 commituje przed końcem)
- **Bezkaskadowy**: ❌ Nie (T2 odczytuje niecommitowane X od T1)
- **Ścisły**: ❌ Nie (T2 odczytuje niecommitowane dane)

## Pułapki egzaminacyjne

1. **Mylenie pojęć**: Bezkaskadowy ≠ bez zakleszczeń
2. **Kolejność commitów**: Ważna dla odtwarzalności
3. **Operacje R vs W**: Ścisły zabrania obu na niecommitowanych danych
4. **Transakcje wycofane**: Pamiętaj o ROLLBACK w analizie