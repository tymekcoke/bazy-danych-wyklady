# Model relacyjny - podstawy teoretyczne

## Definicja modelu relacyjnego

**Model relacyjny** to **matematyczny model danych** oparty na **teorii zbiorów** i **logice predykatów pierwszego rzędu**, w którym dane są reprezentowane jako **relacje (tabele)**.

### Kluczowe cechy:
- **Matematyczne podstawy** - teoria zbiorów i algebra relacji
- **Struktura tabelaryczna** - dane w wierszach i kolumnach
- **Prostota konceptualna** - łatwy do zrozumienia
- **Niezależność danych** - separacja logicznego i fizycznego poziomu

### Historia:
- **Twórca**: Edgar F. Codd (IBM, 1970)
- **Artykuł**: "A Relational Model of Data for Large Shared Data Banks"
- **Rewolucja**: Zastąpienie hierarchicznych i sieciowych modeli
- **Język**: SQL jako implementacja algebry relacji

## Podstawowe pojęcia

### 1. **Domena (Domain)**

#### Definicja:
**Domena** to **zbiór wszystkich możliwych wartości** dla danego atrybutu.

#### Przykłady:
```sql
-- Domenы podstawowe
D_liczby_całkowite = {..., -2, -1, 0, 1, 2, ...}
D_dni_tygodnia = {Poniedziałek, Wtorek, Środa, Czwartek, Piątek, Sobota, Niedziela}
D_oceny = {2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0}
D_płeć = {M, K}

-- Domeny złożone
D_email = {tekst zawierający @ i domenę}
D_telefon = {ciąg 9 cyfr w formacie XXX-XXX-XXX}
D_pesel = {ciąg 11 cyfr spełniający algorytm kontrolny}
```

#### Własności domen:
```
1. ATOMOWOŚĆ - każda wartość w domenie jest niepodzielna
2. SKOŃCZONOŚĆ - praktycznie każda domena ma skończoną liczbę możliwych wartości
3. TYPOWANIE - każda domena ma określony typ danych
```

### 2. **Relacja (Relation)**

#### Definicja matematyczna:
**Relacja R** nad domenami D₁, D₂, ..., Dₙ to **podzbiór iloczynu kartezjańskiego** tych domen:
```
R ⊆ D₁ × D₂ × ... × Dₙ
```

#### Przykład:
```sql
-- Domeny
D_imiona = {Jan, Anna, Piotr, Maria}
D_nazwiska = {Kowalski, Nowak, Wiśniewski}
D_wiek = {18, 19, 20, ..., 100}

-- Iloczyn kartezjański (wszystkie możliwe kombinacje)
D_imiona × D_nazwiska × D_wiek = 
{(Jan, Kowalski, 18), (Jan, Kowalski, 19), ..., (Maria, Wiśniewski, 100)}

-- Relacja STUDENCI (podzbiór iloczynu kartezjańskiego)
STUDENCI = {
    (Jan, Kowalski, 20),
    (Anna, Nowak, 19),
    (Piotr, Wiśniewski, 21)
}
```

### 3. **Krotka (Tuple)**

#### Definicja:
**Krotka** to **pojedynczy element relacji** - uporządkowana lista wartości z odpowiednich domen.

```sql
-- Przykładowe krotki
t₁ = (Jan, Kowalski, 20)
t₂ = (Anna, Nowak, 19) 
t₃ = (Piotr, Wiśniewski, 21)

-- Każda krotka należy do iloczynu kartezjańskiego domen
t₁ ∈ D_imiona × D_nazwiska × D_wiek
```

### 4. **Atrybut (Attribute)**

#### Definicja:
**Atrybut** to **nazwana kolumna** w relacji, powiązana z określoną domeną.

```sql
-- Schemat relacji z atrybutami
STUDENCI(
    imie: D_imiona,
    nazwisko: D_nazwiska, 
    wiek: D_wiek
)

-- Dostęp do wartości atrybutu w krotce
t₁[imie] = Jan
t₁[nazwisko] = Kowalski
t₁[wiek] = 20
```

### 5. **Schemat relacji (Relation Schema)**

#### Definicja:
**Schemat relacji** R(A₁:D₁, A₂:D₂, ..., Aₙ:Dₙ) to **definicja struktury** relacji określająca:
- Nazwę relacji R
- Listę atrybutów A₁, A₂, ..., Aₙ
- Domeny atrybutów D₁, D₂, ..., Dₙ

