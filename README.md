# System analityczny - Rynek Pracy

Interaktywna aplikacja desktopowa służąca do dynamicznego pobierania, zaawansowanego przetwarzania oraz wielokryterialnej wizualizacji danych makroekonomicznych dotyczących rynku pracy. System integruje się bezpośrednio z globalnym repozytorium **World Bank API**.

Projekt został zrealizowany w architekturze modułowej, zapewniającej całkowitą separację warstwy prezentacji danych (GUI) od części analitycznej.

---

## 🚀 Główne Funkcje Systemu

* **Dynamiczne pobieranie danych:** Automatyczne pozyskiwanie szeregów czasowych z internetu przy użyciu oficjalnego pakietu `wbgapi`.
* **Zaawansowane GUI:** Nowoczesny interfejs graficzny w paradygmacie obiektowym z podziałem na ciemny panel sterowania (Dashboard) oraz jasny panel wyników.
* **Wielokryterialne analizy porównawcze:** Możliwość zestawiania ze sobą wskaźników dla jednego kraju lub automatycznego łączenia wewnętrznego (*inner merge*) i analizy dla dwóch państw jednocześnie.
* **Wektorowe obliczenia NumPy:** Niskopoziomowa i szybka realizacja statystyki opisowej (wyliczanie średniej arytmetycznej oraz odchylenia standardowego) bezpośrednio na strukturach *ndarray*.
* **Interaktywna wizualizacja:** Osadzony kontener z wykresami `matplotlib`, pozwalający na dynamiczne przełączanie widoku między wykresem liniowym a słupkowym oraz sterowanie liniami siatki.
* **Eksport danych:** Funkcja zapisu przefiltrowanych i oczyszczonych danych z pamięci podręcznej wprost do pliku formatu `.csv`.

---

## 📊 Zakres Analizy i Przetwarzane Dane

### Filtry i optymalizacja:
* **Zbiór krajów:** Analiza zoptymalizowana dla 10 kluczowych gospodarek europejskich (Austria, Belgia, Czechy, Francja, Niemcy, Włochy, Holandia, Polska, Hiszpania, Szwecja) mapowanych kodami ISO3.
* **Zakres chronologiczny:** Stabilna dekada badań obejmująca lata **2013 – 2023**.

### Monitorowane wskaźniki makroekonomiczne:
1. Stopa bezrobocia ogółem (%)
2. Bezrobocie młodych (15-24 lata) (%)
3. Aktywność zawodowa kobiet (%)
4. Zamożność społeczeństwa (PKB per capita w USD)
5. Pracownicy etatowi (% ogółu pracujących)
6. Udział dochodów z pracy w PKB (%)
7. Wydajność pracy (PKB na osobo-zatrudnionego w USD)

---

## 🛠️ Architektura i Technologie

Projekt został w pełni napisany w języku **Python** przy wykorzystaniu wiodących bibliotek inżynierii danych:
* `tkinter` / `ttk` – warstwa interfejsu użytkownika i nowoczesne widgety systemowe.
* `wbgapi` – asynchroniczne odpytywanie interfejsów API Banku Światowego.
* `pandas` – transformacja surowego strumienia danych do dwuwymiarowych obiektów *DataFrame*, czyszczenie danych (*.dropna*) oraz relacyjne złączenia.
* `numpy` – wektorowe operacje matematyczne i wyliczanie stabilności strukturalnej rynku.
* `matplotlib` – renderowanie i rzutowanie wykresów w czasie rzeczywistym.
* `threading` – obsługa żądań sieciowych w tle, zapobiegająca zamrażaniu wątku głównego GUI.

---

## 💻 Instrukcja Uruchomienia

**1. Klonowanie repozytorium**
```bash
git clone [https://github.com/kkuberacka/System-analizy-rynku-pracy.git]
cd System-analizy-rynku-pracy

## **2. Instalacja wymaganych pakietów**
Przed uruchomieniem aplikacji upewnij się, że posiadasz zainstalowane niezbędne biblioteki. Wszystkie zewnętrzne zależności można zainstalować automatycznie za pomocą managera pakietów pip poprzez wykonanie poniższego polecenia w terminalu:

pip install pandas numpy matplotlib wbgapi

## **3. Uruchomienie programu**
Cała aplikacja wraz z interfejsem użytkownika i integracją API znajduje się w jednym pliku skryptu. Aby zainicjalizować system, uruchom plik główny w swoim środowisku terminalowym:

python main.py

**## 📝 Źródła i Literatura**

* **Dokumentacja techniczna Banku Światowego:** *"Introducing wbgapi: A new python package for accessing World Bank data"*
* **Poradnik implementacji:** *"Python: How to use World Bank API (WBGAPI) and Pandas to import data, and draw charts"*
