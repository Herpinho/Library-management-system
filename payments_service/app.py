from flask import Flask
from controller import *
from pathlib import Path
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
                        INSERT INTO payments (user_id,copy_id,amount,status,transaction_id) VALUES (%s,%s,%s,%s,%s)
                        ''',
                          (data['user_id'],data['copy_id'], data['amount'],data['status'] or 'pending' ,data['transaction_id'] or None)
                        )
        new_id = cursor.fetchone()[0]
        link.commit()
        return jsonify({"message":"Book created","id":new_id}),201
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
            return jsonify(payment_obj.to_json()),200
        return jsonify({"error":f"payment {payment_id} was not found"}),404
    except Exception as e:
        return jsonify({"error":str(e)}),500
def get_payment(payment_id):
    if request.headers.get('User-ID') and int(request.headers.get('User-ID')) == id: ##user id 3 can only acess its own information, admins can access everyone's.
        pass
    else:
        if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check
    link = get_db_connection(Path(__file__).parent.name.replace("_service",""))
    cursor = link.cursor()
    try:
        cursor.execute(
            ''' 
            SELECT
                p.payment_id
                p.user_id
                p.loan_id
                p.amount
                p.status
                p.transaction_id
            FROM public.payments p
            WHERE p.payment_id = %s
            GROUP by p.payment_id
                ''' ,(payment_id,)
        )
        row = cursor.fetchone()
        if not row or row[0] is None:
            return jsonify({"error":f"payment {payment_id} was not found."}),404
        return Payment(*row)
    except Exception as e:
        return jsonify({"error":str(e)}),500
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
    try:
        cursor.execute('SELECT payment_id FROM payments WHERE payment_id = %s',(payment_id,))
        if not cursor.fetchone():
            return jsonify({"error":"payment not found"}),404
        cursor.execute('UPDATE payments SET status = %s, transaction_id = %s WHERE payment_id = %s,', (data['status'] or None,data['tx_id'] or None,payment_id,))
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
    link = get_db_connection(Path(__file__).parent.name.replace("_service",""))
    data=request.json
    cursor = link.cursor()
    try:
        cursor.execute('SELECT payment_id,loan_id from payments WHERE payment_id = %s', (payment_id,))
        loan_id = cursor.fecthone()[1]
        if loan_id:
            return jsonify({"error":"payment not found"}),404
        response = requests.get(f"http://localhost:5003/loans/{loan_id}")
        if response.status_code ==200:
            loan_data = response.json()
            copy_id = loan_data.get('copy_id')
            book_id = str(copy_id).split('.')[0]
        if data['transaction_id']:
            cursor.execute('UPDATE payments SET status =%s, transaction_id = %s', ('completed',data['transaction_id'],))
            requests.put(f"http://localhost:5002/books/{book_id}/copy/{copy_id}",
            json={"status": 'completed'})
            return jsonify({"message":f"payment {payment_id} completed."})
    except Exception as e:
        return jsonify({"error":str(e)})
    finally:
        cursor.close()
        link.close()
def request_payment():
    pass
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5004)