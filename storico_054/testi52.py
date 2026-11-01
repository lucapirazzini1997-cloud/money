"""Testi rimasti in inglese nelle mappe raggiungibili (audit 0.51) -> italiano.
Formato: ¶ = nuova pagina; le righe vanno a capo da sole (max 2 per riquadro). {01}=giocatore, {02}/{03}=variabili."""

DIALOGHI = {
    # --- Centro Pokemon (script comune dell'infermiera, usato dal Centro della Lega)
    0x272d9c: "Grazie per l'attesa.",
    0x272b44: "Grazie per l'attesa.¶I tuoi POKéMON sono di nuovo in piena forma.",
    0x278df4: "Sembra che {02} stia giocando proprio adesso. Vai, buona fortuna!",
    0x2732b3: "I tuoi POKéMON potrebbero avere il POKéRUS.¶Del POKéRUS si sa poco: sono microrganismi che si attaccano ai POKéMON.¶Si dice che i POKéMON che lo hanno crescano molto bene.",
    0x272d2e: "Che piacere vederti, {01}! Il solito, vero?",
    0x272ba1: "Ciao, benvenuto al CENTRO POKéMON.¶Qui facciamo riposare i POKéMON stanchi.¶Vuoi…",
    0x272c0c: "Qu-questa carta… Non sarà la CARTA ORO?!¶Che oro splendente! Le quattro stelle brillano!¶Ho visto tanti ALLENATORI con la CARTA ARGENTO, ma tu, {01},¶sei il primo che vedo con la CARTA ORO!¶Bene, {01}, è un onore curare i tuoi POKéMON!",
    0x272a97: "Ciao, benvenuto al CENTRO POKéMON.¶Qui facciamo riposare i POKéMON stanchi.¶Vuoi far riposare i tuoi POKéMON?",
    0x272dcd: "Benvenuto!¶Come posso aiutarti?",
    0x272deb: "Torna a trovarci!",
    0x229a94: "Da qui in poi passano solo gli ALLENATORI con tutte le MEDAGLIE.¶ALLENATORE, controlliamo che tu abbia tutte le MEDAGLIE.",
    # --- Club Cavo / Club Wireless (piano superiore del Centro della Lega)
    0x278995: "Hai almeno un POKéMON che non può venire con te.",
    0x27341b: "Mi dispiace molto. Il CLUB WIRELESS POKéMON è in manutenzione.",
    0x278d61: "Questa è la SALA UNIONE del CLUB WIRELESS POKéMON.¶Purtroppo l'adattatore wireless non è collegato bene.¶Torna pure quando vuoi.",
    0x2797b9: "Benvenuto nella SALA UNIONE del CLUB WIRELESS POKéMON.¶Qui puoi incontrare altri ALLENATORI, anche persone che non conosci.¶Vuoi entrare nella SALA?",
    0x278cea: "Per entrare nella SALA UNIONE servono almeno due POKéMON.",
    0x278d27: "Nessun POKéMON con la BACCA {02} può entrare nella SALA UNIONE.",
    0x2799c8: "Buon divertimento nella SALA UNIONE!",
    0x279864: "Nella SALA UNIONE trovi i giocatori vicini a te che sono entrati nella SALA.¶Potete salutarvi e fare tante altre cose.¶Puoi lottare uno contro uno con due POKéMON fino al Lv. 30.¶Puoi chattare con due-cinque persone.¶Oppure puoi registrare un POKéMON da scambiare.¶Vuoi entrare nella SALA?",
    0x279ce3: "Ciao, {01}!¶Sono TEALA, l'addetta al primo piano del CENTRO POKéMON.¶Hai bisogno di chiedermi qualcosa sui collegamenti?",
    0x27a03d: "Buon divertimento con il sistema di comunicazione wireless!",
    0x279d56: "Ti spiego come funziona il CLUB WIRELESS POKéMON.¶A questo piano ci sono due sale.¶A sinistra c'è la SALA UNIONE.¶Lì ti colleghi con gli ALLENATORI vicini che sono entrati nella SALA UNIONE.¶Con loro puoi chattare, lottare e scambiare.¶A destra c'è l'ANGOLO DIRETTO.¶Lì puoi scambiare POKéMON o lottare con i tuoi amici.¶A volte non trovi i tuoi amici nella SALA UNIONE o nell'ANGOLO DIRETTO.¶In quel caso, avvicinati a loro.¶Senza adattatore wireless puoi collegarti con il cavo GBA Game Link.¶In quel caso devi andare nell'ANGOLO DIRETTO.¶Buon divertimento con il sistema di comunicazione wireless!",
    0x278250: "Benvenuto al CLUB CAVO POKéMON.¶Quale servizio vuoi usare?",
    0x2783d3: "Per scambiare servono almeno due POKéMON in squadra.",
    0x27840d: "Un POKéMON con la BACCA {02} non può essere scambiato.",
    0x278573: "Qualcuno non è pronto per il collegamento.¶Torna quando tutti sono pronti.",
    0x278601: "Sembra che i giocatori collegati abbiano scelto cose diverse.",
    0x2785c8: "Errore di collegamento… Spegni e riprova.",
    0x278911: "Mi dispiace molto.¶Non possiamo ancora fare scambi con ALLENATORI di regioni lontane…",
    0x27946a: "Quale modalità di lotta vuoi giocare?",
    0x27867d: "La LOTTA IN SINGOLO non si gioca in {02} giocatori.",
    0x27871e: "Controlla il numero di giocatori e ricomincia.",
    0x2786b3: "La LOTTA IN DOPPIO non si gioca in {02} giocatori.",
    0x2786e9: "Per questa modalità servono quattro giocatori.",
    0x2794ee: "Ci sono tre modalità di lotta.¶La LOTTA IN SINGOLO è per due ALLENATORI con almeno un POKéMON ciascuno.¶Ogni ALLENATORE usa un POKéMON alla volta.¶La LOTTA IN DOPPIO è per due ALLENATORI con almeno due POKéMON ciascuno.¶Ogni ALLENATORE manda in campo due POKéMON alla volta.¶La LOTTA MULTIPLA è per quattro ALLENATORI con almeno un POKéMON ciascuno.¶Ogni ALLENATORE usa un POKéMON alla volta.",
    0x27839a: "Per la LOTTA IN DOPPIO servono almeno due POKéMON.",
    0x2789fd: "Errore di trasmissione.¶Non puoi mescolare i record con RUBINO o ZAFFIRO giapponesi.¶Né puoi mescolarli insieme con SMERALDO giapponese e RUBINO o ZAFFIRO esteri.",
    0x2793bf: "Benvenuto nell'ANGOLO DIRETTO del CLUB WIRELESS POKéMON.¶Qui puoi collegarti direttamente con i tuoi amici.¶In quale sala vuoi entrare?",
    0x279449: "Vuoi scambiare POKéMON?",
    0x279679: "Decidete chi di voi due sarà il CAPO.¶L'altro giocatore poi sceglie “UNISCITI”.",
    0x2796e0: "Decidete chi di voi quattro sarà il CAPOGRUPPO.¶Gli altri giocatori poi scelgono “UNISCITI”.",
    0x27974f: "Decidete chi di voi sarà il CAPOGRUPPO.¶Gli altri giocatori poi scelgono “UNISCITI”.",
    0x279494: "Vuoi usare l'ANGOLO RECORD?",
    0x2794c0: "Vuoi usare il sistema SCHIACCIABACCHE?",
    0x278ca8: "Per lo SCHIACCIABACCHE serve almeno una BACCA.",
    0x273524: "Grazie per aver usato il sistema DONO SEGRETO.",
    0x273940: "Grazie per aver usato il sistema EVENTO SEGRETO.¶Tu sei {01}, vero? C'è un biglietto per te.",
    0x27399e: "Sembra che serva al porto di ALGIDOPOLI.¶Perché non provi a scoprire a cosa serve?",
    0x2799f6: "Ciao! Mi chiamo TEALA.¶È la prima volta che sali qui, vero?¶Ti mostro come funziona il sistema di comunicazione wireless.¶Prima ti faccio vedere questo piano del CENTRO POKéMON.¶Da questa parte, prego.",
    0x279ac4: "A questo piano ci sono due sale.¶A sinistra c'è la SALA UNIONE.¶Lì ti colleghi con gli ALLENATORI vicini che sono entrati nella SALA UNIONE.¶Con loro puoi chattare, lottare e scambiare.¶A destra c'è l'ANGOLO DIRETTO.¶Lì puoi scambiare POKéMON o lottare con i tuoi amici.¶Senza adattatore wireless puoi collegarti con il cavo GBA Game Link.¶In quel caso devi andare nell'ANGOLO DIRETTO.¶Buon divertimento con il sistema di comunicazione wireless!",
    0x2788cd: "I dati della SCHEDA ALLENATORE verranno sovrascritti.",
    # --- Pensione
    0x292904: "{01} riprende {02} dalla signora della PENSIONE.",
    0x292515: "{01} riceve l'UOVO dal signore della PENSIONE.",
    # --- Sale del Club
    0x278860: "Prendete posto e iniziate la lotta.",
    0x2789c8: "Prendi posto e attendi, per favore.",
    # --- Alberi di bacche
    0x2748b3: "Terra morbida e fertile. Vuoi piantare una BACCA?",
    0x27490c: "Qui è stata piantata una {02}.",
    0x274a90: "Vuoi innaffiare {02} con l'ANNAFFIATOIO?",
    0x27499a: "Hai trovato {03} {02}!¶Vuoi raccogliere {02}?",
    0x274a3b: "La TASCA BACCHE dello ZAINO è piena.¶Non puoi prendere {02}.",
    0x2749dc: "{01} mette {02} nella TASCA BACCHE dello ZAINO.¶La terra torna morbida e fertile.",
}

# nomi di zona: indice mapsec -> (nome, x, y) (x, y lette dalla ROM se None)
ZONE = {201: 'ISOLA MIRAGGIO', 211: 'ISOLA OMBELICO', 87: 'CLUB CAVO'}
# mappa 22.0 (pensione) -> zona COSTA ADRIATICA (23) invece di "ROUTE 117"
REGIONE_MAPPE = {(22, 0): 23}
