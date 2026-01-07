import requests
import getpass
import sys
import re
from shared_utils.ui_utils import chat_bubble,title,user_input,message_formatter,json_formatter

class UserSession:
    def __init__(self):
        self.headers = {}
        self.role = None
    
    def update_session(self, headers, role=None):
        self.headers = headers
        if role:
            self.role = role
    
    def get_session(self):
        return self.headers
    
    def get_role(self):
        return self.role
    
    def is_admin(self):
        return self.role == 'admin'
    
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
    response = requests.post(f"{USER_SERVICE}/users/login", json=data)
    
    # DEBUG: Vamos ver o que o backend está a retornar
    print(f"\n=== DEBUG ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response JSON: {response.json()}")
    print(f"=============\n")
    
    if response.status_code == 250:
        chat_bubble(message_formatter(response))
        return False
    elif response.status_code == 200:
        data = response.json()
        
        # DEBUG: Ver o que estamos a receber
        print(f"\n=== DEBUG ===")
        print(f"ID: {data.get('ID')}")
        print(f"Password: {data.get('Password')}")
        print(f"Role: {data.get('Role')}")
        print(f"=============\n")
        
        current_session.update_session(
            headers={
                "User-ID": str(data.get('ID')),
                "Password-Hash": str(data.get('Password'))
            },
            role=data.get('Role')
        )
        
        # DEBUG: Ver o que ficou guardado na sessão
        print(f"\n=== DEBUG ===")
        print(f"Session Role: {current_session.get_role()}")
        print(f"Is Admin: {current_session.is_admin()}")
        print(f"=============\n")
        
        chat_bubble(message_formatter(response))
        return True
    else:
        chat_bubble(message_formatter(response))
        return False

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
        chat_bubble(f"{option}","right")
    except:
        log_menu()
        return
    
    match option:
        case 1:
            if login_user():  # Se login for bem-sucedido
                if current_session.is_admin():
                    main_menu_admin()
                else:
                    main_menu_user()
            else:
                log_menu()  # Volta ao menu de login se falhar
        case 2:
            register_user()
            log_menu()
        case 3:
            sys.exit()

