#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Przebudowuje naglowki podstron: zorza w tle i zdjecie obok tekstu.

Uzycie:
    python tools/zrob_hero.py           # przebuduj
    python tools/zrob_hero.py --sucho   # pokaz, co by sie zmienilo

Podstrony powstawaly przez tydzien i kazda miala wlasny naglowek: sam
tekst na plaskim tle. Po zmianie wygladu strony glownej roznica byla
widoczna od razu - glowna wygladala na rok 2026, podstrony na dokument.

Skrypt nie rusza tresci naglowka. Bierze to, co juz jest w <div class="shell">,
pakuje w lewa kolumne i dokleja prawa ze zdjeciem. Dzieki temu strony
z wlasnymi widgetami w naglowku (przyciski KROPiK, wyszukiwarka mapy,
zakladki narzedzi) nie tracza niczego - a te, ktore widgetow potrzebuja
na calej szerokosci, po prostu nie dostaja zdjecia.

Uruchomiony drugi raz nie duplikuje niczego: rozpoznaje wlasna robote
po klasie nx-hero2 i pomija takie strony.
"""

import argparse
import io
import os
import re
import sys

KATALOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# strona -> (plik zdjecia, tekst alternatywny)
ZDJECIA = {
    "adopcja": ("schronisko", u"Pies w schronisku patrzy przez kraty boksu"),
    "apteczka": ("apteczka", u"Zawartość apteczki dla psa rozłożona na jasnym blacie"),
    "dziecko": ("psiecko", u"Pies leży na dywanie, dziecko siedzi w bezpiecznej odległości"),
    "kamera": ("prawnik", u"Pies siedzi przy biurku z książką prawniczą"),
    "kleszcze": ("zdrowie", u"Lekarka weterynarii bada psa stetoskopem"),
    "koszty": ("szczeniak", u"Szczeniak podnosi łapę na jasnej podłodze"),
    "kropik": ("prawnik", u"Pies siedzi przy biurku z książką prawniczą"),
    "lek-separacyjny": ("senior", u"Starszy pies opiera głowę na kolanie właściciela"),
    "mieszkanie": ("prawnik", u"Pies siedzi przy biurku z książką prawniczą"),
    "odebranie-psa": ("schronisko", u"Pies w schronisku patrzy przez kraty boksu"),
    "psy-asystujace": ("spacer", u"Pies na smyczy idzie chodnikiem obok tramwaju"),
    "rasy-agresywne": ("prawnik", u"Pies siedzi przy biurku z książką prawniczą"),
    "rozwod": ("prawnik", u"Pies siedzi przy biurku z książką prawniczą"),
    "schroniska": ("schronisko", u"Pies w schronisku patrzy przez kraty boksu"),
    "smierc-psa": ("senior", u"Starszy pies opiera głowę na kolanie właściciela"),
    "spadek": ("senior", u"Starszy pies opiera głowę na kolanie właściciela"),
    "szkolenie": ("szczeniak", u"Szczeniak podnosi łapę na jasnej podłodze"),
    "transport": ("spacer", u"Pies na smyczy idzie chodnikiem obok tramwaju"),
    "ugryzienie": ("zdrowie", u"Lekarka weterynarii bada psa stetoskopem"),
    "zaginiony": ("spacer", u"Pies na smyczy idzie chodnikiem obok tramwaju"),
    "o-ksiazce": ("portret", u"Golden retriever siedzi na wprost obiektywu"),
}

# Naglowki, ktore zostaja jednokolumnowe: ich widgety potrzebuja calej
# szerokosci (wyszukiwarka mapy, zakladki narzedzi). Dostaja sama zorze.
BEZ_ZDJECIA = {"mapa", "narzedzia"}

WYMIARY = {"portret": (1120, 1400)}
DOMYSLNE_WYMIARY = (1400, 788)

AURORA = '          <div class="nx-aurora" aria-hidden="true"><i></i><i></i><i></i></div>\n'


def foto_html(nazwa, alt):
    szerokosc, wysokosc = WYMIARY.get(nazwa, DOMYSLNE_WYMIARY)
    return (
        '            <figure class="nx-hero2__foto">\n'
        '              <img\n'
        '                src="../assets/photos/%s.webp"\n'
        '                alt="%s"\n'
        '                width="%d"\n'
        '                height="%d"\n'
        '                fetchpriority="high"\n'
        '              />\n'
        '            </figure>\n' % (nazwa, alt, szerokosc, wysokosc)
    )


def przebuduj(html, slug):
    """Zwraca (nowy_html, opis) albo (None, powod_pominiecia)."""
    if 'class="nx-hero2' in html:
        return None, "juz przebudowany"

    dopasowanie = re.search(
        r'( *)<section class="([a-z-]*hero[a-z-]*)">\n'
        r'( *)<div class="shell">\n'
        r'(.*?)\n'
        r'( *)</div>\n'
        r'( *)</section>\n',
        html, re.S)
    if not dopasowanie:
        return None, "nie rozpoznaje naglowka"

    wciecie_sekcji, klasa, wciecie_shell, srodek, _, wciecie_konca = dopasowanie.groups()

    if slug in BEZ_ZDJECIA:
        nowy = (
            '%s<section class="%s nx-hero2 nx-hero2--pelny">\n' % (wciecie_sekcji, klasa)
            + AURORA
            + '%s<div class="shell">\n' % wciecie_shell
            + srodek + '\n'
            + '%s</div>\n' % wciecie_shell
            + '%s</section>\n' % wciecie_konca
        )
        return html[:dopasowanie.start()] + nowy + html[dopasowanie.end():], "bez zdjecia"

    if slug not in ZDJECIA:
        return None, "brak przypisanego zdjecia"

    plik, alt = ZDJECIA[slug]
    # Istniejaca tresc wjezdza w lewa kolumne bez zmian - tylko wciecie
    # rosnie o dwie spacje, zeby kod dalo sie dalej czytac.
    przesuniety = "\n".join(("  " + w if w.strip() else w) for w in srodek.split("\n"))
    nowy = (
        '%s<section class="%s nx-hero2">\n' % (wciecie_sekcji, klasa)
        + AURORA
        + '%s<div class="shell nx-hero2__siatka">\n' % wciecie_shell
        + '            <div class="nx-hero2__tresc">\n'
        + przesuniety + '\n'
        + '            </div>\n'
        + foto_html(plik, alt)
        + '%s</div>\n' % wciecie_shell
        + '%s</section>\n' % wciecie_konca
    )
    return html[:dopasowanie.start()] + nowy + html[dopasowanie.end():], plik


def main():
    parser = argparse.ArgumentParser(description="Naglowki podstron ze zdjeciem.")
    parser.add_argument("--sucho", action="store_true", help="nie zapisuj, tylko pokaz")
    args = parser.parse_args()

    slugi = sorted(set(list(ZDJECIA) + list(BEZ_ZDJECIA)))
    zmienione = 0
    for slug in slugi:
        sciezka = os.path.join(KATALOG, slug, "index.html")
        if not os.path.exists(sciezka):
            print("%-18s BRAK STRONY" % slug, file=sys.stderr)
            continue
        html = io.open(sciezka, encoding="utf-8").read()
        nowy, opis = przebuduj(html, slug)
        if nowy is None:
            print("%-18s pominieta (%s)" % (slug, opis))
            continue
        zmienione += 1
        if args.sucho:
            print("%-18s do zmiany (%s)" % (slug, opis))
        else:
            io.open(sciezka, "w", encoding="utf-8", newline="").write(nowy)
            print("%-18s zapisane (%s)" % (slug, opis))

    print("stron ze zmianami: %d" % zmienione)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
