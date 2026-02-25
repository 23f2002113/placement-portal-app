from flask import Flask,render_template,redirect,request 
from flask import current_app as app 
from .models import *

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("pwd")

