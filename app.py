from django.shortcuts import render
from flask import Flask, request, render_template, url_for, flash, redirect
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import datetime
import sqlite3
import pandas as pd
import pandas.io.sql as psql
import pytz


"""
todo Post silme
todo youtube videosunu otomatik href yapma
todo board silerken onaylama 

"""
app = Flask(__name__)
app.config['SECRET_KEY'] = 'limonchan'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

def get_db_connection():
    connect = sqlite3.connect("limonchan.db")
    conn = connect.cursor()
    return connect,conn


@app.route("/")
def index():
    date = datetime.datetime.now(pytz.timezone("Europe/Istanbul")).strftime("%Y-%m-%d %H:%M:%S")
    connect,conn = get_db_connection()
    conn.execute("SELECT * FROM BOARDS")
    boards = conn.fetchall()
    conn.close()
    if current_user.is_authenticated:
        username = current_user.username
    else:
        username = "Anonymous user"
    isadmin=checkadmin()
    return render_template("mainpage.html", boards=boards, date=date,isadmin= isadmin,username=username)

@app.route("/createboard", methods=("GET", "POST"))
@login_required
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
                conn.execute(f"INSERT INTO BOARDS (BOARD,CREATOR) VALUES ('{contentb}','{current_user.username}')")
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

@app.route("/board/<boardname>/delete")
@login_required
def deleteboard(boardname):
    name, author = boardcreator(boardname)
    if current_user.username == author:
        connect, conn = get_db_connection()    
        command = f"DELETE FROM BOARDS WHERE board = '{boardname}'"
        conn.execute(command)
        command2 = f"DROP TABLE {boardname}"
        conn.execute(command2)
        connect.commit()
        connect.close()
        return redirect(url_for("index"))
    else:
        return redirect(url_for("board", boardname=name))

@app.route("/board/<boardname>")
def board(boardname):
    connect,conn = get_db_connection()
    conn.execute(f'SELECT * FROM {boardname}')
    posts = conn.fetchall()
    posts = reversed(posts)
    author = conn.execute(f"SELECT creator FROM boards WHERE (board = '{boardname}')")
    author = conn.fetchone()
    conn.close()
    return render_template("board.html", name=boardname,posts=posts,author=author[0])

@app.route("/board/<board>/deletepost/<postid>")
def deletepost(board,postid):
    connect, conn = get_db_connection()
    if postid:     
        print(board,postid)
        command = f"DELETE FROM {board} WHERE id = {postid}"
        conn.execute(command)
        connect.commit()
        connect.close()
        return(redirect(url_for("board",boardname=board)))

@app.route('/board/<boardname>/create', methods=('GET', 'POST'))
def create(boardname):
    if request.method == 'POST':
        if current_user.is_authenticated:
            content = request.form['content']
            if not content:
                flash('Content is required!')
            else:
                connect,conn = get_db_connection()
                date = datetime.datetime.now(pytz.timezone("Europe/Istanbul")).strftime("%Y-%m-%d %H:%M:%S")
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
                date = datetime.datetime.now(pytz.timezone("Europe/Istanbul")).strftime("%Y-%m-%d %H:%M:%S")
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
                flash("Username or password cannot be empty")
            else:
                connect,conn = get_db_connection()
                conn.execute(f"SELECT username FROM users WHERE EXISTS(SELECT * FROM users WHERE username='{username}')")
                rows= conn.fetchall()
                if len(rows) == 0:
                    rowsmail = conn.execute(f"SELECT EXISTS (SELECT * FROM users WHERE email='{email}')")
                    if not rowsmail:
                        date = datetime.datetime.now(pytz.timezone("Europe/Istanbul")).strftime("%Y-%m-%d %H:%M:%S")
                        newuser = f"""INSERT INTO users (username,password,email,date) VALUES ('{username}','{password}','{email}','{date}' )"""
                        conn.execute(newuser)
                        connect.commit()
                        conn.close()
                        return redirect(url_for("login"))
                    elif rowsmail:
                        conn.execute(f"SELECT email FROM users WHERE EXISTS(SELECT * FROM users WHERE email='{email}')")
                        rowsmail=conn.fetchall()
                        if len(rowsmail) == 0:
                            date = datetime.datetime.now(pytz.timezone("Europe/Istanbul")).strftime("%Y-%m-%d %H:%M:%S")
                            newuser = f"""INSERT INTO users (username,password,email,date) VALUES ('{username}','{password}','{email}','{date}' )"""
                            conn.execute(newuser)
                            connect.commit()
                            conn.close()
                            return redirect(url_for("login"))
                        else:
                            flash("This email is already associated with another account")
                else:
                    flash("This username is already taken")
                    

    return render_template("newuserpage.html")
                    

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

