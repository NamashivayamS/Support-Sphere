from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supportspherekey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --------------------
# Database Models
# --------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))  
    # roles: customer, agent, manager

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    subject = db.Column(db.String(200), default='')  # Make optional with default
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default="Open")  
    priority = db.Column(db.String(20), default="medium")  # Make optional with default
    # Open, In Progress, Closed, Overdue

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sla_deadline = db.Column(db.DateTime)

    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    agent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Add relationships for easier access
    customer = db.relationship('User', foreign_keys=[customer_id], backref='customer_tickets')
    agent = db.relationship('User', foreign_keys=[agent_id], backref='agent_tickets')
    
    @property
    def customer_name(self):
        return self.customer.name if self.customer else "Unknown"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Custom template filter for date formatting
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    if format == 'medium':
        format='%Y-%m-%d %H:%M'
    return value.strftime(format) if value else ""

# --------------------
# Routes
# --------------------

@app.route('/')
def home():
    return redirect(url_for('login'))

# Register
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # Handle both old and new form field names
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        name = request.form.get('name', f"{first_name} {last_name}".strip())
        
        # If name is still empty, use email prefix
        if not name:
            name = request.form['email'].split('@')[0]
            
        user = User(
            name=name,
            email=request.form['email'],
            password=request.form['password'],
            role=request.form.get('role', 'customer')  # Default to customer if no role specified
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email'], password=request.form['password']).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    # SLA overdue auto-detection
    now = datetime.utcnow()
    overdue_tickets = Ticket.query.filter(Ticket.status != "Closed", Ticket.sla_deadline < now).all()
    for t in overdue_tickets:
        t.status = "Overdue"
    db.session.commit()

    # Role-based view
    if current_user.role == "customer":
        tickets = Ticket.query.filter_by(customer_id=current_user.id).all()
        recent_tickets = tickets[:5]  # Show last 5 tickets
        stats = {
            'open_tickets': len([t for t in tickets if t.status == "Open"]),
            'avg_response_time': '2.5',
            'resolved_month': len([t for t in tickets if t.status == "Closed"]),
            'satisfaction_score': '4.2'
        }
    elif current_user.role == "agent":
        tickets = Ticket.query.filter_by(agent_id=current_user.id).all()
        recent_tickets = tickets[:5]
        stats = {
            'assigned_tickets': len([t for t in tickets if t.status in ["Open", "In Progress"]]),
            'sla_compliance': 85,
            'resolved_week': len([t for t in tickets if t.status == "Closed"]),
            'avg_rating': '4.1'
        }
    else:  # manager
        tickets = Ticket.query.all()
        recent_tickets = tickets[:5]
        agents = User.query.filter_by(role="agent").all()
        stats = {
            'total_open': len([t for t in tickets if t.status == "Open"]),
            'team_sla': 82,
            'active_agents': len([a for a in agents]),
            'total_agents': len(agents),
            'avg_resolution': '4.2'
        }

    # Mock SLA status data
    sla_status = [
        {'name': 'Response Time', 'compliance': 85, 'description': 'First response within 2 hours'},
        {'name': 'Resolution Time', 'compliance': 78, 'description': 'Issue resolved within 24 hours'},
    ]

    return render_template(
        'dashboard.html',
        recent_tickets=recent_tickets,
        stats=stats,
        sla_status=sla_status
    )

@app.route('/assign_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def assign_ticket(ticket_id):
    if current_user.role != "manager":
        return redirect(url_for('dashboard'))

    agent_id = request.form['agent_id']
    ticket = Ticket.query.get(ticket_id)
    ticket.agent_id = agent_id
    ticket.status = "In Progress"
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/update_status/<int:ticket_id>', methods=['POST'])
@login_required
def update_status(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    ticket.status = request.form['status']
    db.session.commit()
    return redirect(url_for('dashboard'))

# Create Ticket (Customer)
@app.route('/create_ticket', methods=['POST'])
@login_required
def create_ticket():
    sla_time = datetime.utcnow() + timedelta(hours=48)  # 48 hour SLA
    ticket = Ticket(
        title=request.form['title'],
        subject=request.form.get('subject', request.form['title']),  # Use title as subject if not provided
        description=request.form['description'],
        priority=request.form.get('priority', 'medium'),
        customer_id=current_user.id,
        sla_deadline=sla_time
    )
    db.session.add(ticket)
    db.session.commit()
    return redirect(url_for('dashboard'))

# Logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Missing routes that are referenced in templates
@app.route('/tickets')
@login_required
def tickets():
    # Role-based ticket view
    if current_user.role == "customer":
        tickets = Ticket.query.filter_by(customer_id=current_user.id).all()
    elif current_user.role == "agent":
        tickets = Ticket.query.filter_by(agent_id=current_user.id).all()
    else:  # manager
        tickets = Ticket.query.all()
    
    return render_template('tickets.html', tickets=tickets)

@app.route('/new_ticket', methods=['GET', 'POST'])
@login_required
def new_ticket():
    if request.method == 'POST':
        sla_time = datetime.utcnow() + timedelta(hours=48)  # 48 hour SLA
        ticket = Ticket(
            title=request.form['title'],
            subject=request.form.get('subject', request.form['title']),
            description=request.form['description'],
            priority=request.form.get('priority', 'medium'),
            customer_id=current_user.id,
            sla_deadline=sla_time
        )
        db.session.add(ticket)
        db.session.commit()
        return redirect(url_for('tickets'))
    return render_template('new_ticket.html')

@app.route('/ticket_detail/<int:id>')
@login_required
def ticket_detail(id):
    ticket = Ticket.query.get_or_404(id)
    return render_template('ticket_detail.html', ticket=ticket)

@app.route('/knowledge_base')
@login_required
def knowledge_base():
    return render_template('knowledge_base.html')

@app.route('/agents')
@login_required
def agents():
    if current_user.role != 'manager':
        return redirect(url_for('dashboard'))
    agents = User.query.filter_by(role='agent').all()
    return render_template('agents.html', agents=agents)

@app.route('/sla_management')
@login_required
def sla_management():
    if current_user.role != 'manager':
        return redirect(url_for('dashboard'))
    return render_template('sla_management.html')

@app.route('/reports')
@login_required
def reports():
    if current_user.role != 'manager':
        return redirect(url_for('dashboard'))
    return render_template('reports.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/help')
@login_required
def help():
    return render_template('help.html')

@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # For now, just redirect back with a message
        # In a real app, you'd send a password reset email
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

# --------------------

if __name__ == '__main__':
    with app.app_context():
        # Check if we need to add new columns
        try:
            # Try to query with new columns
            db.session.execute(db.text("SELECT subject, priority FROM ticket LIMIT 1"))
        except Exception:
            # Columns don't exist, add them
            try:
                db.session.execute(db.text("ALTER TABLE ticket ADD COLUMN subject VARCHAR(200) DEFAULT ''"))
                db.session.execute(db.text("ALTER TABLE ticket ADD COLUMN priority VARCHAR(20) DEFAULT 'medium'"))
                db.session.commit()
                print("Added new columns to ticket table")
            except Exception as e:
                print(f"Error adding columns: {e}")
                # If ALTER TABLE fails, recreate the database
                db.drop_all()
                db.create_all()
                print("Recreated database with new schema")
        
        # Ensure tables exist
        db.create_all()
    app.run(debug=True)
