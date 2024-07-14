from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException
from datetime import datetime
import os
from fpdf import FPDF

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'your_secret_key'
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

app.config['SQLALCHEMY_DATABASE_URI'] = f'mssql+pyodbc://@{server}/{database}?driver={driver}&trusted_connection=yes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ihemaa.4@gmail.com'
app.config['MAIL_PASSWORD'] = 'ohki nqpm edsz crjh'

mail = Mail(app)

# Manager Model
class Manager(db.Model):
    __tablename__ = 'Managers'
    id = db.Column('ManagerID', db.Integer, primary_key=True)
    name = db.Column('Name', db.String(50), nullable=False)
    email = db.Column('Email', db.String(120), nullable=False)
    password = db.Column('Password', db.String(120), nullable=False)

# Gate Model
class Gate(db.Model):
    __tablename__ = 'Gates'
    id = db.Column('GateID', db.Integer, primary_key=True)
    gate_number = db.Column('GateNumber', db.String(50), nullable=False)
    location = db.Column('Location', db.String(100), nullable=False)

# Visitor Model
class Visitor(db.Model):
    __tablename__ = 'Visitors'
    VisitorID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    PhoneNumber = db.Column(db.String(20), nullable=False)
    IDNumber = db.Column(db.String(20), nullable=False)
    NumberOfVisitors = db.Column(db.Integer, nullable=False)
    DateTime = db.Column(db.DateTime, nullable=False)
    ManagerID = db.Column(db.Integer, db.ForeignKey('Managers.ManagerID'), nullable=False)
    GateNumber = db.Column(db.Integer, db.ForeignKey('Gates.GateID'), nullable=False)
    Status = db.Column(db.String(20), nullable=False, default='Pending')
    Email = db.Column(db.String(120), nullable=False)

# Visit Model
class Visit(db.Model):
    __tablename__ = 'Visits'
    VisitID = db.Column(db.Integer, primary_key=True)
    VisitorID = db.Column(db.Integer, db.ForeignKey('Visitors.VisitorID'), nullable=False)
    ManagerID = db.Column(db.Integer, db.ForeignKey('Managers.ManagerID'), nullable=False)
    VisitDate = db.Column(db.DateTime, nullable=False)
    GateID = db.Column(db.Integer, db.ForeignKey('Gates.GateID'), nullable=False)
    ApprovalStatus = db.Column(db.String(50), nullable=False, default='Pending')

    visitor = db.relationship('Visitor', backref=db.backref('visits', lazy=True))
    manager = db.relationship('Manager', backref=db.backref('visits', lazy=True))
    gate = db.relationship('Gate', backref=db.backref('visits', lazy=True))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form')
