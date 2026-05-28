/**
 * Explorador de datos con CRUD completo sobre las 9 tablas del CRM.
 *
 * Cada entrada en TABLAS declara:
 *   - key, label, icon, path, pk, displayCol
 *   - cols:   columnas a renderizar en la tabla
 *   - fields: schema declarativo del formulario de Crear/Editar
 *
 * El render de la tabla, el formulario, los combos FK y los handlers
 * de POST/PUT/DELETE son genéricos: viven en este archivo y reutilizan
 * el mismo modal para todas las tablas.
 */

// ---------------------------------------------------------------------
//  HELPER FK — etiqueta legible "ID — nombre" para los combos
// ---------------------------------------------------------------------
function fkLabel(tabla, row) {
    const id = row[tabla.pk];
    const display = tabla.displayCol ? row[tabla.displayCol] : null;
    if (display === null || display === undefined || display === '') return String(id);
    const corto = String(display).length > 60
        ? String(display).slice(0, 57) + '…'
        : display;
    return `${id} — ${corto}`;
}

// ---------------------------------------------------------------------
//  CATÁLOGO DE TABLAS
// ---------------------------------------------------------------------
const TABLAS = [
    {
        key: 'campanas',
        label: 'Campañas',
        icon: '📣',
        path: '/campanas',
        pk: 'id_campana',
        displayCol: 'nombre',
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
        fields: [
            { key: 'nombre',       label: 'Nombre',       type: 'text',    required: true,  maxLength: 100 },
            { key: 'tipo',         label: 'Tipo',         type: 'text',    required: true,  maxLength: 50 },
            { key: 'canal',        label: 'Canal',        type: 'text',    required: true,  maxLength: 50 },
            { key: 'fecha_inicio', label: 'Fecha inicio', type: 'date',    required: true },
            { key: 'fecha_fin',    label: 'Fecha fin',    type: 'date',    required: true },
            { key: 'presupuesto',  label: 'Presupuesto',  type: 'decimal', min: 0 },
            { key: 'estado',       label: 'Estado',       type: 'select',  required: true,
              options: ['Planeada', 'Activa', 'Finalizada', 'Cancelada'] },
        ],
    },
    {
        key: 'prospectos',
        label: 'Prospectos',
        icon: '👤',
        path: '/prospectos',
        pk: 'id_prospecto',
        displayCol: 'nombre',
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
        fields: [
            { key: 'nombre',              label: 'Nombre',         type: 'text',  required: true, maxLength: 100 },
            { key: 'correo',              label: 'Correo',         type: 'email', required: true },
            { key: 'empresa',             label: 'Empresa',        type: 'text',  maxLength: 100 },
            { key: 'telefono',            label: 'Teléfono',       type: 'text',  maxLength: 20 },
            { key: 'puntuacion',          label: 'Puntuación',     type: 'int',   min: 0, defaultValue: 0 },
            { key: 'estado',              label: 'Estado',         type: 'select', required: true,
              options: ['Pendiente', 'Contactado', 'Calificado', 'Inadecuado', 'Convertido'] },
            { key: 'fecha_registro',      label: 'Fecha registro', type: 'date',  required: true },
            { key: 'fecha_inicio_prueba', label: 'Inicio trial',   type: 'date' },
            { key: 'fecha_fin_prueba',    label: 'Fin trial',      type: 'date' },
            { key: 'id_campana_origen',   label: 'Campaña origen', type: 'fk',    to: 'campanas' },
        ],
    },
    {
        key: 'interacciones',
        label: 'Interacciones marketing',
        icon: '📊',
        path: '/interacciones',
        pk: 'id_interaccion',
        displayCol: 'accion',
        cols: [
            { key: 'id_interaccion',   label: 'ID' },
            { key: 'id_prospecto',     label: 'ID Prospecto' },
            { key: 'id_campana',       label: 'ID Campaña' },
            { key: 'accion',           label: 'Acción' },
            { key: 'peso_scoring',     label: 'Peso' },
            { key: 'fecha_interaccion',label: 'Fecha',       format: formatDateTime },
        ],
        fields: [
            { key: 'accion',            label: 'Acción',           type: 'text',     required: true, maxLength: 80 },
            { key: 'fecha_interaccion', label: 'Fecha interacción',type: 'datetime', required: true },
            { key: 'peso_scoring',      label: 'Peso scoring',     type: 'int',      required: true, min: 0 },
            { key: 'id_prospecto',      label: 'Prospecto',        type: 'fk',       required: true, to: 'prospectos' },
            { key: 'id_campana',        label: 'Campaña',          type: 'fk',       required: true, to: 'campanas' },
        ],
    },
    {
        key: 'plantillas',
        label: 'Plantillas comunicación',
        icon: '📝',
        path: '/plantillas',
        pk: 'id_plantilla',
        displayCol: 'nombre',
        cols: [
            { key: 'id_plantilla',  label: 'ID' },
            { key: 'nombre',        label: 'Nombre' },
            { key: 'asunto',        label: 'Asunto' },
            { key: 'tipo',          label: 'Tipo' },
            { key: 'fecha_creacion',label: 'Creada',  format: formatDate },
            { key: 'activa',        label: 'Activa',  format: boolFmt },
        ],
        fields: [
            { key: 'nombre',         label: 'Nombre',  type: 'text',     required: true, maxLength: 100 },
            { key: 'asunto',         label: 'Asunto',  type: 'text',     required: true, maxLength: 150 },
            { key: 'cuerpo',         label: 'Cuerpo',  type: 'textarea', required: true },
            { key: 'tipo',           label: 'Tipo',    type: 'select',   required: true,
              options: ['Email', 'SMS', 'Notificacion'] },
            { key: 'fecha_creacion', label: 'Fecha creación', type: 'date', required: true },
            { key: 'activa',         label: 'Activa', type: 'bool',     required: true, defaultValue: true },
        ],
    },
    {
        key: 'comunicaciones',
        label: 'Comunicaciones enviadas',
        icon: '✉️',
        path: '/comunicaciones',
        pk: 'id_comunicacion',
        displayCol: 'estado_envio',
        cols: [
            { key: 'id_comunicacion', label: 'ID' },
            { key: 'id_prospecto',    label: 'Prospecto' },
            { key: 'id_plantilla',    label: 'Plantilla' },
            { key: 'id_campana',      label: 'Campaña' },
            { key: 'estado_envio',    label: 'Estado',  format: badgeFmt },
            { key: 'fecha_envio',     label: 'Enviado', format: formatDateTime },
        ],
        fields: [
            { key: 'fecha_envio',  label: 'Fecha envío', type: 'datetime', required: true },
            { key: 'estado_envio', label: 'Estado',      type: 'select',   required: true,
              options: ['Enviado', 'Fallido', 'Rebotado', 'Abierto'] },
            { key: 'id_plantilla', label: 'Plantilla',   type: 'fk',       required: true, to: 'plantillas' },
            { key: 'id_prospecto', label: 'Prospecto',   type: 'fk',       required: true, to: 'prospectos' },
            { key: 'id_campana',   label: 'Campaña',     type: 'fk',       to: 'campanas' },
        ],
    },
    {
        key: 'propuestas',
        label: 'Propuestas',
        icon: '📋',
        path: '/propuestas',
        pk: 'id_propuesta',
        displayCol: 'descripcion',
        cols: [
            { key: 'id_propuesta',   label: 'ID' },
            { key: 'id_prospecto',   label: 'ID Prospecto' },
            { key: 'descripcion',    label: 'Descripción', expand: true },
            { key: 'valor_estimado', label: 'Valor',    format: formatMoney },
            { key: 'estado',         label: 'Estado',   format: badgeFmt },
            { key: 'fecha_propuesta',label: 'Fecha',    format: formatDate },
        ],
        fields: [
            { key: 'descripcion',     label: 'Descripción',     type: 'textarea', required: true },
            { key: 'fecha_propuesta', label: 'Fecha propuesta', type: 'date',     required: true },
            { key: 'estado',          label: 'Estado',          type: 'select',   required: true,
              options: ['Pendiente', 'Aceptada', 'Rechazada', 'Vencida'] },
            { key: 'valor_estimado',  label: 'Valor estimado',  type: 'decimal',  required: true, min: 0 },
            { key: 'id_prospecto',    label: 'Prospecto',       type: 'fk',       required: true, to: 'prospectos' },
        ],
    },
    {
        key: 'clientes',
        label: 'Clientes',
        icon: '🤝',
        path: '/clientes',
        pk: 'id_cliente',
        displayCol: 'nombre',
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
        fields: [
            { key: 'nombre',          label: 'Nombre',          type: 'text',     required: true, maxLength: 100 },
            { key: 'correo',          label: 'Correo',          type: 'email',    required: true },
            { key: 'empresa',         label: 'Empresa',         type: 'text',     maxLength: 100 },
            { key: 'telefono',        label: 'Teléfono',        type: 'text',     maxLength: 20 },
            { key: 'fecha_registro',  label: 'Fecha registro',  type: 'date',     required: true },
            { key: 'id_prospecto',    label: 'Prospecto origen',type: 'fk',       to: 'prospectos' },
            { key: 'sync_salesforce', label: 'Sync Salesforce', type: 'bool',     required: true, defaultValue: false },
            { key: 'fecha_ult_sync',  label: 'Última sync',     type: 'datetime' },
        ],
    },
    {
        key: 'ventas',
        label: 'Ventas',
        icon: '💰',
        path: '/ventas',
        pk: 'id_venta',
        displayCol: 'id_venta',
        cols: [
            { key: 'id_venta',    label: 'ID' },
            { key: 'id_propuesta',label: 'ID Propuesta' },
            { key: 'id_cliente',  label: 'ID Cliente' },
            { key: 'monto',       label: 'Monto',  format: formatMoney },
            { key: 'estado',      label: 'Estado', format: badgeFmt },
            { key: 'metodo_pago', label: 'Pago' },
            { key: 'fecha_venta', label: 'Fecha',  format: formatDate },
        ],
        fields: [
            { key: 'fecha_venta',  label: 'Fecha venta', type: 'date',    required: true },
            { key: 'monto',        label: 'Monto',       type: 'decimal', required: true, min: 0.01 },
            { key: 'estado',       label: 'Estado',      type: 'select',  required: true,
              options: ['Pagada', 'Pendiente', 'Anulada'] },
            { key: 'metodo_pago',  label: 'Método pago', type: 'text',    maxLength: 40 },
            { key: 'id_propuesta', label: 'Propuesta',   type: 'fk',      required: true, to: 'propuestas' },
            { key: 'id_cliente',   label: 'Cliente',     type: 'fk',      required: true, to: 'clientes' },
        ],
    },
    {
        key: 'reportes',
        label: 'Reportes',
        icon: '📈',
        path: '/reportes',
        pk: 'id_reporte',
        displayCol: 'tipo_reporte',
        cols: [
            { key: 'id_reporte',       label: 'ID' },
            { key: 'tipo_reporte',     label: 'Tipo' },
            { key: 'resultado',        label: 'Resultado', expand: true, format: resultadoFmt },
            { key: 'periodo_inicio',   label: 'Periodo desde', format: formatDate },
            { key: 'periodo_fin',      label: 'Periodo hasta', format: formatDate },
            { key: 'fecha_generacion', label: 'Generado',  format: formatDateTime },
            { key: 'id_campana',       label: 'Campaña' },
        ],
        fields: [
            { key: 'tipo_reporte',     label: 'Tipo reporte',  type: 'text',     required: true, maxLength: 60 },
            { key: 'fecha_generacion', label: 'Fecha generación', type: 'datetime', required: true },
            { key: 'periodo_inicio',   label: 'Periodo desde', type: 'date' },
            { key: 'periodo_fin',      label: 'Periodo hasta', type: 'date' },
            { key: 'resultado',        label: 'Resultado',     type: 'textarea' },
            { key: 'id_campana',       label: 'Campaña',       type: 'fk',       to: 'campanas' },
        ],
    },
];

