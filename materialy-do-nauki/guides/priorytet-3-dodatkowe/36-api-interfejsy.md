# API i interfejsy bazodanowe

## Definicja API bazodanowego

**API bazodanowe (Database API)** to **zestaw protokołów, narzędzi i definicji** umożliwiających aplikacjom **komunikację z bazą danych** w sposób standardowy i bezpieczny.

### Kluczowe cechy:
- **Abstrakcja** - ukrywa szczegóły implementacyjne bazy danych
- **Standardyzacja** - jednolity sposób dostępu do różnych SZBD
- **Bezpieczeństwo** - kontrola dostępu i autoryzacji
- **Wydajność** - optymalizacja połączeń i zapytań
- **Skalowość** - obsługa wielu równoczesnych połączeń

### Typy interfejsów:
- **Natywne API** - specyficzne dla konkretnego SZBD
- **Standardowe API** - ODBC, JDBC, PDO
- **ORM** - Object-Relational Mapping
- **REST API** - HTTP-based interfaces
- **GraphQL** - Query language for APIs

## Natywne API baz danych

### 1. **PostgreSQL API**

#### libpq - C library:
```c
#include <libpq-fe.h>

// Połączenie z bazą danych
PGconn *conn = PQconnectdb("host=localhost dbname=testdb user=postgres");

if (PQstatus(conn) != CONNECTION_OK) {
    fprintf(stderr, "Connection failed: %s", PQerrorMessage(conn));
    PQfinish(conn);
    exit(1);
}

// Wykonanie zapytania
PGresult *res = PQexec(conn, "SELECT * FROM employees WHERE salary > 5000");

if (PQresultStatus(res) != PGRES_TUPLES_OK) {
    fprintf(stderr, "Query failed: %s", PQerrorMessage(conn));
    PQclear(res);
    PQfinish(conn);
    exit(1);
}

// Iteracja przez wyniki
int rows = PQntuples(res);
int cols = PQnfields(res);

for (int i = 0; i < rows; i++) {
    for (int j = 0; j < cols; j++) {
        printf("%s\t", PQgetvalue(res, i, j));
    }
    printf("\n");
}

// Cleanup
PQclear(res);
PQfinish(conn);
```

#### psycopg2 - Python PostgreSQL adapter:
```python
import psycopg2
from psycopg2.extras import RealDictCursor

# Połączenie z bazą danych
conn = psycopg2.connect(
    host="localhost",
    database="testdb",
    user="postgres",
    password="password"
)

# Kursor do wykonywania zapytań
cursor = conn.cursor(cursor_factory=RealDictCursor)

try:
    # Zapytanie z parametrami (bezpieczne)
    cursor.execute(
        "SELECT * FROM employees WHERE department = %s AND salary > %s",
        ("IT", 5000)
    )
    
    # Pobranie wyników
    employees = cursor.fetchall()
    
    for emp in employees:
        print(f"{emp['first_name']} {emp['last_name']} - ${emp['salary']}")
    
    # Transakcja z wieloma operacjami
    cursor.execute("BEGIN")
    
    cursor.execute(
        "INSERT INTO employees (first_name, last_name, salary, department) "
        "VALUES (%s, %s, %s, %s)",
        ("Jan", "Kowalski", 6000, "IT")
    )
    
    cursor.execute(
        "UPDATE department_stats SET employee_count = employee_count + 1 "
        "WHERE department_name = %s",
        ("IT",)
    )
    
    cursor.execute("COMMIT")
    
except psycopg2.Error as e:
    print(f"Database error: {e}")
    cursor.execute("ROLLBACK")
    
finally:
    cursor.close()
    conn.close()
```

### 2. **MySQL API**

