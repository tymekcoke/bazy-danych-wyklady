# Model ER - encje, atrybuty, związki

## Definicja modelu ER

**Model Entity-Relationship (ER)** to **konceptualny model danych** służący do **graficznego przedstawienia struktury** bazy danych na wysokim poziomie abstrakcji.

### Kluczowe cechy:
- **Graficzna reprezentacja** - diagramy ER (ERD)
- **Konceptualny poziom** - niezależny od implementacji
- **Intuicyjność** - łatwy do zrozumienia przez non-techników
- **Podstawa projektowania** - punkt wyjścia do modelu relacyjnego

### Historyczne znaczenie:
- **Twórca**: Peter Chen (1976)
- **Cel**: Komunikacja między analitykami a użytkownikami
- **Ewolucja**: Podstawa dla UML i innych notacji

## Komponenty modelu ER

### 1. **Encje (Entities)**

#### Definicja:
**Encja** to **obiekt lub rzecz** z realnego świata, która może być **jednoznacznie identyfikowana** i o której chcemy przechowywać informacje.

#### Notacja graficzna:
```
┌─────────────┐
│   STUDENT   │  ← Prostokąt
└─────────────┘
```

#### Przykłady encji:
```
Fizyczne obiekty:
- STUDENT (konkretna osoba)
- SAMOCHÓD (fizyczny pojazd)
- BUDYNEK (konkretna budowla)

Abstrakcyjne pojęcia:
- KURS (przedmiot nauczania)
- ZAMÓWIENIE (transakcja handlowa)
- KONTO_BANKOWE (abstrakcyjne konto)

Wydarzenia:
- EGZAMIN (zdarzenie)
- SPOTKANIE (wydarzenie)
- TRANSAKCJA (operacja)
```

#### Zbiory encji (Entity Sets):
```
STUDENCI = {student1, student2, student3, ...}
KURSY = {kurs1, kurs2, kurs3, ...}
ZAMÓWIENIA = {zamówienie1, zamówienie2, ...}
```

### 2. **Atrybuty (Attributes)**

#### Definicja:
**Atrybuty** to **właściwości lub cechy** opisujące encje.

#### Notacja graficzna:
```
     ┌─────────┐
     │  imię   │ ← Elipsa
     └─────────┘
         │
    ┌─────────────┐
    │   STUDENT   │
    └─────────────┘
         │
     ┌─────────┐
     │ nazwisko│
     └─────────┘
```

#### Rodzaje atrybutów:

##### **Proste vs Złożone**
```
ADRES (złożony):
├── ulica (prosty)
├── numer_domu (prosty)  
├── kod_pocztowy (prosty)
└── miasto (prosty)

TELEFON (prosty):
- "123-456-789"
```

##### **Jednowartościowe vs Wielowartościowe**
```
STUDENT:
├── nr_indeksu (jednowartościowe) - każdy ma jeden
├── imię (jednowartościowe) - jedno główne imię
└── języki_obce (wielowartościowe) - może znać wiele

Notacja wielowartościowego:
     ══════════════
     ║ języki_obce ║ ← Podwójna elipsa
     ══════════════
```

##### **Przechowywane vs Wyprowadzone**
```
PRACOWNIK:
├── data_urodzenia (przechowywane)
└── wiek (wyprowadzone) ← Obliczane z daty urodzenia

Notacja wyprowadzonego:
     ┌─ ─ ─ ─ ─ ─ ─┐
     │     wiek     │ ← Przerywana linia
     └─ ─ ─ ─ ─ ─ ─┘
```

##### **Atrybuty kluczowe**
```
STUDENT:
└── nr_indeksu (klucz główny)

SAMOCHÓD:
└── nr_rejestracyjny (klucz główny)

Notacja klucza:
     ┌─────────────┐
     │ nr_indeksu  │ ← Podkreślenie
     └─────────────┘
```

### 3. **Związki (Relationships)**

#### Definicja:
**Związek** to **powiązanie lub asocjacja** między dwiema lub więcej encjami.

#### Notacja graficzna:
```
┌─────────┐     ┌─────────────┐     ┌─────────┐
│ STUDENT │─────│   ZAPISUJE  │─────│  KURS   │
└─────────┘     └─────────────┘     └─────────┘
                      ◊                ← Romb
```

