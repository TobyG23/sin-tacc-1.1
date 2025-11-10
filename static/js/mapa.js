// Variables globales
let mapa;
let todosLosLugares = lugares;
let marcadoresActuales = [];
let grupoCluster;
let categorias = [];
let etiquetas = [];
let filtrosActivos = {
    texto: '',
    destacados: false,
    mejores: false,
    categorias: [],
    etiquetas: []
};

// Inicialización del mapa
document.addEventListener('DOMContentLoaded', function () {
    // Inicializar mapa
    mapa = L.map('map');
    grupoCluster = L.markerClusterGroup({
        maxClusterRadius: 50,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false
    });

    // Configurar ubicación inicial
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                mapa.setView([lat, lng], 13);
            },
            function () {
                // Fallback a ubicación por defecto (Argentina)
                mapa.setView([-34.6037, -58.3816], 5);
            }
        );
    } else {
        mapa.setView([-34.6037, -58.3816], 5);
    }

    // Agregar capa de tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(mapa);

    // Cargar categorías y etiquetas
    cargarCategorias();
    cargarEtiquetas();

    // Cargar lugares iniciales
    aplicarFiltros();

    // Configurar event listeners
    configurarEventListeners();
});

// Cargar categorías desde la API
async function cargarCategorias() {
    try {
        const response = await fetch('/api/categorias');
        const data = await response.json();
        categorias = data.categorias;
        renderizarCategorias();
    } catch (error) {
        console.error('Error cargando categorías:', error);
        document.getElementById('categoriasFiltro').innerHTML =
            '<p class="text-danger small">Error cargando categorías</p>';
    }
}

// Cargar etiquetas desde la API
async function cargarEtiquetas() {
    try {
        const response = await fetch('/api/etiquetas');
        const data = await response.json();
        etiquetas = data.etiquetas;
        renderizarEtiquetas();
    } catch (error) {
        console.error('Error cargando etiquetas:', error);
        document.getElementById('etiquetasFiltro').innerHTML =
            '<p class="text-danger small">Error cargando etiquetas</p>';
    }
}

// Renderizar checkboxes de categorías
function renderizarCategorias() {
    const container = document.getElementById('categoriasFiltro');
    if (!container) return;

    if (categorias.length === 0) {
        container.innerHTML = '<p class="text-muted small">No hay categorías</p>';
        return;
    }

    container.innerHTML = categorias.map(cat => `
        <div class="categoria-checkbox">
            <input class="form-check-input me-2" type="checkbox"
                   id="cat_${cat.id}" value="${cat.id}"
                   onchange="toggleCategoria(${cat.id})">
            <label class="form-check-label" for="cat_${cat.id}">
                <i class="fas fa-${cat.icono || 'store'}" style="color: ${cat.color};"></i>
                ${cat.nombre}
            </label>
        </div>
    `).join('');
}

// Renderizar checkboxes de etiquetas
function renderizarEtiquetas() {
    const container = document.getElementById('etiquetasFiltro');
    if (!container) return;

    if (etiquetas.length === 0) {
        container.innerHTML = '<p class="text-muted small">No hay etiquetas</p>';
        return;
    }

    container.innerHTML = etiquetas.map(etiq => `
        <div class="etiqueta-checkbox">
            <input class="form-check-input me-2" type="checkbox"
                   id="etiq_${etiq.id}" value="${etiq.id}"
                   onchange="toggleEtiqueta(${etiq.id})">
            <label class="form-check-label" for="etiq_${etiq.id}">
                <i class="fas fa-${etiq.icono || 'tag'}" style="color: ${etiq.color};"></i>
                ${etiq.nombre}
            </label>
        </div>
    `).join('');
}

// Toggle categoría
function toggleCategoria(categoriaId) {
    const index = filtrosActivos.categorias.indexOf(categoriaId);
    if (index > -1) {
        filtrosActivos.categorias.splice(index, 1);
    } else {
        filtrosActivos.categorias.push(categoriaId);
    }
    aplicarFiltros();
}

