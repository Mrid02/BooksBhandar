import os
from helpers import *
import requests

from flask import Flask, session, request, redirect, url_for, render_template,flash, jsonify
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


@app.route("/",methods=["GET","POST"])
@login_required
def index():
    #return  "Welcome to  BOOKS BHANDAR"
    username = session.get('user_name')
    session['books'] = []
    
    
    if request.method=="POST":
        
        text = request.form.get('text')
        
        #rows = db.execute("SELECT * FROM books WHERE isbn iLIKE '%'+query+'%' OR author iLIKE '%'+:query+'%' OR year iLIKE '%'+:query+'%'",
        #                    {"query":query}).fetchall()
        
        data=db.execute("SELECT * FROM books WHERE author iLIKE '%"+text+"%' OR title iLIKE '%"+text+"%' OR isbn iLIKE '%"+text+"%'").fetchall()
        for x in data:
            session['books'].append(x)

        if len(session["books"])==0:
            return render_template("error.html",message="No results found!")

        return render_template("index.html",data=session['books'])
        


        
    return render_template("index.html")


@app.route("/login", methods=["GET","POST"])
def login():
    session.clear()
    #login user in
    message=""
    if request.method =="POST":
        usernameLogin = request.form.get("username")
        passwordLogin = request.form.get("pwd")

        userdata = db.execute("SELECT * from users WHERE username=:username",
                                {"username":usernameLogin}).fetchone()

        if userdata == None or userdata.password != passwordLogin:
            return render_template("login.html",message="Invalid username or password! Try Again.")

        session['user_id'] = userdata.id 
        session['user_name']= userdata.username

        return redirect("/")

    else:
        return render_template("login.html",message=message)


@app.route("/logout")
@login_required
def logout():
    session.clear()

    return render_template("login.html",message="")


@app.route("/register", methods=["GET","POST"])
def register():
    session.clear()
    message=""
    if request.method =="POST":
        usernameLogin = request.form.get("username")
        passwordLogin = request.form.get("pwd")
        confirmLogin  = request.form.get("cnfpwd")

        if usernameLogin == "":
            return render_template("register.html",message="Please provide username")
        
        if passwordLogin == "":
            return render_template("register.html",message="Please provide password")

        if confirmLogin == "":
            return render_template("register.html",message="Please confirm password") 

        check = db.execute("SELECT * from users WHERE username=:username",
                                {"username":usernameLogin}).fetchone()

    
        if check != None:
            return render_template("register.html",message="Sorry, Username already exists")
        
        elif passwordLogin != confirmLogin:
            return render_template("register.html",message="Password doesn't match")

        requestdata = db.execute("INSERT INTO users (USERNAME,PASSWORD) VALUES (:username,:password)",
                                {"username":usernameLogin,"password":passwordLogin})
       
        db.commit()
        flash("Account created")
        return render_template("login.html",message="Account created, Now you can log in.")

    else:
        return render_template("register.html",message=message)

@app.route("/book/<string:isbn>",methods=["GET","POST"])
@login_required
def bookpage(isbn):

    message=""
    book = db.execute("SELECT * FROM books where isbn=:isbn",{"isbn":isbn}).fetchone()
    userid = session.get('user_id')
    session['reviews'] = []
    alreadyreview = db.execute("SELECT * FROM reviews WHERE user_id=:user_id AND book_id=:book_id",{"user_id":userid,"book_id":book.id}).fetchone()

    if request.method=="POST" and alreadyreview != None:
        message="You have already added review can't again"

    if request.method=="POST" and alreadyreview == None:
        rating = request.form.get("stars")
        review = request.form.get("textarea")
        db.execute("INSERT INTO reviews (USER_ID,BOOK_ID,RATING,REVIEW) VALUES (:userid,:bookid,:rating,:review)",{"userid":userid,"bookid":book.id,"rating":rating,"review":review})
        db.commit()
        message="Review posted"

    
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": goodreadskey , "isbns":isbn})
    average_rating=res.json()['books'][0]['average_rating']
    work_ratings_count=res.json()['books'][0]['work_ratings_count']

    #reviews = db.execute("SELECT * FROM reviews WHERE book_id=:book_id",{"book_id":book.id}).fetchall()

    results = db.execute("SELECT users.username, review, rating FROM users INNER JOIN reviews  ON users.id = reviews.user_id WHERE book_id = :book",{"book": book.id})
    reviews = results.fetchall()

    for rev in reviews:
        session['reviews'].append(rev)

    return render_template("book.html",reviews=session['reviews'],book=book,average_rating=average_rating,work_ratings_count=work_ratings_count,message=message)

    @app.route("/api/<string:isbn>",methods=['GET'])
    @login_required
    def api(isbn):
        book = db.execute("SELECT * FROM books where isbn=:isbn",{"isbn":isbn}).fetchone()
        if book==None:
            return render_temple('402.html')

        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "JDyMvBsjiT8qooOEdgsVjA", "isbns":isbn})
        average_rating=res.json()['books'][0]['average_rating']
        work_ratings_count=res.json()['books'][0]['work_ratings_count']

        x = jsonify({
              
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": isbn,
            "review_count": work_ratings_count,
            "average_score": average_rating
          })
        
        return x