def main_menu_user():
    admin_option = "\n        6) Admin Panel" if current_session.is_admin() else ""
    logout_number = "6" if not current_session.is_admin() else "5"
    
    menu_text = f"""
    Main Library Menu
            
    Choose an option:
        1) Loans
        2) Catalog
        3) Payments
        4) Account Settings
        5) Log-out{admin_option}
    """
    
    chat_bubble(menu_text)
    try:
        option = int(user_input())
        chat_bubble(f"{option}","right")
    except:
        main_menu_user()
        return
        
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
            current_session.update_session(headers={}, role=None)
            current_session.role = None
            log_menu()
        case 6:
            if current_session.is_admin():
                title("Library System - Admin Panel")
                main_menu_admin()
            else:
                main_menu_user()

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
        1) Search Books
        2) View Book Details
        3) Back
    """)
    try:
        option = int(user_input())
        chat_bubble(f"{option}", "right")
    except:
        catalog_menu()
    match option:
        case 1:
            title("Library System - Search Books")
            search_books()
        case 2:
            title("Library System - Book Details")
            view_book_details()
        case 3:
            main_menu_user()

def add_book():
    chat_bubble("""
    Add New Book
    
    Title:                                                                  
    Author:                                                                 
    ISBN:                                                                   
    Genre:                                                                  
    Publication Year:                                                       
    """)
 
    sys.stdout.write("\033[6F\033[13C") 
    sys.stdout.flush()
    title = input()
    
    sys.stdout.write("\033[\033[13C") 
    sys.stdout.flush()
    author = input()
    
    sys.stdout.write("\033[\033[12C")
    sys.stdout.flush()
    isbn = input()
    
    sys.stdout.write("\033[\033[13C")
    sys.stdout.flush()
    genre = input()    

    sys.stdout.write("\033[\033[24C")
    sys.stdout.flush()
    pub_year = input()
    
    print("\n\n")

    add_book_data = {
        "title": title, 
        "author": author, 
        "isbn": isbn,
        "genre": genre if genre else None,
        "publication_year": int(pub_year) if pub_year else None
    }
    response = requests.post(f"{CATALOG_SERVICE}/books/", json=add_book_data, headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    catalog_menu()
    
def search_books():
    chat_bubble("""
    Search Books
            
    Search by:
        1) Title
        2) Author
        3) Genre
        4) Back
    """)
    try:
        option = int(user_input())
        chat_bubble(f"{option}", "right")
    except:
        search_books()
        return
    
    if option == 4:
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
            
        case 3:
            # Buscar lista de géneros
            try:
                genres_response = requests.get(f"{CATALOG_SERVICE}/books/genres")
                if genres_response.status_code == 200:
                    genres = genres_response.json()
                    
                    if not genres:
                        chat_bubble("No genres found in the catalog.")
                        search_books()
                        return
                    
                    # Construir menu dinâmico com os géneros
                    genre_menu = "    Select Genre\n\n"
                    for idx, genre in enumerate(genres, 1):
                        genre_menu += f"        {idx}) {genre}\n"
                    genre_menu += f"        {len(genres)+1}) Back"
                    
                    chat_bubble(genre_menu)
                    
                    try:
                        genre_choice = int(user_input())
                        chat_bubble(f"{genre_choice}", "right")
                        
                        if genre_choice == len(genres) + 1:
                            search_books()
                            return
                        elif 1 <= genre_choice <= len(genres):
                            search_term = genres[genre_choice - 1]
                            search_type = "genre"
                        else:
                            chat_bubble("Invalid option.")
                            search_books()
                            return
                    except:
                        search_books()
                        return
                else:
                    chat_bubble("Error loading genres.")
                    search_books()
                    return
            except Exception as e:
                chat_bubble(f"Error: {str(e)}")
                search_books()
                return
    
    print("\n\n")
    
    # Perform search
    try:
        response = requests.get(f"{CATALOG_SERVICE}/books/search", params={search_type: search_term})
        
        if response.status_code == 200:
            books = response.json()
            if books:
                for book in books:
                    chat_bubble(f"""
    Book ID: {book.get('id')}
    Title: {book.get('title')}
    Author: {book.get('author')}
    ISBN: {book.get('isbn', 'N/A')}
    Genre: {book.get('genre', 'N/A')}
    Publication Year: {book.get('publication_year', 'N/A')}
    Total Copies: {book.get('total_copies', 0)}
    Available Copies: {book.get('available_copies', 0)}
    
""")
            else:
                chat_bubble(f"No books found matching '{search_term}'.")
        else:
            try:
                error_data = response.json()
                chat_bubble(f"Error: {error_data.get('error', 'Unknown error')}")
            except:
                chat_bubble(f"Error: Request failed with status {response.status_code}")
    except Exception as e:
        chat_bubble(f"Error: {str(e)}")
    
    catalog_menu()

def view_book_details():
    chat_bubble("""
    View Book Details
    
    Enter Book ID:                              
    """)
    sys.stdout.write("\033[2F\033[20C")
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
    chat_bubble("""
    Payments Menu
            
    Choose an option:
        1) View Payment Details
        2) View Payments by Loan
        3) Back
    """)
    try:
        option = int(user_input())
        chat_bubble(f"{option}", "right")
    except:
        payments_menu()
    match option:
        case 1:
            view_payment_details()
        case 2:
            view_payment_by_loan()
        case 3:
            main_menu_user()

def view_payment_details():
    chat_bubble("""
    View Payment Details
    
    Enter Payment ID:                              
    """)
    sys.stdout.write("\033[2F\033[20C")
    sys.stdout.flush()
    payment_id = input()
    print("\n\n")
    
    response = requests.get(f"{PAYMENT_SERVICE}/payments/{payment_id}", headers=current_session.get_session())
    if response.status_code == 200:
        payment = response.json()
        chat_bubble(f"""
    Payment Details
    
    Payment ID: {payment.get('payment_id')}
    User ID: {payment.get('user_id')}
    Loan ID: {payment.get('loan_id')}
    Amount: €{payment.get('amount')}
    Status: {payment.get('status')}
    Transaction ID: {payment.get('transaction_id')}
