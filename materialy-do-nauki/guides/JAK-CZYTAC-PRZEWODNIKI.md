# Jak czytać przewodniki - porządek nauki baz danych

## 🎯 Dla kogo ten poradnik?

Ten przewodnik jest dla osób, które chcą **systematycznie nauczyć się baz danych od podstaw**, bez presji egzaminowej. Pliki w folderze `guides/` są ponumerowane według priorytetów egzaminacyjnych, ale **logiczny porządek nauki** jest inny.

---

## 📚 ETAP 1: FUNDAMENTY TEORETYCZNE

### Podstawy modeli danych
1. **25-model-er.md** - Model Entity-Relationship (podstawa projektowania)
2. **26-model-relacyjny.md** - Teoria modelu relacyjnego  
3. **14-er-do-sql.md** - Przekształcanie diagramów ER na tabele SQL

### Kluczowe koncepty
4. **12-klucze-bazy-danych.md** - Klucze główne, obce, kandydujące
5. **01-integralnosc.md** - Integralność danych i ograniczenia
6. **02-relacje-1-1.md** - Związki między tabelami

---

## 🔧 ETAP 2: SQL PODSTAWOWY

### Język SQL - składnia i operacje
7. **29-sql-ddl.md** - DDL: CREATE, ALTER, DROP (tworzenie struktury)
8. **21-sql-joiny.md** - JOIN: łączenie tabel
9. **08-natural-join.md** - Natural Join (specjalny przypadek)
10. **24-wartosc-null.md** - Obsługa wartości NULL

### Zapytania zaawansowane
11. **30-sql-dml-zaawansowany.md** - SELECT zaawansowany
12. **31-podzapytania-sql.md** - Subqueries (podzapytania)
13. **32-funkcje-agregujace.md** - GROUP BY, HAVING, funkcje agregujące
14. **22-perspektywy-views.md** - Widoki (Views)
15. **11-widoki-vs-tabele-tymczasowe.md** - Widoki vs tabele tymczasowe

---

## 📐 ETAP 3: TEORIA NORMALIZACJI

### Zależności i normalizacja
16. **27-zaleznosci-funkcyjne.md** - Zależności funkcyjne (FD)
17. **05-twierdzenie-heatha.md** - Twierdzenie Heatha (dekompozycja)
18. **19-normalizacja.md** - 1NF, 2NF, 3NF, BCNF
19. **28-normalizacja-zaawansowana.md** - 4NF, 5NF (zaawansowana)
20. **15-redundancja.md** - Redundancja danych i jej eliminacja
21. **23-algebra-relacji.md** - Algebra relacji (podstawy teoretyczne)

---

## ⚡ ETAP 4: TRANSAKCJE I WSPÓŁBIEŻNOŚĆ

### Transakcje
22. **18-transakcje-acid.md** - Właściwości ACID
23. **07-poziomy-izolacji.md** - Poziomy izolacji transakcji
24. **17-znaczniki-czasu-transakcji.md** - Timestamp ordering

### Współbieżność i kontrola
25. **20-wspolbieznosc.md** - Problemy współbieżności
26. **10-blokady.md** - Mechanizmy blokad
27. **09-zakleszczenia.md** - Deadlock i jego rozwiązywanie
28. **04-przebiegi-transakcji.md** - Przebiegi: odtwarzalne, bezkaskadowe, ścisłe
29. **03-protokol-dwufazowy.md** - 2PL (Two-Phase Locking)

---

## 🖥️ ETAP 5: PROGRAMOWANIE I AUTOMATYZACJA

### Programowanie po stronie serwera
30. **33-plpgsql-podstawy.md** - PL/pgSQL - język proceduralny
31. **34-funkcje-uzytkownika.md** - Tworzenie własnych funkcji
32. **06-triggery.md** - Triggery - automatyczne reakcje
33. **35-rules-vs-triggery.md** - Rules vs Triggery (porównanie)
34. **16-procedury-skladowane.md** - Procedury składowane

---

## 🌐 ETAP 6: INTEGRACJA I API

### Połączenie z aplikacjami
35. **36-api-interfejsy.md** - API i interfejsy programistyczne
36. **37-rest-api-bazy.md** - REST API dla baz danych
37. **38-integracja-aplikacje.md** - Wzorce integracji (DAO, Repository)

---

## 🔒 ETAP 7: BEZPIECZEŃSTWO

### Ochrona danych
38. **13-sql-injection.md** - SQL Injection i ochrona
39. **39-bezpieczenstwo-baz.md** - Kompleksowe bezpieczeństwo
40. **41-administracja-uzytkownikow.md** - Zarządzanie użytkownikami

---

## 🚀 ETAP 8: ADMINISTRACJA I WYDAJNOŚĆ

### Zarządzanie systemem
41. **40-backup-recovery.md** - Backup i odzyskiwanie danych
42. **42-optymalizacja-wydajnosci.md** - Optymalizacja i indeksy

---

## 💡 WSKAZÓWKI DO NAUKI

### Jak podchodzić do każdego etapu:

1. **Czytaj systematycznie** - nie przeskakuj etapów
2. **Praktykuj od razu** - uruchom przykłady SQL w bazie danych
3. **Rób notatki** - wypisuj kluczowe definicje
4. **Łącz tematy** - szukaj powiązań między przewodnikami
5. **Testuj wiedzę** - używaj sekcji "Pułapki egzaminacyjne"

### Szacowany czas nauki:
- **Etap 1-2**: 2-3 tygodnie (podstawy + SQL)
- **Etap 3**: 1-2 tygodnie (normalizacja - wymaga skupienia)
- **Etap 4**: 2-3 tygodnie (transakcje - trudny materiał)
- **Etap 5-6**: 1-2 tygodnie (programowanie)
- **Etap 7-8**: 1 tydzień (bezpieczeństwo + administracja)

**Łącznie**: 7-11 tygodni systematycznej nauki

### Alternatywny porządek dla praktyka:
Jeśli chcesz szybko zacząć pracować z bazami:
1. Etap 1 (model danych)
2. Etap 2 (SQL podstawowy)
3. Etap 5 (programowanie - tylko podstawy)
4. Pozostałe etapy według potrzeb

---

## 🎓 PRZYGOTOWANIE DO EGZAMINU

Gdy opanujesz już materiał systematycznie, do przygotowania egzaminacyjnego używaj **numeracji oryginalnej** (01-42), która priorytetyzuje tematy egzaminacyjne.

**Powodzenia w nauce baz danych!** 📊