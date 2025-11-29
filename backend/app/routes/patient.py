"""Patient routes - appointments, medical records, profile management."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta

from ..models import db, User, UserRole, Patient, Doctor, Department, Appointment, AppointmentStatus, Treatment, DoctorAvailability
from .decorators import role_required

patient_bp = Blueprint('patient', __name__, url_prefix='/api/patient')


# ============= DASHBOARD =============
@patient_bp.route('/dashboard', methods=['GET'])
@role_required(UserRole.PATIENT)
def dashboard():
    """Patient dashboard with statistics."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    patient = user.patient
    
    today = date.today()
    
    # Upcoming appointments
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.date >= today,
        Appointment.status == AppointmentStatus.BOOKED
    ).count()
    
    # Past appointments
    past_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status == AppointmentStatus.COMPLETED
    ).count()
    
    # Next appointment
    next_appointment = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.date >= today,
        Appointment.status == AppointmentStatus.BOOKED
    ).order_by(Appointment.date.asc(), Appointment.time.asc()).first()
    
    next_apt = None
    if next_appointment:
        next_apt = {
            'id': next_appointment.id,
            'doctor_name': next_appointment.doctor.name,
            'specialization': next_appointment.doctor.department.name,
            'date': next_appointment.date.isoformat(),
            'time': next_appointment.time.strftime('%H:%M')
        }
    
    return jsonify({
        'patient_name': patient.name,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'next_appointment': next_apt
    }), 200


# ============= PROFILE =============
@patient_bp.route('/profile', methods=['GET'])
@role_required(UserRole.PATIENT)
def get_profile():
    """Get patient profile."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    patient = user.patient
    
    return jsonify({
        'id': patient.id,
        'name': patient.name,
        'email': user.email,
        'age': patient.age,
        'gender': patient.gender,
        'contact': patient.contact,
        'address': patient.address,
        'blood_group': patient.blood_group,
        'allergies': patient.allergies
    }), 200


@patient_bp.route('/profile', methods=['PUT'])
@role_required(UserRole.PATIENT)
def update_profile():
    """Update patient profile."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    patient = user.patient
    
    data = request.get_json()
    
    if data.get('name'):
        patient.name = data['name']
    if data.get('age'):
        patient.age = data['age']
    if data.get('gender'):
        patient.gender = data['gender']
    if data.get('contact'):
        patient.contact = data['contact']
    if 'address' in data:
        patient.address = data['address']
    if 'blood_group' in data:
        patient.blood_group = data['blood_group']
    if 'allergies' in data:
        patient.allergies = data['allergies']
    
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200


