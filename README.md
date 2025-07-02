# 📚 Bazy Danych - Materiały do Nauki

## 🎯 Opis

Kompletny zestaw materiałów do nauki baz danych przygotowany na egzamin. Zawiera wszystko od podstaw po zaawansowane tematy - PDF'y z wykładów, guides, cheatsheets, fiszki Anki i materiały egzaminacyjne.

## 📁 Struktura Repozytorium

### 📖 Wykłady (PDF'y)
```
01-Wprowadzenie/     - Podstawy baz danych
02-Modelowanie/      - Model ER, normalizacja
03-SQL/              - Składnia SQL, DDL, DML
04-Zaawansowane/     - Transakcje, indeksy, triggery
05-Administracja/    - Backup, bezpieczeństwo
06-Podsumowanie/     - Przegląd całości
```

### 🎓 Materiały do Nauki
```
materialy-do-nauki/
├── guides/              - 42 szczegółowe przewodniki
├── cheatsheets/         - 35 cheatsheets egzaminacyjnych
├── exam-prep/           - Materiały na ostatnie dni przed egzaminem
├── anki/               - Fiszki do nauki (100+ kart)
└── sql-examples/       - Przykłady SQL
```

## 🔥 Najważniejsze Materiały

### ⏰ **Dzień przed egzaminem:**
- [`exam-prep/LAST-20-MINUTES.md`](materialy-do-nauki/exam-prep/LAST-20-MINUTES.md) - Ostatnie 20 minut
- [`exam-prep/DEFINITIONS-ONLY.md`](materialy-do-nauki/exam-prep/DEFINITIONS-ONLY.md) - Same definicje
- [`exam-prep/COMMON-MISTAKES.md`](materialy-do-nauki/exam-prep/COMMON-MISTAKES.md) - Najczęstsze błędy

### 📚 **Do systematycznej nauki:**
- [`exam-prep/MASTER-CHEAT.md`](materialy-do-nauki/exam-prep/MASTER-CHEAT.md) - Główna ściągawka
- [`anki/fiszki-bazy-danych.csv`](materialy-do-nauki/anki/fiszki-bazy-danych.csv) - 100+ fiszek Anki
- [`exam-prep/FLASHCARDS.md`](materialy-do-nauki/exam-prep/FLASHCARDS.md) - Karty do powtórek

### 🛠️ **Referencje:**
- [`exam-prep/SQL-CHEATSHEET.md`](materialy-do-nauki/exam-prep/SQL-CHEATSHEET.md) - Składnia SQL
- [`exam-prep/KEYWORDS-GLOSSARY.md`](materialy-do-nauki/exam-prep/KEYWORDS-GLOSSARY.md) - Słowniczek PL/ENG

## 📊 Statystyki

- **📄 PDF'y:** Wszystkie wykłady z kursu
- **📝 Guides:** 42 szczegółowe przewodniki
- **🎯 Cheatsheets:** 35 zwięzłych cheatsheets
- **🃏 Fiszki Anki:** 100+ kart do nauki
- **⚡ Exam Prep:** 9 materiałów na egzamin

## 🚀 Jak Zacząć

### 1. **Szybki Start (2-3 dni przed egzaminem):**
```bash
# Przeczytaj w tej kolejności:
1. exam-prep/MASTER-CHEAT.md
2. exam-prep/DEFINITIONS-ONLY.md  
3. exam-prep/COMMON-MISTAKES.md
4. exam-prep/LAST-20-MINUTES.md
```

### 2. **Systematyczna Nauka (2+ tygodni):**
```bash
# Plan nauki:
1. Importuj fiszki Anki (anki/fiszki-bazy-danych.csv)
2. Przeczytaj guides/ dla zrozumienia teorii
3. Ćwicz z cheatsheets/ dla utrwalenia
4. Na koniec exam-prep/ przed egzaminem
```

### 3. **Import Fiszek do Anki:**
1. Otwórz Anki → File → Import
2. Wybierz `anki/fiszki-bazy-danych.csv`
3. Ustaw separator: Comma, Allow HTML: ✓
4. Zobacz [`anki/README.md`](materialy-do-nauki/anki/README.md) dla szczegółów

## 📋 Tematy Egzaminacyjne

### 🔥 **Priority 1 - Kluczowe na egzamin:**
- Normalizacja (1NF, 2NF, 3NF, BCNF)
- ACID i właściwości transakcji
- Poziomy izolacji i anomalie
- Klucze (PK, FK, unique)
- Relacje (1:1, 1:N, M:N)
- JOIN'y w SQL
- Model ER → implementacja SQL

### ⚡ **Priority 2 - Podstawy:**
- SQL DDL, DML, DQL
- Funkcje agregujące
- Subqueries i NULL handling
- Indeksy i wydajność
- Widoki i triggery

### 🎯 **Priority 3 - Zaawansowane:**
- PL/pgSQL i funkcje użytkownika
- Blokady i MVCC
- Backup i recovery
- Bezpieczeństwo baz danych
- Optymalizacja wydajności

## 🎓 Format Egzaminu

- **3 losowe pytania**
- **Odpowiedź ustna** (30-60 sekund)
- **Odpowiedź pisemna** na kartce
- **Możliwość pisania kodu SQL**
- **Czas:** ~15-20 minut na pytanie

## 💡 Tips na Egzamin

1. **Odpowiedzi ustne:** Definicja → Przykład → Korzyści/Problemy
2. **Na kartce:** Rysuj schematy, oznaczaj PK (*) i FK (→)
3. **SQL:** Sprawdzaj składnię, używaj wcięć
4. **Unikaj:** `= NULL`, mylenia HAVING z WHERE, zapominania o FK

## 🤝 Współpraca

Materiały są otwarte do użytku! Jeśli znajdziesz błędy lub chcesz coś dodać:
1. Otwórz Issue
2. Prześlij Pull Request
3. Udostępnij kolegom 📢

## 📈 Status Materiałów

- ✅ **Ukończone:** 35/42 cheatsheets (83%)
- ✅ **Kompletne:** PDF'y, guides, exam-prep, fiszki Anki
- 🔄 **W trakcie:** Pozostałe 7 cheatsheets (API, bezpieczeństwo, optymalizacja)

## 🙏 Podziękowania

Materiały powstały na podstawie wykładów z kursu Baz Danych. Dzięki za udostępnienie! 🎓

---

**💪 POWODZENIA NA EGZAMINIE!** 🍀

*Pamiętaj: Regularna nauka > cramming w ostatniej chwili*