"""
Email Notification Service for SupportSphere
Handles all email notifications in a background-safe manner
"""

from flask import render_template_string
from flask_mail import Message
from threading import Thread
import os


def send_async_email(app, mail, msg):
    """Send email asynchronously to avoid blocking"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {str(e)}")


def send_email(mail, app, subject, recipient, html_body, text_body=None):
    """
    Send email with both HTML and plain text versions
    Uses threading to avoid blocking the main application
    """
    msg = Message(
        subject=subject,
        recipients=[recipient] if isinstance(recipient, str) else recipient,
        html=html_body,
        body=text_body or html_body
    )
    
    # Send asynchronously
    Thread(target=send_async_email, args=(app, mail, msg)).start()


def send_task_assignment_email(mail, app, task, assignee):
    """Send email when a task is assigned to a team member"""
    subject = f"New Task Assigned: {task.title}"
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
            .task-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; 
                           border-left: 4px solid #667eea; }}
            .detail-row {{ margin: 10px 0; }}
            .label {{ font-weight: bold; color: #667eea; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #667eea; 
                      color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            .footer {{ text-align: center; color: #6c757d; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 New Task Assignment</h1>
            </div>
            <div class="content">
                <p>Hi {assignee.name},</p>
                <p>You have been assigned a new task in the <strong>{task.project.title}</strong> project.</p>
                
                <div class="task-details">
                    <h3>{task.title}</h3>
                    <div class="detail-row">
                        <span class="label">Description:</span> {task.description or 'No description provided'}
                    </div>
                    <div class="detail-row">
                        <span class="label">Priority:</span> <strong>{task.priority}</strong>
                    </div>
                    <div class="detail-row">
                        <span class="label">Role:</span> {task.role}
                    </div>
                    <div class="detail-row">
                        <span class="label">Deadline:</span> {task.deadline.strftime('%B %d, %Y')}
                    </div>
                    <div class="detail-row">
                        <span class="label">Status:</span> {task.status}
                    </div>
                </div>
                
                <p>Please review the task details and start working on it at your earliest convenience.</p>
                
                <a href="#" class="button">View Task Details</a>
                
                <div class="footer">
                    <p>This is an automated notification from SupportSphere Project Management System.</p>
                    <p>© 2024 SupportSphere. All rights reserved.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    New Task Assignment
    
    Hi {assignee.name},
    
    You have been assigned a new task in the {task.project.title} project.
    
    Task: {task.title}
    Description: {task.description or 'No description provided'}
    Priority: {task.priority}
    Role: {task.role}
    Deadline: {task.deadline.strftime('%B %d, %Y')}
    Status: {task.status}
    
    Please review the task details and start working on it at your earliest convenience.
    
    ---
    This is an automated notification from SupportSphere Project Management System.
    """
    
    send_email(mail, app, subject, assignee.email, html_body, text_body)


