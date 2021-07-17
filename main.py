import psycopg2
from enum import Enum
import datetime

# UserType enumeration
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
            password="password"
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
    
    # Clean input function (remove ' from input ) for SQL injection defense
    def get_clean_input(self, message):
        return input(message).replace('\'', '')

    # Description: can return a query result (one query as a dictionary)
    # This is useful for returning the user information 
    # as a mapping of attribute to value
    # rather than indexing through it like an array
    # Function: Take database cursor and return fetchone() as a dict(attribute,value)
    def result_to_dict(self, cursor, result):
        keys   = cursor.description
        keys   = [col[0] for col in keys] # description returns Column('attributename','typecode')
        values = result
        data   = dict(zip(keys,values))
        return data

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
        datetime.datetime.strptime(dob, format)
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
        firstname = db.get_clean_input('Enter first name: ')
        lastname  = db.get_clean_input('Enter last name: ')
        dob       = db.get_clean_input('Enter date of birth: ')
        email     = db.get_clean_input('Enter email: ')
        password  = db.get_clean_input('Enter password: ')

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
            cursor.execute(
                """INSERT INTO LibraryUsers(email,firstname,lastname,dob,isadmin,password) 
                VALUES (%s, %s, %s, %s, %s, %s)""", 
                (email,firstname,lastname,dob,'N',password)
            )
            connection.commit()
            print('Patron signup successful\n')

        cursor.close()
        connection.close()

    def login_view(self):
        # Get DB connection class
        db = DataBase()

        # Get the DB cursor
        connection = db.get_patron_connection()
        cursor = connection.cursor()

        # Ask user for email and password
        email    = db.get_clean_input('Email: ')
        password = db.get_clean_input('Password: ')

        # Get user with that email and password
        cursor.execute("""SELECT email,isadmin FROM LibraryUsers WHERE email = %s AND password = %s""",(email,password))
        result = cursor.fetchone() # [email,isadmin]

        # Return the result of the query which is either:
        #   None         (unsuccessful login)
        #   query result (if successful login)
        if result == None:
            print('Sorry, we could not authenticate your credentials.')
            print('Returning to the main menu.\n')
            return None
        print('Login successful.\n')
        return db.result_to_dict(cursor,result)

    def assign_book_view(self):
        # Get DB connection class
        db = DataBase()

        # Get the DB cursor
        connection = db.get_librarian_connection()
        cursor = connection.cursor()

        # Ask user for email and isbn
        print('Assign book: [patron email][book isbn]')
        email    = db.get_clean_input('Patron email: ')
        isbn     = db.get_clean_input('ISBN: ')

        # Get book with that isbn
        #cursor.execute("""SELECT email,isadmin FROM LibraryUsers WHERE email = %s AND password = %s""",(email,password))
        cursor.execute("""SELECT * FROM Books WHERE isbn = %s""", (isbn,))
        book = cursor.fetchone() # result of query

        if book == None:
            print('Could not find the book.')
            return None
        book = db.result_to_dict(cursor,book)       # get attribute -> value


        # Get user with that email
        cursor.execute("""SELECT * FROM LibraryUsers WHERE email = %s""", (email,))
        patron = cursor.fetchone() # result of query

        if patron == None:
            print('Could not find the patron.')
            return None
        patron = db.result_to_dict(cursor,patron)   # get attribute -> value

        # Format for our dates
        format = "%m/%d/%Y" 
        today = datetime.datetime.today()                       # get today as datetime obj
        strToday = datetime.datetime.strftime(today, format)
        duedate = today + datetime.timedelta(days=14)
        strDuedate = datetime.datetime.strftime(duedate, format)

        cursor.execute(
                """INSERT INTO Borrow(isbn,email,borrowdate,duedate) 
                VALUES (%s, %s, %s, %s)""", 
                (book['isbn'],patron['email'],strToday,strDuedate)
        )
        connection.commit()
        print('Successfully checked book out. \'{}\' is due on {}.'.format(book['title'], strDuedate))

        cursor.close()
        connection.close()


def MainLoop():
    # Session to hold any session data for keeping track of system state
    session_data = {}
    session_data['user'] = UserType.ANONYMOUS

    # While user has not quit, run the main loop
    run_loop = True

    while run_loop:
        # Anonymous User menu
        if session_data['user'] == UserType.ANONYMOUS:
            print('---------------- Main Menu ----------------')
            print('Select Option: ')
            print('1: Sign up')
            print('2: Login')
            print('q: quit')
            cmd = input('Selection: ')
            
            if cmd == '1':
                print('Send to sign up view')
                view = Views()
                view.sign_up_view()
            if cmd == '2':
                print('Send to login view')
                view = Views()

                # Get result of logging in as a dictionary with email and isadmin
                result = view.login_view() # keys are 'email' and 'isadmin'
                if result == None:
                    # This means the user was not logged in successfully
                    continue

                # Set the session data for the logged in user
                # Save the appropriate user type in session_data
                if result['isadmin'] == 'Y':
                    # Set the user type to librarian
                    session_data['user']  = UserType.LIBRARIAN
                elif result['isadmin'] == 'N':
                    # Set the user type to patron
                    session_data['user'] = UserType.PATRON

                # Save the user email in session_data (email is pk in LibraryUsers table)
                session_data['email'] = result['email']
            elif cmd == 'q':
                run_loop = False
                print('Goodbye.')

        # Librarian User menu
        if session_data['user']== UserType.LIBRARIAN:
            print('---------------- Librarian Menu ({})----------------'.format(session_data['email']))
            print('Select Option: ')
            print('1: Assign book to patron')   # Main feature
            print('2: Process book return')     # Main feature
            print('3: View book catalog')       # Extra feature
            print('4: View registered patrons') # Extra feature
            print('5: View overdue books')      # Extra feature
            print('q: quit')
            cmd = input('Selection: ')

            if cmd   == '1':
                print('Assign book to patron')
                view = Views()
                view.assign_book_view()
            elif cmd == '2':
                print('Process book return')
            elif cmd == '3':
                print('View book catalog')
            elif cmd == '4':
                print('View registered patrons')
            elif cmd == '5':
                print('View overdue books')
            elif cmd == 'q':
                run_loop = False
                print('Goodbye.')
        
        # Patron User Menu
        if session_data['user'] == UserType.PATRON:
            print('---------------- Patron Menu ({}) ----------------'.format(session_data['email']))
            print('Select Option: ')
            print('1: Search by subject')           # Main feature
            print('2: Search by author')            # Main feature
            print('3: View my borrowed books')      # Extra feature
            print('4: Get a book recommendation')   # Extra feature
            print('q: quit')
            cmd = input('Selection: ')

            if cmd   == '1':
                print('Search by subject') 
            elif cmd == '2':
                print('Search by author')
            elif cmd == '3':
                print('View my borrowed books')
            elif cmd == '4':
                print('Get a book recommendation')
            elif cmd == 'q':
                run_loop = False
                print('Goodbye.')

            
# Run the Main event loop
MainLoop()

# Project Overview

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
    # View overdue books and who has them