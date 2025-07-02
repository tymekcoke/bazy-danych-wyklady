# Bezpieczeństwo baz danych

## Definicja bezpieczeństwa baz danych

**Bezpieczeństwo baz danych** to zestaw **środków, procedur i technologii** mających na celu **ochronę danych** przed nieautoryzowanym dostępem, modyfikacją, zniszczeniem oraz zapewnienie integralności, poufności i dostępności informacji.

### Główne cele bezpieczeństwa:
- **Poufność (Confidentiality)** - dane dostępne tylko dla uprawnionych użytkowników
- **Integralność (Integrity)** - ochrona przed nieautoryzowaną modyfikacją
- **Dostępność (Availability)** - zapewnienie dostępu do danych gdy potrzeba
- **Nieodpieralność (Non-repudiation)** - niemożność zaprzeczenia wykonanym operacjom
- **Uwierzytelnianie (Authentication)** - weryfikacja tożsamości użytkowników
- **Autoryzacja (Authorization)** - kontrola dostępu do zasobów

### Rodzaje zagrożeń:
- **SQL Injection** - wstrzykiwanie złośliwego kodu SQL
- **Nieautoryzowany dostęp** - łamanie mechanizmów uwierzytelniania
- **Privilege escalation** - podnoszenie uprawnień
- **Data breach** - wycieki danych
- **DDoS attacks** - ataki na dostępność
- **Insider threats** - zagrożenia wewnętrzne

## Uwierzytelnianie i autoryzacja

### 1. **Uwierzytelnianie w PostgreSQL**

#### Metody uwierzytelniania:
```sql
-- Konfiguracja pg_hba.conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Trust - brak hasła (tylko lokalne)
local   all             postgres                                trust

# MD5 - hasło szyfrowane MD5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5

# SCRAM-SHA-256 - nowoczesne szyfrowanie (PostgreSQL 10+)
host    all             all             0.0.0.0/0               scram-sha-256

# LDAP - integracja z Active Directory
host    all             all             192.168.1.0/24          ldap ldapserver=ldap.company.com ldapprefix="cn=" ldapsuffix=",ou=users,dc=company,dc=com"

# Certificate - uwierzytelnianie certyfikatami
hostssl all             all             0.0.0.0/0               cert

# Kerberos - integracja z systemami korporacyjnymi
host    all             all             0.0.0.0/0               gss include_realm=0 krb_realm=COMPANY.COM
```

#### Zarządzanie użytkownikami:
```sql
-- Tworzenie użytkowników
CREATE USER app_user WITH PASSWORD 'secure_password_123!';
CREATE USER readonly_user WITH PASSWORD 'readonly_pass_456!';
CREATE USER admin_user WITH PASSWORD 'admin_pass_789!' SUPERUSER;

-- Tworzenie ról
CREATE ROLE app_role;
CREATE ROLE reporting_role;
CREATE ROLE admin_role;

-- Przypisywanie uprawnień do ról
GRANT CONNECT ON DATABASE company_db TO app_role;
GRANT USAGE ON SCHEMA public TO app_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_role;

-- Uprawnienia tylko do odczytu
GRANT CONNECT ON DATABASE company_db TO reporting_role;
GRANT USAGE ON SCHEMA public TO reporting_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO reporting_role;

-- Przypisywanie ról do użytkowników
GRANT app_role TO app_user;
GRANT reporting_role TO readonly_user;
GRANT admin_role TO admin_user;

-- Ograniczenia połączeń
ALTER USER app_user CONNECTION LIMIT 50;
ALTER USER readonly_user CONNECTION LIMIT 20;

-- Ważność hasła
ALTER USER app_user VALID UNTIL '2024-12-31';

-- Wymuszanie SSL
ALTER USER app_user SET ssl TO 'on';
```

### 2. **Row Level Security (RLS)**

#### Podstawowa konfiguracja RLS:
```sql
-- Włączenie RLS na tabeli
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;

-- Podstawowa polityka - użytkownicy widzą tylko swoje dane
CREATE POLICY employee_own_data ON employees
    FOR ALL
    TO app_users
    USING (employee_id = current_setting('app.current_user_id')::INTEGER);

-- Polityka dla managerów - widzą pracowników swojego działu
CREATE POLICY department_manager_policy ON employees
    FOR SELECT
    TO managers
    USING (
        department_id IN (
            SELECT department_id 
            FROM department_managers 
            WHERE manager_id = current_setting('app.current_user_id')::INTEGER
        )
    );

-- Polityka czasowa - dostęp tylko w godzinach pracy
CREATE POLICY business_hours_policy ON sensitive_data
    FOR ALL
    TO regular_users
    USING (
        EXTRACT(HOUR FROM CURRENT_TIME) BETWEEN 8 AND 18
        AND EXTRACT(DOW FROM CURRENT_DATE) BETWEEN 1 AND 5
    );

-- Polityka oparta na IP
CREATE POLICY ip_restriction_policy ON financial_data
    FOR ALL
    TO finance_users
    USING (inet_client_addr() <<= '192.168.100.0/24'::inet);
```

