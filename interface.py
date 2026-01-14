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
user_service = "http://localhost:5001"
catalog_service = "http://localhost:5002"
loan_service = "http://localhost:5003"
payment_service = "http://localhost:5004"

def register_user():
    chat_bubble(
    """Register 

    Email:                                      
    Username: 
    Password: """
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
        sys.stdout.write(f"\033[2E\033[16C" + (" " * len(password)) + f"\033[{len(password)}D")
        sys.stdout.flush()
        password = password_asterisco()
    print("\n\n")
    data = {"username": username, "email": email, "password": password}
    request = requests.post(f"{user_service}/users/register", json=data)
    chat_bubble(message_formatter(request))

def login_user():
    chat_bubble(
        """Login

 Username:                              
 Password:""")
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
        sys.stdout.write(f"\033[1E\033[13C" + (" " * len(password)) + f"\033[{len(password)}D")
        sys.stdout.flush()
        password = password_asterisco()
    print("\n\n")
    
    data = {"username": username, "password": password}
    try: 
        request = requests.post(f"{user_service}/users/login", json=data)

        if request.status_code == 200:
            data = request.json()
            
            current_session.update_session(
                headers={
                "User-ID": str(data.get('ID')),
                "Password-Hash": str(data.get('Password'))
            },
            role=data.get('Role'))
            chat_bubble(message_formatter(request))
            return True
        else:
            chat_bubble(message_formatter(request))
            return login_user()
            
            

    except Exception as e:
        chat_bubble(f"Error: \ncouldnt connect to the server {str(e)}")
def log_menu():
    chat_bubble("""Welcome to the Library
            
    Choose an option:
        1) Log-in
        2) Register
        3) Exit     """)
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
    menu_text = f"""Main Library Menu
            
    Choose an option:
        1) Loans
        2) Catalog
        3) Payments
        4) Account Settings
        5) Log-out{admin_option}"""
    
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
    chat_bubble("""Loans Menu        
    Choose an option:
        1) New Loan
        2) Check Active Loans
        3) Check Returned Loans
        4) Check Overdue Loans
        5) Back""")
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
            title("Library System - Check Active Loans")
            check_loan_menu('active')
        case 3:
            title("Library System - Check Returned Loans")
            check_loan_menu('returned')
        case 4:
            title("Library System - Check Overdue Loans")
            check_loan_menu('overdue')
        case 5:
            main_menu_user()
def loan_book_menu(user_id=None):
    chat_bubble("""Loan a Book
    
    Enter Book ID:         """)
    sys.stdout.write("\033[2F\033[20C")
    sys.stdout.flush()
    book_id = input()
    print("\n\n")
    
    if not book_id:
        chat_bubble("Book ID cannot be empty.")
        loan_menu()
        return
    
    try:
        book_response = requests.get(f"{catalog_service}/books/{book_id}")
        if book_response.status_code != 200:
            chat_bubble("Book not found.")
            loan_menu()
            return
        
        book = book_response.json()
        
        chat_bubble(
            f"""    Book: {book.get('title')}
    Author: {book.get('author')}
    
    Searching for available copies...""")
        
        copies_response = requests.get(f"{catalog_service}/books/{book_id}/available_copies")
        
        if copies_response.status_code == 404:
            chat_bubble("No available copies for this book.")
            loan_menu()
            return
        
        if copies_response.status_code != 200:
            chat_bubble("Error fetching available copies.")
            loan_menu()
            return
        
        copies_data = copies_response.json()
        copies = copies_data.get('copies', [])
        
        if not copies:
            chat_bubble("No available copies for this book.")
            loan_menu()
            return
        
        for idx, copy in enumerate(copies, 1):
            chat_bubble(
f"""        {idx}) Copy ID: {copy['copy_id']}
       ISBN: {copy['isbn']}
       Edition: {copy['edition_info']}
       Price: €{copy['rent_price']}/day""")
        
        chat_bubble(f"""Select a copy (1-{len(copies)}) or 0 to cancel:""")
        
        try:
            choice = int(user_input())
            chat_bubble(f"{choice}", "right")
            
            if choice == 0:
                loan_menu()
                return
            
            if not (1 <= choice <= len(copies)):
                chat_bubble("Invalid selection.")
                loan_menu()
                return
            
            selected_copy = copies[choice - 1]
            
            chat_bubble("""Loan Duration (# weeks/days/months)
    Enter duration :                                 """)
            sys.stdout.write("\033[2F\033[22C")
            sys.stdout.flush()
            loan_time = input()
            print("\n\n")
            
            if not loan_time:
                chat_bubble("Duration cannot be empty.")
                loan_menu()
                return
            
            parts = loan_time.strip().split()
            if len(parts) != 2:
                chat_bubble("Invalid format. Use: '1 week', '2 weeks', '5 days'")
                loan_menu()
                return
            
            try:
                amount = int(parts[0])
                unit = parts[1]
            except:
                chat_bubble("Invalid duration format.")
                loan_menu()
                return
            
            multipliers = {'month': 30, 'months': 30, 'week': 7, 'weeks': 7, 'day': 1, 'days': 1}
            if unit.lower() not in multipliers:
                chat_bubble("Invalid unit. Use: days, weeks, or months")
                loan_menu()
                return
            
            total_days = amount * multipliers[unit.lower()]
            total_cost = total_days * selected_copy['rent_price']
            
            chat_bubble(
f"""Loan Summary
    
    Book: {book.get('title')}
    Copy: {selected_copy['copy_id']}
    Edition: {selected_copy['edition_info']}
    Duration: {loan_time}
    Total Cost: €{total_cost:.2f}
    
    Confirm? (yes/no):       """)
            
            confirmation = user_input().strip().lower()
            chat_bubble(f"{confirmation}", "right")
            
            if confirmation != 'yes':
                chat_bubble("Loan cancelled.")
                loan_menu()
                return
            
            response = requests.post(
                f"{loan_service}/loans",
                json={
                    "copy_id": selected_copy['copy_id'],
                    "user_id": current_session.headers.get('User-ID') if not user_id else user_id,
                    "due_date": loan_time,
                    "status": ""
                }
            )
            
            chat_bubble(message_formatter(response))
            
        except ValueError:
            chat_bubble("Invalid input.")
        except Exception as e:
            chat_bubble(f"Error: {str(e)}")
    
    except Exception as e:
        chat_bubble(f"Error: {str(e)}")
    
    main_menu_user()
def check_loan_menu(status_filter):
    response = requests.get(f"{loan_service}/loans/{current_session.headers.get('User-ID')}", headers = current_session.get_session())
    loans = response.json()
    try:
        for loan in loans:
            if loan.get('status')==status_filter: 
                book_id = loan.get('copy_id').split('.')[0]
                chat_bubble(
        f"""    Loan {loan.get('loan_id')} 
            Due date: {loan.get('due_date')}
            Book: {requests.get(f"{catalog_service}/books/{book_id}").json().get('title')}
            Copy: {loan.get('copy_id').split('.')[1]}
            Status: {loan.get('status')}""")
        if status_filter !='returned':
            loan_menu2()    
        main_menu_user()
    except Exception as e:
        chat_bubble(f"""Error:\n {str(e)}""")
        main_menu_user()
def loan_menu2(user_id=None):
    chat_bubble("""Select a Loan ID to edit or press 0 to go back""")   
    user_id = int(current_session.get_session().get('User-ID') if not user_id==0 else user_id)
    loan_id = int(input())
    if loan_id == 0:
        loan_menu()
    response = requests.get(f"{loan_service}/loans/loan/{loan_id}")
    loan = response.json()
    print(loan.get('user_id'))
    print(user_id)

    if loan.get('user_id')==user_id or user_id == 0:

        chat_bubble("""Select an action
        1) Return book
        2) Change due date
        3) Return to menu""")    
        option = int(input())
        match option:
            case 1:
                requests.put(f"{loan_service}/loans/loan/{loan_id}",json= {"return_date": "today"})
                chat_bubble("""Success:
        Book has been returned.""")
                chat_bubble("""Proceed to Payments?
        1) Proceed
        2) Pay later""")
                option2 = int(input())
                match option2:
                    case 1:
                        complete_user_payment(loan_id)
                    case 2:
                        pass
            case 2:
                chat_bubble(
    """Change due date
        (+/-, #, days,week,months)                                            
        Changes:     """)
                sys.stdout.write("\033[2F\033[14C")
                change_str = input()
                try:
                    requests.put(f"{loan_service}/loans/loan/{loan_id}", json = {"due_date": change_str,"return_date": "","status":""})
                    chat_bubble("""Loan Updated!""")
                except Exception as e:
                    chat_bubble(f"""Error:\n {str(e)}""")
            case 3:
                main_menu_user()

def catalog_menu():
    chat_bubble("""Catalog Menu
            
    Choose an option:
        1) Search Books
        2) View Book Details
        3) View All books
        4) Back""")
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
            view_all_books(admin=False)
        case 4:
            main_menu_user()

def add_book():
    chat_bubble("""Add New Book
    
    Title:                                                            
    Author:                                                            
    Genre:                                                           
    Publication Year:                                                """)
    sys.stdout.write("\033[5F\033[13C") 
    sys.stdout.flush()
    title = input()
    while not re.match(r'^[a-zA-Z0-9.\-\s]{3,}$',title):
        sys.stdout.write("\033[2F\033[2C")
        sys.stdout.flush()
        print("Invalid Title. (min. 3 characters)")
        sys.stdout.write(f"\033[13C" + (" " * len(title)) + f"\033[{len(title)}D")
        sys.stdout.flush()
        title = input()

    sys.stdout.write("\033[14C") 
    sys.stdout.flush()
    author = input()
    while not re.match(r'^[a-zA-Z0-9.\-\s]{3,}$',author):
        sys.stdout.write("\033[2F\033[2C")
        sys.stdout.flush()
        print("Invalid Author. (min. 3 characters)")
        sys.stdout.write(f"\033[14C" + (" " * len(author)) + f"\033[{len(author)}D")
        sys.stdout.flush()
        author = input()
    
    sys.stdout.write("\033[12C")
    sys.stdout.flush()  
    genre = input()
    while not re.match(r'^[a-zA-Z0-9.\-\s]{3,}$',genre):
        sys.stdout.write("\033[2F\033[2C")
        sys.stdout.flush()
        print("Invalid Genre. (min. 3 characters)")
        sys.stdout.write(f"\033[12C" + (" " * len(genre)) + f"\033[{len(genre)}D")
        sys.stdout.flush()
        genre = input()  
  
    sys.stdout.write("\033[24C")
    sys.stdout.flush()
    pub_year=input()
    while not re.match(r'^[a-zA-Z0-9.\-\s]{3,}$',pub_year):
        sys.stdout.write("\033[2F\033[2C")
        sys.stdout.flush()
        print("Invalid Publication Year. (min. 3 characters)")
        sys.stdout.write(f"\033[13C" + (" " * len(pub_year)) + f"\033[{len(pub_year)}D")
        sys.stdout.flush()
        pub_year = input()
    print("\n\n")

    add_book_data = {
        "title": title, 
        "author": author, 

        "genre": genre if genre else None,
        "publication_year": int(pub_year) if pub_year else None
    }
    response = requests.post(f"{catalog_service}/books/", json=add_book_data, headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    manage_catalog_menu()
    
def search_books():
    chat_bubble(
"""Search Books

    Search by:
        1) Title
        2) Author
        3) Genre
        4) Back""")
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
            chat_bubble(
"""Search by Title                    
                                        
    Enter title:                                                                                           """, )
            sys.stdout.write("\033[2F\033[19C")
            sys.stdout.flush()
            search_term = input()
            search_type = "title"
            
        case 2:
            chat_bubble("""Search by Author
    
    Enter author name:                                                                                      """)
            sys.stdout.write("\033[2F\033[25C")
            sys.stdout.flush()
            search_term = input()
            search_type = "author"
            
        case 3:
            try:
                genres_response = requests.get(f"{catalog_service}/books/genres")
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
        response = requests.get(f"{catalog_service}/books/search", params={search_type: search_term})
        
        if response.status_code == 200:
            books = response.json()
            if books:
                for book in books:
                    chat_bubble(
f"""    Book ID: {book.get('id')}
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
                chat_bubble(f"Error:\n {error_data.get('error', 'Unknown error')}")
            except:
                chat_bubble(f"Error:\n Request failed with status {response.status_code}")
    except Exception as e:
        chat_bubble(f"Error: {str(e)}")
    
    catalog_menu()

def view_book_details():
    chat_bubble("""View Book Details
    
    Enter Book ID:             """)
    sys.stdout.write("\033[2F\033[20C")
    sys.stdout.flush()
    book_id = input()
    print("\n\n")
    
    response = requests.get(f"{catalog_service}/books/{book_id}")

    if response.status_code == 200:

        book = response.json()
        
        copies_response = requests.get(f"{catalog_service}/books/{book_id}/copies")
        copies_info = ""
        
        if copies_response.status_code == 200:
            copies = copies_response.json()
            copies_info = f"\n    Total Copies: {len(copies)}"
            available = sum(1 for copy in copies if copy.get('status') == 'available')
            copies_info += f"\n    Available: {available}"
        
        chat_bubble(f"""Book Details
    
    ID: {book.get('book_id')}
    Title: {book.get('title')}
    Author: {book.get('author')}
    Genre: {book.get('genre', 'N/A')}
    Publication Year: {book.get('publication_year', 'N/A')}""")
    else:
        chat_bubble(message_formatter(response))
    
    catalog_menu()

def account_settings():
    chat_bubble("""Account Settings
            
    Choose an option:
        1) View My Profile
        2) Change Username
        3) Change Email
        4) Change Password
        5) Back""")
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
    response = requests.get(f"{user_service}/users/{user_id}", headers=current_session.get_session())
    if response.status_code == 200:
        user = response.json()
        chat_bubble(f"""Your Profile

    User ID: {user.get('id')}
    Username: {user.get('name')}
    Email: {user.get('email')}
    Role: {user.get('role')}
    Member Since: {user.get('creation')}""")
    else:
        chat_bubble(message_formatter(response))
    account_settings()

def change_username():
    user_id = current_session.get_session().get('User-ID')
    response = requests.get(f"{user_service}/users/{user_id}", headers=current_session.get_session())

    if response.status_code != 200:
        chat_bubble("Error fetching user data.")
        account_settings()
        return

    current_user = response.json()
    current_username = current_user.get('name')

    chat_bubble(
f"""Change Username
    Current Username: {current_username}
    New Username:                                           """)
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
    response = requests.put(f"{user_service}/users/", json=data, headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    account_settings()

def change_email():
    user_id = current_session.get_session().get('User-ID')
    response = requests.get(f"{user_service}/users/{user_id}", headers=current_session.get_session())

    if response.status_code != 200:
        chat_bubble("Error fetching user data.")
        account_settings()
        return

    current_user = response.json()
    current_email = current_user.get('email')

    chat_bubble(f"""Change Email

    Current Email: {current_email}
    New Email:                                           """)
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

    while not re.match(r'^[a-zA-Z0-9.]+@[a-zA-Z]+.[a-zA-Z]{2,}$', new_email):
        sys.stdout.write("\033[4F\033[2C")
        sys.stdout.flush()
        print("Invalid Email.")
        sys.stdout.write(f"\033[2E\033[13C" + (" " * len(new_email)) + f"\033[{len(new_email)}D")
        sys.stdout.flush()
        new_email = input()
    print("\n\n")

    data = {"user_id": user_id, "new_email": new_email}
    response = requests.put(f"{user_service}/users/", json=data, headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    account_settings()

def change_password():
    chat_bubble("""Change Password

    New Password:                                           """)
    sys.stdout.write("\033[2F\033[19C")
    sys.stdout.flush()
    new_password = password_asterisco()

    if not new_password:
        chat_bubble("Password cannot be empty.")
        account_settings()
        return

    while not re.match(r'^[a-zA-Z0-9.%+!_?"#$%&/()]{8,}$', new_password):
        sys.stdout.write("\033[4F\033[2C")
        sys.stdout.flush()
        print("Invalid Password. (min. 8 characters)")
        sys.stdout.write(f"\033[2E\033[16C" + (" " * len(new_password)) + f"\033[{len(new_password)}D")
        sys.stdout.flush()
        new_password = password_asterisco()
    print("\n\n")

    user_id = current_session.get_session().get('User-ID')
    data = {"user_id": user_id, "new_password": new_password}
    response = requests.put(f"{user_service}/users/", json=data, headers=current_session.get_session())

    if response.status_code == 200:
        chat_bubble(message_formatter(response))
    else:
        try:
            error_data = response.json()
            chat_bubble(f"Error:\n {error_data.get('error', 'Unknown error')}")
        except:
            chat_bubble(f"Error:\n Request failed")

    account_settings()

def main_menu_admin():
    chat_bubble("""Admin Menu
            
    Choose an option:
        1) Manage Users
        2) Manage Catalog
        3) Manage Loans
        4) Manage Payments
        5) Back to Main Menu""")
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
            title("Library System - Manage Loans")
            manage_loans_menu()
        case 4:
            title("Library System - Manage Payments")
            payments_menu_admin()
        case 5:
            main_menu_user()
def manage_users_menu():
    chat_bubble("""Manage Users
            
    Choose an option:
        1) View All Users
        2) Delete User
        3) Modify User
        4) Back""")
    try:
        option = int(user_input())
        chat_bubble(f"{option}", "right")
    except:
        manage_users_menu()
    match option:
        case 1:
            title("Library System - View All Users")
            view_all_users()
        case 2:
            title("Library System - Delete User")
            delete_user()
        case 3:
            title("Library System - Modify User")
            modify_user()
        case 4:
            main_menu_admin()

def view_all_users():
    response = requests.get(f"{user_service}/users/", headers=current_session.get_session())
    if response.status_code == 200:
        users = response.json()
        for user in users:
            chat_bubble(f"""    User ID: {user.get('id')}
    Name: {user.get('name')}
    Email: {user.get('email')}
    Role: {user.get('role')}
    Created: {user.get('creation')}""")
    else:
        chat_bubble(message_formatter(response))
    manage_users_menu()

def delete_user():
    while True:
        chat_bubble("""Delete User
        
    Enter User ID:                                           """)
        sys.stdout.write("\033[2F\033[20C")
        sys.stdout.flush()
        user_id = input()
        if user_id.isdigit():
            user_id = int(user_id)
            response = requests.get(f"{user_service}/users/")
            users = response.json() if response.status_code==200 else chat_bubble(message_formatter(response))
            user_list = [int(user.get('id')) for user in users]
            if user_id in user_list:
                break
            else: chat_bubble("No valid user with such ID.")
                
        else: chat_bubble("Enter a valid user ID.")
    print("\n\n\n\n")

    
    response = requests.delete(f"{user_service}/users/{user_id}", headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    manage_users_menu()

def modify_user():
    while True:
        chat_bubble("""Modify User
        
        Enter User ID:                                           """)
        sys.stdout.write("\033[2F\033[24C")
        sys.stdout.flush()

        user_id = input()
        if user_id.isdigit():
            user_id = int(user_id)
            response = requests.get(f"{user_service}/users/")
            users = response.json() if response.status_code==200 else chat_bubble(message_formatter(response))
            user_list = [int(user.get('id')) for user in users]
            if user_id in user_list:
                break
            else: chat_bubble("No valid user with such ID.")
                
        else: chat_bubble("Enter a valid user ID.")
    print("\n\n\n\n")

    

    chat_bubble("""What would you like to change?