#### MySQL Connector/Python:
```python
import mysql.connector
from mysql.connector import Error

try:
    # Połączenie
    connection = mysql.connector.connect(
        host='localhost',
        database='testdb',
        user='root',
        password='password',
        autocommit=False  # Manual transaction control
    )
    
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        
        # Zapytanie z parametrami
        query = "SELECT * FROM employees WHERE department = %s"
        cursor.execute(query, ("IT",))
        
        records = cursor.fetchall()
        
        for row in records:
            print(f"ID: {row['id']}, Name: {row['name']}")
        
        # Batch insert
        insert_query = "INSERT INTO employees (name, salary, department) VALUES (%s, %s, %s)"
        data = [
            ("Anna Nowak", 5500, "HR"),
            ("Piotr Wiśniewski", 6200, "IT"),
            ("Maria Kowalczyk", 4800, "Finance")
        ]
        
        cursor.executemany(insert_query, data)
        connection.commit()
        print(f"{cursor.rowcount} records inserted")

except Error as e:
    print(f"Error: {e}")
    if connection.is_connected():
        connection.rollback()

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
```

### 3. **MongoDB API**

#### PyMongo - Python MongoDB driver:
```python
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from bson import ObjectId
import datetime

# Połączenie z MongoDB
try:
    client = MongoClient('mongodb://localhost:27017/')
    
    # Sprawdzenie połączenia
    client.admin.command('ping')
    print("Connected to MongoDB")
    
    # Wybór bazy danych i kolekcji
    db = client['company_db']
    employees = db['employees']
    
    # Wstawienie dokumentu
    employee = {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "email": "jan.kowalski@company.com",
        "department": "IT",
        "salary": 6000,
        "start_date": datetime.datetime.now(),
        "skills": ["Python", "SQL", "Docker"],
        "address": {
            "street": "ul. Warszawska 123",
            "city": "Kraków",
            "postal_code": "30-001"
        }
    }
    
    result = employees.insert_one(employee)
    print(f"Inserted employee with ID: {result.inserted_id}")
    
    # Batch insert
    batch_employees = [
        {
            "first_name": "Anna",
            "last_name": "Nowak",
            "department": "HR",
            "salary": 5500,
            "skills": ["Recruitment", "Training"]
        },
        {
            "first_name": "Piotr",
            "last_name": "Wiśniewski",
            "department": "Finance",
            "salary": 5800,
            "skills": ["Accounting", "Analysis"]
        }
    ]
    
    result = employees.insert_many(batch_employees)
    print(f"Inserted {len(result.inserted_ids)} employees")
    
    # Zapytania
    # Proste wyszukiwanie
    it_employees = employees.find({"department": "IT"})
    for emp in it_employees:
        print(f"{emp['first_name']} {emp['last_name']}")
    
    # Złożone zapytanie z operatorami
    high_salary_employees = employees.find({
        "salary": {"$gte": 5500},
        "department": {"$in": ["IT", "Finance"]}
    }).sort("salary", -1)
    
    # Agregacja
    pipeline = [
        {"$group": {
            "_id": "$department",
            "avg_salary": {"$avg": "$salary"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"avg_salary": -1}}
    ]
    
    dept_stats = employees.aggregate(pipeline)
    for stat in dept_stats:
        print(f"Department: {stat['_id']}, Avg Salary: {stat['avg_salary']:.2f}")
    
    # Aktualizacja
    employees.update_one(
        {"_id": result.inserted_id},
        {"$set": {"salary": 6500, "last_updated": datetime.datetime.now()}}
    )
    
    # Usuwanie
    employees.delete_many({"salary": {"$lt": 3000}})

except ConnectionFailure:
    print("Failed to connect to MongoDB")
except DuplicateKeyError:
    print("Duplicate key error")
finally:
    client.close()
```

## Standardowe API

### 1. **JDBC (Java Database Connectivity)**