#### Zaawansowane polityki RLS:
```sql
-- Tabela z danymi osobowymi
CREATE TABLE employee_personal_data (
    employee_id INTEGER PRIMARY KEY,
    ssn VARCHAR(11),
    salary NUMERIC(10,2),
    bank_account VARCHAR(26),
    home_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE employee_personal_data ENABLE ROW LEVEL SECURITY;

-- Polityka dla pracowników HR - pełny dostęp
CREATE POLICY hr_full_access ON employee_personal_data
    FOR ALL
    TO hr_role
    USING (true)
    WITH CHECK (true);

-- Polityka dla pracowników - tylko własne dane
CREATE POLICY employee_own_personal_data ON employee_personal_data
    FOR SELECT
    TO employee_role
    USING (employee_id = current_setting('app.current_user_id')::INTEGER);

-- Polityka dla managerów - ograniczone dane podwładnych
CREATE POLICY manager_limited_access ON employee_personal_data
    FOR SELECT
    TO manager_role
    USING (
        employee_id IN (
            SELECT e.employee_id
            FROM employees e
            JOIN department_managers dm ON e.department_id = dm.department_id
            WHERE dm.manager_id = current_setting('app.current_user_id')::INTEGER
        )
    );

-- Polityka auditowa - logowanie dostępu do wrażliwych danych
CREATE OR REPLACE FUNCTION log_sensitive_access()
RETURNS void AS $$
BEGIN
    INSERT INTO access_log (
        user_name,
        table_name,
        access_time,
        client_ip
    ) VALUES (
        current_user,
        'employee_personal_data',
        CURRENT_TIMESTAMP,
        inet_client_addr()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger do logowania dostępu
CREATE TRIGGER log_personal_data_access
    BEFORE SELECT ON employee_personal_data
    FOR EACH STATEMENT
    EXECUTE FUNCTION log_sensitive_access();
```

### 3. **Szyfrowanie danych**

#### Szyfrowanie na poziomie kolumn:
```sql
-- Instalacja rozszerzenia pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Tabela z zaszyfrowanymi danymi
CREATE TABLE secure_employee_data (
    employee_id INTEGER PRIMARY KEY,
    encrypted_ssn BYTEA,
    encrypted_salary BYTEA,
    encrypted_notes BYTEA,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Funkcje szyfrowania/deszyfrowania
CREATE OR REPLACE FUNCTION encrypt_sensitive_data(plaintext TEXT, key_name TEXT)
RETURNS BYTEA AS $$
DECLARE
    encryption_key TEXT;
BEGIN
    -- Pobierz klucz z bezpiecznego miejsca
    encryption_key := current_setting('app.encryption_keys.' || key_name);
    
    -- Szyfruj dane używając AES
    RETURN pgp_sym_encrypt(plaintext, encryption_key);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION decrypt_sensitive_data(ciphertext BYTEA, key_name TEXT)
RETURNS TEXT AS $$
DECLARE
    encryption_key TEXT;
BEGIN
    encryption_key := current_setting('app.encryption_keys.' || key_name);
    
    -- Deszyfruj dane
    RETURN pgp_sym_decrypt(ciphertext, encryption_key);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Wstawianie zaszyfrowanych danych
INSERT INTO secure_employee_data (employee_id, encrypted_ssn, encrypted_salary)
VALUES (
    1001,
    encrypt_sensitive_data('123-45-6789', 'ssn_key'),
    encrypt_sensitive_data('75000', 'salary_key')
);

-- Odczytywanie zaszyfrowanych danych
SELECT 
    employee_id,
    decrypt_sensitive_data(encrypted_ssn, 'ssn_key') AS ssn,
    decrypt_sensitive_data(encrypted_salary, 'salary_key')::NUMERIC AS salary
FROM secure_employee_data
WHERE employee_id = 1001;

-- Widok z automatycznym deszyfrowaniem
CREATE VIEW employee_secure_view AS
SELECT 
    employee_id,
    CASE 
        WHEN has_table_privilege(current_user, 'secure_employee_data', 'SELECT') 
        THEN decrypt_sensitive_data(encrypted_ssn, 'ssn_key')
        ELSE '***-**-****'
    END AS ssn,
    CASE 
        WHEN current_user IN (SELECT rolname FROM pg_roles WHERE rolname = 'hr_role')
        THEN decrypt_sensitive_data(encrypted_salary, 'salary_key')::NUMERIC
        ELSE NULL
    END AS salary
FROM secure_employee_data;
```

