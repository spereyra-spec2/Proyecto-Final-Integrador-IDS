// GESTIÓN DEL DISEÑO, MENÚ LATERAL Y USUARIO (LOCALSTORAGE)

document.addEventListener('DOMContentLoaded', () => {
    const hamburgerBtn = document.querySelector('.hamburger');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');

    if (hamburgerBtn && sidebar && overlay) {
        hamburgerBtn.addEventListener('click', () => {
            sidebar.classList.add('active');
            overlay.classList.add('active');
        });

        overlay.addEventListener('click', () => {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        });
    }

    const userNameElement = document.getElementById('user-name');
    const userAvatarElement = document.getElementById('user-avatar');

    if (userNameElement && userAvatarElement) {
        const storedName = localStorage.getItem('profesor_name') || 'Profesor';
        userNameElement.textContent = storedName;
        userAvatarElement.textContent = storedName.charAt(0).toUpperCase();
    }
});

// CONTROLES DE VENTANAS MODALES GLOBALES

window.openModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
};

window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
        
        // Si cerramos el modal de estudiantes, rehabilitamos el campo padrón
        const padronInput = document.getElementById('s-padron');
        if (padronInput) {
            padronInput.disabled = false;
        }
    }
};

// GESTIÓN DE CURSOS (Para profesor-cursos.html)

window.abrirModalActualizar = function(idCurso, nombre, codigo, cuatrimestre, descripcion) {
    const formulario = document.getElementById('form-actualizar-modal');
    if (formulario) {
        // CORRECCIÓN: Apuntar a la ruta de Flask del Frontend en lugar de la API directa del puerto 5000
        formulario.action = "/profesor/cursos/actualizar/" + idCurso;
        
        document.getElementById('u-nombre').value = nombre;
        document.getElementById('u-codigo').value = codigo;
        document.getElementById('u-cuatri').value = cuatrimestre;
        document.getElementById('u-desc').value = descripcion;
        
        window.openModal('modal-update');
    }
};

// GESTIÓN DE ALUMNOS (Para profesor-alumnos.html)

window.configurarModalAlta = function(idCurso) {
    const formulario = document.getElementById('form-alumno-modal');
    if (formulario) {
        // CORRECCIÓN: Quitado el prefijo "/api" para que viaje al controlador de Flask
        formulario.action = "/profesor/cursos/" + idCurso + "/alumnos/inscribir";
        formulario.reset();
        
        document.getElementById('s-padron').disabled = false;
        
        const estadoGroup = document.getElementById('s-estado-group');
        if (estadoGroup) estadoGroup.style.display = 'none';
        
        document.getElementById('modal-student-title').innerText = "Nuevo alumno";
        
        window.openModal('modal-student');
    }
};

window.configurarModalEditar = function(padron, nombres, mail, Estado, idCurso) {
    const formulario = document.getElementById('form-alumno-modal');
    if (formulario) {

        formulario.action = "/profesor/cursos/" + idCurso + "/alumnos/actualizar/" + padron;
        
        document.getElementById('s-nombre').value = nombres;
        document.getElementById('s-padron').value = padron;
        document.getElementById('s-padron').disabled = true; 
        
        const selectEstado = document.getElementById('s-estado');
        if (selectEstado) selectEstado.disabled = true;
        
        const estadoGroup = document.getElementById('s-estado-group');
        if (estadoGroup) estadoGroup.style.display = 'none';
        
        document.getElementById('modal-student-title').innerText = "✏️ Editar Alumno";
        
        window.openModal('modal-student');
    }
};


document.addEventListener('DOMContentLoaded', function() {
  const modalPdf = document.getElementById('modal-exportar-pdf');
  const inputCursoId = document.getElementById('modal-curso-id');
  const modalTitle = modalPdf ? modalPdf.querySelector('.modal-title') : null;

  document.addEventListener('click', function(e) {
    const isDropdownButton = e.target.closest('.dropdown-toggle-btn');
    
    if (isDropdownButton) {
      e.preventDefault();
      const currentMenu = isDropdownButton.nextElementSibling;
      currentMenu.classList.toggle('show');

      document.querySelectorAll('.dropdown-menu-custom').forEach(menu => {
        if (menu !== currentMenu) menu.classList.remove('show');
      });
    } else if (!e.target.closest('.custom-dropdown')) {
      document.querySelectorAll('.dropdown-menu-custom').forEach(menu => {
        menu.classList.remove('show');
      });
    }
  });

  document.addEventListener('click', function(e) {
    const itemCurso = e.target.closest('.btn-abrir-modal-curso');
    if (itemCurso) {
      e.preventDefault();
      const idCurso = itemCurso.getAttribute('data-id');
      const nombreCurso = itemCurso.getAttribute('data-nombre');

      if (inputCursoId) inputCursoId.value = idCurso;
      if (modalTitle) modalTitle.innerHTML = `📄 PDF — ${nombreCurso}`;
      if (modalPdf) modalPdf.classList.remove('hidden');
      
      document.querySelectorAll('.dropdown-menu-custom').forEach(menu => {
        menu.classList.remove('show');
      });
    }
  });

  function ocultarModalPdf() {
    if (modalPdf) modalPdf.classList.add('hidden');
  }

  const btnCerrar = document.getElementById('btn-cerrar-modal-pdf');
  const btnCancelar = document.getElementById('btn-cancelar-modal-pdf');
  
  if (btnCerrar) btnCerrar.addEventListener('click', ocultarModalPdf);
  if (btnCancelar) btnCancelar.addEventListener('click', ocultarModalPdf);
  
  if (modalPdf) {
    modalPdf.addEventListener('click', function(e) {
      if (e.target === modalPdf) ocultarModalPdf();
    });
  }

  const btnDescargar = document.getElementById('btn-confirmar-descarga-pdf');
  if (btnDescargar) {
    btnDescargar.addEventListener('click', function() {
      const idCurso = inputCursoId.value;
      const ordenarPor = document.getElementById('select-ordenar').value;
      const filtrarActivos = document.getElementById('select-filtrar').value;

      if (!idCurso) return;

      window.location.href = `/profesor/curso/${idCurso}/exportar_alumnos_pdf?ordenar_por=${ordenarPor}&filtrar_activos=${filtrarActivos}`;
      ocultarModalPdf();
    });
  }
});

