from datetime import datetime
from .database import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False) 
    company_profile = db.relationship('CompanyProfile', backref='user', cascade="all, delete-orphan",uselist=False)                              
    student_profile = db.relationship('StudentProfile', backref='user',  cascade="all, delete-orphan", uselist=False)

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(20), unique=True)
    cgpa = db.Column(db.Float)
    department = db.Column(db.String(50))
    resume_link = db.Column(db.String(255))
    is_blacklisted = db.Column(db.Boolean, default=False) 
    applications = db.relationship('Application', backref='student', lazy=True)
    placements = db.relationship('Placement',backref='student',lazy=True)

class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    hr_contact = db.Column(db.String(20))
    website = db.Column(db.String(100))
    approval_status = db.Column(db.String(20), default="pending") 
    drives = db.relationship('PlacementDrive', backref='company', lazy=True)

class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id'), nullable=False)
    drive_name=db.Column(db.String(150),nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text)
    salary_package = db.Column(db.String(50))
    eligibility_criteria = db.Column(db.Text)
    location = db.Column(db.String(100))
    application_deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="pending") 
    applications = db.relationship('Application', backref='drive', lazy=True)
    placed_students = db.relationship('Placement', backref='drive', lazy=True)

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    application_date = db.Column(db.DateTime,default=datetime.utcnow)
    status = db.Column(db.String(20), default="Applied") 

class Placement(db.Model):
    __tablename__= "placements"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    package_offered = db.Column(db.String(50))
    selection_date = db.Column(db.DateTime, default=datetime.utcnow)




