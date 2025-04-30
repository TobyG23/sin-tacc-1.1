document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const btnMapa = document.getElementById('activar-mapa');
    const grupoCampos = document.getElementById('grupo-campos');
    const grupoMapa = document.getElementById('grupo-mapa');

    const inputNombre = document.getElementById('nombre');
    const inputDireccion = document.getElementById('direccion');
    const inputCiudad = document.getElementById('ciudad');
    const inputProvincia = document.getElementById('provincia');
    const inputPais = document.getElementById('pais');
    const inputTipo = document.getElementById('tipo');
    const inputComentarios = document.getElementById('comentarios');

    const inputNombreMapa = document.getElementById('nombre-mapa');
    const inputTipoMapa = document.getElementById('tipo-mapa');
    const inputComentariosMapa = document.getElementById('comentarios-mapa');

    // 🚀 CORREGIR REQUIRED INICIAL:
    inputNombreMapa.removeAttribute('required');
    inputTipoMapa.removeAttribute('required');

    let usandoMapa = false;
    let miniMapa = null;
    let marcadorMini = null;

    btnMapa.addEventListener('click', function () {
        usandoMapa = !usandoMapa;
    
        if (usandoMapa) {
            grupoCampos.style.display = 'none';
            grupoMapa.style.display = 'block';
            btnMapa.innerText = "✏️ Volver a escribir dirección manualmente";
            
            // QUITAR required a campos manuales
            inputNombre.removeAttribute('required');
            inputDireccion.removeAttribute('required');
            inputCiudad.removeAttribute('required');
            inputProvincia.removeAttribute('required');
            inputPais.removeAttribute('required');
            inputTipo.removeAttribute('required');

            // ✅ Poner required en los campos del mini-mapa
            inputNombreMapa.setAttribute('required', 'true');
            inputTipoMapa.setAttribute('required', 'true');
    
            // Crear el mini-mapa si aún no existe
            if (!miniMapa) {
                miniMapa = L.map('mini-mapa').setView([-27.4581, -58.9756], 13);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; OpenStreetMap contributors'
                }).addTo(miniMapa);
    
                miniMapa.on('click', function (e) {
                    const { lat, lng } = e.latlng;
                    if (marcadorMini) {
                        marcadorMini.setLatLng([lat, lng]);
                    } else {
                        marcadorMini = L.marker([lat, lng]).addTo(miniMapa);
                    }
                    document.getElementById('lat').value = lat;
                    document.getElementById('lng').value = lng;
                    // Mostrar coordenadas en el HTML
                    const coordTexto = document.getElementById('coordenadas-mapa');
                    if (coordTexto) {
                        coordTexto.textContent = `📍 Coordenadas seleccionadas: Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)}`;
}

                });
            }
    
            setTimeout(() => {
                miniMapa.invalidateSize();
            }, 300);
        } else {
            grupoCampos.style.display = 'block';
            grupoMapa.style.display = 'none';
            btnMapa.innerText = "📍 No encuentro dirección — Ubicar en mapa";

            // Volver a poner required
            inputNombre.setAttribute('required', 'true');
            inputDireccion.setAttribute('required', 'true');
            inputCiudad.setAttribute('required', 'true');
            inputProvincia.setAttribute('required', 'true');
            inputPais.setAttribute('required', 'true');
            inputTipo.setAttribute('required', 'true');

            // ⚡ Sacar required de los campos del mini-mapa
            inputNombreMapa.removeAttribute('required');
            inputTipoMapa.removeAttribute('required');
        }
    });

    form.addEventListener('submit', function (e) {

        if (usandoMapa) {
            if (inputNombreMapa) inputNombreMapa.value = inputNombreMapa.value.trim();
            if (inputTipoMapa) inputTipoMapa.value = inputTipoMapa.value.trim();
            if (inputComentariosMapa) inputComentariosMapa.value = inputComentariosMapa.value.trim();
        }
        const botonEnviar = document.querySelector('.btn-enviar');
        if (botonEnviar) {
            botonEnviar.disabled = true;
            botonEnviar.innerHTML = "⏳ Enviando...";
        }

    });

    // Cargar países
    fetch('https://restcountries.com/v3.1/all')
    .then(response => response.json())
    .then(paises => {
        const selectPais = document.getElementById('pais');
        if (!selectPais) return;

        paises.sort((a, b) => a.name.common.localeCompare(b.name.common));

        paises.forEach(pais => {
            const opcion = document.createElement('option');
            opcion.value = pais.name.common;
            opcion.textContent = pais.name.common;
            selectPais.appendChild(opcion);
        });

        selectPais.value = "Argentina"; // Default
    })
    .catch(error => console.error('Error cargando países:', error));
});
