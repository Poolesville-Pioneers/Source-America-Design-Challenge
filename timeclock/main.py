from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, send_from_directory
from flask_login import login_required, current_user
from . import db
from .models import User, Shift, Job
from sqlalchemy.sql import func
import csv
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template("home.html")

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', jobs=get_jobs(), shift=get_current_shift())
    
@main.route('/clockin', methods = ['GET','POST'])
@login_required
def clockin():
    if current_user.admin:
        return redirect(url_for('main.admin_dashboard'))
        
    if request.method=='GET':
        return render_template("dashboard.html", jobs=get_jobs())
        
    else:
        job_id = request.form.get('id')
        
        new_shift = Shift(job=job_id, start=func.now(), employee=current_user.id)
        
        db.session.add(new_shift)
        db.session.commit()
        
        return redirect(url_for('main.dashboard'))
        
def get_jobs():
    jobs = Job.query.all()
    return jobs

def get_job_by_id(id):
    job = Job.query.filter_by(id=id).first()
    return job

def get_employee_by_id(id):
    employee = User.query.filter_by(id=id).first()
    return employee

def get_current_shift():
    shift = Shift.query.filter_by(employee=current_user.id).filter_by(end=None).first()
    return shift
    
@main.route('/clockout', methods = ['GET','POST'])
@login_required
def clockout():
    if current_user.admin:
        return redirect(url_for('main.admin_dashboard'))
        
    if request.method=='GET':
        return render_template("dashboard.html")
        
    else:        
        shift = get_current_shift()
        setattr(shift, 'end', func.now())
        db.session.commit()
        flash('Clocked out successfully')
        
        return redirect(url_for('main.dashboard'))
    
@main.route('/admin-dashboard')
def admin_dashboard():
    if current_user.is_authenticated:
        if not current_user.admin:
            flash("Please login with an authorized account")
            return redirect(url_for('auth.admin_login'))
        else:
            return render_template('admin-dashboard.html')
    abort(403)

@main.route("/employees/")
def employees():
    if not current_user.is_authenticated:
        abort(403)
    if not current_user.admin:
        flash("Please login with an authorized account")
        return redirect(url_for('auth.admin_login'))

    employees = User.query.filter_by(admin=None).all()
    return render_template("employees.html", employees=employees)

@main.route("/update_employee/", methods=['GET','POST'])
def update_employee():
    if not current_user.is_authenticated:
        abort(403)
    if not current_user.admin:
        flash("Please login with an authorized account")
        return redirect(url_for('auth.admin_login'))

    id = request.args.get('id', "")
    e = get_employee_by_id(id)
    if e == None:
        flash("Employee Not Found")
        return redirect(url_for('main.employees'))
    return render_template("updateemployee.html", employee=e)

@main.route("/cmd_update_employee/", methods=['POST'])
def cmd_update_employee():
    id = request.form.get('id', "")
    user = request.form.get('user', "")
    password = request.form.get('password', "")

    e = get_employee_by_id(id)
    e.user = user
    e.password = password

    db.session.commit()

    flash("Employee Information Successfully Updated!")
    return redirect(url_for('main.employees'))

@main.route("/jobs/")
def jobs():
    if not current_user.is_authenticated:
        abort(403)
    if not current_user.admin:
        flash("Please login with an authorized account")
        return redirect(url_for('auth.admin_login'))

    jobs = Job.query.all()
    return render_template("jobs.html", jobs=jobs)

@main.route("/update_job/", methods=['GET','POST'])
def update_job():
    if not current_user.is_authenticated:
        abort(403)
    if not current_user.admin:
        flash("Please login with an authorized account")
        return redirect(url_for('auth.admin_login'))

    id = request.args.get('id', "")
    j = get_job_by_id(id)
    if j == None:
        flash("Job Entry Not Found")
        return redirect(url_for('main.jobs'))
    return render_template("updatejob.html", job=j)

@main.route("/cmd_update_job/", methods=['POST'])
def cmd_update_job():
    id = request.form.get('id', "")
    name = request.form.get('name', "")
    wage = request.form.get('wage', "")

    j = get_job_by_id(id)
    j.name = name
    j.wage = wage

    db.session.commit()

    flash("Job Information Successfully Updated!")
    return redirect(url_for('main.jobs'))

