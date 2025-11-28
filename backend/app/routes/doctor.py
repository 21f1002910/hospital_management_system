"""Doctor routes - appointments, patient records, schedule management."""

from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..models import db, User, UserRole, Doctor, Patient, Appointment, AppointmentStatus, Treatment, DoctorAvailability
from .decorators import role_required

doctor_bp = Blueprint('doctor', __name__, url_prefix='/api/doctor')

# ============= DASHBOARD =============
@doctor_bp.route('/dashboard', methods=['GET'])
@role_required(UserRole.DOCTOR)
def dashboard():
    """Doctor dashboard with statistics and upcoming appointments."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    doctor = user.doctor
    
    today = date.today()
    week_later = today + timedelta(days=7)
    
    # Today's appointments
    todays_appointments = Appointment.query.filter_by(
        doctor_id=doctor.id,
        date=today,
        status=AppointmentStatus.BOOKED
    ).count()
    
    # This week's appointments
    week_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.date.between(today, week_later),
        Appointment.status == AppointmentStatus.BOOKED
    ).count()
    
    # Total completed
    completed_appointments = Appointment.query.filter_by(
        doctor_id=doctor.id,
        status=AppointmentStatus.COMPLETED
    ).count()
    
    # Total patients
    total_patients = db.session.query(Patient.id).join(Appointment).filter(
        Appointment.doctor_id == doctor.id
    ).distinct().count()
    
    return jsonify({
        'doctor_name': doctor.name,
        'todays_appointments': todays_appointments,
        'week_appointments': week_appointments,
        'completed_appointments': completed_appointments,
        'total_patients': total_patients
    }), 200


# ============= APPOINTMENTS =============
@doctor_bp.route('/appointments', methods=['GET'])
@role_required(UserRole.DOCTOR)
def get_appointments():
    """Get doctor's appointments with filters."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    doctor = user.doctor
    
    # Filters
    status_filter = request.args.get('status', '').strip()
    date_filter = request.args.get('date', '').strip()
    view = request.args.get('view', 'upcoming')  # upcoming, today, week, all
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Appointment.query.filter_by(doctor_id=doctor.id)
    
    # View filters
    today = date.today()
    if view == 'today':
        query = query.filter_by(date=today)
    elif view == 'week':
        week_later = today + timedelta(days=7)
        query = query.filter(Appointment.date.between(today, week_later))
    elif view == 'upcoming':
        query = query.filter(
            Appointment.date >= today,
            Appointment.status == AppointmentStatus.BOOKED
        )
    
    # Status filter
    if status_filter:
        try:
            status_enum = AppointmentStatus[status_filter.upper()]
            query = query.filter_by(status=status_enum)
        except KeyError:
            return jsonify({'message': 'Invalid status'}), 400
    
    # Date filter
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter_by(date=filter_date)
        except ValueError:
            return jsonify({'message': 'Invalid date format'}), 400
    
    # Order by date and time
    query = query.order_by(Appointment.date.asc(), Appointment.time.asc())
    
    # Pagination
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'appointments': [{
            'id': a.id,
            'patient_id': a.patient_id,
            'patient_name': a.patient.name,
            'patient_age': a.patient.age,
            'patient_gender': a.patient.gender,
            'patient_contact': a.patient.contact,
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


@doctor_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@role_required(UserRole.DOCTOR)
def get_appointment(appointment_id):
    """Get specific appointment details."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    doctor = user.doctor
    
    appointment = Appointment.query.filter_by(
        id=appointment_id,
        doctor_id=doctor.id
    ).first()
    
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404
    
    result = {
        'id': appointment.id,
        'patient': {
            'id': appointment.patient.id,
            'name': appointment.patient.name,
            'age': appointment.patient.age,
            'gender': appointment.patient.gender,
            'contact': appointment.patient.contact,
            'address': appointment.patient.address,
            'blood_group': appointment.patient.blood_group,
            'allergies': appointment.patient.allergies
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
            'id': appointment.treatment.id,
            'diagnosis': appointment.treatment.diagnosis,
            'prescription': appointment.treatment.prescription,
            'notes': appointment.treatment.notes,
            'next_visit_date': appointment.treatment.next_visit_date.isoformat() if appointment.treatment.next_visit_date else None
        }
    
    return jsonify(result), 200


@doctor_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@role_required(UserRole.DOCTOR)
def update_appointment(appointment_id):
    """Update appointment status or notes."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    doctor = user.doctor
    
    appointment = Appointment.query.filter_by(
        id=appointment_id,
        doctor_id=doctor.id
    ).first()
    
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404
    
    data = request.get_json()
    
    if data.get('status'):
        try:
            appointment.status = AppointmentStatus[data['status'].upper()]
        except KeyError:
            return jsonify({'message': 'Invalid status value'}), 400
    
    if 'notes' in data:
        appointment.notes = data['notes']
    
    db.session.commit()
    return jsonify({'message': 'Appointment updated successfully'}), 200


# ============= TREATMENTS =============
@doctor_bp.route('/appointments/<int:appointment_id>/treatment', methods=['POST'])
@role_required(UserRole.DOCTOR)
def add_treatment(appointment_id):
    """Add treatment/diagnosis to appointment."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    doctor = user.doctor
    
    appointment = Appointment.query.filter_by(
        id=appointment_id,
        doctor_id=doctor.id
    ).first()
    
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404
    
    if appointment.treatment:
        return jsonify({'message': 'Treatment already exists for this appointment'}), 400
    
    data = request.get_json()
    diagnosis = data.get('diagnosis')
    prescription = data.get('prescription', '')
    notes = data.get('notes', '')
    next_visit_date = data.get('next_visit_date')
    
    if not diagnosis:
        return jsonify({'message': 'Diagnosis is required'}), 400
    
    # Parse next visit date
    next_visit = None
    if next_visit_date:
        try:
            next_visit = datetime.strptime(next_visit_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format'}), 400
    
    new_treatment = Treatment(
        appointment_id=appointment_id,
        diagnosis=diagnosis,
        prescription=prescription,
        notes=notes,
        next_visit_date=next_visit
    )
    db.session.add(new_treatment)
    
    # Mark appointment as completed
    appointment.status = AppointmentStatus.COMPLETED
    
    db.session.commit()
    
    return jsonify({
        'message': 'Treatment added successfully',
        'treatment_id': new_treatment.id
    }), 201


@doctor_bp.route('/treatments/<int:treatment_id>', methods=['PUT'])
@role_required(UserRole.DOCTOR)
def update_treatment(treatment_id):
    """Update existing treatment."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    doctor = user.doctor
    
    treatment = Treatment.query.join(Appointment).filter(
        Treatment.id == treatment_id,
        Appointment.doctor_id == doctor.id
    ).first()
    
    if not treatment:
        return jsonify({'message': 'Treatment not found'}), 404
    
    data = request.get_json()
    
    if data.get('diagnosis'):
        treatment.diagnosis = data['diagnosis']
    if 'prescription' in data:
        treatment.prescription = data['prescription']
    if 'notes' in data:
        treatment.notes = data['notes']
    if 'next_visit_date' in data:
        if data['next_visit_date']:
            try:
                treatment.next_visit_date = datetime.strptime(data['next_visit_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'message': 'Invalid date format'}), 400
        else:
            treatment.next_visit_date = None
    
    db.session.commit()
    return jsonify({'message': 'Treatment updated successfully'}), 200


# ============= PATIENTS =============
@doctor_bp.route('/patients', methods=['GET'])
@role_required(UserRole.DOCTOR)
def get_patients():
    """Get list of patients assigned to this doctor."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    doctor = user.doctor
    
    # Get unique patients who have appointments with this doctor
    patients = db.session.query(Patient).join(Appointment).filter(
        Appointment.doctor_id == doctor.id
    ).distinct().all()
    
    return jsonify({
        'patients': [{
            'id': p.id,
            'name': p.name,
            'age': p.age,
            'gender': p.gender,
            'contact': p.contact,
            'appointment_count': Appointment.query.filter_by(
                patient_id=p.id,
                doctor_id=doctor.id
            ).count()
        } for p in patients]
    }), 200


@doctor_bp.route('/patients/<int:patient_id>', methods=['GET'])
@role_required(UserRole.DOCTOR)
def get_patient_details(patient_id):
    """Get patient details and full medical history with this doctor."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    doctor = user.doctor
    
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404
    
    # Get all appointments with this doctor
    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        doctor_id=doctor.id
    ).order_by(Appointment.date.desc()).all()
    
    return jsonify({
        'patient': {
            'id': patient.id,
            'name': patient.name,
            'age': patient.age,
            'gender': patient.gender,
            'contact': patient.contact,
            'address': patient.address,
            'blood_group': patient.blood_group,
            'allergies': patient.allergies
        },
        'medical_history': [{
            'id': a.id,
            'date': a.date.isoformat(),
            'time': a.time.strftime('%H:%M'),
            'status': a.status.value,
            'reason': a.reason,
            'notes': a.notes,
            'treatment': {
                'diagnosis': a.treatment.diagnosis,
                'prescription': a.treatment.prescription,
                'notes': a.treatment.notes,
                'next_visit_date': a.treatment.next_visit_date.isoformat() if a.treatment.next_visit_date else None
            } if a.treatment else None
        } for a in appointments]
    }), 200


# ============= AVAILABILITY =============
@doctor_bp.route('/availability', methods=['GET'])
@role_required(UserRole.DOCTOR)
def get_availability():
    """Get doctor's availability for next 7 days."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    doctor = user.doctor
    
    today = date.today()
    week_later = today + timedelta(days=7)
    
    availabilities = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date.between(today, week_later)
    ).all()
    
    return jsonify({
        'availabilities': [{
            'id': av.id,
            'date': av.date.isoformat(),
            'time_slots': av.get_time_slots()
        } for av in availabilities]
    }), 200


@doctor_bp.route('/availability', methods=['POST'])
@role_required(UserRole.DOCTOR)
def add_availability():
    """Add availability for a specific date."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    doctor = user.doctor
    
    data = request.get_json()
    date_str = data.get('date')
    time_slots = data.get('time_slots', [])
    
    if not date_str or not time_slots:
        return jsonify({'message': 'Date and time slots are required'}), 400
    
    try:
        availability_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format'}), 400
    
    # Check if availability already exists
    existing = DoctorAvailability.query.filter_by(
        doctor_id=doctor.id,
        date=availability_date
    ).first()
    
    if existing:
        existing.set_time_slots(time_slots)
        db.session.commit()
        return jsonify({'message': 'Availability updated successfully'}), 200
    
    new_availability = DoctorAvailability(
        doctor_id=doctor.id,
        date=availability_date
    )
    new_availability.set_time_slots(time_slots)
    db.session.add(new_availability)
    db.session.commit()
    
    return jsonify({'message': 'Availability added successfully'}), 201


@doctor_bp.route('/availability/<int:availability_id>', methods=['PUT'])
@role_required(UserRole.DOCTOR)
def update_availability(availability_id):
    """Update availability time slots."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    doctor = user.doctor
    
    availability = DoctorAvailability.query.filter_by(
        id=availability_id,
        doctor_id=doctor.id
    ).first()
    
    if not availability:
        return jsonify({'message': 'Availability not found'}), 404
    
    data = request.get_json()
    time_slots = data.get('time_slots', [])
    
    availability.set_time_slots(time_slots)
    db.session.commit()
    
    return jsonify({'message': 'Availability updated successfully'}), 200


@doctor_bp.route('/availability/<int:availability_id>', methods=['DELETE'])
@role_required(UserRole.DOCTOR)
def delete_availability(availability_id):
    """Delete availability for a date."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    doctor = user.doctor
    
    availability = DoctorAvailability.query.filter_by(
        id=availability_id,
        doctor_id=doctor.id
    ).first()
    
    if not availability:
        return jsonify({'message': 'Availability not found'}), 404
    
    db.session.delete(availability)
    db.session.commit()
    
    return jsonify({'message': 'Availability deleted successfully'}), 200


# ============= PROFILE =============
@doctor_bp.route('/profile', methods=['GET'])
@role_required(UserRole.DOCTOR)
def get_profile():
    """Get doctor profile."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    doctor = user.doctor
    
    return jsonify({
        'id': doctor.id,
        'name': doctor.name,
        'email': user.email,
        'specialization': doctor.department.name,
        'bio': doctor.bio,
        'contact': doctor.contact,
        'schedule': doctor.schedule
    }), 200


@doctor_bp.route('/profile', methods=['PUT'])
@role_required(UserRole.DOCTOR)
def update_profile():
    """Update doctor profile."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    doctor = user.doctor
    
    data = request.get_json()
    
    if data.get('contact'):
        doctor.contact = data['contact']
    if 'bio' in data:
        doctor.bio = data['bio']
    if 'schedule' in data:
        doctor.schedule = data['schedule']
    
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200