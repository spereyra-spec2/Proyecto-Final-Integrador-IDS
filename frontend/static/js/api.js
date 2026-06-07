/**
 * api.js — Cliente HTTP para consumir la base de datos de Base44
 * Todas las páginas HTML usan este módulo para leer/escribir datos.
 */

const APP_ID = window.__APP_ID__ || '';
const TOKEN  = window.__TOKEN__  || '';

const BASE_URL = `/api/apps/entities/${APP_ID}/prod`;

async function request(method, path, body = null) {
  const opts = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'X-App-Id': APP_ID,
      ...(TOKEN ? { 'Authorization': `Bearer ${TOKEN}` } : {})
    }
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(BASE_URL + path, opts);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

// Helpers genéricos
const api = {
  list:   (entity, sort = '-created_date', limit = 200) =>
    request('GET', `/${entity}/?sort=${sort}&limit=${limit}`),

  filter: (entity, filters = {}, sort = '-created_date') => {
    const q = encodeURIComponent(JSON.stringify(filters));
    return request('GET', `/${entity}/?filter=${q}&sort=${sort}&limit=200`);
  },

  get:    (entity, id) => request('GET', `/${entity}/${id}/`),
  create: (entity, data) => request('POST', `/${entity}/`, data),
  update: (entity, id, data) => request('PATCH', `/${entity}/${id}/`, data),
  delete: (entity, id) => request('DELETE', `/${entity}/${id}/`),
};

export default api;