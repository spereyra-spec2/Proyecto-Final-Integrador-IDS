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

// Exportar funciones para uso global
window.abrirModal = abrirModal;
window.cerrarModal = cerrarModal;