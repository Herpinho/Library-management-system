import requests
import getpass
import sys
import re
import os
from dotenv import load_dotenv
from shared_utils.ui_utils import chat_bubble,title,user_input,message_formatter,json_formatter
link = None
load_dotenv("../.env")
USER_SERVICE    = "http://localhost:5001"
CATALOG_SERVICE = "http://localhost:5002"
LOAN_SERVICE    = "http://localhost:5003"
PAYMENT_SERVICE = "http://localhost:5004"
if sys.platform == 'win32':
    import msvcrt


def password_asterisco():
   
    password = ""
    
    if sys.platform == 'win32':
        # Windows
        while True:
            char = msvcrt.getch()
            if char in (b'\r', b'\n'):  
                break
            elif char == b'\x08':  
                if len(password) > 0:
                    password = password[:-1]
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            else:
                password += char.decode('utf-8')
                sys.stdout.write('*')
                sys.stdout.flush()
    
    sys.stdout.write('\n')
    sys.stdout.flush()
    return password


if sys.platform == 'win32':
    import msvcrt


def password_asterisco():
   
    password = ""
    
    if sys.platform == 'win32':
        # Windows
        while True:
            char = msvcrt.getch()
            if char in (b'\r', b'\n'):  # Enter
                break
            elif char == b'\x08':  # Backspace
                if len(password) > 0:
                    password = password[:-1]
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            else:
                password += char.decode('utf-8')
                sys.stdout.write('*')
                sys.stdout.flush()
    
    sys.stdout.write('\n')
    sys.stdout.flush()
    return password


class UserSession:
    def __init__(self):
        self.headers = {}
    def update_session(self,headers):
        self.headers = headers
    def get_session(self):
        return self.headers

current_session = UserSession()
<<<<<<< Updated upstream
USER_SERVICE = "http://localhost:5001"
CATALOG_SERVICE = "http://localhost:5002"
LOAN_SERVICE = "http://localhost:5003"
PAYMENT_SERVICE = "http://localhost:5004/payments"
=======
>>>>>>> Stashed changes

def register_user():
    chat_bubble(
    """
    Register 

    Email:                                      
    Username: 
    Password: 
    """
    )
 
    sys.stdout.write("\033[4F\033[13C")
    sys.stdout.flush()
    email = input()
    while not re.match(r'^[a-zA-Z0-9._]+@[a-zA-Z]+\.[a-zA-Z]{2,}$',email):
        sys.stdout.write(f"\033[2F\033[2C")
        sys.stdout.flush()
        print("Invalid Email.")
        sys.stdout.write(f"\033[13C" + (" " * len(email)) + f"\033[{len(email)}D")
        sys.stdout.flush()
        email = input()

    sys.stdout.write("\033[16C")
    sys.stdout.flush()
    username = input()
    while not re.match(r'^[a-zA-Z0-9]{6,}',username):
        sys.stdout.write("\033[3F\033[2C")
        sys.stdout.flush()
        print("Invalid Username. (min. 6 characters)")
        sys.stdout.write(f"\033[1E\033[16C" + (" " * len(username)) + f"\033[{len(username)}D")
        sys.stdout.flush()
        username = input()
    sys.stdout.write("\033[16C")
    sys.stdout.flush()
    
    password = password_asterisco()
    
    
    while not re.match(r'^[a-zA-Z0-9._%+\-!?"#$%&/()]{8,}$', password):
        sys.stdout.write("\033[4F\033[2C")
        sys.stdout.flush()
        print("Invalid Password. (min. 8 characters)")
        sys.stdout.write(f"\033[2E\033[16C")
        sys.stdout.flush()
        password = password_asterisco()
    print("\n\n")
    data = {"username": username, "email": email, "password": password, "role" : "admin"}
    request = requests.post(f"{USER_SERVICE}/users/register", json=data)
    chat_bubble(message_formatter(request))

