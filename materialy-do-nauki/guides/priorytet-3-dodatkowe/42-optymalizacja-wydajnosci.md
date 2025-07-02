# Optymalizacja wydajności baz danych

## Definicja optymalizacji wydajności

**Optymalizacja wydajności baz danych** to **systematyczny proces** poprawy **szybkości, efektywności i skalowalności** systemu bazy danych poprzez **dostrajanie zapytań, struktury danych i konfiguracji systemu**.

### Kluczowe metryki wydajności:
- **Response Time** - czas odpowiedzi na zapytanie
- **Throughput** - liczba operacji na sekundę
- **Latency** - opóźnienie systemu
- **CPU Utilization** - wykorzystanie procesora
- **Memory Usage** - zużycie pamięci
- **I/O Operations** - operacje wejścia/wyjścia
- **Connection Pool** - wykorzystanie puli połączeń

### Poziomy optymalizacji:
- **Query Level** - optymalizacja zapytań SQL
- **Index Level** - optymalizacja indeksów
- **Schema Level** - optymalizacja struktury danych
- **Configuration Level** - dostrajanie konfiguracji
- **Hardware Level** - optymalizacja sprzętowa

## Optymalizacja zapytań SQL

### 1. **Analiza planów wykonania**

#### PostgreSQL - EXPLAIN i EXPLAIN ANALYZE:
```sql
-- Podstawowy plan wykonania
EXPLAIN 
SELECT e.first_name, e.last_name, d.name as department
FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE e.salary > 50000;

-- Szczegółowa analiza z rzeczywistymi czasami
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON)
SELECT e.first_name, e.last_name, d.name as department,
       AVG(e.salary) OVER (PARTITION BY d.name) as avg_dept_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE e.hire_date >= '2020-01-01'
ORDER BY e.salary DESC
LIMIT 100;

-- Analiza kosztów różnych wariantów zapytania
EXPLAIN (ANALYZE, BUFFERS)
WITH high_earners AS (
    SELECT employee_id, salary, department_id,
           RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as rank
    FROM employees
    WHERE salary > 60000
)
SELECT e.first_name, e.last_name, h.salary, d.name
FROM high_earners h
JOIN employees e ON h.employee_id = e.id
JOIN departments d ON h.department_id = d.id
WHERE h.rank <= 5;

-- Porównanie planów dla różnych predykatów
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM employees WHERE salary BETWEEN 40000 AND 80000;

EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM employees WHERE salary >= 40000 AND salary <= 80000;
```

#### Interpretacja planu wykonania:
```sql
-- Przykład optymalizacji na podstawie planu
-- PRZED: Slow query z Sequential Scan
EXPLAIN ANALYZE
SELECT e.first_name, e.last_name, e.salary
FROM employees e
WHERE e.email LIKE '%@company.com'
AND e.hire_date > '2022-01-01';
/*
Seq Scan on employees e  (cost=0.00..2584.00 rows=50 width=68) 
                        (actual time=0.123..45.234 rows=1847 loops=1)
  Filter: ((email ~~ '%@company.com'::text) AND (hire_date > '2022-01-01'::date))
  Rows Removed by Filter: 8153
Planning Time: 0.234 ms
Execution Time: 45.567 ms
*/

-- Analiza problemu - brak indeksu na email i hire_date
-- Rozwiązanie: Tworzenie odpowiednich indeksów
CREATE INDEX CONCURRENTLY idx_employees_email_pattern 
ON employees USING gin(email gin_trgm_ops);

CREATE INDEX CONCURRENTLY idx_employees_hire_date 
ON employees(hire_date) WHERE hire_date > '2020-01-01';

-- PO optymalizacji:
EXPLAIN ANALYZE
SELECT e.first_name, e.last_name, e.salary
FROM employees e
WHERE e.email LIKE '%@company.com'
AND e.hire_date > '2022-01-01';
/*
Bitmap Heap Scan on employees e  (cost=85.45..234.12 rows=50 width=68) 
                                (actual time=2.123..3.456 rows=1847 loops=1)
  Recheck Cond: (hire_date > '2022-01-01'::date)
  Filter: (email ~~ '%@company.com'::text)
  ->  Bitmap Index Scan on idx_employees_hire_date  (cost=0.00..85.43 rows=2000 width=0) 
                                                   (actual time=1.234..1.234 rows=2000 loops=1)
Planning Time: 0.345 ms
Execution Time: 3.789 ms  -- 12x szybciej!
*/
```

### 2. **Optymalizacja JOIN-ów**

