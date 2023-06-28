import pandas as pd
import numpy as np
import os

import funzioni_motore


folder_path = r"C:\Users\Dionisie.Turcanu\Documents\GitHub\Dashboard_PAC"
os.chdir(folder_path)



#lettura file input
file_decodifiche = pd.read_excel('costi.xlsx', index_col=0)
base_dati = pd.read_excel('DB_TOT_PROXY.xlsx', index_col=0)





# Mappa la frequenza a un numero di mesi
frequenze = {
    'Mensile': 1,
    'Bimestrale': 2,
    'Trimestrale': 3,
    'Quadrimestrale': 4,
    'Semestrale': 6,
    'Annuale': 12,
}






def EseguiAnalisi (input_motore):
    
    
    # isin selezionati e corrispettivo peso
    fondi = {
        
    }
    
    
    #estrazione dati input utente (tutti)
    frequenza =  input_motore['frequenza']
    importo_rata = float(input_motore['importo_rata'])
    durata_anni = int(input_motore['durata_anni'])
    giorno_del_mese = int(input_motore['giorno_mese'])
    
    #non ancora gestito
    data_inizio = input_motore['data_inizio']
    
    
    #deroga ancora da gestire
    deroga_iniziale = 1
    deroga_totale = 1
    
    
    #trasformo pesi dei fondi da stringhe in float
    for isin in input_motore["isin_selezionati"]:
        fondi[isin] = float(input_motore["isin_selezionati"][isin])
    
    
    
    num_mesi = frequenze[frequenza]

    numero_rate = (12 / num_mesi) * durata_anni

    importo_rata_mensile = (importo_rata * (12 / num_mesi) * durata_anni) / (durata_anni * 12)

    investimento_iniziale = importo_rata_mensile * 12

    #escluso versamento iniziale
    importo_totale_rate = numero_rate * importo_rata



    dati_input_costi = {
            #fondi selezionati con corrispettivo peso
            "fondi": fondi,
            
            #file con tutte le fasce di costo
            "file_decodifiche": file_decodifiche,
            
            #dati input utente
            'importo_rata_mensile': importo_rata_mensile,
            'importo_totale_rate':importo_totale_rate,
            'investimento_iniziale': investimento_iniziale
    }
    
    
    #calcola costi
    costi = funzioni_motore.calcola_costi(dati_input_costi)
    
    print(costi)

    
    #controlla importo rata minima
    #se non rispettato chiudi
    if costi == "ERRORE RATA MENSILE":
        return "ERRORE RATA MENSILE"
    elif costi == "ERRORE IMPORTO MINIMO":
        return "ERRORE IMPORTO MINIMO"
    
    
    # se sono arrivato qua tutto apposto con le rate    
    
    #tabella contenente le performance per ogni fondo selezionato
    risultati_performance = {}


    #per ogni fondo selezionato estraggo le quote e peso nel portafolgio
    for isin in fondi:
        quote = base_dati[isin]
        peso = fondi[isin]
        
        
        dati_input_performance = {
            
            #serie storica
            "quote" : quote,
            
            #quanto pesa nel portafolgio
            "peso" : peso,
            
            #costi
            "costo_sottoscrizione" : costi["costi_sottoscrizione"],
            "diritto_fisso_iniziale" : costi["diritti_fissi_iniziali"],
            "diritto_fisso" : costi["diritti_fissi"],
            
            #sconti
            "deroga_totale" : deroga_totale,
            "deroga_iniziale" : deroga_iniziale,
            "num_mesi" : num_mesi,
            
            #informazioni rata
            "giorno_del_mese" : giorno_del_mese,
            "numero_rate" : numero_rate,
            "importo_rata" : importo_rata,
            
        }
        
        
        
        #calcolo le performance di ogni fondo
        risultati_performance[isin] = funzioni_motore.calcola_performance(dati_input_performance)
    
    
    
    # # in realtà contiene tutto
    # grafico = funzioni_motore.GraficoPortafolgio(risultati_performance, isin, (importo_totale_rate + investimento_iniziale))
    
    
    
    # return grafico
    
    
