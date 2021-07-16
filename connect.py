import psycopg2

conn = psycopg2.connect(
    host="localhost", 
    port = 5432, 
    database="bookstore", 
    user="postgres", 
    password="finalproject"
)

# Regular User FUNCTIONALITY (Need to create a user in pgadmin4
# and grant them proper priviliges)
# signup view
# login view
# search view
    # Do you want to search by subject
    # Do you want to search by author
    # Do you want to be recommended a random book?
# book results view 



# Create a cursor object
cur = conn.cursor()
cur.execute("SELECT * FROM books WHERE subject = %s ", [subject])

print(cur.fetchone()[0])