/**
 * Página de Inicio — métricas comerciales, propuestas pendientes y actividad.
 */

async function cargarDashboard() {
    try {
        const [embudo, propuestas, prospectos, interacciones, ventas, trials] = await Promise.all([
            API.get('/reportes/conversion'),
            API.get('/propuestas/?limit=500'),
            API.get('/prospectos/?limit=500'),
            API.get('/interacciones/?limit=15'),
            API.get('/ventas/?limit=20'),
            API.get('/prospectos/pruebas-por-vencer?dias=7'),
        ]);

        const prosMap = Object.fromEntries(prospectos.map(p => [p.id_prospecto, p]));

        // ----- KPIs -----
        const pendientes = propuestas.filter(p => p.estado === 'Pendiente');
        const valorTotalPropuestas = pendientes.reduce(
            (sum, p) => sum + parseFloat(p.valor_estimado || 0), 0,
        );
        document.getElementById('kpi-pipeline').textContent = formatMoney(valorTotalPropuestas);
        document.getElementById('kpi-pipeline-count').textContent = pendientes.length;
        document.getElementById('kpi-ingresos').textContent = formatMoney(embudo.ingresos_totales);
        document.getElementById('kpi-ventas-count').textContent = embudo.total_ventas_pagadas;

        const tasa = embudo.total_prospectos_activos > 0
            ? ((embudo.total_clientes / embudo.total_prospectos_activos) * 100).toFixed(1)
            : '0.0';
        document.getElementById('kpi-conversion').textContent = `${tasa}%`;

        // Prospectos por contactar: Calificados que aún no tienen propuesta
        const conPropuesta = new Set(propuestas.map(p => p.id_prospecto));
        const prospectosPorContactar = prospectos.filter(p =>
            p.estado === 'Calificado' && !conPropuesta.has(p.id_prospecto)
        );
        document.getElementById('kpi-leads-calientes').textContent = prospectosPorContactar.length;

        // ----- Top 5 propuestas pendientes por valor -----
        const topPropuestas = [...pendientes]
            .sort((a, b) => parseFloat(b.valor_estimado) - parseFloat(a.valor_estimado))
            .slice(0, 5);
        renderPropuestasPreview(topPropuestas, prosMap);

        // ----- Activity feed -----
        renderActivityFeed(interacciones, ventas, prosMap);

        // ----- Action cards -----
        document.getElementById('action-trials').textContent = trials.length;
        document.getElementById('action-hot').textContent = prospectosPorContactar.length;
        document.getElementById('action-pendientes').textContent = pendientes.length;
    } catch (e) {
        showError(e.message);
    }
}

function renderPropuestasPreview(propuestas, prosMap) {
    const container = document.getElementById('pipeline-preview');
    if (!propuestas.length) {
        container.innerHTML = '<div class="card"><p class="muted text-center">No hay propuestas pendientes.</p></div>';
        return;
    }
    container.innerHTML = propuestas.map(p => {
        const pros = prosMap[p.id_prospecto];
        const nombre = pros ? pros.nombre : `Prospecto #${p.id_prospecto}`;
        const empresa = pros ? (pros.empresa || '—') : '—';
        const desc = (p.descripcion || '').slice(0, 50) +
                     ((p.descripcion || '').length > 50 ? '…' : '');
        return `
            <div class="deal-card">
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
}

function renderActivityFeed(interacciones, ventas, prosMap) {
    const items = [
        ...interacciones.map(i => ({
            type: 'scoring',
            icon: '📊',
            title: `${prosMap[i.id_prospecto]?.nombre || `Prospecto #${i.id_prospecto}`} — ${i.accion}`,
            meta: `+${i.peso_scoring} pts · ${formatDateTime(i.fecha_interaccion)}`,
            date: new Date(i.fecha_interaccion),
        })),
        ...ventas.map(v => ({
            type: 'venta',
            icon: '💰',
            title: `Venta ${v.estado.toLowerCase()} — ${formatMoney(v.monto)}`,
            meta: `Cliente #${v.id_cliente} · ${v.metodo_pago || 'Sin método'} · ${formatDate(v.fecha_venta)}`,
            date: new Date(v.fecha_venta),
        })),
    ].sort((a, b) => b.date - a.date).slice(0, 12);

    const tl = document.getElementById('activity-feed');
    if (!items.length) {
        tl.innerHTML = '<li class="muted text-center" style="padding: 1rem;">Sin actividad reciente.</li>';
        return;
    }
    tl.innerHTML = items.map(a => `
        <li class="activity-item">
            <span class="activity-icon ${a.type}">${a.icon}</span>
            <div class="activity-content">
                <div class="activity-title">${escapeHtml(a.title)}</div>
                <div class="activity-meta">${escapeHtml(a.meta)}</div>
            </div>
        </li>
    `).join('');
}

cargarDashboard();