#### Transparent Data Encryption (TDE):
```sql
-- PostgreSQL 15+ z rozszerzeniem TDE
-- Konfiguracja w postgresql.conf
-- cluster_passphrase_command = '/path/to/key/retrieval/script'
-- data_encryption_key_unwrap_command = '/path/to/unwrap/script'

-- Tworzenie zaszyfrowanej tablespace
CREATE TABLESPACE encrypted_ts 
LOCATION '/encrypted/data/path'
WITH (encryption_key_id = 'company_master_key');

-- Tabela w zaszyfrowanej tablespace
CREATE TABLE encrypted_financial_data (
    transaction_id SERIAL PRIMARY KEY,
    account_number VARCHAR(20),
    amount NUMERIC(15,2),
    transaction_date TIMESTAMP,
    description TEXT
) TABLESPACE encrypted_ts;

-- Wszystkie dane w tej tabeli są automatycznie szyfrowane
```

## Ochrona przed SQL Injection

### 1. **Parametryzowane zapytania**

#### Przykłady bezpiecznych implementacji:
```python
# ❌ VULNERABLE - String concatenation
def get_user_unsafe(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

# ✅ SAFE - Parameterized query
def get_user_safe(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    return execute_query(query, (user_id,))

# ❌ VULNERABLE - Dynamic SQL
def search_employees_unsafe(search_term, department):
    query = f"""
    SELECT * FROM employees 
    WHERE name LIKE '%{search_term}%' 
    AND department = '{department}'
    """
    return execute_query(query)

# ✅ SAFE - Parameterized with proper escaping
def search_employees_safe(search_term, department):
    query = """
    SELECT * FROM employees 
    WHERE name LIKE %s 
    AND department = %s
    """
    search_pattern = f"%{search_term}%"
    return execute_query(query, (search_pattern, department))

# Advanced safe implementation with input validation
import re
from typing import List, Optional

def search_employees_advanced(
    search_term: str, 
    department: Optional[str] = None,
    sort_by: str = 'name',
    sort_order: str = 'ASC'
) -> List[dict]:
    
    # Input validation
    if not search_term or len(search_term.strip()) < 2:
        raise ValueError("Search term must be at least 2 characters")
    
    # Whitelist allowed sort columns
    allowed_sort_columns = ['name', 'email', 'hire_date', 'salary']
    if sort_by not in allowed_sort_columns:
        raise ValueError(f"Invalid sort column: {sort_by}")
    
    # Validate sort order
    if sort_order.upper() not in ['ASC', 'DESC']:
        raise ValueError("Sort order must be ASC or DESC")
    
    # Build query safely
    base_query = """
    SELECT employee_id, name, email, department, hire_date
    FROM employees 
    WHERE name ILIKE %s
    """
    
    params = [f"%{search_term.strip()}%"]
    
    if department:
        base_query += " AND department = %s"
        params.append(department)
    
    # Safe to add sort since we validated the column name
    base_query += f" ORDER BY {sort_by} {sort_order.upper()}"
    
    return execute_query(base_query, params)
```

