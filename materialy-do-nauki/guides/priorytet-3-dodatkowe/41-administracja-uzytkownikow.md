# Administracja użytkowników i uprawnień

## Definicja administracji użytkowników

**Administracja użytkowników** to proces **zarządzania kontami, rolami i uprawnieniami** w systemie bazy danych, zapewniający **bezpieczny i kontrolowany dostęp** do zasobów zgodnie z zasadą najmniejszych uprawnień.

### Kluczowe koncepty:
- **Authentication** - weryfikacja tożsamości użytkownika
- **Authorization** - kontrola dostępu do zasobów
- **Role-Based Access Control (RBAC)** - uprawnienia oparte na rolach
- **Principle of Least Privilege** - minimalne wymagane uprawnienia
- **Separation of Duties** - podział odpowiedzialności
- **Access Audit** - śledzenie dostępu do zasobów

### Hierarchia uprawnień:
- **System level** - uprawnienia na poziomie systemu
- **Database level** - uprawnienia na poziomie bazy danych
- **Schema level** - uprawnienia na poziomie schematu
- **Object level** - uprawnienia na poziomie obiektów (tabele, widoki)
- **Column level** - uprawnienia na poziomie kolumn

## Zarządzanie użytkownikami w PostgreSQL

### 1. **Tworzenie i zarządzanie rolami**

#### Podstawowe operacje na rolach:
```sql
-- Tworzenie roli podstawowej
CREATE ROLE app_user WITH LOGIN PASSWORD 'secure_password_123!';

-- Tworzenie roli z dodatkowymi opcjami
CREATE ROLE senior_developer WITH
    LOGIN
    PASSWORD 'complex_password_456!'
    VALID UNTIL '2024-12-31'
    CONNECTION LIMIT 10
    CREATEDB
    CREATEROLE;

-- Tworzenie roli grupowej (bez logowania)
CREATE ROLE developers;
CREATE ROLE administrators; 
CREATE ROLE readonly_users;

-- Modyfikacja istniejącej roli
ALTER ROLE app_user SET search_path TO app_schema, public;
ALTER ROLE app_user CONNECTION LIMIT 5;
ALTER ROLE app_user VALID UNTIL '2024-06-30';

-- Zmiana hasła
ALTER ROLE app_user PASSWORD 'new_secure_password_789!';

-- Blokowanie/odblokowanie konta
ALTER ROLE app_user NOLOGIN;  -- Blokowanie
ALTER ROLE app_user LOGIN;    -- Odblokowanie

-- Usuwanie roli
DROP ROLE IF EXISTS old_user;
```

#### Zaawansowane zarządzanie rolami:
```sql
-- Rola z ograniczeniami czasowymi
CREATE ROLE temp_contractor WITH
    LOGIN
    PASSWORD 'temp_password_123!'
    VALID UNTIL '2024-03-31 23:59:59'
    CONNECTION LIMIT 2;

-- Rola systemowa bez możliwości logowania
CREATE ROLE service_account WITH
    NOLOGIN
    CREATEROLE
    CREATEDB;

-- Rola z dziedziczeniem uprawnień
CREATE ROLE manager WITH
    LOGIN
    PASSWORD 'manager_password!'
    INHERIT  -- Dziedziczy uprawnienia przypisanych ról
    CREATEROLE;

-- Rola bez dziedziczenia (wymagane jawne SET ROLE)
CREATE ROLE security_admin WITH
    LOGIN
    PASSWORD 'admin_password!'
    NOINHERIT  -- Nie dziedziczy automatycznie
    SUPERUSER;

-- Sprawdzanie istniejących ról
SELECT 
    rolname,
    rolsuper,
    rolinherit,
    rolcreaterole,
    rolcreatedb,
    rolcanlogin,
    rolconnlimit,
    rolvaliduntil
FROM pg_roles
ORDER BY rolname;

-- Szczegółowe informacje o rolach
\du+ -- w psql
```

### 2. **Hierarchie ról i dziedziczenie**

#### System ról hierarchicznych:
```sql
-- Tworzenie hierarchii ról korporacyjnych
-- Poziom 1: Role podstawowe
CREATE ROLE employee WITH NOLOGIN;
CREATE ROLE contractor WITH NOLOGIN;

-- Poziom 2: Role departamentowe  
CREATE ROLE it_department WITH NOLOGIN;
CREATE ROLE hr_department WITH NOLOGIN;
CREATE ROLE finance_department WITH NOLOGIN;

-- Poziom 3: Role funkcyjne
CREATE ROLE developer WITH NOLOGIN;
CREATE ROLE dba WITH NOLOGIN;
CREATE ROLE analyst WITH NOLOGIN;
CREATE ROLE manager WITH NOLOGIN;

-- Poziom 4: Role operacyjne
CREATE ROLE junior_developer WITH NOLOGIN;
CREATE ROLE senior_developer WITH NOLOGIN;
CREATE ROLE lead_developer WITH NOLOGIN;
CREATE ROLE project_manager WITH NOLOGIN;

-- Budowanie hierarchii przez przypisanie ról
-- Wszyscy pracownicy mają podstawowe uprawnienia
GRANT employee TO it_department, hr_department, finance_department;

-- Departament IT ma dodatkowe uprawnienia techniczne
GRANT it_department TO developer, dba;

-- Deweloperzy mają różne poziomy uprawnień
GRANT developer TO junior_developer, senior_developer;
GRANT senior_developer TO lead_developer;

-- Managerowie mają uprawnienia raportowe
GRANT manager TO project_manager;
GRANT it_department TO project_manager;

-- Tworzenie konkretnych użytkowników
CREATE ROLE john_doe WITH 
    LOGIN 
    PASSWORD 'john_secure_pass!'
    INHERIT;
    
CREATE ROLE jane_smith WITH 
    LOGIN 
    PASSWORD 'jane_secure_pass!'
    INHERIT;

-- Przypisanie ról użytkownikom
GRANT junior_developer TO john_doe;
GRANT lead_developer TO jane_smith;

-- Sprawdzenie hierarchii uprawnień
WITH RECURSIVE role_hierarchy AS (
    -- Role bezpośrednio przypisane użytkownikowi
    SELECT 
        r.rolname as user_role,
        m.rolname as granted_role,
        1 as level
    FROM pg_roles r
    JOIN pg_auth_members am ON r.oid = am.member
    JOIN pg_roles m ON am.roleid = m.oid
    WHERE r.rolcanlogin = true
    
    UNION ALL
    
    -- Role dziedziczone przez hierarchię
    SELECT 
        rh.user_role,
        m.rolname as granted_role,
        rh.level + 1
    FROM role_hierarchy rh
    JOIN pg_auth_members am ON am.member = (
        SELECT oid FROM pg_roles WHERE rolname = rh.granted_role
    )
    JOIN pg_roles m ON am.roleid = m.oid
    WHERE rh.level < 10 -- Zabezpieczenie przed cyklami
)
SELECT DISTINCT 
    user_role,
    granted_role,
    level
FROM role_hierarchy
ORDER BY user_role, level, granted_role;
```

