import requests ##this library is holding the whole project together do not remove.
import os
import psycopg2
from flask import request,jsonify

USER_SERVICE_URL = "http://127.0.0.1:5001/users/"

def admin_check(user_id,password_hash):
    if user_id:
        pass
    else:
        user_id = request.headers.get('User-ID')
    if password_hash:
        pass
    else:
        password_hash = request.headers.get('Password-Hash')
    try:
        link = get_db_connection("user")
        cursor = link.cursor()
        cursor.execute('SELECT role,password_hash FROM users WHERE user_id = %s', (user_id,))
        row = cursor.fetchone()
        cursor.close()
        link.close()

        if row and row[0] == 'admin' and password_hash == row[1]:
            return None
        return jsonify({"error": "Unauthorized: Admin access required"}), 403
    except Exception as e:
        return jsonify({"error": f"{e}"})


def get_db_connection(db_name):
    db_host = os.environ.get('DB_HOST', 'localhost')
    return psycopg2.connect(
        host= db_host,
        database = f"library_{db_name}_db",
        user = "postgres",
        password = "1234",
        port = "5433"
    )