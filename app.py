from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException
from datetime import datetime
import os
from mailjet_rest import Client

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)  # Secure random secret key
app.config['DEBUG'] = True

# Error handler for detailed error logging
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    return jsonify(error=str(e)), 500

# Configuration for SQL Server with Windows Authentication
server = 'LAPTOP-77204R0A\\SQLEXPRESS'
database = 'FormVisitors'
driver = 'ODBC Driver 17 for SQL Server'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'mssql+pyodbc://@{server}/{database}?driver={driver}&trusted_connection=yes')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configuration for Mailjet
MAILJET_API_KEY = 'da6ba1e0f448a281debaf01c0476fe3a'
MAILJET_API_SECRET = '58f716e364714d179d4875163c9a3482'  # Replace this with your Mailjet secret key

mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')

# Manager Model
class Manager(db.Model):
    __tablename__ = 'Managers'
    id = db.Column('ManagerID', db.Integer, primary_key=True)
    name = db.Column('Name', db.String(50), nullable=False)
    email = db.Column('Email', db.String(120), nullable=False, unique=True)
    password = db.Column('Password', db.String(120), nullable=False)
    department = db.Column('Department', db.String(100), nullable=True)

# ManagerAccount Model
class ManagerAccount(db.Model):
    __tablename__ = 'ManagerAccounts'
    id = db.Column('ManagerAccountID', db.Integer, primary_key=True)
    manager_id = db.Column('ManagerID', db.Integer, db.ForeignKey('Managers.ManagerID'), nullable=False)
    username = db.Column('Username', db.String(50), nullable=False)
    password = db.Column('Password', db.String(120), nullable=False)

    manager = db.relationship('Manager', backref=db.backref('accounts', lazy=True))

# Visitor Model
class Visitor(db.Model):
    __tablename__ = 'Visitors'
    VisitorID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    PhoneNumber = db.Column(db.String(20), nullable=False)
    IDNumber = db.Column(db.String(20), nullable=False)
    Email = db.Column(db.String(120), nullable=False)
    VisitRequestID = db.Column(db.Integer, db.ForeignKey('VisitRequests.VisitRequestID'), nullable=False)

    visit_request = db.relationship('VisitRequest', back_populates='visitors')

# VisitRequest Model
class VisitRequest(db.Model):
    __tablename__ = 'VisitRequests'
    VisitRequestID = db.Column(db.Integer, primary_key=True)
    ManagerID = db.Column(db.Integer, db.ForeignKey('Managers.ManagerID'), nullable=False)
    GateID = db.Column(db.Integer, db.ForeignKey('Gates.GateID'), nullable=False)
    Status = db.Column(db.String(20), nullable=False, default='Pending')

    manager = db.relationship('Manager', backref=db.backref('visit_requests', lazy=True))
    gate = db.relationship('Gate', backref=db.backref('visit_requests', lazy=True))
    visitors = db.relationship('Visitor', back_populates='visit_request')
    visit_times = db.relationship('VisitTime', backref='visit_request', lazy=True)

# VisitTime Model
class VisitTime(db.Model):
    __tablename__ = 'VisitTimes'
    VisitTimeID = db.Column(db.Integer, primary_key=True)
    VisitRequestID = db.Column(db.Integer, db.ForeignKey('VisitRequests.VisitRequestID'), nullable=False)
    VisitDate = db.Column(db.Date, nullable=False)
    StartTime = db.Column(db.Time, nullable=False)
    EndTime = db.Column(db.Time, nullable=False)

# Gate Model
class Gate(db.Model):
    __tablename__ = 'Gates'
    id = db.Column('GateID', db.Integer, primary_key=True)
    gate_number = db.Column('GateNumber', db.String(50), nullable=False)
    location = db.Column('Location', db.String(100), nullable=False)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/form')