def login_user():
    chat_bubble("""
Login

 Username:                              
 Password:
    """)
    sys.stdout.write("\033[3F\033[13C")
    sys.stdout.flush()
    username = input()
    while not re.match(r'^[a-zA-Z0-9]{6,}',username):
        sys.stdout.write("\033[2F\033[2C")
        sys.stdout.flush()
        print("Invalid Username. (min. 6 characters)")
        sys.stdout.write(f"\033[13C" + (" " * len(username)) + f"\033[{len(username)}D")
        sys.stdout.flush()
        username = input()
    sys.stdout.write("\033[13C")
    sys.stdout.flush()
    
    password = password_asterisco()
   

    while not re.match(r'^[a-zA-Z0-9._%+\-!?"#$%&/()]{8,}$', password):
        sys.stdout.write("\033[3F\033[2C")
        sys.stdout.flush()
        print("Invalid Password. (min. 8 characters)")
        sys.stdout.write(f"\033[1E\033[13C")
        sys.stdout.flush()
        password = password_asterisco()
    print("\n\n")
    data = {"username": username, "password": password}
    request = requests.post(f"{USER_SERVICE}/users/login", json=data)
    if request.status_code == 250:
        chat_bubble(message_formatter(request))
        login_user()
    elif request.status_code == 200:
        data = request.json()
        
        current_session.update_session(headers =
                                        {"User-ID": str(data.get('ID')),
                                         "Password": str(data.get('Password'))})
        chat_bubble(message_formatter(request))

        

    else:
        chat_bubble(message_formatter(request))

<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
def log_menu():
    chat_bubble("""
    Welcome to the Library
            
    Choose an option:
        1) Log-in
        2) Register
        3) Exit     
    """)
    try:
        option = int(user_input())
        chat_bubble(F"{option}","right")
    except:
        log_menu()
    match option:
        case 1:
            login_user()
            main_menu_user()
        case 2:
            register_user()
            log_menu()
        case 3:
            print("\nObrigado por usar a Library System. Até breve!")
            sys.exit(0)

def main_menu_user():
    chat_bubble("""
    Main Library Menu
            
    Choose an option:
        1) Loans
        2) Catalog
        3) Payments
        4) Account Settings
        5) Log-out
    """)
    try:
        option = int(user_input())
        chat_bubble(F"{option}","right")
    except:
        main_menu_user()
    match option:
        case 1:
            title("Library System - Loans")
            loan_menu()
        case 2:
            title("Library System - Catalog")
            catalog_menu()
        case 3:
            title("Library System - Payments")
            payments_menu()
        case 4:
            title("Library System - Account Settings")
            account_settings()
        case 5:
            current_session.update_session(headers={})
            log_menu()

def loan_menu():
    chat_bubble("""
    Loans Menu
            
    Choose an option:
        1) New Loan
        2) Check Loans
        3) Back
    """)
    try:
        option = int(user_input())
        chat_bubble(F"{option}","right")
    except:
        loan_menu()
    match option:
        case 1:
            title("Library System - Loan a Book")
            loan_book_menu()
        case 2:
            title("Library System - Check Loans")
            check_loan_menu()
        case 3:
            main_menu_user()

def loan_book_menu():
    chat_bubble("""
    Loan a Book
            
    Fill the spaces bellow:
        Copy ID:                   
        Loan time:                
    """)
    sys.stdout.write("\033[3F\033[19C")
    sys.stdout.flush()
    copyid = input()
    sys.stdout.write("\033[21C")
    sys.stdout.flush()
    time = input()
    current_session.headers.get('User-ID')
    response = requests.post(f"{LOAN_SERVICE}/loans", json={"copy_id" : copyid, "user_id": current_session.headers.get('User-ID'), "due_date": time, "status" : ""})
    chat_bubble(message_formatter(response))  
    main_menu_user()

def check_loan_menu():
    response = requests.get(f"{LOAN_SERVICE}/loans/{current_session.headers.get('User-ID')}", headers = current_session.get_session())
    loans = response.json()
    for loan in loans:
        book_id = loan.get('copy_id').split('.')[0]
        chat_bubble(f"""
    Loan {loan.get('loan_id')} 
    Due date: {loan.get('due_date')}
    Book: {requests.get(f"{CATALOG_SERVICE}/books/{book_id}").json().get('title')}
    Copy: {loan.get('copy_id').split('.')[1]}

""")
    loan_menu2()    
    main_menu_user()

def loan_menu2():
    chat_bubble("""
Select a Loan to edit or press 0 to go back
""")    
    loan_id = input()
    if loan_id == 0:
        check_loan_menu()
    chat_bubble("""
Select an action
    1) Return book
    2) Change due date
""")    
    option = int(input())
    match option:
        case 1:
            requests.put(f"{LOAN_SERVICE}/loans/{loan_id}",json= {"return_date": "today", "status": "returned", "due_date" : ""})
        case 2:
            chat_bubble("""
Change due date
    (+/-, #, days,week,months)                                            
    Changes:
""")
            
            change_str = input()
            requests.put(f"{LOAN_SERVICE}/loans/{loan_id}", json = {"due_date": change_str,"return_date": "","status":""})

def catalog_menu():
    pass

