/**
 * Página de Prospectos — tarjetas con búsqueda y filtros por estado.
 */

let allProspectos = [];
let estadoFilter = '';
let searchTerm = '';
let prospectoSeleccionado = null;

async function cargarProspectos() {
    try {
        const data = await API.get('/prospectos/?limit=500');
        allProspectos = data;
        renderProspectos();
    } catch (e) {
        showError(e.message);
    }
}

function renderProspectos() {
    let filtered = allProspectos;
    if (estadoFilter) {
        filtered = filtered.filter(p => p.estado === estadoFilter);
    }
    if (searchTerm) {
        const q = searchTerm.toLowerCase();
        filtered = filtered.filter(p =>
            (p.nombre || '').toLowerCase().includes(q) ||
            (p.correo || '').toLowerCase().includes(q) ||
            (p.empresa || '').toLowerCase().includes(q)
        );
    }

    document.getElementById('count').textContent =
        `${filtered.length} de ${allProspectos.length} prospectos`;

    const list = document.getElementById('leads-list');
    if (!filtered.length) {
        list.innerHTML = '<div class="card text-center muted" style="padding: 2rem;">Sin prospectos que coincidan con el filtro.</div>';
        return;
    }

    list.innerHTML = filtered.map(renderProspectoCard).join('');

    list.querySelectorAll('.btn-add-interaccion').forEach(b => {
        b.addEventListener('click', () => abrirModalInteraccion(parseInt(b.dataset.id, 10)));
    });
    list.querySelectorAll('.btn-crear-propuesta').forEach(b => {
        b.addEventListener('click', () => abrirModalPropuesta(parseInt(b.dataset.id, 10)));
    });
    list.querySelectorAll('.btn-marcar-inadec').forEach(b => {
        b.addEventListener('click', () => marcarInadecuado(parseInt(b.dataset.id, 10)));
    });
    list.querySelectorAll('.btn-extender-trial').forEach(b => {
        b.addEventListener('click', () => extenderTrial(parseInt(b.dataset.id, 10)));
    });
}

function abrirModalPropuesta(id) {
    const p = allProspectos.find(x => x.id_prospecto === id);
    if (!p) return;
    prospectoSeleccionado = id;
    document.getElementById('modal-propuesta-prospecto').textContent =
        `${p.nombre} (${p.empresa || 'Sin empresa'})`;
    document.getElementById('modal-propuesta-desc').value = '';
    document.getElementById('modal-propuesta-valor').value = '5000000';
    document.getElementById('modal-resultado-propuesta').innerHTML = '';
    const btn = document.getElementById('btn-confirmar-propuesta');
    btn.disabled = false;
    btn.textContent = 'Crear propuesta';
    document.getElementById('modal-propuesta').classList.add('open');
}

async function crearPropuesta() {
    if (!prospectoSeleccionado) return;
    const descripcion = document.getElementById('modal-propuesta-desc').value.trim();
    const valor = parseFloat(document.getElementById('modal-propuesta-valor').value);

    if (!descripcion) {
        showError('La descripción es obligatoria.');
        return;
    }
    if (isNaN(valor) || valor < 0) {
        showError('El valor debe ser un número positivo.');
        return;
    }

    const btn = document.getElementById('btn-confirmar-propuesta');
    btn.disabled = true;
    btn.textContent = 'Guardando…';

    try {
        const result = await API.post('/propuestas/', {
            descripcion,
            fecha_propuesta: new Date().toISOString().slice(0, 10),
            estado: 'Pendiente',
            valor_estimado: valor,
            id_prospecto: prospectoSeleccionado,
        });
        document.getElementById('modal-resultado-propuesta').innerHTML = `
            <div class="success-bg mt-1">
                <span class="tx-result-tag commit">COMMIT</span>
                <strong>Propuesta PROP-${result.id_propuesta} creada.</strong>
                <div class="mt-1" style="font-size: 0.85rem;">
                    Aparecerá en la página de <strong>Ventas → columna Pendientes</strong>
                    esperando respuesta del prospecto.
                </div>
            </div>
        `;
        setTimeout(() => {
            cerrarModal('modal-propuesta');
            cargarProspectos();
        }, 2500);
    } catch (e) {
        document.getElementById('modal-resultado-propuesta').innerHTML = `
            <div class="error-bg mt-1">
                <span class="tx-result-tag rollback">ROLLBACK</span>
                <strong>Transacción revertida — la propuesta no se creó.</strong>
                <div class="mt-1" style="font-size: 0.9rem;">${escapeHtml(e.message)}</div>
            </div>
        `;
        btn.disabled = false;
        btn.textContent = 'Reintentar';
    }
}

