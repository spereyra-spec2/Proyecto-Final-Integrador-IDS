from flask import Flask, Blueprint, jsonify, request
from Asistencia_db import get_asistencia_id, get_asistencia
from mysql.connector import Error

asistencia_bp = Blueprint("asistencia",__name__)

@asistencia_bp.route('', methods=['GET'])
def asistencia():

    try:
        asistencia = get_asistencia()
        if len(asistencia) == 0:
            return jsonify("insertar mensaje codigo 204"), 204
        
        return jsonify(asistencia),200
    
    except Error as e:
        error_payload= "insertar mensaje codigo 500"

        return jsonify(error_payload),500
    

@asistencia_bp.route('/<int:id>', methods=['GET'])
def asistencia_id(id):

    try:
        #funcion de validación de este id!!!

        asistencia = get_asistencia_id(id)
        if len(asistencia) == 0:
            return jsonify("insertar mensaje codigo 204"),204
        
        return jsonify(asistencia),200
    
    except Error as e:
        error_payload= "insertar mensaje codigo 500"

        return jsonify(error_payload),500
    