@main.route("/cmd_delete_employee/", methods=['POST'])
def cmd_delete_employee():
    """ Accepts confirmation from the delete employee form"""
    id = request.form.get('id', "")
    confirm = request.form.get("confirm", "")
    if confirm != "DELETE":
        flash(f"Contact '{id}' NOT deleted. Please enter DELETE in the confirm field.")
        return redirect(url_for('main.jobs'))
        
    index = get_employee_by_id(id)
    User.query.filter(User.id == id).delete()
    db.session.commit()


    if index != None:
        flash(f"Employee '{id}' was succesfully deleted!")
        return redirect(url_for('main.employees'))
    else:
        flash(f"Employee '{id}' was not found")
        return redirect(url_for('main.employees'))

@main.route("/delete_employee/")
def delete_employee():
    """ Deletes an employee based on id"""
    id = request.args.get('id', "")
    return render_template("delete_employee.html", id=id)

@main.route("/delete_job/")
def delete_job():
    """ Deletes a contact based on id"""
    id = request.args.get('id', "")
    return render_template("delete_job.html", id=id)

@main.route("/cmd_delete_job/", methods=['POST'])
def cmd_delete_job():
    """ Accepts confirmation from the delete job form"""
    id = request.form.get('id', "")
    confirm = request.form.get("confirm", "")
    if confirm != "DELETE":
        flash(f"Contact '{id}' NOT deleted. Please enter DELETE in the confirm field.")
        return redirect(url_for('main.jobs'))
        
    index = get_job_by_id(id)
    Job.query.filter(Job.id == id).delete()
    db.session.commit()


    if index != None:
        flash(f"Job '{id}' was succesfully deleted!")
        return redirect(url_for('main.jobs'))
    else:
        flash(f"Job '{id}' was not found")
        return redirect(url_for('main.jobs'))


@main.route('/create-job', methods = ['GET','POST'])
def create_job():
    if not current_user.is_authenticated:
        abort(403)
    if not current_user.admin:
        flash("Please login with an authorized account")
        return redirect(url_for('auth.admin_login'))
        
    if request.method=='GET':
        return render_template("createjob.html")
        
    else:    
        
        name = request.form.get('name')
        salary = request.form.get('salary')
        
        j = Job(name=name, wage=salary)
        db.session.add(j)
        db.session.commit()

        return redirect(url_for('main.jobs'))


     
@main.route('/clear-shifts', methods = ['GET', 'POST'])
def clear_shifts():
    if not current_user.is_authenticated:
        abort(403)
    if not current_user.admin:
        flash("Please login with an authorized account")
        return redirect(url_for('auth.index'))
    
    if request.method=='GET':
        return render_template("admin-dashboard.html")
        
    else:
        Shift.query.delete()
        db.session.commit()
        flash("Shifts successfully cleared")
        return redirect(url_for('main.admin_dashboard'))
        
@main.route('/download', methods = ['GET', 'POST'])
def download():
    if not current_user.is_authenticated:
        abort(403)
    if not current_user.admin:
        flash("Please login with an authorized account")
        return redirect(url_for('auth.index'))


    if request.method=='GET':
        return render_template("admin-dashboard.html")
        
    else:
        table = request.form.get('table')
        
        if(table == 'users'):
            model = User
        elif(table == 'jobs'):
            model = Job
        else:
            model = Shift
            table = "shift"
        
        records = model.query.all()
        
        print('current directory =',os.getcwd())
        outfile_name = r'TimeClock\static\shift.csv'
        outfile_name2 = r'shift.csv'
        outfile = open(outfile_name, 'w')
        outcsv = csv.writer(outfile)
        
        outcsv.writerow([column.name for column in model.__mapper__.columns])
        [outcsv.writerow([getattr(curr, column.name) for column in model.__mapper__.columns]) for curr in records]

        outfile.close()
        
        return send_from_directory('static', outfile_name2, as_attachment=True)
    

