# Zależności funkcyjne - teoria i zastosowania

## Definicja zależności funkcyjnej

**Zależność funkcyjna** X → Y oznacza, że wartość zbioru atrybutów X **jednoznacznie determinuje** wartość zbioru atrybutów Y w każdej możliwej instancji relacji.

### Formalna definicja:
```
Dla relacji R i zbiorów atrybutów X, Y ⊆ R:
X → Y zachodzi wtedy i tylko wtedy, gdy
∀ t₁, t₂ ∈ R: t₁[X] = t₂[X] ⟹ t₁[Y] = t₂[Y]

Jeśli dwie krotki mają identyczne wartości na X,
to muszą mieć identyczne wartości na Y
```

### Intuicyjna interpretacja:
```
X → Y oznacza:
"Znając wartość X, można jednoznacznie określić wartość Y"
```

## Przykłady zależności funkcyjnych

### 1. **Podstawowe przykłady**
```sql
-- Relacja STUDENCI(nr_indeksu, imie, nazwisko, email, kierunek)

-- Oczywiste zależności funkcyjne:
nr_indeksu → imie              -- Numer indeksu determinuje imię
nr_indeksu → nazwisko          -- Numer indeksu determinuje nazwisko  
nr_indeksu → email             -- Numer indeksu determinuje email
nr_indeksu → {imie, nazwisko}  -- Numer indeksu determinuje imię i nazwisko

-- Możliwe zależności (zależnie od zasad uczelni):
email → nr_indeksu             -- Email determinuje numer (jeśli unikalne)
{imie, nazwisko} → kierunek    -- Może nie zachodzić (dwóch studentów o tym samym imieniu/nazwisku na różnych kierunkach)
```

### 2. **Przykłady biznesowe**
```sql
-- PRACOWNICY(id, imie, nazwisko, pesel, id_dzialu, nazwa_dzialu, kierownik)

-- Zależności funkcyjne:
id → {imie, nazwisko, pesel, id_dzialu}    -- ID pracownika determinuje jego dane
pesel → {id, imie, nazwisko}               -- PESEL determinuje tożsamość
id_dzialu → {nazwa_dzialu, kierownik}      -- ID działu determinuje nazwę i kierownika

-- Zależności przechodnie:
id → id_dzialu → nazwa_dzialu              -- ID pracownika → ID działu → nazwa działu
id → id_dzialu → kierownik                 -- ID pracownika → ID działu → kierownik działu
```

### 3. **Przykłady z kontekstu biznesowego**
```sql
-- ZAMOWIENIA(id_zamowienia, data, id_klienta, nazwa_klienta, adres_klienta, 
--            id_produktu, nazwa_produktu, cena, ilosc)

-- Zależności funkcyjne:
id_zamowienia → {data, id_klienta}                    -- Zamówienie determinuje datę i klienta
id_klienta → {nazwa_klienta, adres_klienta}           -- Klient determinuje swoje dane
id_produktu → {nazwa_produktu, cena}                  -- Produkt determinuje nazwę i cenę
{id_zamowienia, id_produktu} → ilosc                  -- Para zamówienie-produkt determinuje ilość
```

## Notacja i składnia

### 1. **Notacja podstawowa**
```
X → Y    "X determinuje Y" lub "Y zależy funkcyjnie od X"

Gdzie:
X = determinant (lewa strona)  
Y = dependent (prawa strona)
```

### 2. **Rozszerzenia notacji**
```sql
-- Pojedyncze atrybuty
A → B                          -- A determinuje B

-- Zbiory atrybutów  
{A, B} → C                     -- A i B razem determinują C
AB → C                         -- Skrócona notacja dla {A, B} → C

-- Wiele atrybutów po prawej stronie
A → {B, C}                     -- A determinuje B i C
A → BC                         -- Skrócona notacja

-- Złożone zależności
{A, B} → {C, D}                -- {A, B} determinuje {C, D}
AB → CD                        -- Skrócona notacja
```

