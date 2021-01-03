from flask import Blueprint
from flask_login import login_required, current_user
from . import db
from .models import User, Shift, Job
from sqlalchemy.sql import func
import csv

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return 'Index'

@main.route('/dashboard')
@login_required
def dashboard():
    return 'Dashboard'
    
@main.route('/clockin', methods = ['GET','POST'])
@login_required
def clockin():
    if current_user.admin == True:
        return redirect(url_for('main.admin_dashboard'))
        
    if request.method=='GET':
        return "Clock In"
        
    else:
        job_id = request.form.get('id')
        
        new_shift = Shift(job=job_id, start=func.now(), employee=current_user.id)
        
        db.session.add(new_shift)
        db.session.commit()
        
        return redirect(url_for('main.dashboard'))
        
@main.route('/clockout', methods = ['GET','POST'])
@login_required
def clockout():
    if current_user.admin == True:
        return redirect(url_for('main.admin_dashboard'))
        
    if request.method=='GET':
        return "Clock Out"
        
    else:
    
        id = request.form.get('id')
        
        shift = Shift.query.filter_by(job=job_id).filter_by(employee=current_user.id).all()[-1]
        
        setattr(shift, 'end', func.now())
        db.session.commit()
        
        return redirect(url_for('main.dashboard'))
    
@main.route('/admin-dashboard')
@login_required
def admin_dashboard():
    return 'Admin Dashboard'


@main.route('/create-job', methods = ['GET','POST'])
@login_required
def create_job():
    if current_user.admin == False:
        flash("Please login with an authorized account")
        return redirect(url_for('auth.admin_login'))
        
    if request.method=='GET':
        return "Create Job"
        
    else:    
        
        name = request.form.get('name')
        salary = request.form.get('salary')
        
        job = Job.query.filter_by(name=name).first()
            
        setattr(job, 'salary', salary)
        db.session.commit()
        
        return redirect(url_for('main.admin_dashboard'))
        
@main.route('/update-wage', methods = ['GET','POST'])
@login_required
def update_wage():
    if current_user.admin == False:
        flash("Please login with an authorized account")
        return redirect(url_for('auth.admin_login'))
        
    if request.method=='GET':
        return "Update Wage"
        
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
@login_required
def clear_shifts():
    if current_user.admin == False:
        flash("Please login with an authorized account")
        return redirect(url_for('auth.admin_login'))
    
    if request.method=='GET':
        return "Clear Shifts"
        
    else:
        Shift.query.delete()
        db.session.commit()
        return redirect(url_for('main.admin_dashboard'))
        
@main.route('/download', methods = ['GET', 'POST'])
@login_required
def download():
    if current_user.admin == False:
        flash("Please login with an authorized account")
        return redirect(url_for('auth.admin_login'))
    
    if request.method=='GET':
        return "Downloads"
        
    else:
        table = request.form.get('table')
        
        if(table == 'users'):
            model = User
        elif(table == 'jobs'):
            model = Job
        else:
            model = Shift
        
        records = session.query(Shift).all()
        
        outfile = open('tmp/' + table + '.csv', 'wb')
        outcsv = csv.writer(outfile)
        
        outcsv.writerow([column.name for column in model.__mapper__.columns])
        [outcsv.writerow([getattr(curr, column.name) for column in model.__mapper__.columns]) for curr in records]

        outfile.close()
        
        return send_from_directory('tmp/', table + '.csv', as_attachment=True)
    

    

