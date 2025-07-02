# Normalizacja zaawansowana - 4NF i 5NF

## Wprowadzenie do normalizacji zaawansowanej

Po **3NF i BCNF**, które rozwiązują problemy związane z **zależnościami funkcyjnymi**, istnieją wyższe formy normalne zajmujące się **zależnościami wielowartościowymi** i **zależnościami łączenia**.

### Hierarchia form normalnych:
```
1NF ⟸ 2NF ⟸ 3NF ⟸ BCNF ⟸ 4NF ⟸ 5NF

Każda wyższa forma implikuje wszystkie niższe
```

### Problemy rozwiązywane:
- **4NF**: Redundancja z zależności wielowartościowych
- **5NF**: Anomalie związane z dekompozycją złączeń

## Czwarta Postać Normalna (4NF)

### Zależność wielowartościowa (MVD)

#### Definicja:
**Zależność wielowartościowa X ↠ Y** w relacji R oznacza, że dla każdej wartości X, **zbiór wartości Y jest niezależny** od wartości pozostałych atrybutów.

#### Formalna definicja:
```
Dla relacji R(X, Y, Z) zależność X ↠ Y zachodzi, jeśli:
∀ t₁, t₂ ∈ R: jeśli t₁[X] = t₂[X] 
to istnieją krotki t₃, t₄ ∈ R takie, że:
- t₃[X] = t₄[X] = t₁[X] = t₂[X]
- t₃[Y] = t₁[Y] ∧ t₃[Z] = t₂[Z]
- t₄[Y] = t₂[Y] ∧ t₄[Z] = t₁[Z]
```

#### Intuicyjna interpretacja:
```
X ↠ Y oznacza:
"Dla każdej wartości X, wartości Y i pozostałe wartości (Z) 
są niezależne - można je dowolnie kombinować"
```

### Przykład zależności wielowartościowej

#### Problem - nieredundalna relacja:
```sql
-- Relacja PRACOWNIK_UMIEJETNOSCI_PROJEKTY
CREATE TABLE PSK (
    pracownik VARCHAR(50),
    umiejetnosc VARCHAR(50),
    projekt VARCHAR(50),
    PRIMARY KEY (pracownik, umiejetnosc, projekt)
);

-- Dane przykładowe
INSERT INTO PSK VALUES
('Kowalski', 'Java', 'Projekt A'),
('Kowalski', 'Java', 'Projekt B'),  
('Kowalski', 'Python', 'Projekt A'),
('Kowalski', 'Python', 'Projekt B'),
('Nowak', 'C++', 'Projekt C'),
('Nowak', 'SQL', 'Projekt C');
```

#### Analiza problemu:
```sql
-- Kowalski ma umiejętności: {Java, Python}
-- Kowalski pracuje w projektach: {Projekt A, Projekt B}
-- 
-- Problem: musimy przechowywać 4 krotki (2×2 kombinacje)
-- choć logicznie to są 2 niezależne informacje:
-- 1. Kowalski → {Java, Python}
-- 2. Kowalski → {Projekt A, Projekt B}

-- Zależności wielowartościowe:
-- pracownik ↠ umiejetnosc (umiejętności niezależne od projektów)
-- pracownik ↠ projekt (projekty niezależne od umiejętności)
```

#### Redundancja i anomalie:
```sql
-- Anomalia wstawiania: 
-- Aby dodać nową umiejętność Kowalskiego (np. 'JavaScript'), 
-- musimy dodać po jednej krotce dla każdego jego projektu

INSERT INTO PSK VALUES
('Kowalski', 'JavaScript', 'Projekt A'),
('Kowalski', 'JavaScript', 'Projekt B');

-- Anomalia usuwania:
-- Usunięcie umiejętności może usunąć informację o projektach

-- Anomalia aktualizacji:
-- Zmiana nazwy projektu wymaga aktualizacji wielu krotek
```

### Definicja 4NF

#### Formalna definicja:
**Relacja R jest w 4NF**, jeśli:
1. **Jest w BCNF**
2. **Nie zawiera nietrywialnych zależności wielowartościowych**

#### Nietrywialna zależność wielowartościowa:
```
X ↠ Y jest nietrywialna, jeśli:
1. Y ⊄ X (Y nie jest podzbiorem X)
2. X ∪ Y ≠ R (X i Y razem nie wyczerpują wszystkich atrybutów)
```

### Przykłady naruszeń 4NF

