import os
import csv
import requests

from flask import Flask, session, request, render_template, redirect,url_for,flash,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books(isbn,title,author,year) VALUES (:isbn,:title,:author,:year)",{"isbn":isbn, "title":title,"author":author,"year":year})
        print(f"ADDED THE BOOK HAVING {isbn} {title} {author} {year}")
    db.commit()
    print("Insertion Done")
    
if __name__=="__main__":
    with app.app_context():
        main()