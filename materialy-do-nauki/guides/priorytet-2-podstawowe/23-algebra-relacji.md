# Algebra relacji - operacje podstawowe

## Definicja algebry relacji

**Algebra relacji** to **formalny język zapytań** dla modelu relacyjnego, definiujący **zestaw operacji** na relacjach (tabelach), które pozwalają na tworzenie nowych relacji.

### Kluczowe cechy:
- **Matematyczna podstawa** - formalne definicje operacji
- **Zamkniętość** - wynik operacji to też relacja
- **Kompozycyjność** - można łączyć operacje
- **Podstawa SQL** - implementacja w rzeczywistych SZBD

## Przykładowe relacje

### Dane testowe:
```sql
-- Tabela Studenci
S = {
    (1, 'Jan', 'Kowalski', 'Informatyka'),
    (2, 'Anna', 'Nowak', 'Matematyka'),
    (3, 'Piotr', 'Wiśniewski', 'Informatyka'),
    (4, 'Maria', 'Kowalczyk', 'Fizyka')
}

-- Tabela Kursy
K = {
    ('BD101', 'Bazy Danych', 6),
    ('MAT201', 'Analiza Matematyczna', 8),
    ('INF301', 'Algorytmy', 6),
    ('FIZ101', 'Fizyka Ogólna', 4)
}

-- Tabela Oceny
O = {
    (1, 'BD101', 4.5),
    (1, 'INF301', 5.0),
    (2, 'MAT201', 4.0),
    (3, 'BD101', 3.5),
    (4, 'FIZ101', 4.5)
}
```

## Operacje podstawowe

### 1. **Selekcja (σ - Sigma)**

#### Definicja:
**σ_warunek(R)** - wybiera **wiersze** z relacji R spełniające zadany warunek.

#### Składnia:
```
σ_warunek(Relacja)
```

#### Przykłady:
```sql
-- Studenci z kierunku Informatyka
σ_kierunek='Informatyka'(S) = {
    (1, 'Jan', 'Kowalski', 'Informatyka'),
    (3, 'Piotr', 'Wiśniewski', 'Informatyka')
}

-- Kursy z więcej niż 6 ECTS
σ_ects>6(K) = {
    ('MAT201', 'Analiza Matematyczna', 8)
}

-- Oceny większe niż 4.0
σ_ocena>4.0(O) = {
    (1, 'BD101', 4.5),
    (1, 'INF301', 5.0),
    (4, 'FIZ101', 4.5)
}

-- Złożone warunki
σ_kierunek='Informatyka' ∧ nazwisko='Kowalski'(S) = {
    (1, 'Jan', 'Kowalski', 'Informatyka')
}
```

#### SQL equivalent:
```sql
SELECT * FROM Studenci WHERE kierunek = 'Informatyka';
SELECT * FROM Kursy WHERE ects > 6;
SELECT * FROM Oceny WHERE ocena > 4.0;
```

### 2. **Projekcja (π - Pi)**

#### Definicja:
**π_atrybuty(R)** - wybiera **kolumny** z relacji R, eliminując duplikaty.

#### Składnia:
```
π_lista_atrybutów(Relacja)
```

#### Przykłady:
```sql
-- Tylko imiona i nazwiska studentów
π_imie,nazwisko(S) = {
    ('Jan', 'Kowalski'),
    ('Anna', 'Nowak'),
    ('Piotr', 'Wiśniewski'),
    ('Maria', 'Kowalczyk')
}

-- Tylko kierunki (bez duplikatów)
π_kierunek(S) = {
    ('Informatyka'),
    ('Matematyka'),
    ('Fizyka')
}

-- Kombinacja selekcji i projekcji
π_imie,nazwisko(σ_kierunek='Informatyka'(S)) = {
    ('Jan', 'Kowalski'),
    ('Piotr', 'Wiśniewski')
}
```

#### SQL equivalent:
```sql
SELECT DISTINCT imie, nazwisko FROM Studenci;
SELECT DISTINCT kierunek FROM Studenci;
SELECT imie, nazwisko FROM Studenci WHERE kierunek = 'Informatyka';
```

### 3. **Iloczyn kartezjański (×)**

#### Definicja:
**R × S** - łączy **każdy wiersz** z relacji R z **każdym wierszem** z relacji S.

#### Przykład:
```sql
-- Małe relacje dla przykładu
A = {(1, 'a'), (2, 'b')}
B = {('x', 10), ('y', 20)}

A × B = {
    (1, 'a', 'x', 10),
    (1, 'a', 'y', 20),
    (2, 'b', 'x', 10),
    (2, 'b', 'y', 20)
}

-- Rozmiar: |A| × |B| = 2 × 2 = 4 wiersze
```

