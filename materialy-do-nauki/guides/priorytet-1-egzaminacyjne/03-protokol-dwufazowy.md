# Protokół dwufazowy (Two-Phase Locking - 2PL)

## Definicja
Protokół dwufazowy to **mechanizm kontroli współbieżności**, który zapewnia szeregowalnść transakcji poprzez kontrolowane zarządzanie blokadami.

## Idea protokołu
**Każda transakcja przechodzi przez dwie fazy**:
1. **Faza poszerzania (Growing Phase)** - tylko nabywanie blokad
2. **Faza kurczenia (Shrinking Phase)** - tylko zwalnianie blokad

### Zasada kluczowa:
**Po zwolnieniu pierwszej blokady, transakcja nie może nabyć żadnej nowej blokady!**

## Dwie fazy szczegółowo

### Faza 1: Poszerzanie (Growing)
- Transakcja może **tylko nabywać** nowe blokady
- **Nie wolno zwalniać** żadnych blokad
- Trwa do momentu nabycia wszystkich potrzebnych blokad

### Faza 2: Kurczenie (Shrinking) 
- Transakcja może **tylko zwalniać** blokady
- **Nie wolno nabywać** nowych blokad
- Trwa do końca transakcji

## Przykład działania
```
Transakcja T1:
Czas | Akcja           | Faza
-----|-----------------|-------------
1    | LOCK(A)         | Poszerzanie
2    | READ(A)         | Poszerzanie  
3    | LOCK(B)         | Poszerzanie
4    | WRITE(B)        | Poszerzanie
5    | UNLOCK(A)       | Kurczenie ← Koniec fazy 1
6    | READ(C)         | ❌ BŁĄD! Nie można już brać blokad
```

## Odmiany protokołu dwufazowego

### 1. Podstawowy 2PL (Basic Two-Phase Locking)
- Zwykły protokół opisany powyżej
- Blokady zwalniane natychmiast po użyciu

### 2. Konserwatywny 2PL (Conservative/Static 2PL)
- **Wszystkie blokady nabywane na początku transakcji**
- Jeśli nie można nabyć wszystkich - transakcja czeka
- **Zaleta**: Brak zakleszczeń
- **Wada**: Mniejsza współbieżność

```
Konserwatywny 2PL:
1. Zażądaj wszystkich potrzebnych blokad
2. Jeśli wszystkie dostępne → rozpocznij transakcję
3. Jeśli nie → czekaj lub wycofaj
4. Wykonaj operacje
5. Zwolnij wszystkie blokady na końcu
```

### 3. Rygorystyczny 2PL (Rigorous/Strict 2PL)
- **Wszystkie blokady zwalniane dopiero przy COMMIT/ROLLBACK**
- Najpopularniejszy w praktyce
- **Zaleta**: Brak dirty reads, cascading rollbacks
- **Wada**: Dłuższe trzymanie blokad

```
Rygorystyczny 2PL:
1. Nabywaj blokady w miarę potrzeb
2. Wykonuj operacje  
3. NIE zwalniaj blokad podczas transakcji
4. Zwolnij wszystkie blokady przy COMMIT/ROLLBACK
```

## Właściwości gwarantowane przez 2PL

### ✅ Gwarantuje:
1. **Szeregowalnść (Serializability)** - główna zaleta
2. **Brak dirty reads** (w wersji rygorystycznej)
3. **Spójność danych**

### ❌ NIE gwarantuje:
1. **Brak zakleszczeń** - mogą nadal wystąpić
2. **Brak głodzenia** - transakcje mogą czekać w nieskończoność
3. **Wydajność** - może być wolniejszy

## Zakleszczenia w 2PL

### Przykład zakleszczenia:
```
T1: LOCK(A) → czeka na LOCK(B)
T2: LOCK(B) → czeka na LOCK(A)
```

### Rozwiązania:
1. **Wykrywanie zakleszczeń** - graf oczekiwania, cykliczne sprawdzanie
2. **Zapobieganie** - uporządkowanie zasobów, timeouty
3. **Unikanie** - algorytmy przewidywania (wait-die, wound-wait)

## Algorytmy resolucji zakleszczeń

### Wait-Die (Młodsi czekają na starszych)
```
Jeśli T1 (starszy) czeka na T2 (młodszy):
    T1 czeka
Jeśli T1 (młodszy) czeka na T2 (starszy):
    T1 umiera (rollback)
```

### Wound-Wait (Starsi ranią młodszych)
```
Jeśli T1 (starszy) czeka na T2 (młodszy):
    T2 umiera (T1 "rani" T2)
Jeśli T1 (młodszy) czeka na T2 (starszy):
    T1 czeka
```

## Zalety i wady protokołu 2PL

### ✅ Zalety:
1. **Gwarantuje szeregowalnść**
2. **Prosty w implementacji**
3. **Uniwersalny** - działa dla wszystkich transakcji
4. **Sprawdzony** - używany w większości SZBD

### ❌ Wady:
1. **Zakleszczenia** - wymagają dodatkowej obsługi
2. **Ograniczona współbieżność** - długie blokady
3. **Możliwe głodzenie** - niektóre transakcje mogą czekać długo
4. **Overhead** - zarządzanie blokadami kosztuje

## Implementacja w praktyce
```sql
-- PostgreSQL - automatyczny 2PL
BEGIN;
    SELECT * FROM konta WHERE id = 1 FOR UPDATE;  -- Blokada
    UPDATE konta SET saldo = saldo - 100 WHERE id = 1;
    -- Blokada zwolniona dopiero przy COMMIT
COMMIT;  -- Zwolnienie wszystkich blokad
```

## Kiedy używać którego wariantu?

### Podstawowy 2PL:
- Gdy chcemy maksymalną współbieżność
- Gdy mamy dobry mechanizm obsługi zakleszczeń

### Konserwatywny 2PL:
- Gdy chcemy uniknąć zakleszczeń
- Systemy o niskiej współbieżności

### Rygorystyczny 2PL:
- **Najczęściej używany w praktyce**
- Gdy priorytetem jest spójność danych
- Większość komercyjnych SZBD