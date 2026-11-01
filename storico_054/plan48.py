"""Piano dei caselli 0.48."""
R = range
def L(xs, ys):
    xs = [xs] if isinstance(xs, int) else list(xs); ys = [ys] if isinstance(ys, int) else list(ys)
    return [(x, y) for x in xs for y in ys]

# nome sul cartello di ogni estremita' (= luogo verso cui porta) e testo del casellante
# id: (nomeA, nomeB, testo)
TXT = {
 'T1': ('PIANURA', 'LIDO SAVIO', 'CASELLANTE: Da una parte il Lido,\ndall\'altra la pianura di Ravenna.'),
 'T2': ('RAVENNA', 'PIANURA', 'CASELLANTE: Ravenna è a due passi.\nOcchio ai Pokémon nell\'erba alta!'),
 'T3': ('PINETA', 'LIDO SAVIO', 'CASELLANTE: La pineta è fresca e piena\ndi Pokémon. Portati le cure.'),
 'T4': ('CERVIA', 'PINETA', 'CASELLANTE: Da qui si esce dalla pineta.\nCervia è subito oltre.'),
 'T5': ('COSTIERO', 'LIDO SAVIO', 'CASELLANTE: Il passaggio costiero segue\nil mare fino a Cervia.'),
 'T6': ('CERVIA', 'COSTIERO', 'CASELLANTE: Cervia è in fondo al passaggio.\nBuon viaggio!'),
 'T7': ('CAMPAGNA', 'CERVIA', 'CASELLANTE: Dalle saline in giù la strada\nporta alla campagna di Cesena.'),
 'T8': ('CESENA', 'CAMPAGNA', 'CASELLANTE: Cesena è oltre i campi.\nI contadini non amano i curiosi!'),
 'T9': ('COSTA ADR.', 'CESENA', 'CASELLANTE: Questa strada scende al mare,\nverso Cesenatico.'),
 'T10': ('CESENATICO', 'COSTA ADR.', 'CASELLANTE: Cesenatico! Si sente già\nl\'odore del porto canale.'),
 'T11': ('RIVIERA', 'CESENATICO', 'CASELLANTE: La riviera porta fino a Rimini.\nTieni d\'occhio gli altri allenatori.'),
 'T12': ('RIMINI', 'RIVIERA', 'CASELLANTE: Rimini è in fondo alla riviera.\nChe sia ora di un bagno?'),
 'T13': ('M. SPACCATO', 'CESENA', 'CASELLANTE: A ovest di Cesena i colli\nsi fanno ripidi. Occhio ai sassi.'),
 'T14': ('CAPOCOLLE', 'M. SPACCATO', 'CASELLANTE: Di là c\'è Capocolle,\nla strada per Babbi è ancora lunga.'),
 'T15': ('FORLIMPOPOLI', 'CAPOCOLLE', 'CASELLANTE: Forlimpopoli è vicina.\nSi sente già l\'odore di piadina.'),
 'T16': ('VIA EMILIA', 'FORLIMPOPOLI', 'CASELLANTE: Da qui parte la via Emilia\nverso Forlì. Tutta dritta!'),
 'T17': ('FORLI', 'VIA EMILIA', 'CASELLANTE: Forlì è subito oltre.\nLa città ha più di una sorpresa.'),
 'T18': ('CAMPAGNA', 'FORLI', 'CASELLANTE: Dopo Forlì la campagna scende\nverso Faenza, lungo il fiume.'),
 'T19': ('FAENZA', 'CAMPAGNA', 'CASELLANTE: Faenza, città della ceramica!\nOcchio al team Emilia.'),
 'T20': ('V. CANALI', 'RAVENNA', 'CASELLANTE: Questa è la via dei canali,\nporta alle campagne di Lugo.'),
 'T21': ('CAMPAGNE', 'V. CANALI', 'CASELLANTE: Lugo è oltre le campagne.\nFatti furbo con i canali.'),
}