#### Przykład 1: Pracownik-Umiejętności-Projekty
```sql
-- Relacja PSK(pracownik, umiejetnosc, projekt)
-- Naruszenia 4NF:
pracownik ↠ umiejetnosc  -- Nietrywialna MVD
pracownik ↠ projekt      -- Nietrywialna MVD

-- Dowód naruszenia:
-- Dla pracownika 'Kowalski':
-- Umiejętności: {Java, Python}  
-- Projekty: {Projekt A, Projekt B}
-- Konieczne są wszystkie 4 kombinacje (2×2)
```

#### Przykład 2: Kurs-Podręcznik-Wykładowca  
```sql
CREATE TABLE KURS_MATERIAL (
    kurs VARCHAR(50),
    podrecznik VARCHAR(100),
    wykladowca VARCHAR(50),
    PRIMARY KEY (kurs, podrecznik, wykladowca)
);

-- Zależności wielowartościowe:
kurs ↠ podrecznik    -- Kurs ma zestaw podręczników
kurs ↠ wykladowca    -- Kurs ma zestaw wykładowców

-- Problem: n×m kombinacji dla n podręczników i m wykładowców
```

### Dekompozycja do 4NF

#### Zasada dekompozycji:
```
Jeśli relacja R(X, Y, Z) zawiera MVD X ↠ Y,
to można ją podzielić na:
R1(X, Y) i R2(X, Z)

gdzie Z = R - X - Y
```

#### Przykład dekompozycji PSK:
```sql
-- Oryginalna relacja z naruszeniem 4NF:
PSK(pracownik, umiejetnosc, projekt)

-- Dekompozycja na podstawie pracownik ↠ umiejetnosc:
PRACOWNIK_UMIEJETNOSCI(pracownik, umiejetnosc)
PRACOWNIK_PROJEKTY(pracownik, projekt)

-- Dane po dekompozycji:
PRACOWNIK_UMIEJETNOSCI:
(Kowalski, Java)
(Kowalski, Python)
(Nowak, C++)
(Nowak, SQL)

PRACOWNIK_PROJEKTY:
(Kowalski, Projekt A)
(Kowalski, Projekt B)  
(Nowak, Projekt C)
```

#### Korzyści z dekompozycji:
```sql
-- Eliminacja redundancji:
-- Zamiast 4 krotek dla Kowalskiego → 4 krotki łącznie (2+2)

-- Eliminacja anomalii:
-- Dodanie umiejętności: 1 krotka w PRACOWNIK_UMIEJETNOSCI
-- Dodanie projektu: 1 krotka w PRACOWNIK_PROJEKTY
-- Niezależne operacje

-- Rekonstrukcja oryginalnych danych:
SELECT pu.pracownik, pu.umiejetnosc, pp.projekt
FROM PRACOWNIK_UMIEJETNOSCI pu
JOIN PRACOWNIK_PROJEKTY pp ON pu.pracownik = pp.pracownik;
```

## Aksjomaty dla zależności wielowartościowych

### Reguły wnioskowania:

#### 1. **Refleksywność MVD**
```
X ↠ ∅ (pusta zależność)
X ↠ X (trywialny przypadek)
```

#### 2. **Rozszerzalność MVD**
```
Jeśli X ↠ Y, to XZ ↠ YZ
```

#### 3. **Przechodniość MVD**
```
Jeśli X ↠ Y i Y ↠ Z, to X ↠ Z
```

#### 4. **Związek FD i MVD**
```
Jeśli X → Y (zależność funkcyjna), to X ↠ Y (zależność wielowartościowa)

Każda zależność funkcyjna jest szczególnym przypadkiem MVD
```

#### 5. **Uzupełnienie MVD**
```
Jeśli X ↠ Y w relacji R, to X ↠ (R - X - Y)

W PSK: jeśli pracownik ↠ umiejetnosc, 
to też pracownik ↠ projekt
```

### Przykład zastosowania aksjomatów:
```sql
-- Dane: R(A, B, C, D, E)
-- MVD: A ↠ BC, CD ↠ E

-- Zastosowanie rozszerzalności:
-- A ↠ BC ⟹ AD ↠ BCD

-- Zastosowanie uzupełnienia:
-- A ↠ BC ⟹ A ↠ DE (bo R - A - BC = DE)

-- Zastosowanie przechodniości:
-- A ↠ BC i BC ↠ (coś) można kombinować dla wyników
```

## Piąta Postać Normalna (5NF)

### Zależność łączenia (Join Dependency)

