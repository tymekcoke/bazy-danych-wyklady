# 🗣️ KEYWORDS GLOSSARY - SŁOWNICZEK TERMINÓW

## 🎯 JAK UŻYWAĆ
Poznaj polskie i angielskie nazwy - to pokazuje znajomość tematu! Użyj terminów angielskich gdy chcesz zabłysnąć.

---

## 🔥 NORMALIZACJA

| Polski | English | Użycie w zdaniu |
|---------|---------|-----------------|
| Forma normalna | Normal form | "Tabela jest w trzeciej formie normalnej" |
| Zależność funkcyjna | Functional dependency | "X determinuje Y to functional dependency" |
| Zależność przechodnia | Transitive dependency | "3NF eliminuje transitive dependencies" |
| Zależność częściowa | Partial dependency | "2NF usuwa partial dependencies od klucza" |
| Dekompozycja | Decomposition | "Lossless decomposition zachowuje informacje" |
| Dekompozycja bezstratna | Lossless decomposition | "Heath theorem gwarantuje lossless join" |
| Zależność wielowartościowa | Multivalued dependency (MVD) | "4NF eliminuje nietrywialne MVD" |
| Zależność złączeniowa | Join dependency (JD) | "5NF rozwiązuje problemy z join dependencies" |

---

## ⚡ TRANSAKCJE & ACID

| Polski | English | Użycie w zdaniu |
|---------|---------|-----------------|
| Atomowość | Atomicity | "Atomicity gwarantuje all-or-nothing execution" |
| Spójność | Consistency | "Consistency zachowuje database constraints" |
| Izolacja | Isolation | "Isolation levels kontrolują concurrent access" |
| Trwałość | Durability | "Durability zapewnia persistence po commit" |
| Poziom izolacji | Isolation level | "Serializable to najwyższy isolation level" |
| Brudny odczyt | Dirty read | "READ UNCOMMITTED pozwala na dirty reads" |
| Niepowtarzalny odczyt | Non-repeatable read | "REPEATABLE READ eliminuje non-repeatable reads" |
| Fantomowy odczyt | Phantom read | "Phantom reads mogą wystąpić w REPEATABLE READ" |
| Zatwierdzenie | Commit | "COMMIT potwierdza changes w transakcji" |
| Wycofanie | Rollback | "ROLLBACK anuluje uncommitted changes" |

---

## 🔒 BLOKADY & WSPÓŁBIEŻNOŚĆ

| Polski | English | Użycie w zdaniu |
|---------|---------|-----------------|
| Blokada | Lock | "Shared lock pozwala na concurrent reads" |
| Blokada dzielona | Shared lock (S-lock) | "Multiple transactions mogą mieć shared lock" |
| Blokada wyłączna | Exclusive lock (X-lock) | "Exclusive lock blokuje wszystkie inne operations" |
| Zakleszczenie | Deadlock | "Deadlock detection anuluje jedną transakcję" |
| Kontrola współbieżności | Concurrency control | "MVCC to advanced concurrency control mechanism" |
| Wielowersyjność | Multiversion Concurrency Control (MVCC) | "PostgreSQL używa MVCC dla better performance" |
| Punkt przywracania | Savepoint | "Savepoint pozwala na partial rollback" |

---

## 🗝️ KLUCZE

| Polski | English | Użycie w zdaniu |
|---------|---------|-----------------|
| Klucz główny | Primary key | "Primary key to unique + NOT NULL constraint" |
| Klucz obcy | Foreign key | "Foreign key zapewnia referential integrity" |
| Klucz kandydujący | Candidate key | "Candidate key to minimal superkey" |
| Superklucz | Superkey | "Superkey może zawierać redundant attributes" |
| Klucz złożony | Composite key | "Composite key składa się z multiple columns" |
| Klucz naturalny | Natural key | "Natural key pochodzi z business data" |
| Klucz sztuczny | Surrogate key | "Surrogate key to system-generated identifier" |
| Integralność referencyjna | Referential integrity | "Foreign keys enforce referential integrity" |

