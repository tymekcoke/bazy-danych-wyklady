# 🔒 INTEGRALNOŚĆ BAZY DANYCH - ODPOWIEDŹ EGZAMINACYJNA

## 📖 CO POWIEDZIEĆ (30-60 sekund)

"Integralność bazy danych to zestaw zasad i ograniczeń zapewniających dokładność, spójność i wiarygodność danych. Składa się z czterech głównych rodzajów:

1. **Integralność encji** - każdy rekord musi być jednoznacznie identyfikowalny przez klucz główny
2. **Integralność referencyjna** - klucze obce muszą odwoływać się do istniejących kluczy głównych  
3. **Integralność domeny** - wartości muszą być z dozwolonego zakresu
4. **Integralność zdefiniowana przez użytkownika** - dodatkowe reguły biznesowe"

## ✍️ CO NAPISAĆ NA KARTCE

```sql
-- INTEGRALNOŚĆ ENCJI
CREATE TABLE studenci (
    id_studenta INT PRIMARY KEY,  -- nie może być NULL + unikalny
    imie VARCHAR(50) NOT NULL
);

-- INTEGRALNOŚĆ REFERENCYJNA  
CREATE TABLE oceny (
    id_oceny INT PRIMARY KEY,
    id_studenta INT,
    ocena INT,
    FOREIGN KEY (id_studenta) REFERENCES studenci(id_studenta)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- INTEGRALNOŚĆ DOMENY
CREATE TABLE produkty (
    id INT PRIMARY KEY,
    cena DECIMAL(10,2) CHECK (cena > 0),  -- ograniczenie CHECK
    kategoria VARCHAR(20) DEFAULT 'inne'  -- wartość domyślna
);

-- INTEGRALNOŚĆ UŻYTKOWNIKA
ALTER TABLE studenci 
ADD CONSTRAINT chk_wiek CHECK (wiek BETWEEN 16 AND 65);
```

## 🔧 PRZYKŁAD KODU (jeśli prosi o implementację)

```sql
-- Kompleksny przykład z wszystkimi rodzajami integralności
CREATE TABLE zamowienia (
    -- Integralność encji
    id_zamowienia INT PRIMARY KEY,
    
    -- Integralność referencyjna
    id_klienta INT NOT NULL,
    FOREIGN KEY (id_klienta) REFERENCES klienci(id_klienta)
        ON DELETE RESTRICT  -- nie można usunąć klienta z zamówieniami
        ON UPDATE CASCADE,  -- aktualizacja ID klienta w zamówieniach
    
    -- Integralność domeny
    data_zamowienia DATE NOT NULL DEFAULT CURRENT_DATE,
    status ENUM('nowe', 'w_realizacji', 'zakonczone') DEFAULT 'nowe',
    kwota DECIMAL(10,2) CHECK (kwota >= 0),
    
    -- Integralność użytkownika  
    CONSTRAINT chk_data_przyszlosc 
        CHECK (data_zamowienia <= CURRENT_DATE + INTERVAL '30 days')
);
```

## ⚠️ PUŁAPKI EGZAMINACYJNE

1. **NIE mylić** integralności encji z integralną referencyjną
2. **PAMIĘTAĆ**: klucz główny = NOT NULL + UNIQUE automatycznie
3. **ROZRÓŻNIAĆ**: CASCADE vs RESTRICT vs SET NULL w kluczach obcych
4. **NIE zapominać**: CHECK constraints to integralność domeny
5. **UWAGA**: integralność referencyjna może być NULL (jeśli nie ma NOT NULL)

## 🎯 SŁOWA KLUCZOWE DO WPLECENIA

- **Primary Key** - klucz główny
- **Foreign Key** - klucz obcy  
- **CHECK constraints** - ograniczenia sprawdzające
- **ON DELETE CASCADE/RESTRICT** - akcje przy usuwaniu
- **NOT NULL** - wymagana wartość
- **UNIQUE** - unikalność
- **Referential integrity** - integralność referencyjna
- **Entity integrity** - integralność encji
- **Domain integrity** - integralność domeny

## 🔗 POWIĄZANIA Z INNYMI TEMATAMI

- **12-klucze-bazy-danych** - klucze główne i obce
- **02-relacje-1-1** - implementacja relacji  
- **14-er-do-sql** - przekształcanie ograniczeń z ER
- **19-normalizacja** - eliminacja anomalii przez integralność