#### Java PreparedStatement:
```java
public class SafeEmployeeDAO {
    
    private final DataSource dataSource;
    
    // ✅ SAFE - PreparedStatement
    public Employee findById(Long id) {
        String sql = "SELECT * FROM employees WHERE id = ?";
        
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            
            stmt.setLong(1, id);
            ResultSet rs = stmt.executeQuery();
            
            if (rs.next()) {
                return mapToEmployee(rs);
            }
            return null;
            
        } catch (SQLException e) {
            throw new DataAccessException("Error finding employee", e);
        }
    }
    
    // ✅ SAFE - Complex query with multiple parameters
    public List<Employee> searchEmployees(
            String nameFilter, 
            String department, 
            Double minSalary, 
            Double maxSalary,
            String sortBy,
            String sortOrder) {
        
        // Input validation
        validateSortParameters(sortBy, sortOrder);
        
        StringBuilder sql = new StringBuilder(
            "SELECT * FROM employees WHERE 1=1 "
        );
        List<Object> params = new ArrayList<>();
        
        if (nameFilter != null && !nameFilter.trim().isEmpty()) {
            sql.append("AND (first_name ILIKE ? OR last_name ILIKE ?) ");
            String pattern = "%" + nameFilter.trim() + "%";
            params.add(pattern);
            params.add(pattern);
        }
        
        if (department != null && !department.trim().isEmpty()) {
            sql.append("AND department = ? ");
            params.add(department.trim());
        }
        
        if (minSalary != null) {
            sql.append("AND salary >= ? ");
            params.add(minSalary);
        }
        
        if (maxSalary != null) {
            sql.append("AND salary <= ? ");
            params.add(maxSalary);
        }
        
        // Safe to append since we validated
        sql.append("ORDER BY ").append(sortBy).append(" ").append(sortOrder);
        
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql.toString())) {
            
            // Set parameters
            for (int i = 0; i < params.size(); i++) {
                stmt.setObject(i + 1, params.get(i));
            }
            
            ResultSet rs = stmt.executeQuery();
            return mapToEmployeeList(rs);
            
        } catch (SQLException e) {
            throw new DataAccessException("Error searching employees", e);
        }
    }
    
    private void validateSortParameters(String sortBy, String sortOrder) {
        Set<String> allowedColumns = Set.of(
            "first_name", "last_name", "email", "salary", "hire_date", "department"
        );
        
        if (!allowedColumns.contains(sortBy)) {
            throw new IllegalArgumentException("Invalid sort column: " + sortBy);
        }
        
        if (!"ASC".equalsIgnoreCase(sortOrder) && !"DESC".equalsIgnoreCase(sortOrder)) {
            throw new IllegalArgumentException("Invalid sort order: " + sortOrder);
        }
    }
    
    // ✅ SAFE - Batch operations
    public void batchInsertEmployees(List<Employee> employees) {
        String sql = """
            INSERT INTO employees (first_name, last_name, email, salary, department, hire_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """;
        
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            
            conn.setAutoCommit(false);
            
            for (Employee emp : employees) {
                stmt.setString(1, emp.getFirstName());
                stmt.setString(2, emp.getLastName());
                stmt.setString(3, emp.getEmail());
                stmt.setDouble(4, emp.getSalary());
                stmt.setString(5, emp.getDepartment());
                stmt.setTimestamp(6, Timestamp.valueOf(emp.getHireDate()));
                
                stmt.addBatch();
            }
            
            stmt.executeBatch();
            conn.commit();
            
        } catch (SQLException e) {
            throw new DataAccessException("Error batch inserting employees", e);
        }
    }
}
```

### 2. **Walidacja i sanityzacja danych**