```sql
-- Przykłady schematów
STUDENCI(nr_indeksu: INTEGER, imie: VARCHAR(50), nazwisko: VARCHAR(50), wiek: INTEGER)
KURSY(kod: VARCHAR(10), nazwa: VARCHAR(100), ects: INTEGER)
OCENY(nr_indeksu: INTEGER, kod_kursu: VARCHAR(10), ocena: DECIMAL(3,2))
```

### 6. **Instancja relacji (Relation Instance)**

#### Definicja:
**Instancja relacji** to **konkretny zbiór krotek** zgodnych ze schematem relacji w danym momencie czasu.

```sql
-- Schemat
STUDENCI(nr_indeksu: INTEGER, imie: VARCHAR(50), nazwisko: VARCHAR(50))

-- Instancja w czasie T₁
STUDENCI_T1 = {
    (123456, Jan, Kowalski),
    (234567, Anna, Nowak),
    (345678, Piotr, Wiśniewski)
}

-- Instancja w czasie T₂ (po dodaniu studenta)
STUDENCI_T2 = {
    (123456, Jan, Kowalski),
    (234567, Anna, Nowak),
    (345678, Piotr, Wiśniewski),
    (456789, Maria, Kowalczyk)
}
```

## Właściwości relacji

### 1. **Unikalność krotek**
```
W relacji nie mogą występować identyczne krotki
R = {t₁, t₂, t₃} gdzie t₁ ≠ t₂ ≠ t₃

❌ NIEPRAWIDŁOWE:
STUDENCI = {
    (Jan, Kowalski, 20),
    (Jan, Kowalski, 20)  ← Duplikat!
}

✅ PRAWIDŁOWE:
STUDENCI = {
    (Jan, Kowalski, 20),
    (Anna, Nowak, 19)
}
```

### 2. **Brak porządku krotek**
```
Relacja to ZBIÓR krotek - porządek nie ma znaczenia

R₁ = {(Jan, Kowalski), (Anna, Nowak)}
R₂ = {(Anna, Nowak), (Jan, Kowalski)}

R₁ = R₂  ← To są identyczne relacje!
```

### 3. **Znaczenie porządku atrybutów**
```
Krotka to LISTA wartości - porządek ma znaczenie

t₁ = (Jan, Kowalski) ≠ (Kowalski, Jan) = t₂

Ale w praktyce używamy nazw atrybutów:
t₁[imie] = Jan, t₁[nazwisko] = Kowalski
```

### 4. **Atomowość wartości**
```
Każda wartość w komórce musi być ATOMOWA (niepodzielna)

❌ NIEPRAWIDŁOWE (nie-atomowe):
PRACOWNIK = {
    (Jan, {123-456-789, 987-654-321}, Kowalski)  ← Zbiór telefonów
}

✅ PRAWIDŁOWE (atomowe):
TELEFONY = {
    (Jan, 123-456-789),
    (Jan, 987-654-321)
}
```

## Klucze w modelu relacyjnym

### 1. **Superklucz (Superkey)**

#### Definicja:
**Superklucz** to **zbiór atrybutów**, który **jednoznacznie identyfikuje** każdą krotkę w relacji.

```sql
-- Relacja STUDENCI(nr_indeksu, imie, nazwisko, email)
Przykładowe superklucze:
- {nr_indeksu}
- {email}  
- {nr_indeksu, imie}
- {nr_indeksu, imie, nazwisko}
- {nr_indeksu, imie, nazwisko, email}

Wszystkie zawierają wystarczającą informację do identyfikacji krotki
```

### 2. **Klucz kandydujący (Candidate Key)**

#### Definicja:
**Klucz kandydujący** to **minimalny superklucz** - nie można z niego usunąć żadnego atrybutu bez utraty właściwości jednoznacznej identyfikacji.

```sql
-- Z poprzednich superklucze:
{nr_indeksu}           ← KLUCZ KANDYDUJĄCY (minimalny)
{email}                ← KLUCZ KANDYDUJĄCY (minimalny)
{nr_indeksu, imie}     ← SUPERKLUCZ (nie minimalny, można usunąć imie)
{nr_indeksu, nazwisko} ← SUPERKLUCZ (nie minimalny, można usunąć nazwisko)
```

