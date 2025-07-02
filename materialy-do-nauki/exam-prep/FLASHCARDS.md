# 🃏 FLASHCARDS - SZYBKIE POWTÓRKI

## JAK UŻYWAĆ:
Zakryj odpowiedź, przeczytaj pytanie, odpowiedz, sprawdź. Powtarzaj problematyczne karty!

---

## 🔥 DEFINICJE PODSTAWOWE

**Q: Co to 1NF?**
A: Pierwsza forma normalna - wszystkie wartości w tabeli są atomowe (niepodzielne)

**Q: Co to 2NF?**  
A: Druga forma normalna - 1NF + brak zależności częściowych od klucza głównego

**Q: Co to 3NF?**
A: Trzecia forma normalna - 2NF + brak zależności przechodnich

**Q: Co to BCNF?**
A: Boyce-Codd forma normalna - każda zależność funkcyjna X→Y, gdzie X jest superkluczem

**Q: Co oznacza ACID?**
A: **A**tomicity, **C**onsistency, **I**solation, **D**urability

**Q: Co to zależność funkcyjna?**
A: X→Y oznacza, że wartość X jednoznacznie determinuje wartość Y

---

## ⚡ NULL I AGREGACJE

**Q: Co zwraca `WHERE column = NULL`?**
A: Zawsze FALSE (użyj `IS NULL`)

**Q: Różnica między `COUNT(*)` a `COUNT(column)`?**
A: COUNT(*) liczy wszystkie wiersze, COUNT(column) ignoruje NULL

**Q: Co robi COALESCE(a, b, c)?**
A: Zwraca pierwszy argument, który nie jest NULL

**Q: Czy funkcje agregujące (SUM, AVG) uwzględniają NULL?**
A: NIE - ignorują wartości NULL (oprócz COUNT(*))

---

## 🔗 KLUCZE I RELACJE

**Q: Czy PRIMARY KEY może być NULL?**
A: NIE - PRIMARY KEY to UNIQUE + NOT NULL

**Q: Czy FOREIGN KEY może być NULL?**
A: TAK - NULL oznacza brak referencji

**Q: Ile może być NULL w kolumnie UNIQUE?**
A: W PostgreSQL - wiele NULL jest dozwolonych

**Q: Jak modelować relację M:N?**
A: Tabela łącząca z dwoma FOREIGN KEY

**Q: Gdzie dać FK w relacji 1:N?**
A: W tabeli reprezentującej "wiele"

---

## 🔄 TRANSAKCJE I BLOKADY

**Q: 4 poziomy izolacji od najsłabszego?**
A: READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE

**Q: Co to dirty read?**
A: Czytanie niezatwierdzonych zmian z innej transakcji

**Q: Co to phantom read?**
A: Pojawienie się nowych wierszy między odczytami w tej samej transakcji

**Q: Kiedy powstaje deadlock?**
A: Gdy dwie transakcje czekają na siebie wzajemnie (cykliczne oczekiwanie)

**Q: Co to MVCC?**
A: Multiversion Concurrency Control - każdy wiersz ma wersje (xmin/xmax)

---

## 📊 SQL SKŁADNIA

**Q: Różnica HAVING vs WHERE?**
A: WHERE filtruje wiersze przed GROUP BY, HAVING filtruje grupy po GROUP BY

**Q: Co zwraca LEFT JOIN?**
A: Wszystkie wiersze z lewej tabeli + pasujące z prawej (NULL dla niepasujących)

**Q: Czy EXISTS jest szybsze niż IN?**
A: Często TAK - zwłaszcza dla dużych zbiorów i możliwości NULL

**Q: Jak działa INNER JOIN?**
A: Zwraca tylko wiersze, które mają pasujące wartości w obu tabelach

**Q: Kiedy używać UNION vs UNION ALL?**
A: UNION usuwa duplikaty, UNION ALL zostawia wszystko (szybsze)

---

## 🎨 PROJEKTOWANIE

**Q: Jak przekształcić atrybut wielowartościowy?**
A: Osobna tabela z FK do encji głównej

**Q: Co to klucz kandydujący?**
A: Minimalny zbiór atrybutów jednoznacznie identyfikujący każdy wiersz

**Q: Jak modelować dziedziczenie w SQL?**
A: Tabela nadklasy + tabele podklas z FK do nadklasy

**Q: Co to integralność referencyjna?**
A: Wartości FK muszą istnieć w tabeli referencyjnej lub być NULL

---

## ⚡ WYDAJNOŚĆ

**Q: Jaki indeks dla kolumny z WHERE clause?**
A: B-tree indeks na tej kolumnie

**Q: Czy FK automatycznie ma indeks?**
A: NIE - trzeba utworzyć ręcznie (ważne dla wydajności JOIN)

**Q: Co to partial index?**
A: Indeks z warunkiem WHERE (np. tylko dla aktywnych rekordów)

**Q: Kiedy używać composite index?**
A: Gdy często filtrujesz/sortujesz po wielu kolumnach razem

---

## 🔧 ZAAWANSOWANE

**Q: Różnica TRIGGER vs RULE?**
A: TRIGGER wykonuje funkcje podczas operacji, RULE przepisuje zapytania

**Q: Co to CTE?**
A: Common Table Expression - zapytanie w klauzuli WITH

**Q: Kiedy używać RECURSIVE CTE?**
A: Do przetwarzania hierarchii (drzewa organizacyjne, kategorie)

**Q: Co to window function?**
A: Funkcja działająca na "oknie" wierszy bez GROUP BY (np. ROW_NUMBER() OVER)

---

## 🚨 NAJCZĘSTSZE BŁĘDY

**Q: Dlaczego `SELECT name FROM users GROUP BY department` jest błędne?**
A: `name` nie jest w GROUP BY ani nie jest agregowane

**Q: Problem z `WHERE id NOT IN (1,2,NULL)`?**
A: NOT IN z NULL może zwrócić 0 wierszy - użyj NOT EXISTS

**Q: Dlaczego `WHERE salary = NULL` nie działa?**
A: NULL nie równa się niczemu, nawet NULL - użyj IS NULL

**Q: Co złego w `SELECT * FROM a,b WHERE a.id = b.id`?**
A: Stara składnia - lepiej użyć JOIN

---

## 💡 SZYBKIE WSKAZÓWKI

**Q: Jak szybko sprawdzić plan wykonania?**
A: `EXPLAIN ANALYZE SELECT ...`

**Q: Jak zrobić "soft delete"?**
A: Kolumna `deleted_at` lub `is_active`

**Q: Najlepsza praktyka dla PRIMARY KEY?**
A: SERIAL/AUTO_INCREMENT lub UUID

**Q: Jak obsłużyć case-insensitive wyszukiwanie?**
A: ILIKE w PostgreSQL lub LOWER() + indeks funkcyjny

---

**🎯 TIPS:**
- Przejrzyj karty 3 razy
- Problematyczne zapisz osobno  
- Ćwicz na przykładach
- Rysuj schematy!