def form():
    managers = Manager.query.all()
    gates = Gate.query.all()
    return render_template('form.html', managers=managers, gates=gates)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        manager = Manager.query.filter_by(email=email, password=password).first()
        if manager:
            session['manager_id'] = manager.id
            return redirect(url_for('manager_dashboard'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        new_manager = Manager(name=name, email=email, password=password)
        db.session.add(new_manager)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/manager_dashboard')
def manager_dashboard():
    if 'manager_id' not in session:
        return redirect(url_for('login'))
    visits = Visit.query.filter_by(ApprovalStatus='Pending').all()
    return render_template('manager_dashboard.html', visits=visits)

@app.route('/submit', methods=['POST'])
def submit_form():
    num_visitors = int(request.form['numVisitors'])
    first_names = request.form.getlist('firstName[]')
    last_names = request.form.getlist('lastName[]')
    phone_numbers = request.form.getlist('phoneNumber[]')
    id_numbers = request.form.getlist('idNumber[]')
    emails = request.form.getlist('email[]')
    date_time_str = request.form['dateTime']
    date_time = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M')
    gate_number = request.form['gateNumber']
    manager_id = request.form['manager']
    
    files = request.files.getlist('idAttachment[]')
    file_paths = []

    for file in files:
        file_path = os.path.join('uploads', file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        file_paths.append(file_path)

    manager = Manager.query.get(manager_id)
    
    if manager is None:
        return "Manager not found", 400

    manager_email = manager.email

    # Create PDF and email body for all visitors
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Visitor Details", ln=True, align="C")

    body_html = """
    <html>
    <body>
        <h2>Visitor Details</h2>
        <table border="1" cellpadding="5" cellspacing="0">
    """

    for i in range(num_visitors):
        new_visitor = Visitor(
            FirstName=first_names[i],
            LastName=last_names[i],
            PhoneNumber=phone_numbers[i],
            IDNumber=id_numbers[i],
            NumberOfVisitors=num_visitors,
            DateTime=date_time,
            ManagerID=manager_id,
            GateNumber=gate_number,
            Status='Pending',
            Email=emails[i]
        )
        db.session.add(new_visitor)
        db.session.commit()
        
        visitor_id = new_visitor.VisitorID

        new_visit = Visit(
            VisitorID=visitor_id,
            ManagerID=manager_id,
            VisitDate=date_time,
            GateID=gate_number,
            ApprovalStatus='Pending'
        )
        db.session.add(new_visit)
        db.session.commit()

        with open(file_paths[i], 'rb') as f:
            file_data = f.read()

        # Add visitor details to PDF
        pdf.cell(200, 10, txt=f"Visitor {i + 1}", ln=True, align="C")
        pdf.cell(200, 10, txt=f"First Name: {first_names[i]}", ln=True)
        pdf.cell(200, 10, txt=f"Last Name: {last_names[i]}", ln=True)
        pdf.cell(200, 10, txt=f"Phone Number: {phone_numbers[i]}", ln=True)
        pdf.cell(200, 10, txt=f"ID/Iqama: {id_numbers[i]}", ln=True)
        pdf.cell(200, 10, txt=f"Number of Visitors: {num_visitors}", ln=True)
        pdf.cell(200, 10, txt=f"Date/Time: {date_time.strftime('%Y-%m-%d %I:%M %p')}", ln=True)
        pdf.cell(200, 10, txt=f"Gate Number: {gate_number}", ln=True)
        # Add visitor details to email body
        body_html += f"""
            <tr>
                <th colspan="2">Visitor {i + 1}</th>
            </tr>
            <tr>
                <th>First Name</th><td>{first_names[i]}</td>
            </tr>
            <tr>
                <th>Last Name</th><td>{last_names[i]}</td>
            </tr>
            <tr>
                <th>Phone Number</th><td>{phone_numbers[i]}</td>
            </tr>
            <tr>
                <th>ID/Iqama</th><td>{id_numbers[i]}</td>
            </tr>
        """

    body_html += f"""
            <tr>
                <th>Number of Visitors</th><td>{num_visitors}</td>
            </tr>
            <tr>
                <th>Date/Time</th><td>{date_time.strftime('%Y-%m-%d %I:%M %p')}</td>
            </tr>
            <tr>
                <th>Gate Number</th><td>{gate_number}</td>
            </tr>
        </table>
    </body>
    </html>
    """

    pdf_output = f"uploads/Visitor_Details.pdf"
    pdf.output(pdf_output)

    msg = Message(subject="New Visitor Request", sender='ihemaa.4@gmail.com', recipients=[manager_email])
    msg.body = "Please find the visitor details attached."
    msg.html = body_html

    for i, file_path in enumerate(file_paths):
        with open(file_path, 'rb') as f:
            file_data = f.read()
            msg.attach(files[i].filename, files[i].content_type, file_data)

    msg.attach("Visitor_Details.pdf", 'application/pdf', open(pdf_output, 'rb').read())

    try:
        mail.send(msg)
        return render_template('submit.html')
    except Exception as e:
        return str(e)

@app.route('/update_visit_status/<int:visit_id>', methods=['POST'])
def update_visit_status(visit_id):
    if 'manager_id' not in session:
        return redirect(url_for('login'))
    visit = Visit.query.get_or_404(visit_id)
    status = request.form['status']
    visit.ApprovalStatus = status
    db.session.commit()

    visitor = Visitor.query.get(visit.VisitorID)
    subject = "Update on Your Visit Request"
    body = f"Your visit request has been {status.lower()}."

    msg = Message(subject, sender='ihemaa.4@gmail.com', recipients=[visitor.Email])
    msg.body = body

    try:
        mail.send(msg)
    except Exception as e:
        return str(e)
        
    return redirect(url_for('manager_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
