"""Patient routes - appointments, medical records, profile management."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from ..models import db, User, UserRole, Patient, Doctor, Appointment, AppointmentStatus
from .decorators import role_required

patient_bp = Blueprint('patient', __name__, url_prefix='/api/patient')

@patient_bp.route('/dashboard', methods=['GET'])
@role_required(UserRole.PATIENT)
def dashboard():
    """Patient dashboard data."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    patient = user.patient