#### Podstawowy przykład:
```java
import java.sql.*;
import java.util.Properties;

public class DatabaseExample {
    private static final String URL = "jdbc:postgresql://localhost:5432/testdb";
    private static final String USERNAME = "postgres";
    private static final String PASSWORD = "password";
    
    public static void main(String[] args) {
        try {
            // Połączenie z bazą danych
            Connection connection = DriverManager.getConnection(URL, USERNAME, PASSWORD);
            
            // Wyłączenie autocommit dla kontroli transakcji
            connection.setAutoCommit(false);
            
            // PreparedStatement dla bezpiecznych zapytań
            String selectSQL = "SELECT * FROM employees WHERE department = ? AND salary > ?";
            PreparedStatement selectStmt = connection.prepareStatement(selectSQL);
            selectStmt.setString(1, "IT");
            selectStmt.setDouble(2, 5000.0);
            
            ResultSet resultSet = selectStmt.executeQuery();
            
            System.out.println("Employees in IT with salary > 5000:");
            while (resultSet.next()) {
                int id = resultSet.getInt("id");
                String firstName = resultSet.getString("first_name");
                String lastName = resultSet.getString("last_name");
                double salary = resultSet.getDouble("salary");
                
                System.out.printf("%d: %s %s - $%.2f%n", id, firstName, lastName, salary);
            }
            
            // Batch operations
            String insertSQL = "INSERT INTO employees (first_name, last_name, salary, department) VALUES (?, ?, ?, ?)";
            PreparedStatement insertStmt = connection.prepareStatement(insertSQL);
            
            // Dodaj wielu pracowników w jednej operacji
            String[][] newEmployees = {
                {"Jan", "Kowalski", "6000", "IT"},
                {"Anna", "Nowak", "5500", "HR"},
                {"Piotr", "Wiśniewski", "5800", "Finance"}
            };
            
            for (String[] emp : newEmployees) {
                insertStmt.setString(1, emp[0]);
                insertStmt.setString(2, emp[1]);
                insertStmt.setDouble(3, Double.parseDouble(emp[2]));
                insertStmt.setString(4, emp[3]);
                insertStmt.addBatch();
            }
            
            int[] updateCounts = insertStmt.executeBatch();
            connection.commit();
            
            System.out.printf("Inserted %d employees%n", updateCounts.length);
            
            // Cleanup
            resultSet.close();
            selectStmt.close();
            insertStmt.close();
            connection.close();
            
        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
```

#### Connection Pooling z HikariCP:
```java
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;

public class ConnectionPoolExample {
    private static HikariDataSource dataSource;
    
    static {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:postgresql://localhost:5432/testdb");
        config.setUsername("postgres");
        config.setPassword("password");
        
        // Pool configuration
        config.setMaximumPoolSize(20);
        config.setMinimumIdle(5);
        config.setConnectionTimeout(30000);
        config.setIdleTimeout(600000);
        config.setMaxLifetime(1800000);
        
        dataSource = new HikariDataSource(config);
    }
    
    public static Connection getConnection() throws SQLException {
        return dataSource.getConnection();
    }
    
    public static void closeDataSource() {
        if (dataSource != null) {
            dataSource.close();
        }
    }
}
```

### 2. **ODBC (Open Database Connectivity)**

#### Python z pyodbc:
```python
import pyodbc

# Connection string for SQL Server
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=testdb;"
    "UID=sa;"
    "PWD=password"
)

try:
    # Połączenie
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    # Zapytanie z parametrami
    cursor.execute(
        "SELECT * FROM employees WHERE department = ? AND salary > ?",
        ("IT", 5000)
    )
    
    # Pobieranie wyników
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row.first_name} {row.last_name} - ${row.salary}")
    
    # Stored procedure call
    cursor.execute("{CALL GetDepartmentStats(?)}", ("IT",))
    stats = cursor.fetchone()
    print(f"IT Department - Count: {stats[0]}, Avg Salary: {stats[1]}")
    
    # Transaction
    cursor.execute("BEGIN TRANSACTION")
    try:
        cursor.execute(
            "INSERT INTO employees (first_name, last_name, salary, department) "
            "VALUES (?, ?, ?, ?)",
            ("Jan", "Kowalski", 6000, "IT")
        )
        cursor.execute("COMMIT")
    except Exception as e:
        cursor.execute("ROLLBACK")
        raise e

except pyodbc.Error as e:
    print(f"ODBC Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
```

### 3. **PDO (PHP Data Objects)**

