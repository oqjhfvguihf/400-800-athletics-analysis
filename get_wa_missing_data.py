from playwright.sync_api import sync_playwright
import pandas as pd
import time

# Zdefiniowanie 3 brakujących podstron
MISSING_PAGES = [
    ("400m", "sprints/400-metres", 2020, 4),
    ("400mH", "hurdles/400-metres-hurdles", 2020, 8),
    ("800m", "middlelong/800-metres", 2021, 2)
]

patch_rows = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    for event_name, url_path, year, page_num in MISSING_PAGES:
        url = f"https://worldathletics.org/records/toplists/{url_path}/outdoor/men/senior/{year}?page={page_num}"
        print(f"Dociąganie: {event_name} | {year} | Strona {page_num}...")
        
        try:
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            page.wait_for_selector("table.records-table tbody tr", timeout=10000)
            table_rows = page.locator("table.records-table tbody tr").all()

            for row in table_rows:
                text_cells = [td.inner_text().strip() for td in row.locator("td").all()]
                if text_cells:
                    patch_rows.append({
                        "Event": event_name,
                        "Year": year,
                        "Page": page_num,
                        "Raw_Data": " | ".join(text_cells)
                    })
        except Exception as e:
            print(f"   [!] Błąd przy pobieraniu {url}: {e}")
        
        time.sleep(2)

    browser.close()

# Dopisanie wyników (mode='a') na koniec surowego pliku
if patch_rows:
    df_patch = pd.DataFrame(patch_rows)
    df_patch.to_csv("top1000_raw_data.csv", mode='a', header=False, index=False, encoding="utf-8-sig")
    print(f"\nSukces! Dopisano {len(df_patch)} wierszy. Plik 'top1000_raw_data.csv' jest kompletny.")