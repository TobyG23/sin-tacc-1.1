
document.addEventListener('DOMContentLoaded', function () {
    const mapa = L.map('map');

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                mapa.setView([lat, lng], 15);
            },
            function () {
                mapa.setView([-27.4581, -58.9756], 13);
            }
        );
    } else {
        mapa.setView([-27.4581, -58.9756], 13);
    }

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(mapa);

    console.log(lugares);
    let primerMarcador = null;
    const grupoCluster = L.markerClusterGroup();

    lugares.forEach(lugar => {
        if (lugar.lat !== null && lugar.lng !== null) {
            const popup = `
                <div class="popup-contenedor">
                    <strong class="popup-titulo">${lugar.nombre}</strong><br>
                    <span class="popup-direccion">${lugar.direccion}, ${lugar.ciudad}, ${lugar.provincia}</span><br>
                    <em class="popup-tipo">${lugar.tipo}</em><br>
                    ⭐ <strong>${lugar.promedio} / 5</strong><br>
                    <a href="/lugar/${lugar.id}" class="popup-boton">📝 Ver o dejar review</a><br><br>
                    <a href="https://www.google.com/maps/search/?api=1&query=${lugar.lat},${lugar.lng}" 
                        target="_blank" 
                        class="popup-boton pulse">
                            🌍 Ir con Google Maps
                    </a>
                </div>
            `;

            const icono = L.icon({
                iconUrl: lugar.promedio >= 4.5 ? '/static/img/sin_gluten_oro.png' : '/static/img/sin_gluten_legal-01.png',
                iconSize: [48, 48],
                iconAnchor: [24, 48],
                popupAnchor: [0, -48]
            });

            const marker = L.marker([lugar.lat, lugar.lng], { icon: icono }).bindPopup(popup);
            grupoCluster.addLayer(marker);
        }
    });

    mapa.addLayer(grupoCluster);

    if (primerMarcador) {
        mapa.setView(primerMarcador.getLatLng(), 15);
        primerMarcador.openPopup();
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

    // mini mapa
    const miniMapa = L.map('mini-mapa').setView([-27.4581, -58.9756], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(miniMapa);

    let marcadorMini = null;
    miniMapa.on('click', function(e) {
        const { lat, lng } = e.latlng;
        if (marcadorMini) {
            marcadorMini.setLatLng([lat, lng]);
        } else {
            marcadorMini = L.marker([lat, lng]).addTo(miniMapa);
        }
        document.getElementById('lat').value = lat;
        document.getElementById('lng').value = lng;
    });
});
