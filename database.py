import pandas as pd
import numpy as np
import wbgapi as wb

# Pobranie wskaźników do analizy z WB API
WSKAZNIKI = {
    "Bezrobocie młodych (15-24 lata) (%)": "SL.UEM.1524.NE.ZS",
    "Stopa bezrobocia ogółem (%)": "SL.UEM.TOTL.NE.ZS",
    "Aktywność zawodowa kobiet (%)": "SL.TLF.CACT.FE.ZS",
    "Zamożność społeczeństwa (PKB per capita w USD)": "NY.GDP.PCAP.CD",
    "Pracownicy etatowi (% ogółu pracujących)": "SL.EMP.WORK.ZS",
    "Udział dochodów z pracy w PKB (%)": "SL.EMP.1524.SP.ZS",
    "Wydajność pracy (PKB na osobo-zatrudnionego w USD)": "SL.GDP.PCAP.EM.KD",
}

current_df = None
_countries_cache = {}
_data_cache = {}


def download_countries():
    """Zwraca stałą listę 10 wybranych krajów Europy."""
    global _countries_cache
    if _countries_cache:
        return _countries_cache

    top_10_europe = {
        "Austria": "AUT",
        "Belgium": "BEL",
        "Czechia": "CZE",
        "France": "FRA",
        "Germany": "DEU",
        "Italy": "ITA",
        "Netherlands": "NLD",
        "Poland": "POL",
        "Spain": "ESP",
        "Sweden": "SWE"
    }

    _countries_cache = top_10_europe
    return top_10_europe


def fetch_data(iso3_c1, iso3_c2, indicator_code, start_year, end_year):
    """Dynamicznie pobiera szeregi czasowe z World Bank API z użyciem cache."""
    global current_df, _data_cache

    cache_key = (iso3_c1, iso3_c2, indicator_code, start_year, end_year)
    if cache_key in _data_cache:
        current_df = _data_cache[cache_key]
        return current_df

    lata = list(range(start_year, end_year + 1))
    # Kraj 1
    try:
        df1_raw = wb.data.DataFrame(indicator_code, iso3_c1, time=lata, numericTimeKeys=True)
    except Exception as e:
        raise RuntimeError(f"Błąd połączenia z API dla kraju podstawowego: {str(e)}")

    if df1_raw.empty:
        df1 = pd.DataFrame(columns=['Rok', 'Wartosc_Kraj1'])
    else:
        df1 = df1_raw.T.reset_index()
        df1.columns = ['Rok', 'Wartosc_Kraj1']
        df1['Rok'] = df1['Rok'].astype(int)
        df1 = df1.dropna(subset=['Wartosc_Kraj1'])

    # Kraj 2
    if iso3_c2 and iso3_c1 != iso3_c2:
        try:
            df2_raw = wb.data.DataFrame(indicator_code, iso3_c2, time=lata, numericTimeKeys=True)
        except Exception as e:
            raise RuntimeError(f"Błąd połączenia z API dla kraju porównawczego: {str(e)}")

        if df2_raw.empty:
            df2 = pd.DataFrame(columns=['Rok', 'Wartosc_Kraj2'])
        else:
            df2 = df2_raw.T.reset_index()
            df2.columns = ['Rok', 'Wartosc_Kraj2']
            df2['Rok'] = df2['Rok'].astype(int)
            df2 = df2.dropna(subset=['Wartosc_Kraj2'])

        df = pd.merge(df1, df2, on='Rok', how='inner')
    else:
        df = df1.copy()
        df['Wartosc_Kraj2'] = np.nan

    df_sorted = df.sort_values('Rok').reset_index(drop=True)

    _data_cache[cache_key] = df_sorted
    current_df = df_sorted
    return df_sorted


def calculate_numpy_stats(df):
    """Wykonuje obliczenia statystyki opisowej w NumPy."""
    df_clean1 = df.dropna(subset=['Wartosc_Kraj1'])
    arr1 = df_clean1['Wartosc_Kraj1'].to_numpy()

    stats = {
        "max1": np.max(arr1) if len(arr1) > 0 else np.nan,
        "min1": np.min(arr1) if len(arr1) > 0 else np.nan,
        "mean1": np.mean(arr1) if len(arr1) > 0 else np.nan,
        "std1": np.std(arr1) if len(arr1) > 0 else np.nan,
        "max2": None, "min2": None, "mean2": None, "std2": None
    }

    if 'Wartosc_Kraj2' in df.columns and not df['Wartosc_Kraj2'].isna().all():
        df_clean2 = df.dropna(subset=['Wartosc_Kraj2'])
        arr2 = df_clean2['Wartosc_Kraj2'].to_numpy()
        if len(arr2) > 0:
            stats.update({
                "max2": np.max(arr2),
                "min2": np.min(arr2),
                "mean2": np.mean(arr2),
                "std2": np.std(arr2)
            })
    return stats


def export_to_csv(filename):
    """Eksportuje dane z pamięci podręcznej do pliku CSV."""
    global current_df
    if current_df is not None and not current_df.empty:
        current_df.to_csv(filename, index=False, encoding="utf-8-sig")
        return True
    return False