/**
 * evaluaciones.js - Lógica para la página de evaluaciones
 */

document.addEventListener('DOMContentLoaded', function() {
    // Manejar los botones de editar
    document.querySelectorAll('.edit-button').forEach(button => {
        button.addEventListener('click', function() {
            const id = this.dataset.id;
            const tipo = this.dataset.tipo;
            const descripcion = this.dataset.descripcion;
            const fecha = this.dataset.fecha;
            
            abrirModalEditar(id, tipo, descripcion, fecha);
        });
    });
});

function abrirModal() {
  const modal = document.getElementById('modal-eval');
  if (modal) {
    modal.classList.remove('hidden'); // Adaptado a tus clases comunes
    document.body.style.overflow = 'hidden';
  }
}

function cerrarModal() {
  const modal = document.getElementById('modal-eval');
  if (modal) {
    modal.classList.add('hidden'); // Adaptado a tus clases comunes
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
    
    // SOLUCIÓN EXTRA: Extraer el cursoId de forma segura directamente desde la URL actual
    // Ejemplo de URL: /cursos/12/evaluaciones -> extrae el número 12
    const pathParts = window.location.pathname.split('/');
    const cursosIndex = pathParts.indexOf('cursos');
    const cursoId = (cursosIndex !== -1 && pathParts[cursosIndex + 1]) ? pathParts[cursosIndex + 1] : '0';
    
    // Configurar la acción del formulario dinámicamente con la ruta correcta
    document.getElementById('form-editar-evaluacion').action = `/profesor/cursos/${cursoId}/evaluaciones/actualizar/${id}`;
    
    // Abrir el modal usando tu clase hidden
    const modal = document.getElementById('modal-editar-eval');
    if (modal) {
      modal.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
    }
}

function cerrarModalEditar() {
    const modal = document.getElementById('modal-editar-eval');
    if (modal) {
      modal.classList.add('hidden');
      document.body.style.overflow = '';
      
      // Limpiar formulario de forma segura evitando romper si no existe edit_curso_id
      document.getElementById('edit_id').value = '';
      document.getElementById('edit_tipo').value = '';
      document.getElementById('edit_descripcion').value = '';
      document.getElementById('edit_fecha').value = '';
      
      const cursoIdInput = document.getElementById('edit_curso_id');
      if (cursoIdInput) {
        cursoIdInput.value = '';
      }
    }
}

// Exportar funciones para uso global en los botones inline del HTML
window.abrirModal = abrirModal;
window.cerrarModal = cerrarModal;
window.cerrarModalEditar = cerrarModalEditar;