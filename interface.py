import requests
import getpass
import sys
import re
from shared_utils.ui_utils import chat_bubble,title,user_input,message_formatter,json_formatter
class UserSession:
    def __init__(self):
        self.headers = {}
    def update_session(self,headers):
        self.headers = headers
    def get_session(self):
        return self.headers
current_session = UserSession()
USER_SERVICE = "http://localhost:5001"
CATALOG_SERVICE = "http://localhost:5002"
LOAN_SERVICE = "http://localhost:5003"
PAYMENT_SERVICE = "http://localhost:5004"
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
    password = getpass.getpass("")
    while not re.match(r'^[a-zA-Z0-9._%+\-!?"#$%&/()]{8,}$', password):
        sys.stdout.write("\033[4F\033[2C")
        sys.stdout.flush()
        print("Invalid Password. (min. 8 characters)")
        sys.stdout.write(f"\033[2E\033[16C" + (" " * len(password)) + f"\033[{len(password)}D")
        sys.stdout.flush()
        password = getpass.getpass("")
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
    password = getpass.getpass("")
    while not re.match(r'^[a-zA-Z0-9._%+\-!?"#$%&/()]{8,}$', password):
        sys.stdout.write("\033[3F\033[2C")
        sys.stdout.flush()
        print("Invalid Password. (min. 8 characters)")
        sys.stdout.write(f"\033[1E\033[13C" + (" " * len(password)) + f"\033[{len(password)}D")
        sys.stdout.flush()
        password = getpass.getpass("")
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
            exit
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
    pass
def account_settings():
    pass            
def main_menu_admin():
    pass

if __name__ == "__main__": 
    while True:
        log_menu()  




