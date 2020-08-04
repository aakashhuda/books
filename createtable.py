from flask import Flask
from booktable import *

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://pahyiebhyfhgnp:de01692f6d3c0862f559e5f27757682e990d8359742d44f1beb7b1fb92fcc62a@ec2-34-234-228-127.compute-1.amazonaws.com:5432/d5or8olf1atoci'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

def main():
    db.create_all()

if __name__=="__main__":
    with app.app_context():
        main()