(Leave blank to keep current value)
    
    New Username:                              
    New Email:                              
    New Password:                              
    New Role (admin/member):                                           """)
    sys.stdout.write("\033[5F\033[19C")
    sys.stdout.flush()
    new_username = input()
    sys.stdout.write("\033[16C")
    sys.stdout.flush()
    new_email = input()
    sys.stdout.write("\033[19C")
    sys.stdout.flush()
    new_password = password_asterisco()
    sys.stdout.write("\033[30C")
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
    
    response = requests.put(f"{user_service}/users/", json=data, headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    manage_users_menu()

def manage_catalog_menu():
    chat_bubble("""Manage Catalog
            
    Choose an option:
        1) Add Book Manually
        2) Import Book from Google Books       
        3) Add Book Copy
        4) Remove Book
        5) Remove Book Copy
        6) View All Books
        7) Back """)
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
            view_all_books(admin=True)
        case 7:
            main_menu_admin()

def add_book_copy():
    chat_bubble("""Add Book Copy
    
    Enter Book ID:                                           """)
    sys.stdout.write("\033[2F\033[20C")
    sys.stdout.flush()
    book_id = input()
    print("\n\n")
    
    chat_bubble("Searching for editions...")
    
    try:
        response = requests.get(
            f"{catalog_service}/books/{book_id}/search_editions",
            headers=current_session.get_session()
        )
        
        if response.status_code in [200,404]:
            data = response.json()
            editions = data.get('editions', [])
            
            if not editions:
                chat_bubble("No editions found. Creating copy without ISBN...")
                
                chat_bubble("""Enter Rent Price:      """)
                sys.stdout.write("\033[2F\033[19C")
                sys.stdout.flush()
                rent_price = input()
                print("\n\n")
                
                copy_data = {"rent_price": float(rent_price)}
                copy_response = requests.post(
                    f"{catalog_service}/books/{book_id}/copy/",
                    json=copy_data,
                    headers=current_session.get_session()
                )
                chat_bubble(message_formatter(copy_response))
                manage_catalog_menu()
                return
            
            for edition in editions:
                chat_bubble(f"""{edition['index']}) ISBN: {edition['isbn']} ({edition['isbn_type']})
    Edition: {edition['edition_info']}
    Full Title: {edition['full_title']}""")
            
            chat_bubble(f"""Select an edition (1-{len(editions)}) or 0 to cancel:""")
            
            try:
                choice = int(user_input())
                chat_bubble(f"{choice}", "right")
                
                if choice == 0:
                    manage_catalog_menu()
                    return
                
                if 1 <= choice <= len(editions):
                    selected_edition = editions[choice - 1]
                    
                    chat_bubble("""Enter Rent Price (€/day):                 """)
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
                        f"{catalog_service}/books/{book_id}/copy/",
                        json=copy_data,
                        headers=current_session.get_session()
                    )
                    
                    if copy_response.status_code == 201:
                        copy_result = copy_response.json()
                        chat_bubble(f"""Copy Created Successfully!
    
    Copy ID: {copy_result.get('copy_id')}
    ISBN: {selected_edition['isbn']}
    Edition: {selected_edition['edition_info']}
    Rent Price: €{rent_price}/day """)
                    else:
                        chat_bubble(message_formatter(copy_response))
                else:
                    chat_bubble("Invalid selection.")
            except:
                chat_bubble("Invalid input.")
                
        else:
            try:
                error_data = response.json()
                chat_bubble(f"Error:\n {error_data.get('error', 'Unknown error')}")
            except:
                chat_bubble(f"Error:\n Request failed")
    except Exception as e:
        chat_bubble(f"Error:\n {str(e)}")
    
    manage_catalog_menu()
def remove_book():
    chat_bubble("""Remove Book
    
    Enter Book ID:             """)
    sys.stdout.write("\033[2F\033[20C")
    sys.stdout.flush()
    book_id = input()
    print("\n\n")
    
    chat_bubble(f"""Are you sure you want to delete Book ID {book_id}?
