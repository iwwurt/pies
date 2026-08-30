#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Renderuje spis 61 rozdzialow z dane/rozdzialy.json do index.html.

Uzycie:
    python tools/build_rozdzialy.py

Skrypt podmienia tylko fragment miedzy znacznikami
<!-- ROZDZIALY:START --> i <!-- ROZDZIALY:END --> oraz adresy playlisty
w elementach z atrybutem data-yt-playlist. Reszta pliku zostaje nietknieta.

Zeby dodac podcasty: wpisz "playlist" oraz identyfikatory filmow ("yt")
w dane/rozdzialy.json i uruchom skrypt ponownie.
"""

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DANE = os.path.join(ROOT, "dane", "rozdzialy.json")
INDEX = os.path.join(ROOT, "index.html")

START = "<!-- ROZDZIALY:START -->"
END = "<!-- ROZDZIALY:END -->"


def escape(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def link_filmu(yt):
    """Przyjmuje pelny adres albo samo ID filmu."""
    yt = (yt or "").strip()
    if not yt:
        return ""
    if yt.startswith("http"):
        return yt
    return "https://www.youtube.com/watch?v=" + yt


def render(dane):
    czesci = dane["czesci"]
    out = [START]
    for czesc in czesci:
        rozdzialy = czesc["rozdzialy"]
        pierwszy = "%02d" % rozdzialy[0]["nr"]
        ostatni = "%02d" % rozdzialy[-1]["nr"]
        zakres = pierwszy if pierwszy == ostatni else "%s–%s" % (pierwszy, ostatni)
        out.append('            <section class="rozdzialy__czesc reveal">')
        out.append('              <div class="rozdzialy__czesc-head">')
        out.append(
            '                <p class="rozdzialy__rzymska" aria-hidden="true">%s</p>'
            % escape(czesc["rzymska"])
        )
        out.append("                <div>")
        out.append("                  <h3>%s</h3>" % escape(czesc["nazwa"]))
        out.append("                  <p>%s</p>" % escape(czesc["podtytul"]))
        out.append("                </div>")
        out.append(
            '                <p class="rozdzialy__zakres">rozdziały %s</p>' % zakres
        )
        out.append("              </div>")
        out.append('              <ol class="rozdzialy__lista">')
        for rozdzial in rozdzialy:
            nr = "%02d" % rozdzial["nr"]
            tytul = escape(rozdzial["tytul"])
            link = link_filmu(rozdzial.get("yt"))
            if link:
                podcast = (
                    '<a class="rozdzial__podcast" href="%s" target="_blank" rel="noopener"'
                    ' aria-label="Posłuchaj podcastu do rozdziału %s">'
                    '<span class="rozdzial__play" aria-hidden="true"></span>Podcast</a>'
                    % (escape(link), nr)
                )
            else:
                podcast = (
                    '<span class="rozdzial__podcast rozdzial__podcast--soon">'
                    "Wkrótce</span>"
                )
            out.append('                <li class="rozdzial">')
            out.append(
                '                  <span class="rozdzial__nr" aria-hidden="true">%s</span>' % nr
            )
            out.append('                  <span class="rozdzial__tytul">%s</span>' % tytul)
            out.append(
                '                  <span class="rozdzial__strona">s. %s</span>'
                % rozdzial["strona"]
            )
            out.append("                  " + podcast)
            out.append("                </li>")
        out.append("              </ol>")
        out.append("            </section>")
    out.append("            " + END)
    return "\n".join(out)


def main():
    with io.open(DANE, encoding="utf-8") as handle:
        dane = json.load(handle)

    with io.open(INDEX, encoding="utf-8") as handle:
        html = handle.read()

    if START not in html or END not in html:
        sys.stderr.write("Brak znacznikow ROZDZIALY:START / ROZDZIALY:END w index.html\n")
        return 1

    poczatek = html.index(START)
    koniec = html.index(END) + len(END)
    html = html[:poczatek] + render(dane) + html[koniec:]

    playlist = (dane.get("playlist") or "").strip()
    if playlist:
        html = re.sub(
            r'href="[^"]*"(\s+[^>]*?)?\s+data-yt-playlist',
            'href="%s"\\1 data-yt-playlist' % playlist,
            html,
        )

    with io.open(INDEX, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(html)

    ile = sum(len(c["rozdzialy"]) for c in dane["czesci"])
    z_podcastem = sum(
        1 for c in dane["czesci"] for r in c["rozdzialy"] if (r.get("yt") or "").strip()
    )
    print("Rozdzialy: %d (z podcastem: %d)" % (ile, z_podcastem))
    print("Playlista: %s" % (playlist or "— brak, linki zostaja jako 'Wkrotce'"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
