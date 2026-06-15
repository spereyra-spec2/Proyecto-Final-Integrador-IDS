/**
 * alumno-inicio.js - Manejo local del portal del alumno
 */
document.addEventListener('DOMContentLoaded', function() {
    const sel = document.getElementById('curso-select');
    const inputPadron = document.getElementById('padron-input');

    // Recuperar datos guardados si existen
    const savedCurso = localStorage.getItem('alumno_curso');
    if (savedCurso && sel) {
        sel.value = savedCurso;
    }
    const savedPadron = localStorage.getItem('alumno_padron');
    if (savedPadron && inputPadron) {
        inputPadron.value = savedPadron;
    }
});

// Función global de búsqueda llamada por el botón
window.buscar = function() {
    const padron = document.getElementById('padron-input').value.trim();
    const curso  = document.getElementById('curso-select').value;
    
    if (!padron || !curso) { 
        alert('Ingresá tu padrón y seleccioná un curso'); 
        return; 
    }
    
    // Guardar para la próxima visita
    localStorage.setItem('alumno_padron', padron);
    localStorage.setItem('alumno_curso', curso);
    
    // Redireccionar nativamente pasando los parámetros por URL limpia
    window.location.href = `/notas/alumnos/ver?padron=${padron}&curso_id=${curso}`;
};