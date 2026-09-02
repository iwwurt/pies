/* Narzedzia: zakladki, wiek psa, terminarz szczepien, KROPiK. */

(function () {
  "use strict";

  /* ---------------------------------------------------------- zakladki --- */

  var zakladki = [].slice.call(document.querySelectorAll('.narz-zakladki [role="tab"]'));

  function pokaz(tab) {
    zakladki.forEach(function (t) {
      var wybrany = t === tab;
      t.setAttribute("aria-selected", String(wybrany));
      t.tabIndex = wybrany ? 0 : -1;
      var panel = document.getElementById(t.getAttribute("aria-controls"));
      if (panel) panel.hidden = !wybrany;
    });
  }

  function otworzZKotwicy() {
    // pozwala wejsc prosto w konkretne narzedzie z innej strony,
    // np. /koszty/ -> /narzedzia/#panel-oplata
    var hash = window.location.hash.replace("#", "");
    if (!hash) return;
    var tab = zakladki.filter(function (t) {
      return t.getAttribute("aria-controls") === hash || t.id === hash;
    })[0];
    if (!tab) return;
    pokaz(tab);
    var panel = document.getElementById(tab.getAttribute("aria-controls"));
    if (panel) panel.scrollIntoView({ block: "start" });
  }

  zakladki.forEach(function (tab, i) {
    tab.addEventListener("click", function () {
      pokaz(tab);
    });
    tab.addEventListener("keydown", function (e) {
      var krok = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
      if (!krok) return;
      e.preventDefault();
      var next = zakladki[(i + krok + zakladki.length) % zakladki.length];
      pokaz(next);
      next.focus();
    });
  });

  otworzZKotwicy();
  window.addEventListener("hashchange", otworzZKotwicy);

  /* --------------------------------------------------------- wiek psa --- */

  var TEMPO = { maly: 4, sredni: 5, duzy: 6, olbrzymi: 7 };

  function wiekLudzki(lata, rozmiar) {
    if (lata <= 0) return 0;
    if (lata <= 1) return 15 * lata;
    if (lata <= 2) return 15 + 9 * (lata - 1);
    return 24 + (lata - 2) * TEMPO[rozmiar];
  }

  function etap(lata, rozmiar) {
    var prog = rozmiar === "olbrzymi" ? 6 : rozmiar === "duzy" ? 7 : rozmiar === "sredni" ? 8 : 9;
    if (lata < 1) return "szczeniak — okres najszybszych zmian, także tych w głowie";
    if (lata < 2) return "młody pies — dorosły ciałem, nie zawsze zachowaniem";
    if (lata < prog) return "dorosły pies w pełni sił";
    if (lata < prog + 3) return "wiek senioralny zaczyna się właśnie teraz";
    return "pies starszy — warto częściej robić badania kontrolne";
  }

  var wiekLata = document.getElementById("wiek-lata");
  var wiekRozmiar = document.getElementById("wiek-rozmiar");
  var wiekWynik = document.getElementById("wiek-wynik");
  var wiekOpis = document.getElementById("wiek-opis");
  var wiekTabela = document.getElementById("wiek-tabela");

  function odmianaLat(n) {
    var ostatnia = n % 10;
    var przedostatnia = Math.floor(n / 10) % 10;
    if (n === 1) return "rok";
    if (przedostatnia === 1) return "lat";
    if (ostatnia >= 2 && ostatnia <= 4) return "lata";
    return "lat";
  }

  function przeliczWiek() {
    if (!wiekLata || !wiekWynik) return;
    var lata = parseFloat(wiekLata.value);
    var rozmiar = wiekRozmiar.value;
    if (isNaN(lata) || lata < 0) {
      wiekWynik.textContent = "—";
      wiekOpis.textContent = "Wprowadź wiek psa.";
      return;
    }
    var ludzkie = Math.round(wiekLudzki(lata, rozmiar));
    wiekWynik.textContent = ludzkie + " " + odmianaLat(ludzkie);
    wiekOpis.textContent = "To " + etap(lata, rozmiar) + ".";
  }

  if (wiekTabela) {
    var wiersze = [1, 2, 3, 5, 7, 10, 13, 16];
    wiekTabela.innerHTML = wiersze
      .map(function (l) {
        return (
          "<tr><td>" +
          l +
          " " +
          odmianaLat(l) +
          "</td>" +
          ["maly", "sredni", "duzy", "olbrzymi"]
            .map(function (r) {
              return "<td>" + Math.round(wiekLudzki(l, r)) + "</td>";
            })
            .join("") +
          "</tr>"
        );
      })
      .join("");
  }

  if (wiekLata) {
    wiekLata.addEventListener("input", przeliczWiek);
    wiekRozmiar.addEventListener("change", przeliczWiek);
    przeliczWiek();
  }

  /* ------------------------------------------------------ szczepienia --- */

  var PLAN = [
    { dni: 42, co: "Pierwsze szczepienie", opis: "Nosówka, parwowiroza, adenowiroza, parainfluenza. Typowo między 6. a 8. tygodniem życia." },
    { dni: 63, co: "Druga dawka", opis: "Zwykle 3–4 tygodnie po pierwszej. Odporność buduje się dopiero po całej serii." },
    { dni: 91, co: "Trzecia dawka", opis: "Domyka serię szczenięcą. Dopiero po niej pies jest realnie chroniony." },
    { dni: 100, co: "Wścieklizna — obowiązkowo", opis: "Ustawa wymaga szczepienia w ciągu 30 dni od ukończenia 3. miesiąca życia. To obowiązek, nie zalecenie.", waga: true },
    { dni: 365, co: "Pierwsze doszczepienie", opis: "Po roku powtórka szczepień podstawowych i wścieklizny. Dalej według zaleceń lekarza i rodzaju preparatu." },
  ];

  var ODROBACZANIE = [
    { dni: 14, co: "Odrobaczanie — start", opis: "U szczeniąt zwykle co 2 tygodnie, mniej więcej od 2. tygodnia życia do 12." },
    { dni: 120, co: "Odrobaczanie co miesiąc", opis: "Od około 3. do 6. miesiąca życia. Potem przechodzi się na rytm dorosłego psa." },
    { dni: 200, co: "Rytm dorosłego psa", opis: "Orientacyjnie co 3 miesiące, częściej u psów jedzących surowe mięso, polujących lub mających kontakt z dziećmi." },
  ];

  var szczData = document.getElementById("szcz-data");
  var szczLista = document.getElementById("szcz-lista");
  var szczUwaga = document.getElementById("szcz-uwaga");

  function formatujDate(d) {
    return d.toLocaleDateString("pl-PL", { day: "numeric", month: "long", year: "numeric" });
  }

  function rysujPlan() {
    if (!szczData || !szczLista) return;
    var wartosc = szczData.value;
    if (!wartosc) {
      szczLista.innerHTML = "";
      return;
    }
    var urodziny = new Date(wartosc + "T12:00:00");
    if (isNaN(urodziny.getTime())) return;
    var dzis = new Date();

    var pozycje = PLAN.concat(ODROBACZANIE).sort(function (a, b) {
      return a.dni - b.dni;
    });

    szczLista.innerHTML = pozycje
      .map(function (poz) {
        var kiedy = new Date(urodziny.getTime() + poz.dni * 86400000);
        var minelo = kiedy < dzis;
        return (
          '<li class="narz-krok' +
          (minelo ? " narz-krok--przeszly" : "") +
          '">' +
          '<span class="narz-krok__kiedy">' +
          formatujDate(kiedy).replace(/ \d{4}$/, "") +
          "</span>" +
          '<p class="narz-krok__co">' +
          poz.co +
          (poz.waga ? " ⚖" : "") +
          "</p>" +
          '<p class="narz-krok__opis">' +
          poz.opis +
          "</p>" +
          "</li>"
        );
      })
      .join("");

    var wiekDni = Math.floor((dzis - urodziny) / 86400000);
    if (szczUwaga) {
      szczUwaga.innerHTML =
        "Pies ma dziś <strong>" +
        Math.max(0, wiekDni) +
        " dni</strong>. Pozycje przekreślone to terminy, które już minęły — jeśli któraś została pominięta, " +
        "zapytaj lekarza, czy trzeba serię powtórzyć. Daty są orientacyjne: dokładny odstęp między dawkami " +
        "zależy od użytego preparatu. Szerzej o profilaktyce — rozdział 24 książki.";
    }
  }

  if (szczData) {
    szczData.addEventListener("change", rysujPlan);
    szczData.addEventListener("input", rysujPlan);
  }

  /* ----------------------------------------------------------- KROPiK --- */

  var krCzip = document.getElementById("kr-czip");
  var krWiek = document.getElementById("kr-wiek");
  var krZmiana = document.getElementById("kr-zmiana");
  var krWynik = document.getElementById("kr-wynik");

  function ocenKropik() {
    if (!krWynik) return;
    var czip = krCzip.value;
    var wiek = krWiek.value;
    var zmiana = krZmiana.value;

    if (!czip || !wiek || !zmiana) {
      krWynik.innerHTML = '<p class="narz-wynik__opis">Odpowiedz na trzy pytania obok.</p>';
      return;
    }

    var naglowek;
    var kroki = [];

    if (czip === "nie") {
      naglowek = "Czip trzeba wszczepić";
      kroki.push(
        "Umów wizytę u lekarza weterynarii — wszczepienie transpondera to zabieg na kilka sekund, porównywalny ze zwykłym zastrzykiem."
      );
    } else if (czip === "niewiem") {
      naglowek = "Najpierw sprawdź skanerem";
      kroki.push(
        "Poproś lecznicę o odczyt czytnikiem. Zajmuje to chwilę i zwykle robi się to przy okazji innej wizyty. Bywa, że pies ze schroniska jest już oznakowany, tylko nikt o tym nie wie."
      );
    } else {
      naglowek = "Ponowne czipowanie nie jest potrzebne";
      kroki.push(
        "Jeżeli istniejący transponder da się odczytać zgodnym czytnikiem, ustawa nie wymaga wszczepiania nowego."
      );
    }

    kroki.push(
      "Oznakowanie to jednak dopiero połowa sprawy — numer czipa musi jeszcze trafić do rejestru. To dwa osobne kroki i najczęstsze źródło nieporozumień."
    );

    if (wiek === "szczenie") {
      kroki.push(
        "Dla szczeniąt termin rejestracji ma być powiązany między innymi z pierwszym szczepieniem, więc najwygodniej załatwić obie sprawy przy jednej wizycie."
      );
    } else {
      kroki.push(
        "Dla psów, które już są w domach, ustawa przewiduje przepisy przejściowe i czas na dostosowanie — ale wcześniejsze załatwienie sprawy niczego nie psuje."
      );
    }

    if (zmiana === "tak") {
      kroki.push(
        "Zmiana właściciela oraz inne wskazane zdarzenia mają wiązać się z obowiązkiem aktualizacji danych. Nieaktualny numer telefonu w rejestrze sprawia, że cały system przestaje działać wtedy, gdy jest najbardziej potrzebny — przy zaginięciu psa."
      );
    }

    kroki.push(
      "Zasadnicza część przepisów ma wejść w życie 11 czerwca 2028 roku — masz czas, ale warto wiedzieć, co cię czeka."
    );

    krWynik.innerHTML =
      '<p class="narz-wynik__liczba" style="font-size:clamp(1.6rem,3vw,2.4rem);line-height:1.2">' +
      naglowek +
      "</p>" +
      '<ol style="margin:20px 0 0;padding-left:20px;color:var(--muted);font-size:0.88rem;line-height:1.65">' +
      kroki
        .map(function (k) {
          return '<li style="margin-bottom:12px">' + k + "</li>";
        })
        .join("") +
      "</ol>";
  }

  [krCzip, krWiek, krZmiana].forEach(function (el) {
    if (el) el.addEventListener("change", ocenKropik);
  });

  /* ------------------------------------------- oplata od psa --- */

  var opGmina = document.getElementById("op-gmina");
  var opFraza = document.getElementById("op-fraza");
  var opSzukaj = document.getElementById("op-szukaj");
  var opKopiuj = document.getElementById("op-kopiuj");

  function frazaWyszukiwania() {
    var gmina = opGmina ? opGmina.value.trim() : "";
    return gmina
      ? "opłata od posiadania psów " + gmina + " BIP"
      : "opłata od posiadania psów BIP";
  }

  function odswiezFraze() {
    var fraza = frazaWyszukiwania();
    if (opFraza) opFraza.textContent = fraza;
    if (opSzukaj) opSzukaj.href = "https://duckduckgo.com/?q=" + encodeURIComponent(fraza);
  }

  if (opGmina) {
    opGmina.addEventListener("input", odswiezFraze);
    odswiezFraze();
  }

  if (opKopiuj) {
    opKopiuj.addEventListener("click", function () {
      var fraza = frazaWyszukiwania();
      var potwierdz = function () {
        var byl = opKopiuj.textContent;
        opKopiuj.textContent = "Skopiowane";
        setTimeout(function () {
          opKopiuj.textContent = byl;
        }, 1600);
      };

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(fraza).then(potwierdz, zapasoweKopiowanie);
      } else {
        zapasoweKopiowanie();
      }

      function zapasoweKopiowanie() {
        // starsze przegladarki i strony bez bezpiecznego kontekstu
        var pole = document.createElement("textarea");
        pole.value = fraza;
        pole.setAttribute("readonly", "");
        pole.style.position = "fixed";
        pole.style.opacity = "0";
        document.body.appendChild(pole);
        pole.select();
        try {
          document.execCommand("copy");
          potwierdz();
        } catch (e) {
          opKopiuj.textContent = "Zaznacz i skopiuj ręcznie";
        }
        document.body.removeChild(pole);
      }
    });
  }
})();
