/**
 * Helpers para comunicarse con la API REST del backend Zimbra CRM.
 * Sin frameworks — solo fetch nativo del navegador.
 */

const API_BASE = '/api';

async function apiRequest(method, path, body = null) {
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json' },
    };
    if (body !== null) {
        opts.body = JSON.stringify(body);
    }
    const res = await fetch(`${API_BASE}${path}`, opts);
    if (!res.ok) {
        let detail = `HTTP ${res.status}`;
        try {
            const err = await res.json();
            detail = err.detail || JSON.stringify(err);
        } catch { /* respuesta sin JSON */ }
        throw new Error(detail);
    }
    if (res.status === 204) return null;
    return res.json();
}

const API = {
    get:  (path)       => apiRequest('GET',    path),
    post: (path, body) => apiRequest('POST',   path, body),
    put:  (path, body) => apiRequest('PUT',    path, body),
    del:  (path)       => apiRequest('DELETE', path),
};

/* ----- Formatos para presentación ----- */
function formatMoney(n) {
    if (n === null || n === undefined || n === '') return '—';
    return '$' + Number(n).toLocaleString('es-CO', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }) + ' COP';
}

function formatDate(d) {
    if (!d) return '—';
    try { return new Date(d).toLocaleDateString('es-CO'); }
    catch { return String(d); }
}

function formatDateTime(d) {
    if (!d) return '—';
    try { return new Date(d).toLocaleString('es-CO'); }
    catch { return String(d); }
}

/* ----- Helpers de DOM seguros ----- */
function escapeHtml(s) {
    if (s === null || s === undefined) return '';
    return String(s)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;');
}

function showError(msg) {
    alert('Error: ' + msg);
}