This will also delete ALL copies of this book!
    
    Type 'yes' to confirm:      """)
    sys.stdout.write("\033[2F\033[28C")
    sys.stdout.flush()
    confirmation = input()
    print("\n\n")
    
    if confirmation.lower() == 'yes':
        response = requests.delete(f"{catalog_service}/books/{book_id}", headers=current_session.get_session())
        chat_bubble(message_formatter(response))
    else:
        chat_bubble("Operation cancelled.")
    
    manage_catalog_menu()

def remove_book_copy():
    chat_bubble("""Remove Book Copy
    
    Enter Copy ID (book_id.copy_num):                      """)
    sys.stdout.write("\033[2F\033[40C")
    sys.stdout.flush()
    copy_id = input()
    print("\n\n")
    
    response = requests.delete(f"{catalog_service}/books/copy/{copy_id}", headers=current_session.get_session())
    chat_bubble(message_formatter(response))
    manage_catalog_menu()

def view_all_books(admin):
    response = requests.get(f"{catalog_service}/books/")
    if response.status_code == 200:
        books = response.json()
        for book in books:
            chat_bubble(f"""    Book ID: {book.get('id')}
    Title: {book.get('title')}
    Author: {book.get('author')}
    ISBN: {book.get('isbn', 'N/A')}
    Genre: {book.get('genre', 'N/A')}
    Publication Year: {book.get('publication_year', 'N/A')}
    Total Copies: {book.get('total_copies')}
    Available: {book.get('available_copies')}""")
    else:
        chat_bubble(message_formatter(response))
    if admin==True:
        manage_catalog_menu()
    else:
        catalog_menu()

def manage_loans_menu():
    chat_bubble("""Manage Loans
    
    Choose an option:
        1) View Loans
        2) New Loan
        3) Modify Loan
        4) Delete Loan
        5) Back""")

    try:
        option = int(user_input())
        chat_bubble(f"{option}",'right')
    except:
        manage_loans_menu()
    match option:
        case 1:
            title("Library System - View Loans")
            view_all_loans()
        case 2:
            title("Library System - New Loan")
            while True:
                chat_bubble("""Insert User ID
                            
    User ID:       """)
                sys.stdout.write('\033[2F\033[15C')
                sys.stdout.flush()
                try:
                    user_id = int(input())
                    break
                except:
                    sys.stdout.write('\033[3F\033[C')
                    sys.stdout.flush()
                    print("Error: Insert a valid id")
            if user_id:
                print('\n\n')
                loan_book_menu(user_id)
                    
        case 3:
            title("Library System - Modify Loan")
            loan_menu2(user_id=0)
        case 4:
            title("Library System - Delete Loan")
            while True:
                chat_bubble("""Insert Loan ID
                            
    Loan ID:       """)
                sys.stdout.write('\033[F\033[9C')
                sys.stdout.flush()
                try:
                    loan_id = int(input())
                except:
                    sys.stdout.write('\033[2F\033[C')
                    sys.stdout.flush()
                    print("Error: Insert a valid id")
                if loan_id:
                    delete_loan(loan_id)
                    break
            
        case 5:
            main_menu_admin()
    
def view_all_loans():
    chat_bubble("""View All Loans

    Enter User ID (or leave blank for all):                """)
    sys.stdout.write("\033[2F\033[45C")
    sys.stdout.flush()
    user_id = input().strip()
    print("\n\n")
    chat_bubble("""Filter by status

    1) Active
    2) Returned
    3) Overdue
    4) No filter
    5) Back               """)
    try:
        option = int(user_input())
        chat_bubble(f"{option}", "right")
    except:
        view_all_loans()
    match option:
        case 1:
            status_filter = 'active'
        case 2:
            status_filter = 'returned'
        case 3:
            status_filter = 'overdue'
        case 4:
            status_filter = 'pass'
        case 5:
            manage_loans_menu()
    

    if user_id:
        response = requests.get(f"{loan_service}/loans/{user_id}", headers=current_session.get_session())
        
        if response.status_code == 200:
            loans = response.json()
            if status_filter != 'pass':
                try:
                    for loan in loans:
                        if loan.get('status')==status_filter: 
                            book_id = loan.get('copy_id').split('.')[0]
                            chat_bubble(
            f"""Loan {loan.get('loan_id')} 
