import sqlite3

connection = sqlite3.connect('harvard.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
            ('FirstUser', 'FirstPassword'))

connection.commit()
connection.close()