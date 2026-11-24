import pandas as pd

# 1. Wczytanie surowego pliku
df = pd.read_csv("top1000_raw_data.csv")

# 2. Rozbicie kolumny Raw_Data po znaku '|' z usunięciem białych znaków
split_cols = df["Raw_Data"].str.split(r"\s*\|\s*", expand=True)

# 3. Przypisanie wyciągniętych pól do odpowiednich nazw
df["Rank"] = split_cols[0]
df["Mark"] = split_cols[1]
df["Athlete"] = split_cols[3]
df["DOB_raw"] = split_cols[4]
df["Nat"] = split_cols[5]
df["Pos"] = split_cols[6]
df["Venue"] = split_cols[8]
df["Date"] = split_cols[9]
df["Score"] = split_cols[10]

# 4. Przeliczenie czasów (np. 1:44.15 -> 104.15 s) pod algorytmy ML
def time_to_seconds(val):
    if not isinstance(val, str):
        return None
    val = val.strip()
    if ":" in val:
        mins, secs = val.split(":")
        return round(float(mins) * 60 + float(secs), 2)
    try:
        return float(val)
    except ValueError:
        return None

df["Mark_Sec"] = df["Mark"].apply(time_to_seconds)

# 5. Konwersja daty urodzenia (DOB) na pełny format daty i wyciągnięcie roku urodzenia
df["DOB"] = pd.to_datetime(df["DOB_raw"], format="%d %b %Y", errors="coerce")
df["Birth_Year"] = df["DOB"].dt.year

# 6. Czyszczenie i zapis do docelowego pliku
df_clean = df.drop(columns=["Raw_Data", "DOB_raw"])
df_clean.to_csv("top1000_clean.csv", index=False, encoding="utf-8-sig")

print(f"Gotowe! Wyczyszczono i zapisano {len(df_clean)} rekordów w 'top1000_clean.csv'.")
# Sprawdzenie liczby rekordów dla każdej konkurencji i roku
missing_summary = df_clean.groupby(['Event', 'Year']).size()
print(missing_summary[missing_summary < 1000])