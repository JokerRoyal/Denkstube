# -*- coding: utf-8 -*-
"""
Baut aus der Drogenliste gedruckte Lernkarten: Lernkarten-Kraeuterkammer.pdf

Vier Karten je A4-Blatt (A6, 105 x 148,5 mm), vorne das Bild, hinten
Hauptwirkstoff und Anwendungsgebiet — Wortlaut unveraendert aus der App.

Die Rueckseiten sind **spiegelverkehrt angeordnet**, damit beim beidseitigen
Drucken (Wenden an der langen Kante) hinter jedem Bild der richtige Text
landet. Die Seiten wechseln sich ab: vorne, hinten, vorne, hinten ...

Aufruf:  python lernkarten.py
"""

import io, os, re

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = os.path.join(HIER, 'der-merkweg.html')
BILDER = os.path.join(HIER, 'docs', 'bilder')
ZIEL = os.path.join(HIER, 'Lernkarten-Kraeuterkammer.pdf')

TINTE = HexColor('#242a22')
MOOS = HexColor('#44703f')
GRAU = HexColor('#8a9181')
LINIE = HexColor('#c9cfbe')

GRUPPEN = {
    'blatt': 'Blattdroge', 'bluete': 'Blütendroge', 'frucht': 'Fruchtdroge',
    'kraut': 'Krautdroge', 'rinde': 'Rindendroge', 'samen': 'Samendroge',
    'wurzel': 'Wurzeldroge',
}


def drogen_lesen():
    """Die Karten kommen aus der App — eine Quelle, kein zweiter Datenstand."""
    text = io.open(QUELLE, encoding='utf-8').read()
    anfang = text.index('const DROGEN = [')
    ende = text.index('\n];', anfang)
    block = text[anfang:ende]
    raus = []
    for stueck in re.finditer(
            r"\{n:'([^']+)', g:'([a-z]+)',(?: b:'([^']+)', q:'([ka])',)? w:\[([^\]]*)\],\s*\n?\s*a:'([^']+)'\}",
            block):
        name, gruppe, bild, werk, wirk, anwendung = stueck.groups()
        wirkstoffe = [w.strip().strip("'") for w in wirk.split("','")]
        wirkstoffe = [w.strip("'") for w in wirkstoffe]
        raus.append({'n': name, 'g': gruppe, 'b': bild, 'q': werk,
                     'w': ', '.join(wirkstoffe), 'a': anwendung})
    return raus


def bildgroesse(pfad):
    try:
        from PIL import Image
        with Image.open(pfad) as b:
            return b.size
    except Exception:
        return (420, 600)


def vorderseite(c, x, y, breite, hoehe, d, nummer):
    rand = 7 * mm
    c.setFillColor(GRAU)
    c.setFont('Helvetica-Bold', 7)
    c.drawString(x + rand, y + hoehe - rand - 6, GRUPPEN[d['g']].upper())
    c.setFont('Helvetica', 7)
    c.drawRightString(x + breite - rand, y + hoehe - rand - 6, '%d von 40' % nummer)

    # Bildfeld
    feld_x, feld_breite = x + rand, breite - 2 * rand
    feld_unten = y + rand + 16 * mm
    feld_hoehe = hoehe - rand - 12 * mm - (feld_unten - y)
    pfad = os.path.join(BILDER, d['b']) if d['b'] else None
    if pfad and os.path.exists(pfad):
        bw, bh = bildgroesse(pfad)
        faktor = min(feld_breite / bw, feld_hoehe / bh)
        zb, zh = bw * faktor, bh * faktor
        c.drawImage(pfad, feld_x + (feld_breite - zb) / 2, feld_unten + (feld_hoehe - zh) / 2,
                    zb, zh, preserveAspectRatio=True, anchor='c', mask=None)
    else:
        c.setFillColor(HexColor('#f1f3e7'))
        c.roundRect(feld_x, feld_unten, feld_breite, feld_hoehe, 4, stroke=0, fill=1)
        c.setFillColor(GRAU)
        c.setFont('Helvetica-Bold', 11)
        c.drawCentredString(x + breite / 2, feld_unten + feld_hoehe / 2 + 4, GRUPPEN[d['g']])
        c.setFont('Helvetica', 8)
        c.drawCentredString(x + breite / 2, feld_unten + feld_hoehe / 2 - 9, '(keine gemeinfreie Abbildung)')

    # Name unten — zum Abdecken, wer sich selbst abfragen will
    c.setFillColor(TINTE)
    name = d['n']
    groesse = 16 if len(name) < 22 else 12.5
    c.setFont('Helvetica-Bold', groesse)
    c.drawCentredString(x + breite / 2, y + rand + 6 * mm, name)
    if d['b']:
        c.setFillColor(GRAU)
        c.setFont('Helvetica', 5.5)
        quelle = ('Köhlers Medizinal-Pflanzen, 1887 — gemeinfrei' if d['q'] == 'k'
                  else 'Historische Pflanzentafel — gemeinfrei')
        c.drawCentredString(x + breite / 2, y + rand + 1.5 * mm, quelle)


