# -*- coding: latin-1 -*-
from bottle import route, post, delete, get, run, template, request, redirect, response, static_file
import requests
import json
from datetime import datetime, timedelta
import log
import uuid
import urllib
logger = log.setup('root', 'harrybot.log')
import secrets

port = 8083 

import time
from slackclient import SlackClient

token = secrets.global_config.slackkey      # found at https://api.slack.com/web#authentication

sc = SlackClient(token)
print sc.api_call("api.test")
#print sc.api_call("channels.info", channel="1234567890")
#print sc.api_call(
##    "chat.postMessage", channel="#bottest", text="Hello from Python! :tada:",
#    username='pybot', icon_emoji=':robot_face:'
#)

 
# -*- coding: latin-1 -*-
import re 

regs = [
[r"childerswijk", r"childâhswijk"],
[r"(?<![o])ei", r"è"], # moet voor 'scheveningen' en 'eithoeke', geen 'groeit'
[r"koets", r"patsâhbak"],
[r"Kurhaus", r"Koeâhhâhs"], # moet voor 'au' en 'ou'
[r"\\bMaurice\\b", r"Mâhpie"], # moet voor 'au' en 'ou'
[r"Hagenezen", r"Hageneize"], # moet na 'ei'
[r"(L|l)unchroom", r"\1unsroem" ],
[r"\\bThis\\b", r"Dis" ],
[r"\\b(H|h)ighlights\\b", r"\1aailaaits"],
[r"\\b(L|l)ast-minute\\b","\1asminnut" ],
[r"\\bAirport", r"Èâhpogt" ],
[r"\\bairport", r"èâhpogt" ],
[r"(A|a)dvertentie", r"\1dvâhtensie" ],
[r"\\b(B|b)eauty", r"\1joetie" ],
[r"\\bthe\\b", r"de" ],
[r"\\b(B|b)east\\b", r"\1ies" ],
[r"(B|b)each", r"\1ietsj"],
[r"Bites", r"Bèts" ],
[r"Cuisine", r"Kwiesien"],
[r"cuisine", r"kwiesien"],
[r"Europese", r"Euraipeise"],
[r"event(s|)", r"ievent\1" ],
[r"Event(s|)", r"Ievent\1" ],
[r"(F|f)acebook", r"\1eisboek" ],
[r"(F|f)avorite", r"\1avverietûh" ],
[r"(F|f)avoriete", r"\1avverietûh" ],
[r"(F|f)lagship", r"fleksjip" ],
[r"Jazz", r"Djez" ],
[r"jazz", r"djez" ],
[r"(T|t)entoon", r"\1etoon" ],
[r"(C|c)abaret", r"\1abberet" ],
[r"(M|m)usical", r"\1usikol" ],
[r"kids", r"kindâh" ], # 'kindertips'
[r"(M|m)ovies", r"\1oevies" ],
[r"(O|o)rigin", r"\1rresjin" ], # 'originele
[r"(P|p)alace", r"\1ellus"],
[r"(P|p)rivacy", r"\1raaivesie" ],
[r"policy", r"pollesie" ],
[r"\\b(R|r)oots\\b", r"\1oets" ],
[r"SEA LIFE", r"SIELÈF" ],
[r"(S|s)how", r"\1jow" ],
[r"(S|s)hoppen", r"\1joppûh" ],
[r"(S|s)kiën", r"\1kieje"],
[r"(S|s)tores", r"\1toâhs" ],
[r"(T|t)ouchscreen", r"\1atskrien" ],
[r"(T|t)ouch", r"\1ats" ],
[r"that", r"det" ],
[r"(T|t)ripadvisor", r"\1ripetfaaisoâh" ],
[r"(V|v)andaag", r"\1edaag" ],
[r"\\b(V|v)erder\\b", r"\1eâhdahs"],
[r"(V|v)intage", r"\1intuts" ],
[r"you", r"joe" ],
[r"(W|w)eekend", r"\1iekend" ],
[r"(W|w)ork", r"\1urrek" ],
[r"(B|b)ibliotheek", r"\1iebeleteik" ],
[r"cadeau", r"kado" ],
[r"(F|f)ood", r"\1oet"],
[r"doe je het", r"doejenut"],
[r"\\bsee\\b", r"sie"], # van 'must see'
[r"\\b(M|n)ust\\b", r"\1us" ], # van 'must see'
[r"(M|m)oeten", r"\1otte"], # moet voor '-en'
[r"(w|W)eleens", r"\1elles"], # 'weleens', moet voor 'hagenees'
[r"(g|G)ouv", r"\1oev"], # 'gouveneur'
[r"heeft", r"hep"], # 'heeft', moet voor 'heef'
[r"(on|i)der(?!e)", r"\1dâh" ], # 'onder', 'Zuiderpark', geen 'bijzondere'
[r"(?<![ao])ndere", r"ndâhre" ], # 'bijzondere', geen 'andere'
[r"ui", r"ùi"], # moet voor 'ooi' zitte n
[r"Ui", r"Ùi" ],
[r"oort", r"ogt"], # 'soort', moet voor '-ort'
[r"(?<![eo])ert\\b", r"egt" ], # 'gert'
[r"\\b(V|v)ert", r"\1et"], # 'vertegenwoordiger', moet voor '-ert'
[r"(?<![eo])erte", r"egte" ], # 'concerten'
[r"(?<![eo])(a|o)r(|s)t(?!j)", r"\1g$2t" ], # barst, martin etc., geen 'eerste', 'biertje', 'sport', 'voorstellingen'
[r" er aan", r" d'ran"], # 'er aan'
[r"(A|a)an het\\b", r"\1nnut"], # 'aan het', moet voor 'gaan'
[r"\\b(A|a)an", r"\1n" ], # 'aan', 'aanrennen'
[r"\\b(G|g)aan\\b", r"\1an" ], # 'gaan'
[r"(H|h)oud\\b", r"\1ou"], # 'houd', moet voor 'oud'
[r"(au|ou)w(?!e)", r"\1"], # 'vrouw', ''flauw', maar zonder 'blauwe'
[r"oude", r"ouwe"], # 'goude'
[r"\\b(T|t)our\\b", r"\1oeâh"],
[r"diner\\b", r"dinei"],
[r"(B|b)oul", r"\1oel"], # 'boulevard'
[r"(au|ou)(?!v)", r"âh" ], # 'oud', geen 'souvenirs'
[r"aci", r"assi"], # 'racist'
[r"als een", r"assun"], # 'als een'
[r"a(t|l) ik", r"a\1\1ik"], # val ik, at ik
[r"alk\\b", r"alluk"], # 'valk'
[r"(?<![a])ars", r"ags"], # 'harses', geen 'Haagenaars'
[r"oor" ,     "oâh"],
[r"(A|a)ar(?![io])", r"\1ah"], # 'waar, 'aardappel, 'verjaardag', geen 'waarom', 'waarin'
[r"aar(?![i])", r"ar" ], # wel 'waarom', geen 'waarin'
[r"patie", r"petie"], # 'sympatiek'
[r"aagd\\b", r"aag"], # 'ondervraagd'
[r"(am|at|ig|ig|it|kk|nn)en(?![ ,.?!])", r"\1e"], # 'en' in een woord, bijv. 'samenstelling', 'eigenlijk', 'buitenstaander', 'statenkwartier', 'dennenweg', 'klokkenluider'

      # woordcombinaties
[r"\\b(K|k)an er\\b", r"\1andâh"],
[r"\\b(K|k)en ik\\b", r"\1ennik"],
[r"\\b(K|k)en u\\b", r"\1ennu"],
[r"\\b(K|k)en jij\\b", r"\1ejjèh"],
[r"\\b(A|a)ls u", r"\1ssu"],
[r"\\b(M|m)ag het\\b", r"\1aggut"],
[r"\\bik dacht het\\b", r"dachut"],
[r"\\b(V|v)an jâh\\b", r"\1ajjâh"],
[r"\\b(K|k)ijk dan\\b", r"\1èktan"],
[r"\\b(G|g)aat het\\b", r"\1aat-ie"],
[r"\\b(M|m)et je\\b", r"\1ejje"],
[r"\\b(V|v)ind je\\b", r"\1ijje"],
[r"\\bmij het\\b", r"mènnut"],

[r"\\b(A|a)ls er\\b", r"\1stâh"],
[r"\\b(K|k)(u|a)n j(e|ij) er\\b", r"\1ejjedâh"], # 'ken je er'
[r"\\b(K|k)un je\\b", r"\1ajje" ],
[r"\\bje ([^ ]+) je", r"je \1 je ège" ],
[r"ADO Den Haag", r"FC De Haag"],
[r"ADO", r"Adau"],
[r"(?<![i])atie(?![fkv])", r"asie" ], # 'informatie', geen 'initiatief', 'kwalitatieve', 'automatiek'
[r"avil", r"ave" ], # 'strandpaviljoen'
[r"sje\\b", r"ssie"], # 'huisje', moet voor 'asje'
[r"\\balleen\\b", r"enkelt"],
[r"\\bAlleen\\b", r"Enkelt"],
[r"(A|a)ls je", r"\1sje"], # moet voor 'als'
[r"(?<![v])als\\b", r"as"],
[r"(b|k|w)ar\\b", r"\1âh"],
[r"\\bAls\\b", r"As"],
[r" bent\\b", r" ben"], # 'ben', geen 'instrument'
[r"bote", r"baute"], # 'boterham'
[r"(B|b)roc", r"\1rauc" ], # 'brochure'
[r"bt\\b", r"b"], # 'hebt'
[r"cc", r"ks"], # 'accenten'
[r"chique", r"sjieke" ],
[r"chure", r"sjure" ], # 'brochure'
[r"ct", r"kt"], # 'geactualiseerde', 'directie'
[r"Co", r"Ko" ], # 'Concerten'
[r"cor\\b", r"koâh" ], # 'decor'
[r"(?<![.])co", r"ko" ], # 'concerten', 'collectie', geen '.com'
[r"cu", r"ku" ], # 'culturele'
[r"Cu", r"Ku" ], # 'culturele'
[r"(ch|c|k)t\\b", r"\1"], # woorden eindigend op 'cht', 'ct', 'kt', of met een 's' erachter ('geslachts')
[r"(ch|c|k)t(?![aeiouâ])", r"\1"], # woorden eindigend op 'cht', 'ct', 'kt', of met een 's' erachter ('geslachts')
[r"(d|D)at er", r"\1attâh"], # 'dat er'
[r"(d|D)at is ", r"\1a's "], # 'dat is'
[r"denst", r"dest" ],
[r"derb", r"dâhb"],
[r"derd\\b", r"dâhd"], # 'veranderd'
[r"(?i)(d)eze(?![l])", r"\1eize"],
[r"dt\\b", r"d"], # 'dt' op het einde van een woord
[r"\\b(B|b)ied\\b", r"\1iedt" ], # uitzondering, moet na '-dt'
      
[r"(D|d)y", r"\1i"], # dynamiek
[r"eaa", r"eiaa"], # 'ideaal'
[r"ègen", r"ège" ], # 'eigentijds', moet voor 'ee'
[r"Eig", r"Èg" ], # 'Eigenlijk', moet voor 'ee'
[r"eig", r"èg" ], # 'eigenlijk', moet voor 'ee'
[r"uee\\b", r"uwee"], # 'prostituee', moet voor '-ee'
[r"ueel\\b", r"eweil"], # 'audiovisueel'
[r"uele\\b", r"eweile" ], # 'actuele'
[r"(g|n|l|L|m|M)ee(n|s)" , "\1ei$2"], # 'geen', 'hagenees', 'lees', 'burgemeester'
[r"ee\\b", r"ei"], # met '-ee' op het eind zoals 'daarmee', 'veel'
[r"eel", r"eil"], # met '-ee' op het eind zoals 'daarmee', 'veel'
[r" is een ", r" issun "], # moet voor ' een '
[r"(I|i)n een ", r"\1nnun "], # 'in een', voor ' een '
[r"één", r"ein"], # 'één'
[r" een ",    " un "],
[r"Een ", r"Un "],
[r" eens", r" 'ns"], # 'eens'
[r"(?<![eo])erd\\b", r"egd"], # 'werd', geen 'verkeerd', 'gefeliciteerd', 'beroerd
[r"eerd", r"eâhd"], # 'verkeerd'
[r"(?<![k])ee(d|f|g|k|l|m|n|p|s|t)", r"ei\1"], # 'bierfeest', 'kreeg', 'greep', geen 'keeper'
[r"(?<![èijhm])ds(?![eè])", r"s" ], # moet na 'ee','godsdienstige', 'gebedsdienst', geen 'ahdste', 'beroemdste', 'eigentijds', 'weidsheid', 'reeds', 'strandseizoen'
[r"(?<![e])ens\\b", r"es"], # 'ergens', geen 'weleens'
[r"(D|d)ance", r"\1ens" ], # moet na '-ens' 
[r"(?<![ hi])eden\\b", r"eije"], # geen 'bieden'. 'bezienswaardigheden'
[r"(?<![ bgi])eden", r"eide" ], # 'hedendaagse', geen 'bedenken'
[r"\\b(E|e)ve", r"\1ive" ], # 'evenementen'
[r"me(d|t)e", r"mei\1e"], # 'medeklinkers'
[r"eugd", r"eug" ], # 'jeugd', 'jeugdprijs'
[r"(?<![o])epot\\b", r"eipau"], # 'depot'
[r"(e|E)rg\\b", r"\1rrag"], # 'erg', moet voor 'ergens'
[r"(?<![fnN])(a|o)rm","\1rrem" ], # 'platform', 'vormgeving', 'warm', geen 'normale', 'informatie'
[r"(f|N|n)orm", r"\1oâhm" ], # 'normale', 'informatie'
[r"(i|I)nter", r"\1ntâh" ], # moet voor '-ern'
[r"elden", r"elde"], # 'zeeheldenkwartier'
[r"(?<![epvV])er(m|n)", r"erre\1"], # kermis', geen 'vermeer', 'vermoeide', 'externe', 'supermarkt'
[r"(?<![etv])(e|E)rg(?!ez)", r"\1rreg"], # 'kermis', 'ergens', geen 'achtergelaten', 'neergelegd', 'overgebleven', 'ubergezellige'
[r"ber(?![eoiuâè])", r"bâh"], # 'ubergezellige', moet na '-erg'
[r"(G|g)eve(r|n)", r"\1eive$2" ], # 'Gevers', moet voor '-ers', geen 'gevestigd'
[r"(?<![eo ])ers(?![. ,c])", r"egs"], # 'diverse', 'versie', geen klinkers, geen 'eerste', geen 'verscheen'
[r"Vers\\b", r"Vegs"], # 'vers', moet voor -ers}
[r"(?<![ei])vers\\b", r"vegs"], # 'vers', moet voor -ers, geen 'Gevers'
[r"renstr", r"restr" ], # 'herenstraat' (voor koppelwoorden)
[r"(?<![eio])eder", r"eider" ], # 'Nederland', geen 'iedereen', 'bloederige'
[r"(?<![eio])ers\\b", r"âhs"], # 'klinkers'
[r"(?<![v])ers(c|t)", r"âhs\1"], # 'eerste', 'bezoekerscentrum', geen 'verschaffen'
[r"erwt", r"erret" ], # 'erwtensoep'
[r"(?<![eo])eci", r"eici" ], # 'speciaal'
[r"ese", r"eise" ], # 'reserveer'
[r"eiser", r"eisâh"], # 'reserveer'
[r"eur\\b", r"euâh"], # worden eindigend op 'eur', zoals 'deur', 'gouveneurlaan', geen 'kleuren'
[r"eur(?![eio])", r"euâh"], # worden eindigend op 'eur', zoals 'deur', 'gouveneurlaan', geen 'kleuren', 'goedkeuring', 'euro
[r"eur(i|o)", r"euâhr\1"], # 'goedkeuring', 'euro'
[r"eurl", r"euâhl"], # worden eindigend op 'eur', zoals 'deur', 'gouveneurlaan'
[r"eer", r"eâh" ], # 'zweer', 'neer'
[r"elk\\b", r"ellek"], # 'elk'
[r"(E|e)xt", r"\1kst" ], # 'extra'
[r"(H|h)ele", r"\1eile"], # 'gehele', 'hele'
[r"\\b(g|G|v|V)ele\\b", r"\1eile" ], # 'vele', 'gele', 'hele'
[r"nele", r"neile" ], # 'originele'
[r"\\b(D|d)elen", r"\1eile"], # 'delen', geen 'wandelen'
[r"sdelen", r"sdeile"], # 'geslachtsdelen', geen 'wandelen'
[r"(?<![diokrs])ele(n|m)", r"eile\1"], # 'helemaal', geen 'enkele', 'winkelen', 'wandelen', 'borrelen', 'beginselen'
[r"(B|b)eke(?![n])", r"\1eike"], # 'beker', geen 'bekende'
[r"(?<![ioBbg])eke", r"eike"], # geen 'aangekeken' op 'gek', wel 'kek'
[r"(?<![r])rege", r"reige" ], # 'gekregen', geen 'berrege'
[r"(?<![bBIior])e(g|v|p)e(l|n|m| )", r"ei\1e$2" ], # aangegeven, geen 'geleden', 'uitspreken', 'geknepen', 'goeveneur', 'verdiepen', 'postzegels', 'begeleiding', 'berregen'
[r"dige", r"dege"], # 'vertegenwoordiger', moet na 'ege'
[r"alve\\b", r"alleve"], # 'halve', moet na 'aangegeven'
[r"\\b(K|k)en\\b", r"\1an"], # moet voor -en
[r"(a|o)ien\\b", r"\1ie"], # 'uitwaaien', geen 'zien'
[r"(?<![ ieo])en([.?!])", r"ûh\1"], # einde van de zin, haal ' en ', 'doen', 'zien' en 'heen'  eruit
[r"(?<![ bieoh])en\\b", r"e"], # haal '-en' eruit, geen 'verscheen', 'tien', 'indien', 'ben', 'doen', 'hen'
[r"bben\\b", r"bbe"], # 'hebben'
[r"oien\\b", r"oie"], # 'weggooien'
[r"enso", r"eso" ], # 'erwtensoep'
[r"(?<![eio])enm(?![e])", r"em" ], # 'kinderboekenmuseum', geen 'kenmerken'
[r"(?<![eio])en(b|h|j|l|p|r|v|w|z)", r"e\1"], # 'binnenhof', geen 'paviljoenhoeder'
[r"([Hh])eb je ", r"\1ebbie "], # voor '-eb'
[r"(H|h)eb (un|een)\\b", r"\1ep'n"], # voor '-eb'
[r"(?<![eu])eb\\b", r"ep"],
[r"(E|e)x(c|k)", r"\1ksk" ], # 'excursies'
[r"(?<![ s])teri", r"tâhri" ], # 'karakteristieke'
[r"(?<![ sS])ter(?![aeirn])", r"tâh"], # 'achtergesteld', geen 'beluisteren', 'literatuur', 'sterren', 'externe', 'sterker', 'karakteristieke'
[r"feli", r"feili" ], # 'gefeliciteerd'
[r"(I|i)ndeli", r"\1ndeili" ], # 'indeling', geen 'eindelijk', 'wandelingen'
[r"(f|p)t\\b", r"\1"], # 'blijft', 'betrapt'
[r"\\b(N|n)iet\\b", r"\1ie" ], # 'niet', geen 'geniet'
[r"fd\\b", r"f"], # 'hoofd'
[r"(F|f)eb", r"\1eib" ], # 'februari'
[r"ngt\\b", r"nk"], # 'hangt'
[r"eving", r"eiving"], # 'omgeving'
[r"gje\\b", r"ggie"], # 'dagje'
[r"go(r)", r"gau\1" ], # 'algoritme'
[r"gelegd\\b", r"geleige"], # 'neergelegd'
[r"([HhVvr])ee(l|n|t)", r"\1ei$2"], # 'verscheen', 'veel', 'overeenkomsten', 'heet'
[r"(H|h)er(?![e])", r"\1eâh" ], # 'herzien', geen 'herenstraat'
[r"(I|i)n het", r"\1nnut"], # 'in het'
[r"\\b(E|e)te", r"\1ite"], # 'eten'
[r"(?<![ir])ete(?![i])", r"eite" ], # 'hete', 'gegeten', geen 'bibliotheek','erretensoep', 'koffietentjes', 'genieten
[r"(d|h|l|m|r|t)ea(?![m])", r"\1eija" ], # 'theater', geen 'team'
[r"\\bhet\\b", r"ut"],
[r"Het\\b", r"Ut"],
[r"(?<![eouù])i\\b", r"ie" ], # 'januari'
[r"ieri", r"ieâhra"], # 'plezierig'
[r"ier(?![aeio])", r"ieâh" ], # 'bierfeest', geen 'hieronymus', 'plezierig', 'dieren'
[r"iero(?![eo])", r"ierau" ], # 'hieronymus'
[r"ière", r"ijerre"], # 'barriere'
[r"ibu", r"ibe"], # 'tribunaal'
[r"icke", r"ikke" ], # 'tickets'
[r"ijgt\\b", r"ijg"], # 'krijgt', moet voor 'ij\\b'
[r"(B|b)ijz", r"\1iez" ], # 'bijzondere', moet voor 'bij'
[r"ij\\b",  "è"], # 'zij', 'bij'
[r"(?<![e])ije(n|)", r"èje" ], # 'bijenkorf', 'blije', geen 'geleie' 
[r"(B|b)ij", r"\1è" ], # 'bijbehorende'
[r"\\blijk\\b", r"lèk" ], # 'lijk' , geen 'eindelijk' ('-lijk')
[r"(D|d|K|k|R|r|W|w|Z|z)ijk", r"\1èk"], # 'wijk', geen '-lijk'
[r"ij([dgslmnftpvz])",  "è\1"], # 'knijp', 'vijver', 'stijl', 'vervoersbewijzen', geen '-lijk'
[r"(?<![euù])ig\\b",    "ag"], # geen 'kreig', 'vliegtuig'
[r"lige\\b",    "lage"], # 'gezellige'
[r"(?<![euù])igd\\b", r"ag" ], # gevestigd
[r"ilm", r"illem" ], # 'film'
[r"ilieu", r"ejui"], # 'milieu'
[r"inc", r"ink"], # 'incontinentie'
[r"io(?![oen])", r"iau"], # 'audio', geen 'viool', 'station'
[r"\\bin m'n\\b", r"imme"],
[r"(n|r)atio", r"\1asjau" ], # 'internationale'
[r"io\\b", r"iau" ], # 'audio', geen 'viool', 'station', 'internationale'
[r"io(?![oen])", r"iau" ], # 'audio', geen 'viool', 'station', 'internationale'
[r"ir(c|k)", r"irrek" ], # 'circus'
[r"(?<![gr])ties\\b", r"sies"], # 'tradities', moet voor -isch, geen 'smarties'
[r"isch(|e)", r"ies\1"],
[r"is er", r"istâh"],
[r"(p) je\\b", r"\1ie" ], # 'loop je'
[r"(g|k) je\\b", r"\1\1ie" ], # 'zoek je'
[r"jene", r"jenei"], # 'jenever'
[r"jezelf", r"je ège"], # "jezelf"
[r"(?<![oe])kje\\b", r"kkie"], # 'bakje', moet voor algemeen regel op 'je', TODO, 'bekje'
[r"olg", r"olleg"], # 'volgens'
[r"opje\\b", r"oppie"], # 'kopje'
[r"(?<![ deèijst])je\\b", r"ie"], # woorden eindigend op -je', zonder 'asje', 'rijtje', 'avondje', geen 'mejje' 'blèjje', 'skiën'
[r"(K|k)an\\b", r"\1en"], # 'kan', geen 'kans', 'kaneel'
[r"(K|k)unne", r"\1enne"], # 'kunnen', TODO, wisselen van u / e
[r"(K|k)unt", r"\1en" ],
[r"(K|k)led", r"\1leid"], # 'kleding'
[r"orf", r"orref" ],
[r"oro(?![eo])", r"orau" ], # 'Corona'
[r"Oo([igkm])", r"Au\1" ], # 'ook' 
[r"oo([difgklmnpst])",         "au\1"], # 'hoog', 'dood'
[r"rij",      "rè"],
[r"tieg", r"sieg" ], # 'vakantiegevoel'
[r"(?<![e])tie\\b",   "sie"], # 'directie', geen 'beauty'
[r"enties\\b", r"ensies"], # 'inconsequenties', geen 'romantisch'
[r"erpe", r"errepe"], # 'modeontwerper'
[r"(b|B|k|K|m|L|l|M|p|P|t|T|w|W)erk", r"\1errek" ], # 'kerk', 'werkdagen', geen 'verkeer'
[r"(f|k)jes\\b", r"\1\1ies" ], # 'plekjes'
[r"(M|m)'n", r"\1e"], # 'm'n'
[r"(M|m)ong", r"\1eg"], # 'mongool'
[r"(M|m)ein(?![ut])", r"\1eint"], # moet na 'ee', geen 'menu', 'gemeentemuseum'
[r"mt\\b", r"mp"], # 'komt'
[r"(?<![oO])md(?![e])", r"mp" ], # 'beroemdste', geen 'omdat', 'beroemde
[r"lair(?![e])", r"lèh"], # geen 'spectaculaire'
[r"ulaire", r"elère"], # 'spectaculaire'
[r"lein", r"lèn"],
[r"\\bliggûh\\b", r"leggûh"],
[r"\\b(L|l)igge\\b", r"\1egge" ],
[r"\\b(L|l)igt\\b", r"\1eg" ],
[r"(?<![p])(L|l)ez", r"\1eiz"], # 'lezer', geen 'plezierig'
[r"lf", r"lluf"], # 'zelfde'
[r"ll([ ,.])", r"l\1" ], # 'till'
[r"(a|e|i|o|u)rk\\b", r"\1rrek" ], # 'park', 'stork'
[r"(P|p)arke", r"\1agke"], # 'parkeervergunning', moet voor '-ark'
[r"ark(?![a])", r"arrek" ], # 'markt', 'marktstraat', geen 'markante'
[r"ark", r"agk"], # 'markante', moet na -ark
[r"\\b(M|m)oet\\b", r"\1ot"], # 'moet', geen 'moeten'
[r"nair", r"nèâh" ], # 'culinair'
[r"neme\\b", r"neime" ], # 'nemen', geen 'evenementen''
[r"nce", r"nse"], # 'nuance'
[r"\\b(N|n)u\\b", r"\1âh"],
[r"ny", r"ni" ], # 'hieronymus' 
[r"\\bmad", r"med"], # 'madurodam'
[r"oer\\b", r"oeâh"], # 'broer'
[r"oer(?![aieou])", r"oeâh"], # 'beroerd', 'hoer', geen 'toerist', 'stoere
[r"oeder", r"oedâhr" ], # 'bloederigste'
[r"(ordt|ord)(?![e])", r"ogt"], # wordt, word, geen 'worden'
[r"orde", r"ogde"], # 'worden'
[r"(N|n)(|o)od", r"\1aud"], # 'noodzakelijk'
[r"nirs\\b", r"nieâhs" ], # 'souvenirs'
[r"l(f|k|m|p)(?![a])", r"lle\1"], # 'volkslied', 'behulp', geen 'elkaar'
[r"olk", r"ollek"], # 'volkslied'
[r"(F|f)olleklore", r"\1olklore" ],
[r"o(c|k)a", r"auka" ], # 'locaties'
[r"(?<![o])oms", r"omps" ], # 'aankomsthal'
[r"one(e|i)", r"aunei" ], # 'toneel'
[r"oni", r"auni" ], # 'telefonische'
[r"hore", r"hoâhre"], # 'bijbehorende'
[r"org\\b", r"orrag"], # 'zorg'
[r"orge", r"orrage"], # 'zorgen'
[r"orp", r"orrep"], # 'ontworpen'
[r"\\borg", r"oâhg"], # 'orgineel'
[r"Over(?![ei])", r"Auvâh"], # 'overgebleven', 'overnachten', geen 'overeenkomsten', 'overige'
[r"over(?![ei])", r"auvâh"], # 'overgebleven', geen 'overeenkomsten', 'overige'
[r"o(v|z)e", r"au\1e"],
[r"o(b|d|g|k|l|m|p|s|t|v)(i|e)", r"au\1$2"], # 'komen', 'grote', 'over', 'olie', 'notie'
[r"O(b|d|g|k|l|m|p|s|t|v)(i|e)", r"Au\1$2"], # zelfde, maar dan met hoofdletter
[r"\\bout", r"âht" ], # 'outdoor'
[r"\\bOut", r"Âht" ], # 'Outdoor'
[r"\\b(V|v)er\\b", r"\1eâh"], # 'ver'
[r"(D|d)ert","\1eâht"], # 'dertig'
[r"der(?![eianrouèt])", r"dâh"],# 'moderne'/'moderrene', geen 'dertig'
[r"\\b(P|p|T|t)er\\b", r"\1eâh" ], # 'per', 'ter'
[r"(?<![ io])er\\b", r"âh" ], # 'kanker', geen 'hoer', 'er', 'per', 'hier' , moet voor 'over' na o(v)(e)
[r"(P|p)er(?!i)", r"\1âh"], # 'supermarkt', geen 'periode', moet na 'per'
[r"(P| p)o(^st)" , "\1au$2"], # 'poltici'
[r"p ik\\b", r"ppik"], # 'hep ik'
[r"ppen", r"ppe" ], # 'poppentheater'
[r"popu", r"paupe"], # 'populairste'
[r"(p|P)ro(?![oefkns])", r"\1rau" ], # 'probleem', geen 'prof', 'prostituee', 'instaprondleiding'
[r"(p|P)rofe", r"\1raufe" ], # 'professor', 'professioneel'
[r"ersch", r"esch"], # 'verschijn'
[r"(A|a)rme", r"\1rreme"], # 'arme'
[r"re(s|tr)(e|o)", r"rei\1$2"], # 'resoluut', 'retro', 'reserveren'
[r"redespa", r"reidespe"], # voor Vredespaleis
[r"(R|r)elax", r"\1ieleks" ],
[r"(R|r)estâhrant", r"\1esterant"],
[r"rants\\b", r"rans"], # 'restaurants'
[r"rigste", r"ragste"], # 'bloederigste'
[r"rod", r"raud"], # 'madurodam'
[r"(a|o)rt", r"\1gt"],  #'korte' 
[r"([Rr])o(?=ma)" , "\1au"], # voor romantisch, maar haal bijv. rommel eruit
[r"inds", r"ins"], # 'sinds'
[r"seque", r"sekwe"], # 'inconsequenties'
[r"sjes\\b", r"ssies"], # 'huisjes'
[r"(S|s)hop", r"\1jop" ], # 'shop'
[r"stje\\b", r"ssie"], # 'beestje'
[r"st(b|d|g|h|j|k|l|m|n|p|v|w|z)", r"s\1"], # 'lastpakken', geen 'str'
[r"(S|s)ouv", r"\1oev" ], # 'souvenirs'
[r"(s|S)tran", r"\1tgan" ], # 'strand', moet 'na st-'
[r"\\b(s|S)tr", r"\1tg" ], # 'strand', moet 'na st-'
[r"(?<![gr])st\\b", r"s"], # 'haast', 'troost', 'gebedsdienst', geen 'barst'
[r"tep\\b", r"teppie"], # 'step'
[r"té\\b", r"tei"], # 'satè'
[r"tion", r"sion"], # 'station'
[r"tje\\b", r"tsje"], # 'biertje'
[r"to\\b", r"tau"], # moet na 'au'/'ou'
[r"toma", r"tauma"], # moet na 'au'/'ou', 'automatiek', geen 'tom'
[r"(T|t)ram", r"\1rem"], # 'tram'
[r"ua", r"uwa"], # 'nuance', 'menstruatie'
[r"(J|j)anu", r"\1anne" ], # 'januari', moet na 'ua'
[r"ùite\\b", r"ùitûh" ], # 'buiten'
[r"(u|ù)igt\\b", r"\1ig"], # 'zuigt'
[r"(U|u)ren", r"\1re"], # 'uren'
[r"ùidâh\\b", r"ùiâh"], # 'klokkenluider'
[r"unch", r"uns" ], # 'lunch'
[r"urg", r"urrag"], # 'Voorburg'
[r"(?<![u])urs", r"ugs" ], # 'excursies', geen 'cultuurschatten'
[r"uur", r"uâh" ], # 'literatuurfestival', moet voor '-urf'
[r"ur(f|k)", r"urre\1"], # 'Turk','snurkende','surf'
[r"(T|t)eam", r"\1iem"],
[r"tu(?![âfkust])", r"te"], # 'culturele', geen 'tua', 'vintage', 'instituut', 'tussenletter', 'stuks'
[r"\\bvan je\\b", r"vajje"],
[r"\\bvan (het|ut)\\b", r"vannut"],
[r"([Vv])er(?![aeious])", r"\1e"], # wel 'verkoop', geen 'verse', 'veranderd', 'overeenkomsten', 'overige'
[r"\\bvaka", r"veka"], # 'vakantie'
[r"vaka", r"veka" ], # 'vakantie' 
[r"vard\\b", r"vâh"], # 'boulevard'
[r"\\b(V|v)ege", r"\1eige"], # 'vegetarisch'
[r"voetbal", r"foebal"],
[r"we er ", r"we d'r "], # 'we er'
[r"\\ber\\b", r"d'r"],
[r"\\bEr\\b", r"D'r"],
[r"wil hem\\b", r"wil 'm"],
[r"(W|w|H|h)ee(t|l)", r"\1ei$2"], # 'heel', 'heet'
[r"yo", r"yau" ], # 'yoga' 
[r"\\b(Z|z)ee", r"\1ei"], # 'zeeheldenkwartier'
[r"\\b(Z|z)ult\\b", r"\1al"],
[r"z'n" , "ze"], # 'z'n'
[r"\\bzich\\b", r"ze ège"], # 'zich'
[r"z(au|o)'n", r"zaun"],
[r"\\bzegt\\b", r"zeg"],
[r"zo(?![enr])", r"zau"], # 'zogenaamd', geen 'zoeken', 'zondag', 'zorgen'
[r"'t", r"ut"],
[r"derr", r"dèrr" ], # 'moderne, moet na 'ern'/'ode'
[r"Nie-westegse", r"Niet westagse" ],
[r"us sie", r"us-sie" ], # 'must see'
[r"\\bThe Hague\\b", r"De Heek" ], # moet na 'ee -> ei'
[r"Crowne", r"Kraun" ],
[r"social media", r"sausjel miedieja" ], # moet na 'au'

      #quick fixups
[r"stgong>", r"strong>"], #fixups for <strong tag>
[r"kute;", r"cute;" ]
]


def translate(dutch):
    
    result = []
    haags = dutch;
    for replacement in regs:
        original = haags;
        haags = re.sub(replacement[0], replacement[1],original)
    return haags;

@post("/")
def slack_command():
    try:
        fields = ["token",
                    "team_id",
                    "team_domain",
                    "channel_id",
                    "channel_name",
                    "user_id",
                    "user_name",
                    "command",
                    "text",
                    "response_url"]
        data = {}
        for field in fields:
            data[field] = request.forms.getunicode(field)
        logger.debug(data)


        response_text = translate(data["text"])
        responsedata = {
                "text": response_text ,
                }
        r = requests.post(data.get("response_url"),data = json.dumps(responsedata))
        print r.status_code
        print r.content

    except:
        logger.exception("error")
        response.status = 501
        return "Internal server error"



logger.debug("starting server at:" + str(port))

run(host='localhost', port=port)


