import os
import datetime
from flask import Flask, request, render_template_string, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# ----------------- 基础配置 -----------------
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-me-in-production'

basedir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(basedir, 'instance')
if not os.path.exists(instance_dir):
    os.makedirs(instance_dir)

db_path = '/tmp/tbis.db'password_hash = db.Column(db.String(255))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ----------------- 会员数据库模型 -----------------
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10))
    first_name = db.Column(db.String(80), nullable=False)
    middle_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80), nullable=False)
    date_of_birth = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    nationality = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30))
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    position = db.Column(db.String(150))
    institution = db.Column(db.String(200))
    department = db.Column(db.String(200))
    institution_website = db.Column(db.String(200))
    highest_degree = db.Column(db.String(50))
    field_of_study = db.Column(db.String(150))
    graduation_year = db.Column(db.Integer)
    interests = db.Column(db.Text)
    other_interests = db.Column(db.String(300))
    membership_type = db.Column(db.String(50))
    personal_website = db.Column(db.String(200))
    referral_source = db.Column(db.String(100))
    statement = db.Column(db.Text)
    password_hash = db.Column(db.String(128))
    status = db.Column(db.String(20), default='pending')
    member_number = db.Column(db.String(20), unique=True)
    join_date = db.Column(db.Date)
    expire_date = db.Column(db.Date)
    reject_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# ----------------- 会员号生成 -----------------
def generate_member_number():
    current_year = str(datetime.date.today().year)
    prefix = f"TBIS{current_year}"
    last_member = Member.query.filter(
        Member.member_number.like(f"{prefix}%")
    ).order_by(Member.member_number.desc()).first()
    if last_member:
        last_number = int(last_member.member_number[-4:])
        new_number = str(last_number + 1).zfill(4)
    else:
        new_number = '0001'
    return f"{prefix}{new_number}"

# ----------------- 认证装饰器 -----------------
STAFF_USERNAME = 'admin'
STAFF_PASSWORD = '123456'

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('staff_logged_in'):
            return redirect(url_for('staff_login'))
        return f(*args, **kwargs)
    return decorated_function

def member_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('member_logged_in'):
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# ================== HTML 模板 ==================
# 公用组件
NAVBAR_BRAND = '''
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
        <a class="navbar-brand" href="/">
            <img src="https://via.placeholder.com/30x30?text=TB" alt="TBIS Logo" width="30" height="30" class="d-inline-block align-top me-2">
            TBIS Society
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav ms-auto">
                <li class="nav-item"><a class="nav-link" href="/">Member Login</a></li>
                <li class="nav-item"><a class="nav-link" href="/apply">Apply</a></li>
                <li class="nav-item"><a class="nav-link" href="/staff/login">Staff</a></li>
            </ul>
        </div>
    </div>
</nav>
'''

BANNER_HTML = '''
<div class="bg-primary bg-gradient text-white py-5 text-center" style="background: linear-gradient(135deg, #0d6efd, #6610f2); position: relative; overflow: hidden;">
    <div style="position: absolute; top: -50px; right: -50px; opacity: 0.1; font-size: 200px;">TBIS</div>
    <div class="container position-relative">
        <h1 class="display-4 fw-bold">Textile Bioengineering & Informatics Society</h1>
        <p class="lead mb-0">Advancing interdisciplinary research for functional textile products and services</p>
    </div>
</div>
'''

FOOTER_HTML = '''
<footer class="bg-dark text-white text-center py-3 mt-5">
    <div class="container">
        <small>&copy; 2026 TBIS - Textile Bioengineering and Informatics Society. All rights reserved.</small>
    </div>
</footer>
'''

# 会员登录页（首页）
HOME_HTML = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Member Login - TBIS</title>
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.2.3/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #f8f9fa; }}
        .login-card {{ border-radius: 15px; }}
    </style>