Due date: {loan.get('due_date')}
Book: {requests.get(f"{catalog_service}/books/{book_id}").json().get('title')}
Copy: {loan.get('copy_id').split('.')[1]}
Status: {loan.get('status')}""")
                except Exception as e:
                    chat_bubble(f"Error:\n {str(e)}")
            else:
                response = requests.get(f"{loan_service}/loans/{user_id}", headers=current_session.get_session())
                if response.status_code == 200:
                    loans = response.json()
                    try:
                        for loan in loans:
                            book_id = loan.get('copy_id').split('.')[0]
                            chat_bubble(
            f"""Loan {loan.get('loan_id')} 
Due date: {loan.get('due_date')}
Book: {requests.get(f"{catalog_service}/books/{book_id}").json().get('title')}
Copy: {loan.get('copy_id').split('.')[1]}
Status: {loan.get('status')}""")
                    except Exception as e:
                        chat_bubble(f"Error:\n {str(e)}")
                        

        elif response.status_code == 404:
            chat_bubble("No loans found for this user.")
            main_menu_admin()
            return
        else:
            try:
                error_data = response.json()
                chat_bubble(f"Error:\n {error_data.get('error', 'Unknown error')}")
            except:
                chat_bubble(f"Error:\n Request failed with status {response.status_code}")
            main_menu_admin()
            return
    else:
        response = requests.get(f"{loan_service}/loans/getall", headers=current_session.get_session())

        if response.status_code == 200:
            loans = response.json()

            if isinstance(loans, dict) and 'message' in loans:
                chat_bubble(loans['message'])
                main_menu_admin()
                return
        else:
            try:
                error_data = response.json()
                chat_bubble(f"Error:\n {error_data.get('error', 'Unknown error')}")
            except:
                chat_bubble(f"Error:\n Request failed with status {response.status_code}")
            main_menu_admin()
            return

    if loans and isinstance(loans, list):
        if not user_id:
            if status_filter != 'pass':
                    try:
                        for loan in loans:
                            book_id = loan.get('copy_id').split('.')[0]
                            if loan.get('status')==status_filter: 
                                book_id = loan.get('copy_id').split('.')[0]
                                chat_bubble(
                f"""Loan {loan.get('loan_id')} 
    Due date: {loan.get('due_date')}
    Book: {requests.get(f"{catalog_service}/books/{book_id}").json().get('title')}
    Copy: {loan.get('copy_id').split('.')[1]}
    Status: {loan.get('status')}""")
                    except Exception as e:
                        chat_bubble(f"Error:\n {str(e)}")
            else:
                for loan in loans:
                    book_id = loan.get('copy_id').split('.')[0]
                    book_response = requests.get(f"{catalog_service}/books/{book_id}")
                    book_title = book_response.json().get('title') if book_response.status_code == 200 else "Unknown"

                    user_id_loan = loan.get('user_id')
                    user_response = requests.get(f"{user_service}/users/{user_id_loan}", headers=current_session.get_session())
                    username = user_response.json().get('name') if user_response.status_code == 200 else "Unknown"

                    chat_bubble(f"""Loan ID: {loan.get('loan_id')}
        User ID: {user_id_loan}
        Username: {username}
        Copy ID: {loan.get('copy_id')}
        Book: {book_title}
        Loan Date: {loan.get('loan_date')}
        Due Date: {loan.get('due_date')}
        Return Date: {loan.get('return_date') if loan.get('return_date') else 'Not returned yet'}
        Status: {loan.get('status')}""")
    else:
        chat_bubble("No loans found.")
    main_menu_admin()
def delete_loan(loan_id):
    try:
        requests.delete(f'{loan_service}/loans/{loan_id}')
    except Exception as e:
        chat_bubble(f"Error:\n {str(e)}")



def payments_menu():
    chat_bubble("""Payments Menu
            
    Choose an option:
        1) View Pending Payments
        2) Complete Payment
        3) Back""")
    try:
        option = int(user_input())
        chat_bubble(F"{option}","right")
    except:
        payments_menu()
    
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
        f"{loan_service}/loans/{user_id}", 
        headers=current_session.get_session()
    )
    
    if response.status_code != 200:
        chat_bubble(message_formatter(response))
        payments_menu()
        return
    
    loans = response.json()
    pending_payments = []
    
    for loan in loans:
        payment_response = requests.get(
            f"{payment_service}/payments/loan_lookup",
            json={"loan_id": loan.get('loan_id')},
            headers=current_session.get_session()
        )
        
        if payment_response.status_code == 200:
            payment = payment_response.json()
            if payment.get('status') == 'pending':
                
                pending_payments.append({
                    'payment': payment,
                    'loan': loan
                })
    
    if not pending_payments:
        chat_bubble("""No pending payments found!""")
    else:
        for item in pending_payments:
            payment = item['payment']
            loan = item['loan']
            
            
            chat_bubble(f"""    Payment ID: {payment.get('payment_id')}
  
    Loan ID: {loan.get('loan_id')}
    Copy ID: {loan.get('copy_id')}
    Due Date: {loan.get('due_date')}
    
    Amount to Pay: €{payment.get('amount'):.2f}
    Status: {payment.get('status').upper()}""")
    
    chat_bubble("""Press Enter to continue...""")
    input()
    payments_menu()

def complete_user_payment(payment_id=None):
    while not payment_id:
        chat_bubble("""Complete Payment
                
    Enter Payment ID:          """)
        sys.stdout.write("\033[2F\033[23C")
        sys.stdout.flush()

        try:
            payment_id = int(input())
        except ValueError:
            chat_bubble("Error:\n   Insert a valid ID")
            payments_menu()
        

    check_payment = requests.get(
        f"{payment_service}/payments/{payment_id}",
        headers=current_session.get_session()
    )
    
    if check_payment.status_code != 200:
        chat_bubble(message_formatter(check_payment))
        payments_menu()
        return
    
    payment_data = check_payment.json()
    
    chat_bubble(f"""Confirm Payment
    
    Payment ID: {payment_data.get('payment_id')}
    Amount: £{payment_data.get('amount'):.2f}
    
    Do you want to complete this payment?
        1) Yes
        2) No    """)
    
    try:
        confirm = int(user_input())
        chat_bubble(F"{confirm}","right")
    except:
        complete_user_payment()
        return
    
    if confirm == 1:
        response = requests.put(
            f"{payment_service}/payments/{payment_id}/complete",
            json={"transaction_id": "today"},
            headers=current_session.get_session()
        )
        
        if response.status_code == 200:
            chat_bubble("""Payment Completed Successfully!""")
        else:
            chat_bubble(message_formatter(response))
    payments_menu()


def payments_menu_admin():
    chat_bubble("""Payments Menu (Admin)
            
    Choose an option:
        1) View All Pending Payments
        2) View All Payments History
        3) Complete Payment
        4) Modify Payment
        5) Delete Payment
        6) Request Payment for Overdue Loan
        7) Back""")
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
            main_menu_user()

def view_all_pending_payments():
    chat_bubble("""All Pending Payments
    ═══════════════════════════════════════════""")
    
    chat_bubble("""Enter range of Payment IDs to check:
    (Press Enter for defaults: 1 to 100)""")
    
    print("From: ", end="")
    from_raw = input().strip()
    from_id = int(from_raw) if from_raw else 1
    
    print("To: ", end="")
    to_raw = input().strip()
    to_id = int(to_raw) if to_raw else 100

    found_pending = False
    
    for payment_id in range(from_id, to_id + 1):
        try:
            response = requests.get(
                f"{payment_service}/payments/{payment_id}",
                headers=current_session.get_session()
            )
            
            if response.status_code == 200:
                payment = response.json()
                if payment.get('status') == 'pending':
                    found_pending = True
                    chat_bubble(f"""    Payment ID: {payment.get('payment_id')}
    User ID: {payment.get('user_id')}
    Loan ID: {payment.get('loan_id')}
    Amount: €{payment.get('amount'):.2f}
    Status: {payment.get('status').upper()}""")
        except Exception as e:
            continue 
    
    if not found_pending:
        chat_bubble(f"No pending payments found between {from_id} and {to_id}.")
    
    chat_bubble("Press Enter to return to menu...")
    input()
    payments_menu_admin()

def view_all_payments_history():
    chat_bubble("""Payment History
    ------------------------
    
