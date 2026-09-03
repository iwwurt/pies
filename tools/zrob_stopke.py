#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Przepisuje blok odnosnikow w stopce na wszystkich stronach serwisu.

Uzycie:
    python tools/zrob_stopke.py           # przepisz stopki
    python tools/zrob_stopke.py --sucho   # pokaz, co by sie zmienilo

Stopka jest jedynym miejscem, ktore trzeba ruszyc przy KAZDEJ nowej
podstronie, i wlasnie dlatego psula sie najczesciej: raz strona linkowala
sama do siebie, raz brakowalo jej w stopkach pozostalych. Skrypt liczy to
za kazdym razem od nowa z tablicy KOLUMNY ponizej, wiec dodanie sekcji to
jedna linijka w jednym pliku.

Cztery kolumny odpowiadaja czterem czesciom ksiazki pokazywanym na
stronie glownej. Strona nie linkuje sama do siebie - jej pozycja jest
w danej kolumnie pomijana.

Skrypt podmienia wylacznie fragment miedzy <nav class="site-footer__kolumny">
a zamykajacym </nav>. Reszty stopki (znak wodny, nota prawna) nie dotyka.
"""

import argparse
import glob
import io
import os
import re
import sys

KATALOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (etykieta, cel, rodzaj) - rodzaj decyduje o prefiksie i atrybutach:
#   strona     - podstrona serwisu, sciezka wzgledna, pomijana na samej sobie
#   kotwica    - miejsce na stronie glownej
#   plik       - pobieranie, dostaje atrybut download
#   zewnetrzny - pelny adres, otwierany w nowej karcie
KOLUMNY = [
    ("Książka", [
        ("Pobierz książkę", "pliki/Pies-w-Polsce-2026-cala-ksiazka.pdf", "plik"),
        ("O książce", "o-ksiazce/", "strona"),
        ("61 rozdziałów", "#rozdzialy", "kotwica"),
        ("Podcast", "#podcast", "kotwica"),
        ("Checklista", "#checklista", "kotwica"),
        ("Kanał YouTube", "https://www.youtube.com/@PieswPolsce", "zewnetrzny"),
        ("Nagrania na Dysku Google",
         "https://drive.google.com/drive/folders/1g86EYIpOq0Y_I152-HYB8P9jFjz8trbG",
         "zewnetrzny"),
    ]),
    ("Prawo", [
        ("KROPiK i czipowanie", "kropik/", "strona"),
        ("Pogryzienie", "ugryzienie/", "strona"),
        ("Pies w bloku", "mieszkanie/", "strona"),
        ("Transport", "transport/", "strona"),
        ("Pies po rozwodzie", "rozwod/", "strona"),
        ("Kamera i RODO", "kamera/", "strona"),
        ("Rasy agresywne", "rasy-agresywne/", "strona"),
        ("Odebranie psa", "odebranie-psa/", "strona"),
    ]),
    ("Zdrowie", [
        ("Zatrucia", "zatrucia/", "strona"),
        ("Kleszcze", "kleszcze/", "strona"),
        ("Apteczka", "apteczka/", "strona"),
        ("Lęk separacyjny", "lek-separacyjny/", "strona"),
        ("Gdy pies umiera", "smierc-psa/", "strona"),
    ]),
    ("Codzienność", [
        ("Adopcja i wybór psa", "adopcja/", "strona"),
        ("Schroniska w liczbach", "schroniska/", "strona"),
        ("Koszty", "koszty/", "strona"),
        ("Zaginiony pies", "zaginiony/", "strona"),
        ("Narzędzia", "narzedzia/", "strona"),
        ("Mapa lecznic", "mapa/", "strona"),
    ]),
]

WZOR = re.compile(r'        <nav class="site-footer__kolumny".*?\n        </nav>\n', re.S)


def zbuduj(prefiks, wlasna):
    linie = ['        <nav class="site-footer__kolumny" aria-label="Mapa serwisu">']
    for nazwa, pozycje in KOLUMNY:
        wiersze = []
        for etykieta, cel, rodzaj in pozycje:
            if rodzaj == "strona" and cel == wlasna:
                continue
            if rodzaj == "zewnetrzny":
                adres, atrybuty = cel, ' target="_blank" rel="noopener"'
            elif rodzaj == "kotwica":
                adres, atrybuty = (cel if prefiks == "" else prefiks + cel), ""
            elif rodzaj == "plik":
                adres, atrybuty = prefiks + cel, " download"
            else:
                adres, atrybuty = prefiks + cel, ""
            wiersze.append('              <li><a href="%s"%s>%s</a></li>'
                           % (adres, atrybuty, etykieta))
        if not wiersze:
            continue
        linie.append('          <div class="site-footer__kolumna">')
        linie.append('            <p class="site-footer__naglowek">%s</p>' % nazwa)
        linie.append('            <ul>')
        linie.extend(wiersze)
        linie.append('            </ul>')
        linie.append('          </div>')
    linie.append("        </nav>")
    return "\n".join(linie) + "\n"


def strony():
    poprzedni = os.getcwd()
    os.chdir(KATALOG)
    try:
        return sorted(glob.glob("*/index.html")) + ["index.html", "404.html"]
    finally:
        os.chdir(poprzedni)


def main():
    parser = argparse.ArgumentParser(description="Stopka serwisu w czterech kolumnach.")
    parser.add_argument("--sucho", action="store_true", help="nie zapisuj, tylko pokaz zmiany")
    args = parser.parse_args()

    zmienione = 0
    for wzgledna in strony():
        sciezka = os.path.join(KATALOG, wzgledna)
        h = io.open(sciezka, encoding="utf-8").read()
        katalog = os.path.dirname(wzgledna).replace("\\", "/")
        if wzgledna == "index.html":
            prefiks, wlasna = "", None
        elif wzgledna == "404.html":
            prefiks, wlasna = "/", None
        else:
            prefiks, wlasna = "../", katalog + "/"

        if not WZOR.search(h):
            print("%-26s BRAK BLOKU STOPKI" % wzgledna, file=sys.stderr)
            return 1

        nowa = WZOR.sub(lambda _: zbuduj(prefiks, wlasna), h, count=1)
        if nowa == h:
            print("%-26s bez zmian" % wzgledna)
            continue
        zmienione += 1
        if not args.sucho:
            io.open(sciezka, "w", encoding="utf-8", newline="").write(nowa)
        print("%-26s %s" % (wzgledna, "do zmiany" if args.sucho else "zapisane"))

    print("stron ze zmianami: %d" % zmienione)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
