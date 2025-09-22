import sqlite3
import random
from faker import Faker

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('bookstore.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.populate_books()
        
    def create_tables(self):
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE,
                            password TEXT,
                            fullname TEXT,
                            email TEXT)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT,
                            author TEXT,
                            publish_date TEXT,
                            price REAL,
                            rental_price REAL,
                            quantity INTEGER)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            operation_type TEXT,
                            book_id INTEGER,
                            customer_name TEXT,
                            phone TEXT,
                            email TEXT,
                            transaction_date TEXT,
                            price REAL,
                            FOREIGN KEY(book_id) REFERENCES books(id))''')
        
        self.conn.commit()
    
    def populate_books(self):
        fake = Faker()
        self.cursor.execute("SELECT COUNT(*) FROM books")
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            books_data = []
            for _ in range(100):
                title = fake.catch_phrase()
                author = fake.name()
                publish_date = fake.date_between(start_date='-30y', end_date='today').strftime('%Y-%m-%d')
                price = round(random.uniform(5, 100), 2)
                rental_price = round(price * 0.1, 2)
                quantity = random.randint(1, 50)
                books_data.append((title, author, publish_date, price, rental_price, quantity))
            
            self.cursor.executemany('''INSERT INTO books 
                                    (title, author, publish_date, price, rental_price, quantity) 
                                    VALUES (?, ?, ?, ?, ?, ?)''', books_data)
            self.conn.commit()

    def validate_user(self, username, password):
        if username == "admin" and password == "admin":
            return (1, "admin", "admin", "Administrator", "admin@bookstore.com")
            
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        return self.cursor.fetchone()
    
    def add_user(self, fullname, username, email, password):
        try:
            self.cursor.execute('''INSERT INTO users 
                                (username, password, fullname, email) 
                                VALUES (?, ?, ?, ?)''', 
                                (username, password, fullname, email))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_books(self, search_term=None):
        query = """SELECT id, title, author, publish_date, price, rental_price, quantity 
                   FROM books"""
        params = ()
        if search_term:
            query += " WHERE title LIKE ? OR author LIKE ?"
            params = (f"%{search_term}%", f"%{search_term}%")
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def add_transaction(self, operation_type, book_id, customer_name, phone, email, transaction_date, price):
        self.cursor.execute('''INSERT INTO transactions 
                            (operation_type, book_id, customer_name, phone, email, transaction_date, price) 
                            VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                            (operation_type, book_id, customer_name, phone, email, transaction_date, price))
        self.conn.commit()
        
    def get_transactions(self):
        self.cursor.execute("""SELECT t.operation_type, b.title, t.customer_name, 
                             t.phone, t.email, t.transaction_date, t.price 
                             FROM transactions t JOIN books b ON t.book_id = b.id 
                             ORDER BY t.transaction_date DESC""")
        return self.cursor.fetchall()
        
    def __del__(self):
        self.conn.close()