#### Strategie optymalizacji JOIN:
```sql
-- Analiza różnych typów JOIN
-- Hash Join vs Nested Loop vs Merge Join

-- Optymalna kolejność JOIN (mniejsze tabele pierwsze)
EXPLAIN ANALYZE
SELECT p.name as project, e.first_name, e.last_name, d.name as department
FROM projects p
JOIN project_assignments pa ON p.id = pa.project_id
JOIN employees e ON pa.employee_id = e.id
JOIN departments d ON e.department_id = d.id
WHERE p.status = 'active'
AND e.salary > 70000;

-- Optymalizacja poprzez zmianę kolejności
EXPLAIN ANALYZE
SELECT p.name as project, e.first_name, e.last_name, d.name as department
FROM (
    SELECT id, name FROM projects WHERE status = 'active'
) p
JOIN project_assignments pa ON p.id = pa.project_id
JOIN (
    SELECT id, first_name, last_name, department_id 
    FROM employees WHERE salary > 70000
) e ON pa.employee_id = e.id
JOIN departments d ON e.department_id = d.id;

-- Wykorzystanie EXISTS zamiast JOIN gdy nie potrzebujemy danych
-- ZAMIAST:
SELECT DISTINCT e.first_name, e.last_name
FROM employees e
JOIN project_assignments pa ON e.id = pa.employee_id
JOIN projects p ON pa.project_id = p.id
WHERE p.status = 'active';

-- LEPIEJ:
SELECT e.first_name, e.last_name
FROM employees e
WHERE EXISTS (
    SELECT 1 FROM project_assignments pa
    JOIN projects p ON pa.project_id = p.id
    WHERE pa.employee_id = e.id AND p.status = 'active'
);

-- Lateral JOIN dla zaawansowanych przypadków
SELECT d.name, top_earners.first_name, top_earners.salary
FROM departments d
CROSS JOIN LATERAL (
    SELECT first_name, last_name, salary
    FROM employees e
    WHERE e.department_id = d.id
    ORDER BY salary DESC
    LIMIT 3
) top_earners;
```

### 3. **Optymalizacja podzapytań**

#### Przekształcanie podzapytań:
```sql
-- Optymalizacja skorelowanych podzapytań
-- WOLNE:
SELECT e.first_name, e.last_name, e.salary
FROM employees e
WHERE e.salary > (
    SELECT AVG(salary)
    FROM employees e2
    WHERE e2.department_id = e.department_id
);

-- SZYBSZE - z window function:
SELECT first_name, last_name, salary
FROM (
    SELECT first_name, last_name, salary,
           AVG(salary) OVER (PARTITION BY department_id) as avg_dept_salary
    FROM employees
) e
WHERE salary > avg_dept_salary;

-- Optymalizacja IN vs EXISTS
-- WOLNE dla dużych zbiorów:
SELECT e.first_name, e.last_name
FROM employees e
WHERE e.id IN (
    SELECT pa.employee_id
    FROM project_assignments pa
    JOIN projects p ON pa.project_id = p.id
    WHERE p.budget > 100000
);

-- SZYBSZE:
SELECT e.first_name, e.last_name
FROM employees e
WHERE EXISTS (
    SELECT 1
    FROM project_assignments pa
    JOIN projects p ON pa.project_id = p.id
    WHERE pa.employee_id = e.id AND p.budget > 100000
);

-- Window functions zamiast self-join
-- ZAMIAST:
SELECT e1.first_name, e1.last_name, e1.salary,
       e2.salary as next_highest_salary
FROM employees e1
LEFT JOIN employees e2 ON e1.department_id = e2.department_id
WHERE e2.salary = (
    SELECT MAX(salary)
    FROM employees e3
    WHERE e3.department_id = e1.department_id
    AND e3.salary < e1.salary
);

-- LEPIEJ:
SELECT first_name, last_name, salary,
       LAG(salary) OVER (PARTITION BY department_id ORDER BY salary DESC) as next_highest_salary
FROM employees;
```

## Strategie indeksowania

### 1. **Typy indeksów i ich zastosowania**

