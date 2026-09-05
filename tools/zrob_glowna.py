#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sklada strone glowna z szablonu tools/glowna_body.html.

Uzycie:
    python tools/zrob_glowna.py

Podmienia znaczniki __NAZWA__ w szablonie na ikony SVG, pasek tematow
i galerie podgladu, po czym doklada ten korpus do zachowanej sekcji <head>
istniejacego index.html. Naglowek i stopke wypelniaja pozniej
zrob_naglowek.py i zrob_stopke.py - tutaj zostaja tylko puste ramy.

Ikony sa rysowane w kodzie, a nie pobierane z zewnetrznej biblioteki:
strona nie ma laczyc sie z niczym, czego nie kontrolujemy.
"""

import io
import os
import re

KATALOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ikona(sciezki, wypelnienie=False):
    atrybuty = ('viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
                'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"')
    if wypelnienie:
        atrybuty = 'viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"'
    return '<svg %s>%s</svg>' % (atrybuty, sciezki)


IKONY = {
    # waga sprawiedliwosci
    "I_LAW": ikona('<path d="M12 3v18M7 21h10M5 7h14M5 7 2 14h6L5 7Zm14 0-3 7h6l-3-7Z"/>'
                   '<path d="M12 3 5 7m7-4 7 4"/>'),
    # serce z linia tetna
    "I_HEART": ikona('<path d="M20.8 6.6a5 5 0 0 0-8.8-1.9A5 5 0 0 0 3.2 6.6c-1 3 1.2 5.7 3.6 '
                     '7.9L12 19.5l5.2-5c2.4-2.2 4.6-4.9 3.6-7.9Z"/>'
                     '<path d="M3.8 11.5h3.4l1.6-2.6 2 4.6 1.7-3 1.2 1h4.5"/>'),
    # mozg / zachowanie
    "I_BRAIN": ikona('<path d="M12 5.5a2.6 2.6 0 0 0-5 .9 2.6 2.6 0 0 0-1.6 4.3A2.7 2.7 0 0 0 '
                     '6 16a2.6 2.6 0 0 0 3.6 2.2A2.4 2.4 0 0 0 12 19.5Z"/>'
                     '<path d="M12 5.5a2.6 2.6 0 0 1 5 .9 2.6 2.6 0 0 1 1.6 4.3A2.7 2.7 0 0 1 '
                     '18 16a2.6 2.6 0 0 1-3.6 2.2A2.4 2.4 0 0 1 12 19.5Z"/>'
                     '<path d="M12 5.5v14"/>'),
    # moneta
    "I_COIN": ikona('<circle cx="12" cy="12" r="8.6"/>'
                    '<path d="M14.6 9.2A2.8 2.8 0 0 0 12 7.6c-1.6 0-2.6.9-2.6 2s1 1.8 2.6 '
                    '2.1c1.7.3 2.7 1 2.7 2.1s-1.1 2-2.7 2a2.9 2.9 0 0 1-2.7-1.7"/>'
                    '<path d="M12 6.2v1.4m0 8.8v1.4"/>'),
    # pinezka na mapie
    "I_PIN": ikona('<path d="M12 21s7-5.3 7-11a7 7 0 1 0-14 0c0 5.7 7 11 7 11Z"/>'
                   '<circle cx="12" cy="10" r="2.8"/>'),
    # trojkat ostrzegawczy
    "I_ALERT": ikona('<path d="M10.3 3.9 2.4 17.5A2 2 0 0 0 4.1 20.5h15.8a2 2 0 0 0 '
                     '1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/>'
                     '<path d="M12 9.5v4.2m0 3.1v.1"/>'),
    # lupa
    "I_SEARCH": ikona('<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>'),
    # kleszcz
    "I_TICK": ikona('<ellipse cx="12" cy="13" rx="4.2" ry="5.4"/>'
                    '<path d="M12 7.6V5.4"/><path d="M7.8 9.6 4.6 7.2m3.2 6H4.4m3.6 3.8-3 2.2'
                    'm11.2-9.6 3.2-2.4m-3.2 6.2h3.4m-3.6 3.8 3 2.2"/>'),
    # tarcza
    "I_SHIELD": ikona('<path d="M12 3 5 5.8v5.5c0 4.3 2.9 8.1 7 9.4 4.1-1.3 7-5.1 '
                      '7-9.4V5.8L12 3Z"/><path d="m9.2 12 2 2 3.6-3.9"/>'),
    # ksiazka
    "I_BOOK": ikona('<path d="M4 4.8A1.8 1.8 0 0 1 5.8 3H19v15.5H5.8A1.8 1.8 0 0 0 4 20.3Z"/>'
                    '<path d="M4 20.3A1.8 1.8 0 0 1 5.8 18.5H19V21H5.8A1.8 1.8 0 0 1 4 19.2Z"/>'),
    # sluchawki
    "I_AUDIO": ikona('<path d="M4 14v-2a8 8 0 0 1 16 0v2"/>'
                     '<path d="M4 14.5A1.5 1.5 0 0 1 5.5 13h1V19h-1A1.5 1.5 0 0 1 4 17.5Z"/>'
                     '<path d="M20 14.5A1.5 1.5 0 0 0 18.5 13h-1V19h1a1.5 1.5 0 0 0 1.5-1.5Z"/>'),
    # dom
    "I_HOME": ikona('<path d="M3.5 10.5 12 3.6l8.5 6.9V20a1 1 0 0 1-1 1h-15a1 1 0 0 1-1-1Z"/>'
                    '<path d="M9.5 21v-6h5v6"/>'),
    # pociag
    "I_TRAIN": ikona('<rect x="5" y="3.5" width="14" height="12.5" rx="3"/>'
                     '<path d="M5 10h14"/><path d="M9 19.5 7 22m8-2.5 2 2.5"/>'
                     '<path d="M9.2 13.2h.1m5.5 0h.1"/>'),
    # mikroczip
    "I_CHIP": ikona('<rect x="7" y="7" width="10" height="10" rx="2.2"/>'
                    '<path d="M10 3.5v3m4-3v3m-4 11v3m4-3v3M3.5 10h3m-3 4h3m11-4h3m-3 4h3"/>'),
    # kosc / pies
    "I_DOG": ikona('<path d="M5.5 12a2.3 2.3 0 1 1 1.9-3.6 2.3 2.3 0 1 1 2.3 3.1h4.6a2.3 2.3 '
                   '0 1 1 2.3-3.1A2.3 2.3 0 1 1 18.5 12a2.3 2.3 0 1 1-1.9 3.6 2.3 2.3 0 1 '
                   '1-2.3-3.1H9.7a2.3 2.3 0 1 1-2.3 3.1A2.3 2.3 0 1 1 5.5 12Z"/>'),
    # dziecko
    "I_CHILD": ikona('<circle cx="12" cy="6.5" r="3"/>'
                     '<path d="M12 9.5v6m-4 5.5 4-5.5 4 5.5M7.5 12.5h9"/>'),
    # dokument
    "I_DOC": ikona('<path d="M14 3H7a1.8 1.8 0 0 0-1.8 1.8v14.4A1.8 1.8 0 0 0 7 21h10a1.8 1.8 '
                   '0 0 0 1.8-1.8V7.8L14 3Z"/><path d="M14 3v5h4.8M8.5 13h7m-7 3.5h4.5"/>'),
    # youtube
    "I_YT": ikona('<path d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4a2.5 '
                  '2.5 0 0 0-1.8 1.8A26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.8 '
                  '1.8C5.8 19 12 19 12 19s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8A26 26 0 0 0 22 '
                  '12a26 26 0 0 0-.4-4.8ZM10 15V9l5.2 3Z"/>', wypelnienie=True),
}

# pasek przewijanych tematow: (ikona, etykieta, adres)
PASEK = [
    ("I_CHIP", "KROPiK 2026", "kropik/"),
    ("I_ALERT", "Zatrucia", "zatrucia/"),
    ("I_SHIELD", "Pogryzienie", "ugryzienie/"),
    ("I_HOME", "Pies w bloku", "mieszkanie/"),
    ("I_TRAIN", "Transport", "transport/"),
    ("I_TICK", "Kleszcze", "kleszcze/"),
    ("I_SEARCH", "Zaginiony pies", "zaginiony/"),
    ("I_HEART", "Apteczka", "apteczka/"),
    ("I_DOG", "Adopcja", "adopcja/"),
    ("I_CHILD", "Pies i dziecko", "dziecko/"),
    ("I_BRAIN", "Szkolenie", "szkolenie/"),
    ("I_COIN", "Koszty", "koszty/"),
    ("I_PIN", "Mapa lecznic", "mapa/"),
    ("I_DOC", "Pies w spadku", "spadek/"),
    ("I_LAW", "Pies asystujący", "psy-asystujace/"),
]

# strony podgladu pokazywane w galerii - co druga, zeby nie zalac strony
GALERIA = list(range(1, 25, 2))


def pasek_html():
    kafelki = []
    for klucz, etykieta, adres in PASEK:
        kafelki.append('            <a href="%s">%s<span>%s</span></a>'
                       % (adres, IKONY[klucz], etykieta))
    # dwie kopie z rzedu - petla animacji przesuwa sie o polowe szerokosci
    return "\n".join(kafelki + kafelki)


def galeria_html():
    wiersze = []
    for numer in GALERIA:
        wiersze.append(
            '            <img src="pliki/podglad/str-%02d.webp" alt="Strona %d książki '
            'Pies w Polsce" width="827" height="1169" loading="lazy" />' % (numer, numer))
    return "\n".join(wiersze)


PUSTY_NAGLOWEK = '''    <header class="site-header" data-header>
    </header>
'''

PUSTA_STOPKA = '''    <footer class="site-footer">
      <div class="shell site-footer__top">
        <a class="wordmark wordmark--footer" href="./">
          <span class="wordmark__seal" aria-hidden="true">P</span>
          <span class="wordmark__text"><strong>Pies w Polsce</strong><small>Mykola Hrytskov · 2026</small></span>
        </a>
        <nav class="site-footer__kolumny" aria-label="Mapa serwisu">
        </nav>
      </div>
      <div class="shell site-footer__legal">
        <p>
          Treści na stronie i w książce mają charakter informacyjny oraz edukacyjny. Nie stanowią
          indywidualnej porady prawnej ani weterynaryjnej. Przepisy mogą się zmieniać; przed
          podjęciem decyzji sprawdź aktualne źródła lub skonsultuj się ze specjalistą.
        </p>
        <p>© 2026 Mykola Hrytskov</p>
      </div>
    </footer>
'''


def main():
    korpus = io.open(os.path.join(KATALOG, "tools", "glowna_body.html"),
                     encoding="utf-8").read()
    korpus = korpus.replace("__HEADER__", PUSTY_NAGLOWEK.strip("\n"))
    korpus = korpus.replace("__FOOTER__", PUSTA_STOPKA.strip("\n"))
    korpus = korpus.replace("__MARQUEE__", pasek_html())
    korpus = korpus.replace("__GALERIA__", galeria_html())
    for klucz, svg in IKONY.items():
        korpus = korpus.replace("__%s__" % klucz, svg)

    zostalo = re.findall(r"__[A-Z_]+__", korpus)
    assert not zostalo, "niepodmienione znaczniki: %s" % sorted(set(zostalo))

    sciezka = os.path.join(KATALOG, "index.html")
    stary = io.open(sciezka, encoding="utf-8").read()
    glowa = stary[:stary.index("  </head>") + len("  </head>\n")]
    glowa = glowa.replace('<meta name="theme-color" content="#3a3733" />',
                          '<meta name="theme-color" content="#fcfbff" />')
    if "fonts.gstatic.com" not in glowa:
        glowa = glowa.replace(
            '    <link rel="icon"',
            '    <link rel="preconnect" href="https://fonts.googleapis.com" />\n'
            '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
            '    <link rel="icon"', 1)

    io.open(sciezka, "w", encoding="utf-8", newline="").write(glowa + korpus)
    print("index.html zapisany, %d znakow" % len(glowa + korpus))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
