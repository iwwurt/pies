#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Buduje /rozdzialy/ i /podcast/ z dane/rozdzialy.json.

Uzycie:
    python tools/zrob_rozdzialy.py

Do tej pory pelny spis rozdzialow siedzial na stronie glownej w widgecie
z zakladkami: klikniecie jednej czesci chowalo cztery pozostale. Teraz sa
to dwie osobne podstrony, a wszystkie 61 rozdzialow widac naraz.

Skrypt czyta te same dane, co reszta serwisu, wiec kiedy dojda kolejne
identyfikatory YouTube, wystarczy je wpisac w dane/rozdzialy.json
i uruchomic ten plik ponownie.

Naglowek i stopke wypelniaja pozniej zrob_naglowek.py i zrob_stopke.py.

UWAGA: ten generator nadpisuje cale <body>, wiec kasuje wpiety
licznik odwiedzin. Po kazdym uruchomieniu wywolaj ponownie:
    python tools/zrob_analityke.py --cloudflare TOKEN
"""

import io
import json
import os

KATALOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IKONA_YT = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
            '<path d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4a2.5 2.5 0 '
            '0 0-1.8 1.8A26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.8 1.8C5.8 19 12 '
            '19 12 19s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8A26 26 0 0 0 22 12a26 26 0 0 '
            '0-.4-4.8ZM10 15V9l5.2 3Z"/></svg>')

PUSTY_NAGLOWEK = '    <header class="site-header" data-header>\n    </header>'

PUSTA_STOPKA = '''    <footer class="site-footer">
      <div class="shell site-footer__top">
        <a class="wordmark wordmark--footer" href="../">
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
    </footer>'''


def glowa(slug, tytul, opis, og_tytul, og_opis, dodatkowy_ld=""):
    return '''<!doctype html>
<html lang="pl" class="no-js">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>%(tytul)s</title>
    <meta name="description" content="%(opis)s" />
    <meta name="author" content="Mykola Hrytskov" />
    <meta name="robots" content="index, follow, max-image-preview:large" />
    <meta name="theme-color" content="#fcfbff" />
    <link rel="canonical" href="https://pieswpolsce.pl/%(slug)s/" />

    <meta property="og:locale" content="pl_PL" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="Pies w Polsce" />
    <meta property="og:title" content="%(og_tytul)s" />
    <meta property="og:description" content="%(og_opis)s" />
    <meta property="og:url" content="https://pieswpolsce.pl/%(slug)s/" />
    <meta property="og:image" content="https://pieswpolsce.pl/assets/og.jpg" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="%(og_tytul)s" />
    <meta name="twitter:description" content="%(og_opis)s" />
    <meta name="twitter:image" content="https://pieswpolsce.pl/assets/og.jpg" />

    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link rel="icon" href="../assets/favicon.svg" type="image/svg+xml" />
    <link rel="manifest" href="/manifest.json" />
    <link rel="apple-touch-icon" href="/assets/ikony/icon-192.png" />
    <link rel="stylesheet" href="../styles.css" />

    <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "@id": "https://pieswpolsce.pl/%(slug)s/#okruchy",
        "itemListElement": [
          { "@type": "ListItem", "position": 1, "name": "Pies w Polsce", "item": "https://pieswpolsce.pl/" },
          { "@type": "ListItem", "position": 2, "name": "%(og_tytul)s", "item": "https://pieswpolsce.pl/%(slug)s/" }
        ]
      }
    </script>
%(ld)s  </head>
''' % {"slug": slug, "tytul": tytul, "opis": opis, "og_tytul": og_tytul,
       "og_opis": og_opis, "ld": dodatkowy_ld}


def strona_rozdzialow(dane):
    czesci = dane["czesci"]
    wszystkie = [r for c in czesci for r in c["rozdzialy"]]
    z_odcinkiem = [r for r in wszystkie if r.get("yt")]

    pozycje_ld = []
    for i, r in enumerate(wszystkie, 1):
        pozycje_ld.append(
            '          { "@type": "ListItem", "position": %d, "name": %s }'
            % (i, json.dumps(r["tytul"], ensure_ascii=False)))
    ld = '''
    <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "@id": "https://pieswpolsce.pl/rozdzialy/#spis",
        "name": "Spis 61 rozdziałów książki Pies w Polsce",
        "numberOfItems": %d,
        "itemListElement": [
%s
        ]
      }
    </script>
''' % (len(wszystkie), ",\n".join(pozycje_ld))

    w = [glowa(
        "rozdzialy",
        "Spis treści: 61 rozdziałów | Pies w Polsce",
        "Pełny spis treści książki Pies w Polsce: pięć części, 61 rozdziałów, numery stron "
        "i odnośniki do odcinków podcastu. Wszystko na jednej stronie, bez zakładek.",
        "Spis 61 rozdziałów",
        "Pięć części, 61 rozdziałów, numery stron i podcast do każdego z nich.",
        ld)]
    w.append("""
  <body>
    <a class="skip-link" href="#main">Przejdź do treści</a>
    <div class="nx-progress" aria-hidden="true"><span data-progress></span></div>

