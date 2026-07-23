# Pies w Polsce — strona książki

Responsywna strona statyczna książki **„Pies w Polsce. Prawo · Obowiązki · Miłość”** autorstwa Mykoli Hrytskova.

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
- `pliki/Pies-w-Polsce-fragment-rozdzialy-1-5.pdf` — darmowy fragment, 52 strony.
- `pliki/Checklista-pies-w-Polsce-2026.pdf` — darmowa checklista, 2 strony.
- `pliki/podglad/str-01.webp` … `str-52.webp` — strony czytnika online.
- `assets/photos/` — zoptymalizowane zdjęcia strony.

Nie zmieniać nazw PDF ani plików `str-NN.webp`: czytnik korzysta z tego wzorca.

## Sprzedaż

Wszystkie przyciski „Kup e-booka” są zwykłymi linkami prowadzącymi do:

`https://angelread.etsy.com`

Płatność i dostawa pliku odbywają się na Etsy. Strona nie obsługuje płatności i nie zbiera danych kupujących.

## GitHub Pages

Projekt jest gotowy do publikacji z katalogu głównego gałęzi `main`. Pliki `CNAME`, `.nojekyll`, `robots.txt` i `sitemap.xml` są już przygotowane dla domeny `pieswpolsce.pl`.

Po zmianie domeny trzeba zaktualizować canonical, Open Graph, JSON-LD, `robots.txt`, `sitemap.xml` oraz `CNAME`.