#### Stopień związku:

##### **Związki unarne (rekursywne)**
```
           ┌─────────────┐
      ┌────│ ZWIERZCHNIK │────┐
      │    └─────────────┘    │
      │                       │
┌─────────┐                   │
│PRACOWNIK│───────────────────┘
└─────────┘

Przykład: Pracownik może być zwierzchnikiem innego pracownika
```

##### **Związki binarne**
```
┌─────────┐     ┌─────────────┐     ┌─────────┐
│ STUDENT │─────│   ZAPISUJE  │─────│  KURS   │
└─────────┘     └─────────────┘     └─────────┘

Najczęstszy typ związku
```

##### **Związki ternarne**
```
┌─────────┐
│DOSTAWCA │─────┐
└─────────┘     │     ┌─────────────┐
                │─────│  DOSTARCZA  │
┌─────────┐     │     └─────────────┘
│ PROJEKT │─────┘           │
└─────────┘                 │
                      ┌─────────┐
                      │ CZĘŚĆ   │
                      └─────────┘

Przykład: Dostawca dostarcza część do projektu
```

#### Kardynalność związków:

##### **1:1 (jeden do jednego)**
```
┌─────────┐     ┌─────────────┐     ┌─────────┐
│PRACOWNIK│──1──│   ZARZĄDZA  │──1──│ DZIAŁ   │
└─────────┘     └─────────────┘     └─────────┘

Jeden pracownik zarządza co najwyżej jednym działem
Jeden dział ma co najwyżej jednego kierownika
```

##### **1:N (jeden do wielu)**
```
┌─────────┐     ┌─────────────┐     ┌─────────┐
│ DZIAŁ   │──1──│  ZATRUDNIA  │──N──│PRACOWNIK│
└─────────┘     └─────────────┘     └─────────┘

Jeden dział zatrudnia wielu pracowników
Jeden pracownik pracuje w jednym dziale
```

##### **M:N (wiele do wielu)**
```
┌─────────┐     ┌─────────────┐     ┌─────────┐
│ STUDENT │──M──│   ZAPISUJE  │──N──│  KURS   │
└─────────┘     └─────────────┘     └─────────┘

Jeden student może zapisać się na wiele kursów
Jeden kurs może mieć wielu studentów
```

#### Uczestnictwo w związkach:

##### **Częściowe (Partial)**
```
┌─────────┐     ┌─────────────┐     ┌─────────┐
│PRACOWNIK│─────│   ZARZĄDZA  │─────│ DZIAŁ   │
└─────────┘     └─────────────┘     └─────────┘

Nie każdy pracownik musi zarządzać działem
```

##### **Całkowite (Total)**
```
┌─────────┐     ┌─────────────┐     ┌─────────┐
│PRACOWNIK│═════│   PRACUJE   │─────│ DZIAŁ   │
└─────────┘     └─────────────┘     └─────────┘
    ═ - podwójna linia oznacza uczestnictwo całkowite

Każdy pracownik MUSI pracować w jakimś dziale
```

## Typy encji

### 1. **Encje silne (Strong Entities)**
```
┌─────────────────────┐
│      STUDENT        │
├─────────────────────┤
│ nr_indeksu (PK)     │ ← Klucz własny
│ imię                │
│ nazwisko            │
│ email               │
└─────────────────────┘

Cechy:
- Ma własny klucz główny
- Istnieje niezależnie od innych encji
- Standardowy prostokąt
```

### 2. **Encje słabe (Weak Entities)**
```
╔═════════════════════╗
║     DZIECKO         ║ ← Podwójny prostokąt
╠═════════════════════╣
║ imię (Partial Key)  ║ ← Klucz częściowy
║ data_urodzenia      ║
║ płeć                ║
╚═════════════════════╝
         ║
╔═══════════════════╗
║    JEST_DZIECKIEM ║ ← Podwójny romb (Identifying Relationship)
╚═══════════════════╝
         │
┌─────────────────────┐
│      RODZIC         │
├─────────────────────┤
│ nr_pesel (PK)       │
│ imię                │
│ nazwisko            │
└─────────────────────┘

Cechy:
- Nie ma własnego pełnego klucza
- Klucz składa się z klucza częściowego + klucza encji silnej
- Zależy od encji silnej (właściciela)
```