#### Definicja:
**Zależność łączenia (JD)** ⋈{R₁, R₂, ..., Rₙ} oznacza, że relację R można **bezstratnie zrekonstruować** jako naturalny JOIN relacji R₁, R₂, ..., Rₙ.

#### Formalna definicja:
```
R spełnia JD ⋈{R₁, R₂, ..., Rₙ}, jeśli:
R = π_R₁(R) ⋈ π_R₂(R) ⋈ ... ⋈ π_Rₙ(R)

gdzie π_Rᵢ(R) to projekcja R na atrybuty Rᵢ
```

### Przykład zależności łączenia

#### Problem - relacja trójstronna:
```sql
-- Relacja DOSTAWCA_CZĘŚĆ_PROJEKT
CREATE TABLE DCP (
    dostawca VARCHAR(50),
    czesc VARCHAR(50), 
    projekt VARCHAR(50),
    PRIMARY KEY (dostawca, czesc, projekt)
);

-- Dane przykładowe
INSERT INTO DCP VALUES
('D1', 'Śruba', 'P1'),
('D1', 'Nakrętka', 'P1'),
('D1', 'Śruba', 'P2'),
('D2', 'Nakrętka', 'P1'),
('D2', 'Nakrętka', 'P2');
```

#### Analiza dekompozycji:
```sql
-- Binarna dekompozycja (jak w 4NF) może być stratna:

-- Projekcje:
DP(dostawca, projekt):
('D1', 'P1'), ('D1', 'P2'), ('D2', 'P1'), ('D2', 'P2')

DC(dostawca, czesc):  
('D1', 'Śruba'), ('D1', 'Nakrętka'), ('D2', 'Nakrętka')

CP(czesc, projekt):
('Śruba', 'P1'), ('Śruba', 'P2'), ('Nakrętka', 'P1'), ('Nakrętka', 'P2')

-- JOIN DP ⋈ DC ⋈ CP daje:
-- BŁĘDNIE: ('D2', 'Śruba', 'P1') - nie było w oryginalnej relacji!
-- BŁĘDNIE: ('D2', 'Śruba', 'P2') - nie było w oryginalnej relacji!
```

#### Warunki dla bezstratnej dekompozycji:
```sql
-- DCP może być bezstratnie zdekomponowana, jeśli zachodzi:
-- Zależność łączenia ⋈{(dostawca, czesc), (dostawca, projekt), (czesc, projekt)}

-- Ale w naszym przykładzie ta JD nie zachodzi,
-- bo rekonstrukcja tworzy dodatkowe (błędne) krotki
```

### Definicja 5NF (PJNF - Project-Join Normal Form)

#### Formalna definicja:
**Relacja R jest w 5NF**, jeśli:
1. **Jest w 4NF**
2. **Każda zależność łączenia w R jest implikowana przez klucze kandydujące**

#### Alternatywna definicja:
```
R jest w 5NF, jeśli nie da się jej dalej zdekomponować 
bez straty informacji
```

### Przykłady naruszeń 5NF

#### Przykład 1: Agent-Firma-Produkt
```sql
CREATE TABLE SPRZEDAZ (
    agent VARCHAR(50),
    firma VARCHAR(50),
    produkt VARCHAR(50),
    PRIMARY KEY (agent, firma, produkt)
);

-- Reguła biznesowa:
-- Agent sprzedaje produkt firmie wtedy i tylko wtedy, gdy:
-- 1. Agent reprezentuje tę firmę
-- 2. Firma kupuje ten produkt  
-- 3. Agent sprzedaje ten produkt

-- Zależność łączenia:
-- ⋈{(agent, firma), (firma, produkt), (agent, produkt)}

-- Jeśli ta JD zachodzi, można zdekomponować:
AGENT_FIRMA(agent, firma)
FIRMA_PRODUKT(firma, produkt)  
AGENT_PRODUKT(agent, produkt)
```

#### Sprawdzenie dekompozycji:
```sql
-- Dane oryginalne:
SPRZEDAZ:
('A1', 'F1', 'P1')
('A1', 'F1', 'P2') 
('A1', 'F2', 'P1')
('A2', 'F1', 'P1')

-- Projekcje:
AGENT_FIRMA: ('A1','F1'), ('A1','F2'), ('A2','F1')
FIRMA_PRODUKT: ('F1','P1'), ('F1','P2'), ('F2','P1')
AGENT_PRODUKT: ('A1','P1'), ('A1','P2'), ('A2','P1')

-- JOIN projekcji:
A1 ⋈ F1 ⋈ P1: ✓ była w oryginale
A1 ⋈ F1 ⋈ P2: ✓ była w oryginale
A1 ⋈ F2 ⋈ P1: ✓ była w oryginale
A2 ⋈ F1 ⋈ P1: ✓ była w oryginale
A2 ⋈ F1 ⋈ P2: ❌ dodatkowa (błędna) krotka!

-- Dekompozycja stratna - naruszenie 5NF
```

