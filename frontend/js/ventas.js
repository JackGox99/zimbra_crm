/**
 * Página de Ventas — vista en columnas: Pendientes, Aceptadas, Cerradas.
 */

let propuestasCache = [];
let ventasCache = [];
let prosMapCache = {};
let clientesMapCache = {};
let propuestaSeleccionada = null;
let ventaSeleccionada = null;

async function cargarVentas() {
    try {
        const [propuestas, prospectos, ventas, clientes] = await Promise.all([
            API.get('/propuestas/?limit=500'),
            API.get('/prospectos/?limit=500'),
            API.get('/ventas/?limit=500'),
            API.get('/clientes/?limit=500'),
        ]);

        propuestasCache = propuestas;
        ventasCache = ventas;
        prosMapCache = Object.fromEntries(prospectos.map(p => [p.id_prospecto, p]));
        clientesMapCache = Object.fromEntries(clientes.map(c => [c.id_cliente, c]));

        const pendientes = propuestas.filter(p => p.estado === 'Pendiente');

        renderColumnaPropuestas('col-pendientes', 'count-pendientes', 'value-pendientes',
            pendientes, 'pendiente', true);
        renderColumnaVentas('col-cerradas', 'count-cerradas', 'value-cerradas', ventas);
    } catch (e) {
        showError(e.message);
    }
}

function renderColumnaPropuestas(colId, countId, valueId, items, statusClass, clickable) {
    const col = document.getElementById(colId);
    document.getElementById(countId).textContent = items.length;
    const total = items.reduce((sum, x) => sum + parseFloat(x.valor_estimado || 0), 0);
    document.getElementById(valueId).textContent = formatMoney(total);

    if (!items.length) {
        col.innerHTML = '<p class="muted text-center" style="padding: 1rem 0; font-size: 0.85rem;">Sin propuestas en esta etapa.</p>';
        return;
    }

    col.innerHTML = items.map(p => {
        const pros = prosMapCache[p.id_prospecto];
        const nombre = pros ? pros.nombre : `Prospecto #${p.id_prospecto}`;
        const empresa = pros ? (pros.empresa || '—') : '—';
        const desc = (p.descripcion || '').slice(0, 55) +
                     ((p.descripcion || '').length > 55 ? '…' : '');
        return `
            <div class="deal-card ${statusClass} ${clickable ? 'clickable' : ''}"
                 ${clickable ? `data-id="${p.id_propuesta}"` : ''}>
                <div class="deal-header">
                    <span class="deal-id">PROP-${p.id_propuesta}</span>
                    <span class="deal-value">${formatMoney(p.valor_estimado)}</span>
                </div>
                <div class="deal-prospect">${escapeHtml(nombre)} · ${escapeHtml(empresa)}</div>
                <div class="deal-desc">${escapeHtml(desc)}</div>
                <div class="deal-meta">${formatDate(p.fecha_propuesta)}</div>
            </div>
        `;
    }).join('');

    if (clickable) {
        col.querySelectorAll('.deal-card').forEach(card => {
            card.addEventListener('click', () =>
                abrirModalCierre(parseInt(card.dataset.id, 10)));
        });
    }
}

