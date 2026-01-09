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
    
    if response.status_code == 250:
        chat_bubble(message_formatter(response))
        return False
    elif response.status_code == 200:
        data = response.json()
        
        
        current_session.update_session(
            headers={
                "User-ID": str(data.get('ID')),
                "Password-Hash": str(data.get('Password'))
            },
            role=data.get('Role')
        )
        
        
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
            if login_user():  
                if current_session.is_admin():
                    main_menu_admin()
                else:
                    main_menu_user()
            else:
                log_menu()  
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
    response = requests.get(f"{LOAN_SERVICE}/loans/{current_session.headers.get('User-ID')}", headers=current_session.get_session())
    
    if response.status_code == 404:
        chat_bubble("You have no active loans.")
        loan_menu()
        return
    
    if response.status_code != 200:
        chat_bubble("Error fetching loans.")
        loan_menu()
        return
    
    loans = response.json()
    
    active_loans = [loan for loan in loans if loan.get('status') != 'returned']
    
    if not active_loans:
        chat_bubble("You have no active loans.")
        loan_menu()
        return
    
    for loan in active_loans:
        book_id = loan.get('copy_id').split('.')[0]
        book_response = requests.get(f"{CATALOG_SERVICE}/books/{book_id}")
        book_title = book_response.json().get('title') if book_response.status_code == 200 else "Unknown"
        
        status_text = loan.get('status')
        if status_text == 'overdue':
            status_display = "OVERDUE"
        else:
            status_display = "Active"
        
        chat_bubble(f"""
    Loan {loan.get('loan_id')} - {status_display}
    Due date: {loan.get('due_date')}
    Book: {book_title}
    Copy: {loan.get('copy_id').split('.')[1]}

""")
    
    loan_menu2()
    loan_menu()

