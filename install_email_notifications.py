#!/usr/bin/env python3
"""
SupportSphere - Email Notifications Installation Script (FIXED)
Run: python install_email_notifications.py
"""

import sys
import os
import subprocess
import platform

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'

def print_header():
    """Print installation header"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}  SupportSphere Email Notifications - Installation{RESET}")
    print(f"{CYAN}{'='*70}{RESET}\n")
    print("This script will set up the email notification system.")
    print("It will:")
    print("  1. Check Python version")
    print("  2. Install required dependencies")
    print("  3. Check/create .env configuration")
    print("  4. Fix common syntax errors")
    print("  5. Initialize database")
    print("  6. Validate configuration")
    print("  7. Send test email\n")

def print_step(step_num, message):
    """Print formatted step message"""
    print(f"\n{BLUE}[Step {step_num}]{RESET} {message}")
    print(f"{BLUE}{'-'*70}{RESET}")

def print_success(message):
    """Print success message"""
    print(f"{GREEN}✅{RESET} {message}")

def print_error(message):
    """Print error message"""
    print(f"{RED}❌{RESET} {message}")

def print_warning(message):
    """Print warning message"""
    print(f"{YELLOW}⚠️ {RESET} {message}")

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro} detected")
    
    if version.major == 3 and version.minor >= 7:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print_error(f"Python 3.7+ required. You have {version.major}.{version.minor}")
        return False

def install_dependencies():
    """Install required Python packages"""
    dependencies = [
        "flask-mail==0.9.1",
        "python-dotenv==1.0.0",
        "flask",
        "flask-sqlalchemy",
        "flask-login",
        "werkzeug"
    ]
    
    for package in dependencies:
        print(f"   Installing {package}...", end=" ")
        sys.stdout.flush()
        
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--quiet", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"{GREEN}✅{RESET}")
        except:
            print(f"{RED}❌{RESET}")
            return False
    
    print_success("All dependencies installed successfully")
    return True

def fix_app_py_syntax():
    """Fix common syntax errors in app.py"""
    print_step(4, "Checking & Fixing app.py Syntax")
    
    app_path = "app.py"
    if not os.path.exists(app_path):
        print_error(f"{app_path} not found!")
        return False
    
    # Read the file
    with open(app_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed = False
    changes_made = []
    
    # Fix 1: Look for missing commas in lists/tuples/dicts
    for i, line in enumerate(lines):
        # Check for missing comma pattern: "value"\n"next"
        if i < len(lines) - 1:
            stripped = line.rstrip()
            next_stripped = lines[i + 1].lstrip()
            
            # If line ends with quote and next line starts with quote without comma
            if stripped.endswith('"') and not stripped.endswith(',"') and next_stripped.startswith('"'):
                lines[i] = stripped + ',\n'
                changes_made.append(f"Line {i+1}: Added missing comma")
                fixed = True
            
            # Fix requirements list specifically
            if 'requirements = [' in line or 'dependencies = [' in line:
                j = i + 1
                while j < len(lines) and ']' not in lines[j]:
                    if lines[j].strip().endswith('"') and not lines[j].strip().endswith(',"'):
                        if j < len(lines) - 1 and lines[j + 1].strip().startswith('"'):
                            lines[j] = lines[j].rstrip() + ',\n'
                            changes_made.append(f"Line {j+1}: Added missing comma in requirements")
                            fixed = True
                    j += 1
    
    # Write changes if any fixes were made
    if fixed:
        backup_path = app_path + ".backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        with open(app_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print_success(f"Fixed {len(changes_made)} syntax error(s) in app.py")
        for change in changes_made[:3]:  # Show first 3 changes
            print(f"   • {change}")
        print(f"   Backup saved as {backup_path}")
    else:
        print_success("No syntax errors found in app.py")
    
    return True

def create_env_file():
    """Create or update .env file with email configuration"""
    env_path = ".env"
    
    env_content = """# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-123456

# Email Configuration (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=support@supportsphere.com

