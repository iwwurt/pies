"use strict";

// Po wyborze operatora płatności wklej tutaj adres hostowanego checkoutu.
// Przykład: const CHECKOUT_URL = "https://adres-twojej-platnosci.pl/...";
const CHECKOUT_URL = "";

document.documentElement.classList.remove("no-js");
document.documentElement.classList.add("js");

const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
if (!prefersReducedMotion) document.documentElement.classList.add("motion-ok");

const header = document.querySelector("[data-header]");
const menuToggle = document.querySelector("[data-menu-toggle]");
const nav = document.querySelector("[data-nav]");
const dialog = document.querySelector("#checkout-dialog");
const hero = document.querySelector(".hero");
const offer = document.querySelector("#kup");
const mobileBuy = document.querySelector("[data-mobile-buy]");
let lastCheckoutTrigger = null;

function setMenu(open) {
  if (!menuToggle || !nav) return;
  menuToggle.setAttribute("aria-expanded", String(open));
  menuToggle.setAttribute("aria-label", open ? "Zamknij menu" : "Otwórz menu");
  nav.classList.toggle("is-open", open);
  document.body.classList.toggle("menu-open", open);
}

menuToggle?.addEventListener("click", () => {
  setMenu(menuToggle.getAttribute("aria-expanded") !== "true");
});

nav?.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => setMenu(false));
});

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
  header?.classList.toggle("is-scrolled", window.scrollY > 18);
}

updateHeader();
window.addEventListener("scroll", updateHeader, { passive: true });

function openCheckout(trigger) {
  if (CHECKOUT_URL.trim()) {
    window.location.assign(CHECKOUT_URL);
    return;
  }

  lastCheckoutTrigger = trigger;
  document.body.classList.add("dialog-open");

  if (typeof dialog?.showModal === "function") {
    dialog.showModal();
  } else if (dialog) {
    dialog.setAttribute("open", "");
  }
}

function closeCheckout() {
  if (!dialog) return;

  if (typeof dialog.close === "function" && dialog.open) {
    dialog.close();
  } else {
    dialog.removeAttribute("open");
    document.body.classList.remove("dialog-open");
    lastCheckoutTrigger?.focus();
  }
}

document.querySelectorAll("[data-checkout]").forEach((button) => {
  button.addEventListener("click", () => openCheckout(button));
});

document.querySelectorAll("[data-dialog-close]").forEach((button) => {
  button.addEventListener("click", closeCheckout);
});

dialog?.addEventListener("close", () => {
  document.body.classList.remove("dialog-open");
  lastCheckoutTrigger?.focus();
});

dialog?.addEventListener("click", (event) => {
  if (event.target === dialog) closeCheckout();
});

if (CHECKOUT_URL.trim()) {
  document.querySelectorAll("[data-checkout-status], .hero__microcopy").forEach((element) => {
    element.hidden = true;
  });
}

document.querySelectorAll("[data-topics]").forEach((topics) => {
  const tabs = [...topics.querySelectorAll('[role="tab"]')];
  const panels = [...topics.querySelectorAll('[role="tabpanel"]')];
  const counter = topics.querySelector("[data-topic-current]");

  topics.classList.add("is-enhanced");

  function selectTab(nextTab, moveFocus = false) {
    tabs.forEach((tab, index) => {
      const selected = tab === nextTab;
      const panel = panels.find((item) => item.id === tab.getAttribute("aria-controls"));

      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
      if (panel) panel.hidden = !selected;
      if (selected && counter) counter.textContent = String(index + 1).padStart(2, "0");
    });

    if (moveFocus) nextTab.focus();
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

document.querySelectorAll(".faq-list details").forEach((item) => {
  item.addEventListener("toggle", () => {
    if (!item.open) return;
    document.querySelectorAll(".faq-list details[open]").forEach((other) => {
      if (other !== item) other.removeAttribute("open");
    });
  });
});

const reveals = [...document.querySelectorAll(".reveal")];

if (prefersReducedMotion || !("IntersectionObserver" in window)) {
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
    { threshold: 0.12, rootMargin: "0px 0px -40px" },
  );

  reveals.forEach((element) => revealObserver.observe(element));
}

let scrollTicking = false;

function updateMobileBuy() {
  if (!hero || !offer || !mobileBuy) return;

  const isMobile = window.matchMedia("(max-width: 640px)").matches;
  const heroPassed = hero.getBoundingClientRect().bottom < 100;
  const offerVisible = offer.getBoundingClientRect().top < window.innerHeight * 0.84;
  mobileBuy.hidden = !(isMobile && heroPassed && !offerVisible);
  scrollTicking = false;
}

function requestMobileBuyUpdate() {
  if (scrollTicking) return;
  scrollTicking = true;
  window.requestAnimationFrame(updateMobileBuy);
}

updateMobileBuy();
window.addEventListener("scroll", requestMobileBuyUpdate, { passive: true });
window.addEventListener("resize", requestMobileBuyUpdate);
