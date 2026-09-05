#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generuje karty Open Graph dla podstron serwisu do assets/og/.

Uzycie:
    python tools/zrob_og.py               # przerysuj wszystkie karty
    python tools/zrob_og.py kleszcze      # tylko wybrane sekcje
    python tools/zrob_og.py --lista       # wypisz sekcje i sciezki plikow

Karta ma 1200x630 px, czyli proporcje, ktorych oczekuja Facebook, LinkedIn,
WhatsApp, Signal i Telegram. Rysunek powstaje w dwukrotnej skali i dopiero
potem jest zmniejszany, dzieki czemu wlosowe linie i szeryfy nie strzepia sie.

Nic nie jest pobierane z sieci. Kroj pisma bierzemy z systemu (Palatino
Linotype i Segoe UI na Windows, DejaVu jako zapas), a caly rysunek to
gradient, ramka, lapka i tekst — zadnych zdjec, wiec plik wychodzi lekki.

Strona glowna zostaje przy assets/og.jpg ze zdjeciem psa: to okladka calego
serwisu i jedyna karta, na ktorej zdjecie ma sens.
"""

import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

KATALOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEL = os.path.join(KATALOG, "assets", "og")

SZER, WYS = 1200, 630
SKALA = 2

# Kolory zywcem z :root w styles.css, zeby karta i strona byly z jednej rodziny.
PAPIER_GORA = (248, 245, 239)
PAPIER_DOL = (238, 231, 220)
ATRAMENT = (37, 34, 31)
STONOWANY = (95, 90, 82)
ZLOTO_CIEMNE = (127, 90, 38)
ZLOTO_BLADE = (222, 205, 172)
ALARM = (125, 45, 31)
ALARM_BLADY = (226, 192, 182)

TONY = {
    "zloty": (ZLOTO_CIEMNE, ZLOTO_BLADE),
    "alarm": (ALARM, ALARM_BLADY),
}

PISMA = {
    "szeryf": ["pala.ttf", "georgia.ttf", "DejaVuSerif.ttf"],
    "szeryf_kursywa": ["palai.ttf", "georgiai.ttf", "DejaVuSerif-Italic.ttf"],
    "bezszeryfowy": ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"],
}

SCIEZKI_PISM = [
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
    "/usr/share/fonts/truetype/dejavu",
    "/Library/Fonts",
]

# Sekcje. "tytul" jest krotszy od <title> strony, bo na karcie liczy sie to,
# co widac na telefonie w jednej linijce podgladu. "dzial" to etykieta u gory,
# dzieki niej link od razu widac, z ktorej czesci serwisu pochodzi.
SEKCJE = [
    {
        "slug": "o-ksiazce",
        "dzial": "Książka",
        "tytul": "O książce",
        "podtytul": "618 stron, 61 rozdziałów, za darmo",
        "ton": "zloty",
    },
    {
        "slug": "kropik",
        "dzial": "Prawo",
        "tytul": "KROPiK — czipowanie psa",
        "podtytul": "Rejestr, obowiązek właściciela, terminy",
        "ton": "zloty",
    },
    {
        "slug": "koszty",
        "dzial": "Pieniądze",
        "tytul": "Ile kosztuje pies",
        "podtytul": "Start, miesiąc i rok utrzymania",
        "ton": "zloty",
    },
    {
        "slug": "narzedzia",
        "dzial": "Narzędzia",
        "tytul": "Narzędzia dla właściciela",
        "podtytul": "Kalkulatory, ściągi, listy kontrolne",
        "ton": "zloty",
    },
    {
        "slug": "mapa",
        "dzial": "Narzędzia",
        "tytul": "Weterynarz w pobliżu",
        "podtytul": "Lecznice i schroniska na mapie Polski",
        "ton": "zloty",
    },
    {
        "slug": "zatrucia",
        "dzial": "Nagły wypadek",
        "tytul": "Pies zjadł coś trującego",
        "podtytul": "Co robić, a czego nie robić nigdy",
        "ton": "alarm",
    },
    {
        "slug": "apteczka",
        "dzial": "Zdrowie",
        "tytul": "Apteczka dla psa",
        "podtytul": "Lista kontrolna do odhaczenia i wydruku",
        "ton": "zloty",
    },
    {
        "slug": "odebranie-psa",
        "dzial": "Prawo",
        "tytul": "Odebranie psa",
        "podtytul": "Trzy dni na odwołanie, nie czternaście",
        "ton": "zloty",
    },
    {
        "slug": "rasy-agresywne",
        "dzial": "Prawo",
        "tytul": "Rasy uznawane za agresywne",
        "podtytul": "Jedenaście ras, zezwolenie i ubezpieczenie",
        "ton": "zloty",
    },
    {
        "slug": "ugryzienie",
        "dzial": "Prawo",
        "tytul": "Pies kogoś ugryzł",
        "podtytul": "Kto odpowiada i co zrobić od razu",
        "ton": "zloty",
    },
    {
        "slug": "mieszkanie",
        "dzial": "Prawo",
        "tytul": "Pies w bloku i na wynajmie",
        "podtytul": "Wspólnota, umowa najmu, granice zakazów",
        "ton": "zloty",
    },
    {
        "slug": "transport",
        "dzial": "Prawo",
        "tytul": "Pies w podróży",
        "podtytul": "Auto, pociąg, komunikacja miejska",
        "ton": "zloty",
    },
    {
        "slug": "kleszcze",
        "dzial": "Zdrowie",
        "tytul": "Kleszcze u psa",
        "podtytul": "Objawy, ryzyko, jak usunąć kleszcza",
        "ton": "alarm",
    },
    {
        "slug": "zaginiony",
        "dzial": "Nagły wypadek",
        "tytul": "Zaginął pies",
        "podtytul": "Pierwsza godzina i co dalej",
        "ton": "alarm",
    },
    {
        "slug": "dziecko",
        "dzial": "Bezpieczeństwo",
        "tytul": "Pies i dziecko",
        "podtytul": "Protokół zapoznania i prawo, które działa inaczej",
        "ton": "zloty",
    },
    {
        "slug": "psy-asystujace",
        "dzial": "Prawo",
        "tytul": "Pies asystujący",
        "podtytul": "Gdzie muszą wpuścić — i dlaczego żółta wstążka nie wystarczy",
        "ton": "zloty",
    },
    {
        "slug": "spadek",
        "dzial": "Prawo",
        "tytul": "Pies w spadku",
        "podtytul": "Co się stanie, gdy zabraknie właściciela",
        "ton": "zloty",
    },
    {
        "slug": "smierc-psa",
        "dzial": "Zdrowie",
        "tytul": "Gdy pies umiera",
        "podtytul": "Co mówi prawo i co wolno zrobić",
        "ton": "zloty",
    },
    {
        "slug": "lek-separacyjny",
        "dzial": "Zdrowie",
        "tytul": "Lęk separacyjny",
        "podtytul": "Dlaczego wyje i co z tym zrobić",
        "ton": "zloty",
    },
    {
        "slug": "schroniska",
        "dzial": "Codzienność",
        "tytul": "Schroniska w liczbach",
        "podtytul": "Oficjalne dane z raportu za 2024",
        "ton": "zloty",
    },
    {
        "slug": "adopcja",
        "dzial": "Pierwszy pies",
        "tytul": "Adopcja i wybór psa",
        "podtytul": "Schronisko, hodowla, pierwsze dni",
        "ton": "zloty",
    },
    {
        "slug": "kamera",
        "dzial": "Prawo",
        "tytul": "Kamera w domu a RODO",
        "podtytul": "Co wolno nagrywać we własnym mieszkaniu",
        "ton": "zloty",
    },
    {
        "slug": "rozwod",
        "dzial": "Prawo",
        "tytul": "Pies po rozwodzie",
        "podtytul": "Podział majątku a dobro zwierzęcia",
        "ton": "zloty",
    },
]


def znajdz_pismo(nazwy):
    """Zwraca sciezke do pierwszego kroju, ktory jest w systemie."""
    for nazwa in nazwy:
        for katalog in SCIEZKI_PISM:
            sciezka = os.path.join(katalog, nazwa)
            if os.path.exists(sciezka):
                return sciezka
    raise SystemExit(
        "Nie znaleziono zadnego z krojow: %s. Karty OG sa generowane lokalnie, "
        "wiec potrzebny jest kroj szeryfowy i bezszeryfowy w systemie." % ", ".join(nazwy)
    )


def gradient(obraz, gora, dol):
    """Pionowe przejscie miedzy dwoma kolorami, linia po linii."""
    rysunek = ImageDraw.Draw(obraz)
    wysokosc = obraz.height
    for y in range(wysokosc):
        t = y / (wysokosc - 1)
        kolor = tuple(round(g + (d - g) * t) for g, d in zip(gora, dol))
        rysunek.line([(0, y), (obraz.width, y)], fill=kolor)


def szerokosc_rozstrzelona(rysunek, tekst, pismo, odstep):
    if not tekst:
        return 0
    return sum(rysunek.textlength(z, font=pismo) for z in tekst) + odstep * (len(tekst) - 1)


def rozstrzel(rysunek, srodek_x, linia_bazowa, tekst, pismo, kolor, odstep):
    """Rysuje tekst ze swiatlem miedzy literami — PIL nie ma trackingu."""
    x = srodek_x - szerokosc_rozstrzelona(rysunek, tekst, pismo, odstep) / 2
    for znak in tekst:
        rysunek.text((x, linia_bazowa), znak, font=pismo, fill=kolor, anchor="ls")
        x += rysunek.textlength(znak, font=pismo) + odstep


def zawin(rysunek, tekst, pismo, maks_szerokosc):
    linie, biezaca = [], ""
    for slowo in tekst.split():
        proba = (biezaca + " " + slowo).strip()
        if biezaca and rysunek.textlength(proba, font=pismo) > maks_szerokosc:
            linie.append(biezaca)
            biezaca = slowo
        else:
            biezaca = proba
    if biezaca:
        linie.append(biezaca)
    return linie


def dopasuj(rysunek, tekst, sciezka_pisma, maks_szerokosc, rozmiary, maks_linii):
    """Najwiekszy rozmiar, ktory sie miesci — z pierwszenstwem dla jednej linii.

    Tytul lamany na dwie linie jest w podgladzie linku gorzej czytelny niz ten
    sam tytul o kilka punktow mniejszy, ale w calosci. Dlatego najpierw szukamy
    rozmiaru mieszczacego sie w jednej linii i dopiero gdy taki bylby juz za
    maly, schodzimy do lamania.
    """
    warianty = []
    for rozmiar in rozmiary:
        pismo = ImageFont.truetype(sciezka_pisma, rozmiar)
        warianty.append((pismo, zawin(rysunek, tekst, pismo, maks_szerokosc)))
    for pismo, linie in warianty:
        if len(linie) == 1:
            return pismo, linie
    for pismo, linie in warianty:
        if len(linie) <= maks_linii:
            return pismo, linie
    return warianty[-1]


def lapka(rysunek, srodek_x, srodek_y, rozmiar, kolor, grubosc):
    """Obrys psiej lapy — ten sam znak, co na okladce ksiazki."""
    r = rozmiar
    rysunek.ellipse(
        [srodek_x - 0.34 * r, srodek_y - 0.02 * r, srodek_x + 0.34 * r, srodek_y + 0.48 * r],
        outline=kolor,
        width=grubosc,
    )
    palce = [(-0.32, -0.16, 0.13, 0.19), (-0.11, -0.40, 0.13, 0.20),
             (0.11, -0.40, 0.13, 0.20), (0.32, -0.16, 0.13, 0.19)]
    for dx, dy, rx, ry in palce:
        rysunek.ellipse(
            [srodek_x + (dx - rx) * r, srodek_y + (dy - ry) * r,
             srodek_x + (dx + rx) * r, srodek_y + (dy + ry) * r],
            outline=kolor,
            width=grubosc,
        )


def karta(sekcja, pismo_tytul, pismo_tekst):
    akcent, blady = TONY[sekcja["ton"]]
    s = SKALA
    obraz = Image.new("RGB", (SZER * s, WYS * s), PAPIER_GORA)
    gradient(obraz, PAPIER_GORA, PAPIER_DOL)
    d = ImageDraw.Draw(obraz)
    srodek = SZER * s / 2

    d.rounded_rectangle(
        [38 * s, 38 * s, (SZER - 38) * s, (WYS - 38) * s],
        radius=20 * s,
        outline=blady,
        width=2,
    )

    dzial = ImageFont.truetype(pismo_tekst, 19 * s)
    rozstrzel(d, srodek, 112 * s, sekcja["dzial"].upper(), dzial, akcent, 5 * s)

    lapka(d, srodek, 152 * s, 28 * s, akcent, 3)
    for znak in (-1, 1):
        d.line(
            [(srodek + znak * 34 * s, 152 * s), (srodek + znak * 196 * s, 152 * s)],
            fill=blady,
            width=2,
        )

    tytul, linie = dopasuj(
        d, sekcja["tytul"], pismo_tytul, 880 * s, [78 * s, 70 * s, 62 * s, 55 * s], 2
    )
    podtytul, linie_p = dopasuj(
        d, sekcja["podtytul"], pismo_tekst, 800 * s, [28 * s, 25 * s, 22 * s], 2
    )
    wznos, opad = tytul.getmetrics()
    wznos_p, opad_p = podtytul.getmetrics()
    wysokosc_linii = (wznos + opad) * 1.1
    wysokosc_linii_p = (wznos_p + opad_p) * 1.25

    # Tytul, kreska i podtytul to jeden blok wysrodkowany miedzy lapka a
    # adresem na dole. Bez tego dwuliniowy tytul dosuwal podtytul do adresu.
    blok = (
        wysokosc_linii * len(linie)
        + 34 * s
        + 46 * s
        + wysokosc_linii_p * len(linie_p)
    )
    gora = 194 * s + ((524 - 194) * s - blok) / 2

    baza = gora + wznos
    for linia in linie:
        d.text((srodek, baza), linia, font=tytul, fill=ATRAMENT, anchor="ms")
        baza += wysokosc_linii

    kreska_y = gora + wysokosc_linii * len(linie) + 34 * s
    d.line([(srodek - 46 * s, kreska_y), (srodek + 46 * s, kreska_y)], fill=akcent, width=4)

    baza_p = kreska_y + 46 * s + wznos_p
    for linia in linie_p:
        d.text((srodek, baza_p), linia, font=podtytul, fill=STONOWANY, anchor="ms")
        baza_p += wysokosc_linii_p

    adres = ImageFont.truetype(pismo_tekst, 18 * s)
    rozstrzel(d, srodek, 562 * s, "pieswpolsce.pl/%s/" % sekcja["slug"], adres, akcent, 3 * s)

    return obraz.resize((SZER, WYS), Image.LANCZOS)


def zapisz(obraz, sciezka):
    """Paleta zamiast pelnego RGB: karta to plaskie tlo i tekst, wiec 256
    kolorow wystarcza, a plik schodzi z setek kilobajtow do kilkudziesieciu."""
    obraz.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG).save(
        sciezka, optimize=True
    )
    return os.path.getsize(sciezka)


def main():
    parser = argparse.ArgumentParser(description="Karty Open Graph dla podstron.")
    parser.add_argument("sekcje", nargs="*", help="slugi do przerysowania; pusto = wszystkie")
    parser.add_argument("--lista", action="store_true", help="wypisz sekcje i wyjdz")
    args = parser.parse_args()

    if args.lista:
        for sekcja in SEKCJE:
            print("%-16s assets/og/%s.png" % (sekcja["slug"], sekcja["slug"]))
        return 0

    wybrane = SEKCJE
    if args.sekcje:
        znane = {s["slug"] for s in SEKCJE}
        nieznane = [s for s in args.sekcje if s not in znane]
        if nieznane:
            print("Nieznane sekcje: %s" % ", ".join(nieznane), file=sys.stderr)
            return 1
        wybrane = [s for s in SEKCJE if s["slug"] in args.sekcje]

    pismo_tytul = znajdz_pismo(PISMA["szeryf"])
    pismo_tekst = znajdz_pismo(PISMA["bezszeryfowy"])
    os.makedirs(CEL, exist_ok=True)

    razem = 0
    for sekcja in wybrane:
        sciezka = os.path.join(CEL, sekcja["slug"] + ".png")
        waga = zapisz(karta(sekcja, pismo_tytul, pismo_tekst), sciezka)
        razem += waga
        print("assets/og/%-20s %6.1f kB" % (sekcja["slug"] + ".png", waga / 1024))
    print("razem %d kart, %.1f kB" % (len(wybrane), razem / 1024))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
