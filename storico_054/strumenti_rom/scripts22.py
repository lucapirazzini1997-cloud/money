"""Event scripts added in Romagna 0.22 (assembled with the decomp macros)."""

# free flags (verified unused in 0.21)
FLAG = dict(bike=0x4DA, torkoal=0x4DB, snorlax=0x4DC, aie_quest=0x4DD, quiz_seen=0x4DE, cheat_warned=0x4DF)
TRAINERS_AIE = [790, 791, 792, 793, 794]

HEAD = r'''
	.set M_GRATT1F, (34 << 8) | 34
	.set M_FARAWAY, (26 << 8) | 56
	.set M_LIDO, (0 << 8) | 9
	.set M_VISTA, (35 << 8) | 39
	.set M_ROOF, (34 << 8) | 38
	.set M_RAVSEA, (35 << 8) | 40
	.set M_MOON, (35 << 8) | 41
	.set M_WISH, (35 << 8) | 42
	.set M_CERVIA, (0 << 8) | 10
	.set M_RAVENNA, (34 << 8) | 96
	.set M_NAVEL, (26 << 8) | 67
	.set M_GROTTA, (35 << 8) | 43
	.set M_CESENATICO, (34 << 8) | 22
	.set FLAG_R22_BIKE, 0x4DA
	.set FLAG_R22_TORKOAL, 0x4DB
	.set FLAG_R22_SNORLAX, 0x4DC
	.set FLAG_R22_KEYS, 0x4E8
	.set FLAG_R22_KYOGRE_HIDE, 0x4E0
	.set FLAG_R22_KYOGRE, 0x4E1
	.set FLAG_R22_RAYQ_HIDE, 0x4E2
	.set FLAG_R22_RAYQ, 0x4E3
	.set FLAG_R22_CELEBI, 0x4E4
	.set FLAG_R22_GSBALL, 0x4E5
	.set FLAG_R22_DIVE, 0x4E6
	.set FLAG_R22_STONES, 0x4E7
	.set FLAG_R22_RIVAL3, 0x4E9
	.set FLAG_R22_JIRA, 0x4EA
	.set FLAG_R22_DEOX, 0x4EB
	.set FLAG_R22_GATES_HIDE, 0x4EE
	.set FLAG_R22_MEWTWO, 0x4EF
	.set ITEM_GS_BALL, ITEM_MYSTIC_TICKET
'''

