# 👥 RELACJE JEDEN-DO-JEDNEGO - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Relacja jeden-do-jednego oznacza, że jeden rekord z tabeli A odpowiada dokładnie jednemu rekordowi z tabeli B i na odwrót. W praktyce implementuje się ją na trzy sposoby:

1. **Jedna tabela** - łączenie wszystkich atrybutów (najczęściej stosowane)
2. **Dwie tabele z kluczem obcym** - gdy mamy różne częstotliwości dostępu
3. **Tabela łącząca** - gdy obie encje są niezależne

Klucz obcy w relacji 1:1 musi być jednocześnie UNIQUE, żeby zagwarantować unikalność powiązania."

## ✍️ CO NAPISAĆ NA KARTCE

```sql
-- SPOSÓB 1: JEDNA TABELA (najczęściej używany)
CREATE TABLE pracownicy (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    -- dane paszportu w tej samej tabeli
    numer_paszportu VARCHAR(20) UNIQUE,
    data_waznosci DATE,
    kraj_wydania VARCHAR(30)
);

-- SPOSÓB 2: DWIE TABELE Z KLUCZEM OBCYM
CREATE TABLE pracownicy (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50)
);

CREATE TABLE paszporty (
    id_paszportu INT PRIMARY KEY,
    numer_paszportu VARCHAR(20) UNIQUE,
    data_waznosci DATE,
    kraj_wydania VARCHAR(30),
    id_pracownika INT UNIQUE,  -- UNIQUE zapewnia 1:1 !
    FOREIGN KEY (id_pracownika) REFERENCES pracownicy(id_pracownika)
);

-- SPOSÓB 3: TABELA ŁĄCZĄCA (rzadko używany dla 1:1)
CREATE TABLE pracownik_paszport (
    id_pracownika INT UNIQUE,
    id_paszportu INT UNIQUE,
    PRIMARY KEY (id_pracownika, id_paszportu),
    FOREIGN KEY (id_pracownika) REFERENCES pracownicy(id_pracownika),
    FOREIGN KEY (id_paszportu) REFERENCES paszporty(id_paszportu)
);
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- Praktyczny przykład: Użytkownik i Profil
CREATE TABLE uzytkownicy (
    id_uzytkownika INT PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    haslo_hash VARCHAR(255) NOT NULL,
    data_rejestracji TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE profile_uzytkownikow (
    id_profilu INT PRIMARY KEY,
    imie VARCHAR(50),
    nazwisko VARCHAR(50),
    data_urodzenia DATE,
    telefon VARCHAR(20),
    adres TEXT,
    avatar_url VARCHAR(255),
    -- Klucz obcy z ograniczeniem UNIQUE dla relacji 1:1
    id_uzytkownika INT UNIQUE NOT NULL,
    FOREIGN KEY (id_uzytkownika) REFERENCES uzytkownicy(id_uzytkownika)
        ON DELETE CASCADE  -- usunięcie użytkownika = usunięcie profilu
        ON UPDATE CASCADE
);

-- Zapytanie łączące (JOIN) dla relacji 1:1
SELECT u.login, u.email, p.imie, p.nazwisko, p.telefon
FROM uzytkownicy u
LEFT JOIN profile_uzytkownikow p ON u.id_uzytkownika = p.id_uzytkownika
WHERE u.id_uzytkownika = 1;
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **KLUCZOWE**: Klucz obcy w relacji 1:1 MUSI być UNIQUE
2. **NIE mylić** z relacją 1:N - w 1:1 obie strony mają max 1 powiązanie  
3. **PAMIĘTAĆ**: LEFT JOIN przy zapytaniach (profil może nie istnieć)
4. **UWAGA**: CASCADE przy usuwaniu - czy chcemy usunąć powiązane dane?
5. **CZĘSTY BŁĄD**: Zapominanie o ograniczeniu UNIQUE na kluczu obcym

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **One-to-one relationship** - relacja jeden-do-jednego
- **UNIQUE constraint** - ograniczenie unikalności
- **Foreign key** - klucz obcy
- **CASCADE** - kaskadowe usuwanie/aktualizacja
- **LEFT JOIN** - zewnętrzne złączenie lewe
- **Normalizacja** - podział na tabele
- **Entity integrity** - integralność encji
- **Referential integrity** - integralność referencyjna

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **01-integralnosc** - integralność referencyjna
- **12-klucze-bazy-danych** - klucze obce i główne
- **21-sql-joiny** - LEFT JOIN dla relacji 1:1
- **25-model-er** - notacja 1:1 w diagramach ER
- **14-er-do-sql** - implementacja relacji z diagramu