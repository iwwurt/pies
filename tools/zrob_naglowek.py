#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Przepisuje naglowek i nawigacje na wszystkich stronach serwisu.

Uzycie:
    python tools/zrob_naglowek.py           # przepisz naglowki
    python tools/zrob_naglowek.py --sucho   # pokaz, co by sie zmienilo

Powod istnienia tego skryptu: kazda podstrona miala wlasny, recznie
dobrany zestaw odnosnikow w nawigacji. Efekt byl taki, ze przy przejsciu
miedzy stronami pozycje menu znikaly i podmienialy sie na inne - czytelnik
nie mial stalego punktu odniesienia. Teraz nawigacja jest jedna, ta sama
wszedzie, liczona z tablicy MENU ponizej.

Strona, na ktorej wlasnie jestesmy, dostaje aria-current="page" zamiast
byc usuwana z menu - pozycje maja stac w tym samym miejscu zawsze.

Pod pozycja "Poradniki" siedzi rozwijane menu z pelna lista podstron
tematycznych, pogrupowana tak samo jak stopka.
"""

import argparse
import glob
import io
import os
import re
import sys

KATALOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (etykieta, cel, rodzaj): strona | kotwica | plik | zewnetrzny | poradniki
MENU = [
    ("Książka", "o-ksiazce/", "strona"),
    ("Rozdziały", "rozdzialy/", "strona"),
    ("Podcast", "podcast/", "strona"),
    ("Poradniki", None, "poradniki"),
    ("Narzędzia", "narzedzia/", "strona"),
    ("Mapa", "mapa/", "strona"),
]

PORADNIKI = [
    ("Prawo", [
        ("KROPiK i czipowanie", "kropik/"),
        ("Pogryzienie", "ugryzienie/"),
        ("Pies w bloku", "mieszkanie/"),
        ("Transport", "transport/"),
        ("Pies asystujący", "psy-asystujace/"),
        ("Rasy agresywne", "rasy-agresywne/"),
        ("Pies po rozwodzie", "rozwod/"),
        ("Pies w spadku", "spadek/"),
        ("Odebranie psa", "odebranie-psa/"),
        ("Kamera i RODO", "kamera/"),
    ]),
    ("Zdrowie", [
        ("Zatrucia", "zatrucia/"),
        ("Kleszcze", "kleszcze/"),
        ("Apteczka", "apteczka/"),
        ("Lęk separacyjny", "lek-separacyjny/"),
        ("Gdy pies umiera", "smierc-psa/"),
    ]),
    ("Codzienność", [
        ("Adopcja i wybór psa", "adopcja/"),
        ("Pies i dziecko", "dziecko/"),
        ("Szkolenie psa", "szkolenie/"),
        ("Schroniska w liczbach", "schroniska/"),
        ("Koszty", "koszty/"),
        ("Zaginiony pies", "zaginiony/"),
    ]),
]

STRZALKA = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<path d="m6 9 6 6 6-6" /></svg>')

WZOR = re.compile(r'    <header class="site-header".*?\n    </header>\n', re.S)


def zbuduj(prefiks, wlasna):
    w = []
    d = '    '
    w.append(d + '<header class="site-header" data-header>')
    w.append(d + '  <div class="shell site-header__inner">')
    w.append(d + '    <a class="wordmark" href="%s" aria-label="Pies w Polsce — strona główna">'
             % (prefiks if prefiks else './'))
    w.append(d + '      <span class="wordmark__seal" aria-hidden="true">P</span>')
    w.append(d + '      <span class="wordmark__text">')
    w.append(d + '        <strong>Pies w Polsce</strong>')
    w.append(d + '        <small>Kochaj · Rozum · Szanuj</small>')
    w.append(d + '      </span>')
    w.append(d + '    </a>')
    w.append('')
    w.append(d + '    <button')
    w.append(d + '      class="menu-toggle"')
    w.append(d + '      type="button"')
    w.append(d + '      aria-expanded="false"')
    w.append(d + '      aria-controls="site-nav"')
    w.append(d + '      aria-label="Otwórz menu"')
    w.append(d + '      data-menu-toggle')
    w.append(d + '    >')
    w.append(d + '      <span></span><span></span><span></span>')
    w.append(d + '    </button>')
    w.append('')
    w.append(d + '    <nav class="site-nav" id="site-nav" aria-label="Główna nawigacja" data-nav>')

    wszystkie_poradniki = [cel for _, poz in PORADNIKI for _, cel in poz]

    for etykieta, cel, rodzaj in MENU:
        if rodzaj == "poradniki":
            otwarte = 'true' if wlasna in wszystkie_poradniki else 'false'
            w.append(d + '      <div class="nx-drop" data-drop>')
            w.append(d + '        <button class="nx-drop__trigger" type="button" '
                         'aria-expanded="false" data-drop-trigger>')
            w.append(d + '          Poradniki %s' % STRZALKA)
            w.append(d + '        </button>')
            w.append(d + '        <div class="nx-drop__panel">')
            for nazwa, pozycje in PORADNIKI:
                w.append(d + '          <div class="nx-drop__grupa">')
                w.append(d + '            <p>%s</p>' % nazwa)
                for pod_etykieta, pod_cel in pozycje:
                    biezaca = ' aria-current="page"' if pod_cel == wlasna else ''
                    w.append(d + '            <a href="%s%s"%s>%s</a>'
                             % (prefiks, pod_cel, biezaca, pod_etykieta))
                w.append(d + '          </div>')
            w.append(d + '        </div>')
            w.append(d + '      </div>')
            continue
        biezaca = ' aria-current="page"' if cel == wlasna else ''
        w.append(d + '      <a href="%s%s"%s>%s</a>' % (prefiks, cel, biezaca, etykieta))

    w.append(d + '      <a class="button button--primary button--compact" '
                 'href="%spliki/Pies-w-Polsce-2026-cala-ksiazka.pdf" download>' % prefiks)
    w.append(d + '        Pobierz za darmo')
    w.append(d + '      </a>')
    w.append(d + '    </nav>')
    w.append(d + '  </div>')
    w.append(d + '</header>')
    return "\n".join(w) + "\n"


def strony():
    poprzedni = os.getcwd()
    os.chdir(KATALOG)
    try:
        return sorted(glob.glob("*/index.html")) + ["index.html", "404.html"]
    finally:
        os.chdir(poprzedni)


def main():
    parser = argparse.ArgumentParser(description="Jedna nawigacja na calym serwisie.")
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
            print("%-26s BRAK NAGLOWKA" % wzgledna, file=sys.stderr)
            continue

        nowy = WZOR.sub(lambda _: zbuduj(prefiks, wlasna), h, count=1)
        if nowy == h:
            print("%-26s bez zmian" % wzgledna)
            continue
        zmienione += 1
        if args.sucho:
            print("%-26s do zmiany" % wzgledna)
        else:
            io.open(sciezka, "w", encoding="utf-8", newline="").write(nowy)
            print("%-26s zapisane" % wzgledna)

    print("stron ze zmianami: %d" % zmienione)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