### Algorytm sprawdzania 5NF

#### Krok 1: Sprawdź czy relacja jest w 4NF
```sql
-- Sprawdź wszystkie możliwe MVD
-- Jeśli są nietrywialne MVD, dekompozycja do 4NF
```

#### Krok 2: Sprawdź wszystkie możliwe dekompozycje trójstronne
```sql
-- Dla relacji R(A, B, C):
-- Sprawdź czy R = π_AB(R) ⋈ π_BC(R) ⋈ π_AC(R)
```

#### Krok 3: Generalizacja dla n-arnych dekompozycji
```sql
-- Sprawdź czy istnieją dalsze dekompozycje
-- które są bezstratne
```

### Przykład kompletnej normalizacji do 5NF

#### Wyjściowa relacja:
```sql
-- DOSTAWA(dostawca, magazyn, produkt, data)
CREATE TABLE DOSTAWA (
    dostawca VARCHAR(50),
    magazyn VARCHAR(50),
    produkt VARCHAR(50), 
    data DATE,
    PRIMARY KEY (dostawca, magazyn, produkt, data)
);
```

#### Analiza zależności:
```sql
-- Zależności funkcyjne (sprawdź 1NF-BCNF):
-- Brak nietrywianych FD oprócz klucza

-- Zależności wielowartościowe (sprawdź 4NF):
-- dostawca ↠ magazyn (dostawca dostarcza do określonych magazynów)
-- dostawca ↠ produkt (dostawca ma określone produkty)
-- Naruszenie 4NF!

-- Dekompozycja do 4NF:
DOSTAWCA_MAGAZYN(dostawca, magazyn)
DOSTAWCA_PRODUKT(dostawca, produkt)  
DOSTAWA_CZASOWO(dostawca, data)
```

#### Dalsze sprawdzenie 5NF:
```sql
-- Po dekompozycji do 4NF sprawdź czy można dalej:
-- Czy można bezstratnie zdekomponować którykolwiek z powstałych tabel?

-- DOSTAWCA_MAGAZYN - nie da się dalej (binarna)
-- DOSTAWCA_PRODUKT - nie da się dalej (binarna)  
-- DOSTAWA_CZASOWO - nie da się dalej (binarna)

-- Wynik: już w 5NF
```

## Praktyczne aspekty wyższych form normalnych

### 1. **Kiedy stosować 4NF/5NF**

#### Argumenty ZA:
```
✅ Eliminacja redundancji
✅ Eliminacja anomalii wstawiania/usuwania/aktualizacji
✅ Logiczna separacja niezależnych konceptów
✅ Łatwiejsze utrzymanie spójności
```

#### Argumenty PRZECIW:
```
❌ Więcej tabel = więcej JOIN'ów
❌ Gorsza wydajność zapytań
❌ Większa złożoność dla programistów
❌ Więcej kluczy obcych do zarządzania
```

### 2. **Wytyczne praktyczne**

#### Stosuj 4NF gdy:
```sql
-- Masz wyraźne zależności wielowartościowe
-- Dane są często aktualizowane  
-- Redundancja powoduje problemy
-- Logika biznesowa wymaga niezależności

-- Przykład: System CRM
KLIENT_KONTAKTY(klient, telefon)     -- 4NF
KLIENT_PRODUKTY(klient, produkt)     -- 4NF
-- Zamiast KLIENT_KONTAKTY_PRODUKTY  -- Naruszenie 4NF
```

#### Unikaj 4NF/5NF gdy:
```sql
-- System OLAP/raportowanie
-- Wydajność odczytu kluczowa
-- Rzadkie aktualizacje
-- Prostota implementacji ważniejsza

-- Przykład: Hurtownia danych
SPRZEDAZ_DENORM(data, produkt, klient, kwota, region, kategoria)
-- Denormalizacja dla wydajności analiz
```

### 3. **Strategie kompromisowe**

