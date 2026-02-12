# Template Updates Required for Auth Improvements

## ⚠️ Important: Update Your HTML Templates

The improved auth routes require a small update to your registration template.

## 1. Register Template (templates/auth/register.html)

### ADD THIS FIELD:
You need to add a password confirmation field to your registration form.

**Add after the password field:**
```html
<!-- Password Confirmation Field (NEW - REQUIRED) -->
<div class="mb-3">
    <label for="confirm_password" class="form-label">Confirm Password</label>
    <input type="password" 
           class="form-control" 
           id="confirm_password" 
           name="confirm_password" 
           required 
           minlength="6"
           placeholder="Re-enter your password">
    <div class="form-text">Please re-enter your password to confirm.</div>
</div>
```

### Complete Registration Form Structure:
```html
<form method="POST" action="{{ url_for('auth.register') }}">
    <!-- Name Field -->
    <div class="mb-3">
        <label for="name" class="form-label">Full Name</label>
        <input type="text" class="form-control" id="name" name="name" required minlength="2">
    </div>
    
    <!-- Email Field -->
    <div class="mb-3">
        <label for="email" class="form-label">Email Address</label>
        <input type="email" class="form-control" id="email" name="email" required>
    </div>
    
    <!-- Password Field -->
    <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" id="password" name="password" required minlength="6">
        <div class="form-text">Minimum 6 characters</div>
    </div>
    
    <!-- Password Confirmation Field (NEW - REQUIRED) -->
    <div class="mb-3">
        <label for="confirm_password" class="form-label">Confirm Password</label>
        <input type="password" class="form-control" id="confirm_password" name="confirm_password" required minlength="6">
        <div class="form-text">Please re-enter your password to confirm.</div>
    </div>
    
    <!-- Role Selection (Optional) -->
    <div class="mb-3">
        <label for="role" class="form-label">Register As</label>
        <select class="form-select" id="role" name="role">
            <option value="customer" selected>Customer</option>
            <option value="team_member">Team Member</option>
            <option value="manager">Manager</option>
        </select>
    </div>
    
    <!-- Submit Button -->
    <button type="submit" class="btn btn-primary w-100">Register</button>
</form>
```

## 2. Login Template (templates/auth/login.html)

### VERIFY THIS FIELD EXISTS:
Your login form should already have a remember me checkbox. Verify it has the correct name attribute:

```html
<div class="mb-3 form-check">
    <input type="checkbox" class="form-check-input" id="remember" name="remember">
    <label class="form-check-label" for="remember">Remember Me</label>
</div>
```

### Complete Login Form Structure:
```html
<form method="POST" action="{{ url_for('auth.login') }}">
    <!-- Email Field -->
    <div class="mb-3">
        <label for="email" class="form-label">Email Address</label>
        <input type="email" class="form-control" id="email" name="email" required>
    </div>
    
    <!-- Password Field -->
    <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" id="password" name="password" required>
    </div>
    
    <!-- Remember Me Checkbox -->
    <div class="mb-3 form-check">
        <input type="checkbox" class="form-check-input" id="remember" name="remember">
        <label class="form-check-label" for="remember">Remember Me</label>
    </div>
    
    <!-- Submit Button -->
    <button type="submit" class="btn btn-primary w-100">Login</button>
    
    <!-- Forgot Password Link -->
    <div class="text-center mt-3">
        <a href="{{ url_for('auth.forgot_password') }}">Forgot Password?</a>
    </div>
</form>
```

## 3. Flash Messages Display

### Ensure your base template has flash message display:

**In templates/base.html (or your layout template):**
```html
<!-- Flash Messages -->
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        <div class="container mt-3">
            {% for category, message in messages %}
                <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            {% endfor %}
        </div>
    {% endif %}
{% endwith %}
```

### Flash Message Categories Used:
- `success` - Green alerts (registration success, login success)
- `danger` - Red alerts (errors, validation failures)
- `info` - Blue alerts (logout, informational messages)
- `warning` - Yellow alerts (not currently used but available)

## 4. Forgot Password Template (templates/auth/forgot_password.html)

### Should already be correct, but verify:
```html
<form method="POST" action="{{ url_for('auth.forgot_password') }}">
    <!-- Email Field -->
    <div class="mb-3">
        <label for="email" class="form-label">Email Address</label>
        <input type="email" class="form-control" id="email" name="email" required>
        <div class="form-text">Enter your registered email address</div>
    </div>
    
    <!-- Submit Button -->
    <button type="submit" class="btn btn-primary w-100">Send Reset Link</button>
    
    <!-- Back to Login Link -->
    <div class="text-center mt-3">
        <a href="{{ url_for('auth.login') }}">Back to Login</a>
    </div>
</form>
```

## Quick Checklist

- [ ] Add `confirm_password` field to register.html
- [ ] Verify `remember` checkbox exists in login.html with correct name attribute
- [ ] Ensure flash messages are displayed in base template
- [ ] Test registration with matching passwords
- [ ] Test registration with mismatched passwords
- [ ] Test login with remember me checked
- [ ] Verify all flash messages display correctly

## Testing Your Templates

After updating templates, test these scenarios:

1. **Register with mismatched passwords** → Should show error: "Passwords do not match"
2. **Register with matching passwords** → Should succeed and redirect to login
3. **Login with remember me checked** → Session should persist after browser restart
4. **Try to access login when already logged in** → Should redirect to dashboard
5. **All flash messages should appear** → Check success, error, and info messages

Your templates are now ready for the improved authentication system! 🎉
