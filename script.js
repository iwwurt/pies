"use strict";

document.documentElement.classList.remove("no-js");
document.documentElement.classList.add("js");

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const header = document.querySelector("[data-header]");
const menuToggle = document.querySelector("[data-menu-toggle]");
const nav = document.querySelector("[data-nav]");

function setMenu(open) {
  if (!menuToggle || !nav) return;
  if (open) {
    const headerBottom = header?.getBoundingClientRect().bottom || 82;
    nav.style.setProperty("--nav-top", `${Math.round(headerBottom)}px`);
  }
  menuToggle.setAttribute("aria-expanded", String(open));
  menuToggle.setAttribute("aria-label", open ? "Zamknij menu" : "Otwórz menu");
  nav.classList.toggle("is-open", open);
  document.body.classList.toggle("menu-open", open);
}

menuToggle?.addEventListener("click", () => {
  setMenu(menuToggle.getAttribute("aria-expanded") !== "true");
});

nav?.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setMenu(false)));

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && menuToggle?.getAttribute("aria-expanded") === "true") {
    setMenu(false);
    menuToggle.focus();
  }
});

document.addEventListener("click", (event) => {
  if (
    menuToggle?.getAttribute("aria-expanded") === "true" &&
    !nav?.contains(event.target) &&
    !menuToggle.contains(event.target)
  ) {
    setMenu(false);
  }
});

function updateHeader() {
  header?.classList.toggle("is-scrolled", window.scrollY > 12);
}

updateHeader();
window.addEventListener("scroll", updateHeader, { passive: true });

const reveals = [...document.querySelectorAll(".reveal")];

if (reducedMotion || !("IntersectionObserver" in window)) {
  reveals.forEach((element) => element.classList.add("is-visible"));
} else {
  const revealObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.11, rootMargin: "0px 0px -42px" },
  );

  reveals.forEach((element) => revealObserver.observe(element));
}

const numberFormatter = new Intl.NumberFormat("pl-PL");

function animateCount(element) {
  const target = Number(element.dataset.count || 0);
  const suffix = element.dataset.suffix || "";

  if (!target || reducedMotion) {
    element.textContent = `${numberFormatter.format(target)}${suffix}`;
    return;
  }

  const duration = 850;
  const start = performance.now();

  function frame(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = Math.round(target * eased);
    element.textContent = `${numberFormatter.format(value)}${suffix}`;
    if (progress < 1) window.requestAnimationFrame(frame);
  }

  window.requestAnimationFrame(frame);
}

const counters = [...document.querySelectorAll("[data-count]")];

if (!("IntersectionObserver" in window)) {
  counters.forEach(animateCount);
} else {
  const counterObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        animateCount(entry.target);
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.7 },
  );

  counters.forEach((counter) => counterObserver.observe(counter));
}

document.querySelectorAll("[data-parts]").forEach((parts) => {
  const tabs = [...parts.querySelectorAll('[role="tab"]')];
  const panels = [...parts.querySelectorAll('[role="tabpanel"]')];

  function selectTab(selectedTab, moveFocus = false) {
    tabs.forEach((tab) => {
      const selected = tab === selectedTab;
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;

      const panel = panels.find((item) => item.id === tab.getAttribute("aria-controls"));
      if (panel) panel.hidden = !selected;
    });

    if (moveFocus) selectedTab.focus();
  }

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => selectTab(tab));
    tab.addEventListener("keydown", (event) => {
      let nextIndex = index;

      if (["ArrowRight", "ArrowDown"].includes(event.key)) nextIndex = (index + 1) % tabs.length;
      if (["ArrowLeft", "ArrowUp"].includes(event.key)) nextIndex = (index - 1 + tabs.length) % tabs.length;
      if (event.key === "Home") nextIndex = 0;
      if (event.key === "End") nextIndex = tabs.length - 1;

      if (nextIndex !== index) {
        event.preventDefault();
        selectTab(tabs[nextIndex], true);
      }
    });
  });

  selectTab(tabs.find((tab) => tab.getAttribute("aria-selected") === "true") || tabs[0]);
});