```python
import re
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ValidationRule:
    field_name: str
    required: bool = False
    min_length: int = 0
    max_length: int = None
    pattern: str = None
    allowed_values: List[str] = None
    custom_validator: callable = None

class InputValidator:
    
    def __init__(self):
        self.employee_rules = {
            'first_name': ValidationRule(
                field_name='first_name',
                required=True,
                min_length=2,
                max_length=50,
                pattern=r'^[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s\-\']+$'
            ),
            'last_name': ValidationRule(
                field_name='last_name',
                required=True,
                min_length=2,
                max_length=50,
                pattern=r'^[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s\-\']+$'
            ),
            'email': ValidationRule(
                field_name='email',
                required=True,
                max_length=100,
                custom_validator=self._validate_email
            ),
            'salary': ValidationRule(
                field_name='salary',
                required=True,
                custom_validator=self._validate_salary
            ),
            'department': ValidationRule(
                field_name='department',
                required=True,
                allowed_values=['IT', 'HR', 'Finance', 'Marketing', 'Engineering']
            )
        }
    
    def validate_employee_data(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        errors = {}
        
        for field_name, rule in self.employee_rules.items():
            field_errors = self._validate_field(data.get(field_name), rule)
            if field_errors:
                errors[field_name] = field_errors
        
        return errors
    
    def _validate_field(self, value: Any, rule: ValidationRule) -> List[str]:
        errors = []
        
        # Check if required
        if rule.required and (value is None or str(value).strip() == ''):
            errors.append(f"{rule.field_name} is required")
            return errors  # Stop further validation if required field is missing
        
        # Skip validation for optional empty fields
        if value is None or str(value).strip() == '':
            return errors
        
        value_str = str(value).strip()
        
        # Length validation
        if rule.min_length and len(value_str) < rule.min_length:
            errors.append(f"{rule.field_name} must be at least {rule.min_length} characters")
        
        if rule.max_length and len(value_str) > rule.max_length:
            errors.append(f"{rule.field_name} must not exceed {rule.max_length} characters")
        
        # Pattern validation
        if rule.pattern and not re.match(rule.pattern, value_str):
            errors.append(f"{rule.field_name} contains invalid characters")
        
        # Allowed values validation
        if rule.allowed_values and value_str not in rule.allowed_values:
            errors.append(f"{rule.field_name} must be one of: {', '.join(rule.allowed_values)}")
        
        # Custom validation
        if rule.custom_validator:
            custom_error = rule.custom_validator(value)
            if custom_error:
                errors.append(custom_error)
        
        return errors
    
    def _validate_email(self, email: str) -> str:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return "Invalid email format"
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '(', ')', '[', ']', '{', '}']
        if any(char in email for char in dangerous_chars):
            return "Email contains invalid characters"
        
        return None
    
    def _validate_salary(self, salary: Any) -> str:
        try:
            salary_float = float(salary)
            if salary_float < 0:
                return "Salary cannot be negative"
            if salary_float > 1000000:
                return "Salary value is unreasonably high"
            return None
        except (ValueError, TypeError):
            return "Salary must be a valid number"
    
    def sanitize_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize input data to prevent injection attacks"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Remove null bytes
                value = value.replace('\x00', '')
                
                # Trim whitespace
                value = value.strip()
                
                # Remove control characters except newlines and tabs
                value = ''.join(char for char in value 
                              if ord(char) >= 32 or char in '\n\t')
                
                # Limit length to prevent buffer overflow
                if len(value) > 10000:
                    value = value[:10000]
                
                sanitized[key] = value
            else:
                sanitized[key] = value
        
        return sanitized

# Usage in API endpoint
from flask import Flask, request, jsonify

app = Flask(__name__)
validator = InputValidator()

@app.route('/api/employees', methods=['POST'])
def create_employee():
    try:
        # Get and sanitize input
        raw_data = request.get_json()
        if not raw_data:
            return jsonify({'error': 'No data provided'}), 400
        
        sanitized_data = validator.sanitize_input(raw_data)
        
        # Validate input
        validation_errors = validator.validate_employee_data(sanitized_data)
        if validation_errors:
            return jsonify({
                'error': 'Validation failed',
                'details': validation_errors
            }), 400
        
        # Proceed with database operation using safe, validated data
        employee = create_employee_in_db(sanitized_data)
        
        return jsonify({
            'message': 'Employee created successfully',
            'employee_id': employee.id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating employee: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def create_employee_in_db(data: Dict[str, Any]):
    # Use parameterized query
    query = """
    INSERT INTO employees (first_name, last_name, email, salary, department, hire_date)
    VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
    RETURNING id
    """
    
    params = (
        data['first_name'],
        data['last_name'],
        data['email'],
        float(data['salary']),
        data['department']
    )
    
    return execute_query(query, params)
```

## Audyt i monitoring

### 1. **Audit Trail w PostgreSQL**

