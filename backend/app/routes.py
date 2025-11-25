# This file defines the API routes for authentication and basic protected endpoints.
# It uses Flask-JWT-Extended for JWT-based authentication and role-based access control.

from functools import wraps  # Added to preserve function names in decorators

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash

from .models import db, User, UserRole, Patient, Doctor, Appointment, AppointmentStatus  # Added missing imports for dashboards

api_bp = Blueprint('api', __name__)

@api_bp.route('/', methods=['GET'])
def home():
    """Root endpoint message."""
    return jsonify({'message': 'Hospital Management System API is running! Visit /api endpoints for functionality.'}), 200

def role_required(*roles):
    """Decorator to check if the current user has one of the required roles."""
    def wrapper(fn):
        @wraps(fn)  # Preserve the original function name to avoid endpoint conflicts
        @jwt_required()
        def decorator(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or user.role not in roles:
                return jsonify({'message': 'Access forbidden: insufficient permissions'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

@api_bp.route('/register', methods=['POST'])
def register():
    """Patient registration endpoint."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    age = data.get('age')
    gender = data.get('gender')
    contact = data.get('contact')
    address = data.get('address')

    if not username or not password or not name or not age or not gender:
        return jsonify({'message': 'Missing required fields'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    new_user = User(username=username, role=UserRole.PATIENT)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    new_patient = Patient(
        user_id=new_user.id,
        name=name,
        age=age,
        gender=gender,
        contact=contact,
        address=address
    )
    db.session.add(new_patient)
    db.session.commit()

    return jsonify({'message': 'Patient registered successfully'}), 201

@api_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint for all roles."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Create JWT token with user ID as identity
    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token, 'role': user.role.value}), 200

# Example protected dashboards (data endpoints) - Frontend will fetch these and render accordingly
@api_bp.route('/admin/dashboard', methods=['GET'])
@role_required(UserRole.ADMIN)
def admin_dashboard():
    """Admin dashboard data."""
    # Placeholder: Fetch totals
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    return jsonify({
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments
    }), 200

@api_bp.route('/doctor/dashboard', methods=['GET'])
@role_required(UserRole.DOCTOR)
def doctor_dashboard():
    """Doctor dashboard data."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    doctor = user.doctor
    # Placeholder: Fetch upcoming appointments
    upcoming = Appointment.query.filter_by(doctor_id=doctor.id, status=AppointmentStatus.BOOKED).count()
    return jsonify({'upcoming_appointments': upcoming}), 200

@api_bp.route('/patient/dashboard', methods=['GET'])
@role_required(UserRole.PATIENT)
def patient_dashboard():
    """Patient dashboard data."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    patient = user.patient
    # Placeholder: Fetch upcoming appointments
    upcoming = Appointment.query.filter_by(patient_id=patient.id, status=AppointmentStatus.BOOKED).count()
    return jsonify({'upcoming_appointments': upcoming}), 200