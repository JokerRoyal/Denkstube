# Die Denkstube aufs Handy — ohne Internet

Die App ist **eine einzige Seite ohne Server**: alle hundert Level, alle Aufgaben
und der Fortschritt stecken im Gerät. Sie muss nur einmal aufs Handy kommen.

Die Claude-Adresse (`claude.ai/artifact/…`) taugt dafür **nicht**: die braucht
Internet *und* einen Claude-Login, Mama könnte sie gar nicht öffnen. Deshalb die
zwei Wege hier.

---

## Weg 1 — die einzelne Datei verschicken (zwei Minuten, kein Konto)

1. `Die-Denkstube-offline.html` per Mail an Mama schicken (WhatsApp mag HTML
   manchmal nicht; Mail oder ein USB-Kabel gehen immer).
2. Auf dem Handy die Datei antippen → sie öffnet sich im Browser.
   *Android:* in „Dateien" speichern, dann mit Chrome öffnen.
   *iPhone:* Anhang → „In Dateien speichern", dann in der Dateien-App antippen.
3. Fertig. Läuft ab jetzt ohne Netz.

**Ein Nachteil, den du kennen solltest:** Bei einer so geöffneten Datei sperren
manche Handys den Speicher. Dann spielt alles normal, aber Sterne und Tage in
Folge sind beim nächsten Öffnen weg. Wenn das passiert → Weg 2.

---

## Weg 2 — als richtige App auf den Startbildschirm (empfohlen, ~10 Minuten)

Damit bekommt sie ein eigenes Symbol (Honigblüte auf Gartengrün), startet ohne
Browserleiste, läuft offline und merkt sich den Fortschritt zuverlässig.

### a) Den Ordner ins Netz stellen

Nötig ist eine Adresse mit `https`. Zwei einfache Möglichkeiten:

**Netlify Drop** (am schnellsten)
1. `Denkstube-pwa.zip` bereitlegen (liegt neben dieser Anleitung; enthält den Inhalt von `docs/`).
2. Auf <https://app.netlify.com/drop> gehen.
3. Das Zip ins Feld ziehen. Nach ein paar Sekunden steht da eine Adresse wie
   `https://irgendwas-1234.netlify.app`.
4. Diese Adresse aufs Handy schicken. (Ohne Konto bleibt die Seite nur kurze
   Zeit; mit kostenlosem Konto dauerhaft und du kannst sie umbenennen.)

**GitHub Pages** (dauerhaft, kostenlos — empfohlen)
Ausführlich steht das in der Antwort im Chat; kurz:
1. Auf <https://github.com/new> ein **öffentliches** Repository `denkstube` anlegen,
   ohne Häkchen bei README/Lizenz.
2. Im Projektordner (PowerShell im Ordner `Denkstube`):
   ```
   git remote add origin https://github.com/DEIN-NAME/denkstube.git
   git push -u origin master
   ```
3. Im Repository: **Settings → Pages → Source: „Deploy from a branch"**,
   Branch `master`, Ordner **`/docs`** → Save.
4. Nach einer Minute läuft sie unter
   `https://DEIN-NAME.github.io/denkstube/`.

### b) Auf dem Handy installieren

**Android (Chrome):** Adresse öffnen → Menü ⋮ → **„App installieren"** bzw.
„Zum Startbildschirm hinzufügen" → bestätigen.

**iPhone (Safari — wichtig, nicht Chrome):** Adresse öffnen → Teilen-Symbol
(Quadrat mit Pfeil) → **„Zum Home-Bildschirm"** → „Hinzufügen".

### c) Einmal online starten, dann Flugmodus prüfen

Beim ersten Start legt die App sich selbst im Gerät ab (Service Worker). Danach:
Flugmodus einschalten, Symbol antippen — sie muss normal starten. Das ist der
Beweis, dass es offline läuft.

---

## Für Mama einstellen (einmal, in den Einstellungen ☼)

- **Ansicht: Hell** — falls das Handy dunkel eingestellt ist und sie es heller mag.
- **Schriftgröße: Groß** oder **Sehr groß**.
- **Mehr Zeit zum Merken**, wenn die Merkzeiten zu knapp sind.
- **Tagesziel: 10 oder 12 Minuten**.
- Die App kann sich nicht selbst melden. Wenn eine Erinnerung gewünscht ist:
  im Handy einen wiederkehrenden Wecker auf immer dieselbe Uhrzeit stellen.

---

## Wenn du an der App etwas änderst

1. In `der-merkweg.html` ändern (das ist die einzige Quelldatei).
2. `python bau-pwa.py` — baut `docs/`, die Einzeldatei und das Zip neu.
3. In `bau-pwa.py` die Zeile `VERSION = '5'` hochzählen. Sonst behalten schon
   installierte Handys die alte Fassung im Speicher.
4. Neu hochladen. Auf dem Handy passiert die Aktualisierung beim nächsten Start
   von allein.

---

## Was mit den Daten passiert

Nichts verlässt das Handy. Sterne, Minuten und die Texte von den Rastplätzen
liegen ausschließlich im Speicher des Browsers auf ihrem Gerät — es gibt keinen
Server, kein Konto, keine Anmeldung. Umgekehrt heißt das aber auch: **Ein
Handywechsel oder ein gelöschter Browserspeicher nimmt den Fortschritt mit.**
Und falls du Weg 2 wählst: die Adresse selbst ist öffentlich — wer sie kennt,
kann die App öffnen. Zu sehen bekommt er nur das leere Spiel, nie ihre Daten.
