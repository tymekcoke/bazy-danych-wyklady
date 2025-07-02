# Integralność bazy danych

## Co to jest integralność?
Integralność bazy danych to zestaw zasad i ograniczeń mających na celu zapewnienie **dokładności, spójności i wiarygodności** danych w bazie danych.

## Rodzaje integralności

### 1. Integralność encji (Entity Integrity)
- **Definicja**: Każdy rekord w tabeli musi być jednoznacznie identyfikowalny
- **Zasady**:
  - Klucz główny nie może być NULL
  - Klucz główny musi być unikalny
  - Klucz główny jest niezmienialny
- **Przykład**: 
  ```sql
  CREATE TABLE studenci (
    id_studenta INT PRIMARY KEY,  -- nie może być NULL
    imie VARCHAR(50) NOT NULL
  );
  ```

### 2. Integralność referencyjna (Referential Integrity)
- **Definicja**: Relacje między tabelami muszą być spójne
- **Zasady**:
  - Klucz obcy musi odwoływać się do istniejącego klucza głównego
  - Klucz obcy może być NULL (jeśli nie ma ograniczenia NOT NULL)
- **Opcje przy usuwaniu/aktualizacji**:
  - `CASCADE` - automatyczne usuwanie/aktualizacja powiązanych rekordów
  - `RESTRICT` - blokowanie operacji jeśli istnieją powiązania
  - `SET NULL` - ustawienie klucza obcego na NULL
  - `SET DEFAULT` - ustawienie klucza obcego na wartość domyślną

```sql
CREATE TABLE oceny (
    id_oceny INT PRIMARY KEY,
    id_studenta INT,
    ocena INT,
    FOREIGN KEY (id_studenta) REFERENCES studenci(id_studenta)
        ON DELETE CASCADE  -- usuwanie ocen przy usunięciu studenta
        ON UPDATE CASCADE  -- aktualizacja przy zmianie ID studenta
);
```

### 3. Integralność domeny (Domain Integrity)
- **Definicja**: Wartości w kolumnach muszą być z dozwolonego zakresu
- **Mechanizmy**:
  - Typy danych (INT, VARCHAR, DATE)
  - Ograniczenia CHECK
  - Wartości domyślne (DEFAULT)
  - Ograniczenia NOT NULL

```sql
CREATE TABLE studenci (
    id_studenta INT PRIMARY KEY,
    wiek INT CHECK (wiek >= 18 AND wiek <= 65),
    email VARCHAR(100) UNIQUE NOT NULL,
    srednia DECIMAL(3,2) CHECK (srednia >= 2.0 AND srednia <= 5.0)
);
```

### 4. Integralność operacyjna (Business Rules)
- **Definicja**: Reguły biznesowe specyficzne dla aplikacji
- **Implementacja**:
  - Wyzwalacze (triggers)
  - Procedury składowane
  - Ograniczenia CHECK z funkcjami
- **Przykład**: Student nie może mieć więcej niż 30 ECTS w semestrze

### 5. Integralność wartości NULL
- **Zasady**:
  - NULL ≠ NULL (porównanie zawsze zwraca UNKNOWN)
  - NULL w funkcjach agregujących jest ignorowane
  - NULL w wyrażeniach arytmetycznych daje NULL
- **Operatory**:
  - `IS NULL` / `IS NOT NULL`
  - `COALESCE(val1, val2, ...)` - zwraca pierwszą nie-NULL wartość

### 6. Integralność unikalności
- **UNIQUE**: Kolumny muszą mieć unikalne wartości (ale mogą być NULL)
- **PRIMARY KEY**: Unikalność + NOT NULL
- **Indeksy unikalne**: Automatyczne tworzenie przy UNIQUE/PRIMARY KEY

### 7. Integralność wyzwalaczy
- **Wyzwalacze**: Automatyczne procedury uruchamiane przy zdarzeniach
- **Rodzaje**:
  - `BEFORE INSERT/UPDATE/DELETE`
  - `AFTER INSERT/UPDATE/DELETE`
- **Zastosowania**:
  - Walidacja danych
  - Automatyczne obliczenia
  - Logowanie zmian

### 8. Integralność warunków
- **Ograniczenia CHECK**: Warunki logiczne na poziomie tabeli
- **Przykłady**:
  ```sql
  -- Warunek na poziomie kolumny
  ALTER TABLE zamowienia ADD CONSTRAINT chk_kwota 
  CHECK (kwota > 0);
  
  -- Warunek na poziomie tabeli
  ALTER TABLE pracownicy ADD CONSTRAINT chk_daty
  CHECK (data_zatrudnienia <= data_zwolnienia);
  ```

## Korzyści z integralności
1. **Dokładność danych** - dane są poprawne i kompletne
2. **Spójność** - dane są jednolite w całej bazie
3. **Wiarygodność** - można zaufać danym w bazie
4. **Redukcja błędów** - automatyczne wykrywanie nieprawidłowości
5. **Łatwość utrzymania** - mniej ręcznej kontroli danych

## Najczęstsze problemy
1. **Naruszenie integralności referencyjnej** - próba usunięcia rekordu z kluczem głównym przy istniejących kluczach obcych
2. **Duplikaty** - próba wstawienia duplikatu klucza głównego
3. **Nieprawidłowe wartości** - wartości spoza dozwolonego zakresu
4. **Brakujące wartości** - NULL w kolumnach NOT NULL