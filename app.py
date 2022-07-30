from django.shortcuts import render
from flask import Flask, request, render_template, url_for, flash, redirect
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import datetime
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'limonchan'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

def get_db_connection():
    connect = psycopg2.connect("postgres://qubbkhqdeylkex:28b87a762a0fe1dd841f224df2caa5408c99ffe03fa9b47d60155379ad0e4101@ec2-52-204-157-26.compute-1.amazonaws.com:5432/dfn5omign98a33")
    conn = connect.cursor()
    return connect,conn

@app.route("/")
def index():
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    connect,conn = get_db_connection()
    conn.execute("SELECT * FROM BOARDS")
    boards = conn.fetchall()
    conn.close()
    return render_template("mainpage.html", boards=boards, date=date)

@app.route("/createboard", methods=("GET", "POST"))
def createboard():
    connect,conn = get_db_connection()
    if request.method == "POST":    
        contentb = request.form["contentb"]
        if len(contentb) > 20:
            flash("Write less")
        else:
            if not contentb:
                flash("Write something")
            else:
                connect,conn = get_db_connection()
                conn.execute(f"INSERT INTO BOARDS (BOARD) VALUES ('{contentb}')")
                conn.execute(f"""
                CREATE TABLE {contentb}(
        id SERIAL PRIMARY KEY NOT NULL,
        text TEXT NOT NULL,
        date TEXT NOT NULL,
        sender TEXT NOT NULL
    )
                """)
                connect.commit()
                conn.close()
                return redirect(url_for("board", boardname=contentb))

    return render_template("newboard.html")


@app.route("/board/<boardname>")
def board(boardname):
    connect,conn = get_db_connection()
    conn.execute(f'SELECT * FROM {boardname}')
    posts = conn.fetchall()
    posts = reversed(posts)
    conn.close()
    return render_template("board.html", name=boardname,posts=posts)


@app.route('/board/<boardname>/create', methods=('GET', 'POST'))
def create(boardname):
    if request.method == 'POST':
        if current_user.is_authenticated:
            content = request.form['content']
            if not content:
                flash('Content is required!')
            else:
                connect,conn = get_db_connection()
                date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.execute(f"""INSERT INTO {boardname} (text,date,sender) VALUES ($${content}$$, '{date}', '{current_user.username}')""")
                connect.commit()
                conn.close()
                return redirect(url_for("board", boardname=boardname ))
        else:
            content = request.form['content']
            if not content:
                flash('Content is required!')
            else:
                connect,conn = get_db_connection()
                date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.execute(f"INSERT INTO {boardname} (text,date,sender) VALUES ($${content}$$, '{date}', 'Anonymous')")
                connect.commit()
                conn.close()
                return redirect(url_for("board", boardname=boardname ))

    return render_template('newpost.html',name=boardname)

@app.route("/newuser", methods=('GET', 'POST'))
def newuser():
    if current_user.is_authenticated:
        return redirect(url_for("profile"))
    else:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            email = request.form["email"]
            if not username or not password:
                print("Wrong")
            else:
                connect,conn = get_db_connection()
                conn.execute(f"SELECT username FROM users WHERE EXISTS(SELECT * FROM users WHERE username='{username}')")
                rows= conn.fetchall()
                if len(rows) == 0:
                    print("username does not exist")
                    rowsmail = conn.execute(f"SELECT EXISTS (SELECT * FROM users WHERE email='{email}')")
                    if not rowsmail:
                        print("no email, creating user account")
                        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        newuser = f"""INSERT INTO users (username,password,email,date) VALUES ('{username}','{password}','{email}','{date}' )"""
                        conn.execute(newuser)
                        connect.commit()
                        conn.close()
                        return redirect(url_for("login"))
                    elif rowsmail:
                        conn.execute(f"SELECT email FROM users WHERE EXISTS(SELECT 1 FROM users WHERE email='{email}')")
                        rowsmail=conn.fetchone()
                        if len(rowsmail) == 0:
                            print("email not exists, creating user account")
                            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            newuser = f"""INSERT INTO users (username,password,email,date) VALUES ('{username}','{password}','{email}','{date}' )"""
                            conn.execute(newuser)
                            connect.commit()
                            conn.close()
                            return redirect(url_for("login"))
                else:
                    print("username exists")
                    

    return render_template("newuserpage.html")

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username
        self.authenticated = False
    def is_active(self):
         return self.is_active()
    def is_anonymous(self):
         return False
    def is_authenticated(self):
         return self.authenticated
    def is_active(self):
         return True
    def get_id(self):
         return self.id

@app.route("/profile")
@login_required
def profile():
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    connect, conn = get_db_connection()
    command = f"SELECT * FROM BOARDS"
    conn.execute(command)
    board = conn.fetchall()
    posts = []
    for i in board:
        command = f"SELECT * FROM {i[1]} WHERE sender = '{current_user.username}'"
        conn.execute(command)
        data = conn.fetchall()
        print(data)
        if data:
            for x in data:
                boardname = i
                posts.append((i,x))
        else:
            total = 0
            return render_template("profile.html",total=total)
    print(posts[1])
    total = len(posts)
    return render_template("profile.html",date=date,posts=posts,data=data,boardname=boardname,total=total)



@app.route("/admin")
@login_required
def admin():
    return render_template("adminpage.html")

@login_manager.user_loader
def load_user(user_id):
    connect,conn = get_db_connection()
    conn.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
    x = conn.fetchone()
    if x:
        conn.close()
        return User(x[0],x[1])
    else:
        pass

@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    else:
        if request.method == "POST":
            connect,conn = get_db_connection()
            username = request.form["username"]
            conn.execute(f"SELECT * FROM users WHERE username = '{username}'")
            user = conn.fetchone()
            if user:
                Us = load_user(user[0])
                password = request.form["password"]
                if username == user[1]:
                    if password == user[2]:
                        login_user(Us)
                        conn.close()
                        return redirect(url_for("profile"))
    return render_template("loginpage.html")

@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('index'))
    
if __name__ == "__main__":
    app.run(debug=True)