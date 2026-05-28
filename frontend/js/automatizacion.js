/**
 * Página de Automatización — llama a los SP/UDFs y muestra la auditoría
 * generada por los triggers de la sesión 3.
 */

const $ = (id) => document.getElementById(id);

function setResult(elId, html, ok = true) {
    const div = $(elId);
    div.innerHTML = `<div class="${ok ? 'success-bg' : 'error-bg'} mt-1">${html}</div>`;
}

// ----- SP: reporte mensual -----
async function generarReporteMensual() {
    const anio = parseInt($('rep-anio').value, 10);
    const mes  = parseInt($('rep-mes').value, 10);
    const btn = $('btn-reporte-mensual');
    btn.disabled = true; btn.textContent = 'Ejecutando…';
    try {
        const r = await API.post('/automatizacion/reporte-mensual', { anio, mes });
        setResult('result-reporte', `
            <span class="tx-result-tag commit">CALL OK</span>
            <strong>Reporte ${r.id_reporte} generado.</strong>
            <div class="mt-1" style="font-size: 0.88rem;">
                Periodo: ${formatDate(r.periodo_inicio)} → ${formatDate(r.periodo_fin)}<br>
                Ventas pagadas: <strong>${r.num_ventas}</strong><br>
                Facturado: <strong>${formatMoney(r.total_facturado)}</strong><br>
                Top campaña: <strong>${escapeHtml(r.top_campana || 'N/A')}</strong>
            </div>
        `);
    } catch (e) {
        setResult('result-reporte', `<strong>Error del SP:</strong> ${escapeHtml(e.message)}`, false);
    } finally {
        btn.disabled = false; btn.textContent = 'Generar reporte';
    }
}

// ----- SP: limpiar trials vencidos -----
async function limpiarTrials() {
    if (!confirm('¿Ejecutar limpieza? Los prospectos con trial vencido pasarán a Inadecuado.')) return;
    const btn = $('btn-limpiar-trials');
    btn.disabled = true; btn.textContent = 'Ejecutando…';
    try {
        const r = await API.post('/automatizacion/limpiar-trials-vencidos');
        setResult('result-limpieza', `
            <span class="tx-result-tag commit">CALL OK</span>
            <strong>${r.prospectos_marcados} prospecto(s) marcados.</strong>
            <div class="mt-1" style="font-size: 0.88rem;">
                Fecha de proceso: ${formatDate(r.fecha_proceso)}.<br>
                Los triggers BEFORE UPDATE y de auditoría ya dejaron registro.
            </div>
        `);
        cargarAuditoria();
    } catch (e) {
        setResult('result-limpieza', `<strong>Error:</strong> ${escapeHtml(e.message)}`, false);
    } finally {
        btn.disabled = false; btn.textContent = 'Ejecutar limpieza';
    }
}

// ----- SP: extender trial -----
async function extenderTrial() {
    const id = parseInt($('sp-ext-id').value, 10);
    const dias = parseInt($('sp-ext-dias').value, 10);
    const btn = $('btn-extender-trial');
    btn.disabled = true; btn.textContent = 'Ejecutando…';
    try {
        const r = await API.post(`/automatizacion/extender-trial/${id}?dias=${dias}`);
        setResult('result-extender', `
            <span class="tx-result-tag commit">CALL OK</span>
            <strong>Trial de ${escapeHtml(r.nombre)} extendido +${r.dias_extendidos} días.</strong>
            <div class="mt-1" style="font-size: 0.88rem;">
                Fecha anterior: ${formatDate(r.fecha_anterior)}<br>
                Fecha nueva: <strong>${formatDate(r.fecha_nueva)}</strong>
            </div>
        `);
    } catch (e) {
        setResult('result-extender', `<strong>Error del SP:</strong> ${escapeHtml(e.message)}`, false);
    } finally {
        btn.disabled = false; btn.textContent = 'Extender trial';
    }
}

// ----- UDF: nivel de interés -----
async function consultarNivelInteres() {
    const puntuacion = parseInt($('udf-puntuacion').value, 10);
    try {
        const r = await API.get(`/automatizacion/funciones/nivel-interes?puntuacion=${puntuacion}`);
        $('result-nivel-interes').innerHTML = `
            <div class="success-bg" style="padding: 0.6rem 0.9rem;">
                <code>SELECT fn_nivel_interes(${puntuacion})</code> →
                <strong style="font-size: 1.05rem;">${escapeHtml(r.nivel_interes)}</strong>
            </div>
        `;
    } catch (e) {
        $('result-nivel-interes').innerHTML =
            `<div class="error-bg">Error: ${escapeHtml(e.message)}</div>`;
    }
}