### 3. **Przykłady w różnych notacjach**
```sql
-- Wszystkie równoważne zapisy:
nr_indeksu → {imie, nazwisko}
nr_indeksu → imie, nazwisko
nr_indeksu → imie ∧ nr_indeksu → nazwisko

-- Złożone determinanty:
{imie, nazwisko, data_urodzenia} → nr_indeksu
imie, nazwisko, data_urodzenia → nr_indeksu
```

## Reguły wnioskowania (Armstrong's Axioms)

### 1. **Aksjomaty podstawowe**

#### **Refleksywność (Reflexivity)**
```
Jeśli Y ⊆ X, to X → Y

Przykład:
{nr_indeksu, imie} → nr_indeksu    -- Zawsze prawda
{nr_indeksu, imie} → imie          -- Zawsze prawda
{nr_indeksu, imie} → {nr_indeksu, imie}  -- Zawsze prawda
```

#### **Rozszerzalność (Augmentation)**  
```
Jeśli X → Y, to XZ → YZ (dla dowolnego Z)

Przykład:
Jeśli nr_indeksu → imie
To {nr_indeksu, kierunek} → {imie, kierunek}
```

#### **Przechodniość (Transitivity)**
```
Jeśli X → Y i Y → Z, to X → Z

Przykład:
nr_indeksu → id_dzialu     (student ma dział)
id_dzialu → nazwa_dzialu   (dział ma nazwę)
Więc: nr_indeksu → nazwa_dzialu  (student ma nazwę działu)
```

### 2. **Reguły pochodne**

#### **Związek (Union)**
```
Jeśli X → Y i X → Z, to X → YZ

Przykład:
nr_indeksu → imie
nr_indeksu → nazwisko
Więc: nr_indeksu → {imie, nazwisko}
```

#### **Rozkład (Decomposition)**
```
Jeśli X → YZ, to X → Y i X → Z

Przykład:
nr_indeksu → {imie, nazwisko}
Więc: nr_indeksu → imie i nr_indeksu → nazwisko
```

#### **Pseudoprzechodniość (Pseudotransitivity)**
```
Jeśli X → Y i WY → Z, to WX → Z

Przykład:
student_id → kurs_id
{rok, kurs_id} → sala
Więc: {rok, student_id} → sala
```

## Domknięcie atrybutów

### Definicja:
**Domknięcie zbioru atrybutów X** (oznaczane X⁺) to zbiór wszystkich atrybutów, które są funkcyjnie determinowane przez X.

### Algorytm obliczania domknięcia:
```
INPUT: Zbiór atrybutów X, zbiór zależności funkcyjnych F
OUTPUT: X⁺

1. Closure := X
2. REPEAT
3.   OldClosure := Closure  
4.   FOR każdej zależności Y → Z w F DO
5.     IF Y ⊆ Closure THEN
6.       Closure := Closure ∪ Z
7.     END IF
8.   END FOR
9. UNTIL Closure = OldClosure
10. RETURN Closure
```

### Przykład obliczania domknięcia:
```sql
-- Relacja: R(A, B, C, D, E)
-- Zależności funkcyjne: F = {A → BC, B → E, CD → A}

-- Oblicz {A}⁺:
Krok 1: Closure = {A}
Krok 2: A → BC, więc A ⊆ {A}, dodaj BC
        Closure = {A, B, C}
Krok 3: B → E, więc B ⊆ {A, B, C}, dodaj E  
        Closure = {A, B, C, E}
Krok 4: CD → A, ale CD ⊄ {A, B, C, E} (brak D)
        Closure = {A, B, C, E} (bez zmian)

Wynik: {A}⁺ = {A, B, C, E}

-- Oblicz {C, D}⁺:
Krok 1: Closure = {C, D}
Krok 2: CD → A, więc CD ⊆ {C, D}, dodaj A
        Closure = {A, C, D}
Krok 3: A → BC, więc A ⊆ {A, C, D}, dodaj BC
        Closure = {A, B, C, D}
Krok 4: B → E, więc B ⊆ {A, B, C, D}, dodaj E
        Closure = {A, B, C, D, E}

Wynik: {C, D}⁺ = {A, B, C, D, E}
```

