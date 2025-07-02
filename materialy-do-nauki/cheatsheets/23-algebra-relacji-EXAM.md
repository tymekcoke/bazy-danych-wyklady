# 🔢 ALGEBRA RELACJI - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Algebra relacji to formalny język zapytań dla modelu relacyjnego, składający się z operatorów manipulujących relacjami. Operatory podstawowe:

1. **Selekcja (σ)** - wybiera wiersze spełniające warunek
2. **Projekcja (π)** - wybiera kolumny  
3. **Złączenie (⋈)** - łączy relacje na podstawie wspólnych atrybutów
4. **Suma, przecięcie, różnica (∪, ∩, -)** - operacje zbiorowe
5. **Iloczyn kartezjański (×)** - wszystkie kombinacje krotek

Algebra relacji jest podstawą teoretyczną dla SQL i systemów zapytań relacyjnych."

## ✍️ CO NAPISAĆ NA KARTCE

```
ALGEBRA RELACJI - OPERATORY PODSTAWOWE:

NOTACJA:
R, S - relacje (tabele)
σ - selekcja (selection)  
π - projekcja (projection)
⋈ - złączenie (join)
∪ - suma (union)
∩ - przecięcie (intersection)  
- - różnica (difference)
× - iloczyn kartezjański (cartesian product)
÷ - dzielenie (division)

1. SELEKCJA: σ_warunek(R)
   Wybiera wiersze spełniające warunek
   σ_salary>5000(Employee) 
   SQL: SELECT * FROM Employee WHERE salary > 5000;

2. PROJEKCJA: π_atrybuty(R)
   Wybiera określone kolumny
   π_name,salary(Employee)
   SQL: SELECT name, salary FROM Employee;

3. ZŁĄCZENIE: R ⋈_warunek S
   Łączy relacje na podstawie warunku
   Employee ⋈_Employee.dept_id=Department.id Department
   SQL: SELECT * FROM Employee JOIN Department 
        ON Employee.dept_id = Department.id;

4. SUMA: R ∪ S  
   Wszystkie krotki z R i S (bez duplikatów)
   Warunek: R i S mają ten sam schemat
   SQL: SELECT * FROM R UNION SELECT * FROM S;

5. PRZECIĘCIE: R ∩ S
   Krotki występujące w obu relacjach
   SQL: SELECT * FROM R INTERSECT SELECT * FROM S;

6. RÓŻNICA: R - S
   Krotki z R które nie występują w S  
   SQL: SELECT * FROM R EXCEPT SELECT * FROM S;

7. ILOCZYN KARTEZJAŃSKI: R × S
   Wszystkie kombinacje krotek z R i S
   SQL: SELECT * FROM R CROSS JOIN S;

8. DZIELENIE: R ÷ S
   Krotki z R które są związane ze wszystkimi krotkami z S
   Brak bezpośredniego odpowiednika w SQL

PRZYKŁAD ZŁOŻONEGO WYRAŻENIA:
π_name,salary(σ_dept='IT'(Employee ⋈ Department))

SQL: SELECT e.name, e.salary 
     FROM Employee e JOIN Department d ON e.dept_id = d.id
     WHERE d.name = 'IT';
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- DEMONSTRACJA ALGEBRY RELACJI W SQL

-- Przygotowanie relacji testowych
CREATE TABLE Employee (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    salary DECIMAL(10,2),
    dept_id INT
);

CREATE TABLE Department (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    budget DECIMAL(12,2)
);

CREATE TABLE Project (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    budget DECIMAL(12,2)
);

CREATE TABLE Assignment (
    emp_id INT,
    proj_id INT,
    hours INT,
    PRIMARY KEY (emp_id, proj_id)
);

-- Dane testowe
INSERT INTO Employee VALUES 
(1, 'Jan Kowalski', 6000, 1),
(2, 'Anna Nowak', 7000, 1),
(3, 'Piotr Wiśniewski', 5500, 2),
(4, 'Maria Kowalczyk', 8000, 2),
(5, 'Tomasz Zieliński', 5000, 1);

INSERT INTO Department VALUES 
(1, 'IT', 500000),
(2, 'HR', 200000),
(3, 'Finance', 300000);

INSERT INTO Project VALUES 
(1, 'Website', 100000),
(2, 'Mobile App', 150000),
(3, 'Database', 80000);

INSERT INTO Assignment VALUES 
(1, 1, 40), (1, 3, 20),
(2, 1, 30), (2, 2, 35),
(3, 2, 25), (4, 1, 45),
(5, 3, 30);

-- 1. SELEKCJA (σ) - wybór wierszy

-- σ_salary>6000(Employee)
SELECT * FROM Employee WHERE salary > 6000;

-- σ_dept_id=1 AND salary>=6000(Employee)  
SELECT * FROM Employee WHERE dept_id = 1 AND salary >= 6000;

-- Selekcja z warunkiem tekstowym
-- σ_name LIKE 'A%'(Employee)
SELECT * FROM Employee WHERE name LIKE 'A%';

-- 2. PROJEKCJA (π) - wybór kolumn

-- π_name,salary(Employee)
SELECT name, salary FROM Employee;

-- π_name(Department)
SELECT name FROM Department;

-- Projekcja z eliminacją duplikatów
-- π_dept_id(Employee)
SELECT DISTINCT dept_id FROM Employee;

-- 3. ZŁĄCZENIE (⋈) - łączenie relacji

-- Employee ⋈_Employee.dept_id=Department.id Department
SELECT e.name as employee_name, e.salary, d.name as department_name
FROM Employee e JOIN Department d ON e.dept_id = d.id;

-- Natural Join (automatyczne łączenie po wspólnych atrybutach)
-- W algebrze relacji: Employee ⋈ Department (gdyby była wspólna kolumna)
CREATE VIEW emp_dept AS 
SELECT e.id as emp_id, e.name as emp_name, e.salary, e.dept_id,
       d.name as dept_name, d.budget
FROM Employee e JOIN Department d ON e.dept_id = d.id;

-- Theta Join z warunkiem
-- Employee ⋈_Employee.salary > Department.budget/100 Department
SELECT e.name, e.salary, d.name, d.budget
FROM Employee e JOIN Department d ON e.salary > d.budget / 100;

-- 4. OPERACJE ZBIOROWE

-- Przygotowanie relacji o tym samym schemacie
CREATE VIEW high_earners AS
SELECT name, salary FROM Employee WHERE salary > 6500;

CREATE VIEW it_employees AS  
SELECT e.name, e.salary FROM Employee e 
JOIN Department d ON e.dept_id = d.id WHERE d.name = 'IT';

-- SUMA (∪): high_earners ∪ it_employees
SELECT name, salary FROM high_earners
UNION
SELECT name, salary FROM it_employees;

-- PRZECIĘCIE (∩): high_earners ∩ it_employees  
SELECT name, salary FROM high_earners
INTERSECT  
SELECT name, salary FROM it_employees;

-- RÓŻNICA (-): high_earners - it_employees
SELECT name, salary FROM high_earners
EXCEPT
SELECT name, salary FROM it_employees;

-- 5. ILOCZYN KARTEZJAŃSKI (×)

-- Employee × Project (wszystkie kombinacje)
SELECT e.name as employee, p.name as project
FROM Employee e CROSS JOIN Project p;

-- Praktyczne użycie - matryca przypisań
SELECT 
    e.name as employee,
    p.name as project,
    CASE WHEN a.emp_id IS NOT NULL THEN 'Assigned' ELSE 'Not Assigned' END as status
FROM Employee e 
CROSS JOIN Project p
LEFT JOIN Assignment a ON e.id = a.emp_id AND p.id = a.proj_id
ORDER BY e.name, p.name;

-- 6. DZIELENIE (÷) - symulacja w SQL

-- Znajdź pracowników przypisanych do WSZYSTKICH projektów
-- Employee ÷ Project (w kontekście Assignment)

-- Metoda 1: Using double negation
SELECT e.name
FROM Employee e
WHERE NOT EXISTS (
    SELECT p.id
    FROM Project p
    WHERE NOT EXISTS (
        SELECT a.emp_id  
        FROM Assignment a
        WHERE a.emp_id = e.id AND a.proj_id = p.id
    )
);

-- Metoda 2: Using COUNT  
SELECT e.name
FROM Employee e
JOIN Assignment a ON e.id = a.emp_id
GROUP BY e.id, e.name
HAVING COUNT(DISTINCT a.proj_id) = (SELECT COUNT(*) FROM Project);

-- 7. ZŁOŻONE WYRAŻENIA ALGEBRY RELACJI

-- π_name,salary(σ_dept='IT' AND salary>6000(Employee ⋈ Department))
SELECT e.name, e.salary
FROM Employee e JOIN Department d ON e.dept_id = d.id
WHERE d.name = 'IT' AND e.salary > 6000;

-- π_dept_name,avg_salary(γ_dept_id;AVG(salary)(Employee ⋈ Department))
-- (agregacja w algebrze relacji)
SELECT d.name as dept_name, AVG(e.salary) as avg_salary
FROM Employee e JOIN Department d ON e.dept_id = d.id
GROUP BY d.id, d.name;

-- Kompleksowe wyrażenie:
-- π_emp_name,proj_name(
--   σ_hours>30(
--     Employee ⋈ Assignment ⋈ Project
--   )
-- )
SELECT e.name as emp_name, p.name as proj_name
FROM Employee e
JOIN Assignment a ON e.id = a.emp_id  
JOIN Project p ON a.proj_id = p.id
WHERE a.hours > 30;

-- 8. OUTER JOINS w kontekście algebry relacji

-- Left outer join: Employee ⟕ Department
SELECT e.name, e.salary, d.name as dept_name
FROM Employee e LEFT JOIN Department d ON e.dept_id = d.id;

-- Right outer join: Employee ⟖ Department  
SELECT e.name, e.salary, d.name as dept_name
FROM Employee e RIGHT JOIN Department d ON e.dept_id = d.id;

-- Full outer join: Employee ⟗ Department
SELECT e.name, e.salary, d.name as dept_name
FROM Employee e FULL OUTER JOIN Department d ON e.dept_id = d.id;

-- 9. SEMIJOIN i ANTIJOIN

-- Semijoin: Employee ⋉ Assignment
-- (pracownicy którzy mają przypisania)
SELECT DISTINCT e.*
FROM Employee e
WHERE EXISTS (SELECT 1 FROM Assignment a WHERE a.emp_id = e.id);

-- Lub:
SELECT e.*
FROM Employee e
WHERE e.id IN (SELECT emp_id FROM Assignment);

-- Antijoin: Employee ▷ Assignment  
-- (pracownicy którzy NIE mają przypisań)
SELECT e.*
FROM Employee e
WHERE NOT EXISTS (SELECT 1 FROM Assignment a WHERE a.emp_id = e.id);

-- 10. ROZSZERZONA ALGEBRA RELACJI

-- Agregacja (nie w podstawowej algebrze)
-- γ_dept_id;COUNT(*),AVG(salary)(Employee)
SELECT dept_id, COUNT(*) as emp_count, AVG(salary) as avg_salary
FROM Employee
GROUP BY dept_id;

-- Sortowanie (nie w podstawowej algebrze)  
-- τ_salary DESC(Employee)
SELECT * FROM Employee ORDER BY salary DESC;

-- Duplikacja/usuwanie duplikatów
-- δ(π_dept_id(Employee)) - usunięcie duplikatów
SELECT DISTINCT dept_id FROM Employee;

-- 11. TRANSFORMACJE ZAPYTAŃ

-- Optymalizacja przez zmianę kolejności operacji
-- NIEOPTYMALNE:
-- σ_salary>6000(Employee ⋈ Department)
SELECT e.name, e.salary, d.name
FROM Employee e JOIN Department d ON e.dept_id = d.id
WHERE e.salary > 6000;

-- OPTYMALNE:  
-- σ_salary>6000(Employee) ⋈ Department
SELECT e.name, e.salary, d.name
FROM (SELECT * FROM Employee WHERE salary > 6000) e
JOIN Department d ON e.dept_id = d.id;

-- 12. EKVIVALENTNE WYRAŻENIA

-- Te wyrażenia są równoważne:
-- σ_A AND B(R) ≡ σ_A(σ_B(R))
SELECT * FROM Employee WHERE salary > 6000 AND dept_id = 1;
-- równoważne z:
SELECT * FROM (SELECT * FROM Employee WHERE salary > 6000) t WHERE dept_id = 1;

-- π_A(π_A,B(R)) ≡ π_A(R)
SELECT name FROM (SELECT name, salary FROM Employee);
-- równoważne z:
SELECT name FROM Employee;

-- (R ⋈ S) ⋈ T ≡ R ⋈ (S ⋈ T) - łączność
-- Można zmieniać kolejność JOIN'ów
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Algebra relacji operuje na relacjach (zbiorach), nie na multizbiorach
2. **UWAGA**: Operacje zbiorowe wymagają tego samego schematu relacji
3. **BŁĄD**: Mylenie złączenia θ (theta) z natural join
4. **WAŻNE**: Dzielenie (÷) nie ma bezpośredniego odpowiednika w SQL
5. **PUŁAPKA**: W praktyce SQL dodaje elementy nieobecne w czystej algebrze (ORDER BY, GROUP BY)

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Relational algebra** - algebra relacji
- **Selection/Projection** - selekcja/projekcja
- **Join operations** - operacje złączenia  
- **Set operations** - operacje zbiorowe
- **Cartesian product** - iloczyn kartezjański
- **Division operation** - operacja dzielenia
- **Query optimization** - optymalizacja zapytań
- **Algebraic equivalence** - równoważność algebraiczna

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **21-sql-joiny** - implementacja złączeń w SQL
- **30-sql-dml-zaawansowany** - zaawansowane zapytania SQL
- **26-model-relacyjny** - podstawy teoretyczne
- **42-optymalizacja-wydajnosci** - transformacje zapytań
- **32-funkcje-agregujace** - rozszerzenia algebry