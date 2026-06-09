from flask import Blueprint, render_template, request, redirect, flash, url_for


alumno_bp = Blueprint('alumno', __name__)

@alumno_bp.route('/inicio', methods = ['GET'])
def inicio():
    return render_template('alumno-inicio.html')
