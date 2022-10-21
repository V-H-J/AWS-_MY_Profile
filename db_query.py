
import pymysql


ENDPOINT = "database-1.cum7eogqifjn.us-east-2.rds.amazonaws.com"
PORT = "3306"
USR = "admin"
PASSWORD = "VHJmysql19"
DBNAME = "finalproject"
 
print("initialize") 
conn = pymysql.connect(
        host= ENDPOINT, 
        user = USR, 
        password = PASSWORD,
        database = DBNAME,
                )

cur =conn.cursor()
try:   
        cur.execute("DROP TABLE hari_userdetails;")
        cur.execute("DROP TABLE hari_filedetails;")
        print("table deleted")
except Exception as e:
        print("cannot delete table")
        cur.execute("CREATE TABLE hari_userdetails(firstname VARCHAR(100), lastname VARCHAR(100), email VARCHAR(100), password VARCHAR(100));")
        print("table created")
        cur.execute("CREATE TABLE hari_filedetails(filename VARCHAR(2000), fileurl VARCHAR(2000));")
        print("table created")
        cur.execute("INSERT INTO hari_userdetails(firstname,lastname,email,password) VALUES('test','1','test1@gmail.com','password');")
        print("Insert Success")
        cur.execute("INSERT INTO hari_userdetails(firstname,lastname,email,password) VALUES('test','2','test2@gmail.com','password');")
        print("Insert Success")
        cur.execute("INSERT INTO hari_userdetails(firstname,lastname,email,password) VALUES('test','3','test3@gmail.com','password');")
        print("Insert Success")
        cur.execute("INSERT INTO hari_userdetails(firstname,lastname,email,password) VALUES('test','4','test4@gmail.com','password');")
        print("Insert Success")
        conn.commit()

        cur.execute("SELECT * FROM hari_userdetails;")
        query_results = cur.fetchall()
        print(query_results)