def form():
    managers = Manager.query.all()
    gates = Gate.query.all()
    return render_template('form.html', managers=managers, gates=gates)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        manager_account = ManagerAccount.query.filter_by(username=username, password=password).first()
        if manager_account:
            session['manager_id'] = manager_account.manager_id
            return redirect(url_for('manager_dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        username = request.form['username']
        department = request.form['department']

        # Check if all fields are provided
        if not all([name, email, password, confirm_password, username, department]):
            flash('All fields are required')
            return redirect(url_for('signup'))

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('signup'))

        # Ensure email is unique
        existing_manager = Manager.query.filter_by(email=email).first()
        if existing_manager:
            flash('Email already exists')
            return redirect(url_for('signup'))

        new_manager = Manager(name=name, email=email, password=password, department=department)
        db.session.add(new_manager)
        db.session.commit()

        manager_account = ManagerAccount(manager_id=new_manager.id, username=username, password=password)
        db.session.add(manager_account)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/manager_dashboard')
def manager_dashboard():
    if 'manager_id' not in session:
        return redirect(url_for('login'))
    visits = VisitRequest.query.filter_by(ManagerID=session['manager_id'], Status='Pending').all()
    return render_template('manager_dashboard.html', visits=visits)

@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        num_visitors = int(request.form['numVisitors'])
        manager_id = request.form['manager']
        gate_id = request.form['gateNumber']
        status = request.form['status']
        
        visit_request = VisitRequest(ManagerID=manager_id, GateID=gate_id, Status=status)
        db.session.add(visit_request)
        db.session.commit()

        visitors = []
        for i in range(num_visitors):
            first_name = request.form.get(f'firstName[{i}]')
            last_name = request.form.get(f'lastName[{i}]')
            phone_number = request.form.get(f'phoneNumber[{i}]')
            id_number = request.form.get(f'idNumber[{i}]')
            email = request.form.get(f'email[{i}]')
            id_attachment = request.files.get(f'idAttachment[{i}]')
            
            if not (first_name and last_name and phone_number and id_number and email and id_attachment):
                return "Missing required fields", 400

            file_path = os.path.join('uploads', id_attachment.filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            id_attachment.save(file_path)
            
            visitor = Visitor(
                FirstName=first_name,
                LastName=last_name,
                PhoneNumber=phone_number,
                IDNumber=id_number,
                Email=email,
                VisitRequestID=visit_request.VisitRequestID
            )
            db.session.add(visitor)
            visitors.append(visitor)

        visit_dates = request.form.getlist('visitDate[]')
        start_times = request.form.getlist('startTime[]')
        end_times = request.form.getlist('endTime[]')

        visit_times = []
        for visit_date, start_time, end_time in zip(visit_dates, start_times, end_times):
            visit_time = VisitTime(
                VisitRequestID=visit_request.VisitRequestID,
                VisitDate=visit_date,
                StartTime=start_time,
                EndTime=end_time
            )
            db.session.add(visit_time)
            visit_times.append(visit_time)

        db.session.commit()

        # Send email to the manager
        manager = Manager.query.get(manager_id)
        if manager:
            send_email(manager, visitors, visit_times, gate_id)

        return redirect(url_for('submission_success'))
    except Exception as e:
        return str(e), 400

@app.route('/update_visit_status/<int:visit_id>', methods=['POST'])
def update_visit_status(visit_id):
    if 'manager_id' not in session:
        return redirect(url_for('login'))
    visit = VisitRequest.query.get_or_404(visit_id)
    status = request.form['status']
    visit.Status = status
    db.session.commit()

    visitors = Visitor.query.filter_by(VisitRequestID=visit_id).all()
    for visitor in visitors:
        send_status_email(visitor, status)
        
    return redirect(url_for('manager_dashboard'))

@app.route('/api/managers_and_gates', methods=['GET'])
def get_managers_and_gates():
    managers = Manager.query.all()
    gates = Gate.query.all()
    data = {
        'managers': [{'id': manager.id, 'name': manager.name, 'department': manager.department} for manager in managers],
        'gates': [{'id': gate.id, 'gate_number': gate.gate_number} for gate in gates]
    }
    return jsonify(data)

def send_email(manager, visitors, visit_times, gate_id):
    body_html = """
    <html>
    <body>
        <h2>Visitor Details</h2>
        <table border="1" cellpadding="5" cellspacing="0">
    """
    for i, visitor in enumerate(visitors):
        body_html += f"""
            <tr>
                <th colspan="2">Visitor {i + 1}</th>
            </tr>
            <tr>
                <th>First Name</th><td>{visitor.FirstName}</td>
            </tr>
            <tr>
                <th>Last Name</th><td>{visitor.LastName}</td>
            </tr>
            <tr>
                <th>Phone Number</th><td>{visitor.PhoneNumber}</td>
            </tr>
            <tr>
                <th>ID/Iqama</th><td>{visitor.IDNumber}</td>
            </tr>
        """
    body_html += f"""
            <tr>
                <th>Number of Visitors</th><td>{len(visitors)}</td>
            </tr>
            <tr>
                <th>Gate Number</th><td>{gate_id}</td>
            </tr>
        </table>
        <h2>Visit Times</h2>
        <table border="1" cellpadding="5" cellspacing="0">
    """
    for visit_time in visit_times:
        body_html += f"""
            <tr>
                <th>Visit Date</th><td>{visit_time.VisitDate}</td>
                <th>From</th><td>{visit_time.StartTime}</td>
                <th>To</th><td>{visit_time.EndTime}</td>
            </tr>
        """
    body_html += """
        </table>
    </body>
    </html>
    """

    data = {
        'Messages': [
            {
                "From": {
                    "Email": "ihemaa.4@gmail.com",
                    "Name": "Cameron Al-rushaid"
                },
                "To": [
                    {
                        "Email": manager.email,
                        "Name": manager.name
                    }
                ],
                "Subject": "New Visitor Request",
                "HTMLPart": body_html
            }
        ]
    }

    result = mailjet.send.create(data=data)
    if result.status_code != 200:
        print(f"Error sending email to manager: {result.json()}")

def send_status_email(visitor, status):
    subject = "Update on Your Visit Request"
    body = f"Your visit request has been {status.lower()}."

    data = {
        'Messages': [
            {
                "From": {
                    "Email": "ihemaa.4@gmail.com",
                    "Name": "Cameron Al-rushaid"
                },
                "To": [
                    {
                        "Email": visitor.Email,
                        "Name": visitor.FirstName
                    }
                ],
                "Subject": subject,
                "TextPart": body
            }
        ]
    }

    result = mailjet.send.create(data=data)
    if result.status_code != 200:
        print(f"Error sending status email to visitor: {result.json()}")

@app.route('/submission_success')
def submission_success():
    return render_template('submit.html')

if __name__ == '__main__':
    app.run(debug=True)
