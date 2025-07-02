# Twierdzenie Heatha (Heath's Theorem)

## Definicja twierdzenia

**Twierdzenie Heatha** określa warunki, przy których można **bezstratnie rozłożyć** relację na dwie mniejsze relacje.

### Formalne brzmienie:
Niech R będzie schematem relacji. Załóżmy, że **R = α ∪ β ∪ γ**, gdzie:
- **γ = R \ (α ∪ β)** (różnica zbiorów)
- W R spełniona jest **zależność funkcyjna α → β**

**Wtedy R można bezstratnie rozłożyć na (α ∪ β, α ∪ γ).**

## Intuicja twierdzenia

### Co to oznacza w praktyce:
1. **Mamy tabelę R** z atrybutami podzielonymi na 3 grupy: α, β, γ
2. **Istnieje zależność α → β** (α determinuje β)
3. **Możemy podzielić** tabelę na dwie mniejsze bez utraty informacji
4. **Pierwsza tabela**: α + β (determinant + to co determinuje)
5. **Druga tabela**: α + γ (determinant + reszta atrybutów)

## Przykład praktyczny

### Oryginalna tabela PRACOWNICY:
```sql
CREATE TABLE pracownicy (
    id_pracownika,     -- α
    stanowisko,        -- α  
    pensja,           -- β (zależy od stanowiska)
    imie,             -- γ
    nazwisko,         -- γ
    adres             -- γ
);
```

### Zależność funkcyjna:
**stanowisko → pensja** (każde stanowisko ma określoną pensję)

### Rozkład według Heatha:
```sql
-- Tabela 1: α ∪ β = {id_pracownika, stanowisko, pensja}
CREATE TABLE pracownik_stanowisko (
    id_pracownika,
    stanowisko,
    pensja
);

-- Tabela 2: α ∪ γ = {id_pracownika, stanowisko, imie, nazwisko, adres}  
CREATE TABLE pracownik_dane (
    id_pracownika,
    stanowisko,
    imie,
    nazwisko,
    adres
);
```

## Dlaczego to działa?

### Warunek α → β jest kluczowy:
1. **Bez redundancji**: Pensja zależy tylko od stanowiska, nie od innych atrybutów
2. **Bezstratność**: Możemy odtworzyć oryginalną tabelę przez JOIN
3. **Normalizacja**: Eliminujemy powtarzające się dane o pensjach

### Odtworzenie oryginalnej tabeli:
```sql
SELECT * 
FROM pracownik_stanowisko ps
JOIN pracownik_dane pd ON ps.id_pracownika = pd.id_pracownika 
                       AND ps.stanowisko = pd.stanowisko;
```

## Warunki bezstratności

### ✅ Rozkład jest bezstratny gdy:
1. **Istnieje zależność α → β**
2. **α jest obecne w obu tabelach** (klucz łączący)
3. **Żadne dane nie są duplikowane niepotrzebnie**

### ❌ Rozkład NIE jest bezstratny gdy:
1. **Brak zależności α → β**
2. **Nieprawidłowy podział atrybutów**
3. **Utrata informacji o powiązaniach**

## Przykład błędnego rozkładu

### Tabela bez zależności funkcyjnej:
```sql
CREATE TABLE zamowienia (
    id_zamowienia,    -- α
    klient,          -- β (NIE zależy od id_zamowienia!)
    produkt,         -- γ
    ilosc            -- γ
);
```

### Błędny rozkład:
```sql
-- Tabela 1: α ∪ β
CREATE TABLE zamowienie_klient (
    id_zamowienia,
    klient
);

-- Tabela 2: α ∪ γ  
CREATE TABLE zamowienie_produkt (
    id_zamowienia,
    produkt,
    ilosc
);
```

**Problem**: Brak zależności `id_zamowienia → klient` oznacza, że rozkład może wprowadzić **sztuczne powiązania** przy JOIN!

## Zastosowania w normalizacji

### Twierdzenie Heatha w 2NF:
- **2NF eliminuje częściowe zależności**
- Używa rozkładu Heatha do wydzielenia pełnych zależności
- Przykład: `{student_id, kurs_id} → ocena` vs `student_id → imie`

### Twierdzenie Heatha w 3NF:
- **3NF eliminuje zależności przechodnie**  
- Rozkład gdy `A → B → C` (A determinuje B, B determinuje C)
- Podział na `{A, B}` i `{B, C}`

## Algorytm stosowania twierdzenia

### Krok 1: Identyfikacja zależności
```
Znajdź zależność α → β w relacji R
```

### Krok 2: Podział atrybutów
```
α = atrybuty determinujące  
β = atrybuty determinowane przez α
γ = pozostałe atrybuty (R \ (α ∪ β))
```

### Krok 3: Utworzenie rozkładu
```
R1 = α ∪ β
R2 = α ∪ γ
```

### Krok 4: Weryfikacja
```
Sprawdź czy można odtworzyć R przez JOIN(R1, R2)
```

## Pułapki egzaminacyjne

### 1. **Mylenie determinanta**
❌ Błąd: Branie β jako determinanta
✅ Poprawnie: α jest determinantem (α → β)

### 2. **Niepełny rozkład**
❌ Błąd: `R1 = {α, β}`, `R2 = {γ}` (brak α w R2!)
✅ Poprawnie: `R1 = {α, β}`, `R2 = {α, γ}`

### 3. **Ignorowanie zależności**
❌ Błąd: Rozkład bez sprawdzenia α → β
✅ Poprawnie: Zawsze weryfikuj istnienie zależności

### 4. **Mylenie z innymi twierdzeniami**
- Heath = **bezstratny rozkład**
- Armstrong = **wyprowadzanie zależności**
- Boyce-Codd = **eliminacja anomalii**

## Przykład egzaminacyjny

### Zadanie:
Dana relacja `R(A, B, C, D, E)` z zależnością `AB → C`.
Czy można ją rozłożyć według Heatha?

### Rozwiązanie:
```
α = {A, B}     (determinant)
β = {C}        (determinowane)  
γ = {D, E}     (pozostałe)

R1 = α ∪ β = {A, B, C}
R2 = α ∪ γ = {A, B, D, E}
```

**Odpowiedź**: ✅ Tak, rozkład jest bezstratny według twierdzenia Heatha.

## Korzyści zastosowania

1. **Eliminacja redundancji** - dane nie powtarzają się niepotrzebnie
2. **Normalizacja** - wyższe postacie normalne
3. **Integralność** - łatwiejsze utrzymanie spójności
4. **Wydajność** - mniejsze tabele, szybsze operacje
5. **Elastyczność** - łatwiejsze modyfikacje struktury