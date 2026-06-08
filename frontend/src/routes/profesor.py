from flask import Blueprint, render_template, request, redirect, flash, url_for


profesor_bp = Blueprint('profesor', __name__)

@profesor_bp.route('/asistencia', methods = ['GET'])
def asistencia():
    return render_template('profesor-asistencia.html')