#### Częściowa normalizacja:
```sql
-- Normalizuj tabele transakcyjne (OLTP)
ZAMOWIENIA(id, data, klient_id)       -- 3NF/BCNF
POZYCJE(zamowienie_id, produkt_id)    -- 3NF/BCNF

-- Denormalizuj tabele analityczne (OLAP)  
SPRZEDAZ_MIESIĘCZNA(rok, miesiac, kategoria, kwota_total)  -- Denormalizacja
```

#### Indeksy pokrywające:
```sql
-- Zamiast dekompozycji do 4NF, użyj indeksów
CREATE INDEX idx_covering ON PSK(pracownik) INCLUDE (umiejetnosc, projekt);
-- Szybkie zapytania bez dodatkowych JOIN'ów
```

## Algorytmy i narzędzia

### 1. **Algorytm dekompozycji do 4NF**
```
INPUT: Relacja R, zbiór MVD M
OUTPUT: Dekompozycja do 4NF

1. IF R jest w 4NF THEN RETURN {R}
2. Znajdź nietrywialne MVD X ↠ Y w R  
3. Dekompozycja := {R1(X ∪ Y), R2(X ∪ (R - Y))}
4. Recursively decompose R1 and R2
5. RETURN union of decompositions
```

### 2. **Sprawdzanie zależności łączenia**
```
INPUT: Relacja R, podział {R1, R2, ..., Rn}
OUTPUT: Czy dekompozycja jest bezstratna

1. Oblicz projekcje: Pi := π_Ri(R) for all i
2. Oblicz złączenie: J := P1 ⋈ P2 ⋈ ... ⋈ Pn  
3. IF J = R THEN RETURN bezstratna
4. ELSE RETURN stratna
```

### 3. **Narzędzia wspomagające**
```
Akademickie:
- Normalization tools online
- Database design helpers
- MVD/JD analyzers

Komercyjne:
- ERwin - analiza zależności
- PowerDesigner - normalizacja
- Oracle SQL Developer Data Modeler
```

## Zaawansowane koncepty

### 1. **Zależności inkluzji**
```sql
-- Rozszerzenie poza 5NF
-- R1[A] ⊆ R2[B] oznacza, że każda wartość A w R1 
-- musi istnieć jako wartość B w R2

-- Przykład:
PRACOWNICY[id_dzialu] ⊆ DZIALY[id_dzialu]
-- Każdy pracownik musi należeć do istniejącego działu
```

### 2. **Zależności temporalne**
```sql
-- Zależności zmienne w czasie
-- X →t Y oznacza, że X determinuje Y w czasie t

-- Przykład: ceny produktów zmienne w czasie
PRODUKTY_HISTORIA(produkt, data, cena)
produkt, data → cena  -- W danym dniu produkt ma określoną cenę
```

### 3. **Zależności rozmyte (fuzzy)**
```sql
-- Zależności z niepewnością
-- X →α Y oznacza, że X determinuje Y z prawdopodobieństwem α

-- Zastosowanie w ML/AI dla predykcji
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**
1. **Analiza biznesowa** - zrozum semantykę danych
2. **Stopniowa normalizacja** - nie przeskakuj kroków
3. **Testowanie dekompozycji** - sprawdź bezstratność
4. **Dokumentacja** - zapisz uzasadnienie decyzji
5. **Monitoring wydajności** - mierz wpływ na performance

### ❌ **Złe praktyki:**
1. **Ślepa normalizacja** - bez analizy wymagań
2. **Ignorowanie wydajności** - normalizacja za wszelką cenę
3. **Brak testowania** - nie sprawdzanie JOIN'ów
4. **Over-engineering** - nadmierna złożoność
5. **Brak kompromisów** - rigid thinking

## Pułapki egzaminacyjne

### 1. **Różnice między formami normalnymi**
```
3NF: Brak zależności przechodnich (FD)
BCNF: Każdy determinant to klucz (FD)  
4NF: Brak nietrywianych MVD (MVD)
5NF: Brak nietrywianych JD (JD)
```

### 2. **MVD vs FD**
```
X → Y: jedna wartość Y dla każdej wartości X
X ↠ Y: zbiór wartości Y dla każdej wartości X

FD ⟹ MVD, ale MVD ⟹ FD
```

### 3. **Bezstratność dekompozycji**
```
4NF: Binarna dekompozycja zawsze bezstratna dla MVD
5NF: Trzeba sprawdzać bezstratność dla n-arnych dekompozycji
```

### 4. **Praktyczne zastosowanie**
```
4NF/5NF bardziej teoretyczne niż praktyczne
W rzeczywistości rzadko stosowane ze względu na wydajność
Ważne dla zrozumienia teorii normalizacji
```