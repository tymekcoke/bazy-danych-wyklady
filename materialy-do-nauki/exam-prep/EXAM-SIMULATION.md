# 🎓 SYMULACJA EGZAMINU - PRZYKŁADOWE PYTANIA

## 📝 FORMAT EGZAMINU
- **3 losowe pytania**
- **Odpowiedź ustna + pisemna na kartce**
- **Możliwość napisania kodu SQL**
- **Czas: ~15-20 min na pytanie**

---

## 🎯 ZESTAW 1 - NORMALIZACJA

### PYTANIE 1A (ustnie - 60s):
*"Proszę wyjaśnić czym różni się 2NF od 3NF i podać przykład naruszenia każdej z tych form."*

**PRZYKŁADOWA ODPOWIEDŹ:**
2NF eliminuje zależności częściowe od klucza głównego - gdy część klucza złożonego determinuje atrybut niebędący częścią klucza. 3NF dodatkowo eliminuje zależności przechodnie - gdy atrybut niebędący kluczem determinuje inny atrybut niebędący kluczem.

Przykład naruszenia 2NF: tabela ZAMÓWIENIE(id_zamówienia, id_produktu, nazwa_produktu, ilość) - nazwa_produktu zależy tylko od id_produktu, nie od całego klucza.

Przykład naruszenia 3NF: tabela PRACOWNIK(id, imię, departament_id, nazwa_departamentu) - nazwa_departamentu zależy od departament_id, nie bezpośrednio od klucza.

### PYTANIE 1B (na kartce):
*"Znormalizuj poniższą tabelę do 3NF i narysuj schemat wynikowych tabel z kluczami:"*

```
STUDENT_KURS(
    student_id, imie_studenta, email_studenta,
    kurs_id, nazwa_kursu, punkty_ects, 
    prowadzacy_id, imie_prowadzacego, 
    ocena, data_egzaminu
)
```

**DO NARYSOWANIA:**
```
STUDENCI(student_id*, imie_studenta, email_studenta)
PROWADZACY(prowadzacy_id*, imie_prowadzacego)  
KURSY(kurs_id*, nazwa_kursu, punkty_ects, prowadzacy_id→)
OCENY(student_id→, kurs_id→, ocena, data_egzaminu)

*PK, →FK
```

---

## 🎯 ZESTAW 2 - TRANSAKCJE I BLOKADY

### PYTANIE 2A (ustnie - 60s):
*"Co to deadlock, jak powstaje i jakie są sposoby jego unikania?"*

**PRZYKŁADOWA ODPOWIEDŹ:**
Deadlock to sytuacja, gdy dwie lub więcej transakcji czeka na siebie wzajemnie, tworząc cykl oczekiwania. Powstaje gdy T1 blokuje zasób A i chce zasób B, a T2 blokuje B i chce A. 

Sposoby unikania: konsekwentna kolejność dostępu do zasobów, timeouty, redukcja czasu trwania transakcji, obniżenie poziomu izolacji. System zazwyczaj wykrywa deadlock i anuluje jedną z transakcji.

### PYTANIE 2B (na kartce):
*"Napisz dwie transakcje, które mogą prowadzić do deadlocka na tabelach KONTA i PRZELEWY:"*

**DO NAPISANIA:**
```sql
-- Transakcja 1:
BEGIN;
UPDATE konta SET saldo = saldo - 100 WHERE id = 1;  -- blokuje konto 1
UPDATE konta SET saldo = saldo + 100 WHERE id = 2;  -- chce konto 2
COMMIT;

-- Transakcja 2 (jednocześnie):
BEGIN;  
UPDATE konta SET saldo = saldo - 50 WHERE id = 2;   -- blokuje konto 2
UPDATE konta SET saldo = saldo + 50 WHERE id = 1;   -- chce konto 1
COMMIT;

-- DEADLOCK: T1 czeka na konto 2, T2 czeka na konto 1
```

---

## 🎯 ZESTAW 3 - SQL JOINS I NULL

### PYTANIE 3A (ustnie - 60s):
*"Wyjaśnij różnicę między INNER JOIN a LEFT JOIN i kiedy każdy z nich stosować."*

**PRZYKŁADOWA ODPOWIEDŹ:**
INNER JOIN zwraca tylko wiersze, które mają pasujące wartości w obu tabelach. LEFT JOIN zwraca wszystkie wiersze z lewej tabeli plus pasujące z prawej - dla niepasujących kolumny z prawej tabeli mają NULL.

INNER JOIN używamy gdy chcemy tylko kompletne dane z obu tabel. LEFT JOIN gdy chcemy wszystkie rekordy z głównej tabeli, nawet te bez powiązań - np. wszyscy klienci, także ci bez zamówień.

### PYTANIE 3B (na kartce):
*"Napisz zapytanie SQL znajdując wszystkich klientów i ich zamówienia. Pokaż także klientów bez zamówień:"*

