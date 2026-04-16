from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User, NotificationSettings

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect authenticated users away from login page
    if current_user.is_authenticated:
        if current_user.role == 'manager':
            return redirect(url_for('manager.dashboard'))
        elif current_user.role == 'team_member':
            return redirect(url_for('team.dashboard'))
        elif current_user.role == 'customer':
            return redirect(url_for('customer.dashboard'))
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'  # Proper remember me handling
        
        # Validation
        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('auth/login.html')
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Successful login with remember me functionality
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.name}!', 'success')
            
            # Handle next parameter for redirect after login
            next_page = request.args.get('next')
            
            # Redirect based on role
            if next_page:
                return redirect(next_page)
            elif user.role == 'manager':
                return redirect(url_for('manager.dashboard'))
            elif user.role == 'team_member':
                return redirect(url_for('team.dashboard'))
            elif user.role == 'customer':
                return redirect(url_for('customer.dashboard'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect authenticated users away from register page
    if current_user.is_authenticated:
        if current_user.role == 'manager':
            return redirect(url_for('manager.dashboard'))
        elif current_user.role == 'team_member':
            return redirect(url_for('team.dashboard'))
        elif current_user.role == 'customer':
            return redirect(url_for('customer.dashboard'))
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'customer')
        
        # Validation
        if not name or not email or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')
        
        if len(name) < 2:
            flash('Name must be at least 2 characters long.', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html')
        
        # Password confirmation validation
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('auth/register.html')
        
        # Email validation (basic)
        if '@' not in email or '.' not in email:
            flash('Please provide a valid email address.', 'danger')
            return render_template('auth/register.html')
        
        # Check for duplicate email with proper error handling
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('This email is already registered. Please login or use a different email.', 'danger')
            return render_template('auth/register.html')
        
        try:
            # Create new user
            user = User(
                name=name,
                email=email,
                role=role
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.flush()  # Flush to get user.id before creating notification settings
            
            # CRITICAL: Create notification settings for EVERY new user automatically
            notification_settings = NotificationSettings(user_id=user.id)
            db.session.add(notification_settings)
            
            db.session.commit()
            
            flash(f'Registration successful! Welcome, {name}. Please login to continue.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            print(f"Registration error: {str(e)}")  # Log error for debugging
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    user_name = current_user.name
    logout_user()
    flash(f'Goodbye, {user_name}! You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    # Redirect authenticated users away from forgot password page
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Please provide your email address.', 'danger')
            return render_template('auth/forgot_password.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # In production, send email with reset link
            # For now, just show a success message
            flash('If an account exists with this email, a password reset link has been sent.', 'info')
        else:
            # Don't reveal if email exists or not (security best practice)
            flash('If an account exists with this email, a password reset link has been sent.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')
