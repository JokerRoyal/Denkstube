# Die Denkstube

Zwei Räume in einer App, ohne Internet, ohne Server, ohne Konto:

1. **Gedächtnistraining** — 200 Stationen in zwanzig Wegstücken, 35 Spielarten,
   Tagesziel von zehn bis fünfzehn Minuten, Wettstreit per Ergebniskarte.
2. **Die Kräuterkammer** — Lernkasten für die Drogenliste nach verwendeten
   Pflanzenteilen: 40 Karten, Karteikasten nach Leitner, acht Übungen,
   Vorlesefunktion und die Pflanzentafeln aus Köhlers Medizinal-Pflanzen (1887).

Alles steckt in der Datei, gerechnet wird im Gerät. Nichts verlässt das Handy.

**Zum Spielen:** <https://jokerroyal.github.io/Denkstube/>
(gilt, sobald GitHub Pages eingeschaltet ist — siehe unten)

## Was hier liegt

| Datei | wofür |
|---|---|
| `der-merkweg.html` | **die Quelldatei.** Hier wird entwickelt. Sie ist für die Artifact-Umgebung geschrieben, also ohne `<html>`/`<head>`. |
| `bau-pwa.py` | baut daraus `docs/`, die Einzeldatei und das Zip |
| `docs/` | die fertige App, wie GitHub Pages sie ausliefert |
| `docs/bilder/` | die Köhler-Tafeln, über `hol-tafeln.py` geholt und geprüft |
| `hol-tafeln.py` | holt die Tafeln über die Commons-Kategorie der jeweiligen Art; `tafeln-bericht.txt` sagt, was warum durchfiel |
| `Die-Denkstube-offline.html` | dieselbe App als **eine** Datei — zum Verschicken per Mail |
| `Denkstube-pwa.zip` | `docs/` gezippt, für Netlify Drop |
| `ANLEITUNG-HANDY.md` | Schritt für Schritt aufs Handy |

## Etwas ändern

1. `der-merkweg.html` bearbeiten.
2. In `bau-pwa.py` die Zeile `VERSION = '…'` hochzählen — sonst behalten schon
   installierte Handys die alte Fassung im Speicher.
3. `python bau-pwa.py`
4. `git add -A && git commit -m "…" && git push`

Auf dem Handy kommt die neue Fassung beim nächsten Start von allein an.

## GitHub Pages einschalten (einmalig)

Im Repository: **Settings → Pages → Source: „Deploy from a branch"**,
Branch `main`, Ordner **`/docs`** → *Save*. Nach einer Minute läuft die App
unter der Adresse oben.

Das Repository muss dafür **öffentlich** sein (Pages für private Repositories
gehört zum Bezahlplan). In der App stecken keine persönlichen Daten — was auf
den Rastplätzen erzählt wird, bleibt ausschließlich im Speicher des jeweiligen
Geräts.

## Die Kräuterkammer

Der Stoff ist das Seminarblatt „Drogenliste nach verwendeten Pflanzenteilen",
Seite 1. **Der Wortlaut in `DROGEN` ist bindend** — Name, Hauptwirkstoffe und
Anwendungsgebiet stehen exakt so da wie auf dem Blatt. Wer hier umformuliert,
ändert den Prüfungsstoff.

Die Bilder sind gemeinfreie Tafeln aus *Köhler's Medizinal-Pflanzen* (1887).
Geholt werden sie nicht über eine Bildersuche, sondern über die
Commons-Kategorie der botanischen Art — und nur, wenn die Datei dort wirklich
einsortiert ist. Was sich nicht eindeutig zuordnen lässt, bekommt kein Bild,
sondern das Symbol seiner Gruppe. Lieber kein Bild als ein falsches.

Scans des Seminarblatts gehören nicht in dieses Repository.
