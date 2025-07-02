# ⏰ OSTATNIE 20 MINUT PRZED EGZAMINEM

## 🚨 KRYTYCZNE - SPRAWDŹ TERAZ!

### 🔥 NULL - NAJWAŻNIEJSZA PUŁAPKA
```sql
❌ WHERE column = NULL     -- ZAWSZE FALSE!
✅ WHERE column IS NULL    -- OK

❌ NOT IN z NULL w liście  -- może zwrócić 0 wierszy
✅ NOT EXISTS             -- bezpieczne
```

### 🔥 COUNT - UWAGA NA RÓŻNICE  
```sql
COUNT(*)        -- wszystkie wiersze (z NULL)
COUNT(column)   -- tylko NOT NULL w kolumnie
COUNT(DISTINCT column)  -- unikalne NOT NULL
```

### 🔥 NORMALIZACJA - DEFINICJE
- **1NF**: atomowe wartości
- **2NF**: 1NF + brak zależności częściowych od klucza
- **3NF**: 2NF + brak zależności przechodnich  
- **BCNF**: każda zależność funkcyjna X→Y, gdzie X jest superkluczem

### 🔥 ACID - WBIJ W GŁOWĘ
- **A**tomicity - wszystko albo nic
- **C**onsistency - spójność ograniczeń  
- **I**solation - transakcje nie interferują
- **D**urability - zatwierdzone zmiany przetrwają

## ⚡ SZYBKI PRZEGLĄD

### KLUCZE
| Typ | NULL? | Duplikaty? | Uwagi |
|-----|-------|------------|-------|
| PRIMARY KEY | ❌ | ❌ | Max 1 na tabelę |
| FOREIGN KEY | ✅ | ✅ | Referencja do PK |
| UNIQUE | ✅ | ❌ | Wiele NULL dozwolone |

### POZIOMY IZOLACJI (od najsłabszego)
1. **READ UNCOMMITTED** - dirty reads
2. **READ COMMITTED** - PostgreSQL default  
3. **REPEATABLE READ** - phantom reads możliwe
4. **SERIALIZABLE** - pełna izolacja

### RELACJE
- **1:1** → FK w jednej tabeli LUB łączenie tabel
- **1:N** → FK w tabeli "wiele"  
- **M:N** → tabela łącząca z dwoma FK

## 📝 WZORY DO PRZEPISANIA

### ER → SQL
```
ENCJA → CREATE TABLE
ATRYBUT → kolumna
ZWIĄZEK 1:N → FOREIGN KEY  
ZWIĄZEK M:N → tabela łącząca
ATRYBUT WIELOWARTOŚCIOWY → osobna tabela
```

### ZALEŻNOŚĆ FUNKCYJNA
```
X → Y oznacza: 
dla każdej wartości X istnieje dokładnie jedna wartość Y

Przykład: student_id → imie, nazwisko
```

### JOIN'Y - PAMIĘTAJ RÓŻNICE
```sql
INNER JOIN    -- tylko pasujące z obu stron
LEFT JOIN     -- wszystkie z lewej + pasujące z prawej  
RIGHT JOIN    -- wszystkie z prawej + pasujące z lewej
FULL JOIN     -- wszystkie z obu stron
```

## 🎯 TYPOWE PYTANIA - GOTOWE ODPOWIEDZI

### "Czym różni się HAVING od WHERE?"
**HAVING** filtruje grupy po GROUP BY, **WHERE** filtruje wiersze przed grupowaniem.

### "Co to MVCC?"
Multiversion Concurrency Control - każdy wiersz ma wersje (xmin/xmax), czytanie nie blokuje pisania.

### "Kiedy powstaje deadlock?"
Gdy dwie transakcje czekają na siebie wzajemnie:
- T1: blokuje A, chce B
- T2: blokuje B, chce A

### "Co to indeks?"
Struktura danych przyspieszająca wyszukiwanie. B-tree domyślnie, Hash dla równości, GIN dla arrays/JSON.

## 🚨 BŁĘDY DO UNIKANIA

### W SQL:
```sql
❌ SELECT name FROM users GROUP BY department;  -- name nie w GROUP BY
✅ SELECT department FROM users GROUP BY department;

❌ SELECT * FROM a,b WHERE a.id = b.id;  -- old syntax  
✅ SELECT * FROM a JOIN b ON a.id = b.id;

❌ WHERE price NOT IN (10, 20, NULL);  -- problem z NULL
✅ WHERE price NOT IN (10, 20) OR price IS NULL;
```

### W projektowaniu:
- ❌ Klucz główny jako VARCHAR
- ❌ Brak indeksów na FK  
- ❌ Denormalizacja bez powodu
- ❌ Zapomnienie o cascade dla FK

## 🧠 MANTRA PRZED EGZAMINEM

**Powtarzaj:** 
- NULL nie równa się NULL
- COUNT(*) vs COUNT(column)  
- WHERE przed GROUP BY, HAVING po GROUP BY
- EXISTS lepsze niż IN dla dużych zbiorów
- FK zawsze z indeksem
- 3NF = brak zależności przechodnich

## ⏱️ OSTATNIE 5 MINUT

### Sprawdź czy pamiętasz:
- [ ] Co to 1NF, 2NF, 3NF, BCNF?
- [ ] Cztery właściwości ACID?
- [ ] Różnica między HAVING a WHERE?
- [ ] Jak działa LEFT JOIN?
- [ ] Co robi IS NULL vs = NULL?
- [ ] Kiedy używać EXISTS zamiast IN?
- [ ] Co to deadlock i jak powstaje?
- [ ] Jak wygląda tabela łącząca M:N?

### Jeśli nie pamiętasz czegoś - SPOKOJNIE!
Na egzaminie:
1. **Czytaj pytanie 2 razy**
2. **Rysuj schematy** (zawsze pomaga)
3. **Pisz przykłady** (konkretne tabele/dane)
4. **Sprawdzaj składnię SQL** (przecinki, nawiasy)

---

## 🎯 FINALNE WSKAZÓWKI

### Odpowiedzi ustne:
- **30 sekund** na zdefiniowanie pojęcia
- **Przykład** zawsze pomaga  
- **Korzyści/problemy** pokazują zrozumienie

### Odpowiedzi pisemne:
- **Czytelny kod SQL**
- **Komentarze** przy skomplikowanych fragmentach
- **Schematy tabel** przy projektowaniu
- **Strzałki FK** w diagramach

### Na kartce rysuj:
```
STUDENCI                    KURSY
[id*] ----FK----> [id*]
imie              nazwa  
nazwisko          ects

* = PRIMARY KEY
FK = FOREIGN KEY
```

---

**💪 JESTEŚ GOTOWY! POWODZENIA!** 🍀