# 📊 MODEL ER - ENCJE, ATRYBUTY, ZWIĄZKI - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Model Entity-Relationship to konceptualny model danych reprezentujący strukturę informacji w systemie. Składa się z:

1. **Encje** - rzeczy, obiekty, pojęcia (prostokąty)
2. **Atrybuty** - właściwości encji (elipsy)
3. **Związki** - relacje między encjami (romby)

Typy atrybutów: proste, złożone, wielowartościowe, pochodne, klucze. Kardinalności związków: 1:1, 1:N, M:N. Model ER jest podstawą projektowania baz danych - od diagramu ER przechodzi się do schematu relacyjnego."

## ✍️ CO NAPISAĆ NA KARTCE

```
MODEL ER - SKŁADNIKI I NOTACJA:

ENCJE (prostokąty):
┌─────────────┐
│   STUDENT   │  - encja silna
└─────────────┘

╔═════════════╗
║   OCENA     ║  - encja słaba (podwójna ramka)
╚═════════════╝

ATRYBUTY (elipsy):
○ imie          - atrybut prosty
◎ id_studenta   - klucz główny (podkreślony)
⬚ adres         - atrybut złożony
◉ telefony      - atrybut wielowartościowy
⊙ wiek          - atrybut pochodny (przerywaną linią)

ZWIĄZKI (romby):
◇ studiuje      - związek
◆ ma_ocene      - związek słabej encji (podwójna ramka)

KARDINALNOŚCI:
1:1  - jeden do jednego    
1:N  - jeden do wielu      ——————<
M:N  - wiele do wielu      >——————<

SPECJALIZACJA/GENERALIZACJA:
△ - triangle symbol dla ISA hierarchy

PRZYKŁAD DIAGRAMU:
    ◎id         ○imie    ○nazwisko
      │           │        │
      └───────────┼────────┘
                  │
           ┌─────────────┐     1     ◇studiuje    N   ┌─────────────┐
           │   STUDENT   │──────────◇───────────────────│ UNIWERSYTET │
           └─────────────┘           ◇                  └─────────────┘
                  │
                  │ 1
                  │
                  ◆ma_ocene
                  │
                  │ N
           ╔═════════════╗
           ║    OCENA    ║
           ╚═════════════╝
              │     │
           ○data  ○wartosc

ZASADY PROJEKTOWANIA:
• Każda encja musi mieć klucz główny
• Związki M:N wymagają tabeli łączącej
• Encje słabe zależą od encji silnych
• Atrybuty złożone rozbijamy na proste
• Atrybuty wielowartościowe → osobne tabele
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- PRZYKŁAD KOMPLEKSOWEGO MODELU ER I JEGO IMPLEMENTACJI

-- Scenariusz: System zarządzania biblioteką uniwersytecką

/*
MODEL ER - OPIS TEXTOWY:

ENCJE GŁÓWNE:
- STUDENT (id_studenta, imie, nazwisko, nr_indeksu, email, adres)  
- KSIĄŻKA (id_ksiazki, isbn, tytul, rok_wydania, liczba_stron)
- AUTOR (id_autora, imie, nazwisko, narodowosc, data_urodzenia)
- WYDAWNICTWO (id_wydawnictwa, nazwa, adres, telefon)
- EGZEMPLARZ (nr_egzemplarza, stan, data_nabycia) - encja słaba

ZWIĄZKI:
- STUDENT - WYPOŻYCZA - EGZEMPLARZ (M:N z atrybutami data_wyp, data_zwrotu)
- KSIĄŻKA - MA - EGZEMPLARZ (1:N)
- KSIĄŻKA - NAPISANA_PRZEZ - AUTOR (M:N)  
- KSIĄŻKA - WYDANA_PRZEZ - WYDAWNICTWO (N:1)

SPECJALIZACJA:
- KSIĄŻKA → KSIĄŻKA_NAUKOWA (dziedzina, poziom)
- KSIĄŻKA → KSIĄŻKA_BELETRYSTYCZNA (gatunek, seria)
*/

-- 1. IMPLEMENTACJA ENCJI GŁÓWNYCH

-- Encja STUDENT
CREATE TABLE studenci (
    id_studenta SERIAL PRIMARY KEY,  -- klucz główny
    nr_indeksu VARCHAR(10) UNIQUE NOT NULL,  -- klucz kandydujący
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    
    -- Atrybut złożony ADRES rozbity na komponenty
    adres_ulica VARCHAR(100),
    adres_nr_domu VARCHAR(10),
    adres_kod_pocztowy VARCHAR(6),
    adres_miasto VARCHAR(50),
    
    data_urodzenia DATE,
    aktywny BOOLEAN DEFAULT TRUE
);

-- Encja WYDAWNICTWO
CREATE TABLE wydawnictwa (
    id_wydawnictwa SERIAL PRIMARY KEY,
    nazwa VARCHAR(100) NOT NULL,
    adres TEXT,
    telefon VARCHAR(20),
    email VARCHAR(100),
    rok_zalozenia INT
);

-- Encja AUTOR
CREATE TABLE autorzy (
    id_autora SERIAL PRIMARY KEY,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    pseudonim VARCHAR(50),
    narodowosc VARCHAR(50),
    data_urodzenia DATE,
    data_smierci DATE,
    biografia TEXT
);

-- Encja KSIĄŻKA
CREATE TABLE ksiazki (
    id_ksiazki SERIAL PRIMARY KEY,
    isbn VARCHAR(13) UNIQUE,
    tytul VARCHAR(200) NOT NULL,
    podtytul VARCHAR(200),
    rok_wydania INT,
    liczba_stron INT,
    jezyk VARCHAR(50) DEFAULT 'polski',
    id_wydawnictwa INT,
    
    FOREIGN KEY (id_wydawnictwa) REFERENCES wydawnictwa(id_wydawnictwa)
);

-- 2. ENCJA SŁABA - EGZEMPLARZ

-- Egzemplarz zależy od książki (encja słaba)
CREATE TABLE egzemplarze (
    id_ksiazki INT,
    nr_egzemplarza INT,
    stan VARCHAR(20) DEFAULT 'dobry',  -- dobry, uszkodzony, utracony
    data_nabycia DATE DEFAULT CURRENT_DATE,
    cena_nabycia DECIMAL(8,2),
    lokalizacja VARCHAR(50),
    
    -- Klucz złożony (książka + numer egzemplarza)
    PRIMARY KEY (id_ksiazki, nr_egzemplarza),
    FOREIGN KEY (id_ksiazki) REFERENCES ksiazki(id_ksiazki) ON DELETE CASCADE
);

-- 3. ATRYBUT WIELOWARTOŚCIOWY - TELEFONY STUDENTÓW

-- Telefony jako osobna tabela (atrybut wielowartościowy)
CREATE TABLE telefony_studentow (
    id_studenta INT,
    telefon VARCHAR(20),
    typ VARCHAR(20) DEFAULT 'komorkowy',  -- komorkowy, domowy, służbowy
    
    PRIMARY KEY (id_studenta, telefon),
    FOREIGN KEY (id_studenta) REFERENCES studenci(id_studenta) ON DELETE CASCADE
);

-- 4. ZWIĄZKI M:N

-- Związek KSIĄŻKA - NAPISANA_PRZEZ - AUTOR (M:N)
CREATE TABLE ksiazka_autor (
    id_ksiazki INT,
    id_autora INT,
    rola VARCHAR(50) DEFAULT 'autor',  -- autor, współautor, redaktor, tłumacz
    kolejnosc INT DEFAULT 1,
    
    PRIMARY KEY (id_ksiazki, id_autora),
    FOREIGN KEY (id_ksiazki) REFERENCES ksiazki(id_ksiazki) ON DELETE CASCADE,
    FOREIGN KEY (id_autora) REFERENCES autorzy(id_autora) ON DELETE CASCADE
);

-- Związek STUDENT - WYPOŻYCZA - EGZEMPLARZ (M:N z atrybutami)
CREATE TABLE wypozyczenia (
    id_wypozyczenia SERIAL PRIMARY KEY,  -- surrogate key dla wygody
    id_studenta INT NOT NULL,
    id_ksiazki INT NOT NULL,
    nr_egzemplarza INT NOT NULL,
    data_wypozyczenia DATE DEFAULT CURRENT_DATE,
    data_zwrotu_planowana DATE NOT NULL,
    data_zwrotu_faktyczna DATE,
    prolongaty INT DEFAULT 0,
    kara DECIMAL(6,2) DEFAULT 0,
    
    FOREIGN KEY (id_studenta) REFERENCES studenci(id_studenta),
    FOREIGN KEY (id_ksiazki, nr_egzemplarza) 
        REFERENCES egzemplarze(id_ksiazki, nr_egzemplarza),
    
    -- Constraint: nie można wypożyczyć tego samego egzemplarza dwukrotnie
    UNIQUE (id_ksiazki, nr_egzemplarza, data_zwrotu_faktyczna)
);

-- 5. SPECJALIZACJA/GENERALIZACJA (ISA Hierarchy)

-- Specjalizacja książek - podtypy
CREATE TABLE ksiazki_naukowe (
    id_ksiazki INT PRIMARY KEY,
    dziedzina VARCHAR(100),
    poziom VARCHAR(50),  -- podstawowy, średniozaawansowany, zaawansowany
    czy_recenzowana BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (id_ksiazki) REFERENCES ksiazki(id_ksiazki) ON DELETE CASCADE
);

CREATE TABLE ksiazki_beletrystyczne (
    id_ksiazki INT PRIMARY KEY,
    gatunek VARCHAR(50),  -- powieść, opowiadania, poezja, dramat
    seria VARCHAR(100),
    tom_w_serii INT,
    
    FOREIGN KEY (id_ksiazki) REFERENCES ksiazki(id_ksiazki) ON DELETE CASCADE
);

-- 6. ATRYBUTY POCHODNE - implementacja przez views

-- Wiek studenta (atrybut pochodny)
CREATE VIEW studenci_z_wiekiem AS
SELECT 
    s.*,
    EXTRACT(YEAR FROM AGE(s.data_urodzenia)) as wiek,
    -- Pełny adres (atrybut złożony jako pochodny)
    CONCAT_WS(', ', 
        CONCAT(s.adres_ulica, ' ', s.adres_nr_domu),
        s.adres_kod_pocztowy,
        s.adres_miasto
    ) as pelny_adres
FROM studenci s;

-- Liczba książek autora (atrybut pochodny)
CREATE VIEW autorzy_z_statystykami AS
SELECT 
    a.*,
    COUNT(ka.id_ksiazki) as liczba_ksiazek,
    MIN(k.rok_wydania) as pierwsza_publikacja,
    MAX(k.rok_wydania) as ostatnia_publikacja
FROM autorzy a
LEFT JOIN ksiazka_autor ka ON a.id_autora = ka.id_autora
LEFT JOIN ksiazki k ON ka.id_ksiazki = k.id_ksiazki
GROUP BY a.id_autora, a.imie, a.nazwisko, a.pseudonim, 
         a.narodowosc, a.data_urodzenia, a.data_smierci, a.biografia;

-- 7. PRZYKŁADOWE DANE

-- Wydawnictwa
INSERT INTO wydawnictwa VALUES 
(1, 'PWN', 'Warszawa, ul. Miodowa 10', '22-695-4321', 'biuro@pwn.pl', 1951),
(2, 'Helion', 'Gliwice, ul. Kościuszki 1c', '32-230-9863', 'helion@helion.pl', 1991);

-- Autorzy
INSERT INTO autorzy VALUES 
(1, 'Adam', 'Mickiewicz', NULL, 'polska', '1798-12-24', '1855-11-26', 'Poeta, pisarz, działacz polityczny'),
(2, 'Henryk', 'Sienkiewicz', NULL, 'polska', '1846-05-05', '1916-11-15', 'Powieściopisarz, nobelista'),
(3, 'Donald', 'Knuth', NULL, 'amerykańska', '1938-01-10', NULL, 'Informatyk, matematyk');

-- Książki
INSERT INTO ksiazki VALUES 
(1, '9788301167721', 'Pan Tadeusz', NULL, 1834, 400, 'polski', 1),
(2, '9788307033679', 'Quo Vadis', NULL, 1896, 600, 'polski', 1),
(3, '9788324631766', 'The Art of Computer Programming', 'Volume 1', 1968, 650, 'angielski', 2);

-- Związki książka-autor
INSERT INTO ksiazka_autor VALUES 
(1, 1, 'autor', 1),
(2, 2, 'autor', 1),
(3, 3, 'autor', 1);

-- Specjalizacje
INSERT INTO ksiazki_beletrystyczne VALUES 
(1, 'poemat', 'Klasyka Literatury Polskiej', 1),
(2, 'powieść', 'Trylogia', 3);

INSERT INTO ksiazki_naukowe VALUES 
(3, 'informatyka', 'zaawansowany', TRUE);

-- Egzemplarze
INSERT INTO egzemplarze VALUES 
(1, 1, 'dobry', '2020-01-15', 45.00, 'Sala A1'),
(1, 2, 'dobry', '2020-01-15', 45.00, 'Sala A1'),
(2, 1, 'uszkodzony', '2019-03-10', 55.00, 'Sala B2'),
(3, 1, 'dobry', '2021-06-20', 120.00, 'Sala C3');

-- Studenci
INSERT INTO studenci VALUES 
(1, 'S001234', 'Jan', 'Kowalski', 'jan.kowalski@student.uw.edu.pl',
 'ul. Krakowskie Przedmieście', '26/28', '00-927', 'Warszawa', '2000-03-15', TRUE);

-- Telefony studentów (atrybut wielowartościowy)
INSERT INTO telefony_studentow VALUES 
(1, '123456789', 'komorkowy'),
(1, '22-555-0123', 'domowy');

-- 8. ZAPYTANIA TESTUJĄCE MODEL

-- Książki z autorami (związek M:N)
SELECT 
    k.tytul,
    string_agg(a.imie || ' ' || a.nazwisko, ', ' ORDER BY ka.kolejnosc) as autorzy,
    w.nazwa as wydawnictwo
FROM ksiazki k
JOIN ksiazka_autor ka ON k.id_ksiazki = ka.id_ksiazki
JOIN autorzy a ON ka.id_autora = a.id_autora
LEFT JOIN wydawnictwa w ON k.id_wydawnictwa = w.id_wydawnictwa
GROUP BY k.id_ksiazki, k.tytul, w.nazwa;

-- Studenci z telefonami (atrybut wielowartościowy)
SELECT 
    s.imie,
    s.nazwisko,
    string_agg(t.telefon || ' (' || t.typ || ')', ', ') as telefony
FROM studenci s
LEFT JOIN telefony_studentow t ON s.id_studenta = t.id_studenta
GROUP BY s.id_studenta, s.imie, s.nazwisko;

-- Egzemplarze z informacją o książce (encja słaba)
SELECT 
    k.tytul,
    e.nr_egzemplarza,
    e.stan,
    e.lokalizacja
FROM ksiazki k
JOIN egzemplarze e ON k.id_ksiazki = e.id_ksiazki
ORDER BY k.tytul, e.nr_egzemplarza;

-- 9. OGRANICZENIA WYNIKAJĄCE Z MODELU ER

-- Constraint: student nie może wypożyczyć więcej niż 5 książek jednocześnie
CREATE OR REPLACE FUNCTION sprawdz_limit_wypozyczen()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT COUNT(*) 
        FROM wypozyczenia 
        WHERE id_studenta = NEW.id_studenta 
        AND data_zwrotu_faktyczna IS NULL) >= 5 THEN
        RAISE EXCEPTION 'Student może wypożyczyć maksymalnie 5 książek jednocześnie';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_limit_wypozyczen
    BEFORE INSERT ON wypozyczenia
    FOR EACH ROW
    EXECUTE FUNCTION sprawdz_limit_wypozyczen();

-- Constraint: egzemplarz nie może być w stanie "utracony" i jednocześnie wypożyczony
ALTER TABLE wypozyczenia 
ADD CONSTRAINT chk_nie_wypozyczaj_utraconych
CHECK (NOT EXISTS (
    SELECT 1 FROM egzemplarze e 
    WHERE e.id_ksiazki = wypozyczenia.id_ksiazki 
    AND e.nr_egzemplarza = wypozyczenia.nr_egzemplarza 
    AND e.stan = 'utracony'
    AND wypozyczenia.data_zwrotu_faktyczna IS NULL
));
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Encje słabe mają klucz złożony (własny + klucz encji silnej)
2. **UWAGA**: Atrybuty wielowartościowe wymagają osobnych tabel
3. **BŁĄD**: Mylenie kardinalności 1:N z N:1 (kierunek ma znaczenie)
4. **WAŻNE**: Atrybuty złożone rozbijamy na komponenty w implementacji
5. **PUŁAPKA**: Związki M:N zawsze wymagają tabeli łączącej

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Entity-Relationship model** - model encja-związek
- **Strong/Weak entities** - encje silne/słabe
- **Simple/Composite attributes** - atrybuty proste/złożone
- **Multivalued attributes** - atrybuty wielowartościowe
- **Derived attributes** - atrybuty pochodne
- **Cardinality constraints** - ograniczenia kardinalności
- **ISA hierarchy** - hierarchia specjalizacji
- **Identifying relationship** - związek identyfikujący

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **14-er-do-sql** - implementacja modelu ER w SQL
- **26-model-relacyjny** - przekształcenie ER → relacyjny
- **12-klucze-bazy-danych** - klucze w modelu ER
- **01-integralnosc** - ograniczenia w modelu ER
- **02-relacje-1-1** - implementacja związków 1:1