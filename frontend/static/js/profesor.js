/**
 * profesor.js — Lógica compartida de las vistas de PROFESOR
 * Requiere: api.js, utils.js
 */

import api from './api.js';
import { toast, initSidebar } from './utils.js';

// Marcar nav-item activo según la URL
export function highlightNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(a => {
    a.classList.toggle('active', a.getAttribute('href') === path);
  });
}

// Renderizar lista de cursos del profesor en el sidebar o dashboard
export async function loadMyCourses(email) {
  const all = await api.list('Course');
  return all.results.filter(c => c.profesor_email === email);
}

// Helper: cargar alumnos de un curso
export async function loadStudents(cursoId) {
  const res = await api.filter('Student', { curso_id: cursoId });
  return res.results;
}

// Helper: cargar equipos de un curso
export async function loadTeams(cursoId) {
  const res = await api.filter('Team', { curso_id: cursoId });
  return res.results;
}

// Helper: cargar evaluaciones de un curso
export async function loadEvaluations(cursoId) {
  const res = await api.filter('Evaluation', { curso_id: cursoId });
  return res.results;
}

// Helper: cargar notas de un curso + evaluacion
export async function loadGrades(cursoId, evalId = null) {
  const filter = evalId
    ? { curso_id: cursoId, evaluacion_id: evalId }
    : { curso_id: cursoId };
  const res = await api.filter('Grade', filter);
  return res.results;
}

// Inicializar
export function initProfesor() {
  initSidebar();
  highlightNav();
}