%s

    <main id="main">
      <section class="nx-hero">
        <div class="nx-aurora" aria-hidden="true"><i></i><i></i><i></i></div>
        <div class="shell">
          <p class="okruchy"><a href="../">Pies w Polsce</a> <span aria-hidden="true">/</span> Rozdziały</p>
          <p class="kicker">Spis treści</p>
          <h1 style="max-width: 16ch; margin: 14px 0 0; font-family: var(--display); font-size: clamp(2.4rem, 5.6vw, 4.2rem); font-weight: 700; letter-spacing: -0.035em; line-height: 1">
            Wszystkie <span class="nx-grad-text">61 rozdziałów</span>
          </h1>
          <p class="nx-hero__lead">
            Pięć części, od kontekstu rynkowego po codzienność. Każdy rozdział ma numer strony
            w pliku PDF, a docelowo także własny odcinek podcastu. Nic się tu nie chowa
            pod zakładkami — cała lista jest widoczna naraz.
          </p>
          <div class="nx-stats" style="max-width: 640px">
            <div class="nx-stat"><b data-count="61">61</b><span>rozdziałów</span></div>
            <div class="nx-stat"><b data-count="5">5</b><span>części</span></div>
            <div class="nx-stat"><b data-count="618">618</b><span>stron</span></div>
            <div class="nx-stat"><b data-count="%d">%d</b><span>odcinków gotowych</span></div>
          </div>
          <div class="nx-hero__actions">
            <a class="button button--primary button--large" href="../pliki/Pies-w-Polsce-2026-cala-ksiazka.pdf" download>
              <span>Pobierz całość (PDF)</span>
              <span class="button__arrow" aria-hidden="true">↓</span>
            </a>
            <a class="button button--large" href="../podcast/">Strona podcastu</a>
          </div>
        </div>
      </section>

      <section class="nx-sekcja nx-sekcja--tuz">
        <div class="shell">""" % (PUSTY_NAGLOWEK, len(z_odcinkiem), len(z_odcinkiem)))

    for czesc in czesci:
        rozdzialy = czesc["rozdzialy"]
        numery = "%02d–%02d" % (rozdzialy[0]["nr"], rozdzialy[-1]["nr"])
        w.append('          <section class="nx-czesc reveal">')
        w.append('            <div class="nx-czesc__glowa">')
        w.append('              <span class="nx-czesc__nr">%s</span>' % czesc["rzymska"])
        w.append('              <h2>%s</h2>' % czesc["nazwa"])
        w.append('              <span>%s · rozdziały %s</span>' % (czesc["podtytul"], numery))
        w.append('            </div>')
        w.append('            <ul class="nx-rozdzialy">')
        for r in rozdzialy:
            w.append('              <li class="nx-rozdzial">')
            w.append('                <span class="nx-rozdzial__nr">%02d</span>' % r["nr"])
            w.append('                <span class="nx-rozdzial__tytul">%s</span>' % r["tytul"])
            if r.get("yt"):
                w.append('                <span class="nx-rozdzial__meta">s. %d</span>' % r["strona"])
                w.append('                <a class="nx-rozdzial__yt" '
                         'href="https://www.youtube.com/watch?v=%s" target="_blank" '
                         'rel="noopener" aria-label="Posłuchaj odcinka do rozdziału %d">%s</a>'
                         % (r["yt"], r["nr"], IKONA_YT))
            else:
                w.append('                <span class="nx-rozdzial__meta">s. %d</span>' % r["strona"])
                w.append('                <span class="nx-rozdzial__wkrotce">wkrótce</span>')
            w.append('              </li>')
        w.append('            </ul>')
        w.append('          </section>')

    w.append("""        </div>
      </section>

      <section class="nx-cta">
        <div class="shell">
          <h2>Cała treść w jednym pliku</h2>
          <p>618 stron, 19 MB, bez zapisu i bez opłat. Jeśli wolisz najpierw sprawdzić — jest fragment z pięcioma pierwszymi rozdziałami.</p>
          <div class="nx-cta__akcje">
            <a class="button button--primary button--large" href="../pliki/Pies-w-Polsce-2026-cala-ksiazka.pdf" download>
              <span>Pobierz książkę (PDF)</span>
              <span class="button__arrow" aria-hidden="true">↓</span>
            </a>
            <a class="button button--large" href="../pliki/Pies-w-Polsce-fragment-rozdzialy-1-5.pdf" download>Fragment, 52 strony</a>
          </div>
        </div>
      </section>
    </main>

