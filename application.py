import os
import requests

from flask import Flask, session, request, render_template, redirect,url_for,flash,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for('login'))
    return render_template("login.html")

@app.route("/register")
def register():
    if "user_id" in session:
        return redirect(url_for('login'))
    return render_template("signup.html")

@app.route("/signup", methods = ["POST", "GET"])
def signup():
    if "user_id" in session:
        return redirect(url_for('login'))
    username = request.form.get("username")
    password = request.form.get("password")
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    check = db.execute("SELECT * FROM users WHERE username = :username",{"username":username}).fetchone()
    if check:
        flash("Username already exists!")
        return redirect(url_for('signup'))

    db.execute("INSERT INTO users(username, password, first_name, last_name) VALUES (:username, :password, :firstname, :lastname)",
    {"username": username, "password": password, "firstname": firstname, "lastname": lastname})
    db.commit()
    flash("Successfully signed up! Enter your username & password to login.")

    return redirect(url_for('loginpage'))

@app.route("/loginpage")
def loginpage():
    return render_template("login.html")

@app.route("/login", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password",{"username":username,"password":password}).fetchone()
        if user is None:
            flash("Incorrect usernname/password")
            return redirect(url_for('loginpage'))
        session["user_id"] = user.id
        return render_template("search.html", user = user)
    else:
        if "user_id" in session:
            id = session["user_id"]
            user = db.execute("SELECT * FROM users WHERE id = :id",{"id":id}).fetchone()
            return render_template("search.html",user=user)
        else:
            return redirect(url_for('loginpage'))
              


@app.route("/logout")
def logout():
    if "user_id" in session:
        session.pop("user_id", None)
        flash("You have been logged out!", "info")
        return redirect(url_for('loginpage'))
    return redirect(url_for('loginpage'))
    

@app.route("/search", methods = ["POST"])
def search():
    if "user_id" in session:
        id = session["user_id"]
        user = db.execute("SELECT * FROM users WHERE id=:id",{"id":id}).fetchone()
        value = request.form.get("inlineRadioOptions")
        search = request.form.get("search")
        search_q = "%" + search + "%"
        if value == "isbn":
            books = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn", {"isbn": search_q}).fetchall()
            if not books:
                flash("No such book found")
                return redirect(url_for('login'))
            return render_template("searchlist.html",books = books)
        elif value == "title":
            books = db.execute("SELECT * FROM books WHERE title LIKE :title OR lower(title) LIKE :title OR upper(title) LIKE :title", {"title": search_q}).fetchall()
            if not books:
                flash("No such book found")
                return redirect(url_for('login'))
            return render_template("searchlist.html",books = books) 
        elif value == "author":
            books = db.execute("SELECT * FROM books WHERE author LIKE :author OR lower(author) LIKE :author OR upper(author) LIKE :author", {"author": search_q}).fetchall()
            if not books:
                flash("No such book found")
                return redirect(url_for('login'))
            return render_template("searchlist.html",books = books)
        flash("No such book found")
        
        return redirect(url_for('login'))
    else:
        return redirect(url_for('loginpage'))

@app.route("/book/<int:id>")
def book(id):
    if "user_id" in session:
        book = db.execute("SELECT * FROM books WHERE id = :id",{"id":id}).fetchone()
        if book is None:
            return render_template("error.html", message = "No such book found")
        isbn = book.isbn
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":"WLjWCyvJ02uFulD6OvYtIQ","isbns":isbn})
        if res.status_code !=200:
            raise Exception("Error: Api request unsuccessfull")
        data = res.json()
        avg_rating = data['books'][0]['average_rating']
        rate_count = data['books'][0]['ratings_count']
        isbn is None
        reviews = db.execute("SELECT text,rate,first_name,last_name FROM reviews JOIN users ON users.id=reviews.use_id WHERE rev_id = :rev_id",
        {"rev_id":id}).fetchall()
        return render_template("book.html",book=book,avg_rating = avg_rating, reviews = reviews,isbn=isbn,rate_count=rate_count)

    return redirect(url_for('loginpage'))

@app.route("/submitted/<int:book_id>",methods = ["POST"])
def submit(book_id):
    if "user_id" in session:
        user_id = session["user_id"]
        post_check = db.execute("SELECT FROM reviews WHERE use_id = :use_id AND rev_id=:rev_id",{"use_id":user_id, "rev_id":book_id}).fetchone()
        if not post_check is None:
            flash("You have already posted a review!", "info")
            return redirect(url_for('book',id = book_id)) 
        review = request.form.get("text")
        rate = int(request.form.get("rate"))
        db.execute("INSERT INTO reviews(text, rate, rev_id, use_id) VALUES (:text, :rate, :rev_id, :use_id)",
        {"text":review,"rate":rate,"rev_id":book_id,"use_id":user_id})
        db.commit()
        return redirect(url_for('book',id = book_id))
    return redirect(url_for('loginpage'))

@app.route("/api/<isbn>")
def api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn=:isbn",{"isbn":isbn}).fetchone()
    if book is None:
        return jsonify({"book not found: 404 error"}),404
    review_count = db.execute("SELECT COUNT(text) FROM reviews WHERE rev_id = :rev_id",{"rev_id":book.id}).fetchone()[0]
    average_rating = db.execute("SELECT AVG(rate) FROM reviews WHERE rev_id = :rev_id",{"rev_id":book.id}).fetchone()[0]
    avg = round(float(average_rating),2)
    return jsonify({
        "title":book.title,
        "author":book.author,
        "year":book.year,
        "isbn":book.isbn,
        "review_count":review_count,
        "average_rating":avg
    })