```sql
-- Tabela audytu
CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    row_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100) NOT NULL,
    client_ip INET,
    application_name VARCHAR(100),
    session_id VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indeksy dla wydajności
CREATE INDEX idx_audit_log_table_operation ON audit_log(table_name, operation);
CREATE INDEX idx_audit_log_changed_by ON audit_log(changed_by);
CREATE INDEX idx_audit_log_changed_at ON audit_log(changed_at);

-- Funkcja audytu generyczna
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    old_data JSONB;
    new_data JSONB;
    excluded_cols TEXT[] := ARRAY['last_updated', 'updated_at', 'modified_at'];
BEGIN
    -- Przygotuj dane dla logowania
    IF TG_OP = 'DELETE' THEN
        old_data := to_jsonb(OLD);
        new_data := NULL;
    ELSIF TG_OP = 'INSERT' THEN
        old_data := NULL;
        new_data := to_jsonb(NEW);
    ELSIF TG_OP = 'UPDATE' THEN
        old_data := to_jsonb(OLD);
        new_data := to_jsonb(NEW);
        
        -- Sprawdź czy rzeczywiście coś się zmieniło
        IF old_data = new_data THEN
            RETURN COALESCE(NEW, OLD);
        END IF;
    END IF;
    
    -- Usuń kolumny wyłączone z audytu
    IF old_data IS NOT NULL THEN
        SELECT jsonb_object_agg(key, value)
        INTO old_data
        FROM jsonb_each(old_data)
        WHERE key != ALL(excluded_cols);
    END IF;
    
    IF new_data IS NOT NULL THEN
        SELECT jsonb_object_agg(key, value)
        INTO new_data
        FROM jsonb_each(new_data)
        WHERE key != ALL(excluded_cols);
    END IF;
    
    -- Zapisz w logu audytu
    INSERT INTO audit_log (
        table_name,
        operation,
        row_id,
        old_values,
        new_values,
        changed_by,
        client_ip,
        application_name,
        session_id
    ) VALUES (
        TG_TABLE_NAME,
        TG_OP,
        COALESCE(NEW.id, OLD.id),
        old_data,
        new_data,
        current_user,
        inet_client_addr(),
        current_setting('application_name', true),
        current_setting('app.session_id', true)
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Dodaj audyt do tabel
CREATE TRIGGER employees_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER salary_changes_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON salary_changes
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

-- Specjalna funkcja audytu dla wrażliwych operacji
CREATE OR REPLACE FUNCTION sensitive_data_audit()
RETURNS TRIGGER AS $$
DECLARE
    change_summary TEXT;
BEGIN
    IF TG_OP = 'UPDATE' AND TG_TABLE_NAME = 'employees' THEN
        -- Szczególnie monitoruj zmiany pensji
        IF OLD.salary IS DISTINCT FROM NEW.salary THEN
            change_summary := format('Salary changed from %s to %s', OLD.salary, NEW.salary);
            
            -- Natychmiastowe powiadomienie dla dużych zmian
            IF ABS(NEW.salary - OLD.salary) > OLD.salary * 0.2 THEN
                PERFORM pg_notify('salary_alert', 
                    format('Large salary change for employee %s: %s', NEW.id, change_summary)
                );
            END IF;
        END IF;
        
        -- Monitoruj zmiany działu
        IF OLD.department IS DISTINCT FROM NEW.department THEN
            change_summary := format('Department changed from %s to %s', OLD.department, NEW.department);
            
            INSERT INTO department_transfer_log (
                employee_id, old_department, new_department, 
                changed_by, changed_at
            ) VALUES (
                NEW.id, OLD.department, NEW.department,
                current_user, CURRENT_TIMESTAMP
            );
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER employees_sensitive_audit
    AFTER UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION sensitive_data_audit();
```

### 2. **Monitoring połączeń i wydajności**

```sql
-- Widok monitorowania aktywnych połączeń
CREATE VIEW active_connections AS
SELECT 
    pid,
    usename AS username,
    application_name,
    client_addr,
    client_port,
    backend_start,
    state,
    state_change,
    query_start,
    query,
    wait_event_type,
    wait_event
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY backend_start;

-- Funkcja do monitorowania podejrzanej aktywności
CREATE OR REPLACE FUNCTION monitor_suspicious_activity()
RETURNS TABLE (
    alert_type TEXT,
    username TEXT,
    client_ip INET,
    query_count BIGINT,
    details TEXT
) AS $$
BEGIN
    -- Zbyt wiele połączeń z jednego IP
    RETURN QUERY
    SELECT 
        'TOO_MANY_CONNECTIONS'::TEXT,
        usename,
        client_addr,
        COUNT(*)::BIGINT,
        format('IP %s has %s active connections', client_addr, COUNT(*))
    FROM pg_stat_activity
    WHERE state = 'active'
      AND client_addr IS NOT NULL
    GROUP BY usename, client_addr
    HAVING COUNT(*) > 10;
    
    -- Długo wykonujące się zapytania
    RETURN QUERY
    SELECT 
        'LONG_RUNNING_QUERY'::TEXT,
        usename,
        client_addr,
        1::BIGINT,
        format('Query running for %s minutes', 
               EXTRACT(EPOCH FROM (now() - query_start))/60)
    FROM pg_stat_activity
    WHERE state = 'active'
      AND query_start < now() - INTERVAL '5 minutes'
      AND query NOT LIKE '%pg_sleep%';
    
    -- Podejrzane wzorce zapytań
    RETURN QUERY
    SELECT 
        'SUSPICIOUS_QUERY'::TEXT,
        usename,
        client_addr,
        1::BIGINT,
        'Query contains potential SQL injection patterns'
    FROM pg_stat_activity
    WHERE state = 'active'
      AND (
          query ILIKE '%union%select%'
          OR query ILIKE '%1=1%'
          OR query ILIKE '%drop%table%'
          OR query ILIKE '%information_schema%'
      );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Funkcja do logowania nieudanych prób logowania
CREATE TABLE failed_login_attempts (
    attempt_id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    client_ip INET,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    failure_reason TEXT
);

-- Trigger do monitorowania nieudanych logowań (wymaga rozszerzenia)
CREATE OR REPLACE FUNCTION log_failed_login()
RETURNS event_trigger AS $$
BEGIN
    -- Ta funkcja wymagałaby rozszerzenia lub external monitoring
    -- W praktyce monitoruje się logi PostgreSQL
END;
$$ LANGUAGE plpgsql;
```

