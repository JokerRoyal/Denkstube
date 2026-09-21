# Die Denkstube

Gedächtnistraining in hundert Stationen — ruhig, bunt, ohne Internet.
Eine einzige Seite ohne Server: alle Aufgaben, Wortlisten und Geschichten
stecken in der Datei, gerechnet wird im Gerät. Nichts verlässt das Handy.

**Zum Spielen:** `https://DEIN-GITHUB-NAME.github.io/denkstube/`
(die Adresse gilt, sobald GitHub Pages eingeschaltet ist — siehe unten;
DEIN-GITHUB-NAME bitte einmal ersetzen)

## Was hier liegt

| Datei | wofür |
|---|---|
| `der-merkweg.html` | **die Quelldatei.** Hier wird entwickelt. Sie ist für die Artifact-Umgebung geschrieben, also ohne `<html>`/`<head>`. |
| `bau-pwa.py` | baut daraus `docs/`, die Einzeldatei und das Zip |
| `docs/` | die fertige App, wie GitHub Pages sie ausliefert |
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
Branch `master`, Ordner **`/docs`** → *Save*. Nach einer Minute läuft die App
unter der Adresse oben.

Das Repository muss dafür **öffentlich** sein (Pages für private Repositories
gehört zum Bezahlplan). In der App stecken keine persönlichen Daten — was auf
den Rastplätzen erzählt wird, bleibt ausschließlich im Speicher des jeweiligen
Geräts.
