from flask import Blueprint, request, jsonify
import requests
from datetime import datetime, timedelta
from pathlib import Path
from shared_utils.utils import *
from model import Loan

loan_blueprint = Blueprint('loan_blueprint', __name__)
catalog_service = os.getenv("CATALOG_SERVICE", "http://catalog-service:5002")
payment_service = os.getenv("PAYMENTS_SERVICE", "http://payments-service:5004")
def get_loan_object(loan_id):
    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute('SELECT loan_id, copy_id, user_id, loan_date, due_date, return_date, status FROM loans WHERE loan_id = %s', (loan_id,))
        row = cursor.fetchone()
        return Loan(*row) if row else None
    finally:
        cursor.close()
        link.close()

def calculate_due_date(amount, unit):
    multipliers = {
        'month': 30,
        'week': 7,
        'day': 1
    }
    clean_unit = unit.rstrip('s')
    days = amount * multipliers.get(clean_unit,1)
    return timedelta(days=days)

def get_book(book_id):
    response = requests.get(f"{catalog_service}/books/{book_id}")
    if response.status_code == 200:
        return response.json()
    return None

def change_availability(copy_id,status):
    requests.put(
        f"{catalog_service}/books/copy/",
        json={"status": status,
              "copy_id": copy_id}
    )

@loan_blueprint.route('/<int:user_id>', methods = ['GET'])
def check_user_loans(user_id):
    link = get_db_connection()
    cursor = link.cursor()
    cursor.execute(
        '''
        SELECT
            l.loan_id, l.copy_id, l.user_id, l.loan_date, l.due_date, l.return_date, l.status
        FROM loans l WHERE user_id = %s
        ''', (user_id,)
    )
    
    rows = cursor.fetchall()
    if not rows:
        return jsonify({"error":"This user has made no loans yet"}),404
    cursor.execute('''UPDATE loans 
SET status = 'overdue' 
WHERE due_date < CURRENT_DATE AND status = 'active';''')
    loans = []
    for row in rows:
        loan_obj = Loan(row[0],row[1],row[2],row[3],row[4],row[5],row[6])
        loans.append(loan_obj.to_json())
    cursor.close()
    link.close()
    return jsonify(loans)

@loan_blueprint.route('/', methods = ['POST'])
def new_loan():
    data = request.json
    link = get_db_connection()
    cursor = link.cursor()
    amount,unit = data.get('due_date').split()
    days = calculate_due_date(int(amount),unit)
    due_date = datetime.now().date() + days
    try:
        response = requests.get(f"{catalog_service}/books/copy/",json={"copy_id" : str(data['copy_id'])})
        if not response.ok:
            return jsonify({"error": f"Catalog service returned {response.status_code}"}), response.status_code
        copy_data = response.json()
        if copy_data[0] == 'available':
            cursor.execute(
                'INSERT INTO loans (copy_id, user_id, due_date, status) VALUES (%s,%s,%s,%s) RETURNING loan_id',
                (str(data['copy_id']),data['user_id'],due_date,data.get('status') or 'active'),
            )
            new_id = cursor.fetchone()[0]

            if response.status_code ==200:
                price = float(copy_data[1])*days.days
                requests.post(f"{payment_service}/payments/",json={
                    "user_id" : data['user_id'],
                    "loan_id" : new_id,
                    "amount"  : str(price)
                },
                headers = {
                'User-ID': request.headers.get('User-ID'),
                'Password-Hash': request.headers.get('Password-Hash')
                })
                requests.put(f"{catalog_service}/books/copy/", json={"copy_id": str(data['copy_id']), "status": "loaned"}, headers= {
                'User-ID': request.headers.get('User-ID'),
                'Password-Hash': request.headers.get('Password-Hash')
                })
                link.commit()
                
                return jsonify({"message":"Loan added","id":new_id}),201
        return jsonify({"error":"Book copy is unavailable"}),300
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()

