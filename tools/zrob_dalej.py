#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Doklada zdjecia do kafelkow "Co czytac dalej" na koncu podstron.

Uzycie:
    python tools/zrob_dalej.py           # dopisz zdjecia
    python tools/zrob_dalej.py --sucho   # pokaz, co by sie zmienilo

Bloki z odnosnikami do powiazanych tematow byly czystym tekstem, przez co
koniec kazdej podstrony wygladal jak spis literatury. Zdjecie bierze sie
z adresu odnosnika - ta sama tablica, ktora przypisuje zdjecia naglowkom,
wiec kafelek prowadzacy do /schroniska/ pokazuje to samo zdjecie, ktore
zobaczysz po klliknieciu.

Skrypt rozpoznaje wlasna robote po klasie nx-dalej__foto i nie dubluje.
"""

import argparse
import glob
import io
import os
import re
import sys

KATALOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zrob_hero import ZDJECIA, WYMIARY, DOMYSLNE_WYMIARY  # noqa: E402

# Starsze podstrony maja kontener nazwany "-dalej__grid", nowsze samo
# "-dalej". Lapiemy oba, zeby nie zostawiac polowy serwisu bez zdjec.
WZOR_BLOK = re.compile(r'(<div class="[a-z-]+-dalej(?:__grid)?">)(.*?)(\n *</div>)', re.S)
WZOR_LINK = re.compile(r'( *)<a href="\.\./([a-z-]+)/">\n')

# Strony bez wlasnego zdjecia w naglowku - kafelek i tak musi cos pokazac,
# inaczej w jednej siatce polowa jest z obrazkiem, a polowa bez.
ZAPASOWE = {
    "narzedzia": ("apteczka", u"Zawartość apteczki dla psa rozłożona na jasnym blacie"),
    "mapa": ("spacer", u"Pies na smyczy idzie chodnikiem obok tramwaju"),
    "rozdzialy": ("prawnik", u"Pies siedzi przy biurku z książką prawniczą"),
    "podcast": ("spacer", u"Pies na smyczy idzie chodnikiem obok tramwaju"),
    "zatrucia": ("apteczka", u"Zawartość apteczki dla psa rozłożona na jasnym blacie"),
}


def main():
    parser = argparse.ArgumentParser(description="Zdjecia w kafelkach powiazanych tematow.")
    parser.add_argument("--sucho", action="store_true", help="nie zapisuj, tylko pokaz")
    args = parser.parse_args()

    zmienione = 0
    for wzgledna in sorted(glob.glob(os.path.join("*", "index.html"))):
        sciezka = os.path.join(KATALOG, wzgledna)
        html = io.open(sciezka, encoding="utf-8").read()
        if "nx-dalej__foto" in html:
            continue

        dodane = [0]

        def przerob_blok(m):
            poczatek, srodek, koniec = m.groups()

            def przerob_link(lm):
                wciecie, cel = lm.groups()
                wpis = ZDJECIA.get(cel) or ZAPASOWE.get(cel)
                if wpis is None:
                    return lm.group(0)
                plik, alt = wpis
                szer, wys = WYMIARY.get(plik, DOMYSLNE_WYMIARY)
                dodane[0] += 1
                return (
                    '%s<a class="nx-dalej--zfoto" href="../%s/">\n'
                    '%s  <span class="nx-dalej__foto">\n'
                    '%s    <img src="../assets/photos/%s.webp" alt="%s"\n'
                    '%s         width="%d" height="%d" loading="lazy" />\n'
                    '%s  </span>\n'
                    % (wciecie, cel, wciecie, wciecie, plik, alt,
                       wciecie, szer, wys, wciecie)
                )

            return poczatek + WZOR_LINK.sub(przerob_link, srodek) + koniec

        nowy = WZOR_BLOK.sub(przerob_blok, html)
        if not dodane[0]:
            continue
        zmienione += 1
        nazwa = os.path.dirname(wzgledna)
        if args.sucho:
            print("%-18s %d kafelkow" % (nazwa, dodane[0]))
        else:
            io.open(sciezka, "w", encoding="utf-8", newline="").write(nowy)
            print("%-18s %d kafelkow ze zdjeciem" % (nazwa, dodane[0]))

    print("stron ze zmianami: %d" % zmienione)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
