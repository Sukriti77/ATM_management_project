import sqlite3

# Connect to the database (this will create a new file if it doesn't exist)
conn = sqlite3.connect('atm_database.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table to store user data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        passkey TEXT,
        saving_balance INTEGER,
        current_balance INTEGER,
        unlock_id TEXT,
        card_number TEXT,
        saving_lock INTEGER,
        current_lock INTEGER
    )
''')

# Create a table to store admin data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY,
        name TEXT,
        passkey TEXT,
        card_number TEXT
    )
''')

# Create a table to store ATM amount
cursor.execute('''
    CREATE TABLE IF NOT EXISTS atm_amount (
        id INTEGER PRIMARY KEY,
        amount INTEGER
    )
''')

# Commit the changes
conn.commit()

# Insert initial user data
initial_users = [
    ('Swati Awasthy', 'User1', 20000, 2000000, 'Swati_01', 'ACC001', 0, 0),
    ('Anil Sharma', 'User2', 50000, 1000000, 'Anil_02', 'ACC002', 0, 0),
    ('Komal Chauhan', 'User3', 100000, 1000000, 'Komal_03', 'ACC003', 0, 0),
    ('Rishi Solanki', 'User4', 70000, 1000000, 'Rishi_04', 'ACC004', 0, 0),
    ('Eva Verma', 'User5', 80000, 1000000, 'Eva_05', 'ACC005', 0, 0),
]

cursor.executemany('''
    INSERT INTO users (name, passkey, saving_balance, current_balance, unlock_id, card_number, saving_lock, current_lock)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', initial_users)

# Insert initial admin data
initial_admin = ('Admin', 'admin_of_atm', 'ADMIN01')  # Change admin name to 'Admin'
cursor.execute('''
    INSERT INTO admin (name, passkey, card_number)
    VALUES (?, ?, ?)
''', initial_admin)

# Calculate initial ATM amount as the sum of all current and saving balances plus an additional 1000000
initial_atm_amount = sum(user[2] + user[3] for user in initial_users) + 1000000

# Insert initial ATM amount data
cursor.execute('''
    INSERT INTO atm_amount (amount)
    VALUES (?)
''', (initial_atm_amount,))

# Commit the changes and close the connection
conn.commit()
conn.close()
