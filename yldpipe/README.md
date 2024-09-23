## usecases

alle eip hosts - ie to ansible

URLs für alle apps als tabelle generieren

## yaml

yq '.|keys[]' config.yml



## roadmap

excel table neu anlegen, füllen, endgültigen standard festlegen


weitere schritte zur datenbank, 
csv query tests

keepass import dateien csv generieren

## keepass

bisherige group, direkte einträge, subgroups, wiederum einträge - 

Dies abbilden nach ein paar generellen Wegen:

Neue Gruppe wird mit neuer Untergliederung versehen. Alle Einträge aus alter Gruppe inkl. Subgroups werden gemeinsam neu geordnet nach neuer Gliederung (meist nach Behörden ArbG, FinG, etc.)


## tree

pykeepass hat eigene methoden, also wird man entscheiden müssen ob generisch oder kp bezogen...
evtl könnte gehen:
generisch erst;
dann wenn  lauf ok, die speziellen methoden "nach unten" aufrufen, dh nicht erben von pykeepass

also der generische tree, da kann jeder node also ebenso eine liste von einträgen haben, aka kp entries. Und diese werden dann nach der gewissen Logik transferiert. 
ok soweit.

und dann?
ABer die daten sind nunmal im keepass, zb die src ordner struktur
ne nen


also ein keepass mixin wär möglich?, aber hab ja eigl
dadruch ja die doppel definition. 
...
hmm nun abgeändert, kptree init macht nur pykeepass init. 
...



nun elementree wieder erkannt als pykeepass seine grundlage.
Was geht deamit denn schon eigl?
childrens etc zu root hinzu,  is es eine cvollwertige keepass erstelliun?

nun hab zwei PkP trees aka etrees
nun eine TreeMapper klasse, die die transformation des einene trees in den anderen wertet-

level-order tree durchlauf: Erst den erstenlevel durch; bei jedem node schauen ob existiert ein gleichnamiger - dann zuweisen