#### SQL equivalent:
```sql
SELECT * FROM A CROSS JOIN B;
-- lub starszy styl:
SELECT * FROM A, B;
```

### 4. **Złączenie (⋈)**

#### Definicja:
**R ⋈_warunek S** - iloczyn kartezjański z następującą selekcją według warunku.

#### Natural Join (⋈):
```sql
-- Automatyczne złączenie po wspólnych atrybutach
Studenci ⋈ Oceny  -- złączenie po id_studenta

Wynik = {
    (1, 'Jan', 'Kowalski', 'Informatyka', 'BD101', 4.5),
    (1, 'Jan', 'Kowalski', 'Informatyka', 'INF301', 5.0),
    (2, 'Anna', 'Nowak', 'Matematyka', 'MAT201', 4.0),
    (3, 'Piotr', 'Wiśniewski', 'Informatyka', 'BD101', 3.5),
    (4, 'Maria', 'Kowalczyk', 'Fizyka', 'FIZ101', 4.5)
}
```

#### Theta Join (⋈_θ):
```sql
-- Złączenie z określonym warunkiem
Studenci ⋈_Studenci.id=Oceny.id_studenta Oceny

-- Równoważne z:
σ_Studenci.id=Oceny.id_studenta(Studenci × Oceny)
```

#### SQL equivalent:
```sql
SELECT * FROM Studenci NATURAL JOIN Oceny;
SELECT * FROM Studenci JOIN Oceny ON Studenci.id = Oceny.id_studenta;
```

## Operacje zbiorowe

### 1. **Suma (∪)**

#### Definicja:
**R ∪ S** - wszystkie krotki należące do R **lub** S (bez duplikatów).

#### Warunki:
- Relacje muszą być **kompatybilne** (te same atrybuty)

#### Przykład:
```sql
-- Studenci Informatyki
Inf = σ_kierunek='Informatyka'(S) = {
    (1, 'Jan', 'Kowalski', 'Informatyka'),
    (3, 'Piotr', 'Wiśniewski', 'Informatyka')
}

-- Studenci Matematyki  
Mat = σ_kierunek='Matematyka'(S) = {
    (2, 'Anna', 'Nowak', 'Matematyka')
}

-- Suma
Inf ∪ Mat = {
    (1, 'Jan', 'Kowalski', 'Informatyka'),
    (2, 'Anna', 'Nowak', 'Matematyka'),
    (3, 'Piotr', 'Wiśniewski', 'Informatyka')
}
```

#### SQL equivalent:
```sql
SELECT * FROM Studenci WHERE kierunek = 'Informatyka'
UNION
SELECT * FROM Studenci WHERE kierunek = 'Matematyka';
```

### 2. **Przecięcie (∩)**

#### Definicja:
**R ∩ S** - krotki należące **jednocześnie** do R **i** S.

#### Przykład:
```sql
-- Studenci z wysokimi ocenami (>4.0)
Wysokie = π_id_studenta(σ_ocena>4.0(O)) = {(1), (4)}

-- Studenci z kierunku Informatyka
InfID = π_id(σ_kierunek='Informatyka'(S)) = {(1), (3)}

-- Przecięcie - studenci Informatyki z wysokimi ocenami
Wysokie ∩ InfID = {(1)}
```

#### SQL equivalent:
```sql
SELECT id FROM Studenci WHERE kierunek = 'Informatyka'
INTERSECT
SELECT id_studenta FROM Oceny WHERE ocena > 4.0;
```

### 3. **Różnica (-)**

#### Definicja:
**R - S** - krotki należące do R, ale **nie należące** do S.

#### Przykład:
```sql
-- Wszyscy studenci
WszyscyID = π_id(S) = {(1), (2), (3), (4)}

-- Studenci z ocenami
ZOcenamiID = π_id_studenta(O) = {(1), (2), (3), (4)}

-- Studenci bez ocen
BezOcen = WszyscyID - ZOcenamiID = {} -- W tym przypadku pusty zbiór
```

#### SQL equivalent:
```sql
SELECT id FROM Studenci
EXCEPT  -- lub MINUS w Oracle
SELECT id_studenta FROM Oceny;
```

## Operacje pochodne

### 1. **Dzielenie (÷)**

#### Definicja:
**R ÷ S** - krotki z R, które są powiązane ze **wszystkimi** krotkami z S.

