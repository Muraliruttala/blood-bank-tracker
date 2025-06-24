import os
import logging
from flask import Flask, render_template, session, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "blood-bank-secret-key-2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Import blueprints
from auth import auth_bp
from user_routes import user_bp
from admin_routes import admin_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.route('/')
def index():
    """Landing page with navigation"""
    return render_template('index.html')

@app.route('/logout')
def logout():
    """Logout user and clear session"""
    session.clear()
    return redirect(url_for('index'))

@app.context_processor
def inject_user():
    """Make user info available in all templates"""
    return dict(
        current_user=session.get('user'),
        is_logged_in='user' in session
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
