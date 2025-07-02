# 📊 FUNKCJE AGREGUJĄCE - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Funkcje agregujące przetwarzają zbiory wierszy i zwracają pojedynczą wartość. Podstawowe funkcje:

1. **COUNT(*)** - liczba wierszy, **COUNT(kolumna)** - ignoruje NULL
2. **SUM()** - suma wartości numerycznych
3. **AVG()** - średnia arytmetyczna
4. **MIN()/MAX()** - wartości minimalne/maksymalne
5. **GROUP BY** - grupowanie wyników
6. **HAVING** - filtrowanie grup (nie wierszy)

Zaawansowane: ROLLUP, CUBE, GROUPING SETS dla wielopoziomowych analiz. Funkcje okienkowe pozwalają na agregację bez grupowania wierszy."

## ✍️ CO NAPISAĆ NA KARTCE

```sql
FUNKCJE AGREGUJĄCE - PODSTAWY:

PODSTAWOWE FUNKCJE:
COUNT(*) - wszystkie wiersze (z NULL)
COUNT(column) - wiersze z NOT NULL w kolumnie
SUM(column) - suma wartości (ignoruje NULL)
AVG(column) - średnia (ignoruje NULL)
MIN(column) - minimum
MAX(column) - maksimum

GROUP BY:
SELECT column1, COUNT(*), AVG(column2)
FROM table
GROUP BY column1;

HAVING - filtrowanie grup:
SELECT department, AVG(salary)
FROM employees
GROUP BY department
HAVING AVG(salary) > 50000;

ZAAWANSOWANE GRUPOWANIE:
• ROLLUP - hierarchiczne podsumowania
• CUBE - wszystkie kombinacje grup
• GROUPING SETS - wybrane kombinacje

PRZYKŁADY:
GROUP BY ROLLUP(region, city) -- region+city, region, total
GROUP BY CUBE(year, quarter) -- wszystkie kombinacje
GROUP BY GROUPING SETS((year),(quarter),()) -- tylko wybrane

FUNKCJE STRING AGGREGATION:
STRING_AGG(column, separator) - PostgreSQL
GROUP_CONCAT(column) - MySQL
LISTAGG(column, separator) - Oracle/SQL Server

WINDOW FUNCTIONS vs GROUP BY:
-- GROUP BY redukuje wiersze
SELECT dept, COUNT(*) FROM emp GROUP BY dept;

-- Window function zachowuje wiersze
SELECT name, dept, COUNT(*) OVER (PARTITION BY dept)
FROM emp;

DISTINCT w agregacji:
COUNT(DISTINCT column) - unikalne wartości
SUM(DISTINCT column) - suma unikalnych

NULL HANDLING:
• Funkcje agregujące ignorują NULL (oprócz COUNT(*))
• COALESCE(column, 0) dla obsługi NULL
• FILTER clause: COUNT(*) FILTER (WHERE condition)
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- KOMPLEKSOWA DEMONSTRACJA FUNKCJI AGREGUJĄCYCH

-- Przygotowanie tabel testowych
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    position VARCHAR(50),
    salary DECIMAL(10,2),
    hire_date DATE,
    manager_id INT,
    region VARCHAR(50)
);

CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES employees(id),
    sale_date DATE,
    amount DECIMAL(10,2),
    product_category VARCHAR(50),
    customer_type VARCHAR(20)
);

-- Dane testowe
INSERT INTO employees VALUES
(1, 'Jan Kowalski', 'IT', 'Developer', 8000, '2020-01-15', NULL, 'North'),
(2, 'Anna Nowak', 'IT', 'Senior Developer', 12000, '2019-03-20', 1, 'North'),
(3, 'Piotr Wiśniewski', 'Sales', 'Sales Rep', 6000, '2021-06-10', NULL, 'South'),
(4, 'Maria Kowalczyk', 'Sales', 'Senior Sales Rep', 9000, '2018-09-05', 3, 'South'),
(5, 'Tomasz Zieliński', 'HR', 'HR Specialist', 7000, '2020-11-12', NULL, 'North'),
(6, 'Katarzyna Nowakowa', 'IT', 'Developer', 8500, '2021-02-28', 2, 'East'),
(7, 'Robert Kowalczyk', 'Sales', 'Sales Rep', 5500, '2022-01-10', 4, 'West'),
(8, 'Agnieszka Wiśniewska', 'HR', 'HR Manager', 11000, '2017-05-15', NULL, 'North'),
(9, 'Michał Zielińskii', 'IT', 'Team Lead', 15000, '2016-08-30', NULL, 'East'),
(10, 'Joanna Kowalska', 'Sales', 'Sales Manager', 13000, '2019-12-01', NULL, 'West');

INSERT INTO sales VALUES
(1, 3, '2024-01-05', 2500, 'Electronics', 'B2B'),
(2, 4, '2024-01-07', 3200, 'Software', 'B2C'),
(3, 7, '2024-01-10', 1800, 'Electronics', 'B2B'),
(4, 10, '2024-01-12', 4500, 'Software', 'Enterprise'),
(5, 3, '2024-01-15', 2100, 'Hardware', 'B2C'),
(6, 4, '2024-01-18', 3800, 'Software', 'Enterprise'),
(7, 7, '2024-01-20', 1500, 'Electronics', 'B2C'),
(8, 10, '2024-01-22', 5200, 'Software', 'Enterprise'),
(9, 3, '2024-01-25', 2300, 'Hardware', 'B2B'),
(10, 4, '2024-01-28', 2900, 'Electronics', 'B2C');

-- 1. PODSTAWOWE FUNKCJE AGREGUJĄCE

-- Statystyki pracowników
SELECT 
    COUNT(*) as total_employees,
    COUNT(manager_id) as employees_with_managers,  -- NULL ignored
    COUNT(DISTINCT department) as departments_count,
    AVG(salary) as average_salary,
    MIN(salary) as min_salary,
    MAX(salary) as max_salary,
    SUM(salary) as total_salary_cost,
    MIN(hire_date) as first_hire,
    MAX(hire_date) as last_hire
FROM employees;

-- Porównanie COUNT(*) vs COUNT(column)
SELECT 
    department,
    COUNT(*) as all_employees,
    COUNT(manager_id) as employees_with_manager,
    COUNT(DISTINCT position) as unique_positions
FROM employees
GROUP BY department;

-- 2. GROUP BY - GRUPOWANIE PODSTAWOWE

-- Statystyki po departamentach
SELECT 
    department,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary,
    MIN(salary) as min_salary,
    MAX(salary) as max_salary,
    SUM(salary) as dept_salary_cost,
    ROUND(AVG(EXTRACT(YEAR FROM AGE(hire_date))), 1) as avg_years_experience
FROM employees
GROUP BY department
ORDER BY avg_salary DESC;

-- Grupowanie po wielu kolumnach
SELECT 
    department,
    region,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary,
    MAX(salary) as max_salary
FROM employees
GROUP BY department, region
ORDER BY department, region;

-- 3. HAVING - FILTROWANIE GRUP

-- Departamenty z więcej niż 2 pracownikami i średnią pensją > 8000
SELECT 
    department,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary,
    SUM(salary) as total_cost
FROM employees
GROUP BY department
HAVING COUNT(*) > 2 AND AVG(salary) > 8000;

-- Regiony z najwyższymi kosztami wynagrodzeń
SELECT 
    region,
    COUNT(*) as employee_count,
    SUM(salary) as total_salary_cost,
    AVG(salary) as avg_salary
FROM employees
GROUP BY region
HAVING SUM(salary) > 20000
ORDER BY total_salary_cost DESC;

-- 4. FUNKCJE AGREGUJĄCE Z DISTINCT

-- Unikalne wartości w agregacji
SELECT 
    COUNT(DISTINCT department) as unique_departments,
    COUNT(DISTINCT position) as unique_positions,
    COUNT(DISTINCT region) as unique_regions,
    -- Średnia z unikalnych pensji (eliminuje duplikaty)
    AVG(DISTINCT salary) as avg_unique_salaries,
    -- Liczba unikalnych poziomów pensji
    COUNT(DISTINCT salary) as unique_salary_levels
FROM employees;

-- Analiza unikalnych poziomów pensji per departament
SELECT 
    department,
    COUNT(*) as total_employees,
    COUNT(DISTINCT salary) as unique_salary_levels,
    AVG(salary) as avg_salary,
    AVG(DISTINCT salary) as avg_unique_salary
FROM employees
GROUP BY department;

-- 5. STRING AGGREGATION

-- Łączenie wartości tekstowych (PostgreSQL)
SELECT 
    department,
    COUNT(*) as employee_count,
    STRING_AGG(name, ', ' ORDER BY salary DESC) as employees_list,
    STRING_AGG(DISTINCT position, ', ') as positions_in_dept,
    ARRAY_AGG(salary ORDER BY salary DESC) as salaries_array
FROM employees
GROUP BY department;

-- Szczegółowa lista z formatowaniem
SELECT 
    region,
    STRING_AGG(
        name || ' (' || department || ', ' || 
        TO_CHAR(salary, 'FM999,999') || ' PLN)', 
        E'\n' 
        ORDER BY department, salary DESC
    ) as detailed_employee_list
FROM employees
GROUP BY region;

-- 6. ZAAWANSOWANE GRUPOWANIE - ROLLUP

-- ROLLUP - hierarchiczne podsumowania
SELECT 
    department,
    region,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary,
    SUM(salary) as total_salary
FROM employees
GROUP BY ROLLUP(department, region)
ORDER BY department NULLS LAST, region NULLS LAST;

-- ROLLUP z identyfikacją poziomów
SELECT 
    CASE 
        WHEN GROUPING(department) = 1 AND GROUPING(region) = 1 THEN 'GRAND TOTAL'
        WHEN GROUPING(region) = 1 THEN 'DEPARTMENT TOTAL: ' || department
        ELSE department || ' - ' || region
    END as grouping_level,
    COUNT(*) as employee_count,
    SUM(salary) as total_salary,
    AVG(salary) as avg_salary
FROM employees
GROUP BY ROLLUP(department, region)
ORDER BY department NULLS LAST, region NULLS LAST;

-- 7. CUBE - WSZYSTKIE KOMBINACJE

-- CUBE - wszystkie możliwe kombinacje grupowania
SELECT 
    department,
    position,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary,
    GROUPING(department) as dept_grouping,
    GROUPING(position) as pos_grouping
FROM employees
GROUP BY CUBE(department, position)
ORDER BY GROUPING(department), GROUPING(position), department, position;

-- CUBE z opisowymi etykietami
SELECT 
    CASE 
        WHEN GROUPING(department) = 1 AND GROUPING(position) = 1 THEN 'ALL DEPARTMENTS & POSITIONS'
        WHEN GROUPING(department) = 1 THEN 'ALL DEPARTMENTS, Position: ' || position
        WHEN GROUPING(position) = 1 THEN 'Department: ' || department || ', ALL POSITIONS'
        ELSE 'Department: ' || department || ', Position: ' || position
    END as analysis_level,
    COUNT(*) as employee_count,
    ROUND(AVG(salary), 2) as avg_salary
FROM employees
GROUP BY CUBE(department, position)
ORDER BY GROUPING(department), GROUPING(position);

-- 8. GROUPING SETS - WYBRANE KOMBINACJE

-- GROUPING SETS - tylko konkretne kombinacje grupowania
SELECT 
    department,
    region,
    position,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary
FROM employees
GROUP BY GROUPING SETS (
    (department),           -- tylko po departamencie
    (region),              -- tylko po regionie  
    (department, region),  -- department + region
    ()                     -- grand total
)
ORDER BY 
    GROUPING(department), 
    GROUPING(region), 
    GROUPING(position),
    department, 
    region;

-- 9. WINDOW FUNCTIONS vs GROUP BY

-- Porównanie: GROUP BY redukuje wiersze
SELECT 
    department,
    COUNT(*) as dept_employee_count,
    AVG(salary) as dept_avg_salary
FROM employees
GROUP BY department;

-- Window functions zachowują wszystkie wiersze
SELECT 
    name,
    department,
    salary,
    COUNT(*) OVER (PARTITION BY department) as dept_employee_count,
    AVG(salary) OVER (PARTITION BY department) as dept_avg_salary,
    salary - AVG(salary) OVER (PARTITION BY department) as salary_vs_dept_avg,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) as salary_rank_in_dept
FROM employees
ORDER BY department, salary DESC;

-- 10. FUNKCJE AGREGUJĄCE Z FILTROWANIEM

-- FILTER clause (PostgreSQL)
SELECT 
    department,
    COUNT(*) as total_employees,
    COUNT(*) FILTER (WHERE salary > 8000) as high_earners,
    COUNT(*) FILTER (WHERE hire_date >= '2020-01-01') as recent_hires,
    AVG(salary) FILTER (WHERE position LIKE '%Senior%') as avg_senior_salary,
    SUM(salary) FILTER (WHERE region = 'North') as north_salary_cost
FROM employees
GROUP BY department;

-- Conditional aggregation with CASE
SELECT 
    department,
    COUNT(*) as total_employees,
    SUM(CASE WHEN salary > 8000 THEN 1 ELSE 0 END) as high_earners,
    SUM(CASE WHEN hire_date >= '2020-01-01' THEN 1 ELSE 0 END) as recent_hires,
    AVG(CASE WHEN position LIKE '%Senior%' THEN salary END) as avg_senior_salary,
    SUM(CASE WHEN region = 'North' THEN salary ELSE 0 END) as north_salary_cost
FROM employees
GROUP BY department;

-- 11. COMPLEX AGREGACJE Z SUBQUERIES

-- Porównanie z globalnymi statystykami
SELECT 
    department,
    COUNT(*) as dept_count,
    AVG(salary) as dept_avg_salary,
    (SELECT AVG(salary) FROM employees) as global_avg_salary,
    AVG(salary) - (SELECT AVG(salary) FROM employees) as avg_salary_diff,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM employees) as dept_percentage
FROM employees
GROUP BY department;

-- Ranking departamentów
SELECT 
    dept_stats.*,
    RANK() OVER (ORDER BY avg_salary DESC) as salary_rank,
    RANK() OVER (ORDER BY total_cost DESC) as cost_rank
FROM (
    SELECT 
        department,
        COUNT(*) as employee_count,
        AVG(salary) as avg_salary,
        SUM(salary) as total_cost,
        MIN(salary) as min_salary,
        MAX(salary) as max_salary
    FROM employees
    GROUP BY department
) dept_stats;

-- 12. ANALIZA SPRZEDAŻY Z AGREGACJĄ

-- Statystyki sprzedaży per pracownik
SELECT 
    e.name,
    e.department,
    COUNT(s.id) as sales_count,
    COALESCE(SUM(s.amount), 0) as total_sales,
    COALESCE(AVG(s.amount), 0) as avg_sale_amount,
    COALESCE(MAX(s.amount), 0) as max_sale,
    COALESCE(MIN(s.amount), 0) as min_sale
FROM employees e
LEFT JOIN sales s ON e.id = s.employee_id
GROUP BY e.id, e.name, e.department
ORDER BY total_sales DESC;

-- Analiza sprzedaży po kategoriach i typach klientów
SELECT 
    product_category,
    customer_type,
    COUNT(*) as sales_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_sale_amount,
    MIN(amount) as min_sale,
    MAX(amount) as max_sale,
    ROUND(STDDEV(amount), 2) as amount_stddev
FROM sales
GROUP BY product_category, customer_type
ORDER BY total_revenue DESC;

-- 13. PERCENTYLE I STATYSTYKI ROZKŁADU

-- Używając funkcji okienkowych dla percentyli
SELECT 
    department,
    COUNT(*) as employee_count,
    MIN(salary) as min_salary,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY salary) as q1_salary,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) as median_salary,
    AVG(salary) as mean_salary,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY salary) as q3_salary,
    MAX(salary) as max_salary,
    STDDEV(salary) as salary_stddev
FROM employees
GROUP BY department;

-- 14. TEMPORAL AGGREGATIONS

-- Analiza wynagrodzeń w czasie (simulacja zmian)
WITH monthly_stats AS (
    SELECT 
        DATE_TRUNC('month', hire_date) as hire_month,
        COUNT(*) as new_hires,
        AVG(salary) as avg_starting_salary,
        SUM(salary) as monthly_salary_increase
    FROM employees
    GROUP BY DATE_TRUNC('month', hire_date)
)
SELECT 
    hire_month,
    new_hires,
    avg_starting_salary,
    monthly_salary_increase,
    SUM(new_hires) OVER (ORDER BY hire_month) as cumulative_hires,
    SUM(monthly_salary_increase) OVER (ORDER BY hire_month) as cumulative_salary_cost
FROM monthly_stats
ORDER BY hire_month;

-- 15. PERFORMANCE OPTIMIZATION

-- Indeksy wspierające agregację
CREATE INDEX idx_employees_dept_salary ON employees(department, salary);
CREATE INDEX idx_employees_region_hire_date ON employees(region, hire_date);

-- Explain query performance
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    department,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary,
    SUM(salary) as total_salary
FROM employees
GROUP BY department;

-- Materialized view dla częstych agregacji
CREATE MATERIALIZED VIEW mv_department_stats AS
SELECT 
    department,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary,
    MIN(salary) as min_salary,
    MAX(salary) as max_salary,
    SUM(salary) as total_salary_cost,
    CURRENT_TIMESTAMP as last_updated
FROM employees
GROUP BY department;

-- Index na materialized view
CREATE INDEX idx_mv_dept_stats_dept ON mv_department_stats(department);

-- Refresh materialized view
REFRESH MATERIALIZED VIEW mv_department_stats;

-- 16. ZAAWANSOWANE CASE STUDIES

-- Complex business analysis
SELECT 
    e.department,
    e.region,
    COUNT(*) as employee_count,
    -- Salary analysis
    AVG(e.salary) as avg_salary,
    COUNT(*) FILTER (WHERE e.salary > 10000) as high_earners,
    -- Performance analysis (sales employees only)
    COUNT(s.id) as total_sales,
    COALESCE(SUM(s.amount), 0) as total_revenue,
    CASE 
        WHEN COUNT(s.id) > 0 THEN COALESCE(SUM(s.amount), 0) / COUNT(s.id)
        ELSE 0
    END as avg_sale_per_transaction,
    -- Efficiency metrics
    CASE 
        WHEN COUNT(s.id) > 0 THEN COALESCE(SUM(s.amount), 0) / COUNT(*)
        ELSE 0
    END as revenue_per_employee
FROM employees e
LEFT JOIN sales s ON e.id = s.employee_id
GROUP BY e.department, e.region
HAVING COUNT(*) >= 1  -- At least 1 employee in group
ORDER BY revenue_per_employee DESC;
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: COUNT(kolumna) ignoruje NULL, COUNT(*) liczy wszystkie wiersze
2. **UWAGA**: HAVING filtruje grupy, WHERE filtruje wiersze przed grupowaniem
3. **BŁĄD**: Wszystkie kolumny w SELECT muszą być w GROUP BY lub być agregowane
4. **WAŻNE**: Funkcje agregujące (oprócz COUNT(*)) ignorują wartości NULL
5. **PUŁAPKA**: DISTINCT w funkcjach agregujących może znacznie wpływać na wydajność

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Aggregate functions** - funkcje agregujące
- **GROUP BY clause** - klauzula grupowania
- **HAVING vs WHERE** - filtrowanie grup vs wierszy
- **ROLLUP/CUBE/GROUPING SETS** - zaawansowane grupowanie
- **Window functions** - funkcje okienkowe
- **String aggregation** - agregacja tekstów
- **Statistical functions** - funkcje statystyczne
- **NULL handling** - obsługa wartości NULL

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **24-wartosc-null** - NULL w funkcjach agregujących
- **30-sql-dml-zaawansowany** - window functions
- **21-sql-joiny** - agregacja z JOIN'ami
- **42-optymalizacja-wydajnosci** - optymalizacja agregacji
- **31-subqueries** - agregacja w subqueries