**DO NAPISANIA:**
```sql
SELECT k.id, k.nazwa, z.id as zamowienie_id, z.data_zamowienia
FROM klienci k
LEFT JOIN zamowienia z ON k.id = z.klient_id
ORDER BY k.nazwa;

-- LEFT JOIN zapewnia pokazanie wszystkich klientów,
-- nawet tych bez zamówień (z.id będzie NULL)
```

---

## 🎯 ZESTAW 4 - FUNKCJE AGREGUJĄCE

### PYTANIE 4A (ustnie - 60s):
*"Czym różni się COUNT(*) od COUNT(kolumna) i kiedy używać każdego z nich?"*

**PRZYKŁADOWA ODPOWIEDŹ:**
COUNT(*) liczy wszystkie wiersze w grupie, włączając te z wartościami NULL. COUNT(kolumna) liczy tylko wiersze, gdzie dana kolumna nie jest NULL.

COUNT(*) używamy gdy chcemy wiedzieć ile jest rekordów ogółem. COUNT(kolumna) gdy chcemy wiedzieć ile rekordów ma wypełnioną konkretną wartość - np. COUNT(email) powie ile klientów podało email.

### PYTANIE 4B (na kartce):
*"Napisz zapytanie pokazujące dla każdego departamentu: liczbę pracowników, średnią pensję i liczbę pracowników z podanym emailem:"*

**DO NAPISANIA:**
```sql
SELECT 
    departament,
    COUNT(*) as liczba_pracownikow,
    AVG(pensja) as srednia_pensja,
    COUNT(email) as pracownicy_z_emailem
FROM pracownicy 
GROUP BY departament
HAVING COUNT(*) > 1
ORDER BY srednia_pensja DESC;
```

---

## 🎯 ZESTAW 5 - PROJEKTOWANIE BAZY

### PYTANIE 5A (ustnie - 60s):
*"Jak zaprojektować relację wiele-do-wielu między Studentami a Kursami z dodatkowymi informacjami o zapisie?"*

**PRZYKŁADOWA ODPOWIEDŹ:**
Relacja M:N wymaga tabeli łączącej. Tworzymy tabelę ZAPISY z kluczami obcymi do STUDENTÓW i KURSÓW plus dodatkowe atrybuty zapisu.

Struktura: STUDENCI(id), KURSY(id), ZAPISY(student_id, kurs_id, data_zapisu, status, ocena). Klucz główny ZAPISÓW to (student_id, kurs_id). Pozwala to na wielokrotne zapisy studenta na różne kursy i kursu dla różnych studentów.

### PYTANIE 5B (na kartce):
*"Narysuj schemat ERD i implementację SQL dla systemu: Autorzy piszą Książki, Książki mają Wydawców:"*

**DO NARYSOWANIA:**
```
ERD:
AUTOR ----< AUTORSTWO >---- KSIĄŻKA ----< WYDAJE >---- WYDAWCA
  |                           |                          |
 id,imie                   id,tytul                  id,nazwa

SQL:
CREATE TABLE autorzy (
    id SERIAL PRIMARY KEY,
    imie VARCHAR(100),
    nazwisko VARCHAR(100)
);

CREATE TABLE wydawcy (
    id SERIAL PRIMARY KEY,
    nazwa VARCHAR(100)
);

CREATE TABLE ksiazki (
    id SERIAL PRIMARY KEY,
    tytul VARCHAR(200),
    rok INTEGER,
    wydawca_id INT REFERENCES wydawcy(id)
);

CREATE TABLE autorstwo (
    autor_id INT REFERENCES autorzy(id),
    ksiazka_id INT REFERENCES ksiazki(id),
    PRIMARY KEY (autor_id, ksiazka_id)
);
```

---

## 🔍 WSKAZÓWKI DO ODPOWIEDZI

### Odpowiedzi ustne (60s):
1. **Definicja** (10s) - co to jest
2. **Wyjaśnienie** (30s) - jak działa, dlaczego ważne  
3. **Przykład** (20s) - konkretny case

### Odpowiedzi pisemne:
- **Czytelny kod SQL** z wcięciami
- **Komentarze** przy skomplikowanych fragmentach
- **Schematy** z oznaczeniem PK (*) i FK (→)
- **Sprawdź składnię** - przecinki, nawiasy, średniki

### Częste błędy do unikania:
- ❌ `= NULL` zamiast `IS NULL`
- ❌ Brak `GROUP BY` dla nieeagregowanych kolumn
- ❌ `NOT IN` z możliwymi NULL w liście
- ❌ Zapomnienie o FK w tabelach łączących
- ❌ Błędne oznaczenia kluczy w schematach

---

## 🎯 SAMODZIELNY TRENING

**Wylosuj 3 zestawy i odpowiedz w czasie:**
- **5 min** na odpowiedź ustną
- **10 min** na rozwiązanie pisemne  
- **Sprawdź** z przykładowymi odpowiedziami

**Powtarzaj** problematyczne tematy!

---

**💪 GOTOWY NA PRAWDZIWY EGZAMIN!**