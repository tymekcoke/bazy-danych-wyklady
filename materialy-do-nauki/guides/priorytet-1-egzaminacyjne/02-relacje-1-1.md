# Relacje jednoznaczne (1:1)

## Definicja
Relacja 1:1 (jeden do jednego) oznacza, że **jeden rekord w tabeli A jest powiązany z dokładnie jednym rekordem w tabeli B**, i odwrotnie.

## Charakterystyka
- Każdy rekord ma maksymalnie jedno powiązanie
- Relacja jest **dwukierunkowa i symetryczna**
- Rzadko spotykana w praktyce (często można połączyć tabele)

## Implementacja w SQL

### Metoda 1: Klucz obcy z ograniczeniem UNIQUE
```sql
-- Tabela główna
CREATE TABLE osoby (
    id_osoby INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50)
);

-- Tabela powiązana
CREATE TABLE paszporty (
    id_paszportu INT PRIMARY KEY,
    numer_paszportu VARCHAR(20) UNIQUE,
    data_waznosci DATE,
    id_osoby INT UNIQUE,  -- UNIQUE zapewnia relację 1:1
    FOREIGN KEY (id_osoby) REFERENCES osoby(id_osoby)
);
```

### Metoda 2: Wspólny klucz główny
```sql
-- Tabela główna
CREATE TABLE osoby (
    id_osoby INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50)
);

-- Tabela powiązana używa tego samego klucza
CREATE TABLE szczegoly_osoby (
    id_osoby INT PRIMARY KEY,  -- Ten sam klucz co w tabeli głównej
    adres VARCHAR(200),
    telefon VARCHAR(15),
    FOREIGN KEY (id_osoby) REFERENCES osoby(id_osoby)
);
```

### Metoda 3: Tabela łącząca (rzadko używana dla 1:1)
```sql
CREATE TABLE osoba_paszport (
    id_osoby INT UNIQUE,  -- UNIQUE zapewnia 1:1
    id_paszportu INT UNIQUE,  -- UNIQUE zapewnia 1:1
    PRIMARY KEY (id_osoby, id_paszportu),
    FOREIGN KEY (id_osoby) REFERENCES osoby(id_osoby),
    FOREIGN KEY (id_paszportu) REFERENCES paszporty(id_paszportu)
);
```

## Przykłady z życia
1. **Osoba ↔ Paszport** - jedna osoba ma jeden paszport
2. **Pracownik ↔ Stanowisko kierownicze** - jedno stanowisko, jeden kierownik
3. **Kraj ↔ Stolica** - jeden kraj ma jedną stolicę
4. **Użytkownik ↔ Profil** - jeden użytkownik, jeden profil

## Zapytania SQL dla relacji 1:1

### INNER JOIN - tylko rekordy z powiązaniami
```sql
-- Pokaż osoby które mają paszporty
SELECT o.imie, o.nazwisko, p.numer_paszportu
FROM osoby o
INNER JOIN paszporty p ON o.id_osoby = p.id_osoby;
```

### LEFT JOIN - wszystkie osoby, nawet bez paszportu
```sql
-- Pokaż wszystkie osoby (z paszportem lub bez)
SELECT o.imie, o.nazwisko, p.numer_paszportu
FROM osoby o
LEFT JOIN paszporty p ON o.id_osoby = p.id_osoby;
```

### RIGHT JOIN - wszystkie paszporty, nawet bez osoby
```sql
-- Pokaż wszystkie paszporty (z osobą lub bez)
SELECT o.imie, o.nazwisko, p.numer_paszportu
FROM osoby o
RIGHT JOIN paszporty p ON o.id_osoby = p.id_osoby;
```

## Zalety relacji 1:1
1. **Normalizacja** - podział dużych tabel na mniejsze części
2. **Bezpieczeństwo** - oddzielenie danych wrażliwych
3. **Wydajność** - ładowanie tylko potrzebnych danych
4. **Organizacja** - logiczne grupowanie powiązanych danych

## Wady relacji 1:1
1. **Złożoność** - więcej tabel do zarządzania
2. **Wydajność JOIN** - konieczność łączenia tabel
3. **Redundancja kluczy** - dodatkowe klucze obce
4. **Pytanie o sens** - często można połączyć tabele w jedną

## Kiedy używać relacji 1:1?
1. **Duże tabele** - podział na podstawowe i szczegółowe dane
2. **Bezpieczeństwo** - oddzielenie wrażliwych informacji
3. **Opcjonalne dane** - gdy część danych może być pusta
4. **Różne częstotliwości dostępu** - często vs rzadko używane dane

## Integralność w relacjach 1:1
```sql
-- Opcje przy usuwaniu/aktualizacji
CREATE TABLE paszporty (
    id_paszportu INT PRIMARY KEY,
    numer_paszportu VARCHAR(20),
    id_osoby INT UNIQUE,
    FOREIGN KEY (id_osoby) REFERENCES osoby(id_osoby)
        ON DELETE CASCADE     -- Usuń paszport gdy usuniesz osobę
        ON UPDATE CASCADE     -- Zaktualizuj klucz obcy przy zmianie
);
```

## Sprawdzanie relacji 1:1
```sql
-- Sprawdź czy relacja jest rzeczywiście 1:1
SELECT 
    COUNT(*) as total_rows,
    COUNT(DISTINCT id_osoby) as unique_persons,
    COUNT(DISTINCT id_paszportu) as unique_passports
FROM paszporty;

-- Jeśli wszystkie 3 liczby są równe - relacja jest 1:1
```

## Błędy w relacjach 1:1
1. **Brak ograniczenia UNIQUE** - pozwala na relację 1:N
2. **Nieprawidłowe klucze obce** - łamanie integralności referencyjnej  
3. **Duplicate key errors** - próba wstawienia drugiego powiązania