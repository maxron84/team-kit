# Ein doppeltes Anfuehrungszeichen im Notiztext zerlegt rollen-abschluss in Schalter

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Gewachsen (dreizehn Kaskaden), Windows, **nur pwsh-Bahn**, Python + Electron, rund 550 Tests.

## Was passiert ist

Kostenabschluss einer Kaskade. Die Notiz für die Bauzeile zitierte wörtlich das
`result`-Feld eines Laufs, der im vierten Ausgang (`BL-41`) geendet hatte —
also die Stelle, an der die Rolle selbst sagt, worauf sie gewartet hat:

```powershell
$nb = '… Das Feld result sagt es woertlich: "ich warte noch auf das Ergebnis
       des Smoke-Tests". Von Hand quittiert, Zeiger auf 64. …'
.\team-status.cmd --rollen-abschluss <N> <domaene> $nr $nb
```

**Antwort:**

```
Unbekannter Schalter 'warte' — erlaubt: --addieren, --ersetzen, --trotzdem, --auch-aeltere
```

Exit **1**. Die Zeichenkette wird beim Zerlegen der Restargumente an den
doppelten Anführungszeichen zerschnitten; das Wort dahinter landet in der
Schalterprüfung. Der Notiztext war eine **einzelne**, korrekt in einfache
Anführungszeichen gefasste PowerShell-Zeichenkette — an der Aufrufstelle ist
nichts zu sehen, was den Fehler erklärt.

**Verschärfend:** Der Abbruch kommt **nach** der bereits gebuchten
`ralph`-Hälfte (siehe die Schwestermeldung zu `BL-239`). Ein Aufruf, der mit
Exit 1 an einer Notiz scheitert, hinterlässt damit einen halben Zustand im
Ledger.

## Wo es steckt

`team-status.ps1`, in der Zerlegung der Restargumente von
`--rollen-abschluss` / `--akteur-abschluss` — dort, wo entschieden wird, ob
ein Restargument eine Notiz oder ein Schalter ist. Vermutlich dieselbe Wurzel
wie `BL-142` (Restargumente laufen durch die Ausgabepipeline und werden dabei
umgedeutet), aber ein anderer Schritt: `BL-142` betraf die **Weitergabe** einer
zweielementigen Liste, hier geht es um die **Zerlegung** eines einzelnen
Elements.

## Warum das jede Installation trifft

Der Notiztext ist laut Briefing die **einzige Prosa-Spur je Ledgerzeile**:
*„Meine Notiz steht in beiden Zeilen … sie ist die einzige Prosa-Spur je
Ledger-Zeile."* Eine gute Notiz zitiert deshalb, was das Werkzeug oder die
Rolle gesagt hat — Log-Ausgaben, `result`-Felder, Fehlermeldungen. Doppelte
Anführungszeichen sind dort der **Normalfall**, nicht die Ausnahme. Es steckt
in einem Entrypoint des Kits, betrifft also jede Installation der pwsh-Bahn.

Das Ärgerliche ist nicht der Abbruch, sondern seine Diagnose: Die Meldung
nennt ein Wort aus der Mitte des eigenen Fließtextes als „Schalter". Wer den
Zusammenhang nicht kennt, sucht ihn im Aufruf, nicht in der Prosa.

## Was ich vorschlage

Die Restargumente **nicht erneut zerlegen**: Was PowerShell als ein Argument
übergibt, ist ein Argument. Für die Schalterprüfung genügt der Test auf ein
führendes `--` am **ganzen** Element. Falls die Zerlegung aus einem anderen
Grund nötig ist, sollte die Fehlermeldung wenigstens sagen, aus welchem
Argument das unbekannte Wort stammt — dann führt sie zur Ursache statt an ihr
vorbei.

## Was ich schon versucht habe

Behelf: keine doppelten Anführungszeichen in Notiztexten, stattdessen einfache
Anführungszeichen oder Gedankenstriche. Der zweite Aufruf mit derselben Notiz
ohne die zwei Zeichen lief durch.
