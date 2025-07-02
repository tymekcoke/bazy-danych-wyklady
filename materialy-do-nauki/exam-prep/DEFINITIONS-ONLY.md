# 📚 DEFINITIONS ONLY - SAME DEFINICJE

## 🔥 NORMALIZACJA

**1NF (Pierwsza Forma Normalna)**
Wszystkie wartości w tabeli są atomowe (niepodzielne). Brak powtarzających się grup i wartości złożonych.

**2NF (Druga Forma Normalna)**  
1NF + eliminacja zależności częściowych od klucza głównego. Każdy atrybut niebędący kluczem jest w pełni zależny od całego klucza.

**3NF (Trzecia Forma Normalna)**
2NF + eliminacja zależności przechodnich. Żaden atrybut niebędący kluczem nie zależy od innego atrybutu niebędącego kluczem.

**BCNF (Forma Normalna Boyce'a-Codda)**
Każda zależność funkcyjna X→Y, gdzie X jest superkluczem.

**4NF (Czwarta Forma Normalna)**
BCNF + eliminacja wielowartościowych zależności funkcyjnych.

**5NF (Piąta Forma Normalna)**
4NF + eliminacja zależności złączeniowych.

---

## ⚡ ACID & TRANSAKCJE

**ACID**
Zbiór właściwości gwarantujących niezawodne przetwarzanie transakcji.

**Atomicity (Atomowość)**
Transakcja wykonuje się w całości albo wcale. Brak częściowych wykonań.

**Consistency (Spójność)**
Transakcja przeprowadza bazę ze stanu spójnego do stanu spójnego. Wszystkie ograniczenia integralności są zachowane.

**Isolation (Izolacja)**
Współbieżne transakcje nie interferują ze sobą. Każda transakcja działa jak gdyby była jedyna.

**Durability (Trwałość)**
Zatwierdzone zmiany są trwałe i przetrwają awarie systemu.

**Transakcja**
Logiczna jednostka pracy składająca się z jednej lub więcej operacji na bazie danych.

---

## 🔒 POZIOMY IZOLACJI

**READ UNCOMMITTED**
Najniższy poziom. Możliwe dirty reads, non-repeatable reads, phantom reads.

**READ COMMITTED**
Eliminuje dirty reads. Domyślny w PostgreSQL. Możliwe non-repeatable reads i phantom reads.

**REPEATABLE READ**
Eliminuje dirty reads i non-repeatable reads. Możliwe phantom reads.

**SERIALIZABLE**
Najwyższy poziom. Eliminuje wszystkie anomalie. Transakcje działają jak wykonane szeregowo.

**Dirty Read**
Czytanie niezatwierdzonych zmian z innej transakcji.

**Non-repeatable Read**
Różne wyniki tego samego zapytania w ramach jednej transakcji.

**Phantom Read**
Pojawienie się nowych wierszy spełniających warunek między kolejnymi czytaniami.

---

## 🔐 BLOKADY & MVCC

**Blokada (Lock)**
Mechanizm kontroli dostępu do zasobów w środowisku wielodostępowym.

**Shared Lock (S)**
Blokada dzielona. Pozwala na współbieżne czytanie, blokuje pisanie.

**Exclusive Lock (X)**
Blokada wyłączna. Blokuje zarówno czytanie jak i pisanie przez inne transakcje.

**Deadlock**
Sytuacja, gdy dwie lub więcej transakcji czeka na siebie wzajemnie, tworząc cykl oczekiwania.

**MVCC (Multiversion Concurrency Control)**
Mechanizm kontroli współbieżności przez zarządzanie wieloma wersjami danych. Czytanie nie blokuje pisania.

---

## 🗝️ KLUCZE

**Klucz Kandydujący**
Minimalny zbiór atrybutów jednoznacznie identyfikujący każdy wiersz w tabeli.

**Klucz Główny (Primary Key)**
Wybrany klucz kandydujący. Unikalny + NOT NULL. Maksymalnie jeden na tabelę.

**Klucz Obcy (Foreign Key)**
Atrybut lub zbiór atrybutów odwołujący się do klucza głównego innej tabeli.

**Superklucz**
Zbiór atrybutów zawierający klucz kandydujący (może mieć nadmiarowe atrybuty).

**Klucz Złożony**
Klucz składający się z więcej niż jednej kolumny.

---

## 🔗 RELACJE

**Relacja 1:1 (jeden do jednego)**
Jeden rekord w tabeli A odpowiada maksymalnie jednemu rekordowi w tabeli B i vice versa.

**Relacja 1:N (jeden do wielu)**
Jeden rekord w tabeli A może odpowiadać wielu rekordom w tabeli B.

**Relacja M:N (wiele do wielu)**
Wiele rekordów w tabeli A może odpowiadać wielu rekordom w tabeli B. Wymaga tabeli łączącej.

**Integralność Referencyjna**
Ograniczenie zapewniające, że wartości kluczy obcych istnieją w tabeli referencyjnej lub są NULL.

---

## 📊 ALGEBRA RELACJI

**Selekcja (σ)**
Operacja wybierająca wiersze spełniające określony warunek.

**Projekcja (π)**
Operacja wybierająca określone kolumny z relacji.

**Złączenie (⋈)**
Operacja łącząca dwie relacje na podstawie wspólnych atrybutów.

**Suma (∪)**
Operacja zwracająca wszystkie krotki z dwóch relacji (bez duplikatów).

**Przecięcie (∩)**
Operacja zwracająca krotki występujące w obu relacjach.

**Różnica (-)**
Operacja zwracająca krotki z pierwszej relacji, które nie występują w drugiej.

**Iloczyn Kartezjański (×)**
Operacja zwracająca wszystkie możliwe kombinacje krotek z dwóch relacji.

---

## 🎯 ZALEŻNOŚCI FUNKCYJNE

**Zależność Funkcyjna**
X → Y oznacza, że wartość X jednoznacznie determinuje wartość Y.

**Zależność Trywialna**
Zależność funkcyjna X → Y, gdzie Y ⊆ X.

**Zależność Pełna**
Zależność funkcyjna X → Y, gdzie Y nie zależy od żadnego właściwego podzbioru X.

**Zależność Przechodnia**
X → Y ∧ Y → Z ⇒ X → Z, gdzie Y nie jest podzbiorem X ani X podzbiorem Y.

**Domknięcie**
X+ to zbiór wszystkich atrybutów determinowanych przez X.

**Aksjomaty Armstronga**
Zbiór reguł do wyprowadzania nowych zależności funkcyjnych z istniejących.

---

## 💾 SQL KOMPONENTY

**DDL (Data Definition Language)**
Język definicji danych. CREATE, ALTER, DROP.

**DML (Data Manipulation Language)**
Język manipulacji danych. SELECT, INSERT, UPDATE, DELETE.

**DCL (Data Control Language)**
Język kontroli danych. GRANT, REVOKE.

**TCL (Transaction Control Language)**
Język kontroli transakcji. BEGIN, COMMIT, ROLLBACK.

---

## 🔍 JOIN'Y

**INNER JOIN**
Zwraca tylko wiersze mające pasujące wartości w obu tabelach.

**LEFT JOIN (LEFT OUTER JOIN)**
Zwraca wszystkie wiersze z lewej tabeli plus pasujące z prawej.

**RIGHT JOIN (RIGHT OUTER JOIN)**
Zwraca wszystkie wiersze z prawej tabeli plus pasujące z lewej.

**FULL OUTER JOIN**
Zwraca wszystkie wiersze z obu tabel.

**CROSS JOIN**
Zwraca iloczyn kartezjański - wszystkie kombinacje wierszy.

**SELF JOIN**
Łączenie tabeli z samą sobą.

---

## 📈 INDEKSY

**Indeks**
Struktura danych przyspieszająca wyszukiwanie w tabeli.

**B-tree Index**
Domyślny typ indeksu. Dobry dla operacji równości i zakresów.

**Hash Index**
Indeks dla operacji równości. Szybki dla konkretnych wartości.

**Partial Index**
Indeks z warunkiem WHERE, obejmujący tylko część wierszy.

**Composite Index**
Indeks na więcej niż jednej kolumnie.

**Unique Index**
Indeks zapewniający unikalność wartości.

---

## 🎨 MODEL ER

**Encja**
Rzecz, obiekt lub pojęcie o którym przechowujemy informacje.

**Atrybut**
Właściwość opisująca encję.

**Związek (Relacja)**
Powiązanie między encjami.

**Atrybut Złożony**
Atrybut składający się z mniejszych komponentów.

**Atrybut Wielowartościowy**
Atrybut mogący mieć wiele wartości dla jednej encji.

**Atrybut Pochodny**
Atrybut, którego wartość można obliczyć z innych atrybutów.

**Encja Słaba**
Encja, której istnienie zależy od innej encji (silnej).

**Związek Identyfikujący**
Związek, w którym encja słaba potrzebuje klucza encji silnej do identyfikacji.

---

## 🔧 FUNKCJE & TRIGGERY

**Funkcja Użytkownika**
Wielokrotnego użytku blok kodu implementujący logikę biznesową.

**Funkcja Skalarna**
Funkcja zwracająca pojedynczą wartość.

**Funkcja Tabelowa**
Funkcja zwracająca zbiór wierszy.

**Trigger**
Specjalny typ procedury automatycznie wykonywany w odpowiedzi na zdarzenia.

**BEFORE Trigger**
Wykonywany przed operacją DML. Może modyfikować dane.

**AFTER Trigger**
Wykonywany po operacji DML. Nie może modyfikować danych operacji.

**INSTEAD OF Trigger**
Zastępuje operację DML. Używany głównie z widokami.

---

## 🛡️ NULL

**NULL**
Specjalna wartość reprezentująca brak danych lub nieznaną wartość.

**Logika Trójwartościowa**
System logiczny z trzema wartościami: TRUE, FALSE, NULL.

**COALESCE**
Funkcja zwracająca pierwszy argument różny od NULL.

**NULLIF**
Funkcja zwracająca NULL jeśli argumenty są równe.

---

## 📊 AGREGACJE

**Funkcja Agregująca**
Funkcja operująca na zbiorze wartości i zwracająca jedną wartość.

**GROUP BY**
Klauzula grupująca wiersze o tych samych wartościach w określonych kolumnach.

**HAVING**
Klauzula filtrująca grupy po agregacji (odpowiednik WHERE dla grup).

**Window Function**
Funkcja wykonująca obliczenia na zbiorze wierszy powiązanych z bieżącym wierszem.

---

## 🔄 WIDOKI

**Widok (View)**
Wirtualna tabela oparta na wyniku zapytania SQL.

**Zmaterializowany Widok**
Widok, którego wynik jest fizycznie przechowywany i okresowo odświeżany.

**Updatable View**
Widok, na którym można wykonywać operacje INSERT, UPDATE, DELETE.

---

**💡 WSKAZÓWKA:** Te definicje są podstawą - na egzaminie rozwiń je przykładami!