# models.py
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # customer, manager, team_member
    avatar = db.Column(db.String(200), default='default.png')
    theme = db.Column(db.String(20), default='light')  # light or dark theme preference
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships - defined inside the model
    projects_created = db.relationship('Project', foreign_keys='Project.customer_id', back_populates='customer', lazy=True)
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assignee_id', back_populates='assignee', lazy=True)
    created_tasks = db.relationship('Task', foreign_keys='Task.created_by_id', back_populates='created_by', lazy=True)
    managed_projects = db.relationship('Project', foreign_keys='Project.manager_id', back_populates='manager', lazy=True)
    team_assignments = db.relationship('TeamMember', back_populates='member', lazy=True)
    messages = db.relationship('ChatMessage', back_populates='sender', lazy=True)
    task_notes = db.relationship('TaskNote', back_populates='author', lazy=True)
    notification_settings = db.relationship('NotificationSettings', back_populates='user', uselist=False, lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class NotificationSettings(db.Model):
    __tablename__ = 'notification_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Email notification preferences
    email_task_assigned = db.Column(db.Boolean, default=True)
    email_deadline_reminder = db.Column(db.Boolean, default=True)
    email_project_status_change = db.Column(db.Boolean, default=True)
    email_task_completed = db.Column(db.Boolean, default=True)
    email_new_message = db.Column(db.Boolean, default=True)
    email_team_update = db.Column(db.Boolean, default=True)
    
    # In-app notification preferences
    inapp_task_assigned = db.Column(db.Boolean, default=True)
    inapp_deadline_reminder = db.Column(db.Boolean, default=True)
    inapp_project_status_change = db.Column(db.Boolean, default=True)
    inapp_task_completed = db.Column(db.Boolean, default=True)
    inapp_new_message = db.Column(db.Boolean, default=True)
    inapp_team_update = db.Column(db.Boolean, default=True)
    
    # Notification frequency
    digest_frequency = db.Column(db.String(20), default='immediate')
    quiet_hours_start = db.Column(db.Integer, default=22)
    quiet_hours_end = db.Column(db.Integer, default=8)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='notification_settings')
    
    def should_send_email(self, notification_type):
        type_map = {
            'task_assigned': self.email_task_assigned,
            'deadline_reminder': self.email_deadline_reminder,
            'project_status_change': self.email_project_status_change,
            'task_completed': self.email_task_completed,
            'new_message': self.email_new_message,
            'team_update': self.email_team_update
        }
        return type_map.get(notification_type, True)
    
    def is_quiet_hours(self):
        current_hour = datetime.utcnow().hour
        if self.quiet_hours_start < self.quiet_hours_end:
            return self.quiet_hours_start <= current_hour < self.quiet_hours_end
        else:
            return current_hour >= self.quiet_hours_start or current_hour < self.quiet_hours_end


class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    complexity = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    progress = db.Column(db.Integer, default=0)
    budget_range = db.Column(db.String(50), nullable=True)
    nda_required = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships - defined inside the model with cascade delete
    customer = db.relationship('User', foreign_keys=[customer_id], back_populates='projects_created')
    manager = db.relationship('User', foreign_keys=[manager_id], back_populates='managed_projects')
    tasks = db.relationship('Task', back_populates='project', lazy=True, cascade='all, delete-orphan')
    team_members = db.relationship('TeamMember', back_populates='project', lazy=True, cascade='all, delete-orphan')
    milestones = db.relationship('Milestone', back_populates='project', lazy=True, cascade='all, delete-orphan')
    chat_messages = db.relationship('ChatMessage', back_populates='project', lazy=True, cascade='all, delete-orphan')
    
    @property
    def days_remaining(self):
        if self.deadline:
            delta = self.deadline - datetime.utcnow()
            return max(0, delta.days)
        return 0
    
    @property
    def total_tasks(self):
        return len(self.tasks)
    
    @property
    def completed_tasks(self):
        return len([t for t in self.tasks if t.status == 'Completed'])
    
    @property
    def in_progress_tasks(self):
        return len([t for t in self.tasks if t.status == 'In Progress'])
    
    @property
    def pending_tasks(self):
        return len([t for t in self.tasks if t.status == 'Pending'])


class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    role = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), default='Medium')
    status = db.Column(db.String(50), default='Pending')
    progress = db.Column(db.Integer, default=0)
    estimated_hours = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships - defined inside the model with cascade delete
    project = db.relationship('Project', back_populates='tasks')
    assignee = db.relationship('User', foreign_keys=[assignee_id], back_populates='assigned_tasks')
    created_by = db.relationship('User', foreign_keys=[created_by_id], back_populates='created_tasks')
    notes = db.relationship('TaskNote', back_populates='task', lazy=True, cascade='all, delete-orphan')
    dependencies = db.relationship('TaskDependency', foreign_keys='TaskDependency.task_id', back_populates='task', lazy=True)
    
    @property
    def is_overdue(self):
        if self.deadline and self.status != 'Completed':
            return datetime.utcnow() > self.deadline
        return False


class TeamMember(db.Model):
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    project = db.relationship('Project', back_populates='team_members')
    member = db.relationship('User', back_populates='team_assignments')


class Milestone(db.Model):
    __tablename__ = 'milestones'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    progress = db.Column(db.Integer, default=0)
    deadline = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # Relationships
    project = db.relationship('Project', back_populates='milestones')
    
    @property
    def is_completed(self):
        return self.completed_at is not None


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    project = db.relationship('Project', back_populates='chat_messages')
    sender = db.relationship('User', back_populates='messages')
    
    @property
    def sender_name(self):
        return self.sender.name if self.sender else 'Unknown'
    
    @property
    def sender_role(self):
        return self.sender.role if self.sender else 'Unknown'


class TaskNote(db.Model):
    __tablename__ = 'task_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    task = db.relationship('Task', back_populates='notes')
    author = db.relationship('User', back_populates='task_notes')
    
    @property
    def author_name(self):
        return self.author.name if self.author else 'Unknown'


class TaskDependency(db.Model):
    __tablename__ = 'task_dependencies'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    depends_on_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    
    # Relationships
    task = db.relationship('Task', foreign_keys=[task_id], back_populates='dependencies')