## Atrybuty związków

### Związki z atrybutami:
```
┌─────────┐     ┌─────────────┐     ┌─────────┐
│ STUDENT │─────│   ZAPISUJE  │─────│  KURS   │
└─────────┘     └─────────────┘     └─────────┘
                        │
                 ┌─────────────┐
                 │data_zapisu  │ ← Atrybut związku
                 └─────────────┘
                        │
                 ┌─────────────┐
                 │   ocena     │
                 └─────────────┘

Atrybuty należą do związku, nie do pojedynczej encji
```

### Praktyczne zastosowania:
```
PRACOWNIK ─── PRACUJE_W ─── PROJEKT
                 │
           ┌─────────────┐
           │ data_początku│
           └─────────────┘
           ┌─────────────┐
           │ data_końca  │
           └─────────────┘
           ┌─────────────┐
           │   rola      │
           └─────────────┘

Jeden pracownik może pracować w wielu projektach w różnych rolach
```

## Rozszerzenia modelu ER

### 1. **Generalizacja/Specjalizacja**

#### ISA Hierarchy:
```
           ┌─────────────┐
           │   POJAZD    │ ← Superklasa
           ├─────────────┤
           │ nr_rej (PK) │
           │ marka       │
           │ model       │
           └─────────────┘
                  △  ← Trójkąt ISA
                  │
        ┌─────────┼─────────┐
        │                   │
┌─────────────┐    ┌─────────────┐
│  SAMOCHÓD   │    │  MOTOCYKL   │ ← Podklasy
├─────────────┤    ├─────────────┤
│ liczba_drzwi│    │ pojemność   │
│ bagażnik    │    │ typ_silnika │
└─────────────┘    └─────────────┘
```

#### Rodzaje specjalizacji:

##### **Rozłączna (Disjoint)**
```
POJAZD
  │
  ├── SAMOCHÓD    (d)  ← d = disjoint
  └── MOTOCYKL         Pojazd może być ALBO samochodem ALBO motocyklem
```

##### **Nakładająca się (Overlapping)**
```
OSOBA
  │
  ├── STUDENT     (o)  ← o = overlapping  
  └── PRACOWNIK        Osoba może być jednocześnie studentem i pracownikiem
```

##### **Całkowita (Total)**
```
POJAZD
  │
  ├── SAMOCHÓD    
  └── MOTOCYKL    ∥   ← Podwójna linia = Total
                      Każdy pojazd MUSI być albo samochodem albo motocyklem
```

##### **Częściowa (Partial)**
```
OSOBA
  │
  ├── STUDENT     
  └── PRACOWNIK   ─   ← Pojedyncza linia = Partial
                      Osoba może nie być ani studentem ani pracownikiem
```

### 2. **Agregacja**

#### Problem:
```
Jak modelować związek między związkiem a encją?
```

#### Rozwiązanie - Agregacja:
```
┌─────────────────────────────────────┐ ← Prostokąt otaczający
│ ┌─────────┐   ┌─────────┐   ┌─────────┐ │
│ │PRACOWNIK│───│ PRACUJE │───│ PROJEKT │ │
│ └─────────┘   └─────────┘   └─────────┘ │
└─────────────────────────────────────┘
                    │
              ┌─────────────┐
              │  NADZORUJE  │
              └─────────────┘
                    │
              ┌─────────┐
              │ MANAGER │
              └─────────┘

Manager nadzoruje pracę pracownika nad projektem
```

## Diagram ER - przykład kompletny

### System biblioteki uniwersyteckiej:

```
                    ┌─────────────┐
                    │  nr_indeksu │ ← Klucz
                    └─────────────┘
                           │
   ┌─────────┐      ┌─────────────┐      ┌─────────┐
   │  imię   │──────│   STUDENT   │──────│nazwisko │
   └─────────┘      └─────────────┘      └─────────┘
                           │                   │
                           │              ┌─────────┐
                           │              │  email  │
                           │              └─────────┘
                           │
                    ┌─────────────┐
                ┌───│ WYPOŻYCZA   │───┐
                │   └─────────────┘   │
                │          │          │
         ┌─────────────┐   │   ┌─────────────┐
         │data_wypożycz│   │   │data_zwrotu  │
         └─────────────┘   │   └─────────────┘
                │          │          │
         ┌─────────┐       │      ┌─────────┐
         │ KSIĄŻKA │───────┘      │ STATUS  │
         └─────────┘              └─────────┘
              │
        ┌─────────────┐
        │ ISBN (PK)   │
        └─────────────┘
              │
   ┌──────────┼──────────┐
   │          │          │
┌─────────┐ ┌─────────┐ ┌─────────┐
│  tytuł  │ │  autor  │ │  rok    │
└─────────┘ └─────────┘ └─────────┘
```

