// Esperamos a que todo el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    
    // 1. VALIDACIÓN EN CALIENTE PARA CARGAR Y EDITAR NOTAS
    // Evita que el usuario intente escribir notas fuera del rango tradicional (ej: -5 o 45)
    const inputsPuntaje = document.querySelectorAll('input[name="puntaje"]');
    
    inputsPuntaje.forEach(input => {
        input.addEventListener('input', function() {
            const valor = parseFloat(this.value);
            if (valor < 0) this.value = 0;
            if (valor > 10) this.value = 10;
        });
    });

    // 2. CONFIRMACIÓN ANTES DE EDITAR (Pura UX de seguridad)
    // Captura el envío del formulario de edición y pide una doble confirmación
    const formEditar = document.querySelector('form[action="/notas/actualizar"]');
    if (formEditar) {
        formEditar.addEventListener('submit', function(event) {
            const nuevaNota = document.getElementById('edit_puntaje')?.value || this.querySelector('input[name="puntaje"]').value;
            
            const confirmar = confirm(`¿Estás seguro de que deseas cambiar la calificación a: ${nuevaNota}?`);
            
            if (!confirmar) {
                // Si el docente presiona 'Cancelar', frenamos el envío del formulario tradicional
                event.preventDefault(); 
            }
        });
    }
});