```php
<?php
$host = 'localhost';
$dbname = 'testdb';
$username = 'postgres';
$password = 'password';

try {
    // Połączenie z PostgreSQL
    $dsn = "pgsql:host=$host;dbname=$dbname";
    $pdo = new PDO($dsn, $username, $password, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false
    ]);
    
    // Zapytanie z parametrami
    $stmt = $pdo->prepare("SELECT * FROM employees WHERE department = :dept AND salary > :min_salary");
    $stmt->execute([
        ':dept' => 'IT',
        ':min_salary' => 5000
    ]);
    
    $employees = $stmt->fetchAll();
    
    foreach ($employees as $emp) {
        echo "{$emp['first_name']} {$emp['last_name']} - $" . number_format($emp['salary']) . "\n";
    }
    
    // Transakcja
    $pdo->beginTransaction();
    
    try {
        // Wstawienie nowego pracownika
        $insertStmt = $pdo->prepare(
            "INSERT INTO employees (first_name, last_name, salary, department) VALUES (?, ?, ?, ?)"
        );
        $insertStmt->execute(['Jan', 'Kowalski', 6000, 'IT']);
        
        // Aktualizacja statystyk działu
        $updateStmt = $pdo->prepare(
            "UPDATE department_stats SET employee_count = employee_count + 1 WHERE department_name = ?"
        );
        $updateStmt->execute(['IT']);
        
        $pdo->commit();
        echo "Transaction completed successfully\n";
        
    } catch (Exception $e) {
        $pdo->rollback();
        throw $e;
    }
    
    // Batch insert
    $batchStmt = $pdo->prepare(
        "INSERT INTO employees (first_name, last_name, salary, department) VALUES (?, ?, ?, ?)"
    );
    
    $newEmployees = [
        ['Anna', 'Nowak', 5500, 'HR'],
        ['Piotr', 'Wiśniewski', 5800, 'Finance'],
        ['Maria', 'Kowalczyk', 4800, 'Marketing']
    ];
    
    foreach ($newEmployees as $emp) {
        $batchStmt->execute($emp);
    }
    
} catch (PDOException $e) {
    echo "Database error: " . $e->getMessage() . "\n";
}
?>
```

## ORM (Object-Relational Mapping)

### 1. **SQLAlchemy (Python)**

#### Model definition:
```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Department(Base):
    __tablename__ = 'departments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    budget = Column(Float)
    
    # Relationship
    employees = relationship("Employee", back_populates="department")

class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True)
    salary = Column(Float)
    hire_date = Column(DateTime, default=datetime.utcnow)
    department_id = Column(Integer, ForeignKey('departments.id'))
    
    # Relationship
    department = relationship("Department", back_populates="employees")
    
    def __repr__(self):
        return f"<Employee('{self.first_name} {self.last_name}')>"

# Database connection
engine = create_engine('postgresql://postgres:password@localhost/testdb')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
```

#### CRUD operations:
```python
# Create
it_dept = Department(name='IT', budget=100000)
session.add(it_dept)
session.commit()

# Create employee
new_employee = Employee(
    first_name='Jan',
    last_name='Kowalski',
    email='jan.kowalski@company.com',
    salary=6000,
    department=it_dept
)
session.add(new_employee)
session.commit()

# Read
# Query all employees
all_employees = session.query(Employee).all()

# Query with filters
it_employees = session.query(Employee).join(Department).filter(Department.name == 'IT').all()

# Query with conditions
high_earners = session.query(Employee).filter(Employee.salary > 5000).all()

# Complex query with aggregation
from sqlalchemy import func
dept_stats = session.query(
    Department.name,
    func.count(Employee.id).label('employee_count'),
    func.avg(Employee.salary).label('avg_salary')
).join(Employee).group_by(Department.name).all()

for stat in dept_stats:
    print(f"{stat.name}: {stat.employee_count} employees, avg salary: ${stat.avg_salary:.2f}")

# Update
employee = session.query(Employee).filter(Employee.email == 'jan.kowalski@company.com').first()
if employee:
    employee.salary = 6500
    session.commit()

# Bulk update
session.query(Employee).filter(Employee.department_id == it_dept.id).update({
    Employee.salary: Employee.salary * 1.05  # 5% raise
})
session.commit()

# Delete
# Delete specific employee
session.query(Employee).filter(Employee.id == 1).delete()
session.commit()

# Bulk delete
session.query(Employee).filter(Employee.salary < 3000).delete()
session.commit()

session.close()
```

### 2. **Hibernate (Java)**

