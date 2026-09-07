# Der Rollback der Fixphase setzt hart auf einen gemerkten Commit zurueck und wirft fremde Commits weg, die waehrenddessen entstanden sind

- **Art**: Fehler am Kit
- **Kit-Version**: 2.13.1
- **Bahn**: pwsh
- **Plattform**: win32
- **Feldkürzel**: Feld B
- **Lage des Projekts**: Bestandsprojekt, Windows, pwsh-Bahn, Python plus
  Electron-Oberfläche; elfte Kaskade, rund 460 Tests, knapp 50 Funde.

## Was passiert ist

Während ein Fix-Lauf für einen Fund arbeitete, hat eine **zweite, interaktive
Sitzung** im selben Arbeitsbaum einen eigenen Commit angelegt — einen reinen
Doku-Commit an der Fundliste, ohne eine Datei zu berühren, die der Fix-Lauf
anfasste.

Nach dem Fix-Lauf war dieser Commit **aus der Historie verschwunden**. Der
Reflog zeigt, was passierte (Hashes gekürzt):

```
ab11542 HEAD@{0}: commit: docs: ... Status fuer den Fix
b3b895d HEAD@{1}: commit: fix(uat): ... (der Fix selbst)
baf86e4 HEAD@{2}: reset: moving to baf86e45...      <- haerteter Rueckgriff
da7c6a2 HEAD@{3}: commit: docs(beute): ...          <- der fremde Commit
baf86e4 HEAD@{4}: ...
```

Der Lauf hat sich beim Start `baf86e4` als Basis gemerkt und später hart
dorthin zurückgesetzt. Dass die Spitze inzwischen `da7c6a2` war — ein Commit,
den er nicht angelegt hatte —, hat ihn nicht aufgehalten. Der fremde Commit
war anschließend nur noch über den Reflog erreichbar und wurde von Hand per
`git cherry-pick` zurückgeholt.

**Nichts hat gemeldet, dass dabei ein Commit verloren ging.** Der Lauf endete
mit seiner normalen Erfolgsmeldung; die Fundliste sah vollständig aus, weil der
Verlust genau den Eintrag traf, den die zweite Sitzung gerade hinzugefügt
hatte. Aufgefallen ist es nur, weil dieselbe Person kurz darauf nach dem
eigenen Eintrag suchte und ihn nicht fand.

## Wo es steckt

Der Rollback-Pfad der Fixphase (`team/lib.psm1` bzw. `team/lib.sh`, der
Zweig, der nach einem gescheiterten oder verworfenen Versuch aufräumt). Er
setzt auf den beim Start gemerkten Commit zurück, ohne zu prüfen, ob `HEAD`
zum Zeitpunkt des Zurücksetzens noch derselbe ist.

## Warum das jede Installation trifft

**Der Loop ist ausdrücklich dafür gebaut, dass ein Mensch daneben
weiterarbeitet.** Genau das ist die Arbeitsteilung, die das Kit beschreibt:
Der Loop baut headless, während der Mensch plant, abnimmt oder dokumentiert.
Ein Rollback, der die Spitze der Historie für seine eigene hält, ist mit dieser
Arbeitsteilung unvereinbar — und je besser das Team eingespielt ist, desto
öfter greift der Fall.

Der Verlust ist dabei **still und asymmetrisch**: Der Loop schreibt seine
eigenen Commits korrekt, nur die des Menschen verschwinden. Wer nicht zufällig
nach seinem eigenen Eintrag sucht, merkt es nie — und im Reflog steht er nur so
lange, bis die Garbage Collection ihn abräumt.

Zwei Stellen, an denen es zusätzlich weh tut:

1. Ein verlorener **Fund-Eintrag** nimmt dem nächsten Lauf seine Arbeit weg:
   `first 'an Frank übergeben'` findet den Fund nicht mehr, und der Lauf meldet
   „nichts zu tun" — dieselbe Endstelle wie der bereits gemeldete Fall der
   falsch geschriebenen Statuszeile.
2. Ein verlorener **Plan-/Doku-Commit** verschwindet ohne Konflikt, ohne
   Warnung und ohne Spur in der Historie.

## Was ich schon versucht habe

Zurückgeholt per `git cherry-pick <hash>` aus dem Reflog — der Commit
existierte noch als Objekt, der Merge lief ohne Konflikt durch.

Vorschlag, falls er hilft: Vor dem harten Zurücksetzen prüfen, ob `HEAD` noch
der gemerkten Basis oder einem selbst angelegten Commit entspricht. Ist die
Spitze fremd, gibt es zwei gangbare Wege — den Rollback abbrechen und den Fall
an den Menschen geben (die Bauform, die das Kit für den vierten Ausgang schon
kennt), oder statt `reset --hard` nur die eigenen Änderungen zurücknehmen. Der
erste Weg ist der billigere: Fremde Arbeit im Baum ist ein Fall für ein
Urteil, nicht für eine Automatik.