// Toggle etiqueta
function toggleEtiqueta(etiquetaId) {
    const index = filtrosActivos.etiquetas.indexOf(etiquetaId);
    if (index > -1) {
        filtrosActivos.etiquetas.splice(index, 1);
    } else {
        filtrosActivos.etiquetas.push(etiquetaId);
    }
    aplicarFiltros();
}

// Limpiar todos los filtros
function limpiarFiltros() {
    filtrosActivos = {
        texto: '',
        destacados: false,
        mejores: false,
        categorias: [],
        etiquetas: []
    };

    // Limpiar UI
    document.getElementById('buscador').value = '';
    document.getElementById('filtroDestacados').checked = false;
    document.getElementById('filtroMejores').checked = false;

    // Desmarcar categorías
    categorias.forEach(cat => {
        const checkbox = document.getElementById(`cat_${cat.id}`);
        if (checkbox) checkbox.checked = false;
    });

    // Desmarcar etiquetas
    etiquetas.forEach(etiq => {
        const checkbox = document.getElementById(`etiq_${etiq.id}`);
        if (checkbox) checkbox.checked = false;
    });

    aplicarFiltros();
}

// Aplicar todos los filtros
function aplicarFiltros() {
    let filtrados = todosLosLugares;

    // Filtro por texto
    if (filtrosActivos.texto) {
        const texto = filtrosActivos.texto.toLowerCase();
        filtrados = filtrados.filter(l =>
            l.nombre.toLowerCase().includes(texto) ||
            (l.ciudad && l.ciudad.toLowerCase().includes(texto)) ||
            (l.provincia && l.provincia.toLowerCase().includes(texto))
        );
    }

    // Filtro por destacados
    if (filtrosActivos.destacados) {
        filtrados = filtrados.filter(l => l.destacado);
    }

    // Filtro por mejores (4.5+)
    if (filtrosActivos.mejores) {
        filtrados = filtrados.filter(l => l.promedio >= 4.5);
    }

    // Filtro por categorías (OR - mostrar si tiene al menos una)
    if (filtrosActivos.categorias.length > 0) {
        filtrados = filtrados.filter(l => {
            if (!l.categorias || l.categorias.length === 0) return false;
            // Obtener IDs de categorías del lugar
            const categoriasLugar = categorias
                .filter(cat => l.categorias.includes(cat.nombre))
                .map(cat => cat.id);
            // Verificar si tiene al menos una de las categorías seleccionadas
            return filtrosActivos.categorias.some(catId => categoriasLugar.includes(catId));
        });
    }

    // Filtro por etiquetas (OR - mostrar si tiene al menos una)
    if (filtrosActivos.etiquetas.length > 0) {
        filtrados = filtrados.filter(l => {
            if (!l.etiquetas || l.etiquetas.length === 0) return false;
            // Obtener IDs de etiquetas del lugar
            const etiquetasLugar = etiquetas
                .filter(etiq => l.etiquetas.includes(etiq.nombre))
                .map(etiq => etiq.id);
            // Verificar si tiene al menos una de las etiquetas seleccionadas
            return filtrosActivos.etiquetas.some(etiqId => etiquetasLugar.includes(etiqId));
        });
    }

    // Actualizar mapa y contador
    cargarLugares(filtrados);
    actualizarContador(filtrados.length);

    // Si solo hay un resultado, centrarlo en el mapa
    if (filtrados.length === 1 && filtrados[0].lat && filtrados[0].lng) {
        mapa.setView([filtrados[0].lat, filtrados[0].lng], 15);
    }
}