function renderColumnaVentas(colId, countId, valueId, ventas) {
    const col = document.getElementById(colId);
    document.getElementById(countId).textContent = ventas.length;
    const totalPagado = ventas.filter(v => v.estado === 'Pagada')
        .reduce((sum, v) => sum + parseFloat(v.monto || 0), 0);
    document.getElementById(valueId).textContent = formatMoney(totalPagado) + ' facturados';

    if (!ventas.length) {
        col.innerHTML = '<p class="muted text-center" style="padding: 1rem 0; font-size: 0.85rem;">Sin ventas cerradas.</p>';
        return;
    }
    col.innerHTML = ventas.slice(0, 15).map(v => {
        const cardClass = v.estado === 'Anulada' ? 'anulada' : 'cerrada';
        const puedeAnular = v.estado !== 'Anulada';
        const cliente = clientesMapCache[v.id_cliente];
        const nombreCliente = cliente ? cliente.nombre : `Cliente #${v.id_cliente}`;
        const empresaCliente = cliente ? (cliente.empresa || '—') : '—';
        return `
            <div class="deal-card ${cardClass}">
                <div class="deal-header">
                    <span class="deal-id">VENTA-${v.id_venta}</span>
                    <span class="deal-value">${formatMoney(v.monto)}</span>
                </div>
                <div class="deal-prospect">${escapeHtml(nombreCliente)} · ${escapeHtml(empresaCliente)}</div>
                <div class="deal-meta" style="font-size: 0.72rem;">Cliente #${v.id_cliente} · PROP-${v.id_propuesta}</div>
                <div class="deal-meta">${escapeHtml(v.metodo_pago || '—')} · ${formatDate(v.fecha_venta)} · <span class="badge ${v.estado.toLowerCase()}">${escapeHtml(v.estado)}</span></div>
                ${puedeAnular ? `
                    <div class="deal-actions">
                        <button class="btn danger btn-anular" data-id="${v.id_venta}">Anular</button>
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');

    col.querySelectorAll('.btn-anular').forEach(b => {
        b.addEventListener('click', () =>
            abrirModalAnular(parseInt(b.dataset.id, 10)));
    });
}

function abrirModalAnular(id) {
    const v = ventasCache.find(x => x.id_venta === id);
    if (!v) return;
    ventaSeleccionada = id;
    document.getElementById('modal-anular-id').textContent = `#${id}`;
    document.getElementById('modal-anular-monto').textContent = formatMoney(v.monto);
    document.getElementById('modal-resultado-anular').innerHTML = '';
    const btn = document.getElementById('btn-confirmar-anular');
    btn.disabled = false;
    btn.textContent = 'Anular venta';
    document.getElementById('modal-anular').classList.add('open');
}

async function confirmarAnulacion() {
    if (!ventaSeleccionada) return;
    const btn = document.getElementById('btn-confirmar-anular');
    btn.disabled = true;
    btn.textContent = 'Ejecutando transacción…';

    try {
        const venta = await API.post(`/ventas/${ventaSeleccionada}/anular`);
        document.getElementById('modal-resultado-anular').innerHTML = `
            <div class="success-bg mt-1">
                <span class="tx-result-tag commit">COMMIT</span>
                <strong>Venta #${venta.id_venta} anulada correctamente.</strong>
                <div class="mt-1 muted" style="font-size: 0.85rem;">
                    El cambio quedó persistido en la base de datos.
                </div>
            </div>
        `;
        setTimeout(() => {
            cerrarModal('modal-anular');
            cargarVentas();
        }, 2500);
    } catch (e) {
        document.getElementById('modal-resultado-anular').innerHTML = `
            <div class="error-bg mt-1">
                <span class="tx-result-tag rollback">ROLLBACK</span>
                <strong>Transacción revertida — nada cambió en la BD.</strong>
                <div class="mt-1" style="font-size: 0.9rem;">
                    Motivo: ${escapeHtml(e.message)}
                </div>
            </div>
        `;
        btn.disabled = false;
        btn.textContent = 'Cerrar';
    }
}

function abrirModalCierre(id) {
    const p = propuestasCache.find(x => x.id_propuesta === id);
    if (!p) return;
    const pros = prosMapCache[p.id_prospecto];
    const nombreProspecto = pros
        ? `${pros.nombre} (${pros.empresa || 'Sin empresa'})`
        : `Prospecto #${p.id_prospecto}`;
    propuestaSeleccionada = id;
    document.getElementById('modal-prop-id').textContent = `#${id}`;
    document.getElementById('modal-prop-prospecto').textContent = nombreProspecto;
    document.getElementById('modal-prop-valor').textContent = formatMoney(p.valor_estimado);
    document.getElementById('modal-resultado-venta').innerHTML = '';
    const btn = document.getElementById('btn-confirmar-venta');
    btn.disabled = false;
    btn.textContent = 'Cerrar venta';
    document.getElementById('modal-cerrar').classList.add('open');
}

function cerrarModal(id) {
    document.getElementById(id).classList.remove('open');
}

async function confirmarCierreVenta() {
    if (!propuestaSeleccionada) return;
    const metodo = document.getElementById('modal-metodo-pago').value;
    const btn = document.getElementById('btn-confirmar-venta');
    btn.disabled = true;
    btn.textContent = 'Ejecutando transacción…';

    try {
        const result = await API.post('/ventas/cerrar-venta', {
            id_propuesta: propuestaSeleccionada,
            metodo_pago: metodo,
        });
        const v = result.venta;
        const tag = result.cliente_creado
            ? '🆕 <strong>Cliente nuevo creado</strong>'
            : '♻ <strong>Cliente preexistente reutilizado</strong> (recompra)';
        document.getElementById('modal-resultado-venta').innerHTML = `
            <div class="success-bg mt-1">
                <span class="tx-result-tag commit">COMMIT</span>
                <strong>${escapeHtml(result.mensaje)}</strong>
                <div class="mt-1">
                    Venta <strong>#${v.id_venta}</strong> — ${formatMoney(v.monto)}<br>
                    Método: ${escapeHtml(v.metodo_pago || '—')}<br>
                    Cliente ID: ${v.id_cliente}<br>
                    ${tag}
                </div>
            </div>
        `;
        setTimeout(() => {
            cerrarModal('modal-cerrar');
            cargarVentas();
        }, 2500);
    } catch (e) {
        document.getElementById('modal-resultado-venta').innerHTML = `
            <div class="error-bg mt-1">
                <span class="tx-result-tag rollback">ROLLBACK</span>
                <strong>Transacción revertida — nada cambió en la BD.</strong>
                <div class="mt-1" style="font-size: 0.9rem;">
                    Motivo: ${escapeHtml(e.message)}
                </div>
            </div>
        `;
        btn.disabled = false;
        btn.textContent = 'Reintentar';
    }
}

document.getElementById('btn-cancelar-venta').addEventListener('click',
    () => cerrarModal('modal-cerrar'));
document.getElementById('btn-confirmar-venta').addEventListener('click', confirmarCierreVenta);
document.getElementById('btn-cancelar-anular').addEventListener('click',
    () => cerrarModal('modal-anular'));
document.getElementById('btn-confirmar-anular').addEventListener('click', confirmarAnulacion);

cargarVentas();