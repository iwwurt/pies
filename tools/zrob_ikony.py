#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generuje ikony PWA do assets/ikony/ na podstawie assets/favicon.svg.

Uzycie:
    python tools/zrob_ikony.py

Rysuje ta sama lapke i te same kolory, co favicon - zielone tlo #4f5b43
i zlota lapka #e5a33f - zeby ikona na ekranie telefonu byla rozpoznawalna
jako ta sama marka, co karta w zakladce przegladarki.

Powstaja trzy pliki:
    icon-192.png       - minimalna wymagana wielkosc dla instalacji
    icon-512.png       - ekran powitalny i sklepy
    icon-maskable.png  - z marginesem bezpieczenstwa, zeby Android mogl
                         przyciac ikone do kola albo kwadratu z zaokragleniem
                         bez obcinania lapki

Rysunek powstaje w poczwornej skali i jest zmniejszany, wiec krawedzie
elipsy sa gladkie mimo braku wygladzania w samym PIL.
"""

import os

from PIL import Image, ImageDraw

KATALOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEL = os.path.join(KATALOG, "assets", "ikony")

TLO = (79, 91, 67)       # #4f5b43 - jak w favicon.svg
LAPKA = (229, 163, 63)   # #e5a33f
SKALA = 4


def elipsa(rysunek, srodek, promienie, obrot=0):
    """Elipsa z opcjonalnym obrotem - PIL nie umie tego wprost, wiec
    rysujemy ja na osobnej warstwie i obracamy."""
    rx, ry = promienie
    warstwa = Image.new("RGBA", (int(rx * 4), int(ry * 4)), (0, 0, 0, 0))
    d = ImageDraw.Draw(warstwa)
    d.ellipse(
        [warstwa.width / 2 - rx, warstwa.height / 2 - ry,
         warstwa.width / 2 + rx, warstwa.height / 2 + ry],
        fill=LAPKA,
    )
    if obrot:
        warstwa = warstwa.rotate(obrot, resample=Image.BICUBIC, expand=False)
    rysunek.paste(
        warstwa,
        (int(srodek[0] - warstwa.width / 2), int(srodek[1] - warstwa.height / 2)),
        warstwa,
    )


def narysuj(rozmiar, margines=0.0):
    """margines 0.1 zostawia 10% wolnego z kazdej strony - dla wariantu maskable."""
    bok = rozmiar * SKALA
    obraz = Image.new("RGB", (bok, bok), TLO)
    # wszystkie wspolrzedne sa z favicon.svg w ukladzie 64x64
    pole = bok * (1 - 2 * margines)
    odstep = bok * margines
    s = pole / 64.0

    def xy(x, y):
        return (odstep + x * s, odstep + y * s)

    elipsa(obraz, xy(18, 18), (6 * s, 9 * s), obrot=30)
    elipsa(obraz, xy(32, 13), (6 * s, 9 * s))
    elipsa(obraz, xy(46, 18), (6 * s, 9 * s), obrot=-30)
    elipsa(obraz, xy(53, 31), (5 * s, 8 * s), obrot=-35)
    # opuszka - w svg to sciezka, tu wystarczy elipsa o tych samych proporcjach
    elipsa(obraz, xy(31, 42), (18 * s, 14 * s))

    return obraz.resize((rozmiar, rozmiar), Image.LANCZOS)


def main():
    os.makedirs(CEL, exist_ok=True)
    plany = [
        ("icon-192.png", 192, 0.06),
        ("icon-512.png", 512, 0.06),
        ("icon-maskable.png", 512, 0.12),
    ]
    for nazwa, rozmiar, margines in plany:
        sciezka = os.path.join(CEL, nazwa)
        narysuj(rozmiar, margines).save(sciezka, optimize=True)
        print("assets/ikony/%-20s %5.1f kB" % (nazwa, os.path.getsize(sciezka) / 1024))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
