/**
 * evaluaciones.js - Lógica para la página de evaluaciones
 */

// Funciones para el modal
function abrirModal() {
  const modal = document.getElementById('modal-eval');
  if (modal) {
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
  }
}

function cerrarModal() {
  const modal = document.getElementById('modal-eval');
  if (modal) {
    modal.classList.remove('show');
    document.body.style.overflow = '';
  }
}

function mostrarMensaje(mensaje, tipo) {
  const container = document.getElementById('mensajes-container');
  if (container) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${tipo}`;
    alertDiv.textContent = mensaje;
    container.appendChild(alertDiv);
    setTimeout(() => {
      alertDiv.remove();
    }, 5000);
  }
}
function abrirModalEditarPorId(id) {
  // Usar fetch para obtener los datos
  fetch(`/evaluaciones/api/evaluaciones/${id}`)
    .then(response => response.json())
    .then(evaluacion => {
      document.getElementById('edit_id').value = evaluacion.idEvaluacion;
      document.getElementById('edit_tipo').value = evaluacion.tipo || '';
      document.getElementById('edit_descripcion').value = evaluacion.descripcion || '';
      
      if (evaluacion.fecha) {
        let date = new Date(evaluacion.fecha);
        if (!isNaN(date.getTime())) {
          let formattedDate = date.toISOString().slice(0, 16);
          document.getElementById('edit_fecha').value = formattedDate;
        }
      }
      
      document.getElementById('edit_curso_id').value = evaluacion.Curso_idCurso || '';
      document.getElementById('form-editar-evaluacion').action = `/evaluaciones/actualizar/${id}`;
      
      const modal = document.getElementById('modal-editar-eval');
      if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Error al cargar los datos de la evaluación');
    });
}

function cerrarModalEditar() {
    const modal = document.getElementById('modal-editar-eval');
    if (modal) {
      modal.classList.remove('show');
      document.body.style.overflow = '';
      // Limpiar formulario
      document.getElementById('edit_id').value = '';
      document.getElementById('edit_tipo').value = '';
      document.getElementById('edit_descripcion').value = '';
      document.getElementById('edit_fecha').value = '';
      document.getElementById('edit_curso_id').value = '';
    }
}

// Exportar funciones para uso global
window.abrirModal = abrirModal;
window.cerrarModal = cerrarModal;