// ----- UDF: días restantes de trial -----
async function consultarDiasRestantes() {
    const id = parseInt($('udf-id-prospecto').value, 10);
    try {
        const r = await API.get(`/automatizacion/funciones/dias-restantes/${id}`);
        const dias = r.dias_restantes;
        let texto, color;
        if (dias === null) {
            texto = 'Sin trial activo';
            color = 'muted';
        } else if (dias < 0) {
            texto = `Vencido hace ${-dias} días`;
            color = 'error-bg';
        } else {
            texto = `${dias} días restantes`;
            color = 'success-bg';
        }
        $('result-dias-restantes').innerHTML = `
            <div class="${color === 'muted' ? '' : color}" style="padding: 0.6rem 0.9rem;">
                <code>SELECT fn_dias_restantes_trial(${id})</code> →
                <strong>${escapeHtml(texto)}</strong>
                ${r.fecha_fin_prueba ? `<br><span class="muted">Fin de trial: ${formatDate(r.fecha_fin_prueba)}</span>` : ''}
            </div>
        `;
    } catch (e) {
        $('result-dias-restantes').innerHTML =
            `<div class="error-bg">Error: ${escapeHtml(e.message)}</div>`;
    }
}

// ----- UDF: lifetime value -----
async function consultarLifetime() {
    const id = parseInt($('udf-id-cliente').value, 10);
    try {
        const r = await API.get(`/automatizacion/funciones/lifetime-value/${id}`);
        $('result-lifetime').innerHTML = `
            <div class="success-bg" style="padding: 0.6rem 0.9rem;">
                <code>SELECT fn_lifetime_value(${id})</code> →
                <strong style="font-size: 1.05rem;">${formatMoney(r.lifetime_value)}</strong>
            </div>
        `;
    } catch (e) {
        $('result-lifetime').innerHTML =
            `<div class="error-bg">Error: ${escapeHtml(e.message)}</div>`;
    }
}

// ----- Bitácora poblada por trigger (leída de REPORTE) -----
async function cargarAuditoria() {
    const idRaw = $('audit-id').value.trim();
    const query = idRaw ? `?id_prospecto=${parseInt(idRaw, 10)}&limit=200` : '?limit=200';
    const body = $('audit-body');
    body.innerHTML = '<tr><td colspan="7" class="muted text-center">Cargando…</td></tr>';
    try {
        const rows = await API.get(`/automatizacion/auditoria${query}`);
        if (!rows.length) {
            body.innerHTML = '<tr><td colspan="7" class="muted text-center">Sin eventos registrados.</td></tr>';
            return;
        }
        body.innerHTML = rows.map(a => `
            <tr>
                <td>${a.id_reporte}</td>
                <td>#${a.id_prospecto}</td>
                <td><span class="badge ${(a.estado_anterior || '').toLowerCase()}">${escapeHtml(a.estado_anterior || '—')}</span></td>
                <td style="text-align: center;">→</td>
                <td><span class="badge ${a.estado_nuevo.toLowerCase()}">${escapeHtml(a.estado_nuevo)}</span></td>
                <td>${a.puntuacion ?? '—'}</td>
                <td>${formatDateTime(a.fecha_evento)}</td>
            </tr>
        `).join('');
    } catch (e) {
        body.innerHTML = `<tr><td colspan="7" class="error-text text-center">Error: ${escapeHtml(e.message)}</td></tr>`;
    }
}

// ----- Bindings -----
$('btn-reporte-mensual').addEventListener('click', generarReporteMensual);
$('btn-limpiar-trials').addEventListener('click', limpiarTrials);
$('btn-extender-trial').addEventListener('click', extenderTrial);
$('btn-nivel-interes').addEventListener('click', consultarNivelInteres);
$('btn-dias-restantes').addEventListener('click', consultarDiasRestantes);
$('btn-lifetime').addEventListener('click', consultarLifetime);
$('btn-cargar-auditoria').addEventListener('click', cargarAuditoria);

cargarAuditoria();