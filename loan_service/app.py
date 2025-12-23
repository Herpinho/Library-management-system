import sys
from pathlib import Path
import os
from datetime import datetime,timedelta
sys.path.append(str(Path(__file__).parent.parent))
from shared_utils import *
from flask import Flask, request, jsonify
from model import Loan

def get_loan_object(loan_id):
    # This logic belongs in its own function so both routes can use it
    link = get_db_connection(Path(__file__).parent.name.replace("_service", ""))
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
    response = requests.get(f"http://localhost:5002/books/{book_id}")
    if response.status_code == 200:
        return response.json()
    return None
def change_availability(book_id, copy_id, status):
    requests.put(
        f"http://localhost:5002/books/{book_id}/copy/{copy_id}",
        json={"status": status}
    )
app = Flask(__name__)
@app.route('/loans', methods = ['GET']) #check loans by user id
def check_user_loans():
    link = get_db_connection(Path(__file__).parent.name.replace("_service", ""))
    cursor = link.cursor()
    data = request.json
    if request.headers.get('User-ID') and int(request.headers.get('User-ID')) == id: ##user id 3 can only acess its own information, admins can access everyone's.
        pass
    else:
        if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check
    cursor.execute(
        '''
        SELECT
            l.loan_id,
            l.copy_id,
            l.user_id,
            l.loan_date,
            l.due_date,
            l.return_date,
            l.status
        FROM loans l WHERE user_id = %s
        ''', (data.get('user_id'),)
    )
    
    rows = cursor.fetchall()
    if not rows:
        return jsonify({"error":"This user has made no loans yet"})
    loans = []
    for row in rows:
        loan_obj = Loan(row[0],row[1],row[2],row[3],row[4],row[5])
        loans.append(loan_obj.to_json())
    cursor.close()
    link.close()
    return jsonify(loans)
@app.route('/loans', methods = ['POST']) #new loan
def new_loan():
    if check := admin_check(user_id=request.headers.get('User-ID'), password_hash=request.headers.get('Password-Hash')): return check
    data = request.json
    link = get_db_connection(Path(__file__).parent.name.replace("_service",""))
    cursor = link.cursor()
    amount,unit = data.get('due_date').split()
    days = calculate_due_date(int(amount),unit)
    due_date = datetime.now().date() + days
    try:
        response = requests.get(f"http://localhost:5002/copy/",json={"copy_id" : str(data['copy_id'])})
        copy_data = response.json()
        if copy_data[0] == 'available':
            cursor.execute(
                'INSERT INTO loans (copy_id, user_id, due_date, status) VALUES (%s,%s,%s,%s) RETURNING loan_id',
                (str(data['copy_id']),data['user_id'],due_date,data.get('status') or 'active'),
            )
            new_id = cursor.fetchone()[0]

            if response.status_code ==200:
                price = float(copy_data[1])*days.days
                print(price)
                requests.post("http://localhost:5004/payments",json={
                    "user_id" : data['user_id'],
                    "loan_id" : new_id,
                    "amount"  : str(price)
                },
                headers = {
                'User-ID': request.headers.get('User-ID'),
                'Password-Hash': request.headers.get('Password-Hash')
                })
                requests.put(f"http://localhost:5002/copy/", json={"copy_id": str(data['copy_id']), "status": "loaned"}, headers= {
                'User-ID': request.headers.get('User-ID'),
                'Password-Hash': request.headers.get('Password-Hash')
                })
                link.commit()
                
                return jsonify({"message":"Loan added","id":new_id}),201
        return jsonify({"error":"Book copy is unavailable"})
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()
@app.route('/loans/<int:loan_id>', methods = ['DELETE']) #delete loan   
def delete_loan(loan_id):
    if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check
    link = get_db_connection(Path(__file__).parent.name.replace("_service", ""))
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
@app.route('/loans/<int:loan_id>', methods = ['GET']) #check loan by id
def get_loan(loan_id):
    if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check    ##ADMIN COMMAND
    link = get_db_connection(Path(__file__).parent.name.replace("_service", ""))
    cursor = link.cursor()
    try: 
        cursor.execute(
            '''
            SELECT
                l.loan_id,
                l.copy_id,
                l.user_id,
                l.loan_date,
                l.due_date,
                l.return_date,
                l.status
            FROM loans l WHERE loan_id = %s 

            ''',(loan_id,)
        )
        row = cursor.fetchone()
        if not row or row[0] is None:
            return jsonify({"error":"loan id not found."})
        if datetime.now().date() > row[4]:
            row[6] = 'overdue'
            cursor.execute("UPDATE ")
        loan_obj = Loan(*row)
        return jsonify(loan_obj.to_json()),200
    except Exception as e:
        return jsonify({"error":str(e)})
    finally:
        cursor.close()
        link.close()
