import pandas as pd

df = pd.read_csv("top1000_clean.csv")
df['Rank'] = pd.to_numeric(df['Rank'], errors='coerce')
df['Birth_Year'] = df['Birth_Year'].fillna(-1).astype(int)
id_cols = ['Athlete', 'Nat', 'Birth_Year']

# 1. Wektorowe wyznaczenie najlepszego miejsca w danym roku
df['best_year_rank'] = df.groupby(id_cols + ['Year'])['Rank'].transform('min')

# 2. Odfiltrowanie startów na przetarcie (zostawiamy główną konkurencję + ewentualną równorzędną)
dominant = df[
    (df['Rank'] <= df['best_year_rank'] * 1.5) &
    (df['Rank'] - df['best_year_rank'] <= 150)
].copy()

# 3. Sklejenie konkurencji w obrębie jednego roku (posortowane alfabetycznie, bez duplikatów)
dominant = dominant.sort_values(id_cols + ['Year', 'Event']).drop_duplicates(id_cols + ['Year', 'Event'])
yearly_states = (
    dominant.groupby(id_cols + ['Year'])['Event']
    .agg('+'.join)
    .reset_index(name='state')
)

# 4. Wektorowe zwinięcie sąsiadujących identycznych lat (zamiast wolnego apply)
yearly_states['prev_state'] = yearly_states.groupby(id_cols)['state'].shift(1)
state_changes = yearly_states[yearly_states['state'] != yearly_states['prev_state']]

trajectories = (
    state_changes.groupby(id_cols)['state']
    .agg(' -> '.join)
    .reset_index(name='trajectory')
)

# 5. Zapisujemy tylko zawodników, u których nastąpiła zmiana stanu
real_migrants = trajectories[trajectories['trajectory'].str.contains('->')].copy()
df_clean_migrants = df.drop(columns=['best_year_rank']).merge(real_migrants, on=id_cols, how='inner')

real_migrants.to_csv("possible_transfers.csv", index=False, encoding="utf-8-sig")
df_clean_migrants.to_csv("possible_transfers_results.csv", index=False, encoding="utf-8-sig")

print(f"Zapisano {len(real_migrants)} migrantów do 'possible_transfers.csv'.")