function getInteresLabel(puntuacion) {
    // Convierte el scoring numérico en una etiqueta cualitativa.
    // El scoring se acumula con cada interacción (apertura correo +2,
    // click +3, visita precios +5, descarga prueba +10, etc.).
    if (puntuacion >= 15) return { texto: 'Alto',  clase: 'interes-alto'  };
    if (puntuacion >= 5)  return { texto: 'Medio', clase: 'interes-medio' };
    return                       { texto: 'Bajo',  clase: 'interes-bajo'  };
}

function renderProspectoCard(p) {
    const initials = getInitials(p.nombre);
    const scorePercent = Math.min(100, (p.puntuacion / 20) * 100);
    const estadoLower = p.estado.toLowerCase();
    const showActions = p.estado !== 'Convertido' && p.estado !== 'Inadecuado';
    const canCreatePropuesta = p.estado === 'Calificado' || p.estado === 'Contactado';
    const canExtenderTrial = p.fecha_fin_prueba && p.estado !== 'Convertido' && p.estado !== 'Inadecuado';
    const interes = getInteresLabel(p.puntuacion);

    return `
        <div class="lead-card ${estadoLower}">
            <div class="avatar lg">${escapeHtml(initials)}</div>
            <div class="lead-info">
                <div class="name">${escapeHtml(p.nombre)}</div>
                <div class="company">${escapeHtml(p.empresa || '—')}</div>
                <div class="meta">
                    <span>📧 ${escapeHtml(p.correo)}</span>
                    ${p.telefono ? `<span>📞 ${escapeHtml(p.telefono)}</span>` : ''}
                    ${p.fecha_fin_prueba ? `<span>⏰ Trial vence ${formatDate(p.fecha_fin_prueba)}</span>` : ''}
                </div>
                <div class="score-row">
                    <span class="score-label">Interés:</span>
                    <div class="score-bar"><div class="score-bar-fill" style="width: ${scorePercent}%"></div></div>
                    <span class="score-value ${interes.clase}">${interes.texto}</span>
                    <span class="badge ${estadoLower}">${escapeHtml(p.estado)}</span>
                </div>
            </div>
            <div class="lead-actions">
                ${showActions ? `
                    <button class="btn btn-add-interaccion" data-id="${p.id_prospecto}">+ Interacción</button>
                    ${canCreatePropuesta ? `<button class="btn green btn-crear-propuesta" data-id="${p.id_prospecto}">+ Propuesta</button>` : ''}
                    ${canExtenderTrial ? `<button class="btn muted-btn btn-extender-trial" data-id="${p.id_prospecto}" title="Extiende el trial llamando al SP sp_extender_trial">⏰ Extender trial</button>` : ''}
                    <button class="btn danger btn-marcar-inadec" data-id="${p.id_prospecto}">Descalificar</button>
                ` : '<span class="muted" style="font-size: 0.78rem;">Sin acciones disponibles</span>'}
            </div>
        </div>
    `;
}

function getInitials(name) {
    if (!name) return '?';
    return name.trim().split(/\s+/).slice(0, 2).map(w => w[0] || '').join('').toUpperCase();
}

function abrirModalInteraccion(id) {
    const p = allProspectos.find(x => x.id_prospecto === id);
    if (!p) return;
    prospectoSeleccionado = id;
    document.getElementById('modal-prospecto-nombre').textContent =
        `${p.nombre} (${p.empresa || 'Sin empresa'})`;
    document.getElementById('modal-resultado-interaccion').innerHTML = '';
    const btn = document.getElementById('btn-registrar-interaccion');
    btn.disabled = false;
    btn.textContent = 'Registrar';
    document.getElementById('modal-interaccion').classList.add('open');
}

function cerrarModal(id) {
    document.getElementById(id).classList.remove('open');
}

