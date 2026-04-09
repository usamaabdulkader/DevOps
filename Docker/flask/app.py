from flask import Flask
import MySQLdb
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
#Connect to the MySQL database
    db = MySQLdb.connect(
        host=os.environ.get("DB_HOST", "mydb"),
        user=os.environ.get("DB_USER", "root"),
        passwd=os.environ.get("DB_PASSWORD"),
        db=os.environ.get("DB_NAME", "mysql")
    )
    cur = db.cursor()
    cur.execute("SELECT VERSION()")
    version = cur.fetchone()
    return f'Hello, World! MySQL version: {version[0]}'

if  __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
