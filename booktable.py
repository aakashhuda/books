from flask_sqlalchemy import SQLAlchemy 

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key= True)
    isbn = db.Column(db.String, nullable = False)
    title = db.Column(db.String, nullable = False)
    author = db.Column(db.String, nullable = False)
    year = db.Column(db.Integer, nullable = False)

class User(db.Model):
    __tablename__= "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)

class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=True)
    rate = db.Column(db.Integer,nullable=True)
    rev_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    use_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)