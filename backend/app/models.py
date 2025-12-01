# This file defines the database models for the Hospital Management System using SQLAlchemy ORM.
# It includes models for Users (with roles), Doctors, Patients, Appointments, Treatments, Departments,
# and Doctor Availability. Relationships are defined to handle associations like one-to-many and many-to-one.

from datetime import datetime
from enum import Enum
import json

from . import db
from werkzeug.security import generate_password_hash, check_password_hash


class UserRole(Enum):
    """Enumeration for user roles in the system."""
    ADMIN = 'Admin'
    DOCTOR = 'Doctor'
    PATIENT = 'Patient'


class User(db.Model):
    """Base User model for all roles (Admin, Doctor, Patient)."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)  # ✅ PRIMARY LOGIN
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    doctor = db.relationship('Doctor', backref='user', uselist=False, cascade='all, delete-orphan')
    patient = db.relationship('Patient', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify the provided password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f'<User {self.email} - {self.role.value}>'


class Department(db.Model):
    """Model for medical departments/specializations."""
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship: One department has many doctors
    doctors = db.relationship('Doctor', backref='department', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Department {self.name}>'


class Doctor(db.Model):
    """Model for Doctor profiles, linked to User."""
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    specialization_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    contact = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', lazy='dynamic', cascade='all, delete-orphan')
    availabilities = db.relationship('DoctorAvailability', backref='doctor', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'<Doctor {self.name}>'


class DoctorAvailability(db.Model):
    """Model for Doctor's availability slots."""
    __tablename__ = 'doctor_availabilities'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_slots = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_time_slots(self, slots: list[str]) -> None:
        """Set time slots as a JSON string."""
        self.time_slots = json.dumps(slots)

    def get_time_slots(self) -> list[str]:
        """Retrieve time slots as a list."""
        return json.loads(self.time_slots) if self.time_slots else []

    def __repr__(self) -> str:
        return f'<DoctorAvailability for Doctor {self.doctor_id} on {self.date}>'


class Patient(db.Model):
    """Model for Patient profiles, linked to User."""
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    contact = db.Column(db.String(50), nullable=False)  # ✅ Made required
    address = db.Column(db.Text, nullable=True)
    blood_group = db.Column(db.String(5), nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'<Patient {self.name}>'


class AppointmentStatus(Enum):
    """Enumeration for appointment statuses."""
    BOOKED = 'Booked'
    COMPLETED = 'Completed'
    CANCELLED = 'Cancelled'
    NO_SHOW = 'No Show'


class Appointment(db.Model):
    """Model for Appointments between Doctors and Patients."""
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum(AppointmentStatus), default=AppointmentStatus.BOOKED, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    reason = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    treatment = db.relationship('Treatment', backref='appointment', uselist=False, cascade='all, delete-orphan')

    # Index to prevent double booking
    __table_args__ = (
        db.Index('idx_doctor_date_time', 'doctor_id', 'date', 'time'),
    )

    def __repr__(self) -> str:
        return f'<Appointment {self.id} - {self.status.value}>'


class Treatment(db.Model):
    """Model for Treatments recorded during Appointments."""
    __tablename__ = 'treatments'

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), unique=True, nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    next_visit_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f'<Treatment for Appointment {self.appointment_id}>'


# Helper functions

def create_admin_user(email: str, password: str) -> None:
    """Create the Admin user if it doesn't exist."""
    existing_admin = User.query.filter_by(role=UserRole.ADMIN).first()
    if not existing_admin:
        admin = User(email=email, role=UserRole.ADMIN)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()


def seed_departments() -> None:
    """Seed initial departments if none exist."""
    if Department.query.count() == 0:
        departments = [
            Department(name='Cardiology', description='Heart and cardiovascular system'),
            Department(name='Neurology', description='Brain and nervous system'),
            Department(name='Orthopedics', description='Bones, joints, and muscles'),
            Department(name='Pediatrics', description='Children healthcare'),
            Department(name='Dermatology', description='Skin, hair, and nails'),
            Department(name='General Medicine', description='General health checkups'),
        ]
        db.session.add_all(departments)
        db.session.commit()


def init_db(app) -> None:
    """Initialize the database: create tables and seed data."""
    with app.app_context():
        db.create_all()
        create_admin_user('admin@hospital.com', 'admin123')
        seed_departments()