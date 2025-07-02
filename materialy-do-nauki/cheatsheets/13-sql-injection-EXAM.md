# 🛡️ SQL INJECTION - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekunds)

"SQL Injection to atak polegający na wstrzykiwaniu złośliwego kodu SQL przez dane wejściowe użytkownika. Następuje gdy aplikacja nieprawidłowo łączy input użytkownika z zapytaniem SQL. Główne typy to:

1. **Union-based** - wykorzystuje UNION do wyciągnięcia dodatkowych danych
2. **Boolean-based** - wykorzystuje odpowiedzi true/false  
3. **Time-based** - wykorzystuje opóźnienia w odpowiedziach
4. **Error-based** - wykorzystuje komunikaty błędów

Ochrona: parametryzowane zapytania, walidacja input, least privilege, escape znaków specjalnych."

## ✍️ CO NAPISAĆ NA KARTCE

```sql
-- PRZYKŁADY ATAKÓW SQL INJECTION

-- 1. BASIC INJECTION - ominięcie logowania
-- Podatne zapytanie (ZŁE!):
"SELECT * FROM users WHERE username = '" + userInput + "' AND password = '" + passInput + "'"

-- Atak:
username: admin'--
password: cokolwiek

-- Rezultat:
SELECT * FROM users WHERE username = 'admin'--' AND password = 'cokolwiek'
-- Komentarz -- ignoruje resztę, loguje jako admin bez hasła!

-- 2. UNION INJECTION - wyciągnięcie haseł
-- Podatne zapytanie:
"SELECT product_name, price FROM products WHERE category = '" + category + "'"

-- Atak:
category: electronics' UNION SELECT username, password FROM users--

-- Rezultat:
SELECT product_name, price FROM products WHERE category = 'electronics' 
UNION SELECT username, password FROM users--'
-- Zwraca produkty + wszystkie hasła użytkowników!

-- 3. BOOLEAN INJECTION - zgadywanie danych
-- Atak:
id: 1' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='admin')='a'--

-- Jeśli true → pierwsza litera hasła to 'a'
-- Jeśli false → pierwsza litera to coś innego

-- 4. TIME-BASED INJECTION
-- Atak:
id: 1'; IF (SELECT COUNT(*) FROM users WHERE username='admin') > 0 WAITFOR DELAY '00:00:05'--

-- Jeśli jest opóźnienie → admin istnieje

-- OCHRONA (DOBRE PRAKTYKI):

-- ✅ PARAMETRYZOWANE ZAPYTANIA
-- Java (PreparedStatement):
PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE username = ? AND password = ?");
ps.setString(1, userInput);
ps.setString(2, passInput);

-- Python (psycopg2):
cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))

-- PHP (PDO):
$stmt = $pdo->prepare("SELECT * FROM users WHERE username = ? AND password = ?");
$stmt->execute([$username, $password]);

-- ✅ STORED PROCEDURES (jeśli dobrze napisane)
CALL LoginUser(@username, @password)

-- ✅ ESCAPE SPECJALNYCH ZNAKÓW
-- PostgreSQL:
SELECT * FROM users WHERE username = $1 AND password = $2

-- ✅ WALIDACJA INPUT
-- Whitelist dozwolonych znaków
-- Długość input
-- Typy danych

-- ✅ LEAST PRIVILEGE
-- Konto aplikacji tylko z potrzebnymi uprawnieniami
-- Brak uprawnień DROP, CREATE, ALTER
-- Oddzielne konta dla różnych funkcji
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- DEMONSTRACJA VULNERABILITY I OCHRONY

-- TABELA TESTOWA
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user'
);

INSERT INTO users VALUES 
(1, 'admin', 'hashedpassword123', 'admin@company.com', 'admin'),
(2, 'user1', 'hashedpass456', 'user1@company.com', 'user'),
(3, 'guest', 'guestpass789', 'guest@company.com', 'guest');

-- PODATNY KOD (ZŁE!) - nigdy tak nie rób
CREATE OR REPLACE FUNCTION vulnerable_login(user_input TEXT, pass_input TEXT)
RETURNS TABLE(username TEXT, email TEXT, role TEXT) AS $$
DECLARE
    query TEXT;
BEGIN
    -- VULNERABILITY: konkatenacja stringów
    query := 'SELECT username, email, role FROM users WHERE username = ''' 
             || user_input || ''' AND password_hash = ''' || pass_input || '''';
    
    RAISE NOTICE 'Executing: %', query;  -- dla demonstracji
    RETURN QUERY EXECUTE query;
END;
$$ LANGUAGE plpgsql;

-- Test ataku:
SELECT * FROM vulnerable_login('admin''--', 'anything');
-- Zwraca dane admina bez sprawdzania hasła!

-- BEZPIECZNY KOD (DOBRE!)
CREATE OR REPLACE FUNCTION secure_login(user_input TEXT, pass_input TEXT)
RETURNS TABLE(username TEXT, email TEXT, role TEXT) AS $$
BEGIN
    -- Parametryzowane zapytanie - SQL injection niemożliwy
    RETURN QUERY 
    SELECT u.username, u.email, u.role 
    FROM users u 
    WHERE u.username = user_input AND u.password_hash = pass_input;
END;
$$ LANGUAGE plpgsql;

-- APLIKACJA LAYER SECURITY (Python przykład)
-- def secure_login(username, password):
--     # 1. Walidacja input
--     if len(username) > 50 or len(password) > 255:
--         return None
--     if not re.match(r'^[a-zA-Z0-9_]+$', username):
--         return None
--     
--     # 2. Parametryzowane zapytanie
--     cursor.execute(
--         "SELECT username, email, role FROM users WHERE username = %s AND password_hash = %s",
--         (username, hashlib.sha256(password.encode()).hexdigest())
--     )
--     return cursor.fetchone()

-- OCHRONA NA POZIOMIE BAZY DANYCH

-- 1. Separate Application User (least privilege)
CREATE ROLE app_user WITH LOGIN PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE company_db TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE ON users TO app_user;
-- NIE dajemy: DROP, CREATE, ALTER, DELETE na systemowych tabelach

-- 2. Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_own_data ON users 
    FOR ALL TO app_user 
    USING (username = current_setting('app.current_user'));

-- 3. Audit i monitoring
CREATE TABLE security_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    username TEXT,
    action TEXT,
    ip_address INET,
    user_agent TEXT,
    suspicious BOOLEAN DEFAULT FALSE
);

-- Function do logowania podejrzanych prób
CREATE OR REPLACE FUNCTION log_login_attempt(
    attempt_user TEXT,
    attempt_ip INET,
    success BOOLEAN,
    suspicious BOOLEAN DEFAULT FALSE
) RETURNS VOID AS $$
BEGIN
    INSERT INTO security_log (username, action, ip_address, suspicious)
    VALUES (attempt_user, 
            CASE WHEN success THEN 'LOGIN_SUCCESS' ELSE 'LOGIN_FAILED' END,
            attempt_ip, 
            suspicious);
            
    -- Alert przy podejrzanej aktywności
    IF suspicious THEN
        RAISE WARNING 'Suspicious login attempt for user: % from IP: %', attempt_user, attempt_ip;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- DETECTION PATTERNS

-- Wykrywanie SQL injection patterns w logach
CREATE OR REPLACE FUNCTION detect_sql_injection(input_text TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Sprawdź podejrzane wzorce
    IF input_text ~* '(\''|"|;|--|\bunion\b|\bselect\b|\bdrop\b|\bdelete\b|\binsert\b|\bupdate\b)' THEN
        RETURN TRUE;
    END IF;
    
    -- Sprawdź długie inputy (możliwy payload)
    IF length(input_text) > 200 THEN
        RETURN TRUE;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Trigger do automatycznego wykrywania
CREATE OR REPLACE FUNCTION audit_user_input()
RETURNS TRIGGER AS $$
BEGIN
    IF detect_sql_injection(NEW.username) OR detect_sql_injection(NEW.email) THEN
        INSERT INTO security_log (action, username, suspicious)
        VALUES ('SUSPICIOUS_INPUT', NEW.username, TRUE);
        
        -- Opcjonalnie: zablokuj operację
        RAISE EXCEPTION 'Suspicious input detected';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_audit_user_input
    BEFORE INSERT OR UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION audit_user_input();
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Konkatenacja stringów = podatność, parametry = bezpieczeństwo
2. **UWAGA**: Stored procedures nie są automatycznie bezpieczne (mogą być podatne)
3. **BŁĄD**: Escape znaków to ostateczność, nie główna ochrona
4. **WAŻNE**: NoSQL bazy też mają injection (MongoDB, etc.)
5. **PUŁAPKA**: Walidacja po stronie klienta (JS) nie chroni - trzeba server-side

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Parameterized queries** - zapytania parametryzowane
- **Prepared statements** - przygotowane instrukcje
- **Input validation** - walidacja danych wejściowych  
- **Escaping** - eskejpowanie znaków specjalnych
- **Least privilege principle** - zasada najmniejszych uprawnień
- **SQL injection patterns** - wzorce ataków
- **Whitelist validation** - walidacja przez białą listę
- **Row Level Security** - bezpieczeństwo na poziomie wierszy

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **39-bezpieczenstwo-baz** - kompleksowe bezpieczeństwo
- **41-administracja-uzytkownikow** - zarządzanie uprawnieniami
- **16-procedury-skladowane** - bezpieczne stored procedures
- **36-api-interfejsy** - bezpieczeństwo API
- **37-rest-api-bazy** - zabezpieczanie REST API