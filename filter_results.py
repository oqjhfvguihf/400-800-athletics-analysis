import pandas as pd
import numpy as np

df = pd.read_csv("possible_transfers_results.csv")
id_cols = ['Athlete', 'Nat', 'Birth_Year']

# 1. Walidacja czystych ścieżek (1 strzałka A -> B lub płynne A -> A+B -> B)
def normalize_clean_migration(traj):
    parts = traj.split(" -> ")
    
    # Przypadek 1: Bezpośrednie przejście A -> B (bez '+')
    if len(parts) == 2 and "+" not in parts[0] and "+" not in parts[1]:
        return f"{parts[0]} -> {parts[1]}"
    
    # Przypadek 2: Płynne przejście z rokiem przejściowym A -> A+B -> B
    if len(parts) == 3 and "+" not in parts[0] and "+" not in parts[2] and "+" in parts[1]:
        mid = set(parts[1].split("+"))
        if mid == {parts[0], parts[2]} and parts[0] != parts[2]:
            return f"{parts[0]} -> {parts[2]}"
            
    return None

df['clean_path'] = df['trajectory'].apply(normalize_clean_migration)
clean_df = df.dropna(subset=['clean_path']).copy()

print("Liczebność czystych migracji:")
print(clean_df.groupby('clean_path')['Athlete'].nunique().sort_values(ascending=False))

# 2. Budowa macierzy cech przejścia (old_event -> new_event) pod klasteryzację
rows = []
for keys, group in clean_df.groupby(id_cols + ['clean_path']):
    athlete, nat, birth_year, path = keys
    old_ev, new_ev = path.split(" -> ")
    
    old_g = group[group['Event'] == old_ev]
    new_g = group[group['Event'] == new_ev]
    
    best_old = old_g['Rank'].min()
    best_new = new_g['Rank'].min()
    first_year_new = new_g['Year'].min()
    
    rows.append({
        'Athlete': athlete,
        'Nat': nat,
        'Birth_Year': birth_year,
        'clean_path': path,
        'old_event': old_ev,
        'new_event': new_ev,
        'best_rank_old': best_old,
        'best_rank_new': best_new,
        # Dodatni wynik = awans w rankingu po zmianie dystansu (np. z 500. miejsca na 80. = +420)
        'rank_gain': best_old - best_new,
        'seasons_old': old_g['Year'].nunique(),
        'seasons_new': new_g['Year'].nunique(),
        'rank_std_new': new_g['Rank'].std() if len(new_g) > 1 else 0.0,
        'switch_age': (first_year_new - birth_year) if birth_year > 0 else np.nan
    })

features_df = pd.DataFrame(rows)
features_df.to_csv("real_transfers.csv", index=False, encoding="utf-8-sig")
print(f"\nZapisano {len(features_df)} czystych profili transferowych")