%s
  </body>
</html>
""" % PUSTA_STOPKA)
    return "\n".join(w)


def strona_podcastu(dane):
    czesci = dane["czesci"]
    wszystkie = [r for c in czesci for r in c["rozdzialy"]]
    gotowe = [r for r in wszystkie if r.get("yt")]

    w = [glowa(
        "podcast",
        "Podcast o psie w Polsce — 61 odcinków | Pies w Polsce",
        "Audio do książki Pies w Polsce: docelowo 61 odcinków, po jednym do każdego rozdziału. "
        "Bezpłatnie, bez subskrypcji i bez reklam, na YouTube i na Dysku Google.",
        "Podcast Pies w Polsce",
        "Jeden odcinek do każdego z 61 rozdziałów. Za darmo, bez subskrypcji.")]

    kafelki = []
    for r in gotowe:
        kafelki.append('''            <article class="nx-karta reveal">
              <a class="nx-karta__foto" href="https://www.youtube.com/watch?v=%s" target="_blank" rel="noopener" aria-label="Odcinek %d na YouTube">
                <img src="https://i.ytimg.com/vi/%s/hqdefault.jpg" alt="" width="480" height="360" loading="lazy" />
              </a>
              <div class="nx-karta__tresc">
                <h3>%02d. %s</h3>
                <p>Rozdział %d, strona %d w pliku PDF.</p>
                <a class="nx-kafel__link" href="https://www.youtube.com/watch?v=%s" target="_blank" rel="noopener">Posłuchaj</a>
              </div>
            </article>''' % (r["yt"], r["nr"], r["yt"], r["nr"], r["tytul"],
                             r["nr"], r["strona"], r["yt"]))

    w.append("""
  <body>
    <a class="skip-link" href="#main">Przejdź do treści</a>
    <div class="nx-progress" aria-hidden="true"><span data-progress></span></div>

