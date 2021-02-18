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
        #I replaced these with the get_current_shift() method
        #id = request.form.get('id')
        
        #shift = Shift.query.filter_by(job=job_id).filter_by(employee=current_user.id).all()[-1]
        
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
        
        job = Job.query.filter_by(name=name).first()
            
        setattr(job, 'salary', salary)
        db.session.commit()
        
        return redirect(url_for('main.admin_dashboard'))
        
@main.route('/update-wage', methods = ['GET','POST'])
def update_wage():
    if not current_user.is_authenticated:
        abort(403)
    if not current_user.admin:
        flash("Please login with an authorized account")
        return redirect(url_for('auth.admin_login'))
        
    if request.method=='GET':
        return render_template("updatewage.html")
        
    else:    
        
        name = request.form.get('name')
        salary = request.form.get('salary')
        
        if Job.query.filter_by(name=name).first():
            flash("Job already exists.")
            return redirect(url_for('main.create_job'))
            
        new_job = Job(name=name, salary=salary)
        
        db.session.add(new_job)
        db.session.commit()
        
        return redirect(url_for('main.admin_dashboard'))
        
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
    

    