#### Entity definition:
```java
import javax.persistence.*;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "departments")
public class Department {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, length = 100)
    private String name;
    
    private Double budget;
    
    @OneToMany(mappedBy = "department", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Employee> employees;
    
    // Constructors, getters, setters
    public Department() {}
    
    public Department(String name, Double budget) {
        this.name = name;
        this.budget = budget;
    }
    
    // getters and setters...
}

@Entity
@Table(name = "employees")
public class Employee {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "first_name", nullable = false, length = 50)
    private String firstName;
    
    @Column(name = "last_name", nullable = false, length = 50)
    private String lastName;
    
    @Column(unique = true, length = 100)
    private String email;
    
    private Double salary;
    
    @Column(name = "hire_date")
    private LocalDateTime hireDate;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "department_id")
    private Department department;
    
    // Constructors, getters, setters
    public Employee() {}
    
    public Employee(String firstName, String lastName, String email, Double salary) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
        this.salary = salary;
        this.hireDate = LocalDateTime.now();
    }
    
    // getters and setters...
}
```

#### DAO pattern with Hibernate:
```java
import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.Transaction;
import org.hibernate.query.Query;
import java.util.List;

public class EmployeeDAO {
    private SessionFactory sessionFactory;
    
    public EmployeeDAO(SessionFactory sessionFactory) {
        this.sessionFactory = sessionFactory;
    }
    
    public void save(Employee employee) {
        Transaction transaction = null;
        try (Session session = sessionFactory.openSession()) {
            transaction = session.beginTransaction();
            session.save(employee);
            transaction.commit();
        } catch (Exception e) {
            if (transaction != null) {
                transaction.rollback();
            }
            throw e;
        }
    }
    
    public Employee findById(Long id) {
        try (Session session = sessionFactory.openSession()) {
            return session.get(Employee.class, id);
        }
    }
    
    public List<Employee> findByDepartment(String departmentName) {
        try (Session session = sessionFactory.openSession()) {
            Query<Employee> query = session.createQuery(
                "FROM Employee e JOIN e.department d WHERE d.name = :deptName", 
                Employee.class
            );
            query.setParameter("deptName", departmentName);
            return query.list();
        }
    }
    
    public List<Employee> findHighEarners(Double minSalary) {
        try (Session session = sessionFactory.openSession()) {
            Query<Employee> query = session.createQuery(
                "FROM Employee WHERE salary > :minSalary ORDER BY salary DESC", 
                Employee.class
            );
            query.setParameter("minSalary", minSalary);
            return query.list();
        }
    }
    
    public void update(Employee employee) {
        Transaction transaction = null;
        try (Session session = sessionFactory.openSession()) {
            transaction = session.beginTransaction();
            session.update(employee);
            transaction.commit();
        } catch (Exception e) {
            if (transaction != null) {
                transaction.rollback();
            }
            throw e;
        }
    }
    
    public void delete(Long id) {
        Transaction transaction = null;
        try (Session session = sessionFactory.openSession()) {
            transaction = session.beginTransaction();
            Employee employee = session.get(Employee.class, id);
            if (employee != null) {
                session.delete(employee);
            }
            transaction.commit();
        } catch (Exception e) {
            if (transaction != null) {
                transaction.rollback();
            }
            throw e;
        }
    }
}
```

## API Security

### 1. **SQL Injection Prevention**

#### Prepared Statements:
```python
# ❌ VULNERABLE - SQL injection risk
def get_user_by_id_bad(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

# ✅ SAFE - Parameterized query
def get_user_by_id_safe(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    return execute_query(query, (user_id,))

# ❌ VULNERABLE - String concatenation
def search_users_bad(search_term):
    query = f"SELECT * FROM users WHERE name LIKE '%{search_term}%'"
    return execute_query(query)

# ✅ SAFE - Parameterized query
def search_users_safe(search_term):
    query = "SELECT * FROM users WHERE name LIKE %s"
    return execute_query(query, (f"%{search_term}%",))
```

### 2. **Authentication and Authorization**

