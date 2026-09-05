#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Wpina (albo wypina) licznik odwiedzin na wszystkich stronach serwisu.

Uzycie:
    python tools/zrob_analityke.py --cloudflare TOKEN
    python tools/zrob_analityke.py --goatcounter NAZWAKONTA
    python tools/zrob_analityke.py --usun
    python tools/zrob_analityke.py --stan

Dlaczego akurat te dwa liczniki, a nie Google Analytics: oba licza bez
ciasteczek i bez identyfikowania osoby, wiec strona nie potrzebuje banera
zgody. GA4 stawia ciasteczka, a przy ruchu z Polski oznacza to obowiazkowy
baner - na stronie, ktora rozdaje ksiazke za darmo, jest to koszt bez
korzysci.

Skrypt wstawia snippet tuz przed </body> i oznacza go komentarzem, zeby
dalo sie go pozniej znalezc i usunac jednym poleceniem. Uruchomiony
drugi raz nie duplikuje wpisu - najpierw usuwa stary.
"""

import argparse
import glob
import io
import os
import re
import sys

KATALOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ZNACZNIK_POCZATEK = "    <!-- licznik odwiedzin -->"
ZNACZNIK_KONIEC = "    <!-- /licznik odwiedzin -->"

WZOR = re.compile(
    re.escape(ZNACZNIK_POCZATEK) + r".*?" + re.escape(ZNACZNIK_KONIEC) + r"\n",
    re.S,
)


def snippet_cloudflare(token):
    # Dokladnie taka postac, jaka podaje kreator Cloudflare: type="module"
    # i bez defer, bo moduly sa odroczone z definicji. Beacon jest wydawany
    # jako modul ES, wiec wciagniecie go jako zwyklego skryptu potrafi sie
    # wywrocic - dlatego nie "poprawiam" tego zapisu.
    return (
        '    <script\n'
        '      type="module"\n'
        '      src="https://static.cloudflareinsights.com/beacon.min.js"\n'
        '      data-cf-beacon=\'{"token": "%s"}\'\n'
        '    ></script>\n' % token
    )


def snippet_goatcounter(konto):
    return (
        '    <script\n'
        '      data-goatcounter="https://%s.goatcounter.com/count"\n'
        '      async\n'
        '      src="//gc.zgo.at/count.js"\n'
        '    ></script>\n' % konto
    )


def strony():
    poprzedni = os.getcwd()
    os.chdir(KATALOG)
    try:
        return sorted(glob.glob("*/index.html")) + ["index.html", "404.html"]
    finally:
        os.chdir(poprzedni)


def main():
    parser = argparse.ArgumentParser(description="Licznik odwiedzin na calym serwisie.")
    grupa = parser.add_mutually_exclusive_group(required=True)
    grupa.add_argument("--cloudflare", metavar="TOKEN",
                       help="token z Cloudflare Web Analytics")
    grupa.add_argument("--goatcounter", metavar="KONTO",
                       help="nazwa konta w GoatCounter, bez .goatcounter.com")
    grupa.add_argument("--usun", action="store_true", help="wypnij licznik ze wszystkich stron")
    grupa.add_argument("--stan", action="store_true", help="pokaz, gdzie licznik juz jest")
    args = parser.parse_args()

    if args.cloudflare:
        blok = ZNACZNIK_POCZATEK + "\n" + snippet_cloudflare(args.cloudflare) + ZNACZNIK_KONIEC + "\n"
        opis = "Cloudflare Web Analytics"
    elif args.goatcounter:
        blok = ZNACZNIK_POCZATEK + "\n" + snippet_goatcounter(args.goatcounter) + ZNACZNIK_KONIEC + "\n"
        opis = "GoatCounter"
    else:
        blok = None
        opis = None

    zmienione = 0
    for wzgledna in strony():
        sciezka = os.path.join(KATALOG, wzgledna)
        h = io.open(sciezka, encoding="utf-8").read()

        if args.stan:
            print("%-26s %s" % (wzgledna, "jest" if WZOR.search(h) else "-"))
            continue

        nowy = WZOR.sub("", h)

        if blok is not None:
            if "  </body>" not in nowy:
                print("%-26s BRAK ZAMKNIECIA BODY" % wzgledna, file=sys.stderr)
                continue
            nowy = nowy.replace("  </body>", blok + "  </body>", 1)

        if nowy == h:
            continue
        zmienione += 1
        io.open(sciezka, "w", encoding="utf-8", newline="").write(nowy)

    if args.stan:
        return 0
    if blok is None:
        print("licznik usuniety z %d stron" % zmienione)
    else:
        print("%s wpiety na %d stronach" % (opis, zmienione))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
