from flask import Flask,render_template,redirect,request,url_for,flash
from datetime import datetime
from flask import current_app as app 
from .models import *
from werkzeug.utils import secure_filename
import os

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
            if role == "company":
                new_profile = CompanyProfile(
                    user_id=new_user.id, 
                    company_name=username,
                    approval_status="pending"
                )
                db.session.add(new_profile)
            
            elif role == "student":
                new_profile = StudentProfile(
                    user_id=new_user.id, 
                    name=username
                )
                db.session.add(new_profile)

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
    all_students = StudentProfile.query.all()

    ongoing_drives = PlacementDrive.query.filter_by(status="approved").all()

    all_apps = Application.query.all()
    return render_template("admin_dashboard.html",this_user=this_user,stats=stats,pending_companies=pending_companies,pending_drives=pending_drives,all_companies=all_companies,all_students=all_students,ongoing_drives=ongoing_drives,all_apps=all_apps)

@app.route("/admin/company/<int:company_id>/<string:action>")
def manage_company(company_id, action):
    company = CompanyProfile.query.get(company_id)
    
    if action == "approve":
        company.approval_status = "approved"
    
    elif action == "reject":
        user = User.query.get(company.user_id)
        db.session.delete(user)
    
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
    student = StudentProfile.query.get(student_id)
    student.is_blacklisted = True
    
    Application.query.filter_by(student_id=student_id).update({"status": "rejected"})
    
    db.session.commit()
    return redirect(url_for('admin'))

@app.route("/admin/drive/<int:id>/<string:action>")
def manage_drive(id, action):
    drive = PlacementDrive.query.get(id)
    
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
    drive = PlacementDrive.query.get(id)
    return render_template("admin_drives.html", drive=drive)

@app.route("/admin/view_application/<int:id>")
def view_application(id):
    application = Application.query.get(id)
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


@app.route("/company/<int:user_id>")
def company_dashboard(user_id):
    this_user = User.query.get(user_id)
    company = CompanyProfile.query.filter_by(user_id=user_id).first()

    if company.approval_status != "approved":
        return "Your company status are  not approved"

    upcoming_drives = PlacementDrive.query.filter_by(company_id=company.id).filter(PlacementDrive.status != 'completed').all()
    closed_drives = PlacementDrive.query.filter_by(company_id=company.id, status='completed').all()

    return render_template("company_dashboard.html",this_user=this_user,company=company,upcoming_drives=upcoming_drives,closed_drives=closed_drives)

@app.route("/company/<int:user_id>/create_drive", methods=["GET", "POST"])
def create_drive(user_id):
    company = CompanyProfile.query.filter_by(user_id=user_id).first()

    if company.approval_status != "approved":
        return "Your company not be approved by Admin "

    if request.method == "POST":
        deadline_str = request.form.get("deadline")
        deadline_obj = datetime.strptime(deadline_str, '%Y-%m-%d') if deadline_str else None
        
        new_drive = PlacementDrive(
            company_id=company.id,
            drive_name=request.form.get("name"),
            job_title=request.form.get("title"),
            job_description=request.form.get("description"),
            salary_package=request.form.get("salary"),
            location=request.form.get("location"),
            eligibility_criteria=request.form.get("criteria"),
            application_deadline=deadline_obj,
            status="pending" 
        )
        db.session.add(new_drive)
        db.session.commit()
        return redirect(url_for('company_dashboard', user_id=user_id))
    
    return render_template("company_drive_create.html", user_id=user_id)