%s

    <main id="main">
      <section class="nx-hero">
        <div class="nx-aurora" aria-hidden="true"><i></i><i></i><i></i></div>
        <div class="shell nx-hero__inner">
          <div class="nx-hero__copy">
            <p class="okruchy"><a href="../">Pies w Polsce</a> <span aria-hidden="true">/</span> Podcast</p>
            <p class="kicker">Audio do książki</p>
            <h1>Ta sama treść, <span class="nx-grad-text">do słuchania</span></h1>
            <p class="nx-hero__lead">
              Do każdego z 61 rozdziałów powstaje osobny odcinek. W samochodzie, na spacerze,
              przy sprzątaniu — <strong>bez subskrypcji, bez reklam i bez opłat</strong>.
              Komplet nagrań jest też do pobrania z Dysku Google.
            </p>
            <div class="nx-hero__actions">
              <a class="button button--primary button--large" href="https://www.youtube.com/@PieswPolsce" target="_blank" rel="noopener">Kanał na YouTube</a>
              <a class="button button--large" href="https://drive.google.com/drive/folders/1g86EYIpOq0Y_I152-HYB8P9jFjz8trbG" target="_blank" rel="noopener">Nagrania na Dysku</a>
            </div>
            <div class="nx-stats" style="max-width: 520px">
              <div class="nx-stat"><b data-count="%d">%d</b><span>odcinki gotowe</span></div>
              <div class="nx-stat"><b data-count="61">61</b><span>zaplanowanych</span></div>
              <div class="nx-stat"><b>0 zł</b><span>za komplet</span></div>
            </div>
          </div>
          <figure class="nx-cover" data-tilt>
            <div class="nx-cover__inner">
              <img src="../assets/okladka-pies-w-polsce.jpg" width="1024" height="1536" alt="Okładka książki Pies w Polsce" />
              <figcaption class="nx-cover__tag">Audio + PDF <b>za 0 zł</b></figcaption>
            </div>
          </figure>
        </div>
      </section>

      <section class="nx-sekcja">
        <div class="shell">
          <div class="nx-naglowek reveal">
            <p class="kicker">Opublikowane</p>
            <h2>Odcinki, których można posłuchać już teraz</h2>
            <p>Reszta dochodzi po kolei. Postęp widać w <a href="../rozdzialy/" style="color: var(--gold-dark); border-bottom: 1px solid var(--gold-pale)">spisie rozdziałów</a> — odcinek gotowy ma przy sobie ikonę odtwarzania.</p>
          </div>
          <div class="nx-karty">
%s
          </div>
        </div>
      </section>

      <section class="nx-ciemna">
        <div class="shell">
          <p class="kicker">Jak to jest zrobione</p>
          <h2>Jeden rozdział, jeden odcinek</h2>
          <p>
            Podcast nie jest streszczeniem ani osobnym cyklem — to ten sam materiał, który
            znajdziesz w książce, przeczytany od początku do końca. Numeracja odcinków
            odpowiada numeracji rozdziałów, więc można czytać i słuchać naprzemiennie
            bez gubienia miejsca.
          </p>
          <div class="nx-alarm">
            <a href="../rozdzialy/">
              <b>Spis 61 rozdziałów</b>
              <span>Cała lista z numerami stron i odnośnikami do odcinków.</span>
            </a>
            <a href="../pliki/Pies-w-Polsce-2026-cala-ksiazka.pdf" download>
              <b>Wersja tekstowa</b>
              <span>Pełny PDF, 618 stron, do czytania równolegle.</span>
            </a>
            <a href="../o-ksiazce/">
              <b>O książce</b>
              <span>Jak jest zbudowana, skąd źródła i jak ją cytować.</span>
            </a>
          </div>
        </div>
      </section>
    </main>

%s
  </body>
</html>
""" % (PUSTY_NAGLOWEK, len(gotowe), len(gotowe), "\n".join(kafelki), PUSTA_STOPKA))
    return "\n".join(w)


def main():
    dane = json.load(io.open(os.path.join(KATALOG, "dane", "rozdzialy.json"),
                             encoding="utf-8"))
    for slug, tresc in (("rozdzialy", strona_rozdzialow(dane)),
                        ("podcast", strona_podcastu(dane))):
        katalog = os.path.join(KATALOG, slug)
        if not os.path.isdir(katalog):
            os.makedirs(katalog)
        sciezka = os.path.join(katalog, "index.html")
        io.open(sciezka, "w", encoding="utf-8", newline="").write(tresc)
        print("%-12s %6d znakow" % (slug + "/", len(tresc)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
