# „Pies w Polsce” — strona sprzedażowa

Gotowa, responsywna strona statyczna napisana w HTML, CSS i JavaScript.

## Podgląd lokalny

Najprościej otworzyć `index.html` w przeglądarce. Można też uruchomić lokalny serwer w tym katalogu:

```powershell
python -m http.server 8080
```

Następnie otworzyć `http://localhost:8080`.

## Podłączenie płatności

W pliku `script.js` na początku znajduje się stała:

```js
const CHECKOUT_URL = "";
```

Po wybraniu operatora płatności należy wkleić tu adres hostowanego checkoutu. Dopóki adres jest pusty, przyciski otwierają uczciwy komunikat demonstracyjny i nie pobierają opłaty. Po podaniu adresu wszystkie przyciski zakupu automatycznie zaczną przekierowywać do płatności, a informacja o trybie demonstracyjnym zniknie.

Do pełnej sprzedaży treści cyfrowej potrzebne są trzy elementy:

1. hostowany checkout operatora płatności,
2. automatyczna wiadomość e-mail po potwierdzeniu płatności,
3. bezpieczny link do PDF oraz materiałów audio.

## Przed publikacją

- potwierdź: 509 stron, 61 rozdziałów i 61 nagrań,
- uzupełnij dane sprzedawcy, kontakt, regulamin, politykę prywatności i zasady reklamacji,
- opisz sposób dostępu do podcastów i ważność linków,
- zweryfikuj treści prawne, medyczne i behawioralne ze specjalistami,
- potwierdź prawa do okładki i wizerunku psa,
- przy natychmiastowym dostarczeniu treści cyfrowej zadbaj o prawidłową zgodę konsumenta dotyczącą rozpoczęcia świadczenia przed upływem terminu odstąpienia.

Strona celowo nie zawiera fikcyjnych opinii, danych autora ani atrap formularzy płatniczych.
