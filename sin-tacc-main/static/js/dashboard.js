// Confirmar antes de eliminar lugar
document.querySelectorAll('.btn-eliminar').forEach(boton => {
    boton.addEventListener('click', function (e) {
        if (!confirm('🗑️ ¿Estás seguro que querés eliminar este lugar? Esta acción no se puede deshacer.')) {
            e.preventDefault();
        }
    });
});

// Modo oscuro toggle con memoria
const botonModoOscuro = document.getElementById('btn-modo-oscuro');

// Al cargar la página, aplicamos la preferencia guardada
if (localStorage.getItem('modo-oscuro-dashboard') === 'true') {
    document.body.classList.add('modo-oscuro');
    if (botonModoOscuro) botonModoOscuro.innerText = "☀️ Modo claro";
}

if (botonModoOscuro) {
    botonModoOscuro.addEventListener('click', () => {
        document.body.classList.toggle('modo-oscuro');
        const modoOscuroActivo = document.body.classList.contains('modo-oscuro');
        
        // Guardar en localStorage
        localStorage.setItem('modo-oscuro-dashboard', modoOscuroActivo);

        // Cambiar texto del botón
        botonModoOscuro.innerText = modoOscuroActivo ? "☀️ Modo claro" : "🌙 Modo oscuro";
    });
}

