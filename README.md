# Pies w Polsce — strona książki

Responsywna strona statyczna książki **„Pies w Polsce. Prawo · Obowiązki · Miłość”** autorstwa Mykoli Hrytskova.

Od sierpnia 2026 strona nie sprzedaje książki. Cała książka (618 stron, PDF) i podcast do każdego
z 61 rozdziałów są udostępniane bezpłatnie, bez rejestracji i bez zapisu na newsletter.

## Podgląd lokalny

Strona nie wymaga budowania ani instalowania zależności. Można otworzyć `index.html` bezpośrednio albo uruchomić prosty serwer w katalogu projektu:

```powershell
python -m http.server 8080
```

Następnie otworzyć `http://localhost:8080`.

## Najważniejsze pliki

- `index.html` — treść, metadane SEO i dane strukturalne.
- `styles.css` — pełny wygląd strony i wersja mobilna.
- `script.js` — menu, kalkulator kosztów, karuzela, zakładki i czytnik fragmentu.
- `dane/rozdzialy.json` — źródło spisu 61 rozdziałów i linków do podcastów.
- `tools/build_rozdzialy.py` — generator sekcji „Rozdziały” w `index.html`.
- `tools/pobierz_punkty.py` — aktualizator danych mapy z OpenStreetMap.
- `tools/zrob_og.py` — generator kart Open Graph dla podstron.
- `dane/punkty.json` — lecznice i schroniska pokazywane na `/mapa/`.
- `pliki/Pies-w-Polsce-2026-cala-ksiazka.pdf` — pełna książka, 618 stron.
- `pliki/Pies-w-Polsce-fragment-rozdzialy-1-5.pdf` — fragment, 52 strony.
- `pliki/Checklista-pies-w-Polsce-2026.pdf` — checklista, 2 strony.
- `pliki/podglad/str-01.webp` … `str-52.webp` — strony czytnika online.
- `assets/photos/` — zoptymalizowane zdjęcia strony.
- `assets/og/` — karty Open Graph podstron (po jednej na sekcję).

Nie zmieniać nazw PDF ani plików `str-NN.webp`: czytnik i przyciski pobierania korzystają z tych ścieżek.

## Podcast: jak dodać linki do YouTube

1. Otworzyć `dane/rozdzialy.json`.
2. W polu `"playlist"` wpisać adres playlisty na YouTube.
3. Przy każdym rozdziale w polu `"yt"` wpisać identyfikator filmu (np. `dQw4w9WgXcQ`) albo pełny adres.
4. Uruchomić generator:

```powershell
python tools/build_rozdzialy.py
```

Skrypt podmienia wyłącznie fragment `index.html` między znacznikami `<!-- ROZDZIALY:START -->`
i `<!-- ROZDZIALY:END -->` oraz adres playlisty w przycisku z atrybutem `data-yt-playlist`.
Rozdziały bez identyfikatora filmu zostają oznaczone jako „Wkrótce”.

## Strony serwisu

Poza stroną główną serwis ma osobne strony tematyczne, każdą z własnymi
danymi strukturalnymi i wpisem w `sitemap.xml`:

- `/kropik/` — rejestr KROPiK i obowiązkowe czipowanie
- `/koszty/` — pełne wyliczenie kosztów utrzymania psa
- `/narzedzia/` — kalkulatory i ściągi (wiek, szczepienia, wstęp z psem, KROPiK, opłata gminna)
- `/mapa/` — lecznice i schroniska z OpenStreetMap
- `/zatrucia/` — postępowanie przy zatruciu
- `/apteczka/` — lista kontrolna apteczki

Dodając kolejną stronę, pamiętaj o pięciu rzeczach: okruchy chleba
z `BreadcrumbList`, wpis w `sitemap.xml`, odnośnik w stopkach pozostałych
stron, `canonical` we własnym nagłówku i własna karta Open Graph
(patrz niżej).

## Mapa: jak odświeżyć dane

Punkty na stronie `/mapa/` pochodzą z OpenStreetMap i leżą w `dane/punkty.json`.
Baza OSM rośnie, więc raz na kilka miesięcy warto ją odświeżyć:

```powershell
python tools/pobierz_punkty.py
```

Skrypt sam pobiera dane z Overpass API, odsiewa obiekty spoza Polski
i te bez nazwy, po czym nadpisuje `dane/punkty.json`. Nie wymaga klucza
ani konta.

Przydatne przełączniki:

- `--sucho` — pobierz i pokaż statystyki, ale nie zapisuj pliku.
- `--mimo-spadku` — zapisz, nawet jeśli punktów jest wyraźnie mniej niż teraz.

**Dlaczego istnieje próg spadku.** Overpass bywa przeciążony i potrafi oddać
odpowiedź poprawną technicznie, ale pustą albo niekompletną. Gdyby skrypt
zapisywał ją bez sprawdzenia, jedno nieudane uruchomienie skasowałoby dobre
dane. Dlatego plik zostaje bez zmian, jeśli nowy wynik ma mniej niż 80%
obecnej liczby punktów — a pusta odpowiedź jednej kategorii przerywa całość.

Po aktualizacji wystarczy sprawdzić `/mapa/` w przeglądarce i zrobić commit.

Dane są udostępniane na licencji ODbL i wymagają podania źródła — informacja
o OpenStreetMap znajduje się w stopce sekcji na stronie mapy. Nie usuwać jej.

## Karty Open Graph

Obrazek, który pokazuje się przy wklejeniu linku na Facebooku, LinkedInie,
WhatsAppie czy Signalu. Strona główna ma własny — `assets/og.png` ze zdjęciem
psa. Każda podstrona ma swój w `assets/og/<sekcja>.png`.

```powershell
python tools/zrob_og.py                 # przerysuj wszystkie karty
python tools/zrob_og.py kleszcze mapa   # tylko wybrane sekcje
python tools/zrob_og.py --lista         # wypisz sekcje i ścieżki plików
```

Skrypt rysuje karty lokalnie (Pillow + kroje pisma z systemu), nie wysyła
nic do sieci i nie korzysta z żadnego generatora online. Karta to tło,
ramka, łapka i tekst, więc plik waży ok. 25 kB zamiast setek kilobajtów.

**Dodając nową podstronę**, dopisz sekcję do listy `SEKCJE` w
`tools/zrob_og.py` (slug, dział, tytuł, podtytuł, ton), uruchom skrypt
i wskaż nowy plik w `og:image` oraz `twitter:image` w nagłówku strony.
Pola `og:image:width`, `og:image:height` i `og:image:alt` też są wymagane —
bez nich część komunikatorów pokazuje link bez obrazka.

Tony są dwa. `zloty` to domyślny kolor serwisu. `alarm` — ciemna czerwień
z `/zatrucia/` — jest zarezerwowany dla stron, na które trafia się w panice
(zatrucie, zaginięcie, kleszcze). Nie rozszerzać go na resztę: cały sens
polega na tym, że taki link wygląda inaczej niż pozostałe.

## GitHub Pages

Projekt jest gotowy do publikacji z katalogu głównego gałęzi `main`. Pliki `CNAME`, `.nojekyll`, `robots.txt` i `sitemap.xml` są już przygotowane dla domeny `pieswpolsce.pl`.

Po zmianie domeny trzeba zaktualizować canonical, Open Graph, JSON-LD, `robots.txt`, `sitemap.xml` oraz `CNAME`.
