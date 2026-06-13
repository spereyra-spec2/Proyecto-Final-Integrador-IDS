/**
 * utils.js — Funciones de utilidad compartidas por todas las páginas
 */

/** Mostrar toast notification */
export function toast(msg, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

/** Abrir / cerrar modal */
export function openModal(id) {
  document.getElementById(id)?.classList.remove('hidden');
}
export function closeModal(id) {
  document.getElementById(id)?.classList.add('hidden');
}

/** Formatear fecha yyyy-mm-dd → dd/mm/yyyy */
export function formatDate(str) {
  if (!str) return '-';
  const [y, m, d] = str.split('-');
  return `${d}/${m}/${y}`;
}

/** Generar código aleatorio de 6 caracteres */
export function randomCode() {
  return Math.random().toString(36).substring(2, 8).toUpperCase();
}

/** Promedio de un array de notas */
export function average(notes) {
  if (!notes.length) return null;
  return (notes.reduce((s, n) => s + n, 0) / notes.length).toFixed(1);
}

/** Obtener inicial de un nombre */
export function initial(name = '') {
  return name.charAt(0).toUpperCase();
}

/** Sidebar mobile toggle */
export function initSidebar() {
  const sidebar  = document.querySelector('.sidebar');
  const overlay  = document.querySelector('.sidebar-overlay');
  const hamburger = document.querySelector('.hamburger');
  if (!hamburger) return;

  hamburger.addEventListener('click', () => {
    sidebar?.classList.toggle('open');
    overlay?.classList.toggle('open');
  });
  overlay?.addEventListener('click', () => {
    sidebar?.classList.remove('open');
    overlay?.classList.remove('open');
  });
}


//-------------------------------------------------------------------------------------------------------

// utils.js — Funciones de utilidad estéticas compartidas globalmente

//Mostrar notificaciones flotantes (Toast) 
window.toast = function(msg, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

//Abrir modales manipulando la clase de components.css 
window.openModal = function(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove('hidden');
}

//Cerrar modales 
window.closeModal = function(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add('hidden');
}

//Formatear fecha yyyy-mm-dd → dd/mm/yyyy
window.formatDate = function(str) {
  if (!str) return '-';
  const partes = str.split('T')[0].split('-');
  if (partes.length !== 3) return str;
  return `${partes[2]}/${partes[1]}/${partes[0]}`;
}

// Generar código aleatorio de 6 caracteres
window.randomCode = function() {
  return Math.random().toString(36).substring(2, 8).toUpperCase();
}

// Promedio de un array de notas
window.average = function(notes) {
  if (!notes || !notes.length) return null;
  return (notes.reduce((s, n) => s + n, 0) / notes.length).toFixed(1);
}

// Obtener inicial de un nombre
window.initial = function(name = '') {
  return name.charAt(0).toUpperCase();
}

// Sidebar mobile toggle adaptado a tu layout.css
window.initSidebar = function() {
  const sidebar  = document.querySelector('.sidebar');
  const overlay  = document.querySelector('.sidebar-overlay');
  const hamburger = document.querySelector('.hamburger');
  if (!hamburger) return;

  hamburger.addEventListener('click', () => {
    sidebar?.classList.toggle('open');
    overlay?.classList.toggle('open');
  });
  overlay?.addEventListener('click', () => {
    sidebar?.classList.remove('open');
    overlay?.classList.remove('open');
  });
}

document.addEventListener("DOMContentLoaded", function() {
  window.initSidebar();
});

// ===== AGREGADOS DE ACCESIBILIDAD PARA JINJA =====
window.openModal = window.openModal || openModal;
window.closeModal = window.closeModal || closeModal;