#### B-tree indeksy (domyślne):
```sql
-- Podstawowe indeksy B-tree
CREATE INDEX idx_employees_lastname ON employees(last_name);
CREATE INDEX idx_employees_salary ON employees(salary);
CREATE INDEX idx_employees_hire_date ON employees(hire_date);

-- Composite indeksy (ważna kolejność kolumn!)
-- Dla zapytań: WHERE department_id = ? AND salary > ?
CREATE INDEX idx_employees_dept_salary ON employees(department_id, salary);

-- Dla zapytań: WHERE salary > ? AND department_id = ?
-- Ten sam indeks będzie działał, ale mniej efektywnie dla drugiego zapytania

-- Conditional indeksy (częściowe)
CREATE INDEX idx_employees_high_salary 
ON employees(last_name, first_name) 
WHERE salary > 80000;

CREATE INDEX idx_projects_active 
ON projects(created_date, budget) 
WHERE status = 'active';

-- Indeksy z włączanymi kolumnami (INCLUDE)
CREATE INDEX idx_employees_dept_include 
ON employees(department_id) 
INCLUDE (first_name, last_name, salary);
```

#### Specialized indeksy:
```sql
-- GIN indeksy dla pełnotekstowego wyszukiwania
CREATE INDEX idx_employees_fulltext 
ON employees USING gin(to_tsvector('english', first_name || ' ' || last_name));

-- Wyszukiwanie:
SELECT first_name, last_name
FROM employees
WHERE to_tsvector('english', first_name || ' ' || last_name) 
      @@ to_tsquery('english', 'john & smith');

-- GIN indeksy dla JSONB
ALTER TABLE employees ADD COLUMN metadata JSONB;

CREATE INDEX idx_employees_metadata 
ON employees USING gin(metadata);

-- Wyszukiwanie w JSON:
SELECT first_name, last_name
FROM employees
WHERE metadata @> '{"skills": ["PostgreSQL"]}';

SELECT first_name, last_name
FROM employees
WHERE metadata ? 'certification';

-- GiST indeksy dla zakresów i geometrii
CREATE INDEX idx_employees_salary_range 
ON employees USING gist(int4range(salary::int, (salary * 1.1)::int));

-- trigram indeksy dla LIKE queries
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_employees_email_trgm 
ON employees USING gin(email gin_trgm_ops);

-- Szybkie wyszukiwanie LIKE:
SELECT first_name, last_name, email
FROM employees
WHERE email LIKE '%gmail%';

-- Hash indeksy (tylko dla równości)
CREATE INDEX idx_employees_id_hash 
ON employees USING hash(id);
```

### 2. **Monitoring wykorzystania indeksów**

#### Analiza użycia indeksów:
```sql
-- Statystyki wykorzystania indeksów
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Znajdowanie nieużywanych indeksów
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Analiza duplikujących się indeksów
WITH index_columns AS (
    SELECT 
        n.nspname as schema_name,
        t.relname as table_name,
        i.relname as index_name,
        array_agg(a.attname ORDER BY c.ordinality) as columns
    FROM pg_index ix
    JOIN pg_class i ON i.oid = ix.indexrelid
    JOIN pg_class t ON t.oid = ix.indrelid
    JOIN pg_namespace n ON n.oid = t.relnamespace
    JOIN unnest(ix.indkey) WITH ORDINALITY c(attnum, ordinality) ON true
    JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = c.attnum
    WHERE n.nspname = 'public'
    GROUP BY n.nspname, t.relname, i.relname
)
SELECT 
    schema_name,
    table_name,
    array_agg(index_name) as duplicate_indexes,
    columns
FROM index_columns
GROUP BY schema_name, table_name, columns
HAVING count(*) > 1;

-- Monitoring bloat indeksów
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
    pg_size_pretty(pg_relation_size(relid)) as table_size,
    round(100.0 * pg_relation_size(indexrelid) / pg_relation_size(relid), 1) as index_ratio
FROM pg_stat_user_indexes pgsui
JOIN pg_class pgc ON pgc.oid = pgsui.indexrelid
WHERE pg_relation_size(indexrelid) > 1000000  -- > 1MB
ORDER BY pg_relation_size(indexrelid) DESC;
```

## Optymalizacja konfiguracji PostgreSQL

### 1. **Parametry pamięci**

#### postgresql.conf - optymalizacja pamięci:
```bash
# Konfiguracja dla serwera z 16GB RAM

# Shared buffers - 25% całkowitej pamięci RAM
shared_buffers = 4GB

# Effective cache size - 75% RAM (pamięć dostępna dla cache OS + PostgreSQL)
effective_cache_size = 12GB

# Work mem - pamięć dla operacji sortowania/hash (per connection)
# Formuła: (RAM * 0.25) / max_connections
work_mem = 64MB

# Maintenance work mem - dla VACUUM, CREATE INDEX, etc.
maintenance_work_mem = 1GB

# WAL buffers - zwykle 16MB wystarczy
wal_buffers = 16MB

# Random page cost - dla SSD powinno być niższe
random_page_cost = 1.1  # SSD
# random_page_cost = 4.0  # HDD (domyślne)

# Effective IO concurrency - liczba równoległych operacji I/O
effective_io_concurrency = 200  # SSD
# effective_io_concurrency = 2   # HDD

# Max worker processes
max_worker_processes = 8
max_parallel_workers = 8
max_parallel_workers_per_gather = 4
max_parallel_maintenance_workers = 4
```