const TABLAS_BY_KEY = Object.fromEntries(TABLAS.map(t => [t.key, t]));

// ---------------------------------------------------------------------
//  FORMATTERS DE TABLA
// ---------------------------------------------------------------------
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
    try {
        const parsed = JSON.parse(v);
        return `<span class="json-cell">${escapeHtml(JSON.stringify(parsed))}</span>`;
    } catch {
        return escapeHtml(v);
    }
}

// ---------------------------------------------------------------------
//  CACHE DE FK (carga perezosa de cada tabla padre)
// ---------------------------------------------------------------------
const fkCache = {};   // { 'campanas': [ {id_campana, nombre, ...}, ... ] }

async function loadFkOptions(tableKey) {
    if (fkCache[tableKey]) return fkCache[tableKey];
    const t = TABLAS_BY_KEY[tableKey];
    if (!t) throw new Error(`Tabla FK desconocida: ${tableKey}`);
    fkCache[tableKey] = await API.get(`${t.path}/?limit=500`);
    return fkCache[tableKey];
}

function invalidateFkCache(tableKey) {
    delete fkCache[tableKey];
}

// ---------------------------------------------------------------------
//  ESTADO
// ---------------------------------------------------------------------
let tablaActiva = TABLAS[0];
let datosActivos = [];
let busqueda = '';

