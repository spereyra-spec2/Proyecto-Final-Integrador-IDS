

function habilitar_equipo() {
    const checkbox = document.getElementById('es_grupal');
    const divEquipo = document.getElementById('grupo_equipo');
    const inputEquipo = document.getElementById('Equipos_idEquipos');

    if (checkbox.checked) {
        divEquipo.style.display = 'block';
        inputEquipo.required = true; // Se vuelve obligatorio si es grupal
    } else {
        divEquipo.style.display = 'none';
        inputEquipo.required = false;
        inputEquipo.value = null;
    }
}
