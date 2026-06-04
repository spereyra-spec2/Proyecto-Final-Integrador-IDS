/**
 * alumno.js — Lógica para las vistas PÚBLICAS de alumnos
 * No requiere autenticación.
 */

import api from './api.js';
import { toast, average, formatDate } from './utils.js';

/**
 * Buscar datos de un alumno por padrón y curso
 * Devuelve { student, grades, evaluations, team, attendances }
 */
export async function buscarAlumno(cursoId, padron) {
  const [studentsRes, gradesRes, evalsRes, teamsRes, attRes] = await Promise.all([
    api.filter('Student', { curso_id: cursoId, padron }),
    api.filter('Grade',   { curso_id: cursoId, padron }),
    api.filter('Evaluation', { curso_id: cursoId }),
    api.filter('Team', { curso_id: cursoId }),
    api.filter('Attendance', { curso_id: cursoId, padron }),
  ]);

  const student     = studentsRes.results[0] || null;
  const grades      = gradesRes.results;
  const evaluations = evalsRes.results;
  const attendances = attRes.results;
  const team        = teamsRes.results.find(t => (t.integrantes || []).includes(padron)) || null;

  return { student, grades, evaluations, team, attendances };
}

/**
 * Calcular estado académico del alumno
 */
export function calcularEstado(grades) {
  if (!grades.length) return { label: 'Sin notas', cls: 'badge-neutral' };
  const avg = parseFloat(average(grades.map(g => g.nota)));
  if (avg >= 7) return { label: 'Regular ⭐', cls: 'badge-success' };
  if (avg >= 4) return { label: 'Regular', cls: 'badge-info' };
  return { label: 'En riesgo', cls: 'badge-danger' };
}

/**
 * Unirse a equipo por código de acceso
 */
export async function unirseEquipo(cursoId, padron, codigoAcceso, studentId) {
  const res = await api.filter('Team', { curso_id: cursoId });
  const team = res.results.find(t => t.codigo_acceso === codigoAcceso);
  if (!team) throw new Error('Código inválido');
  const integrantes = team.integrantes || [];
  if (integrantes.includes(padron)) throw new Error('Ya estás en este equipo');
  if (integrantes.length >= (team.cupo_maximo || 5)) throw new Error('El equipo está lleno');
  await api.update('Team', team.id, { integrantes: [...integrantes, padron] });
  if (studentId) await api.update('Student', studentId, { equipo_id: team.id });
  return team;
}

/**
 * Abandonar equipo
 */
export async function abandonarEquipo(team, padron, studentId) {
  const integrantes = (team.integrantes || []).filter(p => p !== padron);
  if (integrantes.length === 0) {
    await api.delete('Team', team.id);
  } else {
    await api.update('Team', team.id, { integrantes });
  }
  if (studentId) await api.update('Student', studentId, { equipo_id: '' });
}

/**
 * Darse de baja del curso
 */
export async function bajaCurso(studentId) {
  await api.update('Student', studentId, { estado: 'abandono' });
}