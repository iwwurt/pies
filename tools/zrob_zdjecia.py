#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Przerabia zdjecia z katalogu roboczego na WebP do assets/photos/.

Uzycie:
    python tools/zrob_zdjecia.py "C:/Users/uto4k/Desktop/23424"

Generatory obrazow oddaja PNG-i po pare megabajtow. Strona nie moze ich
podawac w takiej postaci - jeden taki plik wazy wiecej niz cala reszta
strony razem wzietej. Skrypt skaluje je do rozsadnej szerokosci i zapisuje
jako WebP, ktore przy tej samej jakosci wizualnej sa mniej wiecej
dwudziestokrotnie mniejsze.

Szerokosci sa dwie, bo zdjecia trafiaja w dwa miejsca: 1400 px na szerokie
kadry w naglowkach stron i 1120 px na pionowy portret.
"""

import io
import os
import sys

from PIL import Image

KATALOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEL = os.path.join(KATALOG, "assets", "photos")

# nazwa zrodlowa (bez rozszerzenia) -> maksymalna szerokosc
PLIKI = {
    "prawnik": 1400,
    "zdrowie": 1400,
    "apteczka": 1400,
    "spacer": 1400,
    "psiecko": 1400,
    "schronisko": 1400,
    "senior": 1400,
    "szczeniak": 1400,
    "portret": 1120,
}

JAKOSC = 80


def main():
    if len(sys.argv) < 2:
        print("podaj katalog ze zdjeciami", file=sys.stderr)
        return 1
    zrodlo = sys.argv[1]
    if not os.path.isdir(zrodlo):
        print("nie ma katalogu: %s" % zrodlo, file=sys.stderr)
        return 1

    if not os.path.isdir(CEL):
        os.makedirs(CEL)

    razem_przed = 0
    razem_po = 0
    for nazwa, szerokosc in sorted(PLIKI.items()):
        wejscie = None
        for rozszerzenie in (".png", ".jpg", ".jpeg", ".webp"):
            kandydat = os.path.join(zrodlo, nazwa + rozszerzenie)
            if os.path.exists(kandydat):
                wejscie = kandydat
                break
        if wejscie is None:
            print("%-14s BRAK PLIKU ZRODLOWEGO" % nazwa, file=sys.stderr)
            continue

        obraz = Image.open(wejscie).convert("RGB")
        if obraz.width > szerokosc:
            wysokosc = round(obraz.height * szerokosc / obraz.width)
            obraz = obraz.resize((szerokosc, wysokosc), Image.LANCZOS)

        wyjscie = os.path.join(CEL, nazwa + ".webp")
        obraz.save(wyjscie, "WEBP", quality=JAKOSC, method=6)

        przed = os.path.getsize(wejscie)
        po = os.path.getsize(wyjscie)
        razem_przed += przed
        razem_po += po
        print("%-14s %4dx%-4d  %6.1f kB  (bylo %.1f MB)"
              % (nazwa, obraz.width, obraz.height, po / 1024.0, przed / 1048576.0))

    print("razem: %.1f MB -> %.0f kB" % (razem_przed / 1048576.0, razem_po / 1024.0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