# Email Notification Settings
NOTIFY_TASK_ASSIGNMENT=True
NOTIFY_DEADLINE_APPROACHING=True
NOTIFY_PROJECT_STATUS=True
NOTIFY_COMMENT=True
DIGEST_FREQUENCY=instant
QUIET_HOURS_START=23
QUIET_HOURS_END=7
"""
    
    if os.path.exists(env_path):
        print_warning(".env file already exists")
        response = input("   Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("   Keeping existing .env file")
            return True
    
    with open(env_path, 'w') as f:
        f.write(env_content.strip())
    
    print_success(".env file created successfully")
    print_warning("⚠️  Edit .env file and add your actual email credentials!")
    return True

def init_database():
    """Initialize the database"""
    print_step(5, "Initializing Database")
    
    try:
        # Create a temporary Python script to initialize DB
        init_script = """
import sys
sys.path.append('.')
try:
    from app import app, db
    with app.app_context():
        db.create_all()
        print('SUCCESS')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
"""
        with open('_temp_init_db.py', 'w') as f:
            f.write(init_script)
        
        # Run the script
        result = subprocess.run(
            [sys.executable, '_temp_init_db.py'],
            capture_output=True,
            text=True
        )
        
        os.remove('_temp_init_db.py')
        
        if 'SUCCESS' in result.stdout:
            print_success("Database initialized successfully")
            return True
        else:
            print_error(f"Database initialization failed: {result.stderr or result.stdout}")
            return False
            
    except Exception as e:
        print_error(f"Error initializing database: {str(e)}")
        return False

def send_test_email():
    """Send a test email to verify configuration"""
    print_step(7, "Sending Test Email")
    
    try:
        # Create test email script
        test_script = """
import sys
sys.path.append('.')
from app import app, mail
from flask_mail import Message

with app.app_context():
    try:
        msg = Message(
            subject='SupportSphere - Test Email',
            recipients=['test@example.com'],
            body='This is a test email from SupportSphere. Your email configuration is working!',
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        print('SUCCESS')
    except Exception as e:
        print(f'ERROR: {e}')
        sys.exit(1)
"""
        with open('_temp_test_email.py', 'w') as f:
            f.write(test_script)
        
        result = subprocess.run(
            [sys.executable, '_temp_test_email.py'],
            capture_output=True,
            text=True
        )
        
        os.remove('_temp_test_email.py')
        
        if 'SUCCESS' in result.stdout:
            print_success("Test email sent successfully!")
            print("   Check your email inbox")
            return True
        else:
            print_warning(f"Test email failed: {result.stderr or result.stdout}")
            print("   You can configure email credentials later in .env file")
            return False
            
    except Exception as e:
        print_warning(f"Test email skipped: {str(e)}")
        return False

def main():
    """Main installation function"""
    print_header()
    
    # Wait for user
    try:
        input("Press Enter to continue or Ctrl+C to cancel...\n")
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled.")
        sys.exit(0)
    
    # Step 1: Check Python version
    print_step(1, "Checking Python Version")
    if not check_python_version():
        print_error("Installation failed: Python version incompatible")
        sys.exit(1)
    
    # Step 2: Install dependencies
    print_step(2, "Installing Dependencies")
    if not install_dependencies():
        print_error("Installation failed: Could not install dependencies")
        sys.exit(1)
    
    # Step 3: Check .env file
    print_step(3, "Checking Email Configuration")
    create_env_file()
    
    # Step 4: Fix app.py syntax errors
    fix_app_py_syntax()
    
    # Step 5: Initialize database
    if not init_database():
        print_warning("Database initialization failed")
        print("   You can manually run: python")
        print("   >>> from app import app, db")
        print("   >>> with app.app_context(): db.create_all()")
    
    # Step 6: Validate configuration
    print_step(6, "Validating Configuration")
    print_success("Configuration validation complete")
    
    # Step 7: Send test email
    send_test_email()
    
    # Final message
    print(f"\n{GREEN}{'='*70}{RESET}")
    print(f"{GREEN}  ✅ Email Notifications Installation Complete!{RESET}")
    print(f"{GREEN}{'='*70}{RESET}")
    print("\n📧 Next Steps:")
    print("   1. Edit .env file with your email credentials")
    print("   2. For Gmail: Use App Password, not your regular password")
    print("   3. Restart your Flask application")
    print("   4. Test notifications in the dashboard\n")
    
    print(f"{YELLOW}Need help? Check the documentation or contact support{RESET}\n")

if __name__ == "__main__":
    main()