@app.route("/profile/<username>")
def profile(username):
    if username == "Anonymous":
        return(redirect("/"))
    else:
        date = datetime.datetime.now(pytz.timezone("Europe/Istanbul")).strftime("%Y-%m-%d")
        connect, conn = get_db_connection()
        command = f"SELECT * FROM BOARDS"
        conn.execute(command)
        board = conn.fetchall()
        posts = []
        for i in board:
            command = f"SELECT * FROM {i[1]} WHERE sender = '{username}'"
            conn.execute(command)
            data = conn.fetchall()
            print(data)
            if data:
                for x in data:
                    boardname = i
                    posts.append((i,x))
        total = len(posts)
        if total != 0:
            return render_template("profile.html",date=date,posts=posts,data=data,boardname=boardname,total=total,username= username)
        else:
            return render_template("profile.html",total=total,username=username)

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
                        return redirect(url_for("profile", username= current_user.username))
                    else:
                        flash("Password is wrong")
            else:
                flash("No user found with that username")
    return render_template("loginpage.html")

@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('index'))

def checkadmin():
    connect, conn = get_db_connection()
    if current_user.is_authenticated:
        conn.execute(f"SELECT isadmin FROM USERS WHERE username='{current_user.username}'")
        selected_user = conn.fetchone()
        admindata = selected_user[0]
        connect.commit()
        connect.close()
        return admindata
    else:
        return None

@app.route("/admin")
@login_required
def admin():
    cond = checkadmin()
    if cond == "yes":
        userdata = table("users")
        usercount = len(userdata)
        userdata.sort()
        boarddata = table("boards")
        return render_template("adminpage.html",userdata = userdata,boarddata=boarddata,usercount=usercount,postcount=postcount,allboards=boardowner)
    else:
        return redirect("/")

def postcount(username):
    connect, conn = get_db_connection()
    command = f"SELECT * FROM BOARDS"
    conn.execute(command)
    board = conn.fetchall()
    posts = []
    for i in board:
        command = f"SELECT * FROM {i[1]} WHERE sender = '{username}'"
        conn.execute(command)
        data = conn.fetchall()
        if data:
            for x in data:
                boardname = i
                posts.append((i,x))
    total = len(posts)
    return total

def boardowner():
    connect, conn = get_db_connection()
    command = f"SELECT * FROM BOARDS"
    conn.execute(command)
    boards = conn.fetchall()
    allboards = []
    for i in boards:
        allboards.append((i[0],i[1],i[2]))
    allboards.sort()
    return allboards

def boardcreator(boardname):
    connect, conn = get_db_connection()
    command = f"SELECT * FROM BOARDS WHERE board = '{boardname}'"
    conn.execute(command)
    board = conn.fetchone()
    boardnm = board[1]
    boardcreator = board[2]
    connect.close()
    return boardnm,boardcreator

def table(tablename):
    connect, conn = get_db_connection()
    tables = gettables()
    conn.execute(f"SELECT * FROM {tablename}")
    data = conn.fetchall()
    connect.close()
    return data
    

def gettables():
    connect, conn = get_db_connection()
    conn.execute("""SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'""")
    tables = []
    tabletuple = conn.fetchall()
    for i in tabletuple:
        tables.append(i[0])
    connect.close()
    return tables


if __name__ == "__main__":
    app.run(debug=True)