// ---------------------------------------------------------------------
//  RENDER DE TABS Y TABLA
// ---------------------------------------------------------------------
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
    const t = TABLAS_BY_KEY[key];
    if (!t) return;
    tablaActiva = t;
    busqueda = '';
    document.getElementById('search').value = '';
    document.getElementById('btn-crear').textContent = `➕ Crear ${t.label.toLowerCase()}`;
    renderTabs();
    document.getElementById('tbody').innerHTML =
        `<tr><td class="muted text-center" colspan="${t.cols.length + 1}">Cargando…</td></tr>`;
    await recargar();
}

async function recargar() {
    const t = tablaActiva;
    try {
        datosActivos = await API.get(`${t.path}/?limit=500`);
        invalidateFkCache(t.key);  // si esta tabla es referenciada como FK, fuerza recarga
        renderTabla();
    } catch (e) {
        document.getElementById('tbody').innerHTML =
            `<tr><td class="error-text text-center" colspan="${t.cols.length + 1}">Error: ${escapeHtml(e.message)}</td></tr>`;
    }
}

function renderTabla() {
    const cols = tablaActiva.cols;
    const totalCols = cols.length + 1;  // +1 para columna de acciones

    document.getElementById('thead').innerHTML = `
        <tr>
            ${cols.map(c => `<th>${escapeHtml(c.label)}</th>`).join('')}
            <th>Acciones</th>
        </tr>
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
            `<tr><td class="muted text-center" colspan="${totalCols}">Sin registros que coincidan.</td></tr>`;
        return;
    }

    tbody.innerHTML = filas.map(r => {
        const idVal = r[tablaActiva.pk];
        return `
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
                <td class="row-actions">
                    <button class="btn-mini btn-edit"    data-id="${idVal}" title="Editar">✏️</button>
                    <button class="btn-mini btn-delete"  data-id="${idVal}" title="Eliminar">🗑️</button>
                </td>
            </tr>
        `;
    }).join('');

    // Bind acciones por fila
    tbody.querySelectorAll('.btn-edit').forEach(b => {
        b.addEventListener('click', () => abrirFormulario('editar', Number(b.dataset.id)));
    });
    tbody.querySelectorAll('.btn-delete').forEach(b => {
        b.addEventListener('click', () => eliminarRegistro(Number(b.dataset.id)));
    });
}

// ---------------------------------------------------------------------
//  MODAL DE FORMULARIO
// ---------------------------------------------------------------------
function cerrarModal() {
    document.getElementById('modal-form').classList.remove('open');
    document.getElementById('modal-body').innerHTML = '';
    document.getElementById('modal-resultado').innerHTML = '';
}

/**
 * Pinta el resultado de la operación en el modal, distinguiendo:
 *   - COMMIT  (verde)   — operación exitosa, transacción confirmada.
 *   - ROLLBACK (rojo)   — error de BD (FK, UNIQUE, CHECK, regla de negocio).
 *                         Status 4xx/5xx que NO sea 422.
 *   - VALIDACIÓN (rojo) — status 422 (Pydantic): no se llegó a tocar la BD,
 *                         no hay rollback técnicamente, solo entrada inválida.
 */
function mostrarResultadoModal(tipo, mensaje, extraHtml = '') {
    const el = document.getElementById('modal-resultado');
    if (tipo === 'commit') {
        el.innerHTML = `
            <div class="success-bg mt-1">
                <span class="tx-result-tag commit">COMMIT</span>
                <strong>${escapeHtml(mensaje)}</strong>
                ${extraHtml ? `<div class="mt-1" style="font-size: 0.9rem;">${extraHtml}</div>` : ''}
            </div>
        `;
    } else if (tipo === 'rollback') {
        el.innerHTML = `
            <div class="error-bg mt-1">
                <span class="tx-result-tag rollback">ROLLBACK</span>
                <strong>Transacción revertida — nada cambió en la BD.</strong>
                <div class="mt-1" style="font-size: 0.9rem;">
                    Motivo: ${escapeHtml(mensaje)}
                </div>
            </div>
        `;
    } else {
        // 'validacion' u otro
        el.innerHTML = `
            <div class="error-bg mt-1">
                <span class="tx-result-tag rollback">VALIDACIÓN</span>
                <strong>Datos inválidos — la solicitud no llegó a la base de datos.</strong>
                <div class="mt-1" style="font-size: 0.9rem;">
                    ${escapeHtml(mensaje)}
                </div>
            </div>
        `;
    }
}

function clasificarError(e) {
    // 422 = validación Pydantic → no hay rollback de BD
    if (e.status === 422) return 'validacion';
    // 400/409/500/etc → la transacción se inició y InnoDB hizo ROLLBACK
    if (e.status && e.status >= 400) return 'rollback';
    // sin status: error de red u otra cosa → trátalo como rollback (no quedó persistido)
    return 'rollback';
}

/**
 * Construye un <input>/<select>/<textarea> según el tipo del campo y
 * lo deja con el valor que tenga `row[field.key]`. Para campos FK
 * devuelve un placeholder y resuelve las opciones asíncronamente.
 */
function buildField(field, row) {
    const v = row ? row[field.key] : (field.defaultValue ?? null);
    const id = `f-${field.key}`;
    const req = field.required ? 'required' : '';

    let control;
    switch (field.type) {
        case 'text':
        case 'email': {
            const maxAttr = field.maxLength ? `maxlength="${field.maxLength}"` : '';
            const typ = field.type === 'email' ? 'email' : 'text';
            const val = v === null || v === undefined ? '' : escapeHtml(v);
            control = `<input type="${typ}" id="${id}" name="${field.key}" value="${val}" ${maxAttr} ${req}>`;
            break;
        }
        case 'textarea': {
            const val = v === null || v === undefined ? '' : escapeHtml(v);
            control = `<textarea id="${id}" name="${field.key}" rows="3" ${req}>${val}</textarea>`;
            break;
        }
        case 'int': {
            const minAttr = field.min !== undefined ? `min="${field.min}"` : '';
            const val = (v === null || v === undefined) ? '' : v;
            control = `<input type="number" step="1" id="${id}" name="${field.key}" value="${val}" ${minAttr} ${req}>`;
            break;
        }
        case 'decimal': {
            const minAttr = field.min !== undefined ? `min="${field.min}"` : '';
            const val = (v === null || v === undefined) ? '' : v;
            control = `<input type="number" step="0.01" id="${id}" name="${field.key}" value="${val}" ${minAttr} ${req}>`;
            break;
        }
        case 'date': {
            const val = v ? String(v).slice(0, 10) : '';
            control = `<input type="date" id="${id}" name="${field.key}" value="${val}" ${req}>`;
            break;
        }
        case 'datetime': {
            // datetime-local usa 'YYYY-MM-DDTHH:MM' sin zona ni segundos
            let val = '';
            if (v) {
                const d = new Date(v);
                if (!isNaN(d)) {
                    const pad = n => String(n).padStart(2, '0');
                    val = `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
                }
            }
            control = `<input type="datetime-local" id="${id}" name="${field.key}" value="${val}" ${req}>`;
            break;
        }
        case 'bool': {
            const cur = (v === null || v === undefined) ? '' : (v ? 'true' : 'false');
            control = `
                <select id="${id}" name="${field.key}" ${req}>
                    ${field.required ? '' : '<option value="">— vacío —</option>'}
                    <option value="true"  ${cur === 'true'  ? 'selected' : ''}>Sí</option>
                    <option value="false" ${cur === 'false' ? 'selected' : ''}>No</option>
                </select>`;
            break;
        }
        case 'select': {
            const cur = (v === null || v === undefined) ? '' : String(v);
            const opts = field.options.map(o =>
                `<option value="${escapeHtml(o)}" ${o === cur ? 'selected' : ''}>${escapeHtml(o)}</option>`
            ).join('');
            control = `
                <select id="${id}" name="${field.key}" ${req}>
                    ${field.required ? '' : '<option value="">— sin valor —</option>'}
                    ${opts}
                </select>`;
            break;
        }
        case 'fk': {
            // Las opciones se cargan asíncronamente tras montar el DOM.
            control = `
                <select id="${id}" name="${field.key}" data-fk="${field.to}" data-current="${v ?? ''}" ${req}>
                    <option value="">Cargando…</option>
                </select>`;
            break;
        }
        default:
            control = `<input type="text" id="${id}" name="${field.key}" value="${escapeHtml(v ?? '')}" ${req}>`;
    }

    const reqMark = field.required ? '<span style="color: var(--red);">*</span>' : '';
    return `
        <div class="form-row">
            <label for="${id}">${escapeHtml(field.label)} ${reqMark}</label>
            ${control}
        </div>
    `;
}