### 3. **Klucz główny (Primary Key)**

#### Definicja:
**Klucz główny** to **wybrany klucz kandydujący**, który będzie główną metodą identyfikacji krotek.

```sql
-- Wybór klucza głównego
STUDENCI(
    nr_indeksu INTEGER PRIMARY KEY,  ← Wybrany jako klucz główny
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    email VARCHAR(100) UNIQUE        ← Dalej klucz kandydujący, ale nie główny
);
```

### 4. **Klucz obcy (Foreign Key)**

#### Definicja:
**Klucz obcy** to **atrybut (lub zbiór atrybutów)** w jednej relacji, który **referencuje klucz główny** innej relacji.

```sql
-- Relacja nadrzędna
DZIALY(id_dzialu PRIMARY KEY, nazwa)

-- Relacja podrzędna z kluczem obcym
PRACOWNICY(
    id_pracownika INTEGER PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    id_dzialu INTEGER,
    FOREIGN KEY (id_dzialu) REFERENCES DZIALY(id_dzialu)
);
```

## Ograniczenia integralności

### 1. **Ograniczenia domeny**
```sql
-- Wartości muszą należeć do odpowiedniej domeny
CREATE TABLE STUDENCI (
    nr_indeksu INTEGER CHECK (nr_indeksu > 0),
    imie VARCHAR(50) NOT NULL,
    wiek INTEGER CHECK (wiek BETWEEN 18 AND 100),
    ocena DECIMAL(3,2) CHECK (ocena IN (2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0))
);
```

### 2. **Ograniczenia encji (Entity Integrity)**
```sql
-- Klucz główny nie może być NULL
PRIMARY KEY (atrybut) IMPLIES atrybut NOT NULL

-- Automatycznie zapewnione przez SZBD
CREATE TABLE STUDENCI (
    nr_indeksu INTEGER PRIMARY KEY,  -- Automatycznie NOT NULL
    imie VARCHAR(50)
);
```

### 3. **Ograniczenia referencyjne (Referential Integrity)**
```sql
-- Klucz obcy musi referencować istniejący klucz główny
FOREIGN KEY (klucz_obcy) REFERENCES TabeleNadrzedna(klucz_główny)

-- Możliwe akcje przy naruszeniu:
ON DELETE CASCADE      -- Usuń podrzędne
ON DELETE SET NULL     -- Ustaw NULL w podrzędnych  
ON DELETE RESTRICT     -- Zabroń usunięcia
ON UPDATE CASCADE      -- Aktualizuj podrzędne
```

### 4. **Ograniczenia biznesowe**
```sql
-- Niestandardowe reguły biznesowe
CREATE TABLE PRACOWNICY (
    id INTEGER PRIMARY KEY,
    pensja DECIMAL(10,2),
    premia DECIMAL(10,2),
    CHECK (premia <= pensja * 0.5)  -- Premia max 50% pensji
);

-- Ograniczenia międzytabelowe
CREATE ASSERTION SumaPensji 
CHECK (
    (SELECT SUM(pensja) FROM PRACOWNICY) <= 
    (SELECT budzet FROM FIRMA WHERE id = 1)
);
```

## Normalizacja w modelu relacyjnym

### Formy normalne jako właściwości relacji:

#### 1NF - Pierwsza Postać Normalna:
```
Relacja jest w 1NF jeśli:
- Wszystkie atrybuty są atomowe
- Nie ma powtarzających się grup

❌ NIE-1NF:
ZAMOWIENIA(id, klient, produkty)
gdzie produkty = "laptop, mysz, klawiatura"

✅ 1NF:
ZAMOWIENIA(id, klient)
POZYCJE(id_zamowienia, produkt)
```

#### 2NF - Druga Postać Normalna:
```
Relacja jest w 2NF jeśli:
- Jest w 1NF
- Każdy atrybut niekluczowy jest w pełni zależny od klucza głównego

❌ NIE-2NF:
OCENY(nr_studenta, kod_kursu, ocena, imie_studenta)
gdzie imie_studenta zależy tylko od nr_studenta

✅ 2NF:
STUDENCI(nr_studenta, imie_studenta)
OCENY(nr_studenta, kod_kursu, ocena)
```

