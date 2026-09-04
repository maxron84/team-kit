# Bahn: pwsh | Gegenstueck: kit-melden.sh
<#
  kit-melden.ps1 — Rueckkanal Feld -> Kit: einen Fund am T.E.A.M. SELBST melden.

  Fuer Funde an deinem PROJEKT ist dieses Skript falsch — die gehoeren ins
  Beutebuch bzw. in den Backlog des Projekts. Hier geht es um Fehler in der
  Team-Infrastruktur: in team/, in einem Entrypoint (*.cmd in der Wurzel) oder
  in einer Regel aus CLAUDE.md/TEAM.md. Erkennungsmerkmal: Der Fehler trifft
  jede weitere Installation, und dieses Projekt repariert ihn bei jedem
  `-Update` aufs Neue.

  Aufruf:
    .\kit-melden.cmd neu --titel "…"     Entwurf nach Vorlage anlegen
    .\kit-melden.cmd pruefen             Redaktionspruefung (Exit 4 = Befunde)
    .\kit-melden.cmd ablegen <datei>     ins lokal liegende Kit legen + committen
    .\kit-melden.cmd senden <datei>      Pull Request — fragt vorher
    .\kit-melden.cmd issue-link <datei>  nur den vorbefuellten Link
    .\kit-melden.cmd kit-pfad            wo liegt das Kit? (Diagnose)

  WARUM SENDEN EINE EIGENE HANDLUNG IST: Ein Pull Request wirkt nach aussen und
  laesst sich nicht zurueckholen, und die Meldung schreibt eine Rolle, die
  gerade eine private Codebasis gelesen hat. `neu` und `pruefen` duerfen
  automatisch laufen, `senden` nicht — dieselbe Trennung wie "Finder != Fixer".

  ABLEGEN ODER SENDEN (BL-227, der Rest von BL-187): Liegt das Kit geklont
  daneben und zeigt TEAM_KIT_PFAD darauf, ist `ablegen` der Weg — es committet
  PFADGENAU ins Kit und pusht NICHT. `senden` ist fuer Melder OHNE Kit-Repo.
  Ein Owner, der einen Pull Request gegen sein eigenes Repo anlegt, reviewt und
  merged seine eigene Meldung; BL-187 hat das festgestellt und Rollen-Briefing,
  TEAM.md und CLAUDE.md.vorlage nachgezogen — dieser Hilfetext blieb stehen.
  Wer das Werkzeug ueber seine eigene Hilfe erschliesst, fand deshalb weiter
  nur `senden`, also genau den Weg, von dem BL-187 sagt, dass er hier der
  falsche ist.

  `ablegen` ist dabei nicht das lockerere `senden`, sondern das straffere: kein
  Push (den macht ein Mensch, der den Text gelesen hat), keine BL-Nummer (die
  vergibt der Maintainer beim Triage, sonst waere der Nummernraum ein Wettlauf
  zwischen Meldern, die voneinander nichts wissen) und die Redaktionspruefung
  als VORBEDINGUNG, nicht als Empfehlung — was hier durchgeht, liegt im
  Eingangskorb eines oeffentlichen Repos.
#>
$ErrorActionPreference = 'Stop'
# BL-122: Ein Exit-Code != 0 aus einem nativen Befehl soll ein WERT bleiben,
# kein terminierender Fehler — sonst ist Exit 4 der Redaktionspruefung
# unerreichbar. Ausfuehrliche Begruendung in team-test.ps1.
$PSNativeCommandUseErrorActionPreference = $false
Set-Location $PSScriptRoot
# BL-182, dritte Haelfte: `-DisableNameChecking` tragen die neun anderen
# Entrypoints seit jeher, diese eine Datei nicht. Ohne den Schalter schreibt
# Import-Module eine WARNING ueber "unapproved verbs" (Team-Werkzeug, Team-Pfad
# — "Team" ist kein genehmigtes Verb) — und zwar nach STDOUT, mit ANSI-Farbe,
# VOR der eigentlichen Ausgabe. `neu` gibt den PFAD der angelegten Meldung auf
# stdout aus; wer ihn wegliest, bekam die Warnzeile mit. Gesehen hat das nie
# jemand, weil der Aufruf eine Zeile spaeter ohnehin abbrach.
Import-Module (Join-Path $PSScriptRoot 'team/lib.psm1') -Force -DisableNameChecking

# Die Werte werden AUSDRUECKLICH durchgereicht statt exportiert: Ein Werkzeug,
# das seine Eingaben aus der Umgebung erraet, verhaelt sich je nach Aufrufer
# anders — und der Aufrufer ist hier mal ein Mensch, mal eine Rolle, mal ein
# Test. Dieselbe Bauart wie bei beutebuch.py (--pfad).
$meldungen = (Join-Path ($TEAM_PLAN_ORDNER.TrimEnd('/')) 'kit-meldungen')

# BL-182: Die Werkzeugzeile kommt aus der Konfiguration und wird von
# Team-Werkzeug zerlegt — dieselbe Bauart wie bei beutebuch.py und kosten.py.
# Die Fassung davor rief `& $TEAM_PYTHON team/tools/kit_meldung.py` auf. Diese
# Variable gibt es NUR auf der bash-Bahn (team.config.sh, lib.sh); hier war sie
# leer, und `&` auf eine leere Zeichenkette bricht ab ("The expression after '&'
# … must result in a command name"), Exit 1. Betroffen war JEDES Verb, weil
# alle durch diese eine Zeile laufen — der Rueckkanal Feld -> Kit war auf
# dieser Bahn seit dem ersten Tag tot, ohne dass es je jemand gesehen hat.
#
# Die Schalter stehen VOR dem Verb: kit_meldung.py liest sie am Hauptparser,
# der Unterbefehl kommt danach. Deshalb `$args` ans ENDE, nicht an den Anfang.
Team-Werkzeug $TEAM_MELDUNG_TOOL (@(
    '--projektwurzel', '.',
    '--meldungen', $meldungen,
    '--kit', "$(if ($TEAM_KIT_PFAD) { $TEAM_KIT_PFAD } else { '' })",
    '--projekt', "$(if ($TEAM_PROJEKT) { $TEAM_PROJEKT } else { '' })",
    # BL-168: Unter welchem Kuerzel dieses Projekt im Kit gefuehrt wird. Es
    # lebte bis 2026-08-26 nur im Kit-README, also ausserhalb der Installation,
    # die es nennen muesste.
    '--kuerzel', "$(if ($TEAM_FELD_KUERZEL) { $TEAM_FELD_KUERZEL } else { '' })"
) + $args)
exit $LASTEXITCODE
