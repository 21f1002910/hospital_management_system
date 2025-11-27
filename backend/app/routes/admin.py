"""Admin routes - user management, system overview, etc."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..models import db, User, UserRole, Patient, Doctor, Appointment
from .decorators import role_required

from datetime import datetime, date, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/dashboard', methods=['GET'])
@role_required(UserRole.ADMIN)
def dashboard():
    """Admin dashboard data."""
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    
    return jsonify({
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments
    }), 200