### Kardynalności w systemie biblioteki:
```
STUDENT ──1─── WYPOŻYCZA ───N── KSIĄŻKA
│                               │
│  Jeden student może           │
│  wypożyczyć wiele książek     │
│                               │
│                       Jedna książka może być
│                       wypożyczona przez jednego studenta
│                       (w danym momencie)
```

## Konwersja do modelu relacyjnego

### Zasady podstawowe:

#### 1. **Encje silne → Tabele**
```
Encja STUDENT:
┌─────────────────────┐
│      STUDENT        │
├─────────────────────┤
│ nr_indeksu (PK)     │
│ imię                │
│ nazwisko            │
│ email               │
└─────────────────────┘

↓ KONWERSJA ↓

CREATE TABLE Student (
    nr_indeksu INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    email VARCHAR(100)
);
```

#### 2. **Związki 1:N → Klucz obcy**
```
DZIAŁ ──1── ZATRUDNIA ──N── PRACOWNIK

↓ KONWERSJA ↓

CREATE TABLE Dzial (
    id_dzialu INT PRIMARY KEY,
    nazwa VARCHAR(100)
);

CREATE TABLE Pracownik (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    id_dzialu INT,  ← Klucz obcy
    FOREIGN KEY (id_dzialu) REFERENCES Dzial(id_dzialu)
);
```

#### 3. **Związki M:N → Tabela pośrednicząca**
```
STUDENT ──M── ZAPISUJE ──N── KURS

↓ KONWERSJA ↓

CREATE TABLE Student (
    nr_indeksu INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50)
);

CREATE TABLE Kurs (
    kod_kursu VARCHAR(10) PRIMARY KEY,
    nazwa VARCHAR(100),
    ects INT
);

CREATE TABLE Zapisuje (  ← Nowa tabela
    nr_indeksu INT,
    kod_kursu VARCHAR(10),
    data_zapisu DATE,
    ocena DECIMAL(3,2),
    PRIMARY KEY (nr_indeksu, kod_kursu),
    FOREIGN KEY (nr_indeksu) REFERENCES Student(nr_indeksu),
    FOREIGN KEY (kod_kursu) REFERENCES Kurs(kod_kursu)
);
```

#### 4. **Encje słabe → Klucz złożony**
```
RODZIC ──1── MA ──N── DZIECKO (weak)

↓ KONWERSJA ↓

CREATE TABLE Rodzic (
    nr_pesel VARCHAR(11) PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50)
);

CREATE TABLE Dziecko (
    nr_pesel_rodzica VARCHAR(11),
    imie VARCHAR(50),
    data_urodzenia DATE,
    PRIMARY KEY (nr_pesel_rodzica, imie, data_urodzenia),
    FOREIGN KEY (nr_pesel_rodzica) REFERENCES Rodzic(nr_pesel)
);
```

#### 5. **Atrybuty wielowartościowe → Osobna tabela**
```
PRACOWNIK z atrybutem języki_obce (wielowartościowy)

↓ KONWERSJA ↓

CREATE TABLE Pracownik (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50)
);

CREATE TABLE JezykiPracownika (
    id_pracownika INT,
    jezyk VARCHAR(50),
    PRIMARY KEY (id_pracownika, jezyk),
    FOREIGN KEY (id_pracownika) REFERENCES Pracownik(id_pracownika)
);
```

## Najlepsze praktyki modelowania ER

### ✅ **Dobre praktyki:**

#### 1. **Nazewnictwo**
```
✅ DOBRE:
- Encje: rzeczowniki w liczbie pojedynczej (STUDENT, nie STUDENCI)
- Związki: czasowniki (ZAPISUJE, PRACUJE, ZARZĄDZA)
- Atrybuty: rzeczowniki opisowe (imie, data_urodzenia)

❌ ZŁŻE:
- Encje: StudenciTable, tbl_student
- Związki: student_kurs, relacja1
- Atrybuty: pole1, atrybut_x
```