#### Przykład:
```sql
-- StudentKurs(id_studenta, kod_kursu)
SK = {
    (1, 'BD101'), (1, 'INF301'),
    (2, 'MAT201'),
    (3, 'BD101')
}

-- KursyObowiazkowe(kod_kursu)
Obowiazkowe = {('BD101'), ('INF301')}

-- Studenci którzy mają WSZYSTKIE obowiązkowe kursy
SK ÷ Obowiazkowe = {(1)}  -- Tylko student 1 ma oba kursy
```

#### SQL equivalent (złożone zapytanie):
```sql
SELECT id_studenta 
FROM StudentKurs sk1
WHERE NOT EXISTS (
    SELECT kod_kursu FROM KursyObowiazkowe ko
    WHERE NOT EXISTS (
        SELECT * FROM StudentKurs sk2 
        WHERE sk2.id_studenta = sk1.id_studenta 
          AND sk2.kod_kursu = ko.kod_kursu
    )
);
```

### 2. **Outer Join**

#### Left Outer Join (⟕):
```sql
-- Wszyscy studenci + ich oceny (jeśli są)
Studenci ⟕ Oceny = {
    (1, 'Jan', 'Kowalski', 'Informatyka', 'BD101', 4.5),
    (1, 'Jan', 'Kowalski', 'Informatyka', 'INF301', 5.0),
    (2, 'Anna', 'Nowak', 'Matematyka', 'MAT201', 4.0),
    (3, 'Piotr', 'Wiśniewski', 'Informatyka', 'BD101', 3.5),
    (4, 'Maria', 'Kowalczyk', 'Fizyka', 'FIZ101', 4.5)
}
-- Gdyby ktoś nie miał ocen: (id, imie, nazwisko, kierunek, NULL, NULL)
```

#### SQL equivalent:
```sql
SELECT * FROM Studenci LEFT JOIN Oceny ON Studenci.id = Oceny.id_studenta;
```

## Operacje agregujące

### Grupowanie (γ):
```sql
-- Średnia ocena per student
γ_id_studenta; AVG(ocena)(O) = {
    (1, 4.75),  -- (4.5 + 5.0) / 2
    (2, 4.0),
    (3, 3.5),
    (4, 4.5)
}

-- Liczba studentów per kierunek
γ_kierunek; COUNT(*)(S) = {
    ('Informatyka', 2),
    ('Matematyka', 1),
    ('Fizyka', 1)
}
```

#### SQL equivalent:
```sql
SELECT id_studenta, AVG(ocena) FROM Oceny GROUP BY id_studenta;
SELECT kierunek, COUNT(*) FROM Studenci GROUP BY kierunek;
```

## Optymalizacja wyrażeń

### 1. **Przepychanie selekcji**
```sql
-- ❌ Nieoptymalne
π_nazwa((σ_ects>6(K)) ⋈ (σ_ocena>4.0(O)))

-- ✅ Optymalne - selekcja wcześniej
π_nazwa(σ_ects>6(K) ⋈ σ_ocena>4.0(O))
```

### 2. **Przepychanie projekcji**
```sql
-- ❌ Nieoptymalne
π_imie,nazwisko(S ⋈ O)

-- ✅ Optymalne - ograniczamy kolumny wcześniej
π_imie,nazwisko(π_id,imie,nazwisko(S) ⋈ π_id_studenta(O))
```

### 3. **Łączenie operacji**
```sql
-- Zamiast wielu selekcji
σ_warunek1(σ_warunek2(R))

-- Jedna selekcja
σ_warunek1 ∧ warunek2(R)
```

## Równoważności wyrażeń

### Komutywność:
```
R ∪ S ≡ S ∪ R
R ∩ S ≡ S ∩ R  
R ⋈ S ≡ S ⋈ R
R × S ≡ S × R
```

### Łączność:
```
(R ∪ S) ∪ T ≡ R ∪ (S ∪ T)
(R ⋈ S) ⋈ T ≡ R ⋈ (S ⋈ T)
```

### Dystrybucja:
```
σ_warunek(R ∪ S) ≡ σ_warunek(R) ∪ σ_warunek(S)
σ_warunek(R ∩ S) ≡ σ_warunek(R) ∩ σ_warunek(S)
```

### Dekompozycja selekcji:
```
σ_warunek1 ∧ warunek2(R) ≡ σ_warunek1(σ_warunek2(R))
```

## Złożone przykłady