def rueckseite(c, x, y, breite, hoehe, d, nummer):
    rand = 8 * mm
    c.setFillColor(GRAU)
    c.setFont('Helvetica-Bold', 7)
    c.drawString(x + rand, y + hoehe - rand - 6, GRUPPEN[d['g']].upper())
    c.setFont('Helvetica', 7)
    c.drawRightString(x + breite - rand, y + hoehe - rand - 6, '%d von 40' % nummer)

    name = d['n']
    innen = breite - 2 * rand
    stil_wirk = ParagraphStyle('wirk', fontName='Helvetica-Bold', fontSize=12.5, leading=16,
                               textColor=TINTE)
    stil_anw = ParagraphStyle('anw', fontName='Helvetica', fontSize=12.5, leading=17,
                              textColor=TINTE)
    p_wirk = Paragraph(d['w'], stil_wirk)
    _, h_wirk = p_wirk.wrap(innen, 40 * mm)
    p_anw = Paragraph(d['a'], stil_anw)
    _, h_anw = p_anw.wrap(innen, 80 * mm)

    # alles zusammen mittig setzen, statt oben kleben zu lassen
    h_name, h_strich, h_abstand = 18, 16, 9
    gesamt = h_name + h_strich + 10 + h_wirk + 18 + 10 + h_anw
    oben = y + (hoehe + gesamt) / 2

    c.setFillColor(TINTE)
    c.setFont('Helvetica-Bold', 16 if len(name) < 22 else 12.5)
    c.drawCentredString(x + breite / 2, oben - h_name, name)

    c.setStrokeColor(LINIE)
    c.setLineWidth(.8)
    strich_y = oben - h_name - h_strich + 4
    c.line(x + breite / 2 - 10 * mm, strich_y, x + breite / 2 + 10 * mm, strich_y)

    zeile = strich_y - h_abstand - 7
    c.setFillColor(MOOS)
    c.setFont('Helvetica-Bold', 7.5)
    c.drawString(x + rand, zeile, 'HAUPTWIRKSTOFF')
    p_wirk.drawOn(c, x + rand, zeile - 5 - h_wirk)

    zeile2 = zeile - h_wirk - 18
    c.setFillColor(MOOS)
    c.setFont('Helvetica-Bold', 7.5)
    c.drawString(x + rand, zeile2, 'ANWENDUNGSGEBIET')
    p_anw.drawOn(c, x + rand, zeile2 - 5 - h_anw)


def schnittlinien(c, breite, hoehe):
    c.setStrokeColor(LINIE)
    c.setLineWidth(.4)
    c.setDash(2, 3)
    c.line(breite / 2, 0, breite / 2, hoehe)
    c.line(0, hoehe / 2, breite, hoehe / 2)
    c.setDash()


def main():
    drogen = drogen_lesen()
    if len(drogen) != 40:
        print('ACHTUNG: %d Karten gefunden, erwartet waren 40' % len(drogen))
    breite, hoehe = A4
    kb, kh = breite / 2, hoehe / 2
    # Platz 0 oben links, 1 oben rechts, 2 unten links, 3 unten rechts
    plaetze = [(0, kh), (kb, kh), (0, 0), (kb, 0)]
    gespiegelt = [1, 0, 3, 2]          # Wenden an der langen Kante

    c = canvas.Canvas(ZIEL, pagesize=A4)
    c.setTitle('Lernkarten — Drogenliste nach verwendeten Pflanzenteilen')
    c.setAuthor('Die Denkstube')

    for start in range(0, len(drogen), 4):
        vier = drogen[start:start + 4]
        schnittlinien(c, breite, hoehe)
        for i, d in enumerate(vier):
            x, y = plaetze[i]
            vorderseite(c, x, y, kb, kh, d, start + i + 1)
        c.showPage()
        schnittlinien(c, breite, hoehe)
        for i, d in enumerate(vier):
            x, y = plaetze[gespiegelt[i]]
            rueckseite(c, x, y, kb, kh, d, start + i + 1)
        c.showPage()

    # letzte Seite: wie man es druckt
    c.setFillColor(TINTE)
    c.setFont('Helvetica-Bold', 16)
    c.drawString(25 * mm, hoehe - 35 * mm, 'So werden daraus Karten')
    zeilen = [
        '1. Beidseitig drucken, Wenden an der LANGEN Kante.',
        '2. Keine Skalierung — in den Druckeinstellungen „Tatsächliche Größe“ oder 100 %.',
        '3. Entlang der gestrichelten Linien schneiden: vier Karten je Blatt (A6).',
        '',
        'Vorne steht das Bild und der Name, hinten Hauptwirkstoff und Anwendungsgebiet.',
        'Wer sich die Pflanze selbst abfragen will, deckt den Namen unten mit dem Daumen ab.',
        '',
        'Fünf Drogen haben keine Abbildung (Weißdorn, Heidelbeere, Spitzwegerich,',
        'Flohsamen, Kürbissamen) — dort steht nur die Gruppe. Für sie gibt es keine',
        'gemeinfreie Tafel, die sich zweifelsfrei zuordnen ließ.',
        '',
        'Die Texte stehen Wort für Wort so wie auf dem Seminarblatt, Seite 1.',
        'Bilder: Köhlers Medizinal-Pflanzen (1887) und andere gemeinfreie Tafeln.',
    ]
    c.setFont('Helvetica', 10.5)
    y = hoehe - 48 * mm
    for z in zeilen:
        c.drawString(25 * mm, y, z)
        y -= 6.2 * mm
    c.showPage()
    c.save()
    print('PDF gebaut: %s (%d Karten, %d Seiten)' % (ZIEL, len(drogen), len(drogen) // 2 + 1))


if __name__ == '__main__':
    main()