SRC = r'''
@ ---------------------------------------------------------------- generic
	.align 2
R22_LockedDoor::
	msgbox R22_Text_Locked, MSGBOX_SIGN
	end
R22_Text_Locked:
	.string "La porta è chiusa a chiave.$"

@ ---------------------------------------------------------------- fly: visited towns follow story progress
	.align 2
R22_FlyGuard::
	goto_if_unset FLAG_BADGE01_GET, R22_FG_1
	setflag FLAG_VISITED_LITTLEROOT_TOWN
	setflag FLAG_VISITED_OLDALE_TOWN
R22_FG_1:
	goto_if_unset FLAG_BADGE02_GET, R22_FG_2
	setflag FLAG_VISITED_PETALBURG_CITY
R22_FG_2:
	goto_if_unset FLAG_BADGE03_GET, R22_FG_3
	setflag FLAG_VISITED_PACIFIDLOG_TOWN
	setflag FLAG_VISITED_SLATEPORT_CITY
R22_FG_3:
	goto_if_unset FLAG_BADGE04_GET, R22_FG_4
	setflag FLAG_VISITED_MAUVILLE_CITY
R22_FG_4:
	goto_if_unset FLAG_BADGE05_GET, R22_FG_5
	setflag FLAG_VISITED_FALLARBOR_TOWN
R22_FG_5:
	goto_if_unset FLAG_BADGE06_GET, R22_FG_6
	setflag FLAG_VISITED_FORTREE_CITY
	setflag FLAG_VISITED_DEWFORD_TOWN
R22_FG_6:
	goto_if_unset FLAG_BADGE07_GET, R22_FG_7
	setflag FLAG_VISITED_LAVARIDGE_TOWN
	setflag 0x4D9
R22_FG_7:
	goto_if_unset FLAG_BADGE08_GET, R22_FG_8
	setflag FLAG_VISITED_RUSTBORO_CITY
	setflag 0x4D7
R22_FG_8:
	@ story guards of 0.21 (Imola, Bagno, Lega)
	goto_if_unset FLAG_BADGE06_GET, R22_FG_ClrImola
	goto_if_unset 0x4D9, R22_FG_ClrImola
	goto R22_FG_Bagno
R22_FG_ClrImola:
	clearflag FLAG_VISITED_LAVARIDGE_TOWN
R22_FG_Bagno:
	goto_if_unset 0x4CB, R22_FG_ClrBagno
	goto_if_unset 0x4D7, R22_FG_ClrBagno
	goto R22_FG_League
R22_FG_ClrBagno:
	clearflag FLAG_VISITED_RUSTBORO_CITY
R22_FG_League:
	goto_if_unset 0x4D8, R22_FG_ClrLeague
	goto_if_unset FLAG_BADGE08_GET, R22_FG_ClrLeague
	goto R22_FG_Hoenn
R22_FG_ClrLeague:
	clearflag FLAG_VISITED_EVER_GRANDE_CITY
R22_FG_Hoenn:
	@ Hoenn towns that are not part of Romagna never appear on the fly map
	clearflag FLAG_VISITED_VERDANTURF_TOWN
	clearflag FLAG_VISITED_LILYCOVE_CITY
	clearflag FLAG_VISITED_MOSSDEEP_CITY
	clearflag FLAG_VISITED_SOOTOPOLIS_CITY
	@ legendary Pokémon appear only when the story allows it
	setflag FLAG_R22_KYOGRE_HIDE
	goto_if_unset FLAG_BADGE08_GET, R22_FG_Rayq
	goto_if_set FLAG_R22_KYOGRE, R22_FG_Rayq
	clearflag FLAG_R22_KYOGRE_HIDE
R22_FG_Rayq:
	setflag FLAG_R22_RAYQ_HIDE
	setflag FLAG_R22_GATES_HIDE
	goto_if_unset FLAG_SYS_GAME_CLEAR, R22_FG_End
	clearflag FLAG_R22_GATES_HIDE
	goto_if_set FLAG_R22_RAYQ, R22_FG_End
	clearflag FLAG_R22_RAYQ_HIDE
R22_FG_End:
	return

@ ---------------------------------------------------------------- cheater room warning
	.align 2
R22_Cheater::
	lock
	faceplayer
	msgbox R22_Text_CheatWarn, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, R22_Cheater_No
	release
	goto 0x082d8126
R22_Cheater_No:
	msgbox R22_Text_CheatNo, MSGBOX_DEFAULT
	release
	end
R22_Text_CheatWarn:
	.string "ATTENZIONE! Questa è la STANZA CHEATER.\n"
	.string "Il venditore regala 999 MASTER BALL\l"
	.string "e 999 CARAMELLE RARE.\p"
	.string "Usarle rovina l'equilibrio del gioco.\n"
	.string "Vuoi davvero parlargli?$"
R22_Text_CheatNo:
	.string "Saggia scelta! L'avventura è più bella\n"
	.string "senza scorciatoie.$"

	.align 2
R22_CheaterDoorWarn::
	lockall
	setvar VAR_TEMP_1, 1
	msgbox R22_Text_CheatDoor, MSGBOX_DEFAULT
	releaseall
	end
R22_Text_CheatDoor:
	.string "Attenzione: la porta rossa è la\n"
	.string "STANZA CHEATER!\p"
	.string "Dentro c'è un venditore che regala\n"
	.string "MASTER BALL e CARAMELLE RARE.\l"
	.string "Entra solo se vuoi barare!$"

@ ---------------------------------------------------------------- Cesenatico: skyscraper door
	.align 2
R22_GrattDoor::
	lockall
	goto_if_set FLAG_R22_KEYS, R22_GrattDoor_Open
	msgbox R22_Text_GrattLocked, MSGBOX_DEFAULT
	releaseall
	end
R22_GrattDoor_Open:
	msgbox R22_Text_GrattOpen, MSGBOX_DEFAULT
	playse SE_DOOR
	waitse
	warp M_GRATT1F, 0
	waitstate
	releaseall
	end
R22_Text_GrattLocked:
	.string "GRATTACIELO DI CESENATICO.\n"
	.string "La porta è chiusa a chiave.\p"
	.string "Le chiavi le custodisce la CURATRICE\n"
	.string "del MUSEO DELLA MARINERIA.$"
R22_Text_GrattOpen:
	.string "Usi le CHIAVI DEL GRATTACIELO.\n"
	.string "La serratura scatta!$"

@ ---------------------------------------------------------------- ferris wheel quiz -> racing bike
	.align 2
R22_RuotaQuiz::
	lock
	faceplayer
	goto_if_set FLAG_R22_BIKE, R22_Ruota_Done
	msgbox R22_Text_RuotaIntro, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, R22_Ruota_Later
	msgbox R22_Text_Q1, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, R22_Ruota_Wrong
	msgbox R22_Text_Q2, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, R22_Ruota_Wrong
	msgbox R22_Text_Q3, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, R22_Ruota_Wrong
	msgbox R22_Text_RuotaWin, MSGBOX_DEFAULT
	giveitem ITEM_MACH_BIKE
	setflag FLAG_R22_BIKE
	msgbox R22_Text_RuotaBike, MSGBOX_DEFAULT
	release
	end
R22_Ruota_Wrong:
	msgbox R22_Text_RuotaWrong, MSGBOX_DEFAULT
	release
	end
R22_Ruota_Later:
	msgbox R22_Text_RuotaLater, MSGBOX_DEFAULT
	release
	end
R22_Ruota_Done:
	msgbox R22_Text_RuotaBike, MSGBOX_DEFAULT
	release
	end
R22_Text_RuotaIntro:
	.string "Benvenuto sulla RUOTA PANORAMICA!\n"
	.string "Da quassù si vede tutta la Romagna.\p"
	.string "Rispondi giusto a tre domande sulla\n"
	.string "nostra terra e ti regalo la mia\l"
	.string "BICI DA CORSA. Ci stai?$"
R22_Text_Q1:
	.string "Prima domanda! Il regista Federico\n"
	.string "Fellini è nato a Rimini. È vero?$"
R22_Text_Q2:
	.string "Seconda domanda! Il porto canale di\n"
	.string "Cesenatico è opera di Michelangelo?$"
R22_Text_Q3:
	.string "Ultima domanda! Dante Alighieri\n"
	.string "riposa a Ravenna. È vero?$"
R22_Text_RuotaWin:
	.string "Tre risposte esatte! Sei un vero\n"
	.string "romagnolo. Ecco il premio!$"
R22_Text_RuotaBike:
	.string "La BICI DA CORSA è leggera e veloce:\n"
	.string "registrala con SELECT e pedala lungo\l"
	.string "la riviera!$"
R22_Text_RuotaWrong:
	.string "Peccato, risposta sbagliata!\n"
	.string "Fai un altro giro e ripassa da me.$"
R22_Text_RuotaLater:
	.string "Va bene, goditi il panorama!$"

@ ---------------------------------------------------------------- shiny Torkoal at the end of the Rocca maze
	.align 2
R22_Torkoal::
	lock
	faceplayer
	msgbox R22_Text_TorkoalSee, MSGBOX_DEFAULT
	setvar VAR_0x8004, SPECIES_TORKOAL
	setvar VAR_0x8005, 30
	playmoncry SPECIES_TORKOAL, CRY_MODE_ENCOUNTER
	waitmoncry
	setwildbattle SPECIES_TORKOAL, 30
	callnative R22_ShinyWild
	setflag FLAG_SYS_CTRL_OBJ_DELETE
	dowildbattle
	clearflag FLAG_SYS_CTRL_OBJ_DELETE
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, R22_Torkoal_Caught
	msgbox R22_Text_TorkoalStay, MSGBOX_DEFAULT
	release
	end
R22_Torkoal_Caught:
	setflag FLAG_R22_TORKOAL
	removeobject VAR_LAST_TALKED
	release
	end
@ ---------------------------------------------------------------- legendaries
	.macro r22_legend label, species, level, flag, see, stay
	.align 2
	.global \label
\label\():
	lock
	faceplayer
	msgbox \see, MSGBOX_DEFAULT
	playmoncry \species, CRY_MODE_ENCOUNTER
	waitmoncry
	setwildbattle \species, \level
	setflag FLAG_SYS_CTRL_OBJ_DELETE
	dowildbattle
	clearflag FLAG_SYS_CTRL_OBJ_DELETE
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, \label\()_Caught
	msgbox \stay, MSGBOX_DEFAULT
	release
	end
\label\()_Caught:
	setflag \flag
	removeobject VAR_LAST_TALKED
	release
	end
	.endm

	r22_legend R22_Kyogre, SPECIES_KYOGRE, 70, FLAG_R22_KYOGRE, R22_Text_KyogreSee, R22_Text_KyogreStay
	r22_legend R22_Rayquaza, SPECIES_RAYQUAZA, 70, FLAG_R22_RAYQ, R22_Text_RayqSee, R22_Text_RayqStay
	r22_legend R22_Jirachi, SPECIES_JIRACHI, 50, FLAG_R22_JIRA, R22_Text_JiraSee, R22_Text_JiraStay
	r22_legend R22_Deoxys, SPECIES_DEOXYS, 50, FLAG_R22_DEOX, R22_Text_DeoxSee, R22_Text_DeoxStay
	r22_legend R22_Mewtwo, SPECIES_MEWTWO, 70, FLAG_R22_MEWTWO, R22_Text_M2See, R22_Text_M2Stay

R22_Text_M2See:
	.string "In fondo alla grotta, tra i cristalli,\n"
	.string "ti fissa uno sguardo gelido...\p"
	.string "MEWTWO attacca!$"
R22_Text_M2Stay:
	.string "MEWTWO si ritira tra i cristalli.\n"
	.string "Puoi riprovare.$"
R22_CaveDoor::
	lockall
	goto_if_unset FLAG_SYS_GAME_CLEAR, R22_CaveDoor_No
	msgbox R22_Text_Cave1, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, R22_CaveDoor_End
	closemessage
	fadescreen FADE_TO_BLACK
	warp M_GROTTA, 12, 20
	waitstate
R22_CaveDoor_End:
	releaseall
	end
R22_CaveDoor_No:
	msgbox R22_Text_Cave0, MSGBOX_DEFAULT
	releaseall
	end
R22_Motonave::
	lock
	faceplayer
	goto_if_unset FLAG_SYS_GAME_CLEAR, R22_Mn_No
	msgbox R22_Text_Mn1, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, R22_Mn_Bye
	msgbox R22_Text_MB_Go, MSGBOX_DEFAULT
	closemessage
	warp M_NAVEL, 8, 4
	waitstate
	release
	end
R22_Mn_No:
	msgbox R22_Text_Mn0, MSGBOX_DEFAULT
	release
	end
R22_Mn_Bye:
	msgbox R22_Text_MB_Bye, MSGBOX_DEFAULT
	release
	end
R22_MotonaveBack::
	lock
	faceplayer
	msgbox R22_Text_Mn2, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, R22_Mn_Bye
	msgbox R22_Text_MB_Go, MSGBOX_DEFAULT
	closemessage
	warp M_RAVENNA, 66, 45
	waitstate
	release
	end
R22_Text_Cave0:
	.string "L'ingresso della grotta è sbarrato\n"
	.string "da massi e onde altissime.\p"
	.string "I pescatori dicono che solo un\n"
	.string "CAMPIONE può entrarci.$"
R22_Text_Cave1:
	.string "Le onde si sono calmate. Dalla grotta\n"
	.string "arriva una luce violacea...\p"
	.string "Vuoi entrare?$"
R22_Text_Mn0:
	.string "Questa è la MOTONAVE per le isole\n"
	.string "leggendarie dell'Adriatico.\p"
	.string "Imbarchiamo solo il CAMPIONE della\n"
	.string "LEGA POKéMON!$"
R22_Text_Mn1:
	.string "CAMPIONE! La MOTONAVE è pronta.\p"
	.string "Si va all'ISOLA OMBELICO, dove\n"
	.string "riposano LUGIA e HO-OH. Partiamo?$"
R22_Text_Mn2:
	.string "Torniamo al porto di RAVENNA?$"

R22_Text_JiraSee:
	.string "Sulla STELLA DEI DESIDERI dorme un\n"
	.string "piccolo Pokémon. Si sveglia e sorride:\p"
	.string "è JIRACHI!$"
R22_Text_JiraStay:
	.string "JIRACHI torna a dormire sulla stella.\n"
	.string "Puoi riprovare.$"
R22_Text_DeoxSee:
	.string "Tra i crateri brilla un cristallo...\n"
	.string "DEOXYS prende forma davanti a te!$"
R22_Text_DeoxStay:
	.string "DEOXYS fluttua immobile tra i crateri.\n"
	.string "Puoi riprovare.$"

R22_WishPortal::
	lock
	msgbox R22_Text_WP, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, R22_WP_End
	closemessage
	playse SE_WARP_IN
	fadescreen FADE_TO_WHITE
	warp M_WISH, 14, 17
	waitstate
R22_WP_End:
	release
	end
R22_WishReturn::
	lock
	msgbox R22_Text_WR, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, R22_WP_End
	closemessage
	playse SE_WARP_OUT
	fadescreen FADE_TO_WHITE
	warp M_CERVIA, 54, 22
	waitstate
	release
	end
R22_Rocket::
	lockall
	goto_if_unset FLAG_SYS_GAME_CLEAR, R22_Rocket_No
	msgbox R22_Text_Rk1, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, R22_Rocket_End
	msgbox R22_Text_Rk2, MSGBOX_DEFAULT
	closemessage
	playse SE_M_EXPLOSION
	fadescreen FADE_TO_WHITE
	warp M_MOON, 6, 10
	waitstate
R22_Rocket_End:
	releaseall
	end
R22_Rocket_No:
	msgbox R22_Text_Rk0, MSGBOX_DEFAULT
	releaseall
	end
R22_RocketBack::
	lockall
	msgbox R22_Text_Rk3, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, R22_Rocket_End
	closemessage
	playse SE_M_EXPLOSION
	fadescreen FADE_TO_WHITE
	warp M_RAVENNA, 62, 45
	waitstate
	releaseall
	end
R22_Text_WP:
	.string "Sull'acqua gira un vortice di stelle.\n"
	.string "È un portale per il MONDO DEI DESIDERI!\p"
	.string "Vuoi attraversarlo?$"
R22_Text_WR:
	.string "Il portale riporta al mare di CERVIA.\n"
	.string "Vuoi tornare indietro?$"
R22_Text_Rk0:
	.string "RAZZO ROMAGNA-1\n"
	.string "Pronto al lancio, ma il volo è\l"
	.string "riservato al CAMPIONE della LEGA.$"
R22_Text_Rk1:
	.string "RAZZO ROMAGNA-1: tutto pronto!\n"
	.string "Vuoi partire per la LUNA?$"
R22_Text_Rk2:
	.string "3... 2... 1... Lancio!$"
R22_Text_Rk3:
	.string "Il razzo è pronto per il rientro.\n"
	.string "Vuoi tornare a RAVENNA?$"

R22_Text_KyogreSee:
	.string "Tra i piloni spezzati dell'ISOLA DELLE\n"
	.string "ROSE dorme un Pokémon gigantesco...\p"
	.string "KYOGRE apre gli occhi!$"
R22_Text_KyogreStay:
	.string "KYOGRE si riadagia sul fondale.\n"
	.string "Puoi tornare a sfidarlo.$"
R22_Text_RayqSee:
	.string "Sopra il monumento a BARACCA il vento\n"
	.string "ruggisce. RAYQUAZA scende dal cielo!$"
R22_Text_RayqStay:
	.string "RAYQUAZA torna a volteggiare sopra\n"
	.string "LUGO. Puoi riprovare.$"

@ ---------------------------------------------------------------- Celebi shrine (Pineta di Savio)
	.align 2
R22_CelebiShrine::
	lockall
	goto_if_set FLAG_R22_CELEBI, R22_Shrine_Quiet
	checkitem ITEM_GS_BALL, 1
	goto_if_eq VAR_RESULT, FALSE, R22_Shrine_Plain
	msgbox R22_Text_ShrineBall, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, R22_Shrine_End
	msgbox R22_Text_ShrineGlow, MSGBOX_DEFAULT
	playmoncry SPECIES_CELEBI, CRY_MODE_ENCOUNTER
	waitmoncry
	setwildbattle SPECIES_CELEBI, 50
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, R22_Shrine_Caught
	msgbox R22_Text_ShrineFled, MSGBOX_DEFAULT
	releaseall
	end
R22_Shrine_Caught:
	setflag FLAG_R22_CELEBI
	removeitem ITEM_GS_BALL
	msgbox R22_Text_ShrineAfter, MSGBOX_DEFAULT
	releaseall
	end
R22_Shrine_Plain:
	msgbox R22_Text_ShrinePlain, MSGBOX_DEFAULT
R22_Shrine_End:
	releaseall
	end
R22_Shrine_Quiet:
	msgbox R22_Text_ShrineAfter, MSGBOX_DEFAULT
	releaseall
	end
R22_Text_ShrinePlain:
	.string "Un piccolo santuario di legno tra i\n"
	.string "pini. Al centro c'è un incavo rotondo,\l"
	.string "grande come una POKé BALL.$"
R22_Text_ShrineBall:
	.string "La GS BALL vibra nello Zaino...\n"
	.string "Vuoi posarla nel santuario?$"
R22_Text_ShrineGlow:
	.string "La GS BALL si illumina!\n"
	.string "Il bosco diventa silenzioso...\p"
	.string "Un Pokémon compare dal tempo!$"
R22_Text_ShrineFled:
	.string "CELEBI svanisce tra i pini.\n"
	.string "La GS BALL è ancora con te.$"
R22_Text_ShrineAfter:
	.string "Il santuario della pineta è tornato\n"
	.string "tranquillo. Il vento profuma di resina.$"

@ ---------------------------------------------------------------- Prof. Pino gives the GS Ball after the League
	.align 2
R22_ProfPino::
	goto_if_unset FLAG_SYS_GAME_CLEAR, R22_Prof_Orig
	goto_if_set FLAG_R22_GSBALL, R22_Prof_Orig
	lock
	faceplayer
	msgbox R22_Text_ProfGS, MSGBOX_DEFAULT
	giveitem ITEM_GS_BALL
	goto_if_eq VAR_RESULT, FALSE, R22_Prof_Full
	setflag FLAG_R22_GSBALL
	msgbox R22_Text_ProfGS2, MSGBOX_DEFAULT
	release
	end
R22_Prof_Full:
	release
	end
R22_Prof_Orig:
	goto R22_PROF_ORIG_ADDR
R22_Text_ProfGS:
	.string "PROF. PINO: Campione della ROMAGNA!\n"
	.string "Sono fiero di te.\p"
	.string "Un pescatore ha trovato questa sfera\n"
	.string "dorata nella pineta: la GS BALL.$"
R22_Text_ProfGS2:
	.string "Nella PINETA DI SAVIO c'è un vecchio\n"
	.string "santuario di legno. Dicono che la\l"
	.string "GS BALL risvegli chi lo custodisce.$"

@ ---------------------------------------------------------------- HM Dive after the eighth badge
	.align 2
R22_DiveGiver::
	lock
	faceplayer
	goto_if_set FLAG_R22_DIVE, R22_Dive_After
	goto_if_unset FLAG_BADGE08_GET, R22_Dive_Before
	msgbox R22_Text_Dive1, MSGBOX_DEFAULT
	giveitem ITEM_HM08
	setflag FLAG_R22_DIVE
R22_Dive_After:
	msgbox R22_Text_Dive2, MSGBOX_DEFAULT
	release
	end
R22_Dive_Before:
	msgbox R22_Text_Dive0, MSGBOX_DEFAULT
	release
	end
R22_Text_Dive0:
	.string "Sono un sommozzatore della riviera.\n"
	.string "Batti LEDA e ti insegnerò a scendere\l"
	.string "sul fondo del mare.$"
R22_Text_Dive1:
	.string "Hai l'ottava medaglia! Allora sei\n"
	.string "pronto per il mare aperto.$"
R22_Text_Dive2:
	.string "Con SUB puoi immergerti nelle acque\n"
	.string "scure. Al largo di RIMINI ci sono i\l"
	.string "resti dell'ISOLA DELLE ROSE...\p"
	.string "I pescatori dicono che laggiù dorme\n"
	.string "un Pokémon enorme.$"

@ ---------------------------------------------------------------- Isola delle Rose
	.align 2
R22_RoseGuide::
	msgbox R22_Text_RoseGuide, MSGBOX_NPC
	end
R22_Text_RoseGuide:
	.string "Benvenuto sull'ISOLA DELLE ROSE!\n"
	.string "L'ingegner GIORGIO ROSA la costruì\l"
	.string "a 11 km da RIMINI, nel 1967.\p"
	.string "Era una piattaforma d'acciaio di 400\n"
	.string "metri quadri: nel 1968 si dichiarò\l"
	.string "repubblica indipendente!\p"
	.string "L'anno dopo la Marina la fece saltare.\n"
	.string "Questa è una ricostruzione: i resti\l"
	.string "veri sono sul fondale, qui sotto.$"
R22_Text_TorkoalSee:
	.string "Un TORKOAL dal guscio dorato sbuffa\n"
	.string "fumo in fondo al labirinto!$"
R22_Text_TorkoalStay:
	.string "Il TORKOAL dorato si accuccia di nuovo\n"
	.string "nel suo angolo. Puoi riprovare.$"

@ ---------------------------------------------------------------- Casa delle Aie: host gives shiny Snorlax
	.align 2
R22_AieOste::
	lock
	faceplayer
	goto_if_set FLAG_R22_SNORLAX, R22_Aie_After
	goto_if_unset 0x500 + 790, R22_Aie_Busy
	goto_if_unset 0x500 + 791, R22_Aie_Busy
	goto_if_unset 0x500 + 792, R22_Aie_Busy
	goto_if_unset 0x500 + 793, R22_Aie_Busy
	goto_if_unset 0x500 + 794, R22_Aie_Busy
	msgbox R22_Text_AieWin, MSGBOX_DEFAULT
	setvar VAR_0x8004, SPECIES_SNORLAX
	setvar VAR_0x8005, 20
	setvar VAR_0x8006, 143
	callnative R22_ShinyGift
	goto_if_eq VAR_RESULT, 2, R22_Aie_Full
	playfanfare MUS_OBTAIN_ITEM
	message R22_Text_AieGot
	waitmessage
	waitfanfare
	setflag FLAG_R22_SNORLAX
	msgbox R22_Text_AieAfter, MSGBOX_DEFAULT
	release
	end
R22_Aie_Full:
	msgbox R22_Text_AieFull, MSGBOX_DEFAULT
	release
	end
R22_Aie_Busy:
	msgbox R22_Text_AieBusy, MSGBOX_DEFAULT
	release
	end
R22_Aie_After:
	msgbox R22_Text_AieAfter, MSGBOX_DEFAULT
	release
	end
R22_Text_AieBusy:
	.string "OSTE: Benvenuto alla CASA DELLE AIE!\n"
	.string "Qui si mangia come una volta.\p"
	.string "Ai tavoli ci sono cinque allenatori\n"
	.string "che non si alzano finché non perdono.\p"
	.string "Battili tutti e ti darò il mio\n"
	.string "ospite più pigro e più raro!$"
R22_Text_AieWin:
	.string "OSTE: Hai battuto tutti i miei\n"
	.string "clienti! Te lo sei meritato.\p"
	.string "Questo SNORLAX dorme qui da anni e\n"
	.string "mangia più piadine di tutta Cervia.\l"
	.string "Portalo con te!$"
R22_Text_AieGot:
	.string "{PLAYER} ha ricevuto uno SNORLAX\n"
	.string "dal colore raro!$"
R22_Text_AieAfter:
	.string "OSTE: Trattalo bene, quello SNORLAX.\n"
	.string "E torna per un piatto di cappelletti!$"
R22_Text_AieFull:
	.string "OSTE: Non hai più posto per lui...\n"
	.string "Libera un posto nel PC e torna.$"
R22_RoccaGuide::
	lock
	faceplayer
	msgbox R22_Text_RoccaGuide, MSGBOX_DEFAULT
	release
	end
R22_Text_RoccaGuide:
	.string "Benvenuto nella ROCCA MALATESTIANA!\p"
	.string "Il grande portone in fondo alla sala\n"
	.string "dà sul PARCO DELLA ROCCA.\p"
	.string "Gli antichi raccontavano di una forza\n"
	.string "dormiente in fondo al labirinto...$"

R22_MiraggioBoat::
	lock
	faceplayer
	goto_if_unset FLAG_SYS_GAME_CLEAR, R22_MB_No
	msgbox R22_Text_MB_Ask, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, R22_MB_Bye
	msgbox R22_Text_MB_Go, MSGBOX_DEFAULT
	closemessage
	warp M_FARAWAY, 13, 38
	waitstate
	release
	end
R22_MB_No:
	msgbox R22_Text_MB_No, MSGBOX_DEFAULT
	release
	end
R22_MB_Bye:
	msgbox R22_Text_MB_Bye, MSGBOX_DEFAULT
	release
	end
R22_MiraggioReturn::
	lock
	faceplayer
	msgbox R22_Text_MR_Ask, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, R22_MB_Bye
	msgbox R22_Text_MB_Go, MSGBOX_DEFAULT
	closemessage
	warp M_LIDO, 50, 34
	waitstate
	release
	end
R22_Text_MB_No:
	.string "Nelle giornate limpide, al largo,\n"
	.string "appare un'isola che sparisce subito.\p"
	.string "La chiamano ISOLA MIRAGGIO.\n"
	.string "Dicono che solo i CAMPIONI\l"
	.string "riescano a raggiungerla...$"
R22_Text_MB_Ask:
	.string "Oh, sei il CAMPIONE della ROMAGNA!\p"
	.string "Oggi l'ISOLA MIRAGGIO si vede\n"
	.string "benissimo. Ti ci porto in barca?$"
R22_Text_MB_Go:
	.string "Si salpa! Tieniti forte!$"
R22_Text_MB_Bye:
	.string "Quando vuoi, sono qui.$"
R22_Text_MR_Ask:
	.string "Si dice che nell'erba dell'isola\n"
	.string "si nasconda un POKéMON rosa...\p"
	.string "Torniamo a LIDO DI SAVIO?$"

R22_Cannocchiale::
	lockall
	msgbox R22_Text_Cann1, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, R22_Cann_End
	closemessage
	playse SE_PIN
	fadescreen FADE_TO_BLACK
	warpsilent M_VISTA, 11, 9
	waitstate
R22_Cann_End:
	releaseall
	end
R22_VistaFrame::
	lockall
	setvar VAR_TEMP_0, 1
	hideobjectat 0xFF, M_VISTA
	delay 40
	msgbox R22_Text_Cann2, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	warpsilent M_ROOF, 2, 9
	waitstate
	releaseall
	end
R22_Text_Cann1:
	.string "CANNOCCHIALE PANORAMICO\n"
	.string "Puntato verso l'entroterra.\p"
	.string "Vuoi guardare?$"
R22_Text_Cann2:
	.string "Laggiù, sul colle Garampo,\n"
	.string "svetta la ROCCA MALATESTIANA\l"
	.string "di CESENA!\p"
	.string "Si vedono le mura, il mastio e\n"
	.string "il parco con il grande labirinto.$"

R22_RivalRiviera::
	goto_if_set FLAG_R22_RIVAL3, R22_RR_End
	goto_if_unset FLAG_BADGE02_GET, R22_RR_End
	lockall
	playbgm MUS_ENCOUNTER_BRENDAN, FALSE
	applymovement OBJ_EVENT_ID_PLAYER, R22_Mv_FaceRight
	applymovement 3, R22_Mv_FaceLeft
	waitmovement 0
	msgbox R22_Text_RR1, MSGBOX_DEFAULT
	goto_if_eq VAR_STARTER_MON, 0, R22_RR_B0
	goto_if_eq VAR_STARTER_MON, 1, R22_RR_B1
	trainerbattle_no_intro 624, R22_Text_RRLose
	goto R22_RR_After
R22_RR_B0:
	trainerbattle_no_intro 622, R22_Text_RRLose
	goto R22_RR_After
R22_RR_B1:
	trainerbattle_no_intro 623, R22_Text_RRLose
R22_RR_After:
	msgbox R22_Text_RR2, MSGBOX_DEFAULT
	closemessage
	setflag FLAG_R22_RIVAL3
	fadescreen FADE_TO_BLACK
	removeobject 3
	fadescreen FADE_FROM_BLACK
	savebgm MUS_DUMMY
	fadedefaultbgm
	releaseall
R22_RR_End:
	end
R22_RivalTalk::
	lock
	faceplayer
	msgbox R22_Text_RR0, MSGBOX_DEFAULT
	release
	end
R22_Mv_FaceRight:
	face_right
	step_end
R22_Mv_FaceLeft:
	face_left
	step_end
R22_Text_RR0:
	.string "ALDO: Ti aspetto qui! Prima vinci\n"
	.string "la MEDAGLIA COLLINA a CESENA!$"
R22_Text_RR1:
	.string "ALDO: Eccoti! Ho visto che hai\n"
	.string "vinto la MEDAGLIA COLLINA!\p"
	.string "Prima di arrivare a RIMINI voglio\n"
	.string "vedere quanto sei cresciuto.\p"
	.string "Non ti lascio passare senza\n"
	.string "una lotta!$"
R22_Text_RRLose:
	.string "ALDO: Accidenti!\n"
	.string "Sei diventato fortissimo!$"
R22_Text_RR2:
	.string "ALDO: Va bene, la strada è tua.\p"
	.string "A RIMINI c'è la prossima palestra.\n"
	.string "Ci rivedremo, e allora vincerò io!$"

R22_HomePC::
	lockall
	setvar VAR_0x8004, 1
	special DoPCTurnOnEffect
	playse SE_PC_ON
	msgbox R22_Text_HomePC, MSGBOX_DEFAULT
	special PlayerPC
	waitstate
	releaseall
	end
R22_Text_HomePC:
	.string "{PLAYER} accende il PC.$"

R22_TorreStones::
	lock
	faceplayer
	goto_if_set 0x3B, R22_TS_Extra
	msgbox R22_Text_TS1, MSGBOX_DEFAULT
	giveitem ITEM_WATER_STONE
	goto_if_eq VAR_RESULT, FALSE, R22_TS_End
	setflag 0x3B
R22_TS_Extra:
	goto_if_set FLAG_R22_STONES, R22_TS_After
	msgbox R22_Text_TS2, MSGBOX_DEFAULT
	giveitem ITEM_FIRE_STONE
	goto_if_eq VAR_RESULT, FALSE, R22_TS_End
	giveitem ITEM_THUNDER_STONE
	goto_if_eq VAR_RESULT, FALSE, R22_TS_End
	setflag FLAG_R22_STONES
R22_TS_After:
	msgbox R22_Text_TS3, MSGBOX_DEFAULT
R22_TS_End:
	release
	end
R22_Text_TS1:
	.string "Queste vibrazioni arrivano\n"
	.string "dall'Appennino, non dal mare.\p"
	.string "Il TEAM EMILIA cerca qualcosa\n"
	.string "sotto le montagne...\p"
	.string "Dalla TORRE ho raccolto tre campioni.\n"
	.string "Sono tuoi!$"
R22_Text_TS2:
	.string "Prendi anche queste due pietre:\n"
	.string "il fuoco delle saline al tramonto\l"
	.string "e il tuono dei temporali sul mare.$"
R22_Text_TS3:
	.string "Avviserò la stazione di ricerca.\n"
	.string "La prossima pista porta a Cesena.$"

'''


