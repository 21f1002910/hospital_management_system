"""Routes package - registers all blueprints."""

from flask import jsonify

def register_routes(app):
    """Register all blueprints with the Flask app."""
    from .auth import auth_bp
    from .admin import admin_bp
    from .patient import patient_bp
    from .doctor import doctor_bp
    from .appointments import appointment_bp
    
    # Root endpoint
    @app.route('/')
    def home():
        return jsonify({
            'message': 'Hospital Management System API',
            'version': '1.0',
            'endpoints': {
                'auth': '/api/auth (login, register)',
                'admin': '/api/admin (dashboard, appointments)',
                'patient': '/api/patient (dashboard)',
                'doctor': '/api/doctor (dashboard)',
                'appointments': '/api/appointment'
            }
        }), 200
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(appointment_bp)