## Klucze i superklucze

### Definicje w kontekście zależności funkcyjnych:

#### **Superklucz**
```
Zbiór atrybutów K jest superklucze relacji R, jeśli:
K⁺ = R (domknięcie K zawiera wszystkie atrybuty R)

Przykład:
Jeśli {A}⁺ = {A, B, C, D, E} i R = {A, B, C, D, E}
To {A} jest superklucze
```

#### **Klucz kandydujący** 
```
Superklucz K jest kluczem kandydującym, jeśli:
1. K⁺ = R (jest superklucze)
2. Dla każdego właściwego podzbioru K' ⊂ K: K'⁺ ≠ R (jest minimalny)

Przykład:
Jeśli {A}⁺ = {A, B, C, D, E}
To {A} jest kluczem kandydującym (minimalny superklucz)
```

### Algorytm znajdowania kluczy kandydujących:
```
1. Znajdź wszystkie superklucze
2. Dla każdego superklucza sprawdź minimalność
3. Usuń nadmiarowe atrybuty

Przykład systematyczny:
R(A, B, C, D), F = {A → B, B → C, C → D, D → A}

Sprawdź domknięcia:
{A}⁺ = {A, B, C, D} ← Superklucz
{B}⁺ = {A, B, C, D} ← Superklucz  
{C}⁺ = {A, B, C, D} ← Superklucz
{D}⁺ = {A, B, C, D} ← Superklucz

Wszystkie są minimalne, więc klucze kandydujące: {A}, {B}, {C}, {D}
```

## Pokrycie zależności funkcyjnych

### Definicja:
**Pokrycie F⁺** to zbiór wszystkich zależności funkcyjnych, które można wywnioskować z F przy użyciu aksjomatów Armstrong'a.

### Równoważność zbiorów zależności:
```
Dwa zbiory F i G są równoważne (F ≡ G), jeśli:
F⁺ = G⁺

Oznacza to, że można wywnioskować te same zależności z obu zbiorów
```

### Przykład:
```sql
F₁ = {A → B, B → C}
F₂ = {A → B, B → C, A → C}

F₁⁺ zawiera A → C (przez przechodniość)
F₂ jawnie zawiera A → C

Więc F₁ ≡ F₂ (są równoważne)
```

## Pokrycie minimalne (Canonical Cover)

### Definicja:
**Pokrycie minimalne Fc** dla zbioru F to równoważny zbiór zależności taki, że:
1. Każda zależność w Fc ma pojedynczy atrybut po prawej stronie
2. Żadnej zależności nie można usunąć bez zmiany domknięcia
3. Żaden atrybut po lewej stronie nie jest nadmiarowy

### Algorytm znajdowania pokrycia minimalnego:
```
INPUT: Zbiór zależności funkcyjnych F
OUTPUT: Pokrycie minimalne Fc

1. Przejdź na prawą stronę pojedynczą:
   Zamień X → YZ na X → Y i X → Z

2. Usuń nadmiarowe atrybuty z lewej strony:
   Dla każdej zależności X → A:
     Dla każdego B ∈ X:
       Jeśli ((X - {B}) → A) ∈ (F - {X → A})⁺
       To zamień X → A na (X - {B}) → A

3. Usuń nadmiarowe zależności:
   Dla każdej zależności fd:
     Jeśli fd ∈ (F - {fd})⁺
     To usuń fd z F
```

