from flask import Blueprint, render_template, request, redirect, flash, url_for


profesor_bp = Blueprint('profesor', __name__)

@profesor_bp.route('/dashboard', methods = ['GET'])
def dashboard():
    return render_template('profesor-dashboard.html')
