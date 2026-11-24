import pandas as pd

df = pd.read_csv("real_transfers.csv")

# Dodatkowe flagi binarne do policzenia odsetków
df['improved_peak'] = df['rank_gain'] > 0          # czy poprawił najlepszy ranking po zmianie
df['sustained_move'] = df['seasons_new'] >= 2      # czy utrzymał się w Top 1000 min. 2 sezony

summary = df.groupby('clean_path').agg(
    zawodnicy=('Athlete', 'count'),
    odsetek_awansu_pct=('improved_peak', lambda x: round(x.mean() * 100, 1)),
    mediana_zysku_miejsc=('rank_gain', 'median'),
    mediana_best_rank_nowy=('best_rank_new', 'median'),
    odsetek_trwalych_pct=('sustained_move', lambda x: round(x.mean() * 100, 1)),
    mediana_wieku_zmiany=('switch_age', 'median')
).sort_values(by='zawodnicy', ascending=False)

print("=== PODSUMOWANIE SKUTECZNOŚCI TRANSFERÓW ===")
print(summary.to_string())

# Podgląd najbardziej udanych skróceń (800m -> 400m) i wydłużeń (400m -> 800m)
for path in ['800m -> 400m', '400m -> 800m', '400mH -> 800m']:
    print(f"\n--- TOP 5 dla {path} (wg najlepszego miejsca po zmianie) ---")
    top = df[df['clean_path'] == path].sort_values('best_rank_new').head(5)
    print(top[['Athlete', 'Nat', 'switch_age', 'best_rank_old', 'best_rank_new', 'rank_gain', 'seasons_new']].to_string(index=False))