document.querySelectorAll("[data-calculator]").forEach((calculator) => {
  const monthly = calculator.querySelector("[data-monthly]");
  const years = calculator.querySelector("[data-years]");
  const total = calculator.querySelector("[data-total]");
  const monthlyOutput = calculator.querySelector("[data-monthly-output]");
  const yearsOutput = calculator.querySelector("[data-years-output]");
  const yearsLabel = calculator.querySelector("[data-years-label]");
  const monthlyLabel = calculator.querySelector("[data-monthly-label]");
  const daily = calculator.querySelector("[data-daily]");

  if (!monthly || !years || !total) return;

  const yearsWord = (value) => {
    const last = value % 10;
    const lastTwo = value % 100;
    if (value === 1) return "rok";
    if ([2, 3, 4].includes(last) && ![12, 13, 14].includes(lastTwo)) return "lata";
    return "lat";
  };

  const setProgress = (input) => {
    const min = Number(input.min);
    const max = Number(input.max);
    const value = Number(input.value);
    const progress = ((value - min) / (max - min)) * 100;
    input.style.setProperty("--range-progress", `${progress}%`);
  };

  function updateCalculator() {
    const monthlyValue = Number(monthly.value);
    const yearsValue = Number(years.value);
    const fullCost = monthlyValue * yearsValue * 12;
    const dailyCost = Math.round((monthlyValue * 12) / 365);
    const yearsText = `${yearsValue} ${yearsWord(yearsValue)}`;

    total.textContent = `${numberFormatter.format(fullCost)} zł`;
    if (monthlyOutput) monthlyOutput.textContent = `${numberFormatter.format(monthlyValue)} zł`;
    if (yearsOutput) yearsOutput.textContent = yearsText;
    if (yearsLabel) yearsLabel.textContent = yearsText;
    if (monthlyLabel) monthlyLabel.textContent = `${numberFormatter.format(monthlyValue)} zł`;
    if (daily) daily.textContent = `${numberFormatter.format(dailyCost)} zł`;

    setProgress(monthly);
    setProgress(years);
  }

  monthly.addEventListener("input", updateCalculator);
  years.addEventListener("input", updateCalculator);
  updateCalculator();
});

document.querySelectorAll("[data-photo-carousel]").forEach((carousel) => {
  const track = carousel.querySelector("[data-photo-track]");
  const cards = [...carousel.querySelectorAll(".photo-card")];
  const prev = carousel.querySelector("[data-photo-prev]");
  const next = carousel.querySelector("[data-photo-next]");
  const dots = carousel.querySelector("[data-photo-dots]");
  let activeIndex = 0;
  let ticking = false;

  if (!track || !cards.length) return;

  cards.forEach((_, index) => {
    const dot = document.createElement("span");
    dot.classList.toggle("is-active", index === 0);
    dots?.append(dot);
  });

  function updateDots(index) {
    activeIndex = Math.max(0, Math.min(index, cards.length - 1));
    dots?.querySelectorAll("span").forEach((dot, dotIndex) => {
      dot.classList.toggle("is-active", dotIndex === activeIndex);
    });
  }

  function scrollToCard(index) {
    const targetIndex = Math.max(0, Math.min(index, cards.length - 1));
    const card = cards[targetIndex];
    track.scrollTo({ left: card.offsetLeft - track.offsetLeft, behavior: reducedMotion ? "auto" : "smooth" });
    updateDots(targetIndex);
  }

  function findNearestCard() {
    const left = track.scrollLeft;
    let nearest = 0;
    let distance = Infinity;

    cards.forEach((card, index) => {
      const cardDistance = Math.abs(card.offsetLeft - track.offsetLeft - left);
      if (cardDistance < distance) {
        distance = cardDistance;
        nearest = index;
      }
    });

    updateDots(nearest);
    ticking = false;
  }

  track.addEventListener(
    "scroll",
    () => {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(findNearestCard);
    },
    { passive: true },
  );

  prev?.addEventListener("click", () => scrollToCard(activeIndex - 1));
  next?.addEventListener("click", () => scrollToCard(activeIndex + 1));
});

