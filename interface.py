import requests
import getpass
import sys
import re
from shared_utils.ui_utils import chat_bubble,title,user_input,message_formatter,json_formatter

if sys.platform == 'win32':
    import msvcrt


def password_asterisco():
   
    password = ""
    
    if sys.platform == 'win32':
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
PAYMENT_SERVICE = "http://localhost:5004/payments"

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
    try: 
        request = requests.post(f"{USER_SERVICE}/users/login", json=data)
        chat_bubble(message_formatter(request))
        if request.status_code == 250:
            chat_bubble(message_formatter(request))
            login_user()
        elif request.status_code == 200:
            data = request.json()
            
            current_session.update_session(
                headers={
                "User-ID": str(data.get('ID')),
                "Password-Hash": str(data.get('Password'))
            },
            role=data.get('Role'))
            chat_bubble(message_formatter(request))
            return True
            
            

    except Exception as e:
        chat_bubble(f"Error \n          couldnt connect to the server {str(e)}")
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
            if login_user()==True:
                main_menu_user()
            else: 
                login_user() 
        case 2:
            register_user()
            log_menu()
        case 3:
            sys.exit()

def main_menu_user():
    admin_option = "\n        6) Admin Panel" if current_session.is_admin() else ""
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
    if not time or not copyid:
        chat_bubble("""Error:
Insert valid numbers""")
        loan_book_menu() 
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
    Status: {loan.get('status')}
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
    3) Return to menu
""")    
    option = int(input())
    match option:
        case 1:
            requests.put(f"{LOAN_SERVICE}/loans/{loan_id}",json= {"return_date": "today"})
            chat_bubble("""Success:
                        Book has been returned.""")
            chat_bubble("""Proceed to Payments?
                        1) Proceed
                        2) Pay later
                        """)
            option2 = int(input())
            match option2:
                case 1:
                    complete_user_payment(paymentid=loan_id)
                case 2:
                    pass
        case 2:
            chat_bubble("""
Change due date
    (+/-, #, days,week,months)                                            
    Changes:
""")
            
            change_str = input()
            requests.put(f"{LOAN_SERVICE}/loans/{loan_id}", json = {"due_date": change_str,"return_date": "","status":""})
        case 3:
            main_menu_user()

def catalog_menu():
    chat_bubble("""
    Catalog Menu
            
    Choose an option:
        1) Search Books
        2) View Book Details
        3) View All books
        4) Back
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
            view_all_books()
        case 4:
            main_menu_user()

def add_book():
    chat_bubble("""
    Add New Book
    
    Title:                                                                  
    Author:                                                                                                                                 
    Genre:                                                                  
    Publication Year:                                                       
    """)
 
    sys.stdout.write("\033[6F\033[13C") 
    sys.stdout.flush()
    title = input()
    
    sys.stdout.write("\033[\033[13C") 
    sys.stdout.flush()
    author = input()
       
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
    
""")
    else:
        chat_bubble(message_formatter(response))
    
    catalog_menu()

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
    sys.stdout.write("\033[2F\033[19C")
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
    sys.stdout.write("\033[2F\033[16C")
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
    sys.stdout.write("\033[2F\033[19C")
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
            title("Library System - Manage Payments")
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

def payments_menu():
    chat_bubble("""Payments Menu""")
    try:
        if current_session.is_admin():
                payments_menu_admin()
        else:
            payments_menu_user()
    except:   
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
        payments_menu_user()
    
    match option:
        case 1:
            title("Library System - Pending Payments")
            view_user_payments()
        case 2:
            title("Library System - Complete Payment")
            complete_user_payment(paymentid=None)
        case 3:
            main_menu_user()

def view_user_payments():
    chat_bubble("""View pending payments from user""")
    user_id = current_session.headers.get('User-ID')
    
    
    response = requests.get(
        f"{LOAN_SERVICE}/loans/{user_id}", 
        headers=current_session.get_session()
    )
    
    if response.status_code != 200:
        chat_bubble(message_formatter(response))
        payments_menu_user()
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
    
    Amount to Pay: €{payment.get('amount'):.2f}
    Payment Status: {payment.get('status').upper()}
    ──────────────────────────────────────────
            """)
    
    chat_bubble("""Press Enter to continue...""")
    input()
    payments_menu_user()

def complete_user_payment(paymentid):
    if not paymentid:
        chat_bubble("""
        Complete Payment
                
        Enter Payment ID:                   
        """)
        sys.stdout.write("\033[2F\033[24C")
        sys.stdout.flush()
        payment_id = input()
    else:
        payment_id = paymentid
    
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
    Amount: €{payment_data.get('amount'):.2f}
    
    Do you want to complete this payment?
        1) Yes
        2) No
    """)
    
    try:
        confirm = int(user_input())
        chat_bubble(F"{confirm}","right")
    except:
        complete_user_payment(paymentid=None)
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

if __name__ == "__main__": 
    log_menu()  