def aie_trainer_scripts():
    """Battle scripts for the five patrons. Returns asm text."""
    people = [
        ('R22_Aie1', 790, "Sto finendo i passatelli in brodo,\\nma una lotta non la rifiuto mai!$", "Mi è andato di traverso il brodo!$", "Qui la piadina la fanno ancora\\nsul testo di terracotta.$"),
        ('R22_Aie2', 791, "Il mio Pokémon ha mangiato tre\\npiatti di strozzapreti. È carico!$", "Forse aveva mangiato troppo...$", "Le aie erano i cortili delle case\\ncoloniche, dove si batteva il grano.$"),
        ('R22_Aie3', 792, "Prima il Sangiovese, poi la lotta!\\nAnzi no, prima la lotta!$", "Brindo alla tua vittoria!$", "Questa casa colonica ha più di\\ncent'anni. Senti che profumo!$"),
        ('R22_Aie4', 793, "Vengo qui ogni domenica con la\\nfamiglia. Vediamo cosa sai fare!$", "Domenica prossima mi rifaccio!$", "L'oste tiene un SNORLAX in cucina.\\nPensa a quante piadine mangia!$"),
        ('R22_Aie5', 794, "Sono l'ultimo tavolo e il più duro.\\nI miei Pokémon sono cresciuti a Cervia!$", "Hai battuto tutta la sala!$", "Ora parla con l'OSTE. Ha qualcosa\\nper chi batte tutti i clienti.$"),
    ]
    out = []
    for lab, tid, intro, defeat, post in people:
        out.append(f'''
	.align 2
{lab}::
	trainerbattle_single {tid}, {lab}_I, {lab}_D
	msgbox {lab}_P, MSGBOX_AUTOCLOSE
	end
{lab}_I:
	.string "{intro}"
{lab}_D:
	.string "{defeat}"
{lab}_P:
	.string "{post}"
''')
    return ''.join(out)