### 3. **Monitoring na poziomie aplikacji**

```python
import logging
import time
from functools import wraps
from typing import Dict, Any, Optional
import psycopg2
from contextlib import contextmanager

class DatabaseSecurityMonitor:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.suspicious_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bdrop\b.*\btable\b)",
            r"(\bdelete\b.*\bfrom\b.*\bwhere\b.*\b1\s*=\s*1\b)",
            r"(\binformation_schema\b)",
            r"(\bpg_\w+\b)",  # PostgreSQL system functions
            r"(\bload_file\b)",
            r"(\binto\s+outfile\b)"
        ]
    
    def log_database_operation(self, operation: str, user: str, query: str, 
                             params: tuple = None, client_ip: str = None):
        """Log database operations for security monitoring"""
        
        # Check for suspicious patterns
        if self._is_suspicious_query(query):
            self.logger.warning(
                "SUSPICIOUS_QUERY_DETECTED",
                extra={
                    'operation': operation,
                    'user': user,
                    'query': query[:200],  # Truncate for logging
                    'client_ip': client_ip,
                    'alert_level': 'HIGH'
                }
            )
        
        # Log operation
        self.logger.info(
            "DATABASE_OPERATION",
            extra={
                'operation': operation,
                'user': user,
                'query_hash': hash(query),
                'param_count': len(params) if params else 0,
                'client_ip': client_ip
            }
        )
    
    def _is_suspicious_query(self, query: str) -> bool:
        """Check if query contains suspicious patterns"""
        import re
        query_lower = query.lower()
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return True
        
        return False
    
    def monitor_connection_attempts(self, username: str, client_ip: str, 
                                  success: bool, error_msg: str = None):
        """Monitor and log connection attempts"""
        
        if success:
            self.logger.info(
                "SUCCESSFUL_LOGIN",
                extra={
                    'username': username,
                    'client_ip': client_ip
                }
            )
        else:
            self.logger.warning(
                "FAILED_LOGIN_ATTEMPT",
                extra={
                    'username': username,
                    'client_ip': client_ip,
                    'error': error_msg,
                    'alert_level': 'MEDIUM'
                }
            )

class SecureDatabaseConnection:
    def __init__(self, connection_config: Dict[str, Any], 
                 security_monitor: DatabaseSecurityMonitor):
        self.config = connection_config
        self.monitor = security_monitor
        self._connection = None
    
    @contextmanager
    def get_connection(self, user_context: Dict[str, Any] = None):
        """Get secure database connection with monitoring"""
        
        start_time = time.time()
        connection = None
        
        try:
            # Attempt connection
            connection = psycopg2.connect(**self.config)
            
            # Set application context
            if user_context:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT set_config('app.current_user_id', %s, false)",
                        (str(user_context.get('user_id', '')),)
                    )
                    cursor.execute(
                        "SELECT set_config('app.session_id', %s, false)",
                        (user_context.get('session_id', ''),)
                    )
            
            self.monitor.monitor_connection_attempts(
                user_context.get('username', 'unknown') if user_context else 'system',
                user_context.get('client_ip', 'unknown') if user_context else 'localhost',
                success=True
            )
            
            yield connection
            
        except psycopg2.Error as e:
            self.monitor.monitor_connection_attempts(
                user_context.get('username', 'unknown') if user_context else 'system',
                user_context.get('client_ip', 'unknown') if user_context else 'localhost',
                success=False,
                error_msg=str(e)
            )
            raise
            
        finally:
            if connection:
                connection.close()
            
            execution_time = time.time() - start_time
            if execution_time > 30:  # Long connection time
                self.monitor.logger.warning(
                    "LONG_CONNECTION_TIME",
                    extra={
                        'execution_time': execution_time,
                        'user': user_context.get('username', 'unknown') if user_context else 'system'
                    }
                )

def secure_query_executor(monitor: DatabaseSecurityMonitor):
    """Decorator for secure query execution with monitoring"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract query and parameters from function call
            query = kwargs.get('query') or (args[0] if args else '')
            params = kwargs.get('params') or (args[1] if len(args) > 1 else None)
            user_context = kwargs.get('user_context', {})
            
            # Monitor the operation
            monitor.log_database_operation(
                operation=func.__name__,
                user=user_context.get('username', 'system'),
                query=query,
                params=params,
                client_ip=user_context.get('client_ip')
            )
            
            # Execute the function
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log slow queries
                if execution_time > 5:
                    monitor.logger.warning(
                        "SLOW_QUERY",
                        extra={
                            'execution_time': execution_time,
                            'query_hash': hash(query),
                            'user': user_context.get('username', 'system')
                        }
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                monitor.logger.error(
                    "QUERY_EXECUTION_ERROR",
                    extra={
                        'error': str(e),
                        'execution_time': execution_time,
                        'query_hash': hash(query),
                        'user': user_context.get('username', 'system')
                    }
                )
                raise
        
        return wrapper
    return decorator

# Usage example
logger = logging.getLogger('database_security')
security_monitor = DatabaseSecurityMonitor(logger)
db_connection = SecureDatabaseConnection(connection_config, security_monitor)

@secure_query_executor(security_monitor)
def execute_secure_query(query: str, params: tuple = None, user_context: Dict = None):
    """Execute query with security monitoring"""
    
    with db_connection.get_connection(user_context) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

# Example usage
user_ctx = {
    'user_id': 123,
    'username': 'john.doe',
    'session_id': 'sess_abc123',
    'client_ip': '192.168.1.100'
}

employees = execute_secure_query(
    "SELECT * FROM employees WHERE department = %s",
    ('IT',),
    user_context=user_ctx
)
```

