"""Authentication routes - login and registration endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

from ..models import db, User, UserRole, Patient

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Patient registration endpoint."""
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    contact = data.get('contact')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    # Validation
    if password != confirm_password:
        return jsonify({'message': 'Passwords do not match'}), 400
    
    if not email or not password or not name or not contact:
        return jsonify({'message': 'Missing required fields'}), 400

    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 400

    try:
        # Create user account
        new_user = User(email=email, role=UserRole.PATIENT)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()  # Get the user.id before commit

        # Create patient profile
        new_patient = Patient(
            user_id=new_user.id,
            name=name,
            contact=contact
        )
        db.session.add(new_patient)
        db.session.commit()

        return jsonify({'message': 'Patient registered successfully'}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")  # For debugging
        return jsonify({'message': 'Registration failed. Please try again.'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint for all roles."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400

    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'message': 'Account is inactive'}), 403

    # Create JWT token
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'access_token': access_token,
        'role': user.role.value,
        'email': user.email
    }), 200