SIGNS = {
    'R22_SignAie': r"CASA DELLE AIE\nOsteria di campagna dal Settecento.\pPiadina, cappelletti e lotte\nai tavoli!",
    'R22_SignCampagna': r"CAMPAGNA CERVESE\nNord: CERVIA - Sud: CESENA\pAttraverso il grano si arriva a Cesena.",
    'R22_SignPensione': r"PENSIONE POKéMON\nAlleviamo i tuoi Pokémon con cura.",
    'R22_SignCostaW': r"OVEST: CESENA\nRocca Malatestiana e Piazza del Popolo.",
    'R22_SignCostaE': r"EST: CESENATICO\nPorto canale e museo della marineria.",
    'R22_SignCesenatico': r"CESENATICO\nIl porto canale disegnato da Leonardo.",
    'R22_SignCesenaticoW': r"OVEST: COSTA ADRIATICA E CESENA\pLa PENSIONE POKéMON è lungo la strada.",
    'R22_SignRiviera': r"RIVIERA ROMAGNOLA\nSpiaggia fino a Rimini e Cesenatico.",
    'R22_SignAieMenu': r"MENU DEL GIORNO\nPassatelli, strozzapreti, piadina\lcon squacquerone e Sangiovese.",
    'R22_SignRose': r"ISOLA DELLE ROSE\nRepubblica Esperantista, 1968.\pLingua ufficiale: esperanto.\nLa Insulo de la Rozoj.",
    'R22_SignMare': r"MARE DI RIMINI\nAl largo: ISOLA DELLE ROSE.\pSolo per nuotatori esperti!",
    'R22_SignShrine': r"SANTUARIO DELLA PINETA\nNon disturbare il custode del bosco.",
    'R22_SignRayq': r"MONUMENTO A FRANCESCO BARACCA\nL'asso del cielo di LUGO.",
    'R22_SignSaline': r"SALINE DI CERVIA\nOvest: le vasche e la SALINA CAMILLONE.\pEst: il varco per CERVIA.",
    'R22_SignBefane': r"LE BEFANE SHOPPING CENTRE\nNegozi, cinema e ristoranti.\pParcheggio gratuito.",
    'R22_SignPlatform': r"PIATTAFORMA ADRIATICO 7\nBase di lancio ROMAGNA-1.\pAccesso riservato al personale.",
    'R22_SignMaze': r"PARCO DELLA ROCCA\nIl grande labirinto di siepi.\pIn fondo, dicono, vive un Pokémon\nche sbuffa fumo dorato...",
}


def translations_src():
    """Italian versions of the English Emerald texts still reachable (Pensione, trade room)."""
    import json
    T = json.load(open('/home/claude/r22/translations22.json'))
    out = []
    for k, v in T.items():
        out.append(f'''
R22_TT_{k[2:]}::
	.string "{v}$"
''')
    return ''.join(out)


def signs_src():
    out = []
    for lab, txt in SIGNS.items():
        body = txt.replace('\n', '\\n').replace('\\p', '\\p').replace('\\l', '\\l')
        out.append(f'''
	.align 2
{lab}::
	msgbox {lab}_T, MSGBOX_SIGN
	end
{lab}_T:
	.string "{body}$"
''')
    return ''.join(out)
