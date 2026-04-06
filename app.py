from flask import Flask, request, render_template, session, url_for, redirect
import mysql.connector
import re
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

db = mysql.connector.connect(
    host=os.environ.get("MYSQLHOST", "maglev.proxy.rlwy.net"),
    user=os.environ.get("MYSQLUSER", "root"),
    password=os.environ.get("MYSQLPASSWORD", "CyfgvyOzUlbbZpCnqfVTteocosJJslff"),
    database=os.environ.get("MYSQLDATABASE", "railway"),
    port=int(os.environ.get("MYSQLPORT", 50473))
)

cursor = db.cursor()

# Create table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS account (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE
    )
""")

db.commit()

# @app.route("/")
# def dashboard():
    

# @app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username and password:
            cursor = db.cursor(dictionary=True)

            sql = "select * from account where username = %s"
            cursor.execute(sql, (username,))
            account = cursor.fetchone()

            if account and check_password_hash(account["password"], password):
                session["loggedin"] = True
                session["id"] = account["id"]
                session["username"] = account["username"]
                cursor.close()
                db.commit()
                # return render_template("index.html")
                return redirect(url_for("dashboard"))
            else:
                msg = "Incorrect username or password"
        else:
            msg = "Fill both username and password"
    return render_template("login.html", msg=msg)

@app.route("/")
def dashboard():
    if "loggedin" in session:
        return render_template("index.html")
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.clear()
    # return render_template("login.html")
    return redirect(url_for("login"))

@app.route("/registration", methods=["GET", "POST"])
def registration():
    msg=""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        hashed_password = generate_password_hash(password)

        if username and password and email:
            cursor = db.cursor(dictionary=True)

            sql = "select * from account where username = %s"
            cursor.execute(sql, (username,))
            account = cursor.fetchone()

            if account:
                msg = "You already have an account"
            elif not re.match(r"[^@]+@[^@]+\.[^@]", email):
                msg="Type the proper email syntax"
            else:
                sql = "insert into account (username, password, email) values (%s, %s, %s)"
                cursor.execute(sql, (username,  hashed_password, email))
                cursor.close()
                db.commit()
                msg = "You have succcessfully registered"
        else:
            msg = "Submit all username, password and email"
    return render_template("registration.html", msg=msg)

if __name__ == "__main__":
 app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
