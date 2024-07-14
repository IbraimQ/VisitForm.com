from app import db

class Manager(db.Model):
    __tablename__ = 'Managers'
    id = db.Column('ManagerID', db.Integer, primary_key=True)
    name = db.Column('Name', db.String(50), nullable=False)
    email = db.Column('Email', db.String(120), nullable=False)
    password = db.Column('Password', db.String(120), nullable=False)

class Gate(db.Model):
    __tablename__ = 'Gates'
    id = db.Column('GateID', db.Integer, primary_key=True)
    gate_number = db.Column('GateNumber', db.String(50), nullable=False)
    location = db.Column('Location', db.String(100), nullable=False)

class Visitor(db.Model):
    __tablename__ = 'Visitors'
    id = db.Column('VisitorID', db.Integer, primary_key=True)
    first_name = db.Column('FirstName', db.String(50), nullable=False)
    last_name = db.Column('LastName', db.String(50), nullable=False)
    phone_number = db.Column('PhoneNumber', db.String(20), nullable=False)
    id_number = db.Column('IDNumber', db.String(50), nullable=False)
    number_of_visitors = db.Column('NumberOfVisitors', db.Integer, nullable=False)
    date_time = db.Column('DateTime', db.DateTime, nullable=False)
    manager_id = db.Column('ManagerID', db.Integer, db.ForeignKey('Managers.ManagerID'), nullable=False)
    gate_number = db.Column('GateNumber', db.Integer, db.ForeignKey('Gates.GateID'), nullable=False)
    status = db.Column('Status', db.String(50), nullable=False, default='Pending')

class Visit(db.Model):
    __tablename__ = 'Visits'
    id = db.Column('VisitID', db.Integer, primary_key=True)
    visitor_id = db.Column('VisitorID', db.Integer, db.ForeignKey('Visitors.VisitorID'), nullable=False)
    manager_id = db.Column('ManagerID', db.Integer, db.ForeignKey('Managers.ManagerID'), nullable=False)
    gate_id = db.Column('GateID', db.Integer, db.ForeignKey('Gates.GateID'), nullable=False)
    visit_date = db.Column('VisitDate', db.DateTime, nullable=False)
    approval_status = db.Column('ApprovalStatus', db.String(50), nullable=False, default='Pending')
