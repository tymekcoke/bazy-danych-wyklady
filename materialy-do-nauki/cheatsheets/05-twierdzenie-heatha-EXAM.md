# 📐 TWIERDZENIE HEATHA - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Twierdzenie Heatha dotyczy bezstratnej dekompozycji relacji w procesie normalizacji. Mówi ono, że dekompozycja relacji R na relacje R1 i R2 jest bezstratna wtedy i tylko wtedy, gdy jeden z następujących warunków jest spełniony:

R1 ∩ R2 → R1 lub R1 ∩ R2 → R2

Oznacza to, że przecięcie atrybutów R1 i R2 musi funkcyjnie determinować wszystkie atrybuty jednej z tych relacji. To jest kluczowe dla zachowania informacji podczas normalizacji."

## ✍️ CO NAPISAĆ NA KARTCE

```
TWIERDZENIE HEATHA - BEZSTRATNA DEKOMPOZYCJA

WARUNEK:
Dekompozycja R → (R1, R2) jest bezstratna ⟺ 
R1 ∩ R2 → R1 lub R1 ∩ R2 → R2

PRZYKŁAD:
R(A,B,C,D) z FD: A → BC

Dekompozycja: R1(A,B,C), R2(A,D)
R1 ∩ R2 = {A}
Sprawdzenie: A → ABC? NIE, ale A → BC ⊆ R1 ✓
Więc A → R1? NIE (brakuje A→A)
Ale A jest kluczem w R1, więc warunek spełniony ✓

TEST BEZSTRATNOŚCI - ALGORYTM:
1. Utworzyć tabelę z wierszami = liczba relacji w dekompozycji  
2. Kolumny = atrybuty oryginalnej relacji
3. Wypełnić aij gdy atrybut Aj ∈ Ri, bjk w przeciwnym razie
4. Dla każdej FD X→Y: jeśli dwa wiersze zgodne na X, zrównać na Y
5. Jeśli powstanie wiersz z samymi aii - dekompozycja bezstratna

PRZYKŁAD TESTU:
R(A,B,C) → R1(A,B), R2(A,C) z FD: A→B
       A   B   C
R1:   a11 a12 b13
R2:   a21 b22 a23

A→B: a11=a21 więc a12=b22 → a12
       A   B   C  
R1:   a11 a12 b13
R2:   a11 a12 a23

Nie ma wiersza (a11,a12,a13) więc NIE bezstratna
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- PRZYKŁAD BEZSTRATNEJ DEKOMPOZYCJI
-- Oryginalna relacja z problemem (nie 3NF)
CREATE TABLE pracownicy_projekty_original (
    id_pracownika INT,
    imie VARCHAR(50),
    nazwisko VARCHAR(50), 
    id_projektu INT,
    nazwa_projektu VARCHAR(100),
    stawka_godzinowa DECIMAL(10,2),
    -- FD: id_pracownika → imie, nazwisko, stawka_godzinowa
    -- FD: id_projektu → nazwa_projektu
);

-- DEKOMPOZYCJA WEDŁUG HEATHA
-- R1 ∩ R2 = {id_pracownika}, {id_projektu}

-- Tabela pracowników (R1)
CREATE TABLE pracownicy (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    stawka_godzinowa DECIMAL(10,2)
);

-- Tabela projektów (R2)  
CREATE TABLE projekty (
    id_projektu INT PRIMARY KEY,
    nazwa_projektu VARCHAR(100)
);

-- Tabela łącząca (R3) - związek M:N
CREATE TABLE pracownik_projekt (
    id_pracownika INT,
    id_projektu INT,
    PRIMARY KEY (id_pracownika, id_projektu),
    FOREIGN KEY (id_pracownika) REFERENCES pracownicy(id_pracownika),
    FOREIGN KEY (id_projektu) REFERENCES projekty(id_projektu)
);

-- SPRAWDZENIE BEZSTRATNOŚCI - złączenie naturalne
-- Powinno zwrócić oryginalną relację
SELECT p.id_pracownika, p.imie, p.nazwisko, p.stawka_godzinowa,
       pr.id_projektu, pr.nazwa_projektu  
FROM pracownicy p
NATURAL JOIN pracownik_projekt pp
NATURAL JOIN projekty pr;

-- PRZYKŁAD STRATNEJ DEKOMPOZYCJI (ZŁE!)
-- Dekompozycja bez wspólnego klucza
CREATE TABLE pracownicy_dane (
    imie VARCHAR(50),
    nazwisko VARCHAR(50)
);

CREATE TABLE projekty_stawki (
    nazwa_projektu VARCHAR(100),
    stawka_godzinowa DECIMAL(10,2)
);
-- Brak wspólnego atrybutu → nie można odtworzyć oryginalnej relacji!
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Przecięcie R1 ∩ R2 musi determinować CAŁĄ relację R1 lub R2
2. **UWAGA**: Heath dotyczy dekompozycji na 2 relacje (nie więcej!)
3. **BŁĄD**: Mylenie z warunkami 3NF czy BCNF
4. **PAMIĘTAĆ**: Bezstratność ≠ zachowanie zależności funkcyjnych
5. **WAŻNE**: Test tabeliczny zawsze działa, formuła tylko dla 2 relacji

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Lossless decomposition** - dekompozycja bezstratna
- **Heath's theorem** - twierdzenie Heatha
- **Functional dependency** - zależność funkcyjna
- **Natural join** - złączenie naturalne  
- **Intersection** - przecięcie relacji
- **Determinant** - determinanta w FD
- **Tabular test** - test tabeliczny
- **Decomposition** - dekompozycja

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **19-normalizacja** - zastosowanie w normalizacji
- **27-zaleznosci-funkcyjne** - podstawa twierdzenia
- **21-sql-joiny** - Natural JOIN do sprawdzenia
- **26-model-relacyjny** - teoria dekompozycji
- **28-normalizacja-zaawansowana** - BCNF i wyższe postacie