Enter range of Payment IDs to check:
    (Press Enter for defaults: 1 to 100)""")
    
    print("From: ", end="")
    from_raw = input().strip()
    from_id = int(from_raw) if from_raw else 1
    
    print("To: ", end="")
    to_raw = input().strip()
    to_id = int(to_raw) if to_raw else 100

    found_any = False
    for payment_id in range(from_id, to_id + 1):
        response = requests.get(
            f"{payment_service}/payments/{payment_id}",
            headers=current_session.get_session()
        )
        
        if response.status_code == 200:
            found_any = True
            payment = response.json()
            status_symbol = "✓" if payment.get('status') == 'completed' else "○"
            chat_bubble(f"""    {status_symbol} Payment ID: {payment.get('payment_id')}
    User ID: {payment.get('user_id')}
    Loan ID: {payment.get('loan_id')}
    Amount: €{payment.get('amount'):.2f}
    Status: {payment.get('status').upper()}
    Transaction ID: {payment.get('transaction_id') or 'N/A'}""")
    
    if not found_any:
        chat_bubble("""No payments found in this range.""")
    
    chat_bubble("""Press Enter to continue...""")
    input()
    payments_menu_admin()

def create_payment_admin():
    chat_bubble("""Create New Payment
            
    Fill the information below:""")
    
    print("User ID: ", end="")
    user_id = input()
    
    print("Loan ID: ", end="")
    loan_id = input()
    
    print("Amount (€): ", end="")
    amount = input()
    
    response = requests.post(
        f"{payment_service}/payments/",
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
    chat_bubble("""Complete Payment""")
    
    print("Enter Payment ID: ", end="")
    payment_id = input()
    
    response = requests.put(
        f"{payment_service}/payments/{payment_id}/complete",
        json={"transaction_id": "today"},
        headers=current_session.get_session()
    )
    
    chat_bubble(message_formatter(response))
    payments_menu_admin()

def modify_payment_admin():
    chat_bubble("""Modify Payment""")
    
    print("Payment ID: ", end="")
    payment_id = input()
    
    print("New Status (pending/completed/cancelled/failed): ", end="")
    status = input()
    
    print("New Amount (€): ", end="")
    amount = input()
    
    print("Transaction ID: ", end="")
    tx_id = input()
    
    response = requests.put(
        f"{payment_service}/payments/{payment_id}",
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
    chat_bubble("""Delete Payment""")
    
    print("Enter Payment ID: ", end="")
    payment_id = input()
    
    chat_bubble("""Are you sure you want to delete this payment?
        1) Yes
        2) No""")
    
    try:
        confirm = int(user_input())
        chat_bubble(F"{confirm}","right")
    except:
        delete_payment_admin()
        return
    
    if confirm == 1:
        response = requests.delete(
            f"{payment_service}/payments/{payment_id}",
            headers=current_session.get_session()
        )
        chat_bubble(message_formatter(response))
    
    payments_menu_admin()

def request_payment_admin():
    chat_bubble("""Request Payment for Overdue Loan""")
    
    print("Enter Payment ID: ", end="")
    payment_id = input()
    
    response = requests.post(
        f"{payment_service}/payments/request/{payment_id}",
        headers=current_session.get_session()
    )
    
    chat_bubble(message_formatter(response))
    payments_menu_admin()
def import_book_from_google():
    chat_bubble("""Import Book from Google Books
    
    Select Language:
        1) English
        2) Portuguese
        3) Back""")
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
    
    chat_bubble("""Search by:
        1) Title
        2) Author
        3) Back""")
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
            chat_bubble(""" Search by Title
    
    Enter title:                                           """)
            sys.stdout.write("\033[2F\033[19C")
            sys.stdout.flush()
        case 2:
            search_type = "author"
            chat_bubble("""Search by Author
    
    Enter author:                                           """)
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
            f"{catalog_service}/books/search_google",
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
                chat_bubble(f"""    {book['index']}) {book['title']}
       Author: {book['author']}
       ISBN: {book.get('isbn', 'N/A')}
       Genre: {book.get('genre', 'N/A')}
       Year: {book.get('publication_year', 'N/A')}""")
            
            chat_bubble(f"""Select a book to import (1-{len(results)}) or 0 to cancel:""")
            
            try:
                choice = int(user_input())
                chat_bubble(f"{choice}", "right")
                
                if choice == 0:
                    import_book_from_google()
                    return
                
                if 1 <= choice <= len(results):
                    selected_book = results[choice - 1]
                    
                    import_response = requests.post(
                        f"{catalog_service}/books/import_selected",
                        json=selected_book,
                        headers=current_session.get_session()
                    )
                    
                    if import_response.status_code == 201:
                        import_data = import_response.json()
                        book = import_data.get('book', {})
                        chat_bubble(f"""Book Imported Successfully!
    
    ID: {import_data.get('id')}
    Title: {book.get('title')}
    Author: {book.get('author')}
    ISBN: {book.get('isbn', 'N/A')}
    Genre: {book.get('genre', 'N/A')}
    Year: {book.get('publication_year', 'N/A')}""")
                    else:
                        try:
                            error_data = import_response.json()
                            chat_bubble(f"Error:\n {error_data.get('error', 'Unknown error')}")
                        except:
                            chat_bubble(f"Error:\n Request failed")
                else:
                    chat_bubble("Invalid selection.")
            except:
                chat_bubble("Invalid input.")
                
        elif response.status_code == 404:
            chat_bubble("No books found matching your search.")
        else:
            try:
                error_data = response.json()
                chat_bubble(f"Error:\n {error_data.get('error', 'Unknown error')}")
            except:
                chat_bubble(f"Error:\n Request failed with status {response.status_code}")
    except Exception as e:
        chat_bubble(f"Error:\n {str(e)}")
    
    manage_catalog_menu()

if __name__ == "__main__": 
    log_menu()  




