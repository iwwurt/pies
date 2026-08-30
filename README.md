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
- `pliki/Pies-w-Polsce-2026-cala-ksiazka.pdf` — pełna książka, 618 stron.
- `pliki/Pies-w-Polsce-fragment-rozdzialy-1-5.pdf` — fragment, 52 strony.
- `pliki/Checklista-pies-w-Polsce-2026.pdf` — checklista, 2 strony.
- `pliki/podglad/str-01.webp` … `str-52.webp` — strony czytnika online.
- `assets/photos/` — zoptymalizowane zdjęcia strony.

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

## Wsparcie autora

Przyciski „Wesprzyj autora” mają w `index.html` atrybut `data-donate` i tymczasowy adres
`{{DONATE_URL}}`. Dopóki nie zostanie podmieniony na prawdziwy link (np. buycoffee.to,
PayPal.me, Revolut), `script.js` usuwa te elementy ze strony — nic się nie psuje i nikt
nie trafia w martwy odnośnik. Aby je włączyć, wystarczy zamienić `{{DONATE_URL}}` na adres zbiórki.

## GitHub Pages

Projekt jest gotowy do publikacji z katalogu głównego gałęzi `main`. Pliki `CNAME`, `.nojekyll`, `robots.txt` i `sitemap.xml` są już przygotowane dla domeny `pieswpolsce.pl`.

Po zmianie domeny trzeba zaktualizować canonical, Open Graph, JSON-LD, `robots.txt`, `sitemap.xml` oraz `CNAME`.
