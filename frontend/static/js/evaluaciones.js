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
  function abrirModalEditar(id, tipo, descripcion, fecha) {
    // Limpiar campos primero
    document.getElementById('edit_id').value = '';
    document.getElementById('edit_tipo').value = '';
    document.getElementById('edit_descripcion').value = '';
    document.getElementById('edit_fecha').value = '';
    
    // Llenar el formulario con los datos actuales
    document.getElementById('edit_id').value = id;
    document.getElementById('edit_tipo').value = tipo || '';
    document.getElementById('edit_descripcion').value = descripcion || '';
    
    // Formatear fecha para datetime-local
    if (fecha) {
      let date = new Date(fecha);
      if (!isNaN(date.getTime())) {
        let formattedDate = date.toISOString().slice(0, 16);
        document.getElementById('edit_fecha').value = formattedDate;
      }
    }
    
    // Configurar la acción del formulario
    const cursoId = {{ curso_id }};
    document.getElementById('form-editar-evaluacion').action = `/profesor/cursos/${cursoId}/evaluaciones/actualizar/${id}`;
    
    // Abrir el modal
    const modal = document.getElementById('modal-editar-eval');
    if (modal) {
      modal.classList.add('show');
      document.body.style.overflow = 'hidden';
    }
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