### 2. **Parametry połączeń i wydajności**

#### Optymalizacja połączeń:
```bash
# Connection settings
max_connections = 200
superuser_reserved_connections = 3

# Connection pooling (używaj PgBouncer!)
# PgBouncer config:
# pool_mode = transaction
# default_pool_size = 50
# max_client_conn = 1000

# Checkpoint settings - dla wydajności zapisu
checkpoint_completion_target = 0.9
checkpoint_timeout = 15min
max_wal_size = 4GB
min_wal_size = 1GB

# Background writer
bgwriter_delay = 200ms
bgwriter_lru_maxpages = 100
bgwriter_lru_multiplier = 2.0

# Autovacuum tuning
autovacuum = on
autovacuum_max_workers = 6
autovacuum_naptime = 30s
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_scale_factor = 0.1
autovacuum_analyze_threshold = 50
autovacuum_analyze_scale_factor = 0.05

# Vacuum cost delay (throttling)
autovacuum_vacuum_cost_delay = 10ms
autovacuum_vacuum_cost_limit = 1000

# Statistics
track_activities = on
track_counts = on
track_functions = all
track_io_timing = on
```

### 3. **Monitoring wydajności**

#### System monitoring queries:
```sql
-- Aktywne połączenia i zapytania
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    now() - query_start as duration,
    query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;

-- Top 10 najwolniejszych zapytań
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    stddev_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Analiza cache hit ratio
SELECT 
    'buffer hit rate' as metric,
    round(100.0 * sum(blks_hit) / nullif(sum(blks_hit) + sum(blks_read), 0), 2) as percentage
FROM pg_stat_database
UNION ALL
SELECT 
    'index hit rate' as metric,
    round(100.0 * sum(idx_blks_hit) / nullif(sum(idx_blks_hit) + sum(idx_blks_read), 0), 2) as percentage
FROM pg_statio_user_indexes;

-- Analiza wait events
SELECT 
    wait_event_type,
    wait_event,
    count(*) as count,
    round(100.0 * count(*) / sum(count(*)) OVER (), 2) as percentage
FROM pg_stat_activity
WHERE wait_event IS NOT NULL
GROUP BY wait_event_type, wait_event
ORDER BY count DESC;

-- Vacuum i analyze statistics
SELECT 
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze,
    vacuum_count,
    autovacuum_count,
    analyze_count,
    autoanalyze_count,
    n_dead_tup,
    n_live_tup,
    round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 2) as dead_tuple_percent
FROM pg_stat_user_tables
WHERE n_dead_tup > 0
ORDER BY dead_tuple_percent DESC;
```

## Techniki optymalizacji zaawansowanej

### 1. **Partycjonowanie tabel**

#### Range partitioning (przykład dla danych czasowych):
```sql
-- Główna tabela (partitioned)
CREATE TABLE sales (
    id SERIAL,
    sale_date DATE NOT NULL,
    product_id INTEGER,
    quantity INTEGER,
    amount DECIMAL(10,2),
    customer_id INTEGER
) PARTITION BY RANGE (sale_date);

-- Partycje miesięczne
CREATE TABLE sales_2024_01 PARTITION OF sales
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE sales_2024_02 PARTITION OF sales
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

CREATE TABLE sales_2024_03 PARTITION OF sales
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

-- Domyślna partycja dla przyszłych danych
CREATE TABLE sales_default PARTITION OF sales DEFAULT;

-- Indeksy na partycjach
CREATE INDEX idx_sales_2024_01_product ON sales_2024_01(product_id);
CREATE INDEX idx_sales_2024_02_product ON sales_2024_02(product_id);
CREATE INDEX idx_sales_2024_03_product ON sales_2024_03(product_id);

-- Automatyczne tworzenie partycji (pg_partman extension)
SELECT partman.create_parent(
    p_parent_table => 'public.sales',
    p_control => 'sale_date',
    p_type => 'range',
    p_interval => 'monthly',
    p_premake => 3
);

-- Query korzystające z partition pruning
EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, sum(amount)
FROM sales
WHERE sale_date >= '2024-02-01' AND sale_date < '2024-03-01'
GROUP BY product_id;
```