// Cargar lugares en el mapa
function cargarLugares(lugaresAMostrar) {
    // Limpiar marcadores existentes
    grupoCluster.clearLayers();
    marcadoresActuales = [];

    lugaresAMostrar.forEach(lugar => {
        if (lugar.lat !== null && lugar.lng !== null) {
            // Crear contenido del popup
            const popup = `
                <div class="popup-contenedor" style="min-width: 250px;">
                    <h6 class="fw-bold mb-2">${lugar.nombre}</h6>
                    <p class="small mb-1">
                        <i class="fas fa-map-marker-alt text-danger"></i>
                        ${lugar.direccion}, ${lugar.ciudad}
                    </p>
                    ${lugar.tipo ? `<p class="small mb-2"><em>${lugar.tipo}</em></p>` : ''}
                    ${lugar.promedio ? `
                        <div class="mb-2">
                            <span class="badge bg-warning text-dark">
                                <i class="fas fa-star"></i> ${lugar.promedio.toFixed(1)} / 5
                            </span>
                        </div>
                    ` : ''}
                    ${lugar.categorias && lugar.categorias.length > 0 ? `
                        <div class="mb-2">
                            ${lugar.categorias.map(cat => `<span class="badge bg-info small">${cat}</span>`).join(' ')}
                        </div>
                    ` : ''}
                    <div class="d-grid gap-1 mt-2">
                        <a href="/lugar/${lugar.id}" class="btn btn-sm btn-primary">
                            <i class="fas fa-eye"></i> Ver Detalles
                        </a>
                        <a href="https://www.google.com/maps/dir/?api=1&destination=${lugar.lat},${lugar.lng}"
                           target="_blank" class="btn btn-sm btn-outline-secondary">
                            <i class="fas fa-directions"></i> Cómo Llegar
                        </a>
                    </div>
                </div>
            `;

            // Determinar icono según tipo
            const iconoUrl = lugar.destacado
                ? '/static/img/icono-patrocinado.png'
                : (lugar.promedio >= 4.5
                    ? '/static/img/sin_gluten_oro.png'
                    : '/static/img/sin_gluten_legal-01.png');

            const icono = L.icon({
                iconUrl: iconoUrl,
                iconSize: [40, 40],
                iconAnchor: [20, 40],
                popupAnchor: [0, -40],
                className: lugar.destacado ? 'marcador-destacado' : ''
            });

            // Crear marcador
            const marker = L.marker([lugar.lat, lugar.lng], { icon: icono })
                .bindPopup(popup);

            grupoCluster.addLayer(marker);
            marcadoresActuales.push(marker);
        }
    });

    // Agregar cluster al mapa
    if (!mapa.hasLayer(grupoCluster)) {
        mapa.addLayer(grupoCluster);
    }

    // Si hay marcadores, ajustar vista
    if (marcadoresActuales.length > 0 && grupoCluster.getBounds().isValid()) {
        mapa.fitBounds(grupoCluster.getBounds(), { padding: [50, 50] });
    }
}

// Actualizar contador de resultados
function actualizarContador(cantidad) {
    const contador = document.getElementById('contadorResultados');
    if (contador) {
        contador.textContent = cantidad;
    }
}

// Configurar event listeners
function configurarEventListeners() {
    // Buscador
    const buscador = document.getElementById('buscador');
    if (buscador) {
        buscador.addEventListener('input', function() {
            filtrosActivos.texto = this.value;
            aplicarFiltros();
        });
    }

    // Filtro destacados
    const filtroDestacados = document.getElementById('filtroDestacados');
    if (filtroDestacados) {
        filtroDestacados.addEventListener('change', function() {
            filtrosActivos.destacados = this.checked;
            aplicarFiltros();
        });
    }

    // Filtro mejores
    const filtroMejores = document.getElementById('filtroMejores');
    if (filtroMejores) {
        filtroMejores.addEventListener('change', function() {
            filtrosActivos.mejores = this.checked;
            aplicarFiltros();
        });
    }
}

// Estilos adicionales para marcadores destacados
const style = document.createElement('style');
style.textContent = `
    .marcador-destacado {
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
            filter: drop-shadow(0 0 0 rgba(255, 215, 0, 0.7));
        }
        50% {
            transform: scale(1.1);
            filter: drop-shadow(0 0 10px rgba(255, 215, 0, 1));
        }
    }

    .leaflet-popup-content-wrapper {
        border-radius: 10px;
        box-shadow: 0 3px 14px rgba(0,0,0,0.4);
    }

    .leaflet-popup-content {
        margin: 10px;
    }
`;
document.head.appendChild(style);