### 3. **Uprawnienia na różnych poziomach**

#### Uprawnienia na poziomie bazy danych:
```sql
-- Uprawnienia podstawowe na bazę danych
GRANT CONNECT ON DATABASE company_db TO employee;
GRANT CREATE ON DATABASE company_db TO developer;
GRANT TEMP ON DATABASE company_db TO analyst;

-- Uprawnienia na schemat
GRANT USAGE ON SCHEMA public TO employee;
GRANT USAGE ON SCHEMA app_schema TO it_department;
GRANT CREATE ON SCHEMA app_schema TO developer;
GRANT ALL ON SCHEMA admin_schema TO dba;

-- Uprawnienia na wszystkie tabele w schemacie
GRANT SELECT ON ALL TABLES IN SCHEMA public TO employee;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app_schema TO developer;
GRANT ALL ON ALL TABLES IN SCHEMA admin_schema TO dba;

-- Uprawnienia na przyszłe tabele
ALTER DEFAULT PRIVILEGES IN SCHEMA app_schema 
    GRANT SELECT ON TABLES TO employee;
    
ALTER DEFAULT PRIVILEGES IN SCHEMA app_schema 
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO developer;

-- Uprawnienia na sekwencje
GRANT USAGE ON ALL SEQUENCES IN SCHEMA app_schema TO developer;
ALTER DEFAULT PRIVILEGES IN SCHEMA app_schema 
    GRANT USAGE ON SEQUENCES TO developer;

-- Uprawnienia na funkcje
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA app_schema TO developer;
ALTER DEFAULT PRIVILEGES IN SCHEMA app_schema 
    GRANT EXECUTE ON FUNCTIONS TO developer;
```

#### Uprawnienia szczegółowe na tabele:
```sql
-- Tabela z danymi osobowymi - różne poziomy dostępu
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    salary NUMERIC(10,2),
    ssn VARCHAR(11),
    hire_date DATE DEFAULT CURRENT_DATE,
    department_id INTEGER,
    manager_id INTEGER
);

-- HR ma pełny dostęp
GRANT ALL ON employees TO hr_department;

-- Managerowie mogą czytać podstawowe dane podwładnych
GRANT SELECT (employee_id, first_name, last_name, email, department_id, manager_id) 
    ON employees TO manager;

-- Pracownicy mogą czytać tylko podstawowe dane wszystkich
GRANT SELECT (employee_id, first_name, last_name, email, department_id) 
    ON employees TO employee;

-- Księgowość ma dostęp do danych płacowych
GRANT SELECT (employee_id, first_name, last_name, salary, hire_date) 
    ON employees TO finance_department;

-- Zewnętrzni kontrahenci - tylko podstawowe dane kontaktowe
GRANT SELECT (first_name, last_name, email) 
    ON employees TO contractor;

-- Uprawnienia warunkowe z Row Level Security
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;

-- Polityka dla managerów - widzą tylko swoich podwładnych
CREATE POLICY manager_sees_subordinates ON employees
    FOR SELECT
    TO manager
    USING (
        manager_id = current_setting('app.current_user_id')::INTEGER
        OR employee_id = current_setting('app.current_user_id')::INTEGER
    );

-- Polityka dla pracowników - widzą tylko siebie
CREATE POLICY employee_sees_self ON employees
    FOR SELECT  
    TO employee
    USING (employee_id = current_setting('app.current_user_id')::INTEGER);

-- Polityka dla HR - pełny dostęp
CREATE POLICY hr_full_access ON employees
    FOR ALL
    TO hr_department
    USING (true)
    WITH CHECK (true);
```

## Zaawansowane zarządzanie uprawnieniami

### 1. **Dynamic Role Assignment**

