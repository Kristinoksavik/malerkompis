/**
 * static/js/tabs.js — Fanenavigasjon
 * Viser og skjuler fanepaneler.
 */

function showTab(tabId) {
  // Skjul alle paneler
  document.querySelectorAll(".tab-panel").forEach(panel => {
    panel.classList.remove("active");
  });

  // Fjern aktiv-klasse fra alle knapper
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.classList.remove("active");
  });

  // Vis valgt panel
  const panel = document.getElementById("tab-" + tabId);
  if (panel) panel.classList.add("active");

  // Merk aktiv knapp
  const btn = document.querySelector(`[onclick="showTab('${tabId}')"]`);
  if (btn) btn.classList.add("active");

  // Lagre valgt fane i sessionStorage
  sessionStorage.setItem("activeTab", tabId);
}

// Gjenopprett sist brukte fane ved sideload
document.addEventListener("DOMContentLoaded", () => {
  const saved = sessionStorage.getItem("activeTab");
  if (saved) showTab(saved);
});
