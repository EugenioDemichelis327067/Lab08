from database.distributore_DAO import DistributoreDAO


'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()      #dovrei avere teoricamente lista di classi e ogni classe ha a sua volta lista di prezzi

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        prezzi_medi = []
        for distributore in self._distributori: #elemento è gia l'oggetto distributore
            lista_prezzi = distributore.get_prezzi()   #la classe distributore chiama il metodo che ha lei( get_prezzi)
            prezzi_mese_scelto = []
            for p in lista_prezzi:
                if p.data.month == mese:
                    prezzi_mese_scelto.append(p.prezzo_litro)
            media = sum(prezzi_mese_scelto)/len(prezzi_mese_scelto)
            prezzi_medi.append((distributore.nome,media))
        return prezzi_medi


    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        if giorno > 8 or len(sequenza_parziale) == 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale)
            return
        for distributore_id, prezzi in prezzi_settimana.items():
            obj_prezzo = prezzi[giorno - 1]
            prezzo_oggi = obj_prezzo.prezzo_litro
            costo_aggiuntivo = prezzo_oggi * 100
            if ultimo_distributore is not None and ultimo_distributore != distributore_id:
                costo_aggiuntivo += 5.0
            sequenza_parziale.append(distributore_id)
            self.__ricorsione(
                sequenza_parziale,
                giorno + 1,
                distributore_id,
                costo_corrente + costo_aggiuntivo,
                prezzi_settimana
            )
            sequenza_parziale.pop()



    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        lista7gg={}
        for distributore in self._distributori:
            lista_prezzi = distributore.get_prezzi()
            listaDaAppendere=[p for p in lista_prezzi if p.data.month==mese and 1 <= p.data.day <= 7]
            listaDaAppendere.sort(key=lambda x: x.data.day)
            lista7gg[distributore.id]=listaDaAppendere
        return lista7gg


