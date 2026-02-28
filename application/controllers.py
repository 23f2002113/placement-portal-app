from flask import Flask,render_template,redirect,request 
from flask import current_app as app 
from .models import *

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("pwd")
        this_user= User.query.filter_by(username=username).first()
        if this_user:
            if this_user.password==password:
                if this_user.role=="admin":
                    return redirect("/admin")
                elif this_user.role=="company":
                    return redirect(f"/company/{this_user.id}")
                else:
                    return redirect(f"/student/{this_user.id}")                     
            else :
                return render_template("incorrect_password.html")
        else :
            return render_template("not_exist.html")
    return render_template("login.html")



@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        username=request.form.get("username")
        email=request.form.get("email")
        password=request.form.get("pwd")
        role=request.form.get("role")
        this_user=User.query.filter_by(username=username).first()
        this_email=User.query.filter_by(email=email).first()
        if this_user or this_email:
            return render_template("already_exist.html")
        else:
            new_user=User(username=username,email=email,password=password,role=role)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
    return render_template("register.html")

@app.route("/")
def index():
    return render_template("index.html")
    


# @app.route("/admin")
# def admin():


#     return render_template("admin_dashboard.html")

# @app.route("/company/<int:user_id")
# def company(user_id):


#     return render_template("company_dashboard.html")

# @app.route("/student/<int:user_id")
# def student(user_id):

#     return render_template("student_dashboard.html")



