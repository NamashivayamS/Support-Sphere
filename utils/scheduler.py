"""
Background Task Scheduler for SupportSphere
Handles periodic tasks like deadline reminders
"""

from datetime import datetime, timedelta
from threading import Thread
import time


def check_deadline_reminders(app, db, mail, Task):
    """
    Check for tasks with approaching deadlines and send reminders
    This runs in a background thread
    """
    from utils.email_service import send_deadline_reminder_email
    
    with app.app_context():
        try:
            # Get tasks with deadlines within 24 hours that are not completed
            now = datetime.utcnow()
            tomorrow = now + timedelta(hours=24)
            
            tasks_due_soon = Task.query.filter(
                Task.deadline <= tomorrow,
                Task.deadline > now,
                Task.status != 'Completed',
                Task.assignee_id.isnot(None)
            ).all()
            
            reminder_count = 0
            for task in tasks_due_soon:
                if task.assignee and task.assignee.notification_settings:
                    # Check if user wants deadline reminders
                    if task.assignee.notification_settings.should_send_email('deadline_reminder'):
                        # Check if not in quiet hours
                        if not task.assignee.notification_settings.is_quiet_hours():
                            try:
                                send_deadline_reminder_email(mail, app, task, task.assignee)
                                reminder_count += 1
                            except Exception as e:
                                print(f"Error sending deadline reminder for task {task.id}: {str(e)}")
            
            if reminder_count > 0:
                print(f"Sent {reminder_count} deadline reminder(s)")
                
        except Exception as e:
            print(f"Error in deadline reminder check: {str(e)}")


def run_scheduler(app, db, mail, Task, interval_hours=6):
    """
    Run the scheduler in a background thread
    Checks for deadline reminders every interval_hours
    
    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
        mail: Flask-Mail instance
        Task: Task model class
        interval_hours: Hours between checks (default: 6)
    """
    def scheduler_loop():
        print(f"Deadline reminder scheduler started (checking every {interval_hours} hours)")
        while True:
            try:
                check_deadline_reminders(app, db, mail, Task)
            except Exception as e:
                print(f"Scheduler error: {str(e)}")
            
            # Wait for next check
            time.sleep(interval_hours * 3600)
    
    # Start scheduler in background thread
    scheduler_thread = Thread(target=scheduler_loop, daemon=True)
    scheduler_thread.start()
    
    return scheduler_thread


def check_overdue_tasks(app, db, Task):
    """
    Check for overdue tasks and update their status
    This should be called periodically
    """
    with app.app_context():
        try:
            now = datetime.utcnow()
            
            # Find tasks that are overdue but not marked as such
            overdue_tasks = Task.query.filter(
                Task.deadline < now,
                Task.status.in_(['Pending', 'In Progress']),
                Task.status != 'Completed'
            ).all()
            
            for task in overdue_tasks:
                # You could add a 'Overdue' status or just flag them
                # For now, we'll just log them
                print(f"Task {task.id} '{task.title}' is overdue")
            
            return len(overdue_tasks)
            
        except Exception as e:
            print(f"Error checking overdue tasks: {str(e)}")
            return 0