async function hydrateFkSelects() {
    const selects = document.querySelectorAll('#modal-body select[data-fk]');
    for (const sel of selects) {
        const fkKey = sel.dataset.fk;
        const current = sel.dataset.current;
        try {
            const opciones = await loadFkOptions(fkKey);
            const t = TABLAS_BY_KEY[fkKey];
            const required = sel.hasAttribute('required');
            const placeholder = required
                ? '<option value="" disabled selected>— Selecciona —</option>'
                : '<option value="">— sin valor —</option>';
            sel.innerHTML = placeholder + opciones.map(row => {
                const id = row[t.pk];
                const sel2 = String(id) === String(current) ? 'selected' : '';
                return `<option value="${id}" ${sel2}>${escapeHtml(fkLabel(t, row))}</option>`;
            }).join('');
        } catch (e) {
            sel.innerHTML = `<option value="">Error: ${escapeHtml(e.message)}</option>`;
        }
    }
}

async function abrirFormulario(modo, idOriginal = null) {
    const t = tablaActiva;
    const row = idOriginal !== null
        ? datosActivos.find(r => r[t.pk] === idOriginal)
        : null;

    if (modo === 'editar' && !row) {
        showError('Registro no encontrado.');
        return;
    }

    document.getElementById('modal-title').textContent =
        modo === 'crear' ? `Crear ${t.label.toLowerCase()}` : `Editar ${t.label.toLowerCase()} #${idOriginal}`;

    document.getElementById('modal-body').innerHTML = `
        <form id="form-crud">
            ${t.fields.map(f => buildField(f, row)).join('')}
        </form>
    `;
    document.getElementById('modal-resultado').innerHTML = '';
    document.getElementById('modal-form').classList.add('open');

    document.getElementById('btn-guardar').onclick = async () => {
        const btn = document.getElementById('btn-guardar');
        const original = btn.textContent;
        btn.disabled = true;
        btn.textContent = 'Ejecutando transacción…';
        try {
            const payload = readForm(t);
            let resultado;
            if (modo === 'crear') {
                resultado = await API.post(`${t.path}/`, payload);
            } else {
                resultado = await API.put(`${t.path}/${idOriginal}`, payload);
            }
            const pkVal = resultado ? resultado[t.pk] : idOriginal;
            mostrarResultadoModal(
                'commit',
                `${t.label} ${modo === 'crear' ? 'creado' : 'actualizado'} (id=${pkVal}).`,
                'El cambio quedó persistido (COMMIT en InnoDB).'
            );
            setTimeout(async () => {
                cerrarModal();
                await recargar();
            }, 1500);
        } catch (e) {
            mostrarResultadoModal(clasificarError(e), e.message);
            btn.disabled = false;
            btn.textContent = original;
        }
    };

    await hydrateFkSelects();
}

