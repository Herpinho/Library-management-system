from flask import Blueprint, request, jsonify
from pathlib import Path
from datetime import datetime
import requests
import os
from shared_utils.utils import get_db_connection, admin_check
from model import Payment
catalog_service = os.getenv("CATALOG_SERVICE", "http://catalog-service:5002")
loan_service = os.getenv("LOAN_SERVICE","http://loan-service:5003")
payment_blueprint = Blueprint('payment_blueprint', __name__)

def get_payment(payment_id):
    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute(''' 
            SELECT payment_id, user_id, loan_id, amount, payment_status, transaction_id
            FROM payments 
            WHERE payment_id = %s
        ''', (payment_id,))
        row = cursor.fetchone()
        return Payment(*row) if row else None
    except Exception as e:
        raise e
    finally:
        cursor.close()
        link.close()

@payment_blueprint.route('/', methods = ['POST'])
def add_payment():
    if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')):return check
    data = request.json
    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute('''
                        INSERT INTO payments (user_id, loan_id, amount, payment_status) VALUES (%s, %s, %s, %s) RETURNING payment_id
                        ''',
                          (data['user_id'], data['loan_id'], data['amount'],'pending')
                        )
        new_id = cursor.fetchone()[0]
        link.commit()
        return jsonify({"message":"Payment created","id":new_id}),201
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()

@payment_blueprint.route('/<int:payment_id>',methods = ['GET'])    
def get_payment_json(payment_id):
    try:
        payment_obj = get_payment(payment_id)
        if payment_obj:
            if request.headers.get('User-ID') and int(request.headers.get('User-ID')) == payment_obj.user_id:
                pass
            else:
                if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check   
            return jsonify(payment_obj.to_json()),200
        return jsonify({"error":f"payment {payment_id} was not found"}),404
    except Exception as e:
        return jsonify({"error":str(e)}),500

@payment_blueprint.route('/<int:payment_id>', methods = ['DELETE'])
def delete_payment(payment_id):
    if check := admin_check(user_id=request.headers.get('User-ID'), password_hash=request.headers.get('Password-Hash')): return check
    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute('SELECT payment_id FROM payments WHERE payment_id = %s',(payment_id,))
        if not cursor.fetchone():
            return jsonify({"error":"payment id was not found"}),404
        cursor.execute('DELETE FROM payments WHERE payment_id = %s',(payment_id,))
        link.commit()
        return jsonify({"message":f"payment {payment_id} successfuly deleted"}),200
    except Exception as e:
        link.rollback()
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()

@payment_blueprint.route('/<int:payment_id>', methods = ['PUT'])
def modify_payment(payment_id):
    if check := admin_check(user_id=request.headers.get('User-ID'), password_hash=request.headers.get('Password-Hash')): return check
    link = get_db_connection()
    data=request.json
    cursor = link.cursor()
    try:
        cursor.execute('SELECT payment_id FROM payments WHERE payment_id = %s',(payment_id,))
        if not cursor.fetchone():
            return jsonify({"error":"payment not found"}),404
        cursor.execute('UPDATE payments SET payment_status = %s, transaction_id = %s, amount = %s WHERE payment_id = %s', (data['status'] or 'pending',data['tx_id'] or None,float(data['amount']),payment_id))
        link.commit()
        return jsonify({"message":f"Payment {payment_id} updated."}),200
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()

@payment_blueprint.route('/<int:payment_id>/complete', methods = ['PUT'])
def complete_payment(payment_id):
    if check := admin_check(user_id=request.headers.get('User-ID'), password_hash=request.headers.get('Password-Hash')): return check
    headers = {
        'User-ID' : request.headers.get('User-ID'),
        'Password-Hash' : request.headers.get('Password-Hash')
    }
    link = get_db_connection()
    data=request.json
    cursor = link.cursor()
    copy_id = None
    try:
        if data['transaction_id'] == "today":
            cursor.execute('UPDATE payments SET payment_status =%s, transaction_id = %s WHERE payment_id = %s', ('completed', datetime.now().timestamp(),payment_id))
            link.commit()
            requests.put(f"{catalog_service}/copy/",
            json={"status": 'available',"copy_id" : copy_id}, headers=headers)
            return jsonify({"message":f"payment {payment_id} completed."})
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()

@payment_blueprint.route('/loan_lookup', methods = ['GET'])
def get_payment_by_loan_id():
    data = request.json
    loan_id = data['loan_id']
    link = get_db_connection()
    cursor = link.cursor()
    cursor.execute(
        """
            SELECT payment_id, user_id, loan_id, amount, payment_status, transaction_id FROM payments WHERE loan_id = %s
                """, (loan_id,)
    )
    row = cursor.fetchone()
    if row:
        payment_obj = Payment(*row)
        return jsonify(payment_obj.to_json()),200
    return jsonify({"error":"loan id not found."}),404
@payment_blueprint.route('/getuser/<int:user_id>', methods = ['GET'])
def get_payment_by_user(user_id):
    link = get_db_connection()
    cursor = link.cursor() 
    cursor.execute('SELECT * WHERE user_id = %s',(user_id))
    rows = cursor.fetchall()
    if not rows:
        return jsonify({"error":"This user has no payments yet"}),40
    payments = []
    for row in rows:
        payment_obj = Payment(row[0],row[1],row[2],row[3],row[4],row[5])
        payments.append(payment_obj.to_json())
    cursor.close()
    link.close()
    return jsonify(payments)
@payment_blueprint.route('/request/<int:payment_id>', methods = ['POST'])
def request_payment(payment_id):
    if check := admin_check(user_id=request.headers.get('User-ID'), password_hash=request.headers.get('Password-Hash')): return check
    headers = {
        'User-ID' : request.headers.get('User-ID'),
        'Password-Hash' : request.headers.get('Password-Hash')
    }
    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute('SELECT payment_id,loan_id, amount FROM payments WHERE payment_id = %s',(payment_id,))
        cursor_data = cursor.fetchone()
        loan_id = cursor_data[1]
        current_amount = cursor_data[2]
        response = requests.get(f"{loan_service}/loans/{loan_id}",headers=headers)
        if response.status_code ==200:
            loan_data = response.json()
            copy_id = loan_data.get('copy_id')
            if loan_data.get('status') == 'overdue':
                fine = requests.get(f"{loan_service}/loans/fines", 
                                            headers=headers,
                                            json={
                                                        "loan_id" : loan_id,
                                                        "copy_id" : copy_id                                                                        
                                                    })
                fine_data = fine.json()
                cursor.execute('UPDATE payments SET amount = %s WHERE payment_id =%s', (float(current_amount+fine_data['fine']),payment_id))
            return jsonify({"message":"Payment requested"})
        else:
            return jsonify({"error":"loan id not found."})
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()
@payment_blueprint.route('/getall', methods = ['GET'])
def get_all_payments():
    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute('SELECT * FROM payments')
        rows =  cursor.fetchall()
        payments = [Payment(row[0],row[1],row[2],row[3],row[4],row[5]).to_json() for row in rows]
        return jsonify(payments), 200
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()
