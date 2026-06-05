

document.addEventListener('DOMContentLoaded', function() {
    
    const inputsPuntaje = document.querySelectorAll('input[name="puntaje"]');
    
    inputsPuntaje.forEach(input => {
        input.addEventListener('input', function() {
            const valor = parseFloat(this.value);
            if (valor < 0) this.value = 0;
            if (valor > 10) this.value = 10;
        });
    });

    const formEditar = document.querySelector('form[action="/notas/actualizar"]');
    if (formEditar) {
        formEditar.addEventListener('submit', function(event) {
            const nuevaNota = document.getElementById('edit_puntaje')?.value || this.querySelector('input[name="puntaje"]').value;
            
            const confirmar = confirm(`¿Estás seguro de que deseas cambiar la calificación a: ${nuevaNota}?`);
            
            if (!confirmar) {
                event.preventDefault(); 
            }
        });
    }
});