document.querySelectorAll("[data-reader]").forEach((reader) => {
  const totalPages = Number(reader.dataset.pages || 0);
  const pattern = reader.dataset.pattern || "";
  const stage = reader.querySelector("[data-reader-stage]");
  const primary = reader.querySelector("[data-reader-primary]");
  const secondary = reader.querySelector("[data-reader-secondary]");
  const previous = reader.querySelector("[data-reader-prev]");
  const next = reader.querySelector("[data-reader-next]");
  const currentLabel = reader.querySelector("[data-reader-current]");
  const range = reader.querySelector("[data-reader-range]");
  const fullscreen = reader.querySelector("[data-reader-fullscreen]");
  const spreadQuery = window.matchMedia("(min-width: 761px)");
  let currentPage = 1;
  let touchStartX = null;
  let touchStartY = null;

  if (!totalPages || !pattern || !stage || !primary || !range) return;

  const pageSource = (page) => pattern.replace("NN", String(page).padStart(2, "0"));

  function normalizePage(page) {
    let nextPage = Math.max(1, Math.min(page, totalPages));
    if (spreadQuery.matches && nextPage % 2 === 0) nextPage -= 1;
    return nextPage;
  }

  function preload(page) {
    if (page < 1 || page > totalPages) return;
    const image = new Image();
    image.src = pageSource(page);
  }

  function updateRangeProgress() {
    const progress = ((currentPage - 1) / (totalPages - 1)) * 100;
    range.style.setProperty("--reader-progress", `${progress}%`);
  }

  function showPage(page) {
    currentPage = normalizePage(page);
    const showSpread = spreadQuery.matches;
    const secondPage = currentPage + 1;

    primary.src = pageSource(currentPage);
    primary.alt = `Strona ${currentPage} bezpłatnego fragmentu książki Pies w Polsce`;

    if (secondary) {
      const hasSecondPage = showSpread && secondPage <= totalPages;
      secondary.hidden = !hasSecondPage;
      if (hasSecondPage) {
        secondary.src = pageSource(secondPage);
        secondary.alt = `Strona ${secondPage} bezpłatnego fragmentu książki Pies w Polsce`;
      }
    }

    const lastVisiblePage = showSpread ? Math.min(secondPage, totalPages) : currentPage;
    if (currentLabel) {
      currentLabel.textContent = lastVisiblePage > currentPage ? `${currentPage}–${lastVisiblePage}` : String(currentPage);
    }

    range.value = String(currentPage);
    previous.disabled = currentPage <= 1;
    next.disabled = lastVisiblePage >= totalPages;
    updateRangeProgress();

    const step = showSpread ? 2 : 1;
    preload(currentPage + step);
    preload(currentPage + step + (showSpread ? 1 : 0));
    preload(currentPage - step);
  }

  function move(direction) {
    showPage(currentPage + direction * (spreadQuery.matches ? 2 : 1));
  }

  previous?.addEventListener("click", () => move(-1));
  next?.addEventListener("click", () => move(1));
  range.addEventListener("input", () => showPage(Number(range.value)));

  stage.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft" || event.key === "PageUp") {
      event.preventDefault();
      move(-1);
    }
    if (event.key === "ArrowRight" || event.key === "PageDown" || event.key === " ") {
      event.preventDefault();
      move(1);
    }
    if (event.key === "Home") {
      event.preventDefault();
      showPage(1);
    }
    if (event.key === "End") {
      event.preventDefault();
      showPage(totalPages);
    }
  });

  stage.addEventListener(
    "touchstart",
    (event) => {
      const touch = event.changedTouches[0];
      touchStartX = touch.clientX;
      touchStartY = touch.clientY;
    },
    { passive: true },
  );

  stage.addEventListener(
    "touchend",
    (event) => {
      if (touchStartX === null || touchStartY === null) return;
      const touch = event.changedTouches[0];
      const deltaX = touch.clientX - touchStartX;
      const deltaY = touch.clientY - touchStartY;

      if (Math.abs(deltaX) > 48 && Math.abs(deltaX) > Math.abs(deltaY) * 1.2) {
        move(deltaX < 0 ? 1 : -1);
      }

      touchStartX = null;
      touchStartY = null;
    },
    { passive: true },
  );

  fullscreen?.addEventListener("click", async () => {
    if (typeof reader.requestFullscreen !== "function") {
      stage.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "center" });
      return;
    }

    try {
      if (!document.fullscreenElement) {
        await reader.requestFullscreen?.();
      } else {
        await document.exitFullscreen?.();
      }
    } catch {
      stage.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "center" });
    }
  });

  spreadQuery.addEventListener?.("change", () => showPage(currentPage));
  showPage(1);
});

document.querySelectorAll(".faq-list details").forEach((item) => {
  item.addEventListener("toggle", () => {
    if (!item.open) return;
    document.querySelectorAll(".faq-list details[open]").forEach((other) => {
      if (other !== item) other.removeAttribute("open");
    });
  });
});

const hero = document.querySelector(".hero");
const finalOffer = document.querySelector("#pobierz");
const mobileBuy = document.querySelector("[data-mobile-buy]");
let mobileBuyTicking = false;

function updateMobileBuy() {
  if (!hero || !finalOffer || !mobileBuy) return;

  const isMobile = window.matchMedia("(max-width: 760px)").matches;
  const heroPassed = hero.getBoundingClientRect().bottom < 120;
  const finalOfferVisible = finalOffer.getBoundingClientRect().top < window.innerHeight * 0.82;
  mobileBuy.hidden = !(isMobile && heroPassed && !finalOfferVisible);
  mobileBuyTicking = false;
}

function requestMobileBuyUpdate() {
  if (mobileBuyTicking) return;
  mobileBuyTicking = true;
  window.requestAnimationFrame(updateMobileBuy);
}

updateMobileBuy();
window.addEventListener("scroll", requestMobileBuyUpdate, { passive: true });
window.addEventListener("resize", requestMobileBuyUpdate);

/* Linki, ktore czekaja na uzupelnienie (playlista YouTube, wsparcie autora). */
document.querySelectorAll("[data-donate]").forEach((element) => {
  if ((element.getAttribute("href") || "").startsWith("{{")) element.remove();
});

document.querySelectorAll("[data-yt-playlist]").forEach((element) => {
  const href = element.getAttribute("href") || "";
  if (!/^https?:/.test(href)) return;

  element.target = "_blank";
  element.rel = "noopener";
  const label = element.querySelector("[data-yt-playlist-label]");
  if (label) label.textContent = "Podcast na YouTube";
  const arrow = element.querySelector(".button__arrow");
  if (arrow) arrow.textContent = "↗";
});
