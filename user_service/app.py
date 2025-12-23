import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, jsonify, request
from model import User
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from shared_utils import *

app = Flask(__name__)

@app.route('/users/register', methods=['POST']) #REGISTER
def register():
    data = request.json
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({"error":"Fill all fields"}), 400
    password_hash = generate_password_hash(data['password'])
    role = data.get('role') if data.get('role') else 'member'
    if role == 'admin':
            if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check 
    link = None
    try:
        link = get_db_connection(Path(__file__).parent.name.replace("_service", ""))
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
        new_user = User(new_user_id, data['username'], data['email'], password_hash, role, db_creation)
        return jsonify({"message": "User successfully created",
                        "user": new_user.to_json()}), 201
    except psycopg2.IntegrityError:
        return jsonify({"error" : "Username or email already in use."}),409
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        if link:
            link.close()
@app.route('/users/login', methods = ['POST']) #LOGIN
def login():
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify ({"error": "Fill all fields"}),400
    link = None
    try:
        link = get_db_connection(Path(__file__).parent.name.replace("_service", ""))
        cursor = link.cursor()
        cursor.execute(
            'SELECT user_id, username, email, password_hash, role, created_at FROM users WHERE username = %s', (data['username'],)
            )
        row = cursor.fetchone()
        cursor.close()
    
        if row : 
            if check_password_hash(row[3],data['password']):
                user = User(row[0], row[1], row[2], row[3], row[4], row[5])
                return jsonify ({"message":"Logged in!","user": user.to_json()}),200
        return jsonify({"error":"Wrong name or password"}),401
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        if link:
            link.close()
@app.route('/users/<int:id>', methods=['GET']) #GET INFO
def get_user(id):
    if request.headers.get('User-ID') and int(request.headers.get('User-ID')) == id: ##user id 3 can only acess its own information, admins can access everyone's.
        pass
    else:
        if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check
    link = get_db_connection(Path(__file__).parent.name.replace("_service", ""))
    cursor = link.cursor()
    cursor.execute('SELECT user_id, username, email, password_hash,role,created_at FROM users WHERE user_id = %s', (id,))
    row = cursor.fetchone()
    cursor.close()
    link.close()
    
    if row:
        user = User(row[0],row[1],row[2],row[3],row[4],row[5])
        return jsonify(user.to_json())
    return jsonify({"error": "User does not exist."}), 404
@app.route('/users/<int:id>', methods = ['DELETE']) #delete user
def delete_user(id):
    if check := admin_check(user_id=request.headers.get('User-ID'), password_hash=request.headers.get('Password-Hash')): return check
    link = get_db_connection(Path(__file__).parent.name.replace("_service",""))
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
@app.route('/users',methods = ['GET'])
def get_all_users():
    if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check    ##ADMIN COMMAND
    link = get_db_connection(Path(__file__).parent.name.replace("_service", ""))
    cursor = link.cursor()
    try:
        cursor.execute(
        '''
        SELECT
            u.user_id,
            u.username,
            u.email,
            u.role,
            u.created_at
        FROM users u
        GROUP BY u.user_id
        '''
        )
        rows = cursor.fetchall()
        users = []
        for row in rows:
            user_obj = User(row[0],row[1],row[2],row[3],row[4])
            users.append(user_obj.to_json())
        return jsonify(users);200
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()
if __name__ == "__main__":
    app.run(debug=True,port=5001)