#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pobiera lecznice weterynaryjne i schroniska z OpenStreetMap do dane/punkty.json.

Uzycie:
    python tools/pobierz_punkty.py            # pobierz i zapisz
    python tools/pobierz_punkty.py --sucho    # pobierz i pokaz statystyki, nie zapisuj

Dane pochodza z OpenStreetMap (licencja ODbL) i wymagaja podania zrodla —
strona /mapa/ robi to w stopce sekcji. Baza jest tworzona przez wolontariuszy,
wiec bywa niekompletna; skrypt odrzuca obiekty bez nazwy, bo karta bez nazwy
jest dla czytelnika bezuzyteczna.

Skrypt NIE nadpisze pliku, jesli nowy wynik jest wyraznie mniejszy od obecnego
(patrz PROG_SPADKU). Chwilowa awaria Overpassa nie skasuje dobrych danych.
"""

import argparse
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

KATALOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEL = os.path.join(KATALOG, "dane", "punkty.json")

# Polska z waskim marginesem; dokladny ksztalt odsiewa nizej WIELOKAT
BBOX = "48.9,14.0,55.0,24.3"

SERWERY = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]

RODZAJE = [("v", "veterinary"), ("s", "animal_shelter")]

# Nowy wynik musi miec co najmniej tyle procent obecnej liczby punktow,
# zeby nadpisac plik. Chroni przed czesciowa odpowiedzia serwera.
PROG_SPADKU = 0.8

# Zgrubny obrys Polski (lat, lon) - odsiewa sasiadow zlapanych przez bbox
WIELOKAT = [
    (54.84, 18.32), (54.36, 19.64), (54.32, 22.80), (53.90, 23.55),
    (52.28, 23.62), (50.87, 23.93), (50.35, 24.15), (49.60, 22.70),
    (49.09, 22.55), (49.40, 21.00), (49.18, 19.80), (49.40, 18.85),
    (49.99, 18.03), (50.28, 17.72), (50.66, 17.00), (50.10, 16.30),
    (50.86, 14.82), (51.38, 14.72), (52.28, 14.55), (53.25, 14.22),
    (54.02, 14.22), (54.55, 16.50), (54.84, 18.32),
]


def w_polsce(lat, lon):
    """Test punkt-w-wielokacie metoda promienia."""
    wewnatrz = False
    j = len(WIELOKAT) - 1
    for i in range(len(WIELOKAT)):
        yi, xi = WIELOKAT[i]
        yj, xj = WIELOKAT[j]
        if (xi > lon) != (xj > lon):
            if lat < (yj - yi) * (lon - xi) / (xj - xi) + yi:
                wewnatrz = not wewnatrz
        j = i
    return wewnatrz


def pobierz(amenity):
    zapytanie = (
        '[out:json][timeout:280];('
        'node["amenity"="%s"](%s);'
        'way["amenity"="%s"](%s);'
        ');out center tags;' % (amenity, BBOX, amenity, BBOX)
    )
    dane = urllib.parse.urlencode({"data": zapytanie}).encode()

    for url in SERWERY:
        for proba in (1, 2):
            try:
                zadanie = urllib.request.Request(
                    url, data=dane,
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "pieswpolsce.pl map data updater",
                    })
                with urllib.request.urlopen(zadanie, timeout=300) as odp:
                    wynik = json.loads(odp.read())
                elementy = wynik.get("elements", [])
                if not elementy:
                    # Overpass potrafi oddac HTTP 200 z pusta lista, gdy jest
                    # przeciazony. To awaria, a nie wynik - probujemy dalej.
                    print("  %-15s %-24s proba %d: pusta odpowiedz"
                          % (amenity, url.split("/")[2], proba))
                    time.sleep(5)
                    continue
                print("  %-15s %-24s %d obiektow" % (amenity, url.split("/")[2], len(elementy)))
                return elementy
            except Exception as blad:
                print("  %-15s %-24s proba %d: %s"
                      % (amenity, url.split("/")[2], proba, type(blad).__name__))
                time.sleep(5)
    return []


def czysc_telefon(tekst):
    if not tekst:
        return None
    pierwszy = re.split(r"[;,]", tekst)[0].strip()
    cyfry = re.sub(r"[^\d+]", "", pierwszy)
    return cyfry[:16] or None


def na_punkt(element, rodzaj):
    tagi = element.get("tags", {})
    lat = element.get("lat") or (element.get("center") or {}).get("lat")
    lon = element.get("lon") or (element.get("center") or {}).get("lon")
    if lat is None or lon is None:
        return None
    if not w_polsce(lat, lon):
        return None

    nazwa = tagi.get("name")
    if not nazwa:
        return None

    ulica = tagi.get("addr:street")
    numer = tagi.get("addr:housenumber")
    adres = (ulica + " " + numer).strip() if ulica and numer else (ulica or None)

    punkt = {"t": rodzaj, "n": nazwa[:80], "y": round(lat, 5), "x": round(lon, 5)}
    pola = (
        ("m", tagi.get("addr:city")),
        ("a", adres),
        ("p", czysc_telefon(tagi.get("phone") or tagi.get("contact:phone"))),
        ("h", tagi.get("opening_hours")),
        ("w", tagi.get("website") or tagi.get("contact:website")),
    )
    for klucz, wartosc in pola:
        if wartosc:
            punkt[klucz] = wartosc[:80] if klucz == "h" else wartosc[:120]
    return punkt


def obecna_liczba():
    if not os.path.exists(CEL):
        return 0
    try:
        with io.open(CEL, encoding="utf-8") as plik:
            return len(json.load(plik))
    except Exception:
        return 0


def main():
    parser = argparse.ArgumentParser(description="Aktualizuje dane/punkty.json z OpenStreetMap.")
    parser.add_argument("--sucho", action="store_true",
                        help="pobierz i pokaz statystyki, ale nie zapisuj pliku")
    parser.add_argument("--mimo-spadku", action="store_true",
                        help="zapisz nawet jesli punktow jest wyraznie mniej niz teraz")
    args = parser.parse_args()

    print("Pobieram z OpenStreetMap (bbox %s)..." % BBOX)
    punkty = []
    for rodzaj, amenity in RODZAJE:
        elementy = pobierz(amenity)
        if not elementy:
            sys.stderr.write(
                '\nBLAD: nie udalo sie pobrac kategorii "%s" z zadnego serwera.\n'
                "Zapis samej drugiej kategorii skasowalby te dane, wiec przerywam.\n"
                "Sprobuj ponownie za kilka minut.\n" % amenity)
            return 1
        for element in elementy:
            punkt = na_punkt(element, rodzaj)
            if punkt:
                punkty.append(punkt)

    if not punkty:
        sys.stderr.write("BLAD: nie pobrano zadnego punktu. Plik zostaje bez zmian.\n")
        return 1

    punkty.sort(key=lambda p: (p["t"], p.get("m") or "", p["n"]))

    lecznic = sum(1 for p in punkty if p["t"] == "v")
    schronisk = len(punkty) - lecznic
    print("")
    print("Po odsianiu (bez nazwy i poza Polska):")
    print("  lecznice:   %d" % lecznic)
    print("  schroniska: %d" % schronisk)
    print("  razem:      %d" % len(punkty))
    print("  z telefonem: %d, z godzinami: %d, z miastem: %d"
          % (sum("p" in p for p in punkty),
             sum("h" in p for p in punkty),
             sum("m" in p for p in punkty)))

    bylo = obecna_liczba()
    if bylo:
        roznica = len(punkty) - bylo
        print("  poprzednio: %d (%+d)" % (bylo, roznica))

    if args.sucho:
        print("\n--sucho: plik nie zostal zapisany.")
        return 0

    if bylo and len(punkty) < bylo * PROG_SPADKU and not args.mimo_spadku:
        sys.stderr.write(
            "\nBLAD: nowy wynik ma %d punktow wobec %d obecnych (prog: %d%%).\n"
            "Wyglada to na czesciowa odpowiedz serwera, wiec plik zostaje bez zmian.\n"
            "Jesli spadek jest prawdziwy, uruchom ponownie z --mimo-spadku.\n"
            % (len(punkty), bylo, int(PROG_SPADKU * 100)))
        return 1

    with io.open(CEL, "w", encoding="utf-8", newline="\n") as plik:
        plik.write(json.dumps(punkty, ensure_ascii=False, separators=(",", ":")))

    print("\nZapisano %s (%.0f KB)" % (os.path.relpath(CEL, KATALOG), os.path.getsize(CEL) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
