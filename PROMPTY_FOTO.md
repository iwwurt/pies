# Prompty fotograficzne — pieswpolsce (nowa paleta 2026)

Strona ma teraz **jasne, chłodne tło** i gradient różowo-błękitny
(`#f38ad8` → `#7ccbff`) jako akcent. Stare prompty były pisane pod kremowy
beż i do tego wyglądu już nie pasują — poniżej wersja zgodna z obecnym
serwisem.

Zasada jest ta sama co wcześniej: wszystkie zdjęcia mają wyglądać jak
**jedna sesja**, jeden pies, dużo pustej przestrzeni. Prompty po angielsku.

---

## Prefiks stylu — wklejać na początku KAŻDEGO promptu

```
Professional studio pet photography, clean bright off-white background
(#FCFBFF) with a very soft pink-to-blue gradient wash in the corners
(#F38AD8 to #7CCBFF, subtle, like colored studio gel light), crisp diffused
daylight, soft cool shadows, modern editorial composition with generous
negative space, high-end commercial photography, medium format camera,
85mm lens, shallow depth of field, no warm yellow cast
```

Midjourney: `--style raw --v 6.1`
Negatyw: `no cartoon, no illustration, no text, no watermark, no beige, no sepia`

**Kontrola koloru:** tło `#FCFBFF` · tekst `#14111F` · róż `#F38AD8` ·
błękit `#7CCBFF`. Jeśli zdjęcie wychodzi ciepłe/beżowe — dopisz do promptu
`cool white balance, 6500K`.

---

## Gdzie to trafia na stronie

| Plik | Miejsce | Proporcje |
|---|---|---|
| `assets/photos/hero-wide.webp` | karta „Schroniska w liczbach” | 16:9 |
| `assets/photos/prawo.webp` | kafel „Prawo” + karta KROPiK | 16:9 |
| `assets/photos/zdrowie.webp` | kafel „Weterynaria” + karta szkolenia | 16:9 |
| `assets/photos/psiecko.webp` | karta „Pies i dziecko” | 16:9 |
| `assets/photos/portret.webp` | rezerwa | 4:5 |
| `assets/photos/prawnik.webp` | **nowy** — kafel prawa | 16:9 |
| `assets/photos/apteczka.webp` | **nowy** — sekcja nagłego wypadku | 16:9 |
| `assets/photos/spacer.webp` | **nowy** — karta transportu | 16:9 |
| `assets/photos/schronisko.webp` | **nowy** — karta schronisk | 16:9 |
| `assets/photos/senior.webp` | **nowy** — karta o śmierci psa | 16:9 |
| `assets/photos/szczeniak.webp` | **nowy** — karta adopcji | 16:9 |

Nazwy plików trzymaj dokładnie takie — wtedy wystarczy je wrzucić do
`assets/photos/` i podmiana na stronie to jedna linijka.

**Format:** WebP, jakość ~80, szerokość 1400 px dla 16:9. Konwersja:
`python -c "from PIL import Image; Image.open('x.png').save('x.webp', quality=80)"`

---

## A. Kafle na stronie głównej — poziome 16:9

**prawnik.webp — prawo i odpowiedzialność**
```
[styl] + golden retriever sitting calmly beside a desk with a closed law
book and a pair of glasses, bright modern office, dog in the left third,
large clean empty space on the right --ar 16:9
```

**zdrowie.webp — gabinet weterynaryjny**
```
[styl] + calm golden retriever on an examination table, veterinarian's hands
with a stethoscope, bright modern clinic with white and pale blue surfaces,
dog looking trustingly at camera --ar 16:9
```

**apteczka.webp — nagły wypadek**
```
[styl] + flat lay of a dog first aid kit on a white surface: bandage roll,
tick remover, digital thermometer, saline bottle, gauze, seen from directly
above, cool clean light, generous empty space --ar 16:9
```

**spacer.webp — transport i miasto**
```
[styl] + golden retriever walking on a leash beside owner's legs on a clean
city sidewalk, modern tram blurred in the background, bright overcast day,
cool tones, candid lifestyle shot, low angle --ar 16:9
```

**psiecko.webp — pies i dziecko**
```
[styl] + a calm golden retriever lying on a light rug while a small child
sits at a safe distance, bright minimalist living room, soft daylight from
a large window, warm gesture but clearly supervised, candid --ar 16:9
```

**schronisko.webp — schroniska**
```
[styl] + a mixed-breed dog looking through the bars of a clean modern animal
shelter kennel, soft daylight, muted colors, documentary style, respectful
and calm rather than dramatic --ar 16:9
```

**senior.webp — starość psa**
```
[styl] + close-up portrait of an old golden retriever with a grey muzzle
resting its head on a person's knee, eyes half-closed, soft cool daylight,
quiet and dignified, no sadness kitsch --ar 16:9
```

**szczeniak.webp — adopcja**
```
[styl] + a puppy sitting on a light wooden floor looking up at the camera,
one paw raised, bright empty room, lots of negative space above --ar 16:9
```

---

## B. Portret pionowy — 4:5

**portret.webp**
```
[styl] + beautiful golden retriever sitting upright, front view, full body,
looking directly at camera with a gentle expression, centered, clean
background, empty space above the head for a headline --ar 4:5
```

---

## C. Grafiki abstrakcyjne — jeśli zabraknie zdjęć

Zamiast fotografii można wygenerować tła gradientowe pod sekcje:

```
Abstract soft gradient mesh background, pink #F38AD8 blending into light
blue #7CCBFF over an off-white base #FCFBFF, very smooth, blurred, no
texture, no noise, minimal, like a modern SaaS website header --ar 16:9
```

---

## Wskazówki

1. **Jeden pies.** Generuj po cztery warianty i wybieraj zdjęcia
   z retrieverem o tej samej maści — strona ma wyglądać jak jedna sesja.
2. **Puste miejsce.** Wybieraj kadry z czystym tłem z boku albo u góry.
3. **Chłodne światło.** Największy błąd generatorów przy tym stylu to
   ciepły żółty odcień. Jeśli wychodzi beż — dopisz `cool white balance`.
4. **Bez tekstu na obrazie.** Wszystkie napisy dokłada strona.
