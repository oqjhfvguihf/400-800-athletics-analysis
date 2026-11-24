import pandas as pd

df_raw = pd.read_csv("top1000_raw_data.csv")

# Tworzymy zbiór oczekiwanych trójek: (Konkurencja, Rok, Strona)
expected = {(e, y, p) for e in ['400m', '400mH', '800m'] for y in range(2017, 2027) for p in range(1, 11)}
scraped = set(zip(df_raw['Event'], df_raw['Year'], df_raw['Page']))

missing_pages = sorted(list(expected - scraped))
print("Strony, które w ogóle się nie pobrały:")
for event, year, page in missing_pages:
    print(f"- {event} | {year} | Strona {page}")