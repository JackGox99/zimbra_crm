/**
 * Explorador de datos — vista tabular de las 9 tablas del CRM.
 *
 * Cada entrada en TABLAS declara:
 *   - key:    identificador interno + clave para el chip activo.
 *   - label:  nombre humano (lo que el usuario ve).
 *   - icon:   emoji para el chip.
 *   - endpoint: ruta del backend que devuelve la lista.
 *   - cols:   columnas a renderizar [{ key, label, format? }].
 *
 * El render es genérico: una sola función que recibe la definición y
 * los datos. Esto evita repetir tablas y mantiene la página corta.
 */

const TABLAS = [
    {
        key: 'campanas',
        label: 'Campañas',
        icon: '📣',
        endpoint: '/campanas/?limit=500',
        cols: [
            { key: 'id_campana',   label: 'ID' },
            { key: 'nombre',       label: 'Nombre' },
            { key: 'tipo',         label: 'Tipo' },
            { key: 'canal',        label: 'Canal' },
            { key: 'fecha_inicio', label: 'Inicio',     format: formatDate },
            { key: 'fecha_fin',    label: 'Fin',        format: formatDate },
            { key: 'presupuesto',  label: 'Presupuesto', format: formatMoney },
            { key: 'estado',       label: 'Estado',     format: badgeFmt },
        ],
    },
    {
        key: 'prospectos',
        label: 'Prospectos',
        icon: '👤',
        endpoint: '/prospectos/?limit=500',
        cols: [
            { key: 'id_prospecto',     label: 'ID' },
            { key: 'nombre',           label: 'Nombre' },
            { key: 'correo',           label: 'Correo' },
            { key: 'empresa',          label: 'Empresa' },
            { key: 'telefono',         label: 'Teléfono' },
            { key: 'puntuacion',       label: 'Score' },
            { key: 'estado',           label: 'Estado', format: badgeFmt },
            { key: 'fecha_registro',   label: 'Registro',     format: formatDate },
            { key: 'fecha_fin_prueba', label: 'Fin trial',    format: formatDate },
            { key: 'id_campana_origen',label: 'ID Campaña' },
        ],
    },
    {
        key: 'interacciones',
        label: 'Interacciones marketing',
        icon: '📊',
        endpoint: '/interacciones/?limit=500',
        cols: [
            { key: 'id_interaccion',   label: 'ID' },
            { key: 'id_prospecto',     label: 'ID Prospecto' },
            { key: 'id_campana',       label: 'ID Campaña' },
            { key: 'accion',           label: 'Acción' },
            { key: 'peso_scoring',     label: 'Peso' },
            { key: 'fecha_interaccion',label: 'Fecha',       format: formatDateTime },
        ],
    },
    {
        key: 'plantillas',
        label: 'Plantillas comunicación',
        icon: '📝',
        endpoint: '/plantillas/?limit=500',
        cols: [
            { key: 'id_plantilla',  label: 'ID' },
            { key: 'nombre',        label: 'Nombre' },
            { key: 'asunto',        label: 'Asunto' },
            { key: 'tipo',          label: 'Tipo' },
            { key: 'fecha_creacion',label: 'Creada',  format: formatDate },
            { key: 'activa',        label: 'Activa',  format: boolFmt },
        ],
    },
    {
        key: 'comunicaciones',
        label: 'Comunicaciones enviadas',
        icon: '✉️',
        endpoint: '/comunicaciones/?limit=500',
        cols: [
            { key: 'id_comunicacion', label: 'ID' },
            { key: 'id_prospecto',    label: 'Prospecto' },
            { key: 'id_plantilla',    label: 'Plantilla' },
            { key: 'id_campana',      label: 'Campaña' },
            { key: 'estado_envio',    label: 'Estado',  format: badgeFmt },
            { key: 'fecha_envio',     label: 'Enviado', format: formatDateTime },
        ],
    },
    {
        key: 'propuestas',
        label: 'Propuestas',
        icon: '📋',
        endpoint: '/propuestas/?limit=500',
        cols: [
            { key: 'id_propuesta',   label: 'ID' },
            { key: 'id_prospecto',   label: 'ID Prospecto' },
            { key: 'descripcion',    label: 'Descripción', expand: true },
            { key: 'valor_estimado', label: 'Valor',    format: formatMoney },
            { key: 'estado',         label: 'Estado',   format: badgeFmt },
            { key: 'fecha_propuesta',label: 'Fecha',    format: formatDate },
        ],
    },
    {
        key: 'clientes',
        label: 'Clientes',
        icon: '🤝',
        endpoint: '/clientes/?limit=500',
        cols: [
            { key: 'id_cliente',       label: 'ID' },
            { key: 'nombre',           label: 'Nombre' },
            { key: 'correo',           label: 'Correo' },
            { key: 'empresa',          label: 'Empresa' },
            { key: 'telefono',         label: 'Teléfono' },
            { key: 'fecha_registro',   label: 'Registro',     format: formatDate },
            { key: 'id_prospecto',     label: 'ID Prospecto' },
            { key: 'sync_salesforce',  label: 'SF Sync',     format: boolFmt },
            { key: 'fecha_ult_sync',   label: 'Última sync', format: formatDateTime },
        ],
    },
    {
        key: 'ventas',
        label: 'Ventas',
        icon: '💰',
        endpoint: '/ventas/?limit=500',
        cols: [
            { key: 'id_venta',    label: 'ID' },
            { key: 'id_propuesta',label: 'ID Propuesta' },
            { key: 'id_cliente',  label: 'ID Cliente' },
            { key: 'monto',       label: 'Monto',  format: formatMoney },
            { key: 'estado',      label: 'Estado', format: badgeFmt },
            { key: 'metodo_pago', label: 'Pago' },
            { key: 'fecha_venta', label: 'Fecha',  format: formatDate },
        ],
    },
    {
        key: 'reportes',
        label: 'Reportes',
        icon: '📈',
        endpoint: '/reportes/?limit=500',
        cols: [
            { key: 'id_reporte',       label: 'ID' },
            { key: 'tipo_reporte',     label: 'Tipo' },
            { key: 'resultado',        label: 'Resultado', expand: true, format: resultadoFmt },
            { key: 'periodo_inicio',   label: 'Periodo desde', format: formatDate },
            { key: 'periodo_fin',      label: 'Periodo hasta', format: formatDate },
            { key: 'fecha_generacion', label: 'Generado',  format: formatDateTime },
            { key: 'id_campana',       label: 'Campaña' },
        ],
    },
];