#### 3NF - Trzecia Postać Normalna:
```
Relacja jest w 3NF jeśli:
- Jest w 2NF  
- Nie ma zależności przechodnich

❌ NIE-3NF:
PRACOWNICY(id, imie, id_dzialu, nazwa_dzialu)
gdzie id → id_dzialu → nazwa_dzialu (przechodnia)

✅ 3NF:
DZIALY(id_dzialu, nazwa_dzialu)
PRACOWNICY(id, imie, id_dzialu)
```

## Algebra relacji jako fundament

### Operacje podstawowe:

#### 1. **Selekcja (σ)**
```
σ_warunek(R) = {t ∈ R | warunek(t) = true}

σ_wiek>20(STUDENCI) = wszystkie krotki gdzie wiek > 20
```

#### 2. **Projekcja (π)**
```
π_A1,A2,...,An(R) = {t[A1,A2,...,An] | t ∈ R}

π_imie,nazwisko(STUDENCI) = tylko kolumny imie i nazwisko
```

#### 3. **Iloczyn kartezjański (×)**
```
R × S = {(r,s) | r ∈ R ∧ s ∈ S}

STUDENCI × KURSY = każdy student połączony z każdym kursem
```

#### 4. **Suma (∪)**
```
R ∪ S = {t | t ∈ R ∨ t ∈ S}

Wymaga zgodności schematów: dom(R) = dom(S)
```

#### 5. **Różnica (-)**
```
R - S = {t | t ∈ R ∧ t ∉ S}

WSZYSCY_STUDENCI - STUDENCI_Z_OCENAMAMI = studenci bez ocen
```

#### 6. **Przecięcie (∩)**
```
R ∩ S = {t | t ∈ R ∧ t ∈ S}

Może być wyrażone przez inne operacje: R ∩ S = R - (R - S)
```

## Rachunek relacji

### Rachunek krotek z zmiennymi wiązanymi:
```sql
-- Formalna notacja
{t | P(t)}

-- gdzie:
-- t - zmienna krotkowa
-- P(t) - formuła predykatowa

-- Przykład: Studenci starsi niż 20 lat
{t | t ∈ STUDENCI ∧ t[wiek] > 20}

-- SQL equivalent:
SELECT * FROM STUDENCI WHERE wiek > 20;
```

### Rachunek krotek z zmiennymi swobodnymi:
```sql
-- Znajdź imiona studentów zapisanych na kurs "Bazy Danych"
{t[imie] | t ∈ STUDENCI ∧ ∃s(s ∈ OCENY ∧ s[nr_studenta] = t[nr_studenta] 
                            ∧ ∃k(k ∈ KURSY ∧ k[kod] = s[kod_kursu] 
                                 ∧ k[nazwa] = "Bazy Danych"))}

-- SQL equivalent:
SELECT s.imie 
FROM STUDENCI s
JOIN OCENY o ON s.nr_indeksu = o.nr_studenta
JOIN KURSY k ON o.kod_kursu = k.kod
WHERE k.nazwa = 'Bazy Danych';
```

### Rachunek domenowy:
```sql
-- Zmienne domenowe zamiast krotkowych
{⟨x₁, x₂, ..., xₙ⟩ | P(x₁, x₂, ..., xₙ)}

-- Przykład: Studenci z oceną 5.0
{⟨i, n⟩ | ∃s, k, o (STUDENCI(s, i, n) ∧ OCENY(s, k, o) ∧ o = 5.0)}
```

## Implementacja modelu relacyjnego

### 1. **Reprezentacja fizyczna**
```
LOGICZNY POZIOM (Model relacyjny):
- Relacje jako tabele
- Krotki jako wiersze  
- Atrybuty jako kolumny

FIZYCZNY POZIOM (Implementacja):
- Strony/bloki danych
- Indeksy B-tree
- Tablespaces
- Partycjonowanie
```

### 2. **Optymalizacja dostępu**
```sql
-- Indeksy jako implementacja szybkiego dostępu
CREATE INDEX idx_nazwisko ON STUDENCI(nazwisko);

-- Klastry jako fizyczne grupowanie
CLUSTER STUDENCI USING idx_nazwisko;

-- Partycjonowanie jako podział danych
CREATE TABLE SPRZEDAZ (...) 
PARTITION BY RANGE (data_sprzedazy);
```