</head>
<body>
    {NAVBAR_BRAND}
    {BANNER_HTML}

    <div class="container mt-5" style="max-width: 500px;">
        <div class="card shadow login-card">
            <div class="card-body p-4">
                <h3 class="text-center mb-4">Member Login</h3>
                {{% with messages = get_flashed_messages(with_categories=true) %}}
                  {{% if messages %}}
                    {{% for category, message in messages %}}
                      <div class="alert alert-{{{{ category }}}} alert-dismissible fade show">{{{{ message }}}}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>
                    {{% endfor %}}
                  {{% endif %}}
                {{% endwith %}}
                <form method="POST">
                    <div class="mb-3"><label class="form-label">Email</label><input type="email" name="email" class="form-control" required autofocus></div>
                    <div class="mb-3"><label class="form-label">Password</label><input type="password" name="password" class="form-control" required></div>
                    <button type="submit" class="btn btn-primary w-100 btn-lg">Log In</button>
                </form>
                <div class="text-center mt-3">
                    <span>Don't have an account? <a href="{{{{ url_for('apply_page') }}}}">Apply for Membership</a></span>
                </div>
            </div>
        </div>
    </div>
    {FOOTER_HTML}
    <script src="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.2.3/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# 会员注册页
APPLY_HTML = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Membership Application - TBIS</title>
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.2.3/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .section-title {{ border-left: 4px solid #0d6efd; padding-left: 12px; margin-bottom: 20px; color: #0d6efd; font-weight: 600; }}
        .required:after {{ content: " *"; color: red; }}
        .card {{ border-radius: 15px; }}
    </style>
</head>
<body class="bg-light">
    {NAVBAR_BRAND}
    {BANNER_HTML}

    <div class="container mt-4 mb-5" style="max-width: 900px;">
        <div class="card shadow">
            <div class="card-header bg-primary text-white text-center">
                <h3 class="mb-0">Membership Application</h3>
            </div>
            <div class="card-body">
                {{% with messages = get_flashed_messages(with_categories=true) %}}
                  {{% if messages %}}
                    {{% for category, message in messages %}}
                      <div class="alert alert-{{{{ category }}}} alert-dismissible fade show">{{{{ message }}}}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>
                    {{% endfor %}}
                  {{% endif %}}
                {{% endwith %}}

                <form method="POST" action="{{{{ url_for('apply_submit') }}}}" id="applicationForm">
                    <!-- 1. Personal Information -->
                    <h5 class="section-title">1. Personal Information</h5>
                    <div class="row mb-3">
                        <div class="col-md-2"><label class="form-label">Title</label>
                            <select name="title" class="form-select">
                                <option value="">Select</option><option value="Dr.">Dr.</option><option value="Prof.">Prof.</option>
                                <option value="Mr.">Mr.</option><option value="Ms.">Ms.</option><option value="Mrs.">Mrs.</option>
                            </select>
                        </div>
                        <div class="col-md-5"><label class="form-label required">First Name</label><input type="text" name="first_name" class="form-control" required></div>
                        <div class="col-md-5"><label class="form-label required">Last Name</label><input type="text" name="last_name" class="form-control" required></div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-md-6"><label class="form-label">Middle Name</label><input type="text" name="middle_name" class="form-control"></div>
                        <div class="col-md-6"><label class="form-label required">Date of Birth</label><input type="date" name="date_of_birth" class="form-control" required></div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-md-6"><label class="form-label required">Gender</label>
                            <select name="gender" class="form-select" required>
                                <option value="">Select</option><option value="Male">Male</option><option value="Female">Female</option>
                                <option value="Non-binary">Non-binary</option><option value="Prefer not to say">Prefer not to say</option>
                            </select>
                        </div>
                        <div class="col-md-6"><label class="form-label required">Nationality</label><input type="text" name="nationality" class="form-control" required placeholder="e.g., American, German, Japanese"></div>
                    </div>

                    <!-- 2. Contact Information -->
                    <h5 class="section-title">2. Contact Information</h5>
                    <div class="row mb-3">
                        <div class="col-md-6"><label class="form-label required">Email</label><input type="email" name="email" class="form-control" required></div>
                        <div class="col-md-6"><label class="form-label">Phone</label><input type="text" name="phone" class="form-control" placeholder="+1 234 567 8900"></div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label required">Current Address</label>
                        <input type="text" name="address_line1" class="form-control mb-2" required placeholder="Street address">
                        <input type="text" name="address_line2" class="form-control" placeholder="Apartment, suite, etc. (optional)">
                    </div>
                    <div class="row mb-3">
                        <div class="col-md-4"><label class="form-label required">City</label><input type="text" name="city" class="form-control" required></div>
                        <div class="col-md-4"><label class="form-label">State/Province</label><input type="text" name="state" class="form-control"></div>
                        <div class="col-md-4"><label class="form-label required">Country</label><input type="text" name="country" class="form-control" required></div>
                    </div>

                    <!-- 3. Professional Information -->
                    <h5 class="section-title">3. Professional Information</h5>
                    <div class="row mb-3">
                        <div class="col-md-6"><label class="form-label required">Current Position</label><input type="text" name="position" class="form-control" required></div>
                        <div class="col-md-6"><label class="form-label required">Institution</label><input type="text" name="institution" class="form-control" required></div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-md-6"><label class="form-label required">Department</label><input type="text" name="department" class="form-control" required></div>
                        <div class="col-md-6"><label class="form-label">Institution Website</label><input type="url" name="institution_website" class="form-control" placeholder="https://www.example.edu"></div>
                    </div>

                    <!-- 4. Academic Background -->
                    <h5 class="section-title">4. Academic Background</h5>
                    <div class="mb-3"><label class="form-label required">Highest Degree</label>
                        <select name="highest_degree" class="form-select" required>
                            <option value="">Select</option><option value="Bachelor">Bachelor's</option><option value="Master">Master's</option>
                            <option value="PhD">Ph.D.</option><option value="MD">M.D.</option><option value="Postdoctoral">Postdoctoral</option><option value="Other">Other</option>
                        </select>
                    </div>
                    <div class="row mb-3">
                        <div class="col-md-6"><label class="form-label">Field of Study</label><input type="text" name="field_of_study" class="form-control"></div>
                        <div class="col-md-6"><label class="form-label">Year of Graduation</label><input type="number" name="graduation_year" class="form-control" min="1950" max="2030"></div>
                    </div>

                    <!-- 5. Research Interests -->
                    <h5 class="section-title">5. Research & Professional Interests</h5>
                    <div class="mb-3">
                        <label class="form-label">Areas of Expertise (select all that apply)</label>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-check"><input class="form-check-input" type="checkbox" name="interests" value="Textile Bioengineering"><label class="form-check-label">Textile Bioengineering</label></div>
                                <div class="form-check"><input class="form-check-input" type="checkbox" name="interests" value="Functional Fibers & Materials"><label class="form-check-label">Functional Fibers & Materials</label></div>
                                <div class="form-check"><input class="form-check-input" type="checkbox" name="interests" value="Medical Textiles"><label class="form-check-label">Medical Textiles</label></div>
                                <div class="form-check"><input class="form-check-input" type="checkbox" name="interests" value="Protective Textiles"><label class="form-check-label">Protective Textiles</label></div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-check"><input class="form-check-input" type="checkbox" name="interests" value="Sport & Performance Textiles"><label class="form-check-label">Sport & Performance Textiles</label></div>
                                <div class="form-check"><input class="form-check-input" type="checkbox" name="interests" value="Smart & Wearable Textiles"><label class="form-check-label">Smart & Wearable Textiles</label></div>
                                <div class="form-check"><input class="form-check-input" type="checkbox" name="interests" value="Textile Quality & Standards"><label class="form-check-label">Textile Quality & Standards</label></div>
                                <div class="form-check"><input class="form-check-input" type="checkbox" name="interests" value="Sustainable Textiles"><label class="form-check-label">Sustainable Textiles</label></div>
                            </div>
                        </div>
                    </div>
                    <div class="mb-3"><label class="form-label">Other Research Interests</label><input type="text" name="other_interests" class="form-control" placeholder="e.g., textile biotechnology, fiber engineering, smart clothing"></div>

                    <!-- 6. Membership Type -->
                    <h5 class="section-title">6. Membership Type</h5>
                    <div class="mb-3">
                        <select name="membership_type" class="form-select" required>
                            <option value="">Select membership type</option>
                            <option value="Regular">Regular Member ($150/year)</option>
                            <option value="Student">Student Member ($50/year)</option>
                            <option value="Early Career">Early Career Researcher ($75/year)</option>
                            <option value="Emeritus">Emeritus Member ($100/year)</option>
                        </select>
                        <small class="text-muted">Student members must provide proof of enrollment</small>
                    </div>

                    <!-- 7. Account Password -->
                    <h5 class="section-title">7. Create Your Account</h5>
                    <p class="text-muted small">Set a password so you can log in to check your application status and membership details later.</p>
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <label class="form-label required">Password (min. 8 characters)</label>
                            <input type="password" name="password" class="form-control" required minlength="8">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label required">Confirm Password</label>
                            <input type="password" name="confirm_password" class="form-control" required minlength="8">
                        </div>
                    </div>

                    <!-- 8. Optional Information -->
                    <h5 class="section-title">8. Additional Information (Optional)</h5>
                    <div class="mb-3"><label class="form-label">Personal Website / ORCID / Google Scholar</label><input type="url" name="personal_website" class="form-control" placeholder="https://orcid.org/0000-0000-0000-0000"></div>
                    <div class="mb-3"><label class="form-label">How did you hear about TBIS?</label>
                        <select name="referral_source" class="form-select">
                            <option value="">Select</option><option value="Conference">Conference/Event</option><option value="Colleague">Colleague Recommendation</option>
                            <option value="Journal">Journal/Publication</option><option value="Social Media">Social Media</option><option value="Website">Website</option><option value="Other">Other</option>
                        </select>
                    </div>
                    <div class="mb-3"><label class="form-label">Brief Statement of Interest</label><textarea name="statement" class="form-control" rows="3" placeholder="Why do you want to join TBIS?"></textarea></div>
                    <div class="mb-3 form-check">
                        <input type="checkbox" name="agree_terms" class="form-check-input" required>
                        <label class="form-check-label">I agree to the <a href="#" target="_blank">Terms and Conditions</a> and <a href="#" target="_blank">Code of Conduct</a> of TBIS</label>
                    </div>

                    <button type="submit" class="btn btn-primary w-100 btn-lg">Submit Application</button>
                </form>
            </div>
        </div>
    </div>
    {FOOTER_HTML}
    <script>
        document.getElementById('applicationForm').addEventListener('submit', function(e) {{
            const email = document.querySelector('[name="email"]').value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {{
                e.preventDefault();
                alert('Please enter a valid email address.');
                return false;
            }}
            const pwd = document.querySelector('[name="password"]').value;
            const confirmPwd = document.querySelector('[name="confirm_password"]').value;
            if (pwd !== confirmPwd) {{
                e.preventDefault();
                alert('Passwords do not match.');
                return false;
            }}
        }});
    </script>
</body>
</html>
'''

# 员工登录页
STAFF_LOGIN_HTML = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Staff Login - TBIS</title>
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.2.3/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    {NAVBAR_BRAND}
    {BANNER_HTML}
    <div class="container mt-5" style="max-width: 400px;">
        <div class="card shadow">
            <div class="card-header bg-dark text-white"><h5 class="mb-0">Staff Login</h5></div>
            <div class="card-body">
                {{% with messages = get_flashed_messages(with_categories=true) %}}
                  {{% if messages %}}
                    {{% for category, message in messages %}}
                      <div class="alert alert-{{{{ category }}}}">{{{{ message }}}}</div>
                    {{% endfor %}}
                  {{% endif %}}
                {{% endwith %}}
                <form method="POST">
                    <div class="mb-3"><label class="form-label">Username</label><input type="text" name="username" class="form-control" required autofocus></div>
                    <div class="mb-3"><label class="form-label">Password</label><input type="password" name="password" class="form-control" required></div>
                    <button type="submit" class="btn btn-dark w-100">Log In</button>
                </form>
                <div class="text-center mt-3"><a href="/">← Back to Member Login</a></div>
            </div>
        </div>
    </div>
    {FOOTER_HTML}
</body>
</html>
'''

# 员工审核面板
DASHBOARD_HTML = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Application Review - TBIS Admin</title>
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.2.3/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .member-detail {{ font-size: 0.9rem; }}
        .badge {{ font-size: 0.85rem; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/staff">TBIS Admin</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{{{{ url_for('staff_logout') }}}}">Logout</a>
            </div>
        </div>
    </nav>
    <div class="container-fluid mt-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h3>Membership Applications</h3>
            <div class="btn-group">
                <a href="?status=pending" class="btn btn-outline-primary {{{{ 'active' if status=='pending' }}}}">Pending</a>
                <a href="?status=approved" class="btn btn-outline-success {{{{ 'active' if status=='approved' }}}}">Approved</a>
                <a href="?status=rejected" class="btn btn-outline-danger {{{{ 'active' if status=='rejected' }}}}">Rejected</a>
                <a href="?status=all" class="btn btn-outline-secondary {{{{ 'active' if status=='all' }}}}">All</a>
            </div>
        </div>

        {{% with messages = get_flashed_messages(with_categories=true) %}}
          {{% if messages %}}
            {{% for category, message in messages %}}
              <div class="alert alert-{{{{ category }}}} alert-dismissible fade show">{{{{ message }}}}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>
            {{% endfor %}}
          {{% endif %}}
        {{% endwith %}}

        <div class="table-responsive">
            <table class="table table-bordered table-hover">
                <thead class="table-light">
                    <tr><th>ID</th><th>Name</th><th>Email</th><th>Institution</th><th>Position</th><th>Country</th><th>Membership</th><th>Status</th><th>Applied</th><th>Actions</th></tr>
                </thead>
                <tbody>
                    {{% for m in members %}}
                    <tr>
                        <td>{{{{ m.id }}}}</td>
                        <td><strong>{{{{ m.title }}}} {{{{ m.first_name }}}} {{{{ m.last_name }}}}</strong></td>
                        <td>{{{{ m.email }}}}</td>
                        <td class="member-detail">{{{{ m.institution }}}}</td>
                        <td>{{{{ m.position }}}}</td>
                        <td>{{{{ m.country }}}}</td>
                        <td>{{{{ m.membership_type }}}}</td>
                        <td>
                            {{% if m.status == 'pending' %}}
                            <span class="badge bg-warning text-dark">Pending</span>
                            {{% elif m.status == 'approved' %}}
                            <span class="badge bg-success">Approved<br><small>{{{{ m.member_number }}}}</small></span>
                            {{% else %}}
                            <span class="badge bg-danger">Rejected</span>
                            {{% endif %}}
                        </td>
                        <td>{{{{ m.created_at.strftime('%Y-%m-%d') if m.created_at else '-' }}}}</td>
                        <td>
                            {{% if m.status == 'pending' %}}
                            <div class="btn-group-vertical btn-group-sm">
                                <button type="button" class="btn btn-info btn-sm mb-1" data-bs-toggle="modal" data-bs-target="#detailModal{{{{ m.id }}}}">View Details</button>
                                <form method="POST" action="{{{{ url_for('review', member_id=m.id, action='approve') }}}}"><button type="submit" class="btn btn-success btn-sm mb-1 w-100">Approve</button></form>
                                <button type="button" class="btn btn-danger btn-sm w-100" data-bs-toggle="modal" data-bs-target="#rejectModal{{{{ m.id }}}}">Reject</button>
                            </div>
                            <!-- Detail Modal -->
                            <div class="modal fade" id="detailModal{{{{ m.id }}}}">
                                <div class="modal-dialog modal-lg"><div class="modal-content">
                                    <div class="modal-header"><h5 class="modal-title">Application Details - {{{{ m.first_name }}}} {{{{ m.last_name }}}}</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
                                    <div class="modal-body">
                                        <div class="row">
                                            <div class="col-md-6">
                                                <p><strong>Full Name:</strong> {{{{ m.title }}}} {{{{ m.first_name }}}} {{{{ m.middle_name }}}} {{{{ m.last_name }}}}</p>
                                                <p><strong>Date of Birth:</strong> {{{{ m.date_of_birth }}}}</p>
                                                <p><strong>Gender:</strong> {{{{ m.gender }}}}</p>
                                                <p><strong>Nationality:</strong> {{{{ m.nationality }}}}</p>
                                                <p><strong>Email:</strong> {{{{ m.email }}}}</p>
                                                <p><strong>Phone:</strong> {{{{ m.phone or 'N/A' }}}}</p>
                                            </div>
                                            <div class="col-md-6">
                                                <p><strong>Institution:</strong> {{{{ m.institution }}}}</p>
                                                <p><strong>Department:</strong> {{{{ m.department }}}}</p>
                                                <p><strong>Position:</strong> {{{{ m.position }}}}</p>
                                                <p><strong>Highest Degree:</strong> {{{{ m.highest_degree }}}}</p>
                                                <p><strong>Field of Study:</strong> {{{{ m.field_of_study or 'N/A' }}}}</p>
                                                <p><strong>Country:</strong> {{{{ m.country }}}}</p>
                                            </div>
                                        </div>
                                        <hr>
                                        <p><strong>Research Interests:</strong> {{{{ m.interests or 'N/A' }}}}</p>
                                        <p><strong>Membership Type:</strong> {{{{ m.membership_type }}}}</p>
                                        <p><strong>Personal Website:</strong> {{{{ m.personal_website or 'N/A' }}}}</p>
                                        <p><strong>How heard about TBIS:</strong> {{{{ m.referral_source or 'N/A' }}}}</p>
                                        {{% if m.statement %}}<p><strong>Statement:</strong><br>{{{{ m.statement }}}}</p>{{% endif %}}
                                    </div>
                                </div></div>
                            </div>
                            <!-- Reject Modal -->
                            <div class="modal fade" id="rejectModal{{{{ m.id }}}}">
                                <div class="modal-dialog"><div class="modal-content">
                                    <form method="POST" action="{{{{ url_for('review', member_id=m.id, action='reject') }}}}">
                                        <div class="modal-header"><h5 class="modal-title">Reject Application - {{{{ m.first_name }}}} {{{{ m.last_name }}}}</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
                                        <div class="modal-body"><div class="mb-3"><label class="form-label">Reason for Rejection</label><textarea class="form-control" name="reject_reason" rows="3"></textarea></div></div>
                                        <div class="modal-footer"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button><button type="submit" class="btn btn-danger">Confirm Rejection</button></div>
                                    </form>
                                </div></div>
                            </div>
                            {{% elif m.status == 'rejected' %}}
                            <small class="text-danger">Reason: {{{{ m.reject_reason }}}}</small>
                            {{% else %}}
                            <small>Member since: {{{{ m.join_date }}}}<br>Expires: {{{{ m.expire_date }}}}</small>
                            {{% endif %}}
                        </td>
                    </tr>
                    {{% else %}}
                    <tr><td colspan="10" class="text-center text-muted">No applications found</td></tr>
                    {{% endfor %}}
                </tbody>
            </table>
        </div>
    </div>
    <script src="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.2.3/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# 会员中心
MEMBER_DASHBOARD_HTML = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>My Membership - TBIS</title>
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.2.3/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {NAVBAR_BRAND}
    <div class="container mt-4">
        {{% with messages = get_flashed_messages(with_categories=true) %}}
          {{% if messages %}}
            {{% for category, message in messages %}}
              <div class="alert alert-{{{{ category }}}}">{{{{ message }}}}</div>
            {{% endfor %}}
          {{% endif %}}
        {{% endwith %}}

        <h3>Your Membership Status</h3>
        <div class="card mb-4">
            <div class="card-body">
                <p><strong>Name:</strong> {{{{ member.title }}}} {{{{ member.first_name }}}} {{{{ member.last_name }}}}</p>
                <p><strong>Email:</strong> {{{{ member.email }}}}</p>
                <p><strong>Application Status:</strong> 
                    {{% if member.status == 'pending' %}}<span class="badge bg-warning text-dark">Pending Review</span>
                    {{% elif member.status == 'approved' %}}<span class="badge bg-success">Approved</span>
                    {{% else %}}<span class="badge bg-danger">Rejected</span>{{% endif %}}
                </p>
                {{% if member.status == 'approved' %}}
                <p><strong>Member ID:</strong> {{{{ member.member_number }}}}</p>
                <p><strong>Join Date:</strong> {{{{ member.join_date }}}}</p>
                <p><strong>Membership Expires:</strong> {{{{ member.expire_date }}}}</p>
                {{% endif %}}
                {{% if member.status == 'rejected' %}}<p class="text-danger"><strong>Reason:</strong> {{{{ member.reject_reason }}}}</p>{{% endif %}}
            </div>
        </div>
        {{% if member.status == 'approved' %}}
        <div class="card">
            <div class="card-header">Your Certificate</div>
            <div class="card-body">
                <p>Your digital membership certificate is ready.</p>
                <button class="btn btn-primary" disabled>Download Certificate (PDF coming soon)</button>
            </div>
        </div>
        {{% endif %}}
    </div>
    {FOOTER_HTML}
</body>
</html>
'''

# ================== 路由 ==================
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        member = Member.query.filter_by(email=email).first()
        if member and check_password_hash(member.password_hash, password):
            session['member_logged_in'] = True
            session['member_id'] = member.id
            flash(f'Welcome back, {member.first_name}!', 'success')
            return redirect(url_for('member_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template_string(HOME_HTML)

@app.route('/apply')
def apply_page():
    return render_template_string(APPLY_HTML)

@app.route('/apply/submit', methods=['POST'])
def apply_submit():
    interests_list = request.form.getlist('interests')
    interests_str = ', '.join(interests_list) if interests_list else ''

    email = request.form.get('email', '').strip()
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()

    if not first_name or not last_name or not email:
        flash('First Name, Last Name, and Email are required.', 'danger')
        return redirect(url_for('apply_page'))

    if not request.form.get('agree_terms'):
        flash('You must agree to the Terms and Conditions.', 'danger')
        return redirect(url_for('apply_page'))

    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    if len(password) < 8:
        flash('Password must be at least 8 characters long.', 'danger')
        return redirect(url_for('apply_page'))
    if password != confirm_password:
        flash('Passwords do not match.', 'danger')
        return redirect(url_for('apply_page'))

    existing = Member.query.filter_by(email=email).first()
    if existing:
        flash('This email is already registered. Please log in or use a different email.', 'warning')
        return redirect(url_for('apply_page'))

    try:
        new_member = Member(
            title=request.form.get('title', '').strip(),
            first_name=first_name,
            middle_name=request.form.get('middle_name', '').strip(),
            last_name=last_name,
            date_of_birth=request.form.get('date_of_birth', '').strip(),
            gender=request.form.get('gender', '').strip(),
            nationality=request.form.get('nationality', '').strip(),
            email=email,
            phone=request.form.get('phone', '').strip(),
            address_line1=request.form.get('address_line1', '').strip(),
            address_line2=request.form.get('address_line2', '').strip(),
            city=request.form.get('city', '').strip(),
            state=request.form.get('state', '').strip(),
            country=request.form.get('country', '').strip(),
            position=request.form.get('position', '').strip(),
            institution=request.form.get('institution', '').strip(),
            department=request.form.get('department', '').strip(),
            institution_website=request.form.get('institution_website', '').strip(),
            highest_degree=request.form.get('highest_degree', '').strip(),
            field_of_study=request.form.get('field_of_study', '').strip(),
            graduation_year=request.form.get('graduation_year', type=int),
            interests=interests_str,
            other_interests=request.form.get('other_interests', '').strip(),
            membership_type=request.form.get('membership_type', '').strip(),
            personal_website=request.form.get('personal_website', '').strip(),
            referral_source=request.form.get('referral_source', '').strip(),
            statement=request.form.get('statement', '').strip(),
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_member)
        db.session.commit()
        flash('Application submitted! You can log in with your email and password to check status.', 'success')
    except Exception as e:
        flash('An error occurred. Please try again.', 'danger')
        print(f"Error: {e}")

    return redirect(url_for('apply_page'))

# 员工登录
@app.route('/staff/login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == STAFF_USERNAME and password == STAFF_PASSWORD:
            session['staff_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template_string(STAFF_LOGIN_HTML)

@app.route('/staff/logout')
def staff_logout():
    session.pop('staff_logged_in', None)
    flash('Logged out.', 'info')
    return redirect(url_for('staff_login'))

@app.route('/staff')
@staff_required
def dashboard():
    status_filter = request.args.get('status', 'pending')
    keyword = request.args.get('keyword', '').strip()
    search_by = request.args.get('search_by', 'name')  # 默认按姓名

    # 基础查询：按状态过滤
    if status_filter == 'all':
        query = Member.query
    else:
        query = Member.query.filter_by(status=status_filter)

    # 关键词模糊搜索
    if keyword:
        if search_by == 'name':
            query = query.filter(
                db.or_(
                    Member.first_name.ilike(f'%{keyword}%'),
                    Member.last_name.ilike(f'%{keyword}%')
                )
            )
        elif search_by == 'email':
            query = query.filter(Member.email.ilike(f'%{keyword}%'))
        elif search_by == 'institution':
            query = query.filter(Member.institution.ilike(f'%{keyword}%'))
        elif search_by == 'member_number':
            query = query.filter(Member.member_number.ilike(f'%{keyword}%'))
        else:
            # 默认仍按姓名
            query = query.filter(
                db.or_(
                    Member.first_name.ilike(f'%{keyword}%'),
                    Member.last_name.ilike(f'%{keyword}%')
                )
            )

    members = query.order_by(Member.created_at.desc()).all()
    return render_template_string(
        DASHBOARD_HTML,
        members=members,
        status=status_filter,
        keyword=keyword,
        search_by=search_by
    )

@app.route('/staff/review/<int:member_id>/<action>', methods=['POST'])
@staff_required
def review(member_id, action):
    member = Member.query.get_or_404(member_id)
    if member.status != 'pending':
        flash('Application already processed.', 'warning')
        return redirect(url_for('dashboard'))

    if action == 'approve':
        member.status = 'approved'
        member.member_number = generate_member_number()
        member.join_date = datetime.date.today()
        member.expire_date = member.join_date + datetime.timedelta(days=365)
        flash(f'Approved: {member.first_name} {member.last_name} - ID: {member.member_number}', 'success')
    elif action == 'reject':
        reason = request.form.get('reject_reason', '').strip()
        member.status = 'rejected'
        member.reject_reason = reason or 'No reason provided'
        flash(f'Rejected: {member.first_name} {member.last_name}', 'info')
    else:
        flash('Invalid action.', 'danger')
        return redirect(url_for('dashboard'))

    db.session.commit()
    return redirect(url_for('dashboard'))

# 会员登录（重定向到首页）
@app.route('/member/login', methods=['GET', 'POST'])
def member_login_redirect():
    return redirect(url_for('home'))

@app.route('/member/logout')
def member_logout():
    session.pop('member_logged_in', None)
    session.pop('member_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/member/dashboard')
@member_required
def member_dashboard():
    member = Member.query.get(session.get('member_id'))
    if not member:
        session.clear()
        flash('Session expired, please login again.', 'warning')
        return redirect(url_for('home'))
    return render_template_string(MEMBER_DASHBOARD_HTML, member=member)

# ----------------- 启动 -----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    app.run(debug=True, host='0.0.0.0', port=5000)