```sql
-- Funkcja do dynamicznego przypisywania ról na podstawie projektu
CREATE OR REPLACE FUNCTION assign_project_role(
    p_user_name TEXT,
    p_project_id INTEGER,
    p_role_type TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    project_role_name TEXT;
    user_exists BOOLEAN;
    role_exists BOOLEAN;
BEGIN
    -- Sprawdź czy użytkownik istnieje
    SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname = p_user_name) INTO user_exists;
    IF NOT user_exists THEN
        RAISE EXCEPTION 'User % does not exist', p_user_name;
    END IF;
    
    -- Utwórz nazwę roli projektu
    project_role_name := format('project_%s_%s', p_project_id, p_role_type);
    
    -- Sprawdź czy rola projektu istnieje
    SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname = project_role_name) INTO role_exists;
    
    -- Utwórz rolę jeśli nie istnieje
    IF NOT role_exists THEN
        EXECUTE format('CREATE ROLE %I WITH NOLOGIN', project_role_name);
        
        -- Przypisz uprawnienia na podstawie typu roli
        CASE p_role_type
            WHEN 'viewer' THEN
                EXECUTE format('GRANT SELECT ON project_%s_tables TO %I', 
                             p_project_id, project_role_name);
            WHEN 'editor' THEN  
                EXECUTE format('GRANT SELECT, INSERT, UPDATE ON project_%s_tables TO %I', 
                             p_project_id, project_role_name);
            WHEN 'admin' THEN
                EXECUTE format('GRANT ALL ON project_%s_tables TO %I', 
                             p_project_id, project_role_name);
        END CASE;
        
        -- Log utworzenia roli
        INSERT INTO role_audit_log (action, role_name, performed_by, performed_at)
        VALUES ('CREATE_PROJECT_ROLE', project_role_name, current_user, CURRENT_TIMESTAMP);
    END IF;
    
    -- Przypisz rolę użytkownikowi
    EXECUTE format('GRANT %I TO %I', project_role_name, p_user_name);
    
    -- Log przypisania
    INSERT INTO role_audit_log (action, role_name, target_user, performed_by, performed_at)
    VALUES ('GRANT_ROLE', project_role_name, p_user_name, current_user, CURRENT_TIMESTAMP);
    
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        -- Log błędu
        INSERT INTO role_audit_log (action, role_name, target_user, error_message, performed_by, performed_at)
        VALUES ('GRANT_ROLE_ERROR', project_role_name, p_user_name, SQLERRM, current_user, CURRENT_TIMESTAMP);
        
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Funkcja do automatycznego odwoływania ról po zakończeniu projektu
CREATE OR REPLACE FUNCTION revoke_expired_project_roles()
RETURNS INTEGER AS $$
DECLARE
    expired_project RECORD;
    project_role RECORD;
    revoked_count INTEGER := 0;
BEGIN
    -- Znajdź zakończone projekty
    FOR expired_project IN 
        SELECT project_id 
        FROM projects 
        WHERE end_date < CURRENT_DATE 
          AND status = 'COMPLETED'
    LOOP
        -- Znajdź wszystkie role związane z projektem
        FOR project_role IN
            SELECT rolname
            FROM pg_roles
            WHERE rolname LIKE 'project_' || expired_project.project_id || '_%'
        LOOP
            -- Odwołaj rolę od wszystkich użytkowników
            EXECUTE format('REVOKE %I FROM ALL', project_role.rolname);
            
            -- Usuń rolę
            EXECUTE format('DROP ROLE %I', project_role.rolname);
            
            revoked_count := revoked_count + 1;
            
            -- Log operacji
            INSERT INTO role_audit_log (action, role_name, performed_by, performed_at)
            VALUES ('REVOKE_EXPIRED_ROLE', project_role.rolname, 'system', CURRENT_TIMESTAMP);
        END LOOP;
    END LOOP;
    
    RETURN revoked_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Tabela do audytu operacji na rolach
CREATE TABLE role_audit_log (
    log_id SERIAL PRIMARY KEY,
    action VARCHAR(50) NOT NULL,
    role_name VARCHAR(100),
    target_user VARCHAR(100),
    error_message TEXT,
    performed_by VARCHAR(100) NOT NULL,
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index dla wydajności
CREATE INDEX idx_role_audit_log_timestamp ON role_audit_log(performed_at);
CREATE INDEX idx_role_audit_log_action ON role_audit_log(action);
```

### 2. **Temporary Access Management**

