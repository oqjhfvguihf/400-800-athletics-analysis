# Analiza migracji dystansowych w lekkoatletyce (400m / 400mH / 800m)

Projekt analityczny badający zmiany specjalizacji wśród biegaczy ze światowych list Top 1000 (mężczyźni) w latach **2017–2026** na dystansach **400 m**, **400 m przez płotki (400mH)** oraz **800 m**.

Głównym celem analizy jest identyfikacja faktycznych transferów między konkurencjami (zarówno wydłużeń z 400m/400mH na 800m, jak i skróceń z 800m na 400m) oraz ocena ich skuteczności sportowej.

## Struktura projektu i przepływ danych

Pipeline składa się z 7 skryptów uruchamianych kolejno:

1. **`get_wa_toplists.py`** – scraper oparty na `Playwright`, pobierający listy Top 1000 (10 stron po 100 wyników na sezon i konkurencję, łącznie 300 podstron) z serwisu World Athletics do pliku `top1000_raw_data.csv`. Wykorzystuje losowe opóźnienia (`1.5–4.5 s`) między zapytaniami.
2. **`check_data.py`** – skrypt walidujący kompletność pobranych danych na podstawie oczekiwanych trójek `(Event, Year, Page)` i raportujący brakujące podstrony.
3. **`get_wa_missing_data.py`** – skrypt uzupełniający (patch), dociągający brakujące podstrony i dopisujący je do `top1000_raw_data.csv`.
4. **`wa_data_processor.py`** – parser przetwarzający surowe ciągi tekstowe (`Raw_Data`) na ustrukturyzowaną tabelę wynikową `top1000_clean.csv`.
5. **`classify_athletes.py`** – wektorowa klasyfikacja rocznych stanów zawodników. Dla każdego sezonu wyznacza konkurencję wiodącą (odrzucając starty „na przetarcie”, gdzie pozycja jest o ponad 150 miejsc lub 1.5x gorsza od najlepszej w danym roku) i zwija kolejne sezony w trajektorie kariery (`possible_transfers.csv` oraz `possible_transfers_results.csv`).
6. **`filter_results.py`** – odfiltrowuje wielostopniowe oscylacje (np. sezonowe żonglowanie 400m i 400mH) i zostawia wyłącznie czyste transfery jednostopniowe (`A -> B`) oraz płynne przejścia z rokiem przejściowym (`A -> A+B -> B`). Wylicza cechy przejścia (`rank_gain`, `seasons_old`, `seasons_new`, `rank_std_new`, `switch_age`) i zapisuje wynik w `real_transfers.csv`.
7. **`transfers_summary.py`** – generuje zbiorcze statystyki opisowe dla poszczególnych kierunków migracji (odsetek awansów, mediana zysku miejsc, trwałość transferu min. 2 sezony, mediana wieku zmiany) oraz zestawienia czołowych zawodników.

## Kluczowe decyzje metodologiczne i ograniczenia

* **Odrzucenie prostej chronologii debiutów i uśredniania lat:** Starty na przetarcie (np. 800-metrowcy biegający wiosną 400m na poziomie 700–950. miejsca na świecie) generują fałszywe sygnały migracji. Dopiero wyznaczenie **konkurencji wiodącej w każdym sezonie** pozwala oddzielić realną zmianę specjalizacji od startów treningowych.
* **Rezygnacja z algorytmów klasteryzujących (np. K-Means):** Po odfiltrowaniu szumu zbiór czystych transferów liczy 163 zawodników podzielonych na 6 kierunków. Przy tak małej próbie klasteryzacja oparta na odległości euklidesowej jest niestabilna i grupuje zawodników według bezwzględnego poziomu sportowego zamiast charakteru zmiany. Lepszą interpretację dają deterministyczne reguły domenowe i statystyki oparte na medianach.
* **Ucięcie danych na progu Top 1000 (*truncation*):** Baza zawiera wyłącznie najlepszy wynik zawodnika w sezonie, o ile zmieścił się on w światowym Top 1000. Nie widać w niej nieudanych prób zmiany konkurencji, które zatrzymały się poza tysiącem.
* **Błąd przeżywalności:** Wysoka skuteczność w grupach o małej liczebności (np. `400mH -> 800m`) wynika z silnej autoselekcji – na zmianę dystansu decydują się niemal wyłącznie zawodnicy o predyspozycjach wytrzymałościowo-tempowych.

## Uruchomienie i źródło danych

Wymagane biblioteki: `pandas`, `numpy`, `playwright` (wraz z binariami przeglądarki zainstalowanymi przez `playwright install chromium`).

Skrypty powstały wyłącznie na potrzeby prywatnej analizy statystycznej. Surowe zbiory danych (`top1000_raw_data.csv`, `top1000_clean.csv`) nie są udostępniane w repozytorium — dołączono jedynie zagregowany plik wynikowy `real_transfers.csv`.