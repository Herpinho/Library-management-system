import psycopg2
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
from model import User
import os
from shared_utils.utils import get_db_connection, admin_check

user_blueprint = Blueprint('user_blueprint', __name__)
@user_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    password_hash = generate_password_hash(data['password'])
    role = data.get('role') if data.get('role') else 'member'

    link = None
    try:
        link = get_db_connection()
        cursor = link.cursor()
        cursor.execute(
        'INSERT INTO users (username,email,password_hash,role) VALUES (%s, %s, %s, %s) RETURNING user_id,created_at',
        (data['username'],data['email'], password_hash, role)
        )
        result = cursor.fetchone()
        new_user_id = result[0]
        db_creation = result[1]
        link.commit()
        cursor.close()
        new_user = User(new_user_id, data['username'], data['email'], role, db_creation)
        return jsonify({"message": "User successfully created", "user": new_user.to_json()}), 201
    except psycopg2.IntegrityError:
        return jsonify({"error" : "Username or email already in use."}),409
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        if link: link.close()

@user_blueprint.route('/login', methods = ['POST'])
def login():
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify ({"error": "Fill all fields"}),400
    link = None
    try:
        link = get_db_connection()
        cursor = link.cursor()
        cursor.execute('SELECT user_id, username, email, password_hash , role, created_at FROM users WHERE username = %s', (data['username'],))
        row = cursor.fetchone()
        cursor.close()
        if row: 
            if check_password_hash(row[3],data['password']):
                return jsonify({"message":"Logged in!", "ID": row[0], "Password": row[3]}),200
            return jsonify({"error":"Wrong name or password"}),250
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        link.close()

@user_blueprint.route('/<int:id>', methods=['GET'])
def get_user(id):
    user_id_header = request.headers.get('User-ID')
    if user_id_header and int(user_id_header) == id:
        pass
    else:
        if check := admin_check(user_id=user_id_header,password_hash=request.headers.get('Password_Hash')): return check
    link = get_db_connection()
    cursor = link.cursor()
    cursor.execute('SELECT user_id, username, email, role,created_at FROM users WHERE user_id = %s', (id,))
    row = cursor.fetchone()
    cursor.close()
    link.close()
    if row:
        user = User(row[0],row[1],row[2],row[3],row[4])
        return jsonify(user.to_json())
    return jsonify({"error": "User does not exist."}), 404

@user_blueprint.route('/<int:id>', methods = ['DELETE'])
def delete_user(id):
    if check := admin_check(user_id=request.headers.get('User-ID'), password_hash=request.headers.get('Password-Hash')): return check
    link = get_db_connection()
    cursor = link.cursor()
    try:   
        cursor.execute('SELECT user_id FROM users WHERE user_id = %s', (id,))
        if cursor.fetchone() is None:
            return jsonify({"error":"user_id was not found."}),404
        cursor.execute('DELETE FROM users WHERE user_id = %s', (id,))
        link.commit()
        return jsonify({"message":f"user {id} successfully removed"}),200
    except Exception as e:
        link.rollback()
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()

@user_blueprint.route('/', methods = ['GET'])
def get_all_users():
    if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check
    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute('SELECT user_id, username, email, role, created_at FROM users')
        rows = cursor.fetchall()
        users = [User(row[0],row[1],row[2],row[3],row[4]).to_json() for row in rows]
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()

@user_blueprint.route('/', methods = ['PUT'])
def modify_user():
    if check := admin_check(user_id=request.headers.get('User-ID'), password_hash=request.headers.get('Password-Hash')): return check
    link = get_db_connection()
    cursor = link.cursor()
    data = request.json
    user_id = data['user_id']
    try:
        cursor.execute('SELECT * FROM users WHERE user_id = %s',(user_id,))
        user_data = cursor.fetchone()
        if not user_data:
            return jsonify({"error": "User not found"}), 404
        
        cursor.execute('UPDATE users SET username = %s, email = %s, password_hash = %s, role = %s WHERE user_id = %s', 
            (data.get('new_username') or user_data[1],
             data.get('new_email') or user_data[2],
             generate_password_hash(data['new_password']) if data.get('new_password') else user_data[3],
             data.get('new_role') or user_data[4],
             user_id))
        link.commit()
        return jsonify({"message": "User updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        link.close()