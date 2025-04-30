// flash_revisar.js

// Este script se encarga de hacer desaparecer los mensajes flash después de unos segundos
setTimeout(() => {
    const flashes = document.querySelectorAll('.flash-message');
    flashes.forEach(flash => {
        flash.style.display = 'none';
    });
}, 2000);

document.querySelectorAll('.botones-acciones form').forEach(form => {
    form.addEventListener('submit', function (e) {
        const tarjeta = this.closest('.tarjeta-lugar');
        if (tarjeta) {
            tarjeta.classList.add('fade-out');
        }
    });
});
// Modo oscuro toggle con memoria
const botonModoOscuro = document.getElementById('btn-modo-oscuro');

// Al cargar la página, aplicamos la preferencia guardada
if (localStorage.getItem('modo-oscuro') === 'true') {
    document.body.classList.add('modo-oscuro');
    if (botonModoOscuro) botonModoOscuro.innerText = "☀️ Modo claro";
}

if (botonModoOscuro) {
    botonModoOscuro.addEventListener('click', () => {
        document.body.classList.toggle('modo-oscuro');
        const modoOscuroActivo = document.body.classList.contains('modo-oscuro');
        
        // Guardar en localStorage
        localStorage.setItem('modo-oscuro', modoOscuroActivo);

        // Cambiar texto del botón
        botonModoOscuro.innerText = modoOscuroActivo ? "☀️ Modo claro" : "🌙 Modo oscuro";
    });
}
// Confirmar aprobar o rechazar
document.querySelectorAll('.btn-aprobar').forEach(btn => {
    btn.addEventListener('click', function (e) {
        if (!confirm('✅ ¿Estás seguro de aprobar este lugar?')) {
            e.preventDefault();
        }
    });
});

document.querySelectorAll('.btn-rechazar').forEach(btn => {
    btn.addEventListener('click', function (e) {
        if (!confirm('❌ ¿Estás seguro de rechazar este lugar?')) {
            e.preventDefault();
        }
    });
});


