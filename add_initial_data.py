from app import app, db, Manager, Gate

# Create the database tables
with app.app_context():
    db.create_all()

    # Add initial managers
    managers = [
        Manager(Name='Ibrahim Al-Hamed', Email='ihemaa.4@gmail.com', Password='A123+123*/'),
        Manager(Name='Mashel Al-Hamed', Email='s2212001102@uhb.edu.sa', Password='password123')
    ]

    # Add initial gates
    gates = [
        Gate(GateNumber='1', Location='Main Entrance'),
        Gate(GateNumber='2', Location='Back Entrance')
    ]

    # Add the managers and gates to the session and commit
    db.session.bulk_save_objects(managers)
    db.session.bulk_save_objects(gates)
    db.session.commit()

    print("Initial data added.")
