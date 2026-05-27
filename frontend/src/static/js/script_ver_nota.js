


const individual = document.getElementById('tipo_individual');
const grupal = document.getElementById('tipo_grupal');
const padron = document.getElementById('grupo_padron');
const equipo = document.getElementById('grupo_equipo');
const input_padron = document.getElementById('input_padron');
const input_equipo = document.getElementById('input_equipo');



function alternarCampos() {
    if (individual.checked) {
        padron.style.display = 'block';
        equipo.style.display = 'none';
        
        input_padron.disabled = false;
        input_equipo.disabled = true;
    } else {
        padron.style.display = 'none';
        equipo.style.display = 'block';
        
        input_padron.disabled = true;
        input_equipo.disabled = false;
    }
}
if (individual && grupal) {
    individual.addEventListener('change', alternarCampos);
    grupal.addEventListener('change', alternarCampos);
    
    alternarCampos();
}