### Przykład:
```sql
F = {A → BC, B → C, A → B, AB → C}

Krok 1: Rozkład prawej strony
F = {A → B, A → C, B → C, A → B, AB → C}

Krok 2: Usuń duplikaty  
F = {A → B, A → C, B → C, AB → C}

Krok 3: Usuń nadmiarowe atrybuty z lewej strony
AB → C: Sprawdź czy A → C lub B → C
A → C już jest w F, więc AB → C jest nadmiarowe
F = {A → B, A → C, B → C}

Krok 4: Usuń nadmiarowe zależności
A → C: Sprawdź czy A → C ∈ {A → B, B → C}⁺
A → B i B → C dają A → C (przechodniość)
Więc A → C jest nadmiarowe

Fc = {A → B, B → C}
```

## Zastosowania w normalizacji

### 1. **Wykrywanie naruszeń postaci normalnych**

#### Sprawdzanie 2NF:
```sql
-- Relacja jest w 2NF jeśli każdy atrybut niekluczowy
-- jest w pełni zależny od każdego klucza kandydującego

-- Przykład naruszenia 2NF:
R(Student_ID, Course_ID, Grade, Student_Name, Course_Name)
F = {Student_ID → Student_Name, Course_ID → Course_Name, 
     {Student_ID, Course_ID} → Grade}

Klucz: {Student_ID, Course_ID}
Częściowe zależności:
- Student_ID → Student_Name (naruszenie 2NF)
- Course_ID → Course_Name (naruszenie 2NF)
```

#### Sprawdzanie 3NF:
```sql
-- Relacja jest w 3NF jeśli nie ma zależności przechodnich

-- Przykład naruszenia 3NF:
R(Employee_ID, Dept_ID, Dept_Name, Manager)  
F = {Employee_ID → Dept_ID, Dept_ID → {Dept_Name, Manager}}

Zależność przechodnia:
Employee_ID → Dept_ID → Dept_Name (naruszenie 3NF)
Employee_ID → Dept_ID → Manager (naruszenie 3NF)
```

### 2. **Algorytm dekompozycji do 3NF**

#### Algorytm syntezy:
```
INPUT: Relacja R, zależności F
OUTPUT: Dekompozycja do 3NF

1. Znajdź pokrycie minimalne Fc
2. Dla każdej zależności X → Y w Fc:
   Utwórz relację RXY = XY
3. Jeśli żadna relacja nie zawiera klucza R:
   Dodaj relację zawierającą klucz R
4. Usuń relacje będące podzbiorami innych relacji
```

#### Przykład:
```sql
R(A, B, C, D, E, F)
F = {A → BC, B → E, CD → F}

Krok 1: Fc = {A → B, A → C, B → E, CD → F} (już minimalne)

Krok 2: Utwórz relacje
R1(A, B)     -- z A → B
R2(A, C)     -- z A → C  
R3(B, E)     -- z B → E
R4(C, D, F)  -- z CD → F

Krok 3: Sprawdź klucze
Klucze R: {A, D} (można sprawdzić przez domknięcie)
Żadna relacja nie zawiera {A, D}
Dodaj: R5(A, D)

Wynik: R1(A, B), R2(A, C), R3(B, E), R4(C, D, F), R5(A, D)
```

## Algorytm dekompozycji do BCNF

### BCNF vs 3NF:
```
BCNF: Każdy determinant jest kluczem kandydującym
3NF: Każdy atrybut niekluczowy zależy w pełni od kluczy

BCNF jest silniejsza niż 3NF
```

### Algorytm dekompozycji do BCNF:
```
INPUT: Relacja R, zależności F
OUTPUT: Dekompozycja do BCNF

1. Sprawdź czy R jest w BCNF
2. Jeśli nie, znajdź naruszającą zależność X → Y
3. Podziel R na R1 = XY i R2 = R - Y + X
4. Rekurencyjnie zastosuj algorytm do R1 i R2
```

### Przykład:
```sql
R(A, B, C)
F = {AB → C, C → B}

Sprawdź BCNF:
Klucze kandydujące: {A, C} (bo {A,C}⁺ = {A,B,C})
Zależności: AB → C, C → B

C → B narusza BCNF (C nie jest kluczem kandydującym)

Dekompozycja na C → B:
R1 = {C, B}  
R2 = {A, C}

Sprawdź R1: Klucz {C}, zależność C → B ✓ BCNF
Sprawdź R2: Klucz {A, C}, brak innych zależności ✓ BCNF

Wynik: R1(C, B), R2(A, C)
```