---

## 🔗 RELACJE & KARDINALNOŚĆ

| Polski | English | Użycie w zdaniu |
|---------|---------|-----------------|
| Jeden do jednego | One-to-one (1:1) | "User-Profile to typical 1:1 relationship" |
| Jeden do wielu | One-to-many (1:N) | "Customer-Orders to classic 1:N relationship" |
| Wiele do wielu | Many-to-many (M:N) | "Students-Courses wymaga junction table dla M:N" |
| Kardinalność | Cardinality | "Cardinality określa relationship multiplicity" |
| Tabela łącząca | Junction table / Bridge table | "Junction table implementuje M:N relationships" |
| Encja słaba | Weak entity | "Weak entity zależy od strong entity" |
| Encja silna | Strong entity | "Strong entity ma własny primary key" |

---

## 📊 SQL & ALGEBRA RELACJI

| Polski | English | Użycie w zdaniu |
|---------|---------|-----------------|
| Język zapytań | Query language | "SQL to declarative query language" |
| Algebra relacji | Relational algebra | "SQL bazuje na relational algebra operations" |
| Selekcja | Selection (σ) | "Selection σ filtruje rows według predicate" |
| Projekcja | Projection (π) | "Projection π wybiera specific columns" |
| Złączenie | Join (⋈) | "Natural join ⋈ łączy tables po common attributes" |
| Iloczyn kartezjański | Cartesian product (×) | "Cross join to Cartesian product w SQL" |
| Podzapytanie | Subquery | "Correlated subquery odwołuje się do outer query" |
| Zapytanie skorelowane | Correlated query | "EXISTS często używa correlated subqueries" |

---

## 🔍 JOIN'Y

| Polski | English | Użycie w zdaniu |
|---------|---------|-----------------|
| Złączenie wewnętrzne | Inner join | "Inner join zwraca only matching rows" |
| Złączenie lewe | Left join / Left outer join | "Left join preserves all rows from left table" |
| Złączenie prawe | Right join / Right outer join | "Right join to reverse of left join" |
| Złączenie pełne | Full outer join | "Full outer join combines left and right joins" |
| Złączenie krzyżowe | Cross join | "Cross join produces Cartesian product" |
| Złączenie naturalne | Natural join | "Natural join używa common column names" |
| Samo-złączenie | Self join | "Self join łączy table with itself" |

---

## 📈 INDEKSY & WYDAJNOŚĆ

| Polski | English | Użycie w zdaniu |
|---------|---------|-----------------|
| Indeks | Index | "B-tree index to default indexing method" |
| Indeks klastrowany | Clustered index | "Clustered index określa physical row order" |
| Indeks nieklastrowany | Non-clustered index | "Non-clustered index to separate structure" |
| Indeks złożony | Composite index | "Composite index covers multiple columns" |
| Indeks częściowy | Partial index | "Partial index używa WHERE clause condition" |
| Indeks funkcyjny | Functional index | "Functional index on LOWER(name) for case-insensitive search" |
| Pokrycie indeksu | Index coverage | "Covering index eliminuje table lookup" |
| Plan wykonania | Execution plan | "EXPLAIN ANALYZE shows actual execution plan" |
| Optymalizator zapytań | Query optimizer | "Query optimizer wybiera optimal execution path" |

---

## 📊 AGREGACJE & FUNKCJE

| Polski | English | Użycie w zdaniu |
|---------|---------|-----------------|
| Funkcja agregująca | Aggregate function | "COUNT, SUM to podstawowe aggregate functions" |
| Grupowanie | Grouping | "GROUP BY clause creates grouping dla aggregation" |
| Funkcja okienkowa | Window function | "Window functions działają over partitions" |
| Ranking | Ranking | "ROW_NUMBER() to basic ranking function" |
| Percentyl | Percentile | "PERCENTILE_CONT calculates continuous percentiles" |
| Suma krocząca | Running total | "Running total używa window frame specification" |