# ============= DOCTORS =============
@patient_bp.route('/doctors', methods=['GET'])
@role_required(UserRole.PATIENT)
def list_doctors():
    """Get list of doctors with search and filter."""
    search = request.args.get('search', '').strip()
    specialization = request.args.get('specialization', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    query = Doctor.query.join(Department)
    
    # Search by name
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(Doctor.name.ilike(search_pattern))
    
    # Filter by specialization
    if specialization:
        query = query.filter(Department.name.ilike(f"%{specialization}%"))
    
    # Pagination
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'doctors': [{
            'id': d.id,
            'name': d.name,
            'specialization': d.department.name,
            'bio': d.bio,
            'contact': d.contact
        } for d in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200


@patient_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
@role_required(UserRole.PATIENT)
def get_doctor(doctor_id):
    """Get specific doctor details with availability."""
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404
    
    # Get availability for next 7 days
    today = date.today()
    week_later = today + timedelta(days=7)
    
    availabilities = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.date.between(today, week_later)
    ).all()
    
    return jsonify({
        'id': doctor.id,
        'name': doctor.name,
        'specialization': doctor.department.name,
        'bio': doctor.bio,
        'contact': doctor.contact,
        'schedule': doctor.schedule,
        'availability': [{
            'date': av.date.isoformat(),
            'time_slots': av.get_time_slots()
        } for av in availabilities]
    }), 200


@patient_bp.route('/departments', methods=['GET'])
@role_required(UserRole.PATIENT)
def list_departments():
    """Get list of departments for filtering."""
    departments = Department.query.all()
    return jsonify({
        'departments': [{
            'id': d.id,
            'name': d.name,
            'description': d.description
        } for d in departments]
    }), 200


# ============= APPOINTMENTS =============
@patient_bp.route('/appointments', methods=['GET'])
@role_required(UserRole.PATIENT)
def get_appointments():
    """Get patient's appointments with filters."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    patient = user.patient
    
    # Filters
    status_filter = request.args.get('status', '').strip()
    view = request.args.get('view', 'upcoming')  # upcoming, past, all
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Appointment.query.filter_by(patient_id=patient.id)
    
    # View filters
    today = date.today()
    if view == 'upcoming':
        query = query.filter(
            Appointment.date >= today,
            Appointment.status == AppointmentStatus.BOOKED
        )
    elif view == 'past':
        query = query.filter(
            or_(
                Appointment.date < today,
                Appointment.status.in_([AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED])
            )
        )
    
    # Status filter
    if status_filter:
        try:
            status_enum = AppointmentStatus[status_filter.upper()]
            query = query.filter_by(status=status_enum)
        except KeyError:
            return jsonify({'message': 'Invalid status'}), 400
    
    # Order by date
    if view == 'past':
        query = query.order_by(Appointment.date.desc(), Appointment.time.desc())
    else:
        query = query.order_by(Appointment.date.asc(), Appointment.time.asc())
    
    # Pagination
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'appointments': [{
            'id': a.id,
            'doctor_id': a.doctor_id,
            'doctor_name': a.doctor.name,
            'doctor_specialization': a.doctor.department.name,
            'date': a.date.isoformat(),
            'time': a.time.strftime('%H:%M'),
            'status': a.status.value,
            'reason': a.reason,
            'notes': a.notes,
            'has_treatment': a.treatment is not None
        } for a in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200


@patient_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@role_required(UserRole.PATIENT)
def get_appointment(appointment_id):
    """Get specific appointment details."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    patient = user.patient
    
    appointment = Appointment.query.filter_by(
        id=appointment_id,
        patient_id=patient.id
    ).first()
    
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404
    
    result = {
        'id': appointment.id,
        'doctor': {
            'id': appointment.doctor.id,
            'name': appointment.doctor.name,
            'specialization': appointment.doctor.department.name,
            'contact': appointment.doctor.contact
        },
        'date': appointment.date.isoformat(),
        'time': appointment.time.strftime('%H:%M'),
        'status': appointment.status.value,
        'reason': appointment.reason,
        'notes': appointment.notes,
        'treatment': None
    }
    
    if appointment.treatment:
        result['treatment'] = {
            'diagnosis': appointment.treatment.diagnosis,
            'prescription': appointment.treatment.prescription,
            'notes': appointment.treatment.notes,
            'next_visit_date': appointment.treatment.next_visit_date.isoformat() if appointment.treatment.next_visit_date else None
        }
    
    return jsonify(result), 200


@patient_bp.route('/appointments', methods=['POST'])
@role_required(UserRole.PATIENT)
def book_appointment():
    """Book a new appointment."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    patient = user.patient
    
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    appointment_date = data.get('date')
    appointment_time = data.get('time')
    reason = data.get('reason', '')
    
    if not doctor_id or not appointment_date or not appointment_time:
        return jsonify({'message': 'Doctor, date, and time are required'}), 400
    
    # Check if doctor exists
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404
    
    # Parse date and time
    try:
        apt_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        apt_time = datetime.strptime(appointment_time, '%H:%M').time()
    except ValueError:
        return jsonify({'message': 'Invalid date or time format'}), 400
    
    # Check if date is in the future
    if apt_date < date.today():
        return jsonify({'message': 'Cannot book appointments in the past'}), 400
    
    # Check if time slot is available
    availability = DoctorAvailability.query.filter_by(
        doctor_id=doctor_id,
        date=apt_date
    ).first()
    
    if not availability or appointment_time not in availability.get_time_slots():
        return jsonify({'message': 'Selected time slot is not available'}), 400
    
    # Check if slot is already booked
    existing = Appointment.query.filter_by(
        doctor_id=doctor_id,
        date=apt_date,
        time=apt_time,
        status=AppointmentStatus.BOOKED
    ).first()
    
    if existing:
        return jsonify({'message': 'This time slot is already booked'}), 400
    
    # Create appointment
    new_appointment = Appointment(
        doctor_id=doctor_id,
        patient_id=patient.id,
        date=apt_date,
        time=apt_time,
        status=AppointmentStatus.BOOKED,
        reason=reason
    )
    db.session.add(new_appointment)
    db.session.commit()
    
    return jsonify({
        'message': 'Appointment booked successfully',
        'appointment_id': new_appointment.id
    }), 201


@patient_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@role_required(UserRole.PATIENT)
def reschedule_appointment(appointment_id):
    """Reschedule an appointment."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    patient = user.patient
    
    appointment = Appointment.query.filter_by(
        id=appointment_id,
        patient_id=patient.id
    ).first()
    
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404
    
    if appointment.status != AppointmentStatus.BOOKED:
        return jsonify({'message': 'Can only reschedule booked appointments'}), 400
    
    data = request.get_json()
    new_date = data.get('date')
    new_time = data.get('time')
    
    if not new_date or not new_time:
        return jsonify({'message': 'Date and time are required'}), 400
    
    # Parse new date and time
    try:
        apt_date = datetime.strptime(new_date, '%Y-%m-%d').date()
        apt_time = datetime.strptime(new_time, '%H:%M').time()
    except ValueError:
        return jsonify({'message': 'Invalid date or time format'}), 400
    
    # Check if date is in the future
    if apt_date < date.today():
        return jsonify({'message': 'Cannot reschedule to past dates'}), 400
    
    # Check availability
    availability = DoctorAvailability.query.filter_by(
        doctor_id=appointment.doctor_id,
        date=apt_date
    ).first()
    
    if not availability or new_time not in availability.get_time_slots():
        return jsonify({'message': 'Selected time slot is not available'}), 400
    
    # Check if slot is already booked
    existing = Appointment.query.filter_by(
        doctor_id=appointment.doctor_id,
        date=apt_date,
        time=apt_time,
        status=AppointmentStatus.BOOKED
    ).first()
    
    if existing and existing.id != appointment_id:
        return jsonify({'message': 'This time slot is already booked'}), 400
    
    # Update appointment
    appointment.date = apt_date
    appointment.time = apt_time
    db.session.commit()
    
    return jsonify({'message': 'Appointment rescheduled successfully'}), 200


@patient_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@role_required(UserRole.PATIENT)
def cancel_appointment(appointment_id):
    """Cancel an appointment."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    patient = user.patient
    
    appointment = Appointment.query.filter_by(
        id=appointment_id,
        patient_id=patient.id
    ).first()
    
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404
    
    if appointment.status != AppointmentStatus.BOOKED:
        return jsonify({'message': 'Can only cancel booked appointments'}), 400
    
    # Update status to cancelled
    appointment.status = AppointmentStatus.CANCELLED
    db.session.commit()
    
    return jsonify({'message': 'Appointment cancelled successfully'}), 200


# ============= MEDICAL HISTORY =============
@patient_bp.route('/medical-history', methods=['GET'])
@role_required(UserRole.PATIENT)
def get_medical_history():
    """Get complete medical history."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    patient = user.patient
    
    # Get all completed appointments with treatments
    appointments = Appointment.query.filter_by(
        patient_id=patient.id,
        status=AppointmentStatus.COMPLETED
    ).order_by(Appointment.date.desc()).all()
    
    return jsonify({
        'history': [{
            'id': a.id,
            'doctor_name': a.doctor.name,
            'specialization': a.doctor.department.name,
            'date': a.date.isoformat(),
            'time': a.time.strftime('%H:%M'),
            'reason': a.reason,
            'treatment': {
                'diagnosis': a.treatment.diagnosis,
                'prescription': a.treatment.prescription,
                'notes': a.treatment.notes,
                'next_visit_date': a.treatment.next_visit_date.isoformat() if a.treatment.next_visit_date else None
            } if a.treatment else None
        } for a in appointments]
    }), 200