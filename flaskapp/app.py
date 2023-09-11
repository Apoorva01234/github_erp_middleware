from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import yaml


db = yaml.load(open('db.yaml'), Loader=yaml.SafeLoader)

app = Flask(__name__)

app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)


def mysql_operation(func):
    def wrapper(*args, **kwargs):
        cur = mysql.connection.cursor()
        try:
            result = func(cur, *args, **kwargs)
            mysql.connection.commit()
            return result
        except Exception as e:
            mysql.connection.rollback()
            raise e
        finally:
            cur.close()
    return wrapper

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        userdetails = request.form
        name = userdetails['name']
        email = userdetails['email']

        @mysql_operation
        def insert_user(cur, name, email):
            cur.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))

        insert_user(name, email)
        return 'SUCCESS'
    return render_template('index.html')

@app.route('/users')
@mysql_operation
def users(cur):
    cur.execute("SELECT * FROM users")
    userdetails = cur.fetchall()
    return render_template('users.html', userdetails=userdetails)

if __name__ == '__main__':
    app.run(debug=True)
