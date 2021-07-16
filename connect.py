import psycopg2

# If admin, then connect like this
conn = psycopg2.connect(
    host="localhost", 
    port = 5432, 
    database="bookstore", 
    user="librarian", 
    password="finalproject"
)

# Default is
conn = psycopg2.connect(
    host="localhost", 
    port = 5432, 
    database="bookstore", 
    user="patron", 
    password="finalproject"
)

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

# cur = conn.cursor()
# cur.execute("SELECT * FROM books WHERE subject = %s ", [subject])

print(cur.fetchone()[0])