@loan_blueprint.route('/<int:loan_id>', methods = ['DELETE'])
def delete_loan(loan_id):
    if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check
    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute('SELECT loan_id FROM loans WHERE loan_id = %s', (loan_id,))
        if cursor.fetchone() is None:
            return jsonify({"error":"loan_id not found."}),404
        cursor.execute('DELETE FROM loans WHERE loan_id = %s', (loan_id,))
        link.commit()
        return jsonify({"message": f"loan {loan_id} successfully removed"}),200
    except Exception as e:
        link.rollback()
        return jsonify ({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()

@loan_blueprint.route('/<int:loan_id>', methods = ['GET'])
def get_loan(loan_id):
    link = get_db_connection()
    cursor = link.cursor()
    try: 
        cursor.execute(
            'SELECT loan_id, copy_id, user_id, loan_date, due_date, return_date, status FROM loans WHERE loan_id = %s', (loan_id,)
        )
        row = list(cursor.fetchone())
        if not row or row[0] is None:
            return jsonify({"error":"loan id not found."})
        if datetime.now().date() > row[4]:
            row[6] = 'overdue'
            cursor.execute("UPDATE loans SET status = 'overdue' WHERE loan_id = %s", (loan_id,))
            link.commit()
        loan_obj = Loan(*row)
        return jsonify(loan_obj.to_json()),200
    except Exception as e:
        return jsonify({"error":str(e)})
    finally:
        cursor.close()
        link.close()

@loan_blueprint.route('/<int:loan_id>', methods = ['PUT'])
def modify_loan(loan_id):
    if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check
    headers = {'User-ID' : request.headers.get('User-ID'), 'Password-Hash' : request.headers.get('Password-Hash')}
    data = request.json
    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute('SELECT loan_id,status,due_date,copy_id FROM loans WHERE loan_id = %s',(loan_id,))
        current_loan = cursor.fetchone()
        if not current_loan:
            return jsonify({"error":"loan id not found."}),404
            
        payment = requests.get(f'{payment_service}/payments/loan_lookup', json = { "loan_id" : loan_id}, headers=headers )
        current_payment = payment.json()
        payment_id = current_payment['payment_id']
        payment_amount = current_payment['amount']
        
        new_due_date = current_loan[2]
        status = None
        return_date = None
        today = datetime.now().date()
        
        if data.get('return_date') == "today":
            return_date = today
            status = 'overdue' if today > current_loan[2] else 'returned'
            requests.put(f"{catalog_service}/books/copy", json={"copy_id": current_loan[3]})
        
        if data.get('due_date'):
            if datetime.now().date() < current_loan[2]:
                parts = data['due_date'].split()
                if len(parts)==2:  
                    amount = int(parts[0])
                    unit = parts[1]
                    time = calculate_due_date(amount, unit)
                    new_due_date = current_loan[2] + time
                    copy = requests.get(f"{catalog_service}/copy/",json = {"copy_id" : current_loan[3]})
                    copy_data = copy.json()
                    price = float(copy_data[1])
                    
                    adjustment = float(-(price*0.5)) if amount < 0 else float(price*1.1)
                    requests.put(f"{payment_service}/payments/{payment_id}", json = {
                        "status": "", "tx_id": "", "amount": float(payment_amount + adjustment * abs(amount))
                    },headers=headers)
            else:
                return jsonify({"error":"loan is already overdue."})
                
        cursor.execute('''
                    UPDATE loans 
                    SET due_date = %s, return_date = %s, status = %s
                    WHERE loan_id = %s''',
                       (new_due_date, return_date, status or data.get('status') or current_loan[1], loan_id))
        link.commit()
        
        if status == 'returned' or data.get('return_date') == 'today':
            copy_id = current_loan[3]
            change_availability(copy_id=copy_id, status='available')
            
        updated_loan_obj = get_loan_object(loan_id)
        return jsonify({"message":f"loan {loan_id} updated successfully", "loan": updated_loan_obj.to_json()}),200
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()

@loan_blueprint.route('/fines' , methods = ['GET'])
def fine_system():
    data = request.json
    loan_id = data['loan_id']
    copy_id = data['copy_id']
    link = get_db_connection()
    cursor = link.cursor()
    try: 
        cursor.execute('SELECT loan_id, due_date FROM loans WHERE loan_id = %s', (loan_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error":"loan not found."}),404
        response = requests.get(f"{catalog_service}/copy/", json= {"copy_id": copy_id})
        copy_data = response.json()
        due_date = row[1]
        delta = datetime.now().date() - due_date
        return jsonify({"fine" : max(0,delta.days) * float(copy_data[1])})
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()
@loan_blueprint.route('/getall', methods = ['GET'])
def get_all_loans():
    link = get_db_connection()
    cursor = link.cursor()
    try:
        cursor.execute('SELECT * FROM loans')
        rows =  cursor.fetchall()
        cursor.execute('''UPDATE loans 
SET status = 'overdue' 
WHERE due_date < CURRENT_DATE AND status = 'active';''')
        link.commit()
        loans = []
        for row in rows:
            loan_obj = Loan(row[0],row[1],row[2],row[3],row[4],row[5],row[6])
            loans.append(loan_obj.to_json())
        return jsonify(loans), 200
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()
