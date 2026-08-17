from flask import Flask,render_template,request,redirect,session 
from db import Base,engine,SessionLocal 
import models 
import PyPDF2 
import json 
import docx


app = Flask(__name__)
app.secret_key = "secret123"

Base.metadata.create_all(bind=engine)

@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashbord")
    return redirect("/login")
@app.route("/create-account",methods=["GET","POST"])
def create_account():
    

if __name__ == "__main__":
    app.run(debug=True)