def loan_menu2():
    chat_bubble("""
    Loan Actions
    
    Select a Loan ID to edit (or 0 to go back):                                                                                      
    """)
    sys.stdout.write("\033[2F\033[50C")
    sys.stdout.flush()
    loan_id_input = input().strip()
    print("\n\n")
    
    if loan_id_input == "0":
        loan_menu()
        return
    
    try:
        loan_id = int(loan_id_input)
    except ValueError:
        chat_bubble("Invalid Loan ID.")
        loan_menu2()
        return
    
    chat_bubble("""
    Select an action
        1) Return book
        2) Change due date
        3) Cancel
""")
    try:
        option = int(user_input())
        chat_bubble(f"{option}", "right")
    except:
        loan_menu2()
        return
    
    match option:
        case 1:
            try:
                response = requests.put(
                    f"{LOAN_SERVICE}/loans/{loan_id}",
                    json={"return_date": "today", "status": "", "due_date": ""},
                    headers=current_session.get_session()
                )
                
                if response.status_code == 200:
                    chat_bubble("Book returned successfully!")
                elif response.status_code == 400:
                    try:
                        error_data = response.json()
                        chat_bubble(f"Error: {error_data.get('error', 'Unknown error')}")
                    except:
                        chat_bubble("Error: Book may already be returned.")
                else:
                    try:
                        error_data = response.json()
                        chat_bubble(f"Error: {error_data.get('error', 'Unknown error')}")
                    except:
                        chat_bubble(f"Error: Request failed")
            except Exception as e:
                chat_bubble(f"Exception: {str(e)}")
                
            check_loan_menu()
            
        case 2:
            chat_bubble("""
    Change due date
        (+/- number unit)
        Examples: "+2 weeks", "-1 day", "+3 months"
        
        Changes:                                                                                      
    """)
            sys.stdout.write("\033[2F\033[19C")
            sys.stdout.flush()
            change_str = input()
            print("\n\n")
            
            try:
                response = requests.put(
                    f"{LOAN_SERVICE}/loans/{loan_id}",
                    json={"due_date": change_str, "return_date": "", "status": ""},
                    headers=current_session.get_session()
                )
                
                if response.status_code == 200:
                    chat_bubble("Due date changed successfully!")
                else:
                    try:
                        error_data = response.json()
                        chat_bubble(f"Error: {error_data.get('error', 'Unknown error')}")
                    except:
                        chat_bubble(f"Error: Request failed")
            except Exception as e:
                chat_bubble(f"Exception: {str(e)}")
                
            check_loan_menu()
            
        case 3:
            loan_menu2()

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
    Genre:                                                                  
    Publication Year:                                                       
    """)
 
    sys.stdout.write("\033[5F\033[13C") 
    sys.stdout.flush()
    title = input()
    
    sys.stdout.write("\033[13C") 
    sys.stdout.flush()
    author = input()
    
    sys.stdout.write("\033[13C")
    sys.stdout.flush()
    genre = input()    

    sys.stdout.write("\033[24C")
    sys.stdout.flush()
    pub_year = input()
    
    print("\n\n")

    add_book_data = {
        "title": title, 
        "author": author, 
        "genre": genre if genre else None,
        "publication_year": int(pub_year) if pub_year else None
    }
    response = requests.post(f"{CATALOG_SERVICE}/books/", json=add_book_data, headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    manage_catalog_menu()
    
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
            sys.stdout.write("\033[2F\033[21C")
            sys.stdout.flush()
            search_term = input()
            search_type = "title"
            
        case 2:
            chat_bubble("""
    Search by Author
    
    Enter author name:                                                                                      
    """)
            sys.stdout.write("\033[2F\033[23C")
            sys.stdout.flush()
            search_term = input()
            search_type = "author"
            
        case 3:
            try:
                genres_response = requests.get(f"{CATALOG_SERVICE}/books/genres")
                if genres_response.status_code == 200:
                    genres = genres_response.json()
                    
                    if not genres:
                        chat_bubble("No genres found in the catalog.")
                        search_books()
                        return
                    
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
    sys.stdout.write("\033[2F\033[23C")
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
    sys.stdout.write("\033[2F\033[20C")
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
    user_id = current_session.get_session().get('User-ID')
    response = requests.get(f"{USER_SERVICE}/users/{user_id}", headers=current_session.get_session())
    
    if response.status_code != 200:
        chat_bubble("Error fetching user data.")
        account_settings()
        return
    
    current_user = response.json()
    current_username = current_user.get('name')
    
    chat_bubble(f"""
    Change Username
    
    Current Username: {current_username}
    New Username:                                                                                      
    """)
    sys.stdout.write("\033[2F\033[19C")
    sys.stdout.flush()
    new_username = input()
    
    if not new_username:
        chat_bubble("Username cannot be empty.")
        account_settings()
        return
    
    if new_username == current_username:
        chat_bubble("New username is the same as current username.")
        account_settings()
        return
    
    while not re.match(r'^[a-zA-Z0-9]{6,}', new_username):
        sys.stdout.write("\033[4F\033[2C")
        sys.stdout.flush()
        print("Invalid Username. (min. 6 characters)")
        sys.stdout.write(f"\033[2E\033[16C" + (" " * len(new_username)) + f"\033[{len(new_username)}D")
        sys.stdout.flush()
        new_username = input()
    print("\n\n")
    
    data = {"user_id": user_id, "new_username": new_username}
    response = requests.put(f"{USER_SERVICE}/users/", json=data, headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    account_settings()

def change_email():
    user_id = current_session.get_session().get('User-ID')
    response = requests.get(f"{USER_SERVICE}/users/{user_id}", headers=current_session.get_session())
    
    if response.status_code != 200:
        chat_bubble("Error fetching user data.")
        account_settings()
        return
    
    current_user = response.json()
    current_email = current_user.get('email')
    
    chat_bubble(f"""
    Change Email
    
    Current Email: {current_email}
    New Email:                                                                                      
    """)
    sys.stdout.write("\033[2F\033[16C")
    sys.stdout.flush()
    new_email = input()
    
    if not new_email:
        chat_bubble("Email cannot be empty.")
        account_settings()
        return
    
    if new_email == current_email:
        chat_bubble("New email is the same as current email.")
        account_settings()
        return
    
    while not re.match(r'^[a-zA-Z0-9._]+@[a-zA-Z]+\.[a-zA-Z]{2,}$', new_email):
        sys.stdout.write("\033[4F\033[2C")
        sys.stdout.flush()
        print("Invalid Email.")
        sys.stdout.write(f"\033[2E\033[13C" + (" " * len(new_email)) + f"\033[{len(new_email)}D")
        sys.stdout.flush()
        new_email = input()
    print("\n\n")
    
    data = {"user_id": user_id, "new_email": new_email}
    response = requests.put(f"{USER_SERVICE}/users/", json=data, headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    account_settings()

def change_password():
    chat_bubble("""
    Change Password
    
    New Password:                                                                                      
    """)
    sys.stdout.write("\033[2F\033[19C")
    sys.stdout.flush()
    new_password = getpass.getpass("")  
    
    if not new_password:
        chat_bubble("Password cannot be empty.")
        account_settings()
        return
    
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
    
    if response.status_code == 200:
        chat_bubble(message_formatter(response))
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
    
    Select Language:
        1) English
        2) Portuguese
        3) Back
    """)
    try:
        lang_option = int(user_input())
        chat_bubble(f"{lang_option}", "right")
    except:
        import_book_from_google()
        return
    
    if lang_option == 3:
        manage_catalog_menu()
        return
    
    language = ""
    match lang_option:
        case 1:
            language = "en"
        case 2:
            language = "pt"
        case _:
            import_book_from_google()
            return
    
    chat_bubble("""
    Search by:
        1) Title
        2) Author
        3) Back
    """)
    try:
        option = int(user_input())
        chat_bubble(f"{option}", "right")
    except:
        import_book_from_google()
        return
    
    if option == 3:
        import_book_from_google()
        return
    
    search_type = ""
    match option:
        case 1:
            search_type = "title"
            chat_bubble("""
    Search by Title
    
    Enter title:                                                                                      
    """)
            sys.stdout.write("\033[2F\033[19C")
            sys.stdout.flush()
        case 2:
            search_type = "author"
            chat_bubble("""
    Search by Author
    
    Enter author:                                                                                      
    """)
            sys.stdout.write("\033[2F\033[20C")
            sys.stdout.flush()
        case _:
            import_book_from_google()
            return
    
    search_query = input()
    print("\n\n")
    
    if not search_query:
        chat_bubble("Search term cannot be empty.")
        import_book_from_google()
        return
    
    chat_bubble("Searching Google Books API...")
    
    try:
        response = requests.post(
            f"{CATALOG_SERVICE}/books/search_google",
            json={"query": search_query, "type": search_type, "language": language},
            headers=current_session.get_session()
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                chat_bubble("No books found.")
                import_book_from_google()
                return
            
            for book in results:
                chat_bubble(f"""
    {book['index']}) {book['title']}
       Author: {book['author']}
       ISBN: {book.get('isbn', 'N/A')}
       Genre: {book.get('genre', 'N/A')}
       Year: {book.get('publication_year', 'N/A')}
""")
            
            chat_bubble(f"""
    Select a book to import (1-{len(results)}) or 0 to cancel:
""")
            
            try:
                choice = int(user_input())
                chat_bubble(f"{choice}", "right")
                
                if choice == 0:
                    import_book_from_google()
                    return
                
                if 1 <= choice <= len(results):
                    selected_book = results[choice - 1]
                    
                    import_response = requests.post(
                        f"{CATALOG_SERVICE}/books/import_selected",
                        json=selected_book,
                        headers=current_session.get_session()
                    )
                    
                    if import_response.status_code == 201:
                        import_data = import_response.json()
                        book = import_data.get('book', {})
                        chat_bubble(f"""
    Book Imported Successfully!
    
    ID: {import_data.get('id')}
    Title: {book.get('title')}
    Author: {book.get('author')}
    ISBN: {book.get('isbn', 'N/A')}
    Genre: {book.get('genre', 'N/A')}
    Year: {book.get('publication_year', 'N/A')}
""")
                    else:
                        try:
                            error_data = import_response.json()
                            chat_bubble(f"Error: {error_data.get('error', 'Unknown error')}")
                        except:
                            chat_bubble(f"Error: Request failed")
                else:
                    chat_bubble("Invalid selection.")
            except:
                chat_bubble("Invalid input.")
                
        elif response.status_code == 404:
            chat_bubble("No books found matching your search.")
        else:
            try:
                error_data = response.json()
                chat_bubble(f"Error: {error_data.get('error', 'Unknown error')}")
            except:
                chat_bubble(f"Error: Request failed with status {response.status_code}")
    except Exception as e:
        chat_bubble(f"Error: {str(e)}")
    
    manage_catalog_menu()

def add_book_copy():
    chat_bubble("""
    Add Book Copy
    
    Enter Book ID:                                                                                      
    """)
    sys.stdout.write("\033[2F\033[20C")
    sys.stdout.flush()
    book_id = input()
    print("\n\n")
    
    chat_bubble("Searching for editions...")
    
    try:
        response = requests.get(
            f"{CATALOG_SERVICE}/books/{book_id}/search_editions",
            headers=current_session.get_session()
        )
        
        if response.status_code == 200:
            data = response.json()
            editions = data.get('editions', [])
            
            if not editions:
                chat_bubble("No editions found. Creating copy without ISBN...")
                
                chat_bubble("""
    Enter Rent Price:                                                                                      
    """)
                sys.stdout.write("\033[2F\033[23C")
                sys.stdout.flush()
                rent_price = input()
                print("\n\n")
                
                copy_data = {"rent_price": float(rent_price)}
                copy_response = requests.post(
                    f"{CATALOG_SERVICE}/books/{book_id}/copy/",
                    json=copy_data,
                    headers=current_session.get_session()
                )
                chat_bubble(message_formatter(copy_response))
                manage_catalog_menu()
                return
            
            for edition in editions:
                chat_bubble(f"""
    {edition['index']}) ISBN: {edition['isbn']} ({edition['isbn_type']})
       Edition: {edition['edition_info']}
       Full Title: {edition['full_title']}
""")
            
            chat_bubble(f"""
    Select an edition (1-{len(editions)}) or 0 to cancel:
""")
            
            try:
                choice = int(user_input())
                chat_bubble(f"{choice}", "right")
                
                if choice == 0:
                    manage_catalog_menu()
                    return
                
                if 1 <= choice <= len(editions):
                    selected_edition = editions[choice - 1]
                    
                    chat_bubble("""
    Enter Rent Price (€/day):                                                                                      
    """)
                    sys.stdout.write("\033[2F\033[27C")
                    sys.stdout.flush()
                    rent_price = input()
                    print("\n\n")
                    
                    copy_data = {
                        "rent_price": float(rent_price),
                        "isbn": selected_edition['isbn'],
                        "edition_info": selected_edition['edition_info']
                    }
                    
                    copy_response = requests.post(
                        f"{CATALOG_SERVICE}/books/{book_id}/copy/",
                        json=copy_data,
                        headers=current_session.get_session()
                    )
                    
                    if copy_response.status_code == 201:
                        copy_result = copy_response.json()
                        chat_bubble(f"""
    Copy Created Successfully!
    
    Copy ID: {copy_result.get('copy_id')}
    ISBN: {selected_edition['isbn']}
    Edition: {selected_edition['edition_info']}
    Rent Price: €{rent_price}/day
""")
                    else:
                        chat_bubble(message_formatter(copy_response))
                else:
                    chat_bubble("Invalid selection.")
            except:
                chat_bubble("Invalid input.")
                
        else:
            try:
                error_data = response.json()
                chat_bubble(f"Error: {error_data.get('error', 'Unknown error')}")
            except:
                chat_bubble(f"Error: Request failed")
    except Exception as e:
        chat_bubble(f"Error: {str(e)}")
    
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
    sys.stdout.write("\033[2F\033[45C")
    sys.stdout.flush()
    user_id = input().strip()
    print("\n\n")
    
    try:
        if user_id:
            response = requests.get(f"{LOAN_SERVICE}/loans/{user_id}", headers=current_session.get_session())
            
            if response.status_code == 200:
                loans = response.json()
            elif response.status_code == 404:
                chat_bubble("No loans found for this user.")
                main_menu_admin()
                return
            else:
                try:
                    error_data = response.json()
                    chat_bubble(f"Error: {error_data.get('error', 'Unknown error')}")
                except:
                    chat_bubble(f"Error: Request failed with status {response.status_code}")
                main_menu_admin()
                return
        else:
            response = requests.get(f"{LOAN_SERVICE}/loans/all", headers=current_session.get_session())
            
            if response.status_code == 200:
                loans = response.json()
                
                if isinstance(loans, dict) and 'message' in loans:
                    chat_bubble(loans['message'])
                    main_menu_admin()
                    return
            else:
                try:
                    error_data = response.json()
                    chat_bubble(f"Error: {error_data.get('error', 'Unknown error')}")
                except:
                    chat_bubble(f"Error: Request failed with status {response.status_code}")
                main_menu_admin()
                return
        
        if loans and isinstance(loans, list):
            for loan in loans:
                book_id = loan.get('copy_id').split('.')[0]
                book_response = requests.get(f"{CATALOG_SERVICE}/books/{book_id}")
                book_title = book_response.json().get('title') if book_response.status_code == 200 else "Unknown"
                
                user_id_loan = loan.get('user_id')
                user_response = requests.get(f"{USER_SERVICE}/users/{user_id_loan}", headers=current_session.get_session())
                username = user_response.json().get('name') if user_response.status_code == 200 else "Unknown"
                
                chat_bubble(f"""
    Loan ID: {loan.get('loan_id')}
    User ID: {user_id_loan}
    Username: {username}
    Copy ID: {loan.get('copy_id')}
    Book: {book_title}
    Loan Date: {loan.get('loan_date')}
    Due Date: {loan.get('due_date')}
    Return Date: {loan.get('return_date') if loan.get('return_date') else 'Not returned yet'}
    Status: {loan.get('status')}
""")
        else:
            chat_bubble("No loans found.")
            
    except Exception as e:
        chat_bubble(f"Error: {str(e)}")
    
    main_menu_admin()

def view_all_payments():
    chat_bubble("""
    View All Payments
    
    Enter Payment ID to view details:                              
    """)
    sys.stdout.write("\033[2F\033[40C")
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