### 1. **Studenci którzy mają wszystkie kursy z Informatyki**
```sql
-- Krok 1: Kursy z Informatyki (zakładając dodatkowy atrybut)
KursyInf = π_kod_kursu(σ_kierunek='Informatyka'(Kursy))

-- Krok 2: Student-Kurs pary
StudentKurs = π_id_studenta,kod_kursu(Studenci ⋈ Oceny)

-- Krok 3: Dzielenie
StudentKurs ÷ KursyInf
```

### 2. **Najlepsi studenci z każdego kierunku**
```sql
-- Krok 1: Średnie oceny studentów
SrednOceny = γ_id_studenta; AVG(ocena) as srednia(Oceny)

-- Krok 2: Połącz ze studentami
StudSrednie = Studenci ⋈ SrednOceny

-- Krok 3: Maksymalne średnie per kierunek  
MaxPerKier = γ_kierunek; MAX(srednia) as max_srednia(StudSrednie)

-- Krok 4: Znajdź studentów z maksymalnymi średnimi
StudSrednie ⋈_kierunek=kierunek ∧ srednia=max_srednia MaxPerKier
```

### 3. **Studenci bez żadnych ocen**
```sql
-- Wszyscy studenci
WszyscyStud = π_id(Studenci)

-- Studenci z ocenami
StudZOcenami = π_id_studenta(Oceny)

-- Różnica
BezOcen = WszyscyStud - StudZOcenami

-- Połącz z danymi studentów
π_imie,nazwisko(Studenci ⋈_id=id BezOcen)
```

## Praktyczne zastosowania

### Query optimization:
```sql
-- Oryginalny SQL
SELECT s.imie, s.nazwisko
FROM Studenci s, Oceny o, Kursy k  
WHERE s.id = o.id_studenta 
  AND o.kod_kursu = k.kod_kursu
  AND s.kierunek = 'Informatyka'
  AND k.ects > 5;

-- Algebra relacji (optymalizacja)
π_imie,nazwisko(
    σ_kierunek='Informatyka'(Studenci) ⋈ 
    Oceny ⋈ 
    σ_ects>5(Kursy)
)
```

### Database design:
```sql
-- Sprawdzenie czy relacja jest w 3NF
-- przez analizę zależności funkcyjnych w algebrze relacji
```

## Implementacja w SQL

### Mapowanie operacji:
```sql
-- Algebra relacji → SQL
σ_warunek(R)           → SELECT * FROM R WHERE warunek
π_atrybuty(R)          → SELECT DISTINCT atrybuty FROM R  
R ∪ S                  → SELECT * FROM R UNION SELECT * FROM S
R ∩ S                  → SELECT * FROM R INTERSECT SELECT * FROM S
R - S                  → SELECT * FROM R EXCEPT SELECT * FROM S
R ⋈ S                  → SELECT * FROM R NATURAL JOIN S
R ⋈_warunek S          → SELECT * FROM R JOIN S ON warunek
γ_attr; AGG(R)         → SELECT attr, AGG(*) FROM R GROUP BY attr
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**
1. **Push down selekcje** - filtruj dane wcześnie
2. **Push down projekcje** - ograniczaj kolumny wcześnie  
3. **Używaj indeksów** - selekcje na indeksowanych kolumnach
4. **Analizuj koszty** - różne kolejności złączeń
5. **Unikaj iloczynów kartezjańskich** - zawsze z warunkami

### ❌ **Złe praktyki:**
1. **Późne filtrowanie** - selekcje po kosztownych złączeniach
2. **Niepotrzebne kolumny** - projekcje zbyt późno
3. **Złożone warunki** - zamiast prostych selekcji
4. **Ignorowanie optymalizatora** - nie sprawdzanie planów wykonania

## Pułapki egzaminacyjne

### 1. **Różnice między operacjami**
- **Selekcja (σ)**: Wybiera wiersze
- **Projekcja (π)**: Wybiera kolumny  
- **Złączenie (⋈)**: Łączy relacje
- **Iloczyn (×)**: Wszystkie kombinacje

### 2. **UNION vs JOIN**
- **UNION**: Łączy wiersze (operacja zbiorowa)
- **JOIN**: Łączy kolumny (operacja relacyjna)

### 3. **Natural Join vs Theta Join**
- **Natural**: Automatycznie po wspólnych atrybutach
- **Theta**: Z podanym warunkiem

### 4. **Optymalizacja**
- Wcześniejsze filtrowanie = lepsza wydajność
- Kolejność złączeń ma znaczenie
- Indeksy wpływają na koszt operacji