## Testowanie zależności funkcyjnych

### Sprawdzanie czy X → Y zachodzi w F⁺:
```
X → Y ∈ F⁺ ⟺ Y ⊆ X⁺

Algorytm:
1. Oblicz X⁺ względem F
2. Sprawdź czy Y ⊆ X⁺
```

### Przykład:
```sql
R(A, B, C, D)
F = {A → B, B → C, C → D}

Sprawdź czy A → D ∈ F⁺:
1. Oblicz {A}⁺:
   {A}⁺ = {A, B, C, D} (przez przechodniość)
2. Sprawdź czy {D} ⊆ {A, B, C, D}
   TAK, więc A → D ∈ F⁺
```

## Właściwości zależności funkcyjnych

### 1. **Stabilność względem projekcji**
```
Jeśli F jest zbiorem zależności dla R(X),
to πY(F) jest zbiorem zależności dla πY(R)

πY(F) = {U → V | U → V ∈ F⁺ ∧ UV ⊆ Y}
```

### 2. **Niestabilność względem złączeń**
```
Zależności mogą zostać utracone przy dekompozycji

Dekompozycja zachowująca zależności:
F ≡ (π_R1(F) ∪ π_R2(F) ∪ ... ∪ π_Rn(F))
```

### 3. **Zależności wielowartościowe**
```
Rozszerzenie zależności funkcyjnych
X ↠ Y oznacza, że X determinuje zbiór wartości Y

Związek z 4NF i dalszą normalizacją
```

## Narzędzia i implementacja

### 1. **Algorytmy w praktyce**
```python
# Pseudokod obliczania domknięcia
def closure(X, F):
    result = set(X)
    changed = True
    while changed:
        changed = False
        for (left, right) in F:
            if left.issubset(result) and not right.issubset(result):
                result = result.union(right)
                changed = True
    return result
```

### 2. **Narzędzia CASE**
```
- ERwin Data Modeler
- PowerDesigner  
- MySQL Workbench
- DB Designer Fork
- Akademickie narzędzia do normalizacji
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**
1. **Dokumentuj zależności** - jako komentarze lub ograniczenia
2. **Używaj normalnych form** - odpowiednio do zastosowania
3. **Sprawdzaj minimalność** - usuń nadmiarowe zależności
4. **Testuj domknięcia** - dla weryfikacji kluczy

### ❌ **Złe praktyki:**
1. **Ignorowanie teorii** - projektowanie bez analizy zależności
2. **Over-normalization** - nadmierna normalizacja kosztem wydajności
3. **Brak dokumentacji** - nie zapisywanie założeń biznesowych
4. **Naiwne podejście** - projektowanie bez znajomości zależności

## Pułapki egzaminacyjne

### 1. **Różnica między zależnościami**
```
X → Y: funkcyjna (jednoznaczna)
X ↠ Y: wielowartościowa (zbiór wartości)
X ⟶ Y: inkluzji (jeden-do-wielu w kontekście)
```

### 2. **Minimalizacja vs ekvivalencja**
```
Pokrycie minimalne ≠ najmniejszy zbiór
Chodzi o usunięcie nadmiarowości, nie maksymalne zmniejszenie
```

### 3. **BCNF vs 3NF**
```
BCNF: każdy determinant to klucz
3NF: każdy niekluczowy atrybut w pełni zależy od kluczy

BCNF ⟹ 3NF ale 3NF ⟹ BCNF
```

### 4. **Domknięcie atrybutów**
```
X⁺ zawiera X (refleksywność)
Algorytm musi być iterowany do stabilizacji
Porządek zastosowania reguł nie ma znaczenia dla wyniku
```