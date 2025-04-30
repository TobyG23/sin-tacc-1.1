const mapa = L.map('map').setView([-27.4581, -58.9756], 15);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(mapa);
        
        const iconoSinTACC = L.icon({
            iconUrl: '/static/img/sin_gluten_legal-01.png', // URL del ícono
            iconSize: [48, 48],       // Tamaño del ícono
            iconAnchor: [24, 48],     // Punto del ícono que corresponde a la ubicación
            popupAnchor: [0, -48]     // Punto desde el cual se abrirá el popup
        });
        
        console.log(lugares);

        let primerMarcador = null;

        const grupoCluster = L.markerClusterGroup(); // 💬 1) Crear el cluster al principio

        lugares.forEach(lugar => {
            if (lugar.lat !== null && lugar.lng !== null) {
                const popup = `
                    <div class="popup-contenedor">
                        <strong class="popup-titulo">${lugar.nombre}</strong><br>
                        <span class="popup-direccion">${lugar.direccion}, ${lugar.ciudad}, ${lugar.provincia}</span><br>
                        <em class="popup-tipo">${lugar.tipo}</em><br><br>
                        <a href="https://www.google.com/maps/search/?api=1&query=${lugar.lat},${lugar.lng}" 
                            target="_blank" 
                            class="popup-boton pulse">
                                🌍 Ir con Google Maps
                        </a>
                    </div>
                `;

                console.log("Agregando marcador en:", lugar.lat, lugar.lng);
                
                const marker = L.marker([lugar.lat, lugar.lng], { icon: iconoSinTACC }).bindPopup(popup); // 💬 2) Crear el marcador
                grupoCluster.addLayer(marker); // 💬 3) Agregarlo al grupoCluster
            }
        });

mapa.addLayer(grupoCluster); // 💬 4) Al final, agregar todos al mapa de una sola vez


        if (primerMarcador) {
            mapa.setView(primerMarcador.getLatLng(), 15);
            primerMarcador.openPopup();
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            const mapaContenedor = document.getElementById('mapa');
        
            if (mapaContenedor) {
                var latInicial = -27.45;
                var lngInicial = -58.98;
                var zoomInicial = 13;
        
                var mapa = L.map('mapa').setView([latInicial, lngInicial], zoomInicial);
        
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; OpenStreetMap contributors'
                }).addTo(mapa);
            }
        
            const notificacion = document.getElementById('notificacion');
        
            if (notificacion) {
                setTimeout(() => {
                    notificacion.style.animation = "desaparecer 0.5s ease-out forwards";
        
                    setTimeout(() => {
                        notificacion.remove();
                    }, 500);
                }, 3500);
            }
        });
        


// iniciar mini-mapa
// Iniciar mini-mapa
const miniMapa = L.map('mini-mapa').setView([-27.4581, -58.9756], 13); // Centro en Chaco, ajustable

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(miniMapa);

let marcadorMini = null;

miniMapa.on('click', function(e) {
    const { lat, lng } = e.latlng;

    // Si ya había un marcador, moverlo
    if (marcadorMini) {
        marcadorMini.setLatLng([lat, lng]);
    } else {
        marcadorMini = L.marker([lat, lng]).addTo(miniMapa);
    }

    // Guardar lat y lng en los inputs ocultos
    document.getElementById('lat').value = lat;
    document.getElementById('lng').value = lng;
});