@app.route("/company/drive/<int:drive_id>/details")
def view_drive_details(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    return render_template("company_drive_details.html", drive=drive)

@app.route("/company/drive/<int:drive_id>/applications")
def view_drive_applications(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template("company_update_application.html", drive=drive, applications=applications)

@app.route("/company/application/<int:app_id>")
def review_application(app_id):
    application = Application.query.get(app_id)
    return render_template("company_student_application.html", application=application)

@app.route("/company/application/<int:app_id>/status/<string:status>")
def update_application_status(app_id, status):
    application = Application.query.get(app_id)
    application.status = status
    if status == "Selected":
        existing_placement = Placement.query.filter_by(
            student_id=application.student_id, 
            drive_id=application.drive_id
        ).first()

        if not existing_placement:
            drive = PlacementDrive.query.get(application.drive_id)
            
            new_placement = Placement(
                student_id=application.student_id,
                drive_id=application.drive_id,
                package_offered=drive.salary_package, 
                selection_date=datetime.utcnow()
            )
            db.session.add(new_placement)

    elif status == "Rejected":
        existing_placement = Placement.query.filter_by(
            student_id=application.student_id, 
            drive_id=application.drive_id
        ).first()
        if existing_placement:
            db.session.delete(existing_placement)

    db.session.commit()
    return redirect(url_for('view_drive_applications', drive_id=application.drive_id))

@app.route("/company/drive/<int:drive_id>/complete")
def complete_drive(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    drive.status = "completed"
    db.session.commit()
    return redirect(url_for('company_dashboard', user_id=drive.company.user_id))

@app.route("/company/<int:user_id>/edit_profile", methods=["GET", "POST"])
def edit_company_profile(user_id):
    company = CompanyProfile.query.filter_by(user_id=user_id).first()
    
    if request.method == "POST":
        company.company_name = request.form.get("company_name")
        company.website = request.form.get("website")
        company.hr_contact = request.form.get("hr_contact")
        
        db.session.commit()
        return redirect(url_for('company_dashboard', user_id=user_id))
    
    return render_template("company_edit_profile.html", company=company)


UPLOAD_FOLDER = 'static/uploads/resumes'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/student/<int:user_id>")
def student_dashboard(user_id):
    this_user = User.query.get(user_id)
    student = StudentProfile.query.filter_by(user_id=user_id).first()
    
    if student.is_blacklisted:
        return "You have been blacklisted."

    companies = CompanyProfile.query.filter_by(approval_status="approved").all()
    
    applied_apps = Application.query.filter_by(student_id=student.id).all()
    
    return render_template("student_dashboard.html", this_user=this_user, student=student, companies=companies, applied_apps=applied_apps)

@app.route("/student/<int:user_id>/profile", methods=["GET", "POST"])
def edit_student_profile(user_id):
    student = StudentProfile.query.filter_by(user_id=user_id).first()
    if request.method == "POST":
        student.name = request.form.get("student_name")
        student.roll_no = request.form.get("roll_no")
        student.cgpa = request.form.get("cgpa")
        student.department = request.form.get("department")
        
        file = request.files.get('resume')
        if file and allowed_file(file.filename):
            filename = secure_filename(f"resume_{user_id}_{file.filename}")
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            student.resume_link = filename 
            
        db.session.commit()
        return redirect(url_for('student_dashboard', user_id=user_id))
    
    return render_template("student_edit_profile.html", student=student)

@app.route("/student/company/<int:company_id>")
def view_company_for_student(company_id):
    company = CompanyProfile.query.get(company_id)
    drives = PlacementDrive.query.filter_by(company_id=company_id, status="approved").all()
    u_id = request.args.get('user_id')
    return render_template("student_company.html", company=company, drives=drives, student_user_id=u_id)

@app.route("/student/drive/<int:drive_id>")
def view_drive_for_student(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    u_id = request.args.get('user_id') 
    return render_template("student_drives.html", drive=drive, current_user_id=u_id, student_user_id=u_id)

@app.route("/student/apply/<int:drive_id>", methods=["POST"])
def apply_for_drive(drive_id):
    user_id = request.form.get("user_id") 
    student = StudentProfile.query.filter_by(user_id=user_id).first()
    drive = PlacementDrive.query.get(drive_id)

    if drive.status != "approved":
        return "This drive is not approved "

    existing = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()
    if existing:
        return "You have already applied for this job."

    new_app = Application(student_id=student.id, drive_id=drive_id, status="Applied")
    db.session.add(new_app)
    db.session.commit()
    return redirect(url_for('student_history', user_id=user_id))

@app.route("/student/history/<int:user_id>")
def student_history(user_id):
    student = StudentProfile.query.filter_by(user_id=user_id).first()
    apps = Application.query.filter_by(student_id=student.id).all()
    return render_template("student_application_history.html", student=student, apps=apps)

@app.route("/student/search")
def student_search():
    search_word = request.args.get("search")
    key = request.args.get("key") 
    user_id = request.args.get("user_id")
    results = []

    if key == "company":
        results = PlacementDrive.query.join(CompanyProfile).filter(
            CompanyProfile.company_name.like(f"%{search_word}%"),
            PlacementDrive.status == "approved"
        ).all()

    elif key == "position":
        results = PlacementDrive.query.filter(
            PlacementDrive.job_title.like(f"%{search_word}%"),
            PlacementDrive.status == "approved"
        ).all()

    elif key == "skills":
        results = PlacementDrive.query.filter(
            PlacementDrive.eligibility_criteria.like(f"%{search_word}%"),
            PlacementDrive.status == "approved"
        ).all()

    return render_template("student_result.html", results=results, key=key, search_word=search_word,user_id=user_id)

    




