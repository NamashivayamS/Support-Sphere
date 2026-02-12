#!/usr/bin/env python
"""
Notification Management CLI Tool
Provides commands for testing and managing the email notification system
"""

import sys
from app import app, db, mail, Task, User, NotificationSettings
from utils.email_service import check_and_send_deadline_reminders
from datetime import datetime, timedelta


def test_email_config():
    """Test email configuration by sending a test email"""
    print("Testing email configuration...")
    
    with app.app_context():
        from flask_mail import Message
        
        try:
            # Get first user for testing
            user = User.query.first()
            if not user:
                print("❌ No users found in database")
                return False
            
            msg = Message(
                "Test Email from SupportSphere",
                recipients=[user.email]
            )
            msg.body = "This is a test email to verify your email configuration."
            msg.html = """
            <html>
            <body>
                <h2>Test Email</h2>
                <p>This is a test email to verify your email configuration.</p>
                <p>If you received this, your email setup is working correctly!</p>
            </body>
            </html>
            """
            
            mail.send(msg)
            print(f"✅ Test email sent successfully to {user.email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending test email: {str(e)}")
            return False


def check_deadlines():
    """Check for tasks with approaching deadlines"""
    print("Checking for tasks with approaching deadlines...")
    
    with app.app_context():
        try:
            count = check_and_send_deadline_reminders(mail, app, db, Task)
            print(f"✅ Sent {count} deadline reminder(s)")
            return True
        except Exception as e:
            print(f"❌ Error checking deadlines: {str(e)}")
            return False


def list_notification_settings():
    """List notification settings for all users"""
    print("\nNotification Settings Summary:")
    print("=" * 80)
    
    with app.app_context():
        users = User.query.all()
        
        for user in users:
            settings = NotificationSettings.query.filter_by(user_id=user.id).first()
            
            print(f"\n👤 {user.name} ({user.email}) - {user.role}")
            
            if settings:
                print(f"   Email Notifications:")
                print(f"      Task Assigned: {'✅' if settings.email_task_assigned else '❌'}")
                print(f"      Deadline Reminder: {'✅' if settings.email_deadline_reminder else '❌'}")
                print(f"      Project Status: {'✅' if settings.email_project_status_change else '❌'}")
                print(f"   Quiet Hours: {settings.quiet_hours_start}:00 - {settings.quiet_hours_end}:00")
                print(f"   Digest: {settings.digest_frequency}")
            else:
                print("   ⚠️  No notification settings found")


def create_missing_settings():
    """Create notification settings for users who don't have them"""
    print("Creating missing notification settings...")
    
    with app.app_context():
        users = User.query.all()
        created = 0
        
        for user in users:
            settings = NotificationSettings.query.filter_by(user_id=user.id).first()
            
            if not settings:
                settings = NotificationSettings(user_id=user.id)
                db.session.add(settings)
                created += 1
                print(f"   Created settings for {user.name}")
        
        if created > 0:
            db.session.commit()
            print(f"✅ Created {created} notification setting(s)")
        else:
            print("✅ All users already have notification settings")


def show_upcoming_deadlines():
    """Show tasks with upcoming deadlines"""
    print("\nUpcoming Task Deadlines:")
    print("=" * 80)
    
    with app.app_context():
        now = datetime.utcnow()
        week_from_now = now + timedelta(days=7)
        
        tasks = Task.query.filter(
            Task.deadline <= week_from_now,
            Task.deadline > now,
            Task.status != 'Completed'
        ).order_by(Task.deadline).all()
        
        if not tasks:
            print("No upcoming deadlines in the next 7 days")
            return
        
        for task in tasks:
            hours_remaining = int((task.deadline - now).total_seconds() / 3600)
            days_remaining = hours_remaining // 24
            
            assignee_name = task.assignee.name if task.assignee else "Unassigned"
            
            print(f"\n📋 {task.title}")
            print(f"   Project: {task.project.title}")
            print(f"   Assignee: {assignee_name}")
            print(f"   Priority: {task.priority}")
            print(f"   Status: {task.status}")
            print(f"   Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M')}")
            
            if days_remaining > 0:
                print(f"   ⏰ {days_remaining} days remaining")
            else:
                print(f"   ⚠️  {hours_remaining} hours remaining")


def show_help():
    """Display help information"""
    print("""
SupportSphere Notification Management Tool
==========================================

Usage: python manage_notifications.py [command]

Commands:
    test-email      Send a test email to verify configuration
    check-deadlines Check for approaching deadlines and send reminders
    list-settings   Display notification settings for all users
    create-settings Create missing notification settings
    show-deadlines  Show tasks with upcoming deadlines
    help            Display this help message

Examples:
    python manage_notifications.py test-email
    python manage_notifications.py check-deadlines
    python manage_notifications.py list-settings

For more information, see EMAIL_NOTIFICATIONS_README.md
    """)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    commands = {
        'test-email': test_email_config,
        'check-deadlines': check_deadlines,
        'list-settings': list_notification_settings,
        'create-settings': create_missing_settings,
        'show-deadlines': show_upcoming_deadlines,
        'help': show_help
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python manage_notifications.py help' for usage information")


if __name__ == '__main__':
    main()
