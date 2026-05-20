import mysql.connector
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config


def _get_connection():
    return mysql.connector.connect(
        host=config.host,
        user=config.user,
        password=config.password,
        database=config.database
    )


def get_equipo(grupo_id):
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)


def put_equipo(grupo_id, data):
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)



def delete_equipo(grupo_id):
    conn = _get_connection()
    cursor = conn.cursor()