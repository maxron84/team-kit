# Der gedruckte Lauf-Betrag und die Turn-Aufzaehlung darunter beschreiben verschiedene Mengen

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Gewachsen (zwölf Kaskaden), Windows, **nur pwsh-Bahn**, Python + Electron, rund 480 Tests.

## Was passiert ist

Eine Kaskade wurde in **zwei** Vollautomatik-Läufen gebaut: Lauf 1 baute eine
Stufe und stoppte im vierten Ausgang, Lauf 2 baute den Rest und fuhr Red Team
und Fixphase. Der Abschlussbericht von Lauf 2 endet so (Zahlen gerundet
wiedergegeben, Struktur wörtlich):

```
[..] Dieser Lauf: 18.8551 USD (Deckel 70). Gesamt-Kontostand: <..> USD.
[..]   6 Lauf/Laeufe, 279 Turns (Schnitt 46.5).
[..]       61 Turns          3.0520 USD  stufe-56-<stempel>.json
[..]       54 Turns          3.4519 USD  stufe-58-<stempel>.json
[..]       53 Turns          2.7258 USD  stufe-57-<stempel>.json
[..]       48 Turns          2.2178 USD  stufe-59-<stempel>.json
[..]       36 Turns          1.8959 USD  stufe-60-<stempel>.json
[..]       27 Turns          2.0605 USD  stufe-61-<stempel>.json
```

**Die sechs aufgezählten Zeilen summieren sich auf 15,4039 — nicht auf die
18,8551 zwei Zeilen darüber.** Beide Zahlen sind für sich richtig, sie zählen
nur Verschiedenes:

- **18,8551** ist Lauf 2 **vollständig**: die fünf Stufen dieses Laufs (12,3519)
  plus die Rollen-Läufe, die der Bericht nirgends einzeln nennt (zwei Sweeps,
  zwei Fixe).
- **Die Aufzählung** listet den **Log-Ordner**, und darin liegt zusätzlich die
  Stufe aus **Lauf 1** — dafür fehlt ihr jeder Rollen-Lauf.

Keine der beiden Mengen ist der ganze Lauf, und keine ist die ganze Kaskade. Die
Kaskade kostete über beide Läufe 21,9071 in den Bau- und Rollenzeilen.

## Wo es steckt

Im Abschlussbericht der Vollautomatik (`team/lib.psm1` / `team/lib.sh`, der
Block, der „Dieser Lauf: … USD" druckt und danach das Turn-Profil).

Der Betrag stammt aus der **Lauf-Buchhaltung** (was dieser Prozess seit seinem
Start ausgegeben hat, alle Rollen), das Profil aus dem **Ralph-Log-Ordner** (was
dort gerade liegt, unabhängig davon, welcher Lauf es hineingeschrieben hat).
Solange eine Kaskade in genau einem Lauf gebaut wird und man die Rollen-Kosten
nicht vermisst, fallen beide Mengen zusammen — deshalb fällt es lange nicht auf.

## Warum das jede Installation trifft

**Der zweite Lauf ist kein Sonderfall, sondern eingeplantes Verhalten.** Genau
diese Mehrläufigkeit erzeugen die benannten Ausgänge des Kits selbst: der vierte
Ausgang (Stufe fertig, Quittung fehlt) und der Abbruch am Lauf-Deckel. Beide
enden mit „von Hand quittieren, dann erneut starten" — also mit einem zweiten
Lauf über derselben Kaskade und einem Log-Ordner, der nun beide enthält.

Der Bericht ist zugleich die Quelle, aus der man den Ledger füllt, wenn man ihn
nicht ohnehin über `--rollen-abschluss` füllen lässt: Es ist die einzige Stelle,
an der eine Gesamtzahl steht. Wer die falsche der beiden Zahlen nimmt, bucht
**15,40 oder 18,86 statt 21,91** — und beide Zahlen stehen zwei Zeilen
auseinander, ohne dass etwas auf den Wechsel der Bezugsmenge hinweist.

Verschärfend: Die Zeile „6 Lauf/Laeufe, 279 Turns" liest sich wie eine
Aufschlüsselung des Betrags darüber. Die Turn-Zahl **ist** die des Log-Ordners,
der Betrag **ist** der des Prozesses — sie stehen in einer Zeile beieinander und
gehören verschiedenen Mengen an.

## Was ich schon versucht habe

- **Beide Mengen nachgerechnet**, aus den Rohlogs und aus dem Ledger; daher die
  Zuordnung oben. Die Differenz von 3,4512 zwischen Aufzählung und Betrag löst
  sich exakt in „Stufe aus Lauf 1 herausrechnen, Rollen-Läufe hinzurechnen" auf.
- **Kein lokaler Fix** — der Befund sitzt in der Bibliothek.

**Drei Richtungen, aufsteigend im Aufwand:**

- **(a)** Der Betragszeile ihre Menge geben: „Dieser Lauf (alle Rollen seit
  Start): …". Kostet eine Zeile und macht den Rest lesbar.
- **(b)** Die Aufzählung auf denselben Lauf begrenzen (Logs nach Startzeit des
  Laufs filtern — die Altersprüfung aus `BL-221` kann das bereits) und die
  Rollen-Läufe mit auflisten, damit sich das Profil auf den Betrag summiert.
- **(c)** Eine zweite Zeile für die **Kaskade** (über alle Läufe), da das die
  Zahl ist, die am Ende ins Abschluss-Protokoll gehört. Sie ist heute nur über
  das Ledger zu bekommen, also erst nach dem Abschluss.
