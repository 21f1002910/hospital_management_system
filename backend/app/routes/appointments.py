"""
Enhanced Appointment History and Conflict Prevention System
Handles complete appointment history, double-booking prevention, and status management
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date, time

from ..models import (db,
    User, UserRole, Patient, Doctor, Appointment, AppointmentStatus,
    Treatment, Department
)
from .decorators import role_required

appointment_bp = Blueprint('appointments', __name__, url_prefix='/api/appointments')

# ============= CONFLICT PREVENTION =============
def check_appointment_conflict(doctor_id, appointment_date, appointment_time, exclude_id=None):
    """
    Check if a doctor already has an appointment at the given time.
    Returns: (has_conflict, conflicting_appointment)
    """
    query = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == appointment_date,
        Appointment.time == appointment_time,
        Appointment.status == AppointmentStatus.BOOKED  # Only check booked appointments
    )
    
    # Exclude specific appointment (for rescheduling)
    if exclude_id:
        query = query.filter(Appointment.id != exclude_id)
    
    conflict = query.first()
    return (conflict is not None, conflict)


def validate_appointment_slot(doctor_id, appointment_date, appointment_time, exclude_id=None):
    """
    Validate if an appointment slot is available.
    Returns: (is_valid, error_message)
    """
    # Check if date is in the past
    if appointment_date < date.today():
        return (False, "Cannot book appointments in the past")
    
    # Check if date is today and time is in the past
    if appointment_date == date.today():
        current_time = datetime.now().time()
        if appointment_time < current_time:
            return (False, "Cannot book appointments in the past")
    
    # Check for conflicts
    has_conflict, conflict = check_appointment_conflict(
        doctor_id, appointment_date, appointment_time, exclude_id
    )
    
    if has_conflict:
        return (False, f"This time slot is already booked")
    
    return (True, None)


# ============= APPOINTMENT HISTORY =============
@appointment_bp.route('/history', methods=['GET'])
@role_required(UserRole.ADMIN, UserRole.DOCTOR, UserRole.PATIENT)
def get_appointment_history():
    """
    Get complete appointment history based on user role.
    Admin: All appointments
    Doctor: Their appointments
    Patient: Their appointments
    """
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Filters
    status_filter = request.args.get('status', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    patient_id = request.args.get('patient_id', type=int)
    doctor_id = request.args.get('doctor_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Base query based on role
    query = Appointment.query
    
    if user.role == UserRole.PATIENT:
        query = query.filter_by(patient_id=user.patient.id)
    elif user.role == UserRole.DOCTOR:
        query = query.filter_by(doctor_id=user.doctor.id)
    # Admin sees all appointments
    
    # Apply filters
    if status_filter:
        try:
            status_enum = AppointmentStatus[status_filter.upper()]
            query = query.filter_by(status=status_enum)
        except KeyError:
            return jsonify({'message': 'Invalid status'}), 400
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Appointment.date >= from_date)
        except ValueError:
            return jsonify({'message': 'Invalid date_from format'}), 400
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Appointment.date <= to_date)
        except ValueError:
            return jsonify({'message': 'Invalid date_to format'}), 400
    
    if patient_id and user.role in [UserRole.ADMIN, UserRole.DOCTOR]:
        query = query.filter_by(patient_id=patient_id)
    
    if doctor_id and user.role == UserRole.ADMIN:
        query = query.filter_by(doctor_id=doctor_id)
    
    # Order by date (newest first)
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
            'reason': a.reason,
            'notes': a.notes,
            'has_treatment': a.treatment is not None,
            'created_at': a.created_at.isoformat(),
            'updated_at': a.updated_at.isoformat()
        } for a in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
        'per_page': per_page
    }), 200


@appointment_bp.route('/history/statistics', methods=['GET'])
@role_required(UserRole.ADMIN, UserRole.DOCTOR, UserRole.PATIENT)
def get_history_statistics():
    """Get appointment statistics for the current user."""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Base query based on role
    query = Appointment.query
    
    if user.role == UserRole.PATIENT:
        query = query.filter_by(patient_id=user.patient.id)
    elif user.role == UserRole.DOCTOR:
        query = query.filter_by(doctor_id=user.doctor.id)
    
    # Count by status
    total = query.count()
    booked = query.filter_by(status=AppointmentStatus.BOOKED).count()
    completed = query.filter_by(status=AppointmentStatus.COMPLETED).count()
    cancelled = query.filter_by(status=AppointmentStatus.CANCELLED).count()
    
    # Count this month
    from datetime import timedelta
    today = date.today()
    first_day = today.replace(day=1)
    this_month = query.filter(Appointment.date >= first_day).count()
    
    return jsonify({
        'total_appointments': total,
        'booked': booked,
        'completed': completed,
        'cancelled': cancelled,
        'this_month': this_month
    }), 200


# ============= TREATMENT RECORDS ACCESS =============
@appointment_bp.route('/<int:appointment_id>/treatment', methods=['GET'])
@role_required(UserRole.ADMIN, UserRole.DOCTOR, UserRole.PATIENT)
def get_treatment_record(appointment_id):
    """
    Get treatment record for an appointment.
    Access control: Admin (all), Doctor (their patients), Patient (their own)
    """
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404
    
    # Access control
    if user.role == UserRole.PATIENT:
        if appointment.patient_id != user.patient.id:
            return jsonify({'message': 'Access denied'}), 403
    elif user.role == UserRole.DOCTOR:
        if appointment.doctor_id != user.doctor.id:
            return jsonify({'message': 'Access denied'}), 403
    # Admin has access to all
    
    if not appointment.treatment:
        return jsonify({'message': 'No treatment record found'}), 404
    
    treatment = appointment.treatment
    
    return jsonify({
        'id': treatment.id,
        'appointment_id': appointment.id,
        'diagnosis': treatment.diagnosis,
        'prescription': treatment.prescription,
        'notes': treatment.notes,
        'next_visit_date': treatment.next_visit_date.isoformat() if treatment.next_visit_date else None,
        'created_at': treatment.created_at.isoformat(),
        'updated_at': treatment.updated_at.isoformat()
    }), 200


@appointment_bp.route('/patient/<int:patient_id>/records', methods=['GET'])
@role_required(UserRole.ADMIN, UserRole.DOCTOR)
def get_patient_treatment_records(patient_id):
    """
    Get all treatment records for a patient.
    Access: Admin (all patients), Doctor (only their patients)
    """
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404
    
    # Query appointments with treatments
    query = Appointment.query.filter_by(patient_id=patient_id)
    
    # Doctor can only see their own appointments with the patient
    if user.role == UserRole.DOCTOR:
        query = query.filter_by(doctor_id=user.doctor.id)
    
    appointments = query.order_by(Appointment.date.desc()).all()
    
    return jsonify({
        'patient': {
            'id': patient.id,
            'name': patient.name,
            'age': patient.age,
            'gender': patient.gender,
            'blood_group': patient.blood_group,
            'allergies': patient.allergies
        },
        'records': [{
            'appointment_id': a.id,
            'doctor_name': a.doctor.name,
            'specialization': a.doctor.department.name,
            'date': a.date.isoformat(),
            'time': a.time.strftime('%H:%M'),
            'status': a.status.value,
            'reason': a.reason,
            'treatment': {
                'diagnosis': a.treatment.diagnosis,
                'prescription': a.treatment.prescription,
                'notes': a.treatment.notes,
                'next_visit_date': a.treatment.next_visit_date.isoformat() if a.treatment.next_visit_date else None
            } if a.treatment else None
        } for a in appointments]
    }), 200


# ============= STATUS UPDATES =============
@appointment_bp.route('/<int:appointment_id>/status', methods=['PUT'])
@role_required(UserRole.ADMIN, UserRole.DOCTOR)
def update_appointment_status(appointment_id):
    """
    Update appointment status.
    Access: Admin (all), Doctor (their appointments)
    """
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404
    
    # Access control for doctors
    if user.role == UserRole.DOCTOR:
        if appointment.doctor_id != user.doctor.id:
            return jsonify({'message': 'Access denied'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    notes = data.get('notes')
    
    if not new_status:
        return jsonify({'message': 'Status is required'}), 400
    
    try:
        status_enum = AppointmentStatus[new_status.upper()]
    except KeyError:
        return jsonify({'message': 'Invalid status value'}), 400
    
    # Status change validation
    old_status = appointment.status
    
    # Prevent changing completed appointments back to booked
    if old_status == AppointmentStatus.COMPLETED and status_enum == AppointmentStatus.BOOKED:
        return jsonify({'message': 'Cannot change completed appointment back to booked'}), 400
    
    appointment.status = status_enum
    
    if notes:
        appointment.notes = notes
    
    db.session.commit()
    
    return jsonify({
        'message': 'Status updated successfully',
        'old_status': old_status.value,
        'new_status': status_enum.value
    }), 200


# ============= CONFLICT CHECKING ENDPOINT =============
@appointment_bp.route('/check-availability', methods=['POST'])
@role_required(UserRole.ADMIN, UserRole.DOCTOR, UserRole.PATIENT)
def check_availability():
    """Check if a time slot is available for booking."""
    data = request.get_json()
    
    doctor_id = data.get('doctor_id')
    appointment_date = data.get('date')
    appointment_time = data.get('time')
    exclude_id = data.get('exclude_id')  # For rescheduling
    
    if not doctor_id or not appointment_date or not appointment_time:
        return jsonify({'message': 'Missing required fields'}), 400
    
    try:
        apt_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        apt_time = datetime.strptime(appointment_time, '%H:%M').time()
    except ValueError:
        return jsonify({'message': 'Invalid date or time format'}), 400
    
    is_valid, error_message = validate_appointment_slot(
        doctor_id, apt_date, apt_time, exclude_id
    )
    
    return jsonify({
        'available': is_valid,
        'message': error_message if not is_valid else 'Slot is available'
    }), 200


# ============= APPOINTMENT AUDIT LOG =============
@appointment_bp.route('/<int:appointment_id>/audit-log', methods=['GET'])
@role_required(UserRole.ADMIN)
def get_appointment_audit_log(appointment_id):
    """
    Get audit log for an appointment (status changes, updates).
    Admin only.
    """
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404
    
    return jsonify({
        'appointment_id': appointment.id,
        'created_at': appointment.created_at.isoformat(),
        'updated_at': appointment.updated_at.isoformat(),
        'current_status': appointment.status.value,
        'patient_name': appointment.patient.name,
        'doctor_name': appointment.doctor.name,
        'date': appointment.date.isoformat(),
        'time': appointment.time.strftime('%H:%M')
    }), 200


# ============= BULK OPERATIONS =============
@appointment_bp.route('/bulk-status-update', methods=['PUT'])
@role_required(UserRole.ADMIN)
def bulk_status_update():
    """
    Bulk update appointment statuses.
    Admin only - for administrative operations.
    """
    data = request.get_json()
    appointment_ids = data.get('appointment_ids', [])
    new_status = data.get('status')
    
    if not appointment_ids or not new_status:
        return jsonify({'message': 'Missing required fields'}), 400
    
    try:
        status_enum = AppointmentStatus[new_status.upper()]
    except KeyError:
        return jsonify({'message': 'Invalid status value'}), 400
    
    updated_count = 0
    for apt_id in appointment_ids:
        appointment = Appointment.query.get(apt_id)
        if appointment:
            appointment.status = status_enum
            updated_count += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'Updated {updated_count} appointments',
        'updated_count': updated_count
    }), 200


# ============= APPOINTMENT SEARCH =============
@appointment_bp.route('/search', methods=['GET'])
@role_required(UserRole.ADMIN, UserRole.DOCTOR)
def search_appointments():
    """
    Advanced appointment search.
    Admin: All appointments, Doctor: Their appointments
    """
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Search parameters
    patient_name = request.args.get('patient_name', '').strip()
    doctor_name = request.args.get('doctor_name', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    status = request.args.get('status', '').strip()
    
    query = Appointment.query.join(Patient).join(Doctor)
    
    # Role-based filtering
    if user.role == UserRole.DOCTOR:
        query = query.filter(Appointment.doctor_id == user.doctor.id)
    
    # Apply search filters
    if patient_name:
        query = query.filter(Patient.name.ilike(f'%{patient_name}%'))
    
    if doctor_name:
        query = query.filter(Doctor.name.ilike(f'%{doctor_name}%'))
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Appointment.date >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Appointment.date <= to_date)
        except ValueError:
            pass
    
    if status:
        try:
            status_enum = AppointmentStatus[status.upper()]
            query = query.filter(Appointment.status == status_enum)
        except KeyError:
            pass
    
    appointments = query.order_by(Appointment.date.desc()).limit(50).all()
    
    return jsonify({
        'results': [{
            'id': a.id,
            'patient_name': a.patient.name,
            'doctor_name': a.doctor.name,
            'date': a.date.isoformat(),
            'time': a.time.strftime('%H:%M'),
            'status': a.status.value
        } for a in appointments]
    }), 200