function readForm(tabla) {
    const form = document.getElementById('form-crud');
    const payload = {};
    for (const field of tabla.fields) {
        const el = form.elements[field.key];
        if (!el) continue;
        const raw = el.value;
        if (raw === '' || raw === null) {
            payload[field.key] = field.required ? '' : null;
            continue;
        }
        switch (field.type) {
            case 'int':
                payload[field.key] = parseInt(raw, 10);
                break;
            case 'decimal':
                payload[field.key] = raw;  // mandar como string para preservar precisión
                break;
            case 'bool':
                payload[field.key] = raw === 'true';
                break;
            case 'fk':
                payload[field.key] = parseInt(raw, 10);
                break;
            case 'datetime':
                // 'YYYY-MM-DDTHH:MM' → añade segundos para que Pydantic lo acepte sin sorpresas
                payload[field.key] = raw.length === 16 ? `${raw}:00` : raw;
                break;
            default:
                payload[field.key] = raw;
        }
    }
    // Validación de mínima coherencia: requeridos vacíos
    for (const field of tabla.fields) {
        if (field.required) {
            const v = payload[field.key];
            if (v === null || v === undefined || v === '' || Number.isNaN(v)) {
                throw new Error(`El campo "${field.label}" es obligatorio.`);
            }
        }
    }
    return payload;
}