@app.route('/loans/<int:loan_id>', methods = ['PUT']) #update loan 
def modify_loan(loan_id):
    if check := admin_check(user_id=request.headers.get('User-ID'),password_hash=request.headers.get('Password_Hash')): return check
    headers = {'User-ID' : request.headers.get('User-ID'), 'Password-Hash' : request.headers.get('Password_Hash')}
    data = request.json
    link = get_db_connection(Path(__file__).parent.name.replace("_service", ""))
    cursor = link.cursor()
    try:
        cursor.execute('SELECT loan_id,status,due_date,copy_id FROM loans WHERE loan_id = %s',(loan_id,))
        payment = requests.get(f'http://localhost:5004/payments', json = { "loan_id" : loan_id}, headers=headers )
        current_payment = payment.json()

        payment_id = current_payment['payment_id']
        payment_amount = current_payment['amount']
        current_loan = cursor.fetchone()
        
        if not current_loan:
            return jsonify({"error":"loan id not found."}),404
        new_due_date = current_loan[2]
        status = None
        return_date = None
        today = datetime.now().date()
        if data.get('return_date') == "today":
            return_date = today
            if today > current_loan[2]:
                status = 'overdue'
            else:
                status = 'returned'
            requests.put(f"http://localhost:5004/payments/{payment_id}/complete",json = {
                "transaction_id" : "today"
            },headers=headers)

        else: return_date = None
        if not data.get('due_date') == "":
            if datetime.now().date() < current_loan[2]:
                parts = data['due_date'].split()
                if len(parts)==2:  
                    reduction, extra = 0, 0 
                    amount = int(parts[0])
                    unit = parts[1]
                    time = calculate_due_date(amount, unit)
                    new_due_date = current_loan[2] + time
                    copy = requests.get("http://localhost:5002/copy/",json = {
                        "copy_id" : current_loan[3]
                    })
                    copy_data = copy.json()
                    price = float(copy_data[1])

                    if amount < 0:
                        reduction = float(-(price*0.5))
                    else:
                        extra = float(price*1.1)
                    requests.put(f"http://localhost:5004/payments/{payment_id}", json = {
                    "status": "",
                    "tx_id": "",
                    "amount": float(payment_amount + (reduction + extra)*amount)
                    },headers=headers)
            else:
                return jsonify({"error":"loan is already overdue."})
                
        cursor.execute('''
                    UPDATE loans 
                    SET due_date = %s, return_date = %s, status = %s
                    WHERE loan_id = %s''',
                       (new_due_date or current_loan[2],return_date or None , status or data['status'] or current_loan[1],loan_id))
        link.commit()
        if data['status'] == 'returned' or not data['return_date'] == None: 
            cursor.execute('SELECT copy_id FROM loans where loan_id = %s',(loan_id,))
            row = cursor.fetchone()
            if row is None:
                return jsonify({"error":"loan id not found."}),404
            copy_id = row[0]
            change_availability(book_id=copy_id.split('.')[0],copy_id =copy_id,status = 'available')
        updated_loan_obj = get_loan_object(loan_id)
        return jsonify({"message":f"loan {loan_id} updated successfully",
                        "loan": updated_loan_obj.to_json()}),200
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()
def warning_system():
    pass
    ##email user warning that they're book is expiring 1-2 days before 
    ##day 2 how does one email via python 
@app.route('/fines' , methods = ['GET']) # get fines if necessary
def fine_system():
    data = request.json
    loan_id = data['loan_id']
    copy_id = data['copy_id']
    link = get_db_connection(Path(__file__).parent.name.replace("_service", ""))
    cursor = link.cursor()
    try: 
        cursor.execute('''
                    SELECT 
                       l.loan_id,
                       l.due_date
                    FROM loans l WHERE loan_id = %s
                    GROUP BY l.loan_id
                       ''', (loan_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error":"loan not found."}),404
        response = requests.get("http://localhost:5002/copy/", json= {"copy_id": copy_id})
        copy_data = response.json()
        due_date = row[1]
        delta = datetime.now().date() - due_date
        return jsonify({"fine" : delta.days * copy_data['rent_price']})
    except Exception as e:
        return jsonify({"error":str(e)}),500
    finally:
        cursor.close()
        link.close()
def user_card_checkup():
    pass
    #not sure yet what it means but i added this in the project notes.
    #day 2 of not knowing what to do with this, the whole thing feels physical.
if __name__ == '__main__':   
    app.run(debug=True, port = 5003)                           

        
