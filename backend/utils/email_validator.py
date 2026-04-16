"""
Email Configuration Validator
Checks if email settings are properly configured
"""

import os
from dotenv import load_dotenv

load_dotenv()


def validate_email_config():
    """
    Validate email configuration settings
    Returns: (is_valid, messages)
    """
    messages = []
    is_valid = True
    
    # Check required environment variables
    required_vars = {
        'MAIL_SERVER': os.getenv('MAIL_SERVER'),
        'MAIL_PORT': os.getenv('MAIL_PORT'),
        'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
        'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD')
    }
    
    print("=" * 60)
    print("Email Configuration Validation")
    print("=" * 60)
    
    # Check each required variable
    for var_name, var_value in required_vars.items():
        if not var_value:
            messages.append(f"❌ {var_name} is not set")
            is_valid = False
        else:
            # Mask password for security
            if var_name == 'MAIL_PASSWORD':
                display_value = '*' * len(var_value)
            else:
                display_value = var_value
            messages.append(f"✅ {var_name}: {display_value}")
    
    # Check optional variables
    mail_use_tls = os.getenv('MAIL_USE_TLS', 'True')
    mail_use_ssl = os.getenv('MAIL_USE_SSL', 'False')
    mail_sender = os.getenv('MAIL_DEFAULT_SENDER', 'Not set')
    
    messages.append(f"ℹ️  MAIL_USE_TLS: {mail_use_tls}")
    messages.append(f"ℹ️  MAIL_USE_SSL: {mail_use_ssl}")
    messages.append(f"ℹ️  MAIL_DEFAULT_SENDER: {mail_sender}")
    
    # Validate port number
    try:
        port = int(required_vars['MAIL_PORT']) if required_vars['MAIL_PORT'] else 0
        if port not in [25, 465, 587, 2525]:
            messages.append(f"⚠️  Unusual port number: {port} (common ports: 587, 465, 25)")
    except ValueError:
        messages.append(f"❌ MAIL_PORT must be a number")
        is_valid = False
    
    # Check for common configuration issues
    if required_vars['MAIL_SERVER'] == 'smtp.gmail.com':
        messages.append("\n📧 Gmail Configuration Detected:")
        messages.append("   - Ensure 2-Factor Authentication is enabled")
        messages.append("   - Use App Password, not regular password")
        messages.append("   - Generate at: https://myaccount.google.com/apppasswords")
    
    # Print all messages
    print()
    for msg in messages:
        print(msg)
    
    print("\n" + "=" * 60)
    if is_valid:
        print("✅ Configuration appears valid")
        print("   Run 'python manage_notifications.py test-email' to test")
    else:
        print("❌ Configuration has errors")
        print("   Please check your .env file")
    print("=" * 60)
    
    return is_valid, messages


def test_smtp_connection():
    """
    Test SMTP connection without sending email
    """
    import smtplib
    from email.mime.text import MIMEText
    
    print("\nTesting SMTP Connection...")
    print("-" * 60)
    
    server = os.getenv('MAIL_SERVER')
    port = int(os.getenv('MAIL_PORT', 587))
    username = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    use_tls = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    
    try:
        # Connect to server
        print(f"Connecting to {server}:{port}...")
        
        if use_tls:
            smtp = smtplib.SMTP(server, port, timeout=10)
            smtp.starttls()
        else:
            smtp = smtplib.SMTP_SSL(server, port, timeout=10)
        
        print("✅ Connected successfully")
        
        # Try to login
        print(f"Authenticating as {username}...")
        smtp.login(username, password)
        print("✅ Authentication successful")
        
        # Close connection
        smtp.quit()
        print("✅ SMTP connection test passed")
        print("-" * 60)
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed")
        print("   Check your username and password")
        if 'gmail.com' in server:
            print("   For Gmail: Use App Password, not regular password")
        print("-" * 60)
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {str(e)}")
        print("-" * 60)
        return False
        
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        print("   Check MAIL_SERVER and MAIL_PORT settings")
        print("-" * 60)
        return False


if __name__ == '__main__':
    # Run validation
    is_valid, messages = validate_email_config()
    
    # If valid, test connection
    if is_valid:
        print("\nWould you like to test the SMTP connection? (y/n): ", end='')
        response = input().strip().lower()
        if response == 'y':
            test_smtp_connection()