// ---------------------------------------------------------------------
//  ELIMINAR
// ---------------------------------------------------------------------
async function eliminarRegistro(id) {
    const t = tablaActiva;
    const row = datosActivos.find(r => r[t.pk] === id);
    const etiqueta = row && t.displayCol ? `"${row[t.displayCol]}"` : `#${id}`;
    if (!confirm(`¿Eliminar ${t.label.toLowerCase()} ${etiqueta}?\n\nEsta acción no se puede deshacer.`)) {
        return;
    }
    try {
        await API.del(`${t.path}/${id}`);
        await recargar();
        mostrarToast('commit', `${t.label} #${id} eliminado (COMMIT).`);
    } catch (e) {
        mostrarToast(clasificarError(e), `ROLLBACK al eliminar #${id}: ${e.message}`);
    }
}

/**
 * Toast efímero arriba a la derecha — verde para COMMIT, rojo para ROLLBACK.
 * Se usa para feedback de DELETE (no abre modal).
 */
function mostrarToast(tipo, mensaje) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }
    const tag = tipo === 'commit' ? 'COMMIT' : 'ROLLBACK';
    const cls = tipo === 'commit' ? 'success-bg' : 'error-bg';
    const tagCls = tipo === 'commit' ? 'commit' : 'rollback';
    const toast = document.createElement('div');
    toast.className = `toast ${cls}`;
    toast.innerHTML = `<span class="tx-result-tag ${tagCls}">${tag}</span> ${escapeHtml(mensaje)}`;
    container.appendChild(toast);
    setTimeout(() => toast.classList.add('toast-out'), 3000);
    setTimeout(() => toast.remove(), 3500);
}

// ---------------------------------------------------------------------
//  BINDINGS GLOBALES
// ---------------------------------------------------------------------
document.getElementById('search').addEventListener('input', (e) => {
    busqueda = e.target.value.trim();
    renderTabla();
});

document.getElementById('btn-crear').addEventListener('click', () => abrirFormulario('crear'));
document.getElementById('btn-cancelar').addEventListener('click', cerrarModal);
document.getElementById('btn-cerrar-modal').addEventListener('click', cerrarModal);
document.getElementById('modal-form').addEventListener('click', (e) => {
    if (e.target.id === 'modal-form') cerrarModal();
});
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') cerrarModal();
});

renderTabs();
seleccionar(tablaActiva.key);