document.addEventListener('click', function(e) {
    const item_reporte = e.target.closest('.descargar-reporte-directo');
    if (item_reporte) {
        e.preventDefault();
        const id_curso = item_reporte.getAttribute('data-id');
        
        if (id_curso) {
            window.location.href = `/api/cursos/${id_curso}/reporte-estadisticas`;
        }
        
        document.querySelectorAll('.dropdown-menu-custom').forEach(menu => {
            menu.classList.remove('show');
        });
    }
});

document.addEventListener('click', function(e) {
    const item_reporte = e.target.closest('.descargar-reporte-directo');
    if (item_reporte) {
        e.preventDefault();
        const id_curso = item_reporte.getAttribute('data-id');
        
        if (id_curso) {
        window.location.href = '/api/cursos/${id_curso}/reporte-estadisticas';
        }
        
        document.querySelectorAll('.dropdown-menu-custom').forEach(menu => {
            menu.classList.remove('show');
        });
    }
});

document.addEventListener('click', function(e) {
    const itemCursoEquipos = e.target.closest('.btn-abrir-modal-equipos');
    if (itemCursoEquipos) {
        e.preventDefault();
        const idCurso = itemCursoEquipos.getAttribute('data-id');
        const nombreCurso = itemCursoEquipos.getAttribute('data-nombre');

        const modalEquiposPdf = document.getElementById('modal-exportar-equipos-pdf');
        const inputEquiposCursoId = document.getElementById('modal-equipos-curso-id');
        const modalEquiposTitle = modalEquiposPdf ? modalEquiposPdf.querySelector('.modal-title') : null;

        if (inputEquiposCursoId) inputEquiposCursoId.value = idCurso;
        if (modalEquiposTitle) modalEquiposTitle.innerHTML = `🤝 PDF Equipos — ${nombreCurso}`;
        if (modalEquiposPdf) modalEquiposPdf.classList.remove('hidden');
        
        document.querySelectorAll('.dropdown-menu-custom').forEach(menu => {
            menu.classList.remove('show');
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const modalEquiposPdf = document.getElementById('modal-exportar-equipos-pdf');
    
    function ocultarModalEquiposPdf() {
        if (modalEquiposPdf) modalEquiposPdf.classList.add('hidden');
    }
    
    const btnCerrarEquipos = document.getElementById('btn-cerrar-modal-equipos-pdf');
    const btnCancelarEquipos = document.getElementById('btn-cancelar-modal-equipos-pdf');
    
    if (btnCerrarEquipos) btnCerrarEquipos.addEventListener('click', ocultarModalEquiposPdf);
    if (btnCancelarEquipos) btnCancelarEquipos.addEventListener('click', ocultarModalEquiposPdf);
    
    if (modalEquiposPdf) {
        modalEquiposPdf.addEventListener('click', function(e) {
            if (e.target === modalEquiposPdf) ocultarModalEquiposPdf();
        });
    }

    const btnDescargarEquipos = document.getElementById('btn-confirmar-descarga-equipos-pdf');
    if (btnDescargarEquipos) {
        btnDescargarEquipos.addEventListener('click', function() {
            const inputEquiposCursoId = document.getElementById('modal-equipos-curso-id');
            const idCurso = inputEquiposCursoId ? inputEquiposCursoId.value : null;
            const sinEquipo = document.getElementById('select-incluir-sin-equipo').value;

            if (!idCurso) return;

            window.location.href = `/profesor/curso/${idCurso}/exportar_equipos_pdf?sin_equipo=${sinEquipo}`;
            ocultarModalEquiposPdf();
        });
    }
});