from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db, mail
from models import NotificationSettings
from utils.email_service import send_email
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/settings')
@login_required
def settings():
    """Display notification settings page"""
    # Get or create notification settings for current user
    settings = NotificationSettings.query.filter_by(user_id=current_user.id).first()
    
    if not settings:
        settings = NotificationSettings(user_id=current_user.id)
        db.session.add(settings)
        db.session.commit()
    
    return render_template('pages/notification_settings.html', settings=settings)


@notifications_bp.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    """Update notification settings"""
    settings = NotificationSettings.query.filter_by(user_id=current_user.id).first()
    
    if not settings:
        settings = NotificationSettings(user_id=current_user.id)
        db.session.add(settings)
    
    # Update email notification preferences
    settings.email_task_assigned = request.form.get('email_task_assigned') == 'on'
    settings.email_deadline_reminder = request.form.get('email_deadline_reminder') == 'on'
    settings.email_project_status_change = request.form.get('email_project_status_change') == 'on'
    settings.email_task_completed = request.form.get('email_task_completed') == 'on'
    settings.email_new_message = request.form.get('email_new_message') == 'on'
    settings.email_team_update = request.form.get('email_team_update') == 'on'
    
    # Update in-app notification preferences
    settings.inapp_task_assigned = request.form.get('inapp_task_assigned') == 'on'
    settings.inapp_deadline_reminder = request.form.get('inapp_deadline_reminder') == 'on'
    settings.inapp_project_status_change = request.form.get('inapp_project_status_change') == 'on'
    settings.inapp_task_completed = request.form.get('inapp_task_completed') == 'on'
    settings.inapp_new_message = request.form.get('inapp_new_message') == 'on'
    settings.inapp_team_update = request.form.get('inapp_team_update') == 'on'
    
    # Update notification frequency
    settings.digest_frequency = request.form.get('digest_frequency', 'immediate')
    
    # Update quiet hours
    try:
        settings.quiet_hours_start = int(request.form.get('quiet_hours_start', 22))
        settings.quiet_hours_end = int(request.form.get('quiet_hours_end', 8))
    except ValueError:
        flash('Invalid quiet hours values', 'danger')
        return redirect(url_for('notifications.settings'))
    
    db.session.commit()
    
    flash('Notification settings updated successfully!', 'success')
    return redirect(url_for('notifications.settings'))


@notifications_bp.route('/settings/reset', methods=['POST'])
@login_required
def reset_settings():
    """Reset notification settings to defaults"""
    settings = NotificationSettings.query.filter_by(user_id=current_user.id).first()
    
    if settings:
        # Reset to defaults
        settings.email_task_assigned = True
        settings.email_deadline_reminder = True
        settings.email_project_status_change = True
        settings.email_task_completed = True
        settings.email_new_message = True
        settings.email_team_update = True
        
        settings.inapp_task_assigned = True
        settings.inapp_deadline_reminder = True
        settings.inapp_project_status_change = True
        settings.inapp_task_completed = True
        settings.inapp_new_message = True
        settings.inapp_team_update = True
        
        settings.digest_frequency = 'immediate'
        settings.quiet_hours_start = 22
        settings.quiet_hours_end = 8
        
        db.session.commit()
        
        flash('Notification settings reset to defaults!', 'success')
    
    return redirect(url_for('notifications.settings'))


@notifications_bp.route('/test-email', methods=['POST'])
@login_required
def test_email():
    """Send a test email to verify email configuration"""
    try:
        html_body = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Test Email from SupportSphere</h2>
            <p>This is a test email to verify your email notification settings.</p>
            <p>If you received this email, your email configuration is working correctly!</p>
            <hr>
            <p style="color: #6c757d; font-size: 12px;">
                This is an automated test email from SupportSphere Project Management System.
            </p>
        </body>
        </html>
        """
        
        text_body = """
        Test Email from SupportSphere
        
        This is a test email to verify your email notification settings.
        If you received this email, your email configuration is working correctly!
        
        ---
        This is an automated test email from SupportSphere Project Management System.
        """
        
        send_email(
            mail,
            current_app._get_current_object(),
            "Test Email from SupportSphere",
            current_user.email,
            html_body,
            text_body
        )
        
        flash('Test email sent! Please check your inbox.', 'success')
    except Exception as e:
        flash(f'Error sending test email: {str(e)}', 'danger')
    
    return redirect(url_for('notifications.settings'))
