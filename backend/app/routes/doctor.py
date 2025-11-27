"""Doctor routes - appointments, patient records, schedule management."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..models import db, User, UserRole, Doctor, Patient, Appointment, AppointmentStatus
from .decorators import role_required

doctor_bp = Blueprint('doctor', __name__, url_prefix='/api/doctor')

@doctor_bp.route('/dashboard', methods=['GET'])
@role_required(UserRole.DOCTOR)
def dashboard():
    """Doctor dashboard data."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    doctor = user.doctor
    
    upcoming = Appointment.query.filter_by(
        doctor_id=doctor.id, 
        status=AppointmentStatus.BOOKED
    ).count()
    
    completed = Appointment.query.filter_by(
        doctor_id=doctor.id,
        status=AppointmentStatus.COMPLETED
    ).count()
    
    return jsonify({
        'upcoming_appointments': upcoming,
        'completed_appointments': completed,
        'doctor_name': doctor.name
    }), 200