#### Hash partitioning (dla równomiernego rozłożenia):
```sql
-- Partycjonowanie hash dla customer_data
CREATE TABLE customer_data (
    customer_id INTEGER,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    registration_date DATE
) PARTITION BY HASH (customer_id);

-- 4 partycje hash
CREATE TABLE customer_data_0 PARTITION OF customer_data
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE customer_data_1 PARTITION OF customer_data
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE customer_data_2 PARTITION OF customer_data
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE customer_data_3 PARTITION OF customer_data
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

### 2. **Materialized Views**

#### Optymalizacja przez materialized views:
```sql
-- Wolne zapytanie analityczne
SELECT 
    d.name as department,
    extract(year from e.hire_date) as hire_year,
    count(*) as employee_count,
    avg(e.salary) as avg_salary,
    max(e.salary) as max_salary,
    min(e.salary) as min_salary
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.name, extract(year from e.hire_date);

-- Tworzenie materialized view
CREATE MATERIALIZED VIEW mv_department_stats AS
SELECT 
    d.id as department_id,
    d.name as department_name,
    extract(year from e.hire_date) as hire_year,
    count(*) as employee_count,
    avg(e.salary) as avg_salary,
    max(e.salary) as max_salary,
    min(e.salary) as min_salary,
    current_timestamp as last_updated
FROM employees e
JOIN departments d ON e.department_id = d.id
GROUP BY d.id, d.name, extract(year from e.hire_date);

-- Indeks na materialized view
CREATE INDEX idx_mv_dept_stats_dept_year 
ON mv_department_stats(department_id, hire_year);

-- Odświeżanie danych
REFRESH MATERIALIZED VIEW mv_department_stats;

-- Concurrent refresh (nie blokuje zapytań)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_department_stats;

-- Automatyczne odświeżanie (trigger-based)
CREATE OR REPLACE FUNCTION refresh_department_stats()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_department_stats;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER refresh_stats_trigger
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_department_stats();
```

### 3. **Connection Pooling i Cache**

#### PgBouncer konfiguracja:
```ini
[databases]
company_db = host=localhost port=5432 dbname=company_db user=app_user

[pgbouncer]
pool_mode = transaction
listen_port = 6432
listen_addr = *
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

# Pool settings
default_pool_size = 50
max_client_conn = 1000
reserve_pool_size = 10
reserve_pool_timeout = 5

# Timing
server_lifetime = 3600
server_idle_timeout = 600
server_connect_timeout = 15
server_login_retry = 15

# Logging
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1

# Stats
stats_period = 60
```

#### Redis cache integration:
```python
import redis
import json
import psycopg2
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def cache_result(expiration=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Tworzenie klucza cache
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Sprawdzenie cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Wykonanie zapytania
            result = func(*args, **kwargs)
            
            # Zapisanie w cache
            redis_client.setex(
                cache_key, 
                expiration, 
                json.dumps(result, default=str)
            )
            
            return result
        return wrapper
    return decorator

@cache_result(expiration=1800)  # 30 minut
def get_department_statistics(department_id):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    count(*) as employee_count,
                    avg(salary) as avg_salary,
                    max(salary) as max_salary,
                    min(salary) as min_salary
                FROM employees
                WHERE department_id = %s
            """, (department_id,))
            
            result = cur.fetchone()
            return {
                'employee_count': result[0],
                'avg_salary': float(result[1]),
                'max_salary': float(result[2]),
                'min_salary': float(result[3])
            }

# Invalidacja cache przy zmianach
def invalidate_department_cache(department_id):
    pattern = f"get_department_statistics:*{department_id}*"
    for key in redis_client.scan_iter(match=pattern):
        redis_client.delete(key)
```

## Pułapki egzaminacyjne

1. **Indeksy composite** - kolejność kolumn ma znaczenie krytyczne
2. **EXPLAIN vs EXPLAIN ANALYZE** - pierwszy pokazuje plan, drugi rzeczywiste wykonanie  
3. **Selectivity** - indeksy są nieskuteczne dla kolumn o niskiej selektywności
4. **Index bloat** - indeksy wymagają okresowego REINDEX
5. **Parallel queries** - nie zawsze są szybsze, zależą od work_mem
6. **VACUUM** - brak autovacuum może drastycznie obniżyć wydajność
7. **Connection pooling** - każde połączenie PostgreSQL zużywa ~10MB RAM
8. **Cache hit ratio** - powinien być > 95% dla shared_buffers
9. **Query cache** - PostgreSQL nie ma query cache (w przeciwieństwie do MySQL)
10. **Prepared statements** - mogą być wolniejsze dla zapytań z różną selektywnością