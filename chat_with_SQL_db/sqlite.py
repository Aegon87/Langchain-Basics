import sqlite3

#connect to sqlite database
connection = sqlite3.connect("student.db")

#create a cursor object
cursor = connection.cursor()

#create a table
table_info = '''
CREATE TABLE STUDENT (NAME VARCHAR(25), CLASS VARCHAR(15), SECTION VARCHAR(15), MARKS INT)
'''
cursor.execute(table_info)

#insert some data into the table
data = [
    ('John Doe', '10th', 'A', 85),
    ('Jane Smith', '10th', 'B', 90),
    ('Alice Johnson', '9th', 'A', 78),
    ('Bob Brown', '9th', 'B', 88)
]
cursor.executemany('''INSERT INTO STUDENT (NAME, CLASS, SECTION, MARKS) VALUES (?, ?, ?, ?)''', data)

#display the data in the table
print("Data in the STUDENT table:")
data = cursor.execute('''SELECT * FROM STUDENT''')
for row in data:
    print(row)

#commit the changes and close the connection
connection.commit()
connection.close()