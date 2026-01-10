import requests ##this library is holding the whole project together do not remove.
import os
import psycopg2
from flask import request,jsonify


def admin_check(user_id,password_hash):
    return None
    """if user_id:
        pass
    else:
        user_id = request.headers.get('User-ID')
    if password_hash:
        pass
    else:
        password_hash = request.headers.get('Password-Hash')
    try:
        link = get_db_connection()
        cursor = link.cursor()
        cursor.execute('SELECT role,password_hash FROM users WHERE user_id = %s', (user_id,))
        row = cursor.fetchone()
        cursor.close()
        link.close()

        if row and row[0] == 'admin' and password_hash == row[1]:
            return None
        return jsonify({"error": "Unauthorized: Admin access required"}), 403
    except Exception as e:
        return jsonify({"error": f"{e}"})"""


def get_db_connection():
    host = os.environ.get('DB_HOST') 
    port = os.environ.get('DB_PORT', '5432')
    password = os.environ.get('DB_PASSWORD')
    user = os.environ.get('DB_USER')
    db_name = os.environ.get('DB_NAME')
    
    return psycopg2.connect(
        host=host,
        database=db_name,
        user=user,
        password=password,
        port=port
    )