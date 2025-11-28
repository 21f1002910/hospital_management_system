"""Admin routes - complete system management."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from sqlalchemy import or_, func

from app import db
from ..models import (db,
    User, UserRole, Patient, Doctor, Appointment, AppointmentStatus,
    Department, DoctorAvailability
)
from .decorators import role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# ============= DASHBOARD =============
@admin_bp.route('/dashboard', methods=['GET'])
@role_required(UserRole.ADMIN)
def dashboard():
    """Admin dashboard with comprehensive statistics."""
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    
    # Today's appointments
    today = date.today()
    todays_appointments = Appointment.query.filter_by(date=today).count()
    
    # Upcoming appointments (booked)
    upcoming_appointments = Appointment.query.filter_by(
        status=AppointmentStatus.BOOKED
    ).count()
    
    # Recent appointments (last 7 days)
    from datetime import timedelta
    week_ago = today - timedelta(days=7)
    recent_appointments = Appointment.query.filter(
        Appointment.date >= week_ago
    ).count()
    
    return jsonify({
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'todays_appointments': todays_appointments,
        'upcoming_appointments': upcoming_appointments,
        'recent_appointments': recent_appointments
    }), 200

# ============= PATIENTS MANAGEMENT =============
@admin_bp.route('/patients', methods=['GET'])
@role_required(UserRole.ADMIN)
def list_patients():
    """Get all patients with search capability."""
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Patient.query.join(User)
    
    # Search by name, contact, email, or ID
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Patient.name.ilike(search_pattern),
                Patient.contact.ilike(search_pattern),
                User.email.ilike(search_pattern),
                Patient.id == int(search) if search.isdigit() else False
            )
        )
    
    # Pagination
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'patients': [{
            'id': p.id,
            'name': p.name,
            'email': p.user.email,
            'age': p.age,
            'gender': p.gender,
            'contact': p.contact,
            'address': p.address,
            'created_at': p.created_at.isoformat()
        } for p in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200

@admin_bp.route('/patients/<int:patient_id>', methods=['GET'])
@role_required(UserRole.ADMIN)
def get_patient(patient_id):
    """Get specific patient with appointment history."""
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404
    
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()
    
    return jsonify({
        'id': patient.id,
        'name': patient.name,
        'email': patient.user.email,
        'age': patient.age,
        'gender': patient.gender,
        'contact': patient.contact,
        'address': patient.address,
        'blood_group': patient.blood_group,
        'allergies': patient.allergies,
        'appointments': [{
            'id': a.id,
            'doctor_name': a.doctor.name,
            'doctor_specialization': a.doctor.department.name,
            'date': a.date.isoformat(),
            'time': a.time.strftime('%H:%M'),
            'status': a.status.value,
            'notes': a.notes
        } for a in appointments]
    }), 200

# ============= DOCTORS MANAGEMENT =============
@admin_bp.route('/doctors', methods=['GET'])
@role_required(UserRole.ADMIN)
def list_doctors():
    """Get all doctors with search capability."""
    search = request.args.get('search', '').strip()
    specialization = request.args.get('specialization', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Doctor.query.join(Department).join(User)
    
    # Search by name or email
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Doctor.name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        )
    
    # Filter by specialization
    if specialization:
        query = query.filter(Department.name.ilike(f"%{specialization}%"))
    
    # Pagination
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'doctors': [{
            'id': d.id,
            'name': d.name,
            'email': d.user.email,
            'specialization': d.department.name,
            'bio': d.bio,
            'contact': d.contact,
            'created_at': d.created_at.isoformat()
        } for d in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200

@admin_bp.route('/doctors', methods=['POST'])
@role_required(UserRole.ADMIN)
def create_doctor():
    """Create a new doctor."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    specialization_id = data.get('specialization_id')
    bio = data.get('bio', '')
    contact = data.get('contact', '')
    
    if not email or not password or not name or not specialization_id:
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if email exists
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    # Check if department exists
    department = Department.query.get(specialization_id)
    if not department:
        return jsonify({'message': 'Department not found'}), 404
    
    try:
        # Create user account
        new_user = User(email=email, role=UserRole.DOCTOR)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()  # Get user.id
        
        # Create doctor profile
        new_doctor = Doctor(
            user_id=new_user.id,
            name=name,
            specialization_id=specialization_id,
            bio=bio,
            contact=contact
        )
        db.session.add(new_doctor)
        db.session.commit()
        
        return jsonify({
            'message': 'Doctor created successfully',
            'doctor_id': new_doctor.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create doctor: {str(e)}'}), 500

@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@role_required(UserRole.ADMIN)
def update_doctor(doctor_id):
    """Update doctor information."""
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404
    
    data = request.get_json()
    
    if data.get('name'):
        doctor.name = data['name']
    if data.get('specialization_id'):
        department = Department.query.get(data['specialization_id'])
        if not department:
            return jsonify({'message': 'Department not found'}), 404
        doctor.specialization_id = data['specialization_id']
    if 'bio' in data:
        doctor.bio = data['bio']
    if 'contact' in data:
        doctor.contact = data['contact']
    
    db.session.commit()
    return jsonify({'message': 'Doctor updated successfully'}), 200

@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@role_required(UserRole.ADMIN)
def delete_doctor(doctor_id):
    """Delete a doctor."""
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404
    
    try:
        user = User.query.get(doctor.user_id)
        db.session.delete(doctor)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Doctor deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to delete doctor: {str(e)}'}), 500

# ============= APPOINTMENTS MANAGEMENT =============
@admin_bp.route('/appointments', methods=['GET'])
@role_required(UserRole.ADMIN)
def list_appointments():
    """Get all appointments with filters."""
    status_filter = request.args.get('status', '').strip()
    date_filter = request.args.get('date', '').strip()
    doctor_id = request.args.get('doctor_id', type=int)
    patient_id = request.args.get('patient_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Appointment.query
    
    # Filter by status
    if status_filter:
        try:
            status_enum = AppointmentStatus[status_filter.upper()]
            query = query.filter_by(status=status_enum)
        except KeyError:
            return jsonify({'message': 'Invalid status'}), 400
    
    # Filter by date
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter_by(date=filter_date)
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Filter by doctor
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    
    # Filter by patient
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    
    # Order by date and time (upcoming first)
    query = query.order_by(Appointment.date.desc(), Appointment.time.desc())
    
    # Pagination
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'appointments': [{
            'id': a.id,
            'patient_id': a.patient_id,
            'patient_name': a.patient.name,
            'doctor_id': a.doctor_id,
            'doctor_name': a.doctor.name,
            'doctor_specialization': a.doctor.department.name,
            'date': a.date.isoformat(),
            'time': a.time.strftime('%H:%M'),
            'status': a.status.value,
            'notes': a.notes
        } for a in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200

@admin_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@role_required(UserRole.ADMIN)
def get_appointment(appointment_id):
    """Get specific appointment details."""
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404
    
    return jsonify({
        'id': appointment.id,
        'patient': {
            'id': appointment.patient_id,
            'name': appointment.patient.name,
            'email': appointment.patient.user.email,
            'age': appointment.patient.age,
            'gender': appointment.patient.gender,
            'contact': appointment.patient.contact
        },
        'doctor': {
            'id': appointment.doctor_id,
            'name': appointment.doctor.name,
            'email': appointment.doctor.user.email,
            'specialization': appointment.doctor.department.name
        },
        'date': appointment.date.isoformat(),
        'time': appointment.time.strftime('%H:%M'),
        'status': appointment.status.value,
        'notes': appointment.notes
    }), 200

@admin_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@role_required(UserRole.ADMIN)
def update_appointment(appointment_id):
    """Update appointment status or details."""
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404
    
    data = request.get_json()
    
    if data.get('status'):
        try:
            appointment.status = AppointmentStatus[data['status'].upper()]
        except KeyError:
            return jsonify({'message': 'Invalid status value'}), 400
    
    if data.get('notes'):
        appointment.notes = data['notes']
    
    if data.get('date'):
        try:
            appointment.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format'}), 400
    
    if data.get('time'):
        try:
            appointment.time = datetime.strptime(data['time'], '%H:%M').time()
        except ValueError:
            return jsonify({'message': 'Invalid time format'}), 400
    
    db.session.commit()
    return jsonify({'message': 'Appointment updated successfully'}), 200

# ============= DEPARTMENTS MANAGEMENT =============
@admin_bp.route('/departments', methods=['GET'])
@role_required(UserRole.ADMIN)
def list_departments():
    """Get all departments/specializations."""
    departments = Department.query.all()
    return jsonify({
        'departments': [{
            'id': d.id,
            'name': d.name,
            'description': d.description,
            'doctor_count': d.doctors.count()
        } for d in departments]
    }), 200

@admin_bp.route('/departments', methods=['POST'])
@role_required(UserRole.ADMIN)
def create_department():
    """Create a new department."""
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    
    if not name:
        return jsonify({'message': 'Department name is required'}), 400
    
    # Check if department exists
    if Department.query.filter_by(name=name).first():
        return jsonify({'message': 'Department already exists'}), 400
    
    new_department = Department(name=name, description=description)
    db.session.add(new_department)
    db.session.commit()
    
    return jsonify({
        'message': 'Department created successfully',
        'department_id': new_department.id
    }), 201

@admin_bp.route('/departments/<int:department_id>', methods=['PUT'])
@role_required(UserRole.ADMIN)
def update_department(department_id):
    """Update department information."""
    department = Department.query.get(department_id)
    if not department:
        return jsonify({'message': 'Department not found'}), 404
    
    data = request.get_json()
    
    if data.get('name'):
        # Check if new name conflicts with existing department
        existing = Department.query.filter_by(name=data['name']).first()
        if existing and existing.id != department_id:
            return jsonify({'message': 'Department name already exists'}), 400
        department.name = data['name']
    
    if 'description' in data:
        department.description = data['description']
    
    db.session.commit()
    return jsonify({'message': 'Department updated successfully'}), 200

@admin_bp.route('/departments/<int:department_id>', methods=['DELETE'])
@role_required(UserRole.ADMIN)
def delete_department(department_id):
    """Delete a department (only if no doctors assigned)."""
    department = Department.query.get(department_id)
    if not department:
        return jsonify({'message': 'Department not found'}), 404
    
    # Check if any doctors are assigned
    if department.doctors.count() > 0:
        return jsonify({
            'message': 'Cannot delete department with assigned doctors'
        }), 400
    
    db.session.delete(department)
    db.session.commit()
    
    return jsonify({'message': 'Department deleted successfully'}), 200