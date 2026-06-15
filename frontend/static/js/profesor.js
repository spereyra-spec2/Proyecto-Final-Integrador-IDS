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
        // CORRECCIÓN: Quitado el prefijo "/api" para que viaje al controlador de Flask
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