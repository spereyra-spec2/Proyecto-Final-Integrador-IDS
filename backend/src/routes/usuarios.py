from os import close
from flask import Blueprint, jsonify, request, url_for
from db import get_connection
import mysql.connector

usuarios_bp = Blueprint("usuarios", __name__)

@usuarios_bp.route("", methods=["GET"])
def get_usuarios(): 
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(usuarios), 200
