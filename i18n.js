/**
 * static/js/i18n.js — Språkhåndtering
 * Bytter mellom norsk og engelsk.
 * Legger til nye tekster her etter hvert.
 */

const translations = {
  no: {
    logout:           "Logg ut",
    tab_mix:          "Fargemiksing",
    tab_harmony:      "Fargeharmoni",
    tab_app3:         "App 3",          // TODO: Oppdater navn
    tab_app4:         "App 4",          // TODO: Oppdater navn
    chat_title:       "Malerkompis",
    chat_placeholder: "Spør om farger...",
    chat_send:        "Send",
  },
  en: {
    logout:           "Log out",
    tab_mix:          "Color Mixing",
    tab_harmony:      "Color Harmony",
    tab_app3:         "App 3",          // TODO: Oppdater navn
    tab_app4:         "App 4",          // TODO: Oppdater navn
    chat_title:       "Paintbuddy",
    chat_placeholder: "Ask about colors...",
    chat_send:        "Send",
  }
};

let currentLang = localStorage.getItem("lang") || "no";

function setLang(lang) {
  currentLang = lang;
  localStorage.setItem("lang", lang);
  applyTranslations();
  updateLangButtons();
}

function applyTranslations() {
  const t = translations[currentLang];

  // Tekst-elementer
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.dataset.i18n;
    if (t[key]) el.textContent = t[key];
  });

  // Placeholder-tekster
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.dataset.i18nPlaceholder;
    if (t[key]) el.placeholder = t[key];
  });
}

function updateLangButtons() {
  document.getElementById("btn-no")?.classList.toggle("active", currentLang === "no");
  document.getElementById("btn-en")?.classList.toggle("active", currentLang === "en");
}

// Kjør ved sideload
document.addEventListener("DOMContentLoaded", () => {
  applyTranslations();
  updateLangButtons();
});