```sql
-- System tymczasowego dostępu
CREATE TABLE temporary_access_grants (
    grant_id SERIAL PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    role_name VARCHAR(100) NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    granted_by VARCHAR(100) NOT NULL,
    reason TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    revoked_at TIMESTAMP,
    revoked_by VARCHAR(100)
);

-- Funkcja przyznawania tymczasowego dostępu
CREATE OR REPLACE FUNCTION grant_temporary_access(
    p_user_name TEXT,
    p_role_name TEXT,
    p_duration_hours INTEGER,
    p_reason TEXT
)
RETURNS INTEGER AS $$
DECLARE
    grant_id INTEGER;
    expires_at TIMESTAMP;
BEGIN
    -- Sprawdź czy użytkownik i rola istnieją
    IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname = p_user_name) THEN
        RAISE EXCEPTION 'User % does not exist', p_user_name;
    END IF;
    
    IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname = p_role_name) THEN
        RAISE EXCEPTION 'Role % does not exist', p_role_name;
    END IF;
    
    -- Oblicz czas wygaśnięcia
    expires_at := CURRENT_TIMESTAMP + (p_duration_hours || ' hours')::INTERVAL;
    
    -- Sprawdź czy użytkownik już ma tę rolę na stałe
    IF EXISTS(
        SELECT 1 FROM pg_auth_members am
        JOIN pg_roles member ON am.member = member.oid
        JOIN pg_roles role_granted ON am.roleid = role_granted.oid
        WHERE member.rolname = p_user_name 
          AND role_granted.rolname = p_role_name
          AND am.admin_option = FALSE  -- Nie jest temporary grant
    ) THEN
        RAISE NOTICE 'User % already has permanent access to role %', p_user_name, p_role_name;
        RETURN NULL;
    END IF;
    
    -- Przyznaj rolę
    EXECUTE format('GRANT %I TO %I', p_role_name, p_user_name);
    
    -- Zapisz w systemie tymczasowych dostępów
    INSERT INTO temporary_access_grants (
        user_name, role_name, expires_at, granted_by, reason
    ) VALUES (
        p_user_name, p_role_name, expires_at, current_user, p_reason
    ) RETURNING grant_id INTO grant_id;
    
    -- Log operacji
    INSERT INTO role_audit_log (action, role_name, target_user, performed_by, performed_at)
    VALUES ('GRANT_TEMPORARY', p_role_name, p_user_name, current_user, CURRENT_TIMESTAMP);
    
    RAISE NOTICE 'Temporary access granted to % for % until %', p_user_name, p_role_name, expires_at;
    
    RETURN grant_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Funkcja do automatycznego odwoływania wygasłych dostępów
CREATE OR REPLACE FUNCTION revoke_expired_access()
RETURNS INTEGER AS $$
DECLARE
    expired_grant RECORD;
    revoked_count INTEGER := 0;
BEGIN
    -- Znajdź wygasłe dostępy
    FOR expired_grant IN 
        SELECT grant_id, user_name, role_name
        FROM temporary_access_grants
        WHERE expires_at < CURRENT_TIMESTAMP 
          AND is_active = TRUE
    LOOP
        -- Odwołaj rolę
        BEGIN
            EXECUTE format('REVOKE %I FROM %I', expired_grant.role_name, expired_grant.user_name);
            
            -- Oznacz jako nieaktywny
            UPDATE temporary_access_grants 
            SET is_active = FALSE,
                revoked_at = CURRENT_TIMESTAMP,
                revoked_by = 'system_auto'
            WHERE grant_id = expired_grant.grant_id;
            
            revoked_count := revoked_count + 1;
            
            -- Log operacji
            INSERT INTO role_audit_log (action, role_name, target_user, performed_by, performed_at)
            VALUES ('REVOKE_EXPIRED', expired_grant.role_name, expired_grant.user_name, 'system', CURRENT_TIMESTAMP);
            
        EXCEPTION WHEN OTHERS THEN
            -- Log błędu, ale kontynuuj
            INSERT INTO role_audit_log (action, role_name, target_user, error_message, performed_by, performed_at)
            VALUES ('REVOKE_ERROR', expired_grant.role_name, expired_grant.user_name, SQLERRM, 'system', CURRENT_TIMESTAMP);
        END;
    END LOOP;
    
    RETURN revoked_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Widok dla monitorowania tymczasowych dostępów
CREATE VIEW active_temporary_grants AS
SELECT 
    tag.grant_id,
    tag.user_name,
    tag.role_name,
    tag.granted_at,
    tag.expires_at,
    tag.granted_by,
    tag.reason,
    EXTRACT(EPOCH FROM (tag.expires_at - CURRENT_TIMESTAMP))/3600 AS hours_remaining
FROM temporary_access_grants tag
WHERE tag.is_active = TRUE
  AND tag.expires_at > CURRENT_TIMESTAMP
ORDER BY tag.expires_at;

-- Funkcja do przedłużania tymczasowego dostępu
CREATE OR REPLACE FUNCTION extend_temporary_access(
    p_grant_id INTEGER,
    p_additional_hours INTEGER
)
RETURNS BOOLEAN AS $$
DECLARE
    old_expires_at TIMESTAMP;
    new_expires_at TIMESTAMP;
BEGIN
    -- Sprawdź czy grant istnieje i jest aktywny
    SELECT expires_at INTO old_expires_at
    FROM temporary_access_grants
    WHERE grant_id = p_grant_id
      AND is_active = TRUE;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Temporary grant % not found or not active', p_grant_id;
    END IF;
    
    -- Oblicz nowy czas wygaśnięcia
    new_expires_at := old_expires_at + (p_additional_hours || ' hours')::INTERVAL;
    
    -- Aktualizuj
    UPDATE temporary_access_grants
    SET expires_at = new_expires_at
    WHERE grant_id = p_grant_id;
    
    -- Log operacji  
    INSERT INTO role_audit_log (action, role_name, target_user, performed_by, performed_at)
    SELECT 'EXTEND_TEMPORARY', role_name, user_name, current_user, CURRENT_TIMESTAMP
    FROM temporary_access_grants
    WHERE grant_id = p_grant_id;
    
    RAISE NOTICE 'Temporary access extended until %', new_expires_at;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 3. **Access Review and Compliance**

```sql
-- System okresowego przeglądu uprawnień
CREATE TABLE access_reviews (
    review_id SERIAL PRIMARY KEY,
    review_type VARCHAR(50) NOT NULL, -- QUARTERLY, ANNUAL, AUDIT
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    performed_by VARCHAR(100) NOT NULL,
    scope TEXT, -- JSON with review scope
    status VARCHAR(20) DEFAULT 'IN_PROGRESS' -- IN_PROGRESS, COMPLETED, CANCELLED
);

CREATE TABLE access_review_items (
    item_id SERIAL PRIMARY KEY,
    review_id INTEGER REFERENCES access_reviews(review_id),
    user_name VARCHAR(100) NOT NULL,
    role_name VARCHAR(100) NOT NULL,
    granted_date TIMESTAMP,
    last_used TIMESTAMP,
    review_status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, APPROVED, REVOKED
    reviewer VARCHAR(100),
    reviewed_at TIMESTAMP,
    justification TEXT
);