def send_deadline_reminder_email(mail, app, task, assignee):
    """Send email reminder when task deadline is within 24 hours"""
    subject = f"⚠️ Task Deadline Reminder: {task.title}"
    
    hours_remaining = int((task.deadline - task.deadline.utcnow()).total_seconds() / 3600)
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                      color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
            .warning-box {{ background: #fff3cd; border-left: 4px solid #ffc107; 
                           padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .task-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .detail-row {{ margin: 10px 0; }}
            .label {{ font-weight: bold; color: #f5576c; }}
            .urgent {{ color: #dc3545; font-weight: bold; font-size: 18px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #f5576c; 
                      color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            .footer {{ text-align: center; color: #6c757d; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚠️ Deadline Reminder</h1>
            </div>
            <div class="content">
                <p>Hi {assignee.name},</p>
                
                <div class="warning-box">
                    <p class="urgent">⏰ Your task deadline is approaching!</p>
                    <p>Only <strong>{hours_remaining} hours</strong> remaining until the deadline.</p>
                </div>
                
                <div class="task-details">
                    <h3>{task.title}</h3>
                    <div class="detail-row">
                        <span class="label">Project:</span> {task.project.title}
                    </div>
                    <div class="detail-row">
                        <span class="label">Priority:</span> <strong>{task.priority}</strong>
                    </div>
                    <div class="detail-row">
                        <span class="label">Current Status:</span> {task.status}
                    </div>
                    <div class="detail-row">
                        <span class="label">Progress:</span> {task.progress}%
                    </div>
                    <div class="detail-row">
                        <span class="label">Deadline:</span> {task.deadline.strftime('%B %d, %Y at %I:%M %p')}
                    </div>
                </div>
                
                <p>Please ensure you complete this task before the deadline. If you need assistance or an extension, 
                please contact your project manager immediately.</p>
                
                <a href="#" class="button">Update Task Status</a>
                
                <div class="footer">
                    <p>This is an automated reminder from SupportSphere Project Management System.</p>
                    <p>© 2024 SupportSphere. All rights reserved.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    Deadline Reminder
    
    Hi {assignee.name},
    
    ⚠️ Your task deadline is approaching!
    Only {hours_remaining} hours remaining until the deadline.
    
    Task: {task.title}
    Project: {task.project.title}
    Priority: {task.priority}
    Current Status: {task.status}
    Progress: {task.progress}%
    Deadline: {task.deadline.strftime('%B %d, %Y at %I:%M %p')}
    
    Please ensure you complete this task before the deadline. If you need assistance or an extension, 
    please contact your project manager immediately.
    
    ---
    This is an automated reminder from SupportSphere Project Management System.
    """
    
    send_email(mail, app, subject, assignee.email, html_body, text_body)


def send_project_status_change_email(mail, app, project, recipients, old_status, new_status):
    """Send email when project status changes"""
    subject = f"Project Status Update: {project.title}"
    
    status_colors = {
        'Pending': '#6c757d',
        'In Progress': '#0d6efd',
        'Completed': '#198754',
        'On Hold': '#ffc107'
    }
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                      color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
            .status-change {{ background: white; padding: 25px; border-radius: 8px; 
                            margin: 20px 0; text-align: center; }}
            .status-badge {{ display: inline-block; padding: 8px 20px; border-radius: 20px; 
                           color: white; font-weight: bold; margin: 0 10px; }}
            .arrow {{ font-size: 24px; color: #6c757d; margin: 0 10px; }}
            .project-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .detail-row {{ margin: 10px 0; }}
            .label {{ font-weight: bold; color: #4facfe; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #4facfe; 
                      color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            .footer {{ text-align: center; color: #6c757d; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Project Status Update</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>The status of project <strong>{project.title}</strong> has been updated.</p>
                
                <div class="status-change">
                    <h3>Status Change</h3>
                    <div>
                        <span class="status-badge" style="background: {status_colors.get(old_status, '#6c757d')}">
                            {old_status}
                        </span>
                        <span class="arrow">→</span>
                        <span class="status-badge" style="background: {status_colors.get(new_status, '#6c757d')}">
                            {new_status}
                        </span>
                    </div>
                </div>
                
                <div class="project-details">
                    <h3>{project.title}</h3>
                    <div class="detail-row">
                        <span class="label">Description:</span> {project.description[:100]}...
                    </div>
                    <div class="detail-row">
                        <span class="label">Progress:</span> {project.progress}%
                    </div>
                    <div class="detail-row">
                        <span class="label">Deadline:</span> {project.deadline.strftime('%B %d, %Y')}
                    </div>
                    <div class="detail-row">
                        <span class="label">Days Remaining:</span> {project.days_remaining} days
                    </div>
                </div>
                
                <p>Please check the project dashboard for more details and updates.</p>
                
                <a href="#" class="button">View Project Details</a>
                
                <div class="footer">
                    <p>This is an automated notification from SupportSphere Project Management System.</p>
                    <p>© 2024 SupportSphere. All rights reserved.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    Project Status Update
    
    Hello,
    
    The status of project "{project.title}" has been updated.
    
    Status Change: {old_status} → {new_status}
    
    Project Details:
    - Title: {project.title}
    - Description: {project.description[:100]}...
    - Progress: {project.progress}%
    - Deadline: {project.deadline.strftime('%B %d, %Y')}
    - Days Remaining: {project.days_remaining} days
    
    Please check the project dashboard for more details and updates.
    
    ---
    This is an automated notification from SupportSphere Project Management System.
    """
    
    # Send to all recipients
    for recipient in recipients:
        send_email(mail, app, subject, recipient.email, html_body, text_body)


def check_and_send_deadline_reminders(mail, app, db, Task):
    """
    Check for tasks with deadlines within 24 hours and send reminders
    This function should be called periodically (e.g., via cron job or scheduler)
    """
    from datetime import datetime, timedelta
    
    # Get tasks with deadlines within 24 hours that are not completed
    now = datetime.utcnow()
    tomorrow = now + timedelta(hours=24)
    
    tasks_due_soon = Task.query.filter(
        Task.deadline <= tomorrow,
        Task.deadline > now,
        Task.status != 'Completed',
        Task.assignee_id.isnot(None)
    ).all()
    
    for task in tasks_due_soon:
        if task.assignee:
            send_deadline_reminder_email(mail, app, task, task.assignee)
    
    return len(tasks_due_soon)