```python
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self, secret_key):
        self.secret_key = secret_key
    
    def hash_password(self, password):
        # Generate salt
        salt = secrets.token_hex(16)
        
        # Hash password with salt
        pwd_hash = hashlib.pbkdf2_hmac('sha256', 
                                       password.encode('utf-8'), 
                                       salt.encode('utf-8'), 
                                       100000)
        
        return salt + pwd_hash.hex()
    
    def verify_password(self, password, stored_hash):
        # Extract salt
        salt = stored_hash[:32]
        stored_pwd_hash = stored_hash[32:]
        
        # Hash provided password with same salt
        pwd_hash = hashlib.pbkdf2_hmac('sha256',
                                       password.encode('utf-8'),
                                       salt.encode('utf-8'),
                                       100000)
        
        return pwd_hash.hex() == stored_pwd_hash
    
    def create_token(self, user_id, roles=None):
        payload = {
            'user_id': user_id,
            'roles': roles or [],
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")

# Decorator for API authorization
def require_auth(required_role=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            token = get_token_from_request()  # Extract from headers
            
            try:
                payload = auth_manager.verify_token(token)
                
                if required_role and required_role not in payload.get('roles', []):
                    raise Exception("Insufficient permissions")
                
                # Add user info to request context
                kwargs['current_user'] = payload
                return func(*args, **kwargs)
                
            except Exception as e:
                return {"error": "Authentication failed", "message": str(e)}, 401
        
        return wrapper
    return decorator

# Usage
@require_auth(required_role='admin')
def delete_employee(employee_id, current_user=None):
    # Only admins can delete employees
    return employee_service.delete(employee_id)
```

### 3. **Connection Security**

```python
import ssl
import psycopg2

# SSL connection configuration
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_REQUIRED

# Secure connection string
conn = psycopg2.connect(
    host="db.company.com",
    port=5432,
    database="production_db",
    user="app_user",
    password="secure_password",
    sslmode="require",
    sslcert="/path/to/client.crt",
    sslkey="/path/to/client.key",
    sslrootcert="/path/to/ca.crt"
)
```

## Performance Optimization

### 1. **Connection Pooling**

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Connection pool configuration
engine = create_engine(
    'postgresql://user:password@localhost/dbname',
    poolclass=QueuePool,
    pool_size=10,         # Number of connections to maintain
    max_overflow=20,      # Additional connections beyond pool_size
    pool_pre_ping=True,   # Verify connections before use
    pool_recycle=3600,    # Recycle connections after 1 hour
    echo=False            # Set to True for SQL logging
)

class DatabaseManager:
    def __init__(self, engine):
        self.engine = engine
    
    def execute_query(self, query, params=None):
        with self.engine.connect() as conn:
            result = conn.execute(query, params or {})
            return result.fetchall()
    
    def execute_transaction(self, operations):
        with self.engine.begin() as conn:  # Auto-commit/rollback
            results = []
            for operation in operations:
                result = conn.execute(operation['query'], operation.get('params', {}))
                results.append(result)
            return results
```

### 2. **Query Optimization**

```python
class OptimizedQueries:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_employee_with_department(self, employee_id):
        # Single query with JOIN instead of multiple queries
        query = """
        SELECT e.*, d.name as department_name, d.budget
        FROM employees e
        JOIN departments d ON e.department_id = d.id
        WHERE e.id = %(emp_id)s
        """
        return self.db.execute_query(query, {'emp_id': employee_id})
    
    def get_department_statistics(self):
        # Efficient aggregation query
        query = """
        SELECT 
            d.name as department_name,
            COUNT(e.id) as employee_count,
            AVG(e.salary) as avg_salary,
            MIN(e.salary) as min_salary,
            MAX(e.salary) as max_salary
        FROM departments d
        LEFT JOIN employees e ON d.id = e.department_id
        GROUP BY d.id, d.name
        ORDER BY avg_salary DESC
        """
        return self.db.execute_query(query)
    
    def bulk_insert_employees(self, employees_data):
        # Efficient bulk insert
        query = """
        INSERT INTO employees (first_name, last_name, email, salary, department_id)
        VALUES %(values)s
        """
        # Use execute_values for bulk operations in psycopg2
        with self.db.engine.raw_connection() as conn:
            with conn.cursor() as cursor:
                from psycopg2.extras import execute_values
                execute_values(
                    cursor, query, employees_data,
                    template=None, page_size=100
                )
                conn.commit()