---

## 🎨 MODEL ER

| Polski | English | Użycie w zdaniu |
|---------|---------|-----------------|
| Model encja-związek | Entity-Relationship model | "ER model to conceptual database design tool" |
| Encja | Entity | "Customer to example of strong entity" |
| Atrybut | Attribute | "Primary key attribute uniquely identifies entity" |
| Związek | Relationship | "Relationships connect entities w ER model" |
| Atrybut złożony | Composite attribute | "Address to composite attribute (street, city, zip)" |
| Atrybut wielowartościowy | Multivalued attribute | "Phone numbers to multivalued attribute" |
| Atrybut pochodny | Derived attribute | "Age to derived attribute from birth_date" |
| Identyfikator | Identifier | "Entity identifier becomes primary key" |

---

## 🛡️ BEZPIECZEŃSTWO

| Polski | English | Użycie w zdaniu |
|---------|---------|-----------------|
| Uprawnienia | Privileges | "GRANT statement assigns privileges to users" |
| Autoryzacja | Authorization | "Role-based authorization simplifies user management" |
| Uwierzytelnianie | Authentication | "Database authentication verifies user identity" |
| Kontrola dostępu | Access control | "Row-level security provides granular access control" |
| Rola | Role | "Database roles group related privileges" |

---

## 🔧 FUNKCJE & TRIGGERY

| Polski | English | Użycie w zdaniu |
|---------|---------|-----------------|
| Funkcja składowana | Stored function | "Stored functions encapsulate business logic" |
| Procedura składowana | Stored procedure | "Stored procedures nie zwracają values like functions" |
| Wyzwalacz | Trigger | "BEFORE trigger może modify NEW record" |
| Funkcja wyzwalacza | Trigger function | "Trigger function implements trigger logic" |
| Język proceduralny | Procedural language | "PL/pgSQL to PostgreSQL procedural language" |

---

## 🔄 WIDOKI

| Polski | English | Użycie w zdaniu |
|---------|---------|-----------------|
| Widok | View | "Views provide abstraction layer over tables" |
| Widok zmaterializowany | Materialized view | "Materialized views cache query results" |
| Widok aktualizowalny | Updatable view | "Simple views are often updatable" |

---

## 💾 ARCHITEKTURA

| Polski | English | Użycie w zdaniu |
|---------|---------|-----------------|
| System zarządzania bazą danych | Database Management System (DBMS) | "PostgreSQL to advanced open-source DBMS" |
| Silnik bazy danych | Database engine | "Storage engine determines data persistence" |
| Bufor | Buffer | "Buffer pool cache frequently accessed pages" |
| Dziennik transakcji | Transaction log / Write-Ahead Log (WAL) | "WAL ensures durability w PostgreSQL" |
| Punkt kontrolny | Checkpoint | "Checkpoint flushes dirty pages to disk" |

---

## 🎯 TIPS DO UŻYWANIA

### ✅ DOBRZE:
- "Ta tabela jest w third normal form"
- "Użyjemy foreign key dla referential integrity"  
- "MVCC pozwala na better concurrency"
- "Left join preserves wszystkie rows z lewej strony"

### ❌ UNIKAJ:
- Wymieszanych języków w jednym terminie
- Błędnych tłumaczeń ("klucz zagraniczny" zamiast "klucz obcy")
- Zbyt częstego używania angielskich terminów

### 💡 STRATEGIA:
1. **Najpierw po polsku** - pokaż, że znasz polską terminologię
2. **Dodaj angielski** - "czyli po angielsku foreign key"
3. **Używaj naturalnie** - nie forsuj angielskiego tam gdzie nie trzeba

---

**🎓 PAMIĘTAJ:** Znajomość terminologii w obu językach pokazuje profesjonalizm i głęboką znajomość tematu!