// ----- Formatters específicos del explorador -----
function badgeFmt(v) {
    if (v === null || v === undefined || v === '') return '—';
    const cls = String(v).toLowerCase();
    return `<span class="badge ${cls}">${escapeHtml(v)}</span>`;
}

function boolFmt(v) {
    if (v === null || v === undefined) return '—';
    return v
        ? '<span class="badge calificado">Sí</span>'
        : '<span class="badge pendiente">No</span>';
}

function resultadoFmt(v) {
    if (!v) return '—';
    // Si el campo trae JSON (lo poblado por trg_audit_estado_prospecto),
    // lo mostramos como código compacto en lugar del texto crudo.
    try {
        const parsed = JSON.parse(v);
        return `<span class="json-cell">${escapeHtml(JSON.stringify(parsed))}</span>`;
    } catch {
        return escapeHtml(v);
    }
}

// ----- Estado -----
let tablaActiva = TABLAS[0];
let datosActivos = [];
let busqueda = '';

function renderTabs() {
    document.getElementById('tabs').innerHTML = TABLAS.map(t => `
        <div class="chip ${t.key === tablaActiva.key ? 'active' : ''}"
             data-key="${t.key}">${t.icon} ${escapeHtml(t.label)}</div>
    `).join('');
    document.querySelectorAll('#tabs .chip').forEach(c => {
        c.addEventListener('click', () => seleccionar(c.dataset.key));
    });
}

async function seleccionar(key) {
    const t = TABLAS.find(x => x.key === key);
    if (!t) return;
    tablaActiva = t;
    busqueda = '';
    document.getElementById('search').value = '';
    renderTabs();
    document.getElementById('tbody').innerHTML =
        `<tr><td class="muted text-center" colspan="${t.cols.length}">Cargando…</td></tr>`;
    try {
        datosActivos = await API.get(t.endpoint);
        renderTabla();
    } catch (e) {
        document.getElementById('tbody').innerHTML =
            `<tr><td class="error-text text-center" colspan="${t.cols.length}">Error: ${escapeHtml(e.message)}</td></tr>`;
    }
}

function renderTabla() {
    const cols = tablaActiva.cols;
    document.getElementById('thead').innerHTML = `
        <tr>${cols.map(c => `<th>${escapeHtml(c.label)}</th>`).join('')}</tr>
    `;

    let filas = datosActivos;
    if (busqueda) {
        const q = busqueda.toLowerCase();
        filas = filas.filter(r =>
            cols.some(c => {
                const raw = r[c.key];
                return raw !== null && raw !== undefined &&
                       String(raw).toLowerCase().includes(q);
            })
        );
    }

    document.getElementById('count').innerHTML =
        `<strong>${filas.length}</strong> de ${datosActivos.length} registros`;

    const tbody = document.getElementById('tbody');
    if (!filas.length) {
        tbody.innerHTML =
            `<tr><td class="muted text-center" colspan="${cols.length}">Sin registros que coincidan.</td></tr>`;
        return;
    }

    tbody.innerHTML = filas.map(r => `
        <tr>
            ${cols.map(c => {
                const raw = r[c.key];
                let html;
                if (raw === null || raw === undefined || raw === '') {
                    html = '<span class="muted">—</span>';
                } else if (c.format) {
                    html = c.format(raw);
                } else {
                    html = escapeHtml(raw);
                }
                return `<td${c.expand ? ' class="expand"' : ''}>${html}</td>`;
            }).join('')}
        </tr>
    `).join('');
}

// ----- Bindings -----
document.getElementById('search').addEventListener('input', (e) => {
    busqueda = e.target.value.trim();
    renderTabla();
});

renderTabs();
seleccionar(tablaActiva.key);