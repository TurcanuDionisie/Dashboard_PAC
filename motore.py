import pandas as pd
import numpy as np

import funzioni_motore





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
    
    
    
    #ESTRAZIONE DATI RICEVUTI IN INPUT
    
    file_quote = input_motore['file_quote']
    file_costi = input_motore['file_costi']
    
    #estrazione dati input utente (tutti)
    frequenza =  input_motore['frequenza']
    importo_rata = input_motore['importo_rata']
    durata_anni = input_motore['durata_anni']
    giorno_del_mese = input_motore['giorno_mese']
    
   
    
    deroga = input_motore['deroga']
    
    #DEROGA
    if deroga == 'Nessuna':
        deroga_iniziale = 1
        deroga_totale = 1
    elif deroga == 'Iniziale 25%':
        deroga_iniziale = 0.75
        deroga_totale = 1
    elif deroga == 'Iniziale 50%':
        deroga_iniziale = 0.5
        deroga_totale = 1
    elif deroga == 'Iniziale 75%':
        deroga_iniziale = 0.25
        deroga_totale = 1
    elif deroga == 'Iniziale 100%':
        deroga_iniziale = 0
        deroga_totale = 1
    elif deroga == 'Totale 25%':
        deroga_iniziale = 1
        deroga_totale = 0.75
    elif deroga == 'Totale 50%':
        deroga_iniziale = 1
        deroga_totale = 0.5
    elif deroga == 'Totale 75%':
        deroga_iniziale = 1
        deroga_totale = 0.25
    elif deroga == 'Totale 100%':
        deroga_iniziale = 1
        deroga_totale = 0
    
    
    

    
    #i pesi dei fondi inseriti dall'utente sono stringhe
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
            "file_costi": file_costi,
            
            #dati input utente
            'importo_rata_mensile': importo_rata_mensile,
            'importo_totale_rate':importo_totale_rate,
            'investimento_iniziale': investimento_iniziale
    }
    
    
    #calcola costi
    costi = funzioni_motore.calcola_costi(dati_input_costi)
    
    print("COSTI")
    print(costi)
    

    
    #prima di calcolare performance controlla importo rata minima
    #se non rispettato chiudi
    if costi == "ERRORE RATA MENSILE":
        return "ERRORE RATA MENSILE"
    elif costi == "ERRORE IMPORTO MINIMO":
        return "ERRORE IMPORTO MINIMO"
    
    
    # se sono arrivato qua tutto apposto con le rate    
    
    
    
    #salvo le performance per ogni fondo selezionato
    #serviranno per il calcolo performance portafolgio e per le varie tabs
    risultati_performance = {}


    #per ogni fondo selezionato estraggo le quote e peso nel portafolgio
    for isin in fondi:
        quote = file_quote[isin]
        peso = fondi[isin]
        
        
        dati_input_performance = {
            
            #serie storica
            "quote" : quote,
            
            #quanto pesa nel portafolgio
            "peso" : peso,
            
            #costi
            "costi_sottoscrizione" : costi["costi_sottoscrizione"],
            "diritti_fissi_iniziali" : costi["diritti_fissi_iniziali"],
            "diritti_fissi" : costi["diritti_fissi"],
            
            #sconti
            "deroga_totale" : deroga_totale,
            "deroga_iniziale" : deroga_iniziale,
            "num_mesi" : num_mesi,
            
            #informazioni rata
            "giorno_del_mese" : giorno_del_mese,
            "numero_rate" : numero_rate,
            "importo_rata" : importo_rata,
            "durata_anni": durata_anni
            
        }
        
        
        
        #calcolo le performance del fondo
        
        risultati_performance[isin] = funzioni_motore.calcola_performance(dati_input_performance)
        
        
    
    
    #dati input per calcolo performance portafolgio
    dati_input_portafolgio = {
        
        "risultati_performance": risultati_performance,
        "importo_totale_rate": importo_totale_rate,
        "investimento_iniziale": investimento_iniziale,
    }
    
    
    # contiene tutti i dati elaborati del portafolgio
    elaborazione = funzioni_motore.CalcolaPerformancePortafolgio(dati_input_portafolgio)
    
    

    
    #SALVO CALCOLI SU EXCEL
    #ELIMINARE DOPO
    with pd.ExcelWriter('test/output.xlsx') as writer:  
        for isin in fondi:
            temp_excel = risultati_performance[isin]['calcoli'].copy()
            temp_excel.replace(0, np.nan, inplace=True)
            temp_excel.to_excel(writer, sheet_name=isin)
            
            
        temp_excel = elaborazione['calcoli'].copy()
        temp_excel.replace(0, np.nan, inplace=True)
        temp_excel.to_excel(writer, sheet_name="PORTAFOLGIO")
        

    

    
    #contiene tutti i dati necessari per tutti i componenti
    risultato_motore = {
        
        #dati portafolgio
        "portafoglio": elaborazione,
        
        #dati singoli fondi
        "singoli_fondi": risultati_performance
    }
    
        
    
    return risultato_motore
    
    

