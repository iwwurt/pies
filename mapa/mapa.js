/* Mapa lecznic weterynaryjnych i schronisk. Dane: OpenStreetMap (ODbL). */

(function () {
  "use strict";

  var TYPY = { v: "Weterynarz", s: "Schronisko" };
  var SRODEK_POLSKI = [52.07, 19.48];
  var LIMIT_LISTY = 60;

  var elLista = document.getElementById("lista");
  var elStan = document.getElementById("stan");
  var elSzukaj = document.getElementById("szukaj");
  var elMiasta = document.getElementById("lista-miast");
  var elLokalizacja = document.getElementById("moja-lokalizacja");
  var przyciskiTypu = [].slice.call(document.querySelectorAll(".mapa-przelacznik button"));

  if (!elLista || typeof L === "undefined") return;

  // Celowo waska lista: lepiej pominac czynna lecznice, niz wyslac kogos
  // o trzeciej w nocy pod zamkniete drzwi. "Sa 00:00-24:00" to sobota na
  // caly dzien, a nie calodobowosc - takie zapisy tu nie przechodza.
  var CALODOBOWE = [
    "24/7",
    "00:00-24:00",
    "mo-su00:00-24:00",
    "mo-su,ph00:00-24:00",
    "24/7;ph24/7",
  ];

  function calodobowa(p) {
    if (!p.h) return false;
    return CALODOBOWE.indexOf(p.h.toLowerCase().replace(/\s/g, "")) !== -1;
  }

  var punkty = [];
  var widoczneTypy = { v: true, s: true };
  var tylkoCalodobowe = false;
  var mojaPozycja = null;
  var markery = {};

  var mapa = L.map("mapa", { scrollWheelZoom: true }).setView(SRODEK_POLSKI, 6);

  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(mapa);

  var klaster = L.markerClusterGroup({
    maxClusterRadius: 60,
    showCoverageOnHover: false,
    chunkedLoading: true,
  });
  mapa.addLayer(klaster);

  function ikona(typ) {
    var kolor = typ === "s" ? "#5d8065" : "#34718c";
    return L.divIcon({
      className: "",
      iconSize: [18, 18],
      iconAnchor: [9, 9],
      html:
        '<span style="display:block;width:18px;height:18px;border-radius:50%;' +
        "background:" +
        kolor +
        ';border:3px solid #fffdf9;box-shadow:0 2px 6px rgba(0,0,0,.35)"></span>',
    });
  }

  function odleglosc(aLat, aLon, bLat, bLon) {
    var R = 6371;
    var dLat = ((bLat - aLat) * Math.PI) / 180;
    var dLon = ((bLon - aLon) * Math.PI) / 180;
    var a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((aLat * Math.PI) / 180) *
        Math.cos((bLat * Math.PI) / 180) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);
    return 2 * R * Math.asin(Math.sqrt(a));
  }

  function bezpieczny(tekst) {
    var d = document.createElement("div");
    d.textContent = tekst == null ? "" : String(tekst);
    return d.innerHTML;
  }

  function bezpiecznyAdres(url) {
    var u = String(url || "").trim();
    return /^https?:\/\//i.test(u) ? u : null;
  }

  function trescPopupu(p) {
    var czesci = ["<strong>" + bezpieczny(p.n) + "</strong>"];
    czesci.push("<em>" + TYPY[p.t] + (p._24 ? " · czynne całą dobę" : "") + "</em>");
    var adres = [p.a, p.m].filter(Boolean).join(", ");
    if (adres) czesci.push(bezpieczny(adres));
    if (p.h) czesci.push("Godziny: " + bezpieczny(p.h));
    if (p.p) czesci.push('<a href="tel:' + bezpieczny(p.p) + '">' + bezpieczny(p.p) + "</a>");
    var www = bezpiecznyAdres(p.w);
    if (www) czesci.push('<a href="' + bezpieczny(www) + '" target="_blank" rel="noopener">Strona ↗</a>');
    czesci.push(
      '<a href="https://www.openstreetmap.org/?mlat=' +
        p.y +
        "&mlon=" +
        p.x +
        '#map=18/' +
        p.y +
        "/" +
        p.x +
        '" target="_blank" rel="noopener">Pokaż w OpenStreetMap ↗</a>'
    );
    return czesci.join("<br />");
  }

  function pasujeDoFrazy(p, fraza) {
    if (!fraza) return true;
    var f = fraza.toLowerCase();
    return (
      (p.n && p.n.toLowerCase().indexOf(f) !== -1) ||
      (p.m && p.m.toLowerCase().indexOf(f) !== -1) ||
      (p.a && p.a.toLowerCase().indexOf(f) !== -1)
    );
  }

  function aktualne() {
    var fraza = (elSzukaj && elSzukaj.value.trim()) || "";
    return punkty.filter(function (p) {
      if (!widoczneTypy[p.t]) return false;
      if (tylkoCalodobowe && !p._24) return false;
      return pasujeDoFrazy(p, fraza);
    });
  }

  function rysujMarkery(lista) {
    klaster.clearLayers();
    markery = {};
    var warstwy = lista.map(function (p) {
      var m = L.marker([p.y, p.x], { icon: ikona(p.t), title: p.n });
      m.bindPopup(trescPopupu(p));
      markery[p.id] = m;
      return m;
    });
    klaster.addLayers(warstwy);
  }

  function rysujListe(lista) {
    var punktOdniesienia = mojaPozycja;
    var kopia = lista.slice();

    if (punktOdniesienia) {
      kopia.forEach(function (p) {
        p._d = odleglosc(punktOdniesienia[0], punktOdniesienia[1], p.y, p.x);
      });
      kopia.sort(function (a, b) {
        return a._d - b._d;
      });
    }

    var pokazane = kopia.slice(0, LIMIT_LISTY);
    elLista.innerHTML = pokazane
      .map(function (p) {
        var meta = [p.a, p.m].filter(Boolean).join(", ");
        var wiersze = [];
        if (meta) wiersze.push(bezpieczny(meta));
        if (p.h) wiersze.push(bezpieczny(p.h));
        if (p.p) wiersze.push(bezpieczny(p.p));
        return (
          '<button class="mapa-karta" type="button" data-id="' +
          p.id +
          '">' +
          '<span class="mapa-karta__typ mapa-karta__typ--' +
          p.t +
          '">' +
          TYPY[p.t] +
          "</span>" +
          (p._24 ? '<span class="mapa-karta__typ mapa-karta__typ--24">całą dobę</span>' : "") +
          '<p class="mapa-karta__nazwa">' +
          bezpieczny(p.n) +
          "</p>" +
          '<p class="mapa-karta__meta">' +
          (wiersze.join("<br />") || "Brak dodatkowych danych w OpenStreetMap") +
          "</p>" +
          (p._d != null
            ? '<span class="mapa-karta__odleglosc">' +
              (p._d < 1 ? Math.round(p._d * 1000) + " m" : p._d.toFixed(1) + " km") +
              " stąd</span>"
            : "") +
          "</button>"
        );
      })
      .join("");

    if (!pokazane.length) {
      elLista.innerHTML =
        '<p class="mapa-karta__meta" style="padding:26px">Nic nie znaleziono. Spróbuj innej nazwy miasta.</p>';
    }

    var ile = lista.length;
    elStan.textContent =
      ile === 0
        ? "Brak wyników"
        : "Znaleziono " +
          ile +
          (ile > LIMIT_LISTY ? " · lista pokazuje " + LIMIT_LISTY : "") +
          (mojaPozycja ? " · od najbliższych" : "");
  }

  function odswiez(dopasujWidok) {
    var lista = aktualne();
    rysujMarkery(lista);
    rysujListe(lista);

    if (dopasujWidok && lista.length) {
      var granice = L.latLngBounds(
        lista.map(function (p) {
          return [p.y, p.x];
        })
      );
      mapa.fitBounds(granice.pad(0.15), { maxZoom: 14 });
    }
  }

  elLista.addEventListener("click", function (e) {
    var karta = e.target.closest(".mapa-karta");
    if (!karta) return;
    var m = markery[karta.getAttribute("data-id")];
    if (!m) return;
    mapa.setView(m.getLatLng(), Math.max(mapa.getZoom(), 15), { animate: true });
    klaster.zoomToShowLayer(m, function () {
      m.openPopup();
    });
  });

  przyciskiTypu.forEach(function (b) {
    b.addEventListener("click", function () {
      var typ = b.getAttribute("data-typ");
      var wlaczone = b.getAttribute("aria-pressed") === "true";
      // nie pozwalamy wylaczyc obu rodzajow naraz
      var drugi = przyciskiTypu.find(function (x) {
        return x !== b;
      });
      if (wlaczone && drugi && drugi.getAttribute("aria-pressed") !== "true") return;
      b.setAttribute("aria-pressed", String(!wlaczone));
      widoczneTypy[typ] = !wlaczone;
      odswiez(false);
    });
  });

  var przelacznik24 = document.querySelector("[data-tylko-24]");
  if (przelacznik24) {
    przelacznik24.addEventListener("click", function () {
      tylkoCalodobowe = przelacznik24.getAttribute("aria-pressed") !== "true";
      przelacznik24.setAttribute("aria-pressed", String(tylkoCalodobowe));
      odswiez(false);
    });
  }

  function zKotwicy() {
    // /zatrucia/ prowadzi tu przez #calodobowe - filtr ma byc juz wlaczony
    if (window.location.hash !== "#calodobowe" || !przelacznik24) return;
    tylkoCalodobowe = true;
    przelacznik24.setAttribute("aria-pressed", "true");
  }

  window.addEventListener("hashchange", function () {
    // dziala tez, gdy ktos zmieni adres bez przeladowania strony
    zKotwicy();
    if (punkty.length) odswiez(false);
  });

  var opoznienie;
  if (elSzukaj) {
    elSzukaj.addEventListener("input", function () {
      clearTimeout(opoznienie);
      opoznienie = setTimeout(function () {
        odswiez(Boolean(elSzukaj.value.trim()));
      }, 220);
    });
  }

  if (elLokalizacja) {
    elLokalizacja.addEventListener("click", function () {
      if (!navigator.geolocation) {
        elStan.textContent = "Przeglądarka nie udostępnia lokalizacji";
        return;
      }
      elStan.textContent = "Ustalanie lokalizacji…";
      navigator.geolocation.getCurrentPosition(
        function (poz) {
          mojaPozycja = [poz.coords.latitude, poz.coords.longitude];
          L.circleMarker(mojaPozycja, {
            radius: 9,
            color: "#b0833f",
            weight: 3,
            fillColor: "#b0833f",
            fillOpacity: 0.35,
          })
            .addTo(mapa)
            .bindPopup("Tu jesteś");
          mapa.setView(mojaPozycja, 12);
          odswiez(false);
        },
        function () {
          elStan.textContent = "Nie udało się ustalić lokalizacji — wpisz miasto ręcznie";
        },
        { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 }
      );
    });
  }

  fetch("../dane/punkty.json")
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(function (dane) {
      punkty = dane.map(function (p, i) {
        p.id = "p" + i;
        p._24 = calodobowa(p);
        return p;
      });

      var ile24 = punkty.filter(function (p) {
        return p._24;
      }).length;
      var etykieta = document.querySelector("[data-liczba-24]");
      if (etykieta) etykieta.textContent = ile24;

      var miasta = {};
      punkty.forEach(function (p) {
        if (p.m) miasta[p.m] = true;
      });
      if (elMiasta) {
        elMiasta.innerHTML = Object.keys(miasta)
          .sort(function (a, b) {
            return a.localeCompare(b, "pl");
          })
          .map(function (m) {
            return '<option value="' + bezpieczny(m) + '"></option>';
          })
          .join("");
      }

      zKotwicy();
      odswiez(false);
    })
    .catch(function (err) {
      elStan.textContent = "Nie udało się wczytać danych mapy";
      elLista.innerHTML =
        '<p class="mapa-karta__meta" style="padding:26px">Spróbuj odświeżyć stronę. Szczegóły: ' +
        bezpieczny(err.message) +
        "</p>";
    });
})();
