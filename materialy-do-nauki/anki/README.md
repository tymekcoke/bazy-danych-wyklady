# 🃏 ANKI FLASHCARDS - INSTRUKCJA

## 📁 ZAWARTOŚĆ
- **fiszki-bazy-danych.csv** - 100+ fiszek ze wszystkimi tematami baz danych

## 🔄 JAK ZAIMPORTOWAĆ DO ANKI

### Krok 1: Otwórz Anki
- Uruchom aplikację Anki na komputerze

### Krok 2: Import
1. **File → Import** (lub Ctrl+Shift+I)
2. Wybierz plik `fiszki-bazy-danych.csv`
3. Ustaw konfigurację:
   - **Field separator:** Comma
   - **Allow HTML:** ✓ (zaznacz)
   - **First field is:** Front
   - **Second field is:** Back

### Krok 3: Utwórz deck
- Wybierz lub utwórz nowy deck np. "Bazy Danych - Egzamin"
- Kliknij **Import**

## 📚 ZAWARTOŚĆ FISZEK

### 🔥 Tematy główne (100+ kart):
- **Normalizacja** (1NF, 2NF, 3NF, BCNF, 4NF, 5NF)
- **ACID & Transakcje** (poziomy izolacji, anomalie)
- **Blokady & Współbieżność** (deadlock, MVCC, locks)
- **Klucze** (PK, FK, unique, integrity)
- **Relacje** (1:1, 1:N, M:N, kardinalność)
- **SQL** (JOIN'y, agregacje, subqueries)
- **Algebra relacji** (selekcja, projekcja, złączenia)
- **Model ER** (encje, atrybuty, związki)
- **Indeksy** (B-tree, GIN, partial, composite)
- **NULL handling** (logika trójwartościowa)
- **Funkcje & Triggery** (stored procedures, triggers)
- **Widoki** (views, materialized views)
- **Wydajność** (optymalizacja, plany wykonania)
- **Zaawansowane** (partycjonowanie, replikacja, OLTP/OLAP)

## 🎯 STRATEGIA NAUKI

### 📅 Harmonogram:
- **2 tygodnie przed egzaminem:** 20 nowych kart dziennie
- **1 tydzień przed:** tylko powtórki
- **Dzień przed:** express review problematycznych

### ⭐ Ustawienia Anki:
- **New cards/day:** 15-25
- **Maximum reviews/day:** 100
- **Graduating interval:** 3 dni
- **Easy interval:** 4 dni

### 🎨 Tips:
- **Czytaj na głos** - lepsze zapamiętywanie
- **Rysuj schematy** - wizualizuj relacje
- **Łącz z przykładami** - myśl o konkretnych zastosowaniach
- **Używaj mnemonic** - ACID = Anna Codziennie Idzie Do pracy

## 📖 FORMAT KART

Każda karta ma:
- **Przód:** Konkretne pytanie (np. "Co to 3NF?")
- **Tył:** Zwięzła, precyzyjna odpowiedź z kluczowymi słowami

## 🔧 TROUBLESHOOTING

### Problem: Znaki diakrytyczne
**Rozwiązanie:** Przy imporcie wybierz encoding UTF-8

### Problem: Karty się źle importują
**Rozwiązanie:** Sprawdź czy separator to przecinek, nie średnik

### Problem: HTML nie działa
**Rozwiązanie:** Zaznacz "Allow HTML in fields" przy imporcie

## 🎯 STATYSTYKI SUKCESU

**Cel:** 95%+ accuracy na wszystkich kartach
**Czas nauki:** 15-20 min dziennie przez 2 tygodnie
**Wynik:** Pewność siebie na egzaminie! 💪

---

**💡 PAMIĘTAJ:** Regularne powtórki to klucz! Lepiej 15 minut dziennie niż 3 godziny raz w tygodniu.