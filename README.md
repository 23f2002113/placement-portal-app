## placement-portal-app
This is a placement portal app  which is made by using simple HTML, CSS, FLASK .It is used for Students to create their students profile and search for job and for companies to create their company profile and  get employee for their company.

## Features
* User(Students and Companies) registration and authentication.Admin don't required registration.
* Students edit their profile,view the companies whose registration is approved and also view the approved drives of these approved companies,view the applied drive and their status and also see the application history and their status.
* After registration approved by admin,company edit their profile ,create drives ,and sees the application  for the drive and also see the profile of students and update their application status.
* Admin view the company registeration and their drives and approved their registration and drives and also view the students details and their application,etc.

## Technologies Used
Frontend: HTML, CSS , Jinja2 templating
Backend: Flask
Database: SQLite
ORM: Flask SQLAlchemy

## Milestones
1)Database Models
* Create models for User, Student profile,Company profile,Placement drive,Application and placements.
* Set up relationships and initialized the SQLite database.

2)Authentication and Role Management
* Implemented user(Students,Companies) registration and login for all user.
* Role-based access for admin,companies and students dashboards.

3)Admin Dashboard and Management
*Dashboard showing total companies, students, placement drives,placements and job applications.
*Approve and Reject company profiles registration and also job postings/placement drives created by these approved companies.
*View and manage all students, companies, job postings and applications .
*Search students by name, ID, or contact.
*Search companies by name or industry.
*Blacklist/deactivate companies or students from the system.

4)Company Dashboard and Job Management
*Companies can only access the dashboard when approved by admin.
*View dashboard with posted jobs/placement drives created and received applications.
*Post new job positions with required skills, experience, and salary range.
*Update job posting status (Active/Closed).
*Review student applications and shortlist candidates.
*Share acceptance or rejection status(Shortlisted / Selected / Rejected) to applicants.
*View shortlisted student profiles and resumes.

5)Student Dashboard and Job Application System
*Register, log in, and update profile (education, skills, resume).
*View and Search approved job postings by company, position, or skills.
*Apply for jobs and track application status.
*View applied jobs with application status.

6)Job Application History and Status Tracking
*Store and display complete job application history.
*Prevent duplicate job applications for the same job posting.
*Ensure only approved companies can create placement drives.
*Ensure students can view and apply only to approved placement drives.
*Maintain status updates (Applied / Shortlisted / Interview / Rejected / Placed  etc.).