-- Funkcja do rozpoczęcia przeglądu uprawnień
CREATE OR REPLACE FUNCTION start_access_review(
    p_review_type TEXT,
    p_scope TEXT DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    review_id INTEGER;
    role_assignment RECORD;
BEGIN
    -- Utwórz nowy przegląd
    INSERT INTO access_reviews (review_type, performed_by, scope)
    VALUES (p_review_type, current_user, p_scope)
    RETURNING review_id INTO review_id;
    
    -- Dodaj wszystkie przypisania ról do przeglądu
    FOR role_assignment IN
        SELECT 
            member.rolname as user_name,
            role_granted.rolname as role_name,
            COALESCE(ral.performed_at, '1970-01-01'::timestamp) as granted_date,
            aus.last_access as last_used
        FROM pg_auth_members am
        JOIN pg_roles member ON am.member = member.oid
        JOIN pg_roles role_granted ON am.roleid = role_granted.oid
        LEFT JOIN role_audit_log ral ON ral.target_user = member.rolname 
                                      AND ral.role_name = role_granted.rolname
                                      AND ral.action = 'GRANT_ROLE'
        LEFT JOIN access_usage_stats aus ON aus.user_name = member.rolname
                                           AND aus.role_name = role_granted.rolname
        WHERE member.rolcanlogin = TRUE  -- Tylko użytkownicy mogący się logować
          AND role_granted.rolname NOT LIKE 'pg_%'  -- Wyklucz role systemowe
    LOOP
        INSERT INTO access_review_items (
            review_id, user_name, role_name, granted_date, last_used
        ) VALUES (
            review_id, role_assignment.user_name, role_assignment.role_name,
            role_assignment.granted_date, role_assignment.last_used
        );
    END LOOP;
    
    RAISE NOTICE 'Access review % started with % items', review_id, 
                 (SELECT COUNT(*) FROM access_review_items WHERE review_id = review_id);
    
    RETURN review_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Funkcja raportowania niewykorzystanych uprawnień
CREATE OR REPLACE FUNCTION report_unused_access(
    p_days_threshold INTEGER DEFAULT 90
)
RETURNS TABLE(
    user_name TEXT,
    role_name TEXT,
    granted_date TIMESTAMP,
    days_unused INTEGER,
    risk_level TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH role_usage AS (
        SELECT 
            member.rolname as user_name,
            role_granted.rolname as role_name,
            COALESCE(ral.performed_at, '1970-01-01'::timestamp) as granted_date,
            COALESCE(aus.last_access, '1970-01-01'::timestamp) as last_used
        FROM pg_auth_members am
        JOIN pg_roles member ON am.member = member.oid
        JOIN pg_roles role_granted ON am.roleid = role_granted.oid
        LEFT JOIN role_audit_log ral ON ral.target_user = member.rolname 
                                      AND ral.role_name = role_granted.rolname
                                      AND ral.action = 'GRANT_ROLE'
        LEFT JOIN access_usage_stats aus ON aus.user_name = member.rolname
                                           AND aus.role_name = role_granted.rolname
        WHERE member.rolcanlogin = TRUE
          AND role_granted.rolname NOT LIKE 'pg_%'
    )
    SELECT 
        ru.user_name::TEXT,
        ru.role_name::TEXT,
        ru.granted_date,
        EXTRACT(DAY FROM CURRENT_TIMESTAMP - ru.last_used)::INTEGER as days_unused,
        CASE 
            WHEN EXTRACT(DAY FROM CURRENT_TIMESTAMP - ru.last_used) > 365 THEN 'HIGH'
            WHEN EXTRACT(DAY FROM CURRENT_TIMESTAMP - ru.last_used) > 180 THEN 'MEDIUM'
            WHEN EXTRACT(DAY FROM CURRENT_TIMESTAMP - ru.last_used) > p_days_threshold THEN 'LOW'
            ELSE 'ACTIVE'
        END::TEXT as risk_level
    FROM role_usage ru
    WHERE EXTRACT(DAY FROM CURRENT_TIMESTAMP - ru.last_used) > p_days_threshold
    ORDER BY days_unused DESC, ru.user_name, ru.role_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Tabela do śledzenia użycia dostępów (przykładowa)
CREATE TABLE access_usage_stats (
    user_name VARCHAR(100),
    role_name VARCHAR(100),
    last_access TIMESTAMP,
    access_count INTEGER DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_name, role_name)
);

-- Funkcja automatycznego czyszczenia nieużywanych uprawnień
CREATE OR REPLACE FUNCTION cleanup_stale_permissions(
    p_dry_run BOOLEAN DEFAULT TRUE,
    p_days_threshold INTEGER DEFAULT 365
)
RETURNS TABLE(
    action TEXT,
    user_name TEXT,
    role_name TEXT,
    days_unused INTEGER
) AS $$
DECLARE
    stale_permission RECORD;
    action_taken TEXT;
BEGIN
    FOR stale_permission IN
        SELECT * FROM report_unused_access(p_days_threshold)
        WHERE risk_level = 'HIGH'
    LOOP
        IF p_dry_run THEN
            action_taken := 'DRY_RUN_REVOKE';
        ELSE
            -- Odwołaj uprawnienie
            EXECUTE format('REVOKE %I FROM %I', 
                         stale_permission.role_name, stale_permission.user_name);
            action_taken := 'REVOKED';
            
            -- Log operacji
            INSERT INTO role_audit_log (action, role_name, target_user, performed_by, performed_at)
            VALUES ('AUTO_REVOKE_STALE', stale_permission.role_name, 
                   stale_permission.user_name, 'system', CURRENT_TIMESTAMP);
        END IF;
        
        RETURN QUERY SELECT 
            action_taken,
            stale_permission.user_name,
            stale_permission.role_name,
            stale_permission.days_unused;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## Zarządzanie hasłami i zabezpieczenia

### 1. **Password Policy Implementation**

```sql
-- Funkcja walidacji siły hasła
CREATE OR REPLACE FUNCTION validate_password_strength(password TEXT)
RETURNS TABLE(
    is_valid BOOLEAN,
    errors TEXT[]
) AS $$
DECLARE
    error_list TEXT[] := '{}';
    min_length INTEGER := 12;
    max_length INTEGER := 128;
BEGIN
    -- Sprawdź długość
    IF LENGTH(password) < min_length THEN
        error_list := array_append(error_list, 
            format('Password must be at least %s characters long', min_length));
    END IF;
    
    IF LENGTH(password) > max_length THEN
        error_list := array_append(error_list, 
            format('Password cannot exceed %s characters', max_length));
    END IF;
    
    -- Sprawdź złożoność
    IF password !~ '[A-Z]' THEN
        error_list := array_append(error_list, 'Password must contain uppercase letters');
    END IF;
    
    IF password !~ '[a-z]' THEN
        error_list := array_append(error_list, 'Password must contain lowercase letters');  
    END IF;
    
    IF password !~ '[0-9]' THEN
        error_list := array_append(error_list, 'Password must contain numbers');
    END IF;
    
    IF password !~ '[^A-Za-z0-9]' THEN
        error_list := array_append(error_list, 'Password must contain special characters');
    END IF;
    
    -- Sprawdź czy nie zawiera słów słownikowych
    IF password ~* '(password|admin|user|login|system|database|postgres)' THEN
        error_list := array_append(error_list, 'Password cannot contain common words');
    END IF;
    
    -- Sprawdź sekwencje
    IF password ~ '(123|abc|qwerty|password)' THEN
        error_list := array_append(error_list, 'Password cannot contain common sequences');
    END IF;
    
    RETURN QUERY SELECT 
        (array_length(error_list, 1) IS NULL), 
        error_list;
END;
$$ LANGUAGE plpgsql;

-- Tabela historii haseł
CREATE TABLE password_history (
    user_name VARCHAR(100),
    password_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_name, created_at)
);

-- Funkcja zmiany hasła z walidacją
CREATE OR REPLACE FUNCTION change_user_password(
    p_user_name TEXT,
    p_new_password TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    validation_result RECORD;
    password_hash TEXT;
    history_count INTEGER;
BEGIN
    -- Sprawdź czy użytkownik istnieje
    IF NOT EXISTS(SELECT 1 FROM pg_roles WHERE rolname = p_user_name) THEN
        RAISE EXCEPTION 'User % does not exist', p_user_name;
    END IF;
    
    -- Waliduj siłę hasła
    SELECT * INTO validation_result FROM validate_password_strength(p_new_password);
    
    IF NOT validation_result.is_valid THEN
        RAISE EXCEPTION 'Password validation failed: %', 
                       array_to_string(validation_result.errors, '; ');
    END IF;
    
    -- Sprawdź historię haseł (ostatnie 5)
    password_hash := md5(p_new_password || p_user_name); -- Uproszczony hash
    
    SELECT COUNT(*) INTO history_count
    FROM password_history
    WHERE user_name = p_user_name
      AND password_hash = password_hash
      AND created_at > CURRENT_TIMESTAMP - INTERVAL '1 year';
    
    IF history_count > 0 THEN
        RAISE EXCEPTION 'Cannot reuse recent passwords';
    END IF;
    
    -- Zmień hasło
    EXECUTE format('ALTER ROLE %I PASSWORD %L', p_user_name, p_new_password);
    
    -- Zapisz w historii
    INSERT INTO password_history (user_name, password_hash)
    VALUES (p_user_name, password_hash);
    
    -- Wyczyść starą historię (zostaw ostatnie 5)
    DELETE FROM password_history
    WHERE user_name = p_user_name
      AND created_at NOT IN (
          SELECT created_at
          FROM password_history
          WHERE user_name = p_user_name
          ORDER BY created_at DESC
          LIMIT 5
      );
    
    -- Log operacji
    INSERT INTO role_audit_log (action, target_user, performed_by, performed_at)
    VALUES ('PASSWORD_CHANGE', p_user_name, current_user, CURRENT_TIMESTAMP);
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Funkcja wymuszania zmiany hasła
CREATE OR REPLACE FUNCTION force_password_expiry()
RETURNS INTEGER AS $$
DECLARE
    user_record RECORD;
    expired_count INTEGER := 0;
BEGIN
    -- Znajdź użytkowników z wygasłymi hasłami (90 dni)
    FOR user_record IN
        SELECT DISTINCT ph.user_name
        FROM password_history ph
        WHERE ph.created_at = (
            SELECT MAX(created_at)
            FROM password_history ph2
            WHERE ph2.user_name = ph.user_name
        )
        AND ph.created_at < CURRENT_TIMESTAMP - INTERVAL '90 days'
    LOOP
        -- Ustaw wygaśnięcie hasła na wczoraj
        EXECUTE format('ALTER ROLE %I VALID UNTIL %L', 
                      user_record.user_name, 
                      (CURRENT_DATE - 1)::TEXT);
        
        expired_count := expired_count + 1;
        
        -- Log operacji
        INSERT INTO role_audit_log (action, target_user, performed_by, performed_at)
        VALUES ('FORCE_PASSWORD_EXPIRY', user_record.user_name, 'system', CURRENT_TIMESTAMP);
    END LOOP;
    
    RETURN expired_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 2. **Account Lockout and Security**

```sql
-- Tabela prób logowania
CREATE TABLE login_attempts (
    attempt_id SERIAL PRIMARY KEY,
    user_name VARCHAR(100),
    client_ip INET,
    success BOOLEAN,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT
);

-- Tabela zablokowanych kont
CREATE TABLE locked_accounts (
    user_name VARCHAR(100) PRIMARY KEY,
    locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    locked_by VARCHAR(100),
    unlock_at TIMESTAMP,
    reason TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- Funkcja logowania prób logowania (wywoływana przez trigger lub external system)
CREATE OR REPLACE FUNCTION log_login_attempt(
    p_user_name TEXT,
    p_client_ip INET,
    p_success BOOLEAN,
    p_error_message TEXT DEFAULT NULL
)
RETURNS VOID AS $$
DECLARE
    failed_attempts INTEGER;
    lockout_threshold INTEGER := 5;
    lockout_duration INTERVAL := '30 minutes';
BEGIN
    -- Zapisz próbę logowania
    INSERT INTO login_attempts (user_name, client_ip, success, error_message)
    VALUES (p_user_name, p_client_ip, p_success, p_error_message);
    
    -- Jeśli próba nieudana, sprawdź czy trzeba zablokować konto
    IF NOT p_success THEN
        -- Policz nieudane próby w ostatnich 15 minutach
        SELECT COUNT(*) INTO failed_attempts
        FROM login_attempts
        WHERE user_name = p_user_name
          AND success = FALSE
          AND attempted_at > CURRENT_TIMESTAMP - INTERVAL '15 minutes';
        
        -- Zablokuj konto jeśli przekroczono próg
        IF failed_attempts >= lockout_threshold THEN
            INSERT INTO locked_accounts (user_name, locked_by, unlock_at, reason)
            VALUES (
                p_user_name,
                'system',
                CURRENT_TIMESTAMP + lockout_duration,
                format('Account locked after %s failed login attempts', failed_attempts)
            )
            ON CONFLICT (user_name) DO UPDATE SET
                locked_at = CURRENT_TIMESTAMP,
                unlock_at = CURRENT_TIMESTAMP + lockout_duration,
                is_active = TRUE;
            
            -- Wymusz wygaśnięcie sesji
            EXECUTE format('ALTER ROLE %I VALID UNTIL %L', 
                          p_user_name, CURRENT_TIMESTAMP::TEXT);
            
            -- Log blokady
            INSERT INTO role_audit_log (action, target_user, performed_by, performed_at)
            VALUES ('ACCOUNT_LOCKED', p_user_name, 'system', CURRENT_TIMESTAMP);
            
            -- Notify administrators
            PERFORM pg_notify('security_alert', 
                           format('Account %s locked due to failed login attempts from %s', 
                                 p_user_name, p_client_ip));
        END IF;
    ELSE
        -- Udane logowanie - wyczyść licznik niepowodzeń
        DELETE FROM login_attempts
        WHERE user_name = p_user_name
          AND success = FALSE
          AND attempted_at > CURRENT_TIMESTAMP - INTERVAL '15 minutes';
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Funkcja automatycznego odblokowywania kont
CREATE OR REPLACE FUNCTION unlock_expired_accounts()
RETURNS INTEGER AS $$
DECLARE
    unlocked_count INTEGER := 0;
    locked_account RECORD;
BEGIN
    FOR locked_account IN
        SELECT user_name
        FROM locked_accounts
        WHERE is_active = TRUE
          AND unlock_at <= CURRENT_TIMESTAMP
    LOOP
        -- Przywróć ważność konta
        EXECUTE format('ALTER ROLE %I VALID UNTIL NULL', locked_account.user_name);
        
        -- Oznacz jako odblokowane
        UPDATE locked_accounts
        SET is_active = FALSE
        WHERE user_name = locked_account.user_name;
        
        unlocked_count := unlocked_count + 1;
        
        -- Log operacji
        INSERT INTO role_audit_log (action, target_user, performed_by, performed_at)
        VALUES ('ACCOUNT_UNLOCKED', locked_account.user_name, 'system', CURRENT_TIMESTAMP);
    END LOOP;
    
    RETURN unlocked_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Funkcja manualnego odblokowywania konta
CREATE OR REPLACE FUNCTION unlock_account(p_user_name TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Sprawdź czy konto jest zablokowane
    IF NOT EXISTS(
        SELECT 1 FROM locked_accounts 
        WHERE user_name = p_user_name AND is_active = TRUE
    ) THEN
        RAISE NOTICE 'Account % is not locked', p_user_name;
        RETURN FALSE;
    END IF;
    
    -- Odblokuj konto
    EXECUTE format('ALTER ROLE %I VALID UNTIL NULL', p_user_name);
    
    -- Oznacz jako odblokowane
    UPDATE locked_accounts
    SET is_active = FALSE
    WHERE user_name = p_user_name;
    
    -- Wyczyść nieudane próby logowania
    DELETE FROM login_attempts
    WHERE user_name = p_user_name
      AND success = FALSE;
    
    -- Log operacji
    INSERT INTO role_audit_log (action, target_user, performed_by, performed_at)
    VALUES ('MANUAL_UNLOCK', p_user_name, current_user, CURRENT_TIMESTAMP);
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## Monitoring i raportowanie

### 1. **User Activity Monitoring**

```sql
-- Widok aktywności użytkowników
CREATE VIEW user_activity_summary AS
SELECT 
    usename as username,
    client_addr,
    state,
    application_name,
    backend_start,
    state_change,
    query_start,
    CASE 
        WHEN state = 'active' THEN 
            EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - query_start))
        ELSE NULL
    END as query_duration_seconds,
    LEFT(query, 100) as current_query_preview
FROM pg_stat_activity
WHERE usename IS NOT NULL
ORDER BY backend_start DESC;

-- Funkcja raportowania aktywności
CREATE OR REPLACE FUNCTION generate_user_activity_report(
    p_start_date DATE DEFAULT CURRENT_DATE - 7,
    p_end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE(
    username TEXT,
    total_connections INTEGER,
    total_queries INTEGER,
    avg_connection_duration INTERVAL,
    last_activity TIMESTAMP,
    most_used_application TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH connection_stats AS (
        SELECT 
            la.user_name,
            COUNT(*) as connection_count,
            COUNT(CASE WHEN la.success THEN 1 END) as successful_connections,
            AVG(EXTRACT(EPOCH FROM (
                LEAD(la.attempted_at) OVER (
                    PARTITION BY la.user_name 
                    ORDER BY la.attempted_at
                ) - la.attempted_at
            ))) as avg_session_duration,
            MAX(la.attempted_at) as last_login
        FROM login_attempts la
        WHERE la.attempted_at::DATE BETWEEN p_start_date AND p_end_date
        GROUP BY la.user_name
    ),
    application_stats AS (
        SELECT 
            user_name,
            application_name,
            COUNT(*) as usage_count,
            ROW_NUMBER() OVER (PARTITION BY user_name ORDER BY COUNT(*) DESC) as app_rank
        FROM access_usage_stats aus  -- Hypothetical table
        WHERE updated_at::DATE BETWEEN p_start_date AND p_end_date
        GROUP BY user_name, application_name
    )
    SELECT 
        cs.user_name::TEXT,
        cs.connection_count::INTEGER,
        cs.successful_connections::INTEGER,
        (cs.avg_session_duration || ' seconds')::INTERVAL,
        cs.last_login,
        COALESCE(apps.application_name, 'Unknown')::TEXT
    FROM connection_stats cs
    LEFT JOIN application_stats apps ON cs.user_name = apps.user_name 
                                      AND apps.app_rank = 1
    ORDER BY cs.last_login DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Funkcja alertów bezpieczeństwa
CREATE OR REPLACE FUNCTION check_security_alerts()
RETURNS TABLE(
    alert_type TEXT,
    severity TEXT,
    description TEXT,
    affected_user TEXT,
    occurred_at TIMESTAMP
) AS $$
BEGIN
    -- Alert 1: Podejrzane logowania z wielu IP
    RETURN QUERY
    SELECT 
        'MULTIPLE_IP_LOGIN'::TEXT,
        'HIGH'::TEXT,
        format('User logged in from %s different IP addresses', ip_count)::TEXT,
        user_name::TEXT,
        MAX(attempted_at)
    FROM (
        SELECT 
            user_name,
            COUNT(DISTINCT client_ip) as ip_count,
            MAX(attempted_at) as attempted_at
        FROM login_attempts
        WHERE attempted_at > CURRENT_TIMESTAMP - INTERVAL '1 hour'
          AND success = TRUE
        GROUP BY user_name
        HAVING COUNT(DISTINCT client_ip) >= 3
    ) multi_ip
    GROUP BY user_name, ip_count;
    
    -- Alert 2: Logowania po godzinach
    RETURN QUERY
    SELECT 
        'OFF_HOURS_LOGIN'::TEXT,
        'MEDIUM'::TEXT,
        'Login attempt outside business hours'::TEXT,
        user_name::TEXT,
        attempted_at
    FROM login_attempts
    WHERE attempted_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
      AND success = TRUE
      AND (
          EXTRACT(HOUR FROM attempted_at) < 7 
          OR EXTRACT(HOUR FROM attempted_at) > 19
          OR EXTRACT(DOW FROM attempted_at) IN (0, 6) -- Weekend
      );
    
    -- Alert 3: Długo nieużywane konta z aktywnością
    RETURN QUERY
    SELECT 
        'DORMANT_ACCOUNT_ACTIVE'::TEXT,
        'HIGH'::TEXT,
        'Previously dormant account showed activity'::TEXT,
        la.user_name::TEXT,
        la.attempted_at
    FROM login_attempts la
    WHERE la.attempted_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
      AND la.success = TRUE
      AND NOT EXISTS (
          SELECT 1 FROM login_attempts la2
          WHERE la2.user_name = la.user_name
            AND la2.success = TRUE
            AND la2.attempted_at BETWEEN 
                CURRENT_TIMESTAMP - INTERVAL '90 days' 
                AND CURRENT_TIMESTAMP - INTERVAL '24 hours'
      );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## Najlepsze praktyki

### ✅ **Dobre praktyki:**

#### 1. **Principle of Least Privilege**
```sql
-- Minimalne wymagane uprawnienia
GRANT CONNECT ON DATABASE app_db TO app_user;
GRANT USAGE ON SCHEMA app_schema TO app_user;
GRANT SELECT, INSERT, UPDATE ON app_tables TO app_user;
-- Nie: GRANT ALL ON DATABASE
```

#### 2. **Role-based approach**
```sql
-- Grupy funkcjonalne, nie indywidualne uprawnienia
CREATE ROLE developers;
CREATE ROLE analysts;
CREATE ROLE managers;

GRANT developers TO john_doe, jane_smith;
```

#### 3. **Regular reviews**
```sql
-- Automatyczne przeglądy dostępów
SELECT * FROM report_unused_access(90);
SELECT * FROM check_security_alerts();
```

### ❌ **Złe praktyki:**

```sql
-- ❌ Nadmierne uprawnienia
GRANT ALL PRIVILEGES ON ALL TABLES TO app_user;

-- ❌ Dzielenie kont
-- Wszyscy używają jednego konta 'app_user'

-- ❌ Hasła w kodzie
CREATE USER test WITH PASSWORD 'password123';

-- ❌ Brak rotacji uprawnień
-- Użytkownicy zachowują uprawnienia na zawsze

-- ❌ Ignorowanie auditów
-- Brak monitorowania kto ma jakie uprawnienia
```

## Pułapki egzaminacyjne

### 1. **Role vs User**
```
PostgreSQL: USER = ROLE WITH LOGIN
Wszystko to role, różnica tylko w opcji LOGIN
Dziedziczenie przez INHERIT/NOINHERIT
```

### 2. **Uprawnienia**
```
GRANT/REVOKE operują na rolach
DEFAULT PRIVILEGES dla nowych obiektów
Column-level permissions możliwe
Row Level Security (RLS) dla zaawansowanej kontroli
```

### 3. **Bezpieczeństwo**
```
pg_hba.conf kontroluje authentication
SECURITY DEFINER vs SECURITY INVOKER
Connection limits na poziomie roli
Password policies przez custom functions
```

### 4. **Audyt**
```
pg_stat_activity dla aktywnych sesji
Custom audit tables dla historii
pg_roles dla informacji o rolach
Monitoring failed login attempts
```