def payments_menu():
    chat_bubble("""Payments Menu""")

    check_admin = requests.get(
        f"{USER_SERVICE}/users/{current_session.headers.get('User-ID')}", 
        headers=current_session.get_session()
    )
    
    if check_admin.status_code == 200:
        user_data = check_admin.json()
        if user_data.get('role') == 'admin':
            payments_menu_admin()
        else:
            payments_menu_user()
    else:
        chat_bubble(message_formatter(check_admin))
        main_menu_user()

def payments_menu_user():
    """Menu de pagamentos para usuários regulares"""
    chat_bubble("""
    Payments Menu
            
    Choose an option:
        1) View Pending Payments
        2) Complete Payment
        3) Back
    """)
    try:
        option = int(user_input())
        chat_bubble(F"{option}","right")
    except:
<<<<<<< Updated upstream
        payments_menu_user()
=======
        payments_menu()
>>>>>>> Stashed changes
    
    match option:
        case 1:
            title("Library System - Pending Payments")
            view_user_payments()
        case 2:
            title("Library System - Complete Payment")
            complete_user_payment()
        case 3:
            main_menu_user()

def view_user_payments():
    chat_bubble("""View pending payments from user""")
    user_id = current_session.headers.get('User-ID')
    
    
    response = requests.get(
        f"{LOAN_SERVICE}/loans/{user_id}", 
        headers=current_session.get_session()
    )
<<<<<<< Updated upstream
=======
    
    if response.status_code != 200:
        chat_bubble(message_formatter(response))
        payments_menu()
        return
    
    loans = response.json()
    pending_payments = []
    
    for loan in loans:
        
        payment_response = requests.get(
            f"{PAYMENT_SERVICE}/payments/loan_lookup",
            json={"loan_id": loan.get('loan_id')},
            headers=current_session.get_session()
        )
        
        if payment_response.status_code == 200:
            payment = payment_response.json()
            if payment.get('status') == 'pending':
                
                book_id = loan.get('copy_id').split('.')[0]
                book_response = requests.get(f"{CATALOG_SERVICE}/books/{book_id}")
                
                if book_response.status_code == 200:
                    book = book_response.json()
                    pending_payments.append({
                        'payment': payment,
                        'loan': loan,
                        'book': book
                    })
    
    if not pending_payments:
        chat_bubble("""No pending payments found!
                       No payments due at the moment.""")
    else:
        for item in pending_payments:
            payment = item['payment']
            loan = item['loan']
            book = item['book']
            
            chat_bubble(f"""
    Payment ID: {payment.get('payment_id')}
    ──────────────────────────────────────────
    Book: {book.get('title')}
    Book ID: {loan.get('copy_id').split('.')[0]}
    Copy: {loan.get('copy_id').split('.')[1]}
    
    Loan ID: {loan.get('loan_id')}
    Due Date: {loan.get('due_date')}
    Status: {loan.get('status')}
    
    Amount to Pay: €{payment.get('amount'):.2f}
    Payment Status: {payment.get('status').upper()}
    ──────────────────────────────────────────
            """)
    
    chat_bubble("""Press Enter to continue...""")
    input()
    payments_menu()

def complete_user_payment():
    chat_bubble("""
    Complete Payment
            
    Enter Payment ID:                   
    """)
    sys.stdout.write("\033[2F\033[24C")
    sys.stdout.flush()
    payment_id = input()
    
    
    check_payment = requests.get(
        f"{PAYMENT_SERVICE}/payments/{payment_id}",
        headers=current_session.get_session()
    )
    
    if check_payment.status_code != 200:
        chat_bubble(message_formatter(check_payment))
        payments_menu()
        return
    
    payment_data = check_payment.json()
    
   
    chat_bubble(f"""
    Confirm Payment
    
    Payment ID: {payment_data.get('payment_id')}
    Amount: €{payment_data.get('amount'):.2f}
    
    Do you want to complete this payment?
        1) Yes
        2) No
    """)
    
    try:
        confirm = int(user_input())
        chat_bubble(F"{confirm}","right")
    except:
        complete_user_payment()
        return
    
    if confirm == 1:
      
        response = requests.put(
            f"{PAYMENT_SERVICE}/payments/{payment_id}/complete",
            json={"transaction_id": "today"},
            headers=current_session.get_session()
        )
        
        if response.status_code == 200:
            chat_bubble("""Payment Completed Successfully!""")
        else:
            chat_bubble(message_formatter(response))
    
    payments_menu()

def account_settings():
    chat_bubble("""
    Account Settings
            
    Choose an option:
        1) View My Profile
        2) Change Username
        3) Change Email
        4) Change Password
        5) Back
    """)
    try:
        option = int(user_input())
        chat_bubble(f"{option}", "right")
    except:
        account_settings()
    match option:
        case 1:
            view_profile()
        case 2:
            change_username()
        case 3:
            change_email()
        case 4:
            change_password()
        case 5:
            main_menu_user()