""")
    else:
        chat_bubble(message_formatter(response))
    payments_menu()

def view_payment_by_loan():
    chat_bubble("""
    View Payment by Loan
    
    Enter Loan ID:                              
    """)
    sys.stdout.write("\033[2F\033[17C")
    sys.stdout.flush()
    loan_id = input()
    print("\n\n")
    
    response = requests.get(f"{PAYMENT_SERVICE}/payments/loan_lookup", json={"loan_id": loan_id}, headers=current_session.get_session())
    if response.status_code == 200:
        payment = response.json()
        chat_bubble(f"""
    Payment Details for Loan {loan_id}
    
    Payment ID: {payment.get('payment_id')}
    User ID: {payment.get('user_id')}
    Amount: €{payment.get('amount')}
    Status: {payment.get('status')}
    Transaction ID: {payment.get('transaction_id')}
""")
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
    chat_bubble("""
    Change Username
    
    New Username:                              
    """)
    sys.stdout.write("\033[2F\033[16C")
    sys.stdout.flush()
    new_username = input()
    while not re.match(r'^[a-zA-Z0-9]{6,}', new_username):
        sys.stdout.write("\033[3F\033[2C")
        sys.stdout.flush()
        print("Invalid Username. (min. 6 characters)")
        sys.stdout.write(f"\033[1E\033[16C" + (" " * len(new_username)) + f"\033[{len(new_username)}D")
        sys.stdout.flush()
        new_username = input()
    print("\n\n")
    
    user_id = current_session.get_session().get('User-ID')
    data = {"user_id": user_id, "new_username": new_username}
    response = requests.put(f"{USER_SERVICE}/users/", json=data, headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    account_settings()

def change_email():
    chat_bubble("""
    Change Email
    
    New Email:                              
    """)
    sys.stdout.write("\033[2F\033[13C")
    sys.stdout.flush()
    new_email = input()
    while not re.match(r'^[a-zA-Z0-9._]+@[a-zA-Z]+\.[a-zA-Z]{2,}$', new_email):
        sys.stdout.write("\033[3F\033[2C")
        sys.stdout.flush()
        print("Invalid Email.")
        sys.stdout.write(f"\033[1E\033[13C" + (" " * len(new_email)) + f"\033[{len(new_email)}D")
        sys.stdout.flush()
        new_email = input()
    print("\n\n")
    
    user_id = current_session.get_session().get('User-ID')
    data = {"user_id": user_id, "new_email": new_email}
    response = requests.put(f"{USER_SERVICE}/users/", json=data, headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    account_settings()

def change_password():
    chat_bubble("""
    Change Password
    
    New Password:                              
    """)
    sys.stdout.write("\033[2F\033[16C")
    sys.stdout.flush()
    new_password = getpass.getpass("")
    while not re.match(r'^[a-zA-Z0-9._%+\-!?"#$%&/()]{8,}$', new_password):
        sys.stdout.write("\033[4F\033[2C")
        sys.stdout.flush()
        print("Invalid Password. (min. 8 characters)")
        sys.stdout.write(f"\033[2E\033[16C" + (" " * len(new_password)) + f"\033[{len(new_password)}D")
        sys.stdout.flush()
        new_password = getpass.getpass("")
    print("\n\n")
    
    user_id = current_session.get_session().get('User-ID')
    data = {"user_id": user_id, "new_password": new_password}
    response = requests.put(f"{USER_SERVICE}/users/", json=data, headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    account_settings() 

def main_menu_admin():
    chat_bubble("""
    Admin Menu
            
    Choose an option:
        1) Manage Users
        2) Manage Catalog
        3) View All Loans
        4) View All Payments
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
            view_all_payments()
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
    sys.stdout.write("\033[2F\033[17C")
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
        1) Add Book
        2) Add Book Copy
        3) Remove Book
        4) Remove Book Copy
        5) View All Books
        6) Back
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
            add_book_copy()
        case 3:
            remove_book()
        case 4:
            remove_book_copy()
        case 5:
            view_all_books()
        case 6:
            main_menu_admin()

