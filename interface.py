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
    data = {"username": username, "email": email, "password": password}
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
    title("Library System")
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
            log_menu()
        case 2:
            register_user()
            log_menu()
        case 3:
            exit
     
log_menu()