def view_profile():
    user_id = current_session.get_session().get('User-ID')
    response = requests.get(f"{USER_SERVICE}/users/{user_id}", headers=current_session.get_session())
    if response.status_code == 200:
        user = response.json()
        chat_bubble(f"""
    Your Profile
    
    User ID: {user.get('id')}
    Username: {user.get('name')}
    Email: {user.get('email')}
    Role: {user.get('role')}
    Member Since: {user.get('creation')}
""")
    else:
        chat_bubble(message_formatter(response))
    account_settings()

def change_username():
    user_id = current_session.get_session().get('User-ID')
    response = requests.get(f"{USER_SERVICE}/users/{user_id}", headers=current_session.get_session())
>>>>>>> Stashed changes
    
    if response.status_code != 200:
        chat_bubble(message_formatter(response))
<<<<<<< Updated upstream
        payments_menu_user()
=======
    else:
        try:
            error_data = response.json()
            chat_bubble(f"Error: {error_data.get('error', 'Unknown error')}")
        except:
            chat_bubble(f"Error: Request failed")
    
    account_settings() 

def main_menu_admin():
    chat_bubble("""
    Admin Menu
            
    Choose an option:
        1) Manage Users
        2) Manage Catalog
        3) View All Loans
        4) Manage Payments
        5) Back to Main Menu
    """)
    try:
        option = int(user_input())
        chat_bubble(f"{option}", "right")
    except:
        main_menu_admin()
    match option:
        case 1:
            title("Library System - Manage Users")
            manage_users_menu()
        case 2:
            title("Library System - Manage Catalog")
            manage_catalog_menu()
        case 3:
            title("Library System - All Loans")
            view_all_loans()
        case 4:
            title("Library System - All Payments")
            payments_menu_admin()
        case 5:
            main_menu_user()

def manage_users_menu():
    chat_bubble("""
    Manage Users
            
    Choose an option:
        1) View All Users
        2) Delete User
        3) Modify User
        4) Back
    """)
    try:
        option = int(user_input())
        chat_bubble(f"{option}", "right")
    except:
        manage_users_menu()
    match option:
        case 1:
            view_all_users()
        case 2:
            delete_user()
        case 3:
            modify_user()
        case 4:
            main_menu_admin()

def view_all_users():
    response = requests.get(f"{USER_SERVICE}/users/", headers=current_session.get_session())
    if response.status_code == 200:
        users = response.json()
        for user in users:
            chat_bubble(f"""
    User ID: {user.get('id')}
    Name: {user.get('name')}
    Email: {user.get('email')}
    Role: {user.get('role')}
    Created: {user.get('creation')}
""")
    else:
        chat_bubble(message_formatter(response))
    manage_users_menu()