def add_book_copy():
    chat_bubble("""
    Add Book Copy
    
    Enter Book ID:                              
    Enter Rent Price:                              
    """)
    sys.stdout.write("\033[3F\033[20C")
    sys.stdout.flush()
    book_id = input()
    sys.stdout.write("\033[23C")
    sys.stdout.flush()
    rent_price = input()
    print("\n\n")
    
    data = {"rent_price": rent_price}
    response = requests.post(f"{CATALOG_SERVICE}/books/{book_id}/copy/", json=data, headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    manage_catalog_menu()

def remove_book():
    chat_bubble("""
    Remove Book
    
    Enter Book ID:                                                                                                           
    """)
    sys.stdout.write("\033[2F\033[20C")
    sys.stdout.flush()
    book_id = input()
    print("\n\n")
    
    # Confirmação antes de eliminar
    chat_bubble(f"""
    Are you sure you want to delete Book ID {book_id}?
    This will also delete ALL copies of this book!
    
    Type 'yes' to confirm:                                                                                                           
    """)
    sys.stdout.write("\033[2F\033[28C")
    sys.stdout.flush()
    confirmation = input()
    print("\n\n")
    
    if confirmation.lower() == 'yes':
        response = requests.delete(f"{CATALOG_SERVICE}/books/{book_id}", headers=current_session.get_session())
        chat_bubble(message_formatter(response))
    else:
        chat_bubble("Operation cancelled.")
    
    manage_catalog_menu()

def remove_book_copy():
    chat_bubble("""
    Remove Book Copy
    
    Enter Copy ID (book_id.copy_num):                       
    """)
    sys.stdout.write("\033[2F\033[40C")
    sys.stdout.flush()
    copy_id = input()
    print("\n\n")
    
    response = requests.delete(f"{CATALOG_SERVICE}/books/copy/{copy_id}", headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    manage_catalog_menu()

def view_all_books():
    response = requests.get(f"{CATALOG_SERVICE}/books/")
    if response.status_code == 200:
        books = response.json()
        for book in books:
            chat_bubble(f"""
    Book ID: {book.get('id')}
    Title: {book.get('title')}
    Author: {book.get('author')}
    ISBN: {book.get('isbn', 'N/A')}
    Genre: {book.get('genre', 'N/A')}
    Publication Year: {book.get('publication_year', 'N/A')}
    Total Copies: {book.get('total_copies')}
    Available: {book.get('available_copies')}
""")
    else:
        chat_bubble(message_formatter(response))
    manage_catalog_menu()

def view_all_loans():
    chat_bubble("""
    View All Loans
    
    Enter User ID (or leave blank for all):                              
    """)
    sys.stdout.write("\033[2F\033[42C")
    sys.stdout.flush()
    user_id = input()
    print("\n\n")
    
    if user_id:
        response = requests.get(f"{LOAN_SERVICE}/loans/{user_id}", headers=current_session.get_session())
    else:
        # Esta funcionalidade precisa de um endpoint no backend para listar todos os loans
        chat_bubble("Feature not yet implemented for all loans.")
        main_menu_admin()
        return
    
    if response.status_code == 200:
        loans = response.json()
        for loan in loans:
            book_id = loan.get('copy_id').split('.')[0]
            book_response = requests.get(f"{CATALOG_SERVICE}/books/{book_id}")
            book_title = book_response.json().get('title') if book_response.status_code == 200 else "Unknown"
            
            chat_bubble(f"""
    Loan ID: {loan.get('loan_id')}
    User ID: {loan.get('user_id')}
    Copy ID: {loan.get('copy_id')}
    Book: {book_title}
    Loan Date: {loan.get('loan_date')}
    Due Date: {loan.get('due_date')}
    Status: {loan.get('status')}
""")
    else:
        chat_bubble(message_formatter(response))
    main_menu_admin()

def view_all_payments():
    chat_bubble("""
    View All Payments
    
    Enter Payment ID to view details:                              
    """)
    sys.stdout.write("\033[2F\033[36C")
    sys.stdout.flush()
    payment_id = input()
    print("\n\n")
    
    if payment_id:
        response = requests.get(f"{PAYMENT_SERVICE}/payments/{payment_id}", headers=current_session.get_session())
        if response.status_code == 200:
            payment = response.json()
            chat_bubble(f"""
    Payment ID: {payment.get('payment_id')}
    User ID: {payment.get('user_id')}
    Loan ID: {payment.get('loan_id')}
    Amount: €{payment.get('amount')}
    Status: {payment.get('status')}
    Transaction ID: {payment.get('transaction_id')}
""")
        else:
            chat_bubble(message_formatter(response))
    main_menu_admin()

if __name__ == "__main__": 
    log_menu()  




