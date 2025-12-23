from flask import Flask
from controller import *
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent.parent))
from shared_utils import *

app = Flask(__name__)
app.register_blueprint(payment_blueprint, url_prefix="/payments")
@app.route('/payments', methods = ['POST']) #add a payment
def add_payment():
    if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')):return check
    data = request.json
    link = get_db_connection(Path(__file__).parent.name.replace("_service",""))
    cursor = link.cursor()
    try:
        cursor.execute('''
                        INSERT INTO payments (user_id, loan_id, amount, payment_status) VALUES (%s, %s, %s, %s) RETURNING payment_id
                        ''',
                          (data['user_id'], data['loan_id'], data['amount'],'pending')
                        )
        new_id = cursor.fetchone()[0]
        print(new_id)
        link.commit()
        return jsonify({"message":"Payment created","id":new_id}),201
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()     
@app.route('/payments/<int:payment_id>',methods = ['GET'])    
def get_payment_json(payment_id):
    try:
        payment_obj = get_payment(payment_id)
        if payment_obj:
            if request.headers.get('User-ID') and int(request.headers.get('User-ID')) == payment_obj.user_id: ##user id 3 can only acess its own information, admins can access everyone's.
                pass
            else:
                if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check   
            return jsonify(payment_obj.to_json()),200
        return jsonify({"error":f"payment {payment_id} was not found"}),404
    except Exception as e:
        return jsonify({"error":str(e)}),500
def get_payment(payment_id):
    link = get_db_connection(Path(__file__).parent.name.replace("_service",""))
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
@app.route('/payments/<int:payment_id>', methods = ['DELETE'])
def delete_payment(payment_id):
    if check := admin_check(user_id=request.headers.get('User-ID'), password_hash=request.headers.get('Password-Hash')): return check
    link = get_db_connection(Path(__file__).parent.name.replace("_service",""))
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
@app.route('/payments/<int:payment_id>', methods = ['PUT'])
def modify_payment(payment_id):
    if check := admin_check(user_id=request.headers.get('User-ID'), password_hash=request.headers.get('Password-Hash')): return check
    link = get_db_connection(Path(__file__).parent.name.replace("_service",""))
    data=request.json
    cursor = link.cursor()
    print(payment_id)
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
@app.route('/payments/<int:payment_id>/complete', methods = ['PUT'])
def complete_payment(payment_id):
    if check := admin_check(user_id=request.headers.get('User-ID'), password_hash=request.headers.get('Password-Hash')): return check
    headers = {
                                                    'User-ID' : request.headers.get('User-ID'),
                                                    'Password-Hash' : request.headers.get('Password-Hash')
                                                }
    link = get_db_connection(Path(__file__).parent.name.replace("_service",""))
    data=request.json
    cursor = link.cursor()
    copy_id = None
    try:
        if data['transaction_id'] == "today":
            cursor.execute('UPDATE payments SET payment_status =%s, transaction_id = %s WHERE payment_id = %s', ('completed', datetime.now().timestamp(),payment_id))
            link.commit()
            requests.put(f"http://localhost:5002/copy/",
            json={"status": 'available',"copy_id" : copy_id}, headers=headers)
            return jsonify({"message":f"payment {payment_id} completed."})
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()
@app.route('/payments', methods = ['GET'])
def get_payment_by_loan_id():
    data = request.json
    loan_id = data['loan_id']
    link = get_db_connection(Path(__file__).parent.name.replace("_service",""))
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
@app.route('/request', methods = ['POST'])
def request_payment(payment_id):
    if check := admin_check(user_id=request.headers.get('User-ID'), password_hash=request.headers.get('Password-Hash')): return check
    headers = {
                                                    'User-ID' : request.headers.get('User-ID'),
                                                    'Password-Hash' : request.headers.get('Password-Hash')
                                                }
    
    link = get_db_connection(Path(__file__).parent.name.replace("_service",""))
    cursor = link.cursor()
    try:
        cursor.execute('SELECT payment_id,loan_id, amount FROM payments WHERE payment_id = %s',(payment_id,))
        cursor_data = cursor.fetchone()
        loan_id = cursor_data[1]
        current_amount = cursor_data[2]
        response = requests.get(f"http://localhost:5003/loans/{loan_id}",headers=headers)
        if response.status_code ==200:
            loan_data = response.json()
            copy_id = loan_data.get('copy_id')
            if loan_data.get('status') == 'overdue':
                fine = requests.get(f"http://localhost:5003/fines", 
                                            headers=headers,
                                            json={
                                                        "loan_id" : loan_id,
                                                        "copy_id" : copy_id                                                
                                                    })
                fine_data = fine.json()
                cursor.execute('UPDATE payments SET amount = %s WHERE payment_id =%s', (float(current_amount+fine_data['fine']),payment_id))
            ###REQUEST PAYMENT TO CLIENT VIA EMAIL 
            ###HOW DO I EMAIL
        else:
            return jsonify({"error":"loan id not found."})
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5004)