async function registrarInteraccion() {
    if (!prospectoSeleccionado) return;
    const [accion, peso] = document.getElementById('modal-accion').value.split('|');
    const id_campana = parseInt(document.getElementById('modal-campana').value, 10);
    if (!id_campana || id_campana < 1) {
        showError('ID de campaña inválido.');
        return;
    }

    const btn = document.getElementById('btn-registrar-interaccion');
    btn.disabled = true;
    btn.textContent = 'Procesando…';

    try {
        const result = await API.post('/interacciones/registrar', {
            accion,
            peso_scoring: parseInt(peso, 10),
            id_prospecto: prospectoSeleccionado,
            id_campana,
            fecha_interaccion: new Date().toISOString().slice(0, 19),
        });
        const calif = result.prospecto_calificado_ahora;
        const bgClass = calif ? 'success-bg' : '';
        const extra = calif
            ? '<br><span style="font-size: 1.2em;">🎉</span> Prospecto promovido a <strong>Calificado</strong>.'
            : '';
        document.getElementById('modal-resultado-interaccion').innerHTML = `
            <div class="${bgClass}" style="padding: 0.75rem 1rem; margin-top: 1rem; border-radius: 4px; background: ${calif ? '#d4edda' : '#e6f2ff'};">
                <strong>✓ ${escapeHtml(result.mensaje)}</strong><br>
                Puntuación: <strong>${result.puntuacion_actualizada} pts</strong>
                ${extra}
            </div>
        `;
        setTimeout(() => {
            cerrarModal('modal-interaccion');
            cargarProspectos();
        }, 1800);
    } catch (e) {
        document.getElementById('modal-resultado-interaccion').innerHTML = `
            <div class="error-bg mt-1">
                <strong>✗ Transacción revertida</strong><br>${escapeHtml(e.message)}
            </div>
        `;
        btn.disabled = false;
        btn.textContent = 'Reintentar';
    }
}

async function marcarInadecuado(id) {
    const p = allProspectos.find(x => x.id_prospecto === id);
    const nombre = p ? p.nombre : `#${id}`;
    if (!confirm(`¿Descalificar a ${nombre}?\nSu puntuación se reseteará a 0 dentro de una transacción atómica.`)) return;
    try {
        await API.post(`/prospectos/${id}/marcar-inadecuado`);
        cargarProspectos();
    } catch (e) {
        showError(e.message);
    }
}

async function extenderTrial(id) {
    const p = allProspectos.find(x => x.id_prospecto === id);
    const nombre = p ? p.nombre : `#${id}`;
    const diasStr = prompt(`Extender trial de ${nombre}\n¿Cuántos días sumar al periodo de prueba? (1-90)`, '15');
    if (diasStr === null) return;
    const dias = parseInt(diasStr, 10);
    if (!dias || dias < 1 || dias > 90) {
        showError('Días debe ser un número entre 1 y 90.');
        return;
    }
    try {
        const r = await API.post(`/automatizacion/extender-trial/${id}?dias=${dias}`);
        alert(
            `✓ Trial extendido por SP sp_extender_trial\n\n` +
            `Prospecto: ${r.nombre}\n` +
            `Antes:  ${formatDate(r.fecha_anterior)}\n` +
            `Ahora: ${formatDate(r.fecha_nueva)}\n` +
            `Días sumados: ${r.dias_extendidos}`
        );
        cargarProspectos();
    } catch (e) {
        showError(e.message);
    }
}

// ----- Event listeners -----
document.getElementById('chips').addEventListener('click', (e) => {
    if (!e.target.classList.contains('chip')) return;
    document.querySelectorAll('#chips .chip').forEach(c => c.classList.remove('active'));
    e.target.classList.add('active');
    estadoFilter = e.target.dataset.estado || '';
    renderProspectos();
});

document.getElementById('search').addEventListener('input', (e) => {
    searchTerm = e.target.value.trim();
    renderProspectos();
});

document.getElementById('btn-cancelar-interaccion').addEventListener('click',
    () => cerrarModal('modal-interaccion'));
document.getElementById('btn-registrar-interaccion').addEventListener('click', registrarInteraccion);
document.getElementById('btn-cancelar-propuesta').addEventListener('click',
    () => cerrarModal('modal-propuesta'));
document.getElementById('btn-confirmar-propuesta').addEventListener('click', crearPropuesta);

cargarProspectos();