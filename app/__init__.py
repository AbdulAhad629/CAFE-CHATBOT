"""
Flask Application Factory
UPDATED VERSION - With Twilio Support
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config.config import config
import os


def create_app(config_name='development'):
    """
    Application factory
    Creates and configures the Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    messaging_provider = 'Twilio' if os.getenv('USE_TWILIO', 'false').lower() == 'true' else 'Meta WhatsApp'
    # Enable CORS
    CORS(app)
    
    # Import and register blueprints
    from app.routes.whatsapp_routes import whatsapp_bp
    from app.routes.menu_routes import menu_bp
    from app.routes.order_routes import order_bp
    from app.routes.payment_routes import payment_bp
    from app.routes.staff_routes import staff_bp
    from app.routes.twilio_routes import twilio_bp
    
    # Register blueprints with URL prefixes
    app.register_blueprint(whatsapp_bp, url_prefix='/webhook')
    app.register_blueprint(twilio_bp, url_prefix='/webhook')
    app.register_blueprint(menu_bp, url_prefix='/api/menu')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(payment_bp, url_prefix='/api/payment')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    
    # Health check route
    @app.route('/')
    def index():
        """API health check endpoint"""
        messaging_provider = 'Twilio' if os.getenv('USE_TWILIO', 'false').lower() == 'true' else 'Meta WhatsApp'
        
        return jsonify({
            'status': 'running',
            'message': 'WhatsApp Cafeteria Chatbot API',
            'version': '2.0.0',
            'messaging_provider': messaging_provider,
            'endpoints': {
                'whatsapp_webhook': '/webhook/whatsapp',
                'twilio_webhook': '/webhook/twilio',
                'menu': '/api/menu',
                'orders': '/api/orders',
                'payment': '/api/payment',
                'staff_dashboard': '/staff/dashboard'
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'status': 'error',
            'message': 'Endpoint not found',
            'error': str(error)
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'error': str(error)
        }), 500
    
    # Log startup info
    print("=" * 70)
    print("🚀 Flask Application Started")
    print("=" * 70)
    print(f"📱 Messaging Provider: {messaging_provider}")
    print(f"🗄️  Database: Supabase")
    print(f"🌐 Environment: {config_name}")
    print("=" * 70)
    
    return app