### 3. **Ograniczenia wydajnościowe**
```
TEORIA vs PRAKTYKA:

TEORIA:
- Nieskończone domeny
- Nieograniczone rozmiary relacji
- Idealna atomowość

PRAKTYKA:
- Ograniczone typy danych (VARCHAR(255))
- Limity rozmiaru tabel
- Kompromisy wydajnościowe (denormalizacja)
```

## Rozszerzenia modelu relacyjnego

### 1. **NULL values**
```sql
-- Rozszerzenie logiki dwuwartościowej do trójwartościowej
TRUE, FALSE, UNKNOWN

-- Wpływ na operacje
NULL = NULL     → UNKNOWN
NULL + 5        → NULL
COUNT(kolumna)  → ignoruje NULL
```

### 2. **Obiekto-relacyjne rozszerzenia**
```sql
-- Typy zdefiniowane przez użytkownika
CREATE TYPE ADRES AS (
    ulica VARCHAR(100),
    numer VARCHAR(10),
    miasto VARCHAR(50)
);

-- Atrybuty złożone
CREATE TABLE PRACOWNICY (
    id INTEGER,
    adres ADRES
);
```

### 3. **XML i JSON**
```sql
-- Przechowywanie semi-strukturalnych danych
CREATE TABLE DOKUMENTY (
    id INTEGER,
    dane JSON,
    metadane XML
);

-- Zapytania
SELECT dane->>'nazwa' FROM DOKUMENTY WHERE id = 1;
```

## Najlepsze praktyki projektowania

### ✅ **Dobre praktyki:**

#### 1. **Właściwe klucze**
```sql
✅ DOBRE:
- Klucze surogatowe dla stabilności
- Klucze naturalne gdzie sensowne
- Indeksy na kluczach obcych

❌ ZŁŻE:
- Złożone klucze naturalne (imie + nazwisko)
- Brak indeksów na JOIN'ach
```

#### 2. **Ograniczenia integralności**
```sql
✅ DOBRE:
- NOT NULL gdzie wymagane
- CHECK constraints dla domen
- FOREIGN KEYs dla spójności

❌ ZŁŻE:
- Brak ograniczeń (walidacja tylko w aplikacji)
- Zbyt restrykcyjne ograniczenia
```

#### 3. **Normalizacja vs wydajność**
```sql
✅ BALANS:
- 3NF dla OLTP
- Kontrolowana denormalizacja dla OLAP
- Indeksy pokrywające dla częstych zapytań

❌ EKSTREMUM:
- Pełna normalizacja kosztem wydajności
- Pełna denormalizacja kosztem spójności
```

### ❌ **Złe praktyki:**

#### 1. **Naruszenie teorii**
```sql
❌ ZŁŻE:
- Przechowywanie wielu wartości w jednej kolumnie
- Brak kluczy głównych  
- Duplikaty krotek
```

#### 2. **Ignorowanie ograniczeń**
```sql
❌ ZŁŻE:
- Brak walidacji na poziomie bazy
- Założenia o "dobrych" danych z aplikacji
- Ignorowanie kluczy obcych
```

## Pułapki egzaminacyjne

### 1. **Terminologia**
```
RELACJA ≠ TABELA (ale w praktyce używane zamiennie)
KROTKA ≠ REKORD (ale konceptualnie podobne)
ATRYBUT ≠ KOLUMNA (ale reprezentowane tak samo)
```

### 2. **Właściwości relacji**
```
- Brak duplikatów krotek (zbiór, nie multi-zbiór)
- Brak porządku krotek (zbiór, nie lista)
- Atomowość wartości (1NF)
- Każdy atrybut ma domenę
```

### 3. **Klucze**
```
SUPERKLUCZ ⊃ KLUCZ KANDYDUJĄCY ⊃ KLUCZ GŁÓWNY

- Każdy klucz kandydujący to superklucz
- Klucz główny to wybrany klucz kandydujący
- Może być wiele kluczy kandydujących
```

### 4. **Algebra vs SQL**
```
ALGEBRA RELACJI = teoretyczne podstawy
SQL = praktyczna implementacja

- Różnice w obsłudze NULL
- Różnice w duplikatach (DISTINCT)
- Rozszerzenia SQL poza algebrę
```