def delete_user():
    chat_bubble("""
    Delete User
    
    Enter User ID:                              
    """)
    sys.stdout.write("\033[2F\033[17C")
    sys.stdout.flush()
    user_id = input()
    print("\n\n")
    
    response = requests.delete(f"{USER_SERVICE}/users/{user_id}", headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    manage_users_menu()

def modify_user():
    chat_bubble("""
    Modify User
    
    Enter User ID:                              
    """)
    sys.stdout.write("\033[2F\033[20C")
    sys.stdout.flush()
    user_id = input()
    print("\n\n")
    
    chat_bubble("""
    What would you like to change?
    (Leave blank to keep current value)
    
    New Username:                              
    New Email:                              
    New Password:                              
    New Role (admin/member):                              
    """)
    sys.stdout.write("\033[7F\033[16C")
    sys.stdout.flush()
    new_username = input()
    sys.stdout.write("\033[13C")
    sys.stdout.flush()
    new_email = input()
    sys.stdout.write("\033[16C")
    sys.stdout.flush()
    new_password = getpass.getpass("")
    sys.stdout.write("\033[27C")
    sys.stdout.flush()
    new_role = input()
    print("\n\n")
    
    data = {
        "user_id": user_id,
        "new_username": new_username if new_username else None,
        "new_email": new_email if new_email else None,
        "new_password": new_password if new_password else None,
        "new_role": new_role if new_role else None
    }
    
    response = requests.put(f"{USER_SERVICE}/users/", json=data, headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    manage_users_menu()

def manage_catalog_menu():
    chat_bubble("""
    Manage Catalog
            
    Choose an option:
        1) Add Book Manually
        2) Import Book from Google Books
        3) Add Book Copy
        4) Remove Book
        5) Remove Book Copy
        6) View All Books
        7) Back
    """)
    try:
        option = int(user_input())
        chat_bubble(f"{option}", "right")
    except:
        manage_catalog_menu()
    match option:
        case 1:
            add_book()
        case 2:
            import_book_from_google()
        case 3:
            add_book_copy()
        case 4:
            remove_book()
        case 5:
            remove_book_copy()
        case 6:
            view_all_books()
        case 7:
            main_menu_admin()

def import_book_from_google():
    chat_bubble("""
    Import Book from Google Books
    
    Enter search term (ISBN, title, or author):                                                                                      
    """)
    sys.stdout.write("\033[2F\033[49C")
    sys.stdout.flush()
    search_query = input()
    print("\n\n")
    
    if not search_query:
        chat_bubble("Search term cannot be empty.")
        manage_catalog_menu()
>>>>>>> Stashed changes
        return
    
    loans = response.json()
    pending_payments = []
    
    for loan in loans:
        
        payment_response = requests.get(
            f"{PAYMENT_SERVICE}/loan_lookup",
            json={"loan_id": loan.get('loan_id')},
            headers=current_session.get_session()
        )
        
        if payment_response.status_code == 200:
            payment = payment_response.json()
            if payment.get('status') == 'pending':
                
                book_id = loan.get('copy_id').split('.')[0]
                book_response = requests.get(f"{CATALOG_SERVICE}/books/{book_id}")
                
                if book_response.status_code == 200:
                    book = book_response.json()
                    pending_payments.append({
                        'payment': payment,
                        'loan': loan,
                        'book': book
                    })
    
    if not pending_payments:
        chat_bubble("""No pending payments found!
                       No payments due at the moment.""")
    else:
        for item in pending_payments:
            payment = item['payment']
            loan = item['loan']
            book = item['book']
            
            chat_bubble(f"""
    Payment ID: {payment.get('payment_id')}
    ──────────────────────────────────────────
    Book: {book.get('title')}
    Book ID: {loan.get('copy_id').split('.')[0]}
    Copy: {loan.get('copy_id').split('.')[1]}
    
    Loan ID: {loan.get('loan_id')}
    Due Date: {loan.get('due_date')}
    Status: {loan.get('status')}
    
    Amount to Pay: £{payment.get('amount'):.2f}
    Payment Status: {payment.get('status').upper()}
    ──────────────────────────────────────────
            """)
    
    chat_bubble("""Press Enter to continue...""")
    input()
    payments_menu_user()

def complete_user_payment():
    """Completar um pagamento específico"""
    chat_bubble("""
    Complete Payment
            
    Enter Payment ID:                   
    """)
    sys.stdout.write("\033[2F\033[24C")
    sys.stdout.flush()
    payment_id = input()
    
    
    check_payment = requests.get(
        f"{PAYMENT_SERVICE}/{payment_id}",
        headers=current_session.get_session()
    )
    
    if check_payment.status_code != 200:
        chat_bubble(message_formatter(check_payment))
        payments_menu_user()
        return
    
    payment_data = check_payment.json()
    
   
    chat_bubble(f"""
    Confirm Payment
    
    Payment ID: {payment_data.get('payment_id')}
    Amount: £{payment_data.get('amount'):.2f}
    
    Do you want to complete this payment?
        1) Yes
        2) No
    """)
    
    try:
        confirm = int(user_input())
        chat_bubble(F"{confirm}","right")
    except:
        complete_user_payment()
        return
    
    if confirm == 1:
      
        response = requests.put(
            f"{PAYMENT_SERVICE}/{payment_id}/complete",
            json={"transaction_id": "today"},
            headers=current_session.get_session()
        )
        
        if response.status_code == 200:
            chat_bubble("""Payment Completed Successfully!""")
        else:
            chat_bubble(message_formatter(response))
    
    payments_menu_user()

def payments_menu_admin():
    chat_bubble("""
    Payments Menu (Admin)
            
    Choose an option:
        1) View All Pending Payments
        2) View All Payments History
        3) Create New Payment
        4) Complete Payment
        5) Modify Payment
        6) Delete Payment
        7) Request Payment for Overdue Loan
        8) Back
    """)
    try:
        option = int(user_input())
        chat_bubble(F"{option}","right")
    except:
        payments_menu_admin()
    
    match option:
        case 1:
            title("Library System - Pending Payments")
            view_all_pending_payments()
        case 2:
            title("Library System - Payment History")
            view_all_payments_history()
        case 3:
            title("Library System - Create Payment")
            create_payment_admin()
        case 4:
            title("Library System - Complete Payment")
            complete_payment_admin()
        case 5:
            title("Library System - Modify Payment")
            modify_payment_admin()
        case 6:
            title("Library System - Delete Payment")
            delete_payment_admin()
        case 7:
            title("Library System - Request Payment")
            request_payment_admin()
        case 8:
            main_menu_user()

def view_all_pending_payments():
    chat_bubble("""
    All Pending Payments
    ══════════════════════════════════════════
    """)
    
    chat_bubble("""
    Enter range of Payment IDs to check:
    (Press Enter for defaults: 1 to 100)
    From:                   
    To:
    """)
    
    try:
       
        sys.stdout.write("\033[2F\033[10C")
        sys.stdout.flush()
        from_raw = input().strip()
        from_id = int(from_raw) if from_raw else 1
        
        
        sys.stdout.write("\033[8C")
        sys.stdout.flush()
        to_raw = input().strip()
        to_id = int(to_raw) if to_raw else 100
        
    except ValueError:
        chat_bubble("Invalid input! Using default range 1-100.")
        from_id, to_id = 1, 100

    found_pending = False
    
    for payment_id in range(from_id, to_id + 1):
        try:
            response = requests.get(
                f"{PAYMENT_SERVICE}/{payment_id}",
                headers=current_session.get_session()
            )
            
            if response.status_code == 200:
                payment = response.json()
                if payment.get('status') == 'pending':
                    found_pending = True
                    chat_bubble(f"""
    Payment ID: {payment.get('payment_id')}
    User ID: {payment.get('user_id')}
    Loan ID: {payment.get('loan_id')}
    Amount: €{payment.get('amount'):.2f}
    Status: {payment.get('status').upper()}
    ──────────────────────────────────────────
                    """)
        except Exception as e:
            continue 
    
    if not found_pending:
        chat_bubble(f"No pending payments found between {from_id} and {to_id}.")
    
    chat_bubble("Press Enter to return to menu...")
    input()
    payments_menu_admin()

def view_all_payments_history():
    """Visualizar histórico de todos os pagamentos (Admin)"""
    chat_bubble("""
    Payment History
    ══════════════════════════════════════════
    
    Enter range of Payment IDs to check (e.g., 1-50):
    From:                   
    To:
    """)
    sys.stdout.write("\033[3F\033[10C")
    sys.stdout.flush()
    from_id = int(input())
    sys.stdout.write("\033[8C")
    sys.stdout.flush()
    to_id = int(input())
    
    found_any = False
    for payment_id in range(from_id, to_id + 1):
        response = requests.get(
            f"{PAYMENT_SERVICE}/{payment_id}",
            headers=current_session.get_session()
        )
        
        if response.status_code == 200:
            found_any = True
            payment = response.json()
            status_symbol = "✓" if payment.get('status') == 'completed' else "○"
            chat_bubble(f"""
    {status_symbol} Payment ID: {payment.get('payment_id')}
    User ID: {payment.get('user_id')}
    Loan ID: {payment.get('loan_id')}
    Amount: €{payment.get('amount'):.2f}
    Status: {payment.get('status').upper()}
    Transaction ID: {payment.get('transaction_id') or 'N/A'}
    ──────────────────────────────────────────
            """)
    
    if not found_any:
        chat_bubble("""
    No payments found in this range.
        """)
    
    chat_bubble("""
Press Enter to continue...
    """)
    input()
    payments_menu_admin()

def create_payment_admin():
    """Criar novo pagamento (Admin)"""
    chat_bubble("""
    Create New Payment
            
    Fill the information below:
        User ID:                   
        Loan ID:
        Amount (€):
    """)
    sys.stdout.write("\033[4F\033[19C")
    sys.stdout.flush()
    user_id = input()
    sys.stdout.write("\033[19C")
    sys.stdout.flush()
    loan_id = input()
    sys.stdout.write("\033[22C")
    sys.stdout.flush()
    amount = input()
    
    response = requests.post(
        f"{PAYMENT_SERVICE}/",
        json={
            "user_id": user_id,
            "loan_id": loan_id,
            "amount": float(amount),
            "status": "pending"
        },
        headers=current_session.get_session()
    )
    
    chat_bubble(message_formatter(response))
    payments_menu_admin()

def complete_payment_admin():
    """Completar pagamento (Admin)"""
    chat_bubble("""
    Complete Payment
            
    Enter Payment ID:                   
    """)
    sys.stdout.write("\033[2F\033[24C")
    sys.stdout.flush()
    payment_id = input()
    
    response = requests.put(
        f"{PAYMENT_SERVICE}/{payment_id}/complete",
        json={"transaction_id": "today"},
        headers=current_session.get_session()
    )
    
    chat_bubble(message_formatter(response))
    payments_menu_admin()

def modify_payment_admin():
    chat_bubble("""
    Modify Payment
            
    Payment ID:                   
    New Status (pending/completed/cancelled/failed):
    New Amount (€):
    Transaction ID:
    """)
    sys.stdout.write("\033[5F\033[18C")
    sys.stdout.flush()
    payment_id = input()
    sys.stdout.write("\033[52C")
    sys.stdout.flush()
    status = input()
    sys.stdout.write("\033[18C")
    sys.stdout.flush()
    amount = input()
    sys.stdout.write("\033[18C")
    sys.stdout.flush()
    tx_id = input()
    
    response = requests.put(
        f"{PAYMENT_SERVICE}/{payment_id}",
        json={
            "status": status,
            "amount": amount,
            "tx_id": tx_id
        },
        headers=current_session.get_session()
    )
    
    chat_bubble(message_formatter(response))
    payments_menu_admin()

def delete_payment_admin():
    """Deletar pagamento (Admin)"""
    chat_bubble("""
    Delete Payment
            
    Enter Payment ID:                   
    """)
    sys.stdout.write("\033[2F\033[24C")
    sys.stdout.flush()
    payment_id = input()
    
    chat_bubble("""
    Are you sure you want to delete this payment?
        1) Yes
        2) No
    """)
    
    try:
        confirm = int(user_input())
        chat_bubble(F"{confirm}","right")
    except:
        delete_payment_admin()
        return
    
    if confirm == 1:
        response = requests.delete(
            f"{PAYMENT_SERVICE}/{payment_id}",
            headers=current_session.get_session()
        )
        chat_bubble(message_formatter(response))
    
    payments_menu_admin()

def request_payment_admin():
    chat_bubble("""
    Request Payment for Overdue Loan
            
    Enter Payment ID:                   
    """)
    sys.stdout.write("\033[2F\033[24C")
    sys.stdout.flush()
    payment_id = input()
    
    response = requests.post(
        f"{PAYMENT_SERVICE}/request/{payment_id}",
        headers=current_session.get_session()
    )
    
    chat_bubble(message_formatter(response))
    payments_menu_admin()

def account_settings():
    pass            


   

def payments_menu_admin():
    chat_bubble("""
    Payments Menu (Admin)
            
    Choose an option:
        1) View All Pending Payments
        2) View All Payments History
        3) Complete Payment
        4) Modify Payment
        5) Delete Payment
        6) Request Payment for Overdue Loan
        7) Back
    """)
    try:
        option = int(user_input())
        chat_bubble(F"{option}","right")
    except:
        payments_menu_admin()
    
    match option:
        case 1:
            title("Library System - Pending Payments")
            view_all_pending_payments()
        case 2:
            title("Library System - Payment History")
            view_all_payments_history()
        case 3:
            title("Library System - Complete Payment")
            complete_payment_admin()
        case 4:
            title("Library System - Modify Payment")
            modify_payment_admin()
        case 5:
            title("Library System - Delete Payment")
            delete_payment_admin()
        case 6:
            title("Library System - Request Payment")
            request_payment_admin()
        case 7:
            main_menu_admin()

def view_all_pending_payments():
    chat_bubble("""
    All Pending Payments
    ══════════════════════════════════════════
    """)
    
    chat_bubble("""
    Enter range of Payment IDs to check:
    (Press Enter for defaults: 1 to 100)
    From:                   
    To:
    """)
    
    try:
       
        sys.stdout.write("\033[3F\033[11C")
        sys.stdout.flush()
        from_raw = input().strip()
        from_id = int(from_raw) if from_raw else 1
        
        
        sys.stdout.write("\033[9C")
        sys.stdout.flush()
        to_raw = input().strip()
        to_id = int(to_raw) if to_raw else 100
        
    except ValueError:
        chat_bubble("Invalid input! Using default range 1-100.")
        from_id, to_id = 1, 100

    found_pending = False
    
    for payment_id in range(from_id, to_id + 1):
        try:
            response = requests.get(
                f"{PAYMENT_SERVICE}/payments/{payment_id}",
                headers=current_session.get_session()
            )
            
            if response.status_code == 200:
                payment = response.json()
                if payment.get('status') == 'pending':
                    found_pending = True
                    chat_bubble(f"""
    Payment ID: {payment.get('payment_id')}
    User ID: {payment.get('user_id')}
    Loan ID: {payment.get('loan_id')}
    Amount: €{payment.get('amount'):.2f}
    Status: {payment.get('status').upper()}
    ──────────────────────────────────────────
                    """)
        except Exception as e:
            continue 
    
    if not found_pending:
        chat_bubble(f"No pending payments found between {from_id} and {to_id}.")
    
    chat_bubble("Press Enter to return to menu...")
    input()
    payments_menu_admin()

def view_all_payments_history():
   
    chat_bubble("""
    Payment History
    ══════════════════════════════════════════
    
    Enter range of Payment IDs to check (e.g., 1-50):
    From:                   
    To:
    """)
    try:
        sys.stdout.write("\033[3F\033[11C")
        sys.stdout.flush()
        from_id = int(input())
        sys.stdout.write("\033[9C")
        sys.stdout.flush()
        to_id = int(input())
    except:
        chat_bubble("""Error:
                    Please insert a valid number.""")
        view_all_payments_history()
    
    found_any = False
    for payment_id in range(from_id, to_id + 1):
        response = requests.get(
            f"{PAYMENT_SERVICE}/payments/{payment_id}",
            headers=current_session.get_session()
        )
        
        if response.status_code == 200:
            found_any = True
            payment = response.json()
            status_symbol = "✓" if payment.get('status') == 'completed' else "○"
            chat_bubble(f"""
    {status_symbol} Payment ID: {payment.get('payment_id')}
    User ID: {payment.get('user_id')}
    Loan ID: {payment.get('loan_id')}
    Amount: €{payment.get('amount'):.2f}
    Status: {payment.get('status').upper()}
    Transaction ID: {payment.get('transaction_id') or 'N/A'}
    ──────────────────────────────────────────
            """)
    
    if not found_any:
        chat_bubble("""
    No payments found in this range.
        """)
    
    chat_bubble("""
Press Enter to continue...
    """)
    input()
    payments_menu_admin()


def complete_payment_admin():
    """Completar pagamento (Admin)"""
    chat_bubble("""
    Complete Payment             
            
    Enter Payment ID:                   
    """)
    sys.stdout.write("\033[2F\033[24C")
    sys.stdout.flush()
    payment_id = input()
    
    response = requests.put(
        f"{PAYMENT_SERVICE}/payments/{payment_id}/complete",
        json={"transaction_id": "today"},
        headers=current_session.get_session()
    )
    
    chat_bubble(message_formatter(response))
    payments_menu_admin()

def modify_payment_admin():
    chat_bubble("""
    Modify Payment
            
    Payment ID:                   
    New Status (pending/completed/cancelled/failed):
    New Amount (€):
    Transaction ID:
    """)
    sys.stdout.write("\033[5F\033[18C")
    sys.stdout.flush()
    payment_id = input()
    sys.stdout.write("\033[52C")
    sys.stdout.flush()
    status = input()
    sys.stdout.write("\033[18C")
    sys.stdout.flush()
    amount = input()
    sys.stdout.write("\033[18C")
    sys.stdout.flush()
    tx_id = input()
    
    response = requests.put(
        f"{PAYMENT_SERVICE}/payments/{payment_id}",
        json={
            "status": status,
            "amount": amount,
            "tx_id": tx_id
        },
        headers=current_session.get_session()
    )
    
    chat_bubble(message_formatter(response))
    payments_menu_admin()

def delete_payment_admin():
    """Deletar pagamento (Admin)"""
    chat_bubble("""
    Delete Payment
            
    Enter Payment ID:                   
    """)
    sys.stdout.write("\033[2F\033[24C")
    sys.stdout.flush()
    payment_id = input()
    
    chat_bubble("""
    Are you sure you want to delete this payment?
        1) Yes
        2) No
    """)
    
    try:
        confirm = int(user_input())
        chat_bubble(F"{confirm}","right")
    except:
        delete_payment_admin()
        return
    
    if confirm == 1:
        response = requests.delete(
            f"{PAYMENT_SERVICE}/payments/{payment_id}",
            headers=current_session.get_session()
        )
        chat_bubble(message_formatter(response))
    
    payments_menu_admin()

def request_payment_admin():
    chat_bubble("""
    Request Payment for Overdue Loan
            
    Enter Payment ID:                   
    """)
    sys.stdout.write("\033[2F\033[24C")
    sys.stdout.flush()
    payment_id = input()
    
    response = requests.post(
        f"{PAYMENT_SERVICE}/payments/request/{payment_id}",
        headers=current_session.get_session()
    )
    
    chat_bubble(message_formatter(response))
    payments_menu_admin()
if __name__ == "__main__": 
<<<<<<< Updated upstream
    log_menu()
=======
    payments_menu_admin() 
>>>>>>> Stashed changes
