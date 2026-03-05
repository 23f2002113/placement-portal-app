from flask import Flask,render_template,redirect,request,url_for
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
                    company = CompanyProfile.query.filter_by(user_id=this_user.id).first()
                    if company.approval_status == "approved":
                       return redirect(f"/company/{this_user.id}")
                    else:
                        return redirect("/login")
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
    
@app.route("/admin")
def admin():
    this_user = User.query.filter_by(role="admin").first()

    stats = {
        "total_companies": CompanyProfile.query.count(),
        "total_students": StudentProfile.query.count(),
        "total_drives": PlacementDrive.query.count(),
        "total_applications": Application.query.count(),
        "total_placements": Placement.query.count()
    }

    pending_companies = CompanyProfile.query.filter_by(approval_status="pending").all()
    pending_drives = PlacementDrive.query.filter_by(status="pending").all()
    
    all_companies = CompanyProfile.query.filter_by(approval_status = "approved").all()
    # all_companies = CompanyProfile.query.filter(CompanyProfile.approval_status != "blacklisted").all()
    all_students = StudentProfile.query.all()

    ongoing_drives = PlacementDrive.query.filter_by(status="approved").all()

    all_apps = Application.query.all()
    return render_template("admin_dashboard.html",this_user=this_user,stats=stats,pending_companies=pending_companies,pending_drives=pending_drives,all_companies=all_companies,all_students=all_students,ongoing_drives=ongoing_drives,all_apps=all_apps)

@app.route("/admin/company/<int:company_id>/<string:action>")
def manage_company(company_id, action):
    company = CompanyProfile.query.get(id=company_id)
    
    if action == "approve":
        company.approval_status = "approved"
    
    elif action == "reject":
        db.session.delete(company)
    
    elif action == "blacklist":
        company.approval_status = "blacklisted"
        
        drives = PlacementDrive.query.filter_by(company_id=company_id).all()
        for d in drives:
            d.status = "cancelled"
            Application.query.filter_by(drive_id=d.id).update({"status": "rejected"})
            
    db.session.commit()
    return redirect(url_for('admin'))

@app.route("/admin/student/blacklist/<int:student_id>")
def blacklist_student(student_id):
    student = StudentProfile.query.get(id=student_id)
    student.is_blacklisted = True
    
    Application.query.filter_by(student_id=student_id).update({"status": "rejected"})
    
    db.session.commit()
    return redirect(url_for('admin'))

@app.route("/admin/drive/<int:id>/<string:action>")
def manage_drive(id, action):
    drive = PlacementDrive.query.get(id=id)
    
    if action == "approve":
        drive.status = "approved" 
    elif action == "reject":
        drive.status = "rejected" 
    elif action == "complete":
        drive.status = "completed" 
        
    db.session.commit()
    return redirect(url_for('admin'))

@app.route("/admin/view_drive/<int:id>")
def view_drive(id):
    drive = PlacementDrive.query.get(id=id)
    return render_template("admin_drives.html", drive=drive)

@app.route("/admin/view_application/<int:id>")
def view_application(id):
    application = Application.query.get(id=id)
    return render_template("admin_student_application.html", application=application)

@app.route("/search")
def search():
    search_word = request.args.get("search")
    key = request.args.get("key")
    result = []

    if key == "student":
        result = StudentProfile.query.filter_by(name=search_word).first()
        if not result:
            result= StudentProfile.query.filter_by(id=search_word).first()

    else:
        result = CompanyProfile.query.filter_by(company_name=search_word).first()
        if not result:
            result = CompanyProfile.query.filter_by(id=search_word).first()

    return render_template("admin_result.html", result=result, key=key)


# @app.route("/company/<int:user_id")
# def company(user_id):


#     return render_template("company_dashboard.html")

# @app.route("/student/<int:user_id")
# def student(user_id):

#     return render_template("student_dashboard.html")



