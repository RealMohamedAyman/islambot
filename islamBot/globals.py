import mysql.connector

PREFIX = '&'

# All you need here is replacing db_host,db_username, db_password, db_name with real right ones

def DBConnect():
    db = mysql.connector.connect(
        host='db_host',
        user='db_username',
        password='db_password',
        database='db_name',
        auth_plugin='mysql_native_password'
    )
    cursor = db.cursor()
    return db, cursor
