import sqlite3

# Can also use this script to execute stuff on the harvard.db database
connection = sqlite3.connect('harvard.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
            ('FirstUser', 'FirstPassword'))

connection.commit()
connection.close()