#### 2. **Minimalizacja redundancji**
```
✅ DOBRE - osobne encje:
AUTOR ──1── NAPISAŁ ──N── KSIĄŻKA

❌ ZŁŻE - redundancja:
KSIĄŻKA {tytuł, autor_imie, autor_nazwisko, autor_data_urodzenia}
```

#### 3. **Właściwe klucze**
```
✅ DOBRE:
- Klucze naturalne gdy stabilne (ISBN, PESEL)
- Klucze sztuczne gdy naturalne mogą się zmieniać

❌ ZŁŻE:
- Email jako klucz główny (może się zmienić)
- Imię + nazwisko jako klucz (nie unikalny)
```

### ❌ **Złe praktyki:**

#### 1. **Overengineering**
```
❌ ZŁŻE - zbyt szczegółowo:
Tworzenie osobnej encji dla każdego małego atrybutu

✅ LEPIEJ:
Grupowanie powiązanych atrybutów w jednej encji
```

#### 2. **Fan trap**
```
❌ PROBLEM:
DZIAŁ ──1── ZAWIERA ──N── PRACOWNIK
  │                         │
  1                         N
  │                         │
  └── POSIADA ──N── PROJEKT ──┘

Problem: Implicit związek PRACOWNIK-PROJEKT przez DZIAŁ

✅ ROZWIĄZANIE:
Explicit związek PRACOWNIK ──M── PRACUJE ──N── PROJEKT
```

#### 3. **Chasm trap**
```
❌ PROBLEM:
DZIAŁ ──1── MA ──N── PRACOWNIK ──M── POSIADA ──N── UMIEJĘTNOŚĆ

Problem: Jeśli pracownik nie ma umiejętności, dział nie ma związku z umiejętnościami

✅ ROZWIĄZANIE:
Dodanie bezpośredniego związku DZIAŁ ──M── WYMAGA ──N── UMIEJĘTNOŚĆ
```

## Narzędzia do modelowania ER

### Graficzne:
- **Lucidchart** - online
- **draw.io** - darmowy online
- **MySQL Workbench** - dla MySQL
- **pgModeler** - dla PostgreSQL
- **ERwin** - komercyjny

### Tekstowe notacje:
```sql
-- Mermaid syntax (dla dokumentacji)
erDiagram
    STUDENT {
        int nr_indeksu PK
        string imie
        string nazwisko
        string email
    }
    KURS {
        string kod_kursu PK
        string nazwa
        int ects
    }
    STUDENT ||--o{ ZAPISUJE : records
    ZAPISUJE }o--|| KURS : for
```

## Pułapki egzaminacyjne

### 1. **Różnica encja vs atrybut**
```
Kiedy coś jest encją a kiedy atrybutem?

ENCJA jeśli:
- Ma własne atrybuty
- Może uczestniczyć w związkach
- Ma znaczenie biznesowe

ATRYBUT jeśli:
- Prosty opis encji
- Nie ma pod-atrybutów
- Nie uczestniczy w związkach
```

### 2. **Kardynalność vs uczestnictwo**
```
KARDYNALNOŚĆ: 1:1, 1:N, M:N
- Ile maksymalnie encji może uczestniczyć

UCZESTNICTWO: częściowe vs całkowite
- Czy wszystkie encje MUSZĄ uczestniczyć
```

### 3. **Weak vs Strong entity**
```
WEAK ENTITY:
- Nie ma własnego pełnego klucza
- Zależy od encji silnej
- Podwójny prostokąt w notacji

STRONG ENTITY:
- Ma własny klucz główny
- Istnieje niezależnie
- Zwykły prostokąt
```

### 4. **Specjalizacja**
```
TOTAL vs PARTIAL:
- Total: każda instancja nadklasy MUSI być w podklasie
- Partial: instancja nadklasy MOŻE nie być w żadnej podklasie

DISJOINT vs OVERLAPPING:
- Disjoint: instancja może być tylko w jednej podklasie
- Overlapping: instancja może być w wielu podklasach
```