```

### 3. **Caching Strategies**

```python
import redis
import json
from functools import wraps

class CacheManager:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    
    def cache_result(self, key, data, ttl=3600):
        """Cache data with TTL (time to live)"""
        self.redis_client.setex(key, ttl, json.dumps(data, default=str))
    
    def get_cached_result(self, key):
        """Retrieve cached data"""
        cached = self.redis_client.get(key)
        return json.loads(cached) if cached else None
    
    def invalidate_cache(self, pattern):
        """Invalidate cache by pattern"""
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)

def cached_query(cache_key_template, ttl=3600):
    """Decorator for caching query results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_key_template.format(*args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_manager.get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.cache_result(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

# Usage
@cached_query("dept_stats", ttl=1800)  # Cache for 30 minutes
def get_department_statistics():
    return db.execute_query("SELECT * FROM department_stats_view")

@cached_query("employee_{}", ttl=600)  # Cache for 10 minutes
def get_employee_details(employee_id):
    return db.execute_query(
        "SELECT * FROM employees WHERE id = %s", 
        (employee_id,)
    )
```

## Monitoring and Logging

### 1. **Query Performance Monitoring**

```python
import time
import logging
from contextlib import contextmanager

class QueryMonitor:
    def __init__(self):
        self.logger = logging.getLogger('db_monitor')
        self.slow_query_threshold = 1.0  # seconds
    
    @contextmanager
    def monitor_query(self, query, params=None):
        start_time = time.time()
        try:
            yield
        finally:
            execution_time = time.time() - start_time
            
            if execution_time > self.slow_query_threshold:
                self.logger.warning(
                    f"Slow query detected: {execution_time:.3f}s - {query[:100]}..."
                )
            
            self.logger.info(
                f"Query executed in {execution_time:.3f}s",
                extra={
                    'query': query,
                    'params': params,
                    'execution_time': execution_time
                }
            )

# Usage
monitor = QueryMonitor()

def execute_monitored_query(query, params=None):
    with monitor.monitor_query(query, params):
        return db.execute_query(query, params)
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**

#### 1. **Security First**
```python
# Zawsze używaj parametryzowanych zapytań
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# Waliduj input
def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Używaj HTTPS dla wszystkich połączeń
# Implementuj proper authentication/authorization
```

#### 2. **Error Handling**
```python
try:
    result = db.execute_query(query, params)
    return result
except DatabaseConnectionError:
    # Log error, implement retry logic
    logger.error("Database connection failed")
    raise
except QueryError as e:
    # Log query details for debugging
    logger.error(f"Query failed: {query}", extra={'params': params, 'error': str(e)})
    raise
```

#### 3. **Resource Management**
```python
# Always use context managers or try/finally
try:
    conn = get_connection()
    # Use connection
finally:
    conn.close()

# Or better - use context managers
with get_connection() as conn:
    # Use connection
    pass  # Automatically closed
```

### ❌ **Złe praktyki:**

```python
# ❌ SQL injection vulnerability
query = f"SELECT * FROM users WHERE name = '{user_input}'"

# ❌ Nie zamykanie połączeń
conn = get_connection()
result = conn.execute(query)
# Connection nie została zamknięta!

# ❌ Ignorowanie błędów
try:
    db.execute(query)
except:
    pass  # Nigdy nie ignoruj błędów!

# ❌ Storing passwords in plain text
user.password = request.password  # Should be hashed!
```

## Pułapki egzaminacyjne

### 1. **Connection Management**
```
Connection pools zapobiegają wyczerpaniu połączeń
Zawsze zamykaj connections/cursors w bloku finally
Używaj context managers gdy dostępne
```

### 2. **SQL Injection**
```
Parametryzowane zapytania są JEDYNĄ bezpieczną metodą
String concatenation = vulnerability
Prepared statements = bezpieczeństwo
```

### 3. **Performance**
```
N+1 Query Problem: unikaj zapytań w pętlach
Używaj JOIN zamiast multiple queries
Connection pooling dla wydajności
```

### 4. **Transactions**
```
ACID properties - Atomicity, Consistency, Isolation, Durability
Begin/Commit/Rollback pattern
Autocommit vs manual transaction control
```