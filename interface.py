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
    chat_bubble("""
    Catalog Menu
            
    Choose an option:
        1) Browse Books
        2) Search Books
        3) View Book Details
        4) Back
    """)
    try:
        option = int(user_input())
        chat_bubble(f"{option}", "right")
    except:
        catalog_menu()
    match option:
        case 1:
            title("Library System - Browse Books")
            browse_books()
        case 2:
            title("Library System - Search Books")
            search_books()
        case 3:
            title("Library System - Book Details")
            view_book_details()
        case 4:
            main_menu_user()

def browse_books():
    response = requests.get(f"{CATALOG_SERVICE}/books")
    if response.status_code == 200:
        books = response.json()
        if books:
            for book in books:
                chat_bubble(f"""
    Book ID: {book.get('book_id')}
    Title: {book.get('title')}
    Author: {book.get('author')}
    Available Copies: {book.get('available_copies', 0)}
    
""")
        else:
            chat_bubble("No books found in the catalog.")
    else:
        chat_bubble(message_formatter(response))
    
    catalog_menu()

def search_books():
    chat_bubble("""
    Search Books
            
    Search by:
        1) Title
        2) Author
        3) Back
    """)
    try:
        option = int(user_input())
        chat_bubble(f"{option}", "right")
    except:
        search_books()
    
    if option == 3:
        catalog_menu()
        return
    
    search_term = ""
    search_type = ""
    
    match option:
        case 1:
            chat_bubble("""
    Search by Title
    
    Enter title:                              
    """)
            sys.stdout.write("\033[2F\033[19C")
            sys.stdout.flush()
            search_term = input()
            search_type = "title"
        case 2:
            chat_bubble("""
    Search by Author
    
    Enter author name:                              
    """)
            sys.stdout.write("\033[2F\033[21C")
            sys.stdout.flush()
            search_term = input()
            search_type = "author"
    
    print("\n\n")
    
    # Perform search
    response = requests.get(f"{CATALOG_SERVICE}/books/search", params={search_type: search_term})
    
    if response.status_code == 200:
        books = response.json()
        if books:
            for book in books:
                chat_bubble(f"""
    Book ID: {book.get('book_id')}
    Title: {book.get('title')}
    Author: {book.get('author')}
    Available Copies: {book.get('available_copies', 0)}
    
""")
        else:
            chat_bubble(f"No books found matching '{search_term}'.")
    else:
        chat_bubble(message_formatter(response))
    
    catalog_menu()

def view_book_details():
    chat_bubble("""
    View Book Details
    
    Enter Book ID:                              
    """)
    sys.stdout.write("\033[2F\033[17C")
    sys.stdout.flush()
    book_id = input()
    print("\n\n")
    
    response = requests.get(f"{CATALOG_SERVICE}/books/{book_id}")
    
    if response.status_code == 200:
        book = response.json()
        
        # Get copies information if available
        copies_response = requests.get(f"{CATALOG_SERVICE}/books/{book_id}/copies")
        copies_info = ""
        
        if copies_response.status_code == 200:
            copies = copies_response.json()
            copies_info = f"\n    Total Copies: {len(copies)}"
            available = sum(1 for copy in copies if copy.get('status') == 'available')
            copies_info += f"\n    Available: {available}"
        
        chat_bubble(f"""
    Book Details
    
    ID: {book.get('book_id')}
    Title: {book.get('title')}
    Author: {book.get('author')}
    Genre: {book.get('genre', 'N/A')}
    Publication Year: {book.get('publication_year', 'N/A')}
    Publisher: {book.get('publisher', 'N/A')}{copies_info}
    
""")
    else:
        chat_bubble(message_formatter(response))
    
    catalog_menu()
def payments_menu():
    pass
def account_settings():
    pass            
def main_menu_admin():
    pass

if __name__ == "__main__": 
    while True:
        log_menu()  




