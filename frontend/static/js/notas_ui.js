

document.addEventListener('DOMContentLoaded', function() {
    
    const inputs_de_puntaje = document.querySelectorAll('input[name="nota"]');
    
    inputs_de_puntaje.forEach(input => {
        input.addEventListener('input', function() {
            const valor = parseFloat(this.value);
            if (valor < 0) this.value = 0;
            if (valor > 10) this.value = 10;
        });
    });

    const form_editar = document.querySelector('form[action="/notas/editar"]');
    if (form_editar) {
        form_editar.addEventListener('submit', function(event) {
            
            const nueva_nota = this.querySelector('input[name="nota"]').value;
            
            const confirmacion = confirm(`¿Estás seguro de que deseas cambiar la nota a: ${nueva_nota}?`);
            
            if (!confirmacion) {
                event.preventDefault();
            }
        });
    }
});