import psycopg2
from enum import Enum
from datetime import datetime

# UseType enumeration
class UserType(Enum):
    LIBRARIAN = 1
    PATRON = 2
    ANONYMOUS = 3

# Database class
class DataBase():
    # Get the librarian connection
    def get_librarian_connection(self):
        # If librarian, then connect like this
        connection = psycopg2.connect(
            host="localhost", 
            port = 5432, 
            database="bookstore", 
            user="librarian", 
            password="finalproject"
        )
        return connection

    # Get the Patron (Default) connection
    def get_patron_connection(self):
        # Connect Patron (default)
        connection = psycopg2.connect(
            host="localhost", 
            port = 5432, 
            database="bookstore", 
            user="patron", 
            password="password"
        )
        return connection

# Form validation 
def validate_form(formdata, cursor):
    firstname = formdata['firstname']
    lastname  = formdata['lastname']
    email     = formdata['email']
    dob       = formdata['dob']
    password  = formdata['password']
    # If anything is empty
    if len(firstname) == 0 or len(lastname) == 0 or len(dob) == 0 or len(password) == 0:
        print('Sorry, all fields are required')
        return False
    
    # If the email already exists
    cursor.execute("SELECT * FROM LibraryUsers WHERE email = %s", [email])
    if cursor.fetchone() != None:
        print('Sorry, that email has already been used')
        return False

    # If email does not have @ or ends in com,org,edu
    if not email.endswith('com') and not email.endswith('org') and not email.endswith('edu'):
        print("Invalid email entered")
        return False
    if not '@' in email:
        print("Invalid email entered")
        return False

    # DOB format should be "MM/DD/YYYY"
    format = "%m/%d/%Y" 
    try:
        datetime.strptime(dob, format)
    except ValueError:
        print("This is the incorrect date format. It should be DD/MM/YYYY")
        return False
    return True

class Views():
    def sign_up_view(self):
        # Get DB connection class
        db = DataBase()

        # Get the DB cursor
        connection = db.get_patron_connection()
        cursor = connection.cursor()

        # Replace ' to prevent SQL injection
        firstname = input('Enter first name: ').replace('\'', '')
        lastname  = input('Enter last name: ').replace('\'', '')
        dob       = input('Enter date of birth: ').replace('\'', '')
        email     = input('Enter email: ').replace('\'', '')
        password  = input('Enter password: ').replace('\'', '')

        # Check if the form is valid
        valid = validate_form(
            {
                'firstname' : firstname,
                'lastname'  : lastname,
                'dob'       : dob,
                'email'     : email,
                'password'  : password
            },
            cursor
        )

        if valid:
            cursor.execute("INSERT INTO LibraryUsers(email,firstname,lastname,dob,isadmin,password) VALUES (%s, %s, %s, %s, %s, %s)", (email,firstname,lastname,dob,'N',password))
            connection.commit()
            print('Patron signup successful')
        cursor.close()
        connection.close()


def MainLoop():
    # db = DataBase()
    # cursor = db.get_patron_connection()
    # cursor.execute("SELECT * FROM Authors")
    # print(cursor.fetchone())
    user = UserType.ANONYMOUS
    run_loop = True
    while run_loop:
        if user == UserType.ANONYMOUS:
            print('---------------- Welcome ANON ----------------')
            print('Select Option: ')
            print('1: Sign up')
            print('q: quit')
            cmd = input('Selection: ')
            if cmd == '1':
                print('Send to sign up view')
                view = Views()
                view.sign_up_view()
            elif cmd == 'q':
                run_loop = False

MainLoop()

# Regular User FUNCTIONALITY
# signup view
# login view
# search view
    # Do you want to search by subject
        # book results view 
    # Do you want to search by author
        # book results view
    # Do you want to see your checked out books (include their due dates)

    # Extra Feature (choose subject): WHERE subject = '' ORDER BY RANDOM LIMIT 1
    # Do you want to be recommended a random book?

# Librarian 
    # Assign book to a user:
        # Input: Email
        # Input: ISBN
        # Create the borrow entry (INSERT)

    # Return book from user:
        # Input: Email
        # Input: ISBN
        # Delete the borrow entry (INSERT)

    # View all emails
    # View all books