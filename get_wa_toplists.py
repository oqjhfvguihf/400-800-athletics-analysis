from playwright.sync_api import sync_playwright
import pandas as pd
import random
import time

# Konfiguracja konkurencji i ich unikalnych fragmentów w URL World Athletics
EVENTS = {
    "400m": "sprints/400-metres",
    "400mH": "hurdles/400-metres-hurdles",
    "800m": "middlelong/800-metres"
}

YEARS = range(2017, 2027)  # Lata 2017 - 2026
PAGES_PER_YEAR = 10        # 10 stron = Top 1000

all_rows = []

with sync_playwright() as p:
    # Uruchamiamy widoczną przeglądarkę (headless=False) z realizmem zachowania człowieka
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        viewport={'width': 1280, 'height': 800}
    )
    page = context.new_page()

    total_steps = len(EVENTS) * len(YEARS) * PAGES_PER_YEAR
    current_step = 0

    print(f"Rozpoczynam pobieranie łącznie {total_steps} podstron...\n")

    for event_name, event_url_path in EVENTS.items():
        for year in YEARS:
            for page_num in range(1, PAGES_PER_YEAR + 1):
                current_step += 1
                
                # Konstrukcja bezpośredniego adresu URL dla konkretnej strony
                url = f"https://worldathletics.org/records/toplists/{event_url_path}/outdoor/men/senior/{year}?page={page_num}"
                
                print(f"[{current_step}/{total_steps}] Pobieranie: {event_name} | {year} | Strona {page_num}/10...")

                try:
                    page.goto(url, timeout=30000, wait_until="domcontentloaded")
                    
                    # Czekamy na załadowanie wierszy tabeli
                    page.wait_for_selector("table.records-table tbody tr", timeout=10000)
                    
                    # Pobieramy wiersze
                    table_rows = page.locator("table.records-table tbody tr").all()

                    for row in table_rows:
                        text_cells = [td.inner_text().strip() for td in row.locator("td").all()]
                        if text_cells:
                            all_rows.append({
                                "Event": event_name,
                                "Year": year,
                                "Page": page_num,
                                "Raw_Data": " | ".join(text_cells)
                            })

                except Exception as e:
                    print(f"   [!] Błąd na stronie {url}: {e}")

                # Kluczowy moment: losowa przerwa od 1.5 do 3.5 sekundy imitująca człowieka
                sleep_time = random.uniform(1.5, 4.5)
                time.sleep(sleep_time)

    browser.close()

# Zapis zebranych danych
if all_rows:
    df = pd.DataFrame(all_rows)
    df.to_csv("top1000_raw_data.csv", index=False, encoding="utf-8-sig")
    print(f"\nSukces! Zapisano {len(df)} wierszy do pliku 'top1000_raw_data.csv'.")
else:
    print("\nBrak pobranych danych.")