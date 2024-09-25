import sqlite3
from data_dict import random_users
from flask import Flask, jsonify, request

def createTable():
    with sqlite3.connect('members.db') as conn:
        cur = conn.cursor()
        cur.execute(""" CREATE TABLE IF NOT EXISTS members
            (id INTEGER PRIMARY KEY , 
            first_name TEXT, 
            last_name TEXT,
            birth_date TEXT,
            email TEXT,
            phonenumber TEXT,
            address TEXT,
            nationality TEXT,
            active BOOLEAN,
            github_username TEXT
            )""")
    conn.executemany('''INSERT INTO members (
             first_name,
             last_name,
             birth_date,
             email,
             phonenumber,
             address,
             nationality,
             active,
             github_username
             ) VALUES (:first_name, :last_name, :birth_date, :email, :phonenumber, :address, :nationality, :active, :github_username)''', random_users)
    
    conn.commit()

# GET 
# Read all from members table
def read():
    # Initialize an empty list
    members = []
    with sqlite3.connect('members.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM members')
        conn.commit()

        # Append each row as a dictionary to the list
        for i in cur.fetchall():
            members.append(i)

    return members

# GET
# Read one from members table
def get_member_by_id(id):
    member = None
    with sqlite3.connect('members.db') as conn:
        # Allows rows to be treated like dictionaries
        conn.row_factory = sqlite3.Row  
        cur = conn.cursor()
        cur.execute('SELECT * FROM members WHERE id = ?', (id,))
        
        row = cur.fetchone()
        # If a row is returned, convert it to a dictionary
        if row:
            member = dict(row)

    return member

# PUT
# Update github_username in members table
def update_member_github_username(id, new_github_username):
    with sqlite3.connect('members.db') as conn:
        cur = conn.cursor()
        
        # Update the github_username for the given member id
        cur.execute('UPDATE members SET github_username = ? WHERE id = ?', (new_github_username, id))
        
        # Error handling
        if cur.rowcount == 0:
            return False
        
        conn.commit()  
    return True

# DELETE
# Delete member from members table
def delete_member(id):
    with sqlite3.connect('members.db') as conn:
        cur = conn.cursor()
        
        # Delete the member with the given id
        cur.execute('DELETE FROM members WHERE id = ?', (id,))
        conn.commit()

        # Error handling
        if cur.rowcount == 0:
            return False
    return True
        






#createTable()
