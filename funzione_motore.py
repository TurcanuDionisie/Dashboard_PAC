import pandas as pd
import numpy as np
import os


folder_path = r"C:\Users\Dionisie.Turcanu\Documents\GitHub\Dashboard_PAC"
os.chdir(folder_path)

base_dati = pd.read_excel('DB_TOT_PROXY.xlsx', index_col=0)



# %% FUNZIONI



def financial_analysis(quote, giorno_del_mese, frequenza, durata_anni, importo_rata):
    # Mappa la frequenza a un numero di mesi
    frequenze = {
        'Mensile': 1,
        'Bimestrale': 2,
        'Trimestrale': 3,
        'Quadrimestrale': 4,
        'Semestrale': 6,
        'Annuale': 12,
    }

    num_mesi = frequenze[frequenza]
    numero_rate = (12 / num_mesi) * durata_anni
    importo_rata_mensile = (importo_rata * (12 / num_mesi) * durata_anni) / (durata_anni * 12)
    investimento_iniziale = importo_rata_mensile * 12
    importo_totale = numero_rate * importo_rata

    costo_sottoscrizione = 0.03
    diritto_fisso_iniziale = 2.4 * 0.3
    diritto_fisso = 1.54 * 0.3

    importo_costo_sottoscrizione = costo_sottoscrizione * (importo_totale + investimento_iniziale) * 0.3

    prima_fetta = importo_costo_sottoscrizione * 0.33
    seconda_fetta = importo_costo_sottoscrizione * 0.19
    terza_fetta = importo_costo_sottoscrizione * 0.48

    movimenti = pd.DataFrame(index=quote.index)
    movimenti['Movimenti'] = 0
    movimenti.iloc[0] = investimento_iniziale

    def trova_data(dates, target_day):
        for date in dates:
            if date.day >= target_day:
                return date
        return None

    mesi_anni = [(date.year, date.month) for date in quote.index]
    mesi_anni = list(set(mesi_anni))
    mesi_anni.sort()

    rate_added = 0
    current_month = None
    for year, month in mesi_anni:
        if current_month is None or ((month - current_month) % 12) >= num_mesi:
            dates = quote.index[(quote.index.year == year) & (quote.index.month == month)]
            dates = dates.sort_values()

            date = trova_data(dates, giorno_del_mese)

            if date is not None and rate_added < numero_rate:
                movimenti.loc[date] += importo_rata
                rate_added += 1
                current_month = month

    quote = pd.concat([quote, movimenti], axis=1)

    quote['COSTI UP1'] = np.nan
    movimenti_index = quote[quote['Movimenti'] != 0].index
    quote.loc[movimenti_index[0], 'COSTI UP1'] = prima_fetta

    for i in range(1, 7):
        if i < len(movimenti_index):
            quote.loc[movimenti_index[i], 'COSTI UP1'] = seconda_fetta / 6

    num_movimenti_rimanenti = len(movimenti_index) - 7
    for i in range(7, len(movimenti_index)):
        if i < len(movimenti_index):
            quote.loc[movimenti_index[i], 'COSTI UP1'] = terza_fetta / num_movimenti_rimanenti

    quote['COSTI UP3'] = np.nan
    movimenti_index = quote[quote['Movimenti'] != 0].index
    quote.loc[movimenti_index[0], 'COSTI UP3'] = diritto_fisso_iniziale

    for i in range(1, len(movimenti_index)):
        quote.loc[movimenti_index[i], 'COSTI UP3'] = diritto_fisso

    quote["MOVIMENTO_NETTO"] = quote["Movimenti"] - quote["COSTI UP1"] - quote["COSTI UP3"]
    quote = quote.fillna(0)

    quote['CTV_LORDO'] = np.nan
    movimenti_index = quote[quote['Movimenti'] != 0].index
    quote.loc[movimenti_index[0], 'CTV_LORDO'] = quote.loc[movimenti_index[0], 'Movimenti']

    for i in range(1, len(quote.index)):
        ctv_precedente = quote.loc[quote.index[i-1], 'CTV_LORDO']
        quote_precedente = quote.loc[quote.index[i-1], quote.columns[0]]
        quote_corrispettivo = quote.loc[quote.index[i], quote.columns[0]]
        movimento_corrispettivo = quote.loc[quote.index[i], 'Movimenti']

        quote.loc[quote.index[i], 'CTV_LORDO'] = (ctv_precedente * quote_corrispettivo / quote_precedente) + movimento_corrispettivo

    quote['CTV_NETTO'] = np.nan
    movimenti_index = quote[quote['MOVIMENTO_NETTO'] != 0].index
    quote.loc[movimenti_index[0], 'CTV_NETTO'] = quote.loc[movimenti_index[0], 'MOVIMENTO_NETTO']

    for i in range(1, len(quote.index)):
        ctv_precedente = quote.loc[quote.index[i-1], 'CTV_NETTO']
        quote_precedente = quote.loc[quote.index[i-1], quote.columns[0]]
        quote_corrispettivo = quote.loc[quote.index[i], quote.columns[0]]
        movimento_corrispettivo = quote.loc[quote.index[i], 'MOVIMENTO_NETTO']

        quote.loc[quote.index[i], 'CTV_NETTO'] = (ctv_precedente * quote_corrispettivo / quote_precedente) + movimento_corrispettivo

    max_date = quote.index.max()
    quote['Numeri'] = quote['Movimenti'] * (max_date - quote.index).days

    totale_dovuto = importo_totale + investimento_iniziale
    quote['CTV Complessivo'] = quote['CTV_NETTO'] + totale_dovuto - quote['MOVIMENTO_NETTO'].cumsum()

    quote['VOL'] = quote['CTV Complessivo'].pct_change()
    quote['MAX DD'] = quote['CTV_NETTO'] / quote['MOVIMENTO_NETTO'].cumsum() - 1

    volatilita = quote['CTV Complessivo'].resample('M').last().pct_change()

    numero_rate = numero_rate
    importo_rata = importo_rata
    totale_rate_versate = sum(quote['Movimenti'])
    patrimonio_finale = quote['CTV_NETTO'].iloc[-1]
    plus = patrimonio_finale - totale_rate_versate
    mwrr = plus / (sum(quote['Numeri']) / (quote.index[-1] - quote.index[0]).days)
    mwrr_annualizzato = ((1 + mwrr) ** (365 / (quote.index[-1] - quote.index[0]).days)) - 1
    volatilita_finale = np.std(volatilita) * np.sqrt(12)
    max_dd = min(quote['MAX DD'])


    results = {
        "numero_rate": numero_rate,
        "importo_rata": importo_rata,
        "totale_rate_versate": totale_rate_versate,
        "patrimonio_finale": patrimonio_finale,
        "plus": plus,
        "mwrr": mwrr,
        "mwrr_annualizzato": mwrr_annualizzato,
        "volatilita_finale": volatilita_finale,
        "max_dd": max_dd
    }

    return results




# %% 
quote = base_dati["IE0004878744"]
giorno_del_mese = 8
frequenza = 'Mensile'
durata_anni = 10
importo_rata = 200 * 0.3


hh = financial_analysis(quote, giorno_del_mese, frequenza, durata_anni, importo_rata)