## Najlepsze praktyki bezpieczeństwa

### ✅ **Dobre praktyki:**

#### 1. **Principle of Least Privilege**
```sql
-- Dedykowane role dla różnych funkcji
CREATE ROLE app_read_only;
CREATE ROLE app_write;
CREATE ROLE reporting_user;
CREATE ROLE backup_operator;

-- Minimalne wymagane uprawnienia
GRANT CONNECT ON DATABASE company_db TO app_read_only;
GRANT USAGE ON SCHEMA public TO app_read_only;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_read_only;
```

#### 2. **Szyfrowanie**
```sql
-- Szyfrowanie wrażliwych danych
-- TLS/SSL dla połączeń
-- Szyfrowanie na poziomie kolumn dla PII
-- Szyfrowanie backup'ów
```

#### 3. **Monitoring i audyt**
```sql
-- Logowanie wszystkich operacji DML na wrażliwych tabelach
-- Monitoring nieudanych prób logowania
-- Alerting na podejrzane aktywności
-- Regular security audits
```

### ❌ **Złe praktyki:**

```sql
-- ❌ Używanie kont z nadmiernymi uprawnieniami
GRANT ALL PRIVILEGES ON ALL TABLES TO app_user;

-- ❌ Hasła w kodzie źródłowym
conn = psycopg2.connect("host=localhost user=postgres password=admin123")

-- ❌ Brak walidacji input'u
query = f"SELECT * FROM users WHERE id = {user_input}"

-- ❌ Przechowywanie haseł w plain text
INSERT INTO users VALUES ('john', 'password123');
```

## Pułapki egzaminacyjne

### 1. **Row Level Security**
```
RLS działa tylko dla operacji przez SQL
SUPERUSER może ominąć polityki RLS
Polityki muszą być włączone per tabela
```

### 2. **SQL Injection**
```
Prepared statements = bezpieczne
String concatenation = niebezpieczne
Walidacja po stronie klienta = nie wystarczy
```

### 3. **Uprawnienia**
```
GRANT/REVOKE operują na poziomie ról
Uprawnienia są dziedziczone przez role
PUBLIC = wszyscy użytkownicy
```

### 4. **Audyt**
```
Triggery AFTER vs BEFORE dla audytu
SECURITY DEFINER vs SECURITY INVOKER
pg_stat_activity dla monitorowania sesji
```