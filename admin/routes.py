import csv
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from scheduler import get_automation_status, set_automation_status, get_schedule, set_schedule
from id_manager import get_all_ids, add_id, edit_id, delete_id, set_id_enabled
from logger import safe_read_json, RESULTS_DIR
from config import CONFIG_DIR
import threading

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
def require_login():
    if request.endpoint and request.endpoint not in ['admin.login', 'admin.ping'] and not request.endpoint.startswith('static'):
        if not session.get('logged_in'):
            return redirect(url_for('admin.login'))

@admin_bp.route('/ping')
def ping():
    # Dedicated microscopic endpoint for cron-job.org to prevent 302 Redirect errors!
    return "OK", 200

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    from config import config
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        error = "Invalid username or password."
    return render_template('login.html', error=error)

@admin_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
def dashboard():
    status = get_automation_status()
    schedule = get_schedule()
    
    # Load batch summary stats
    daily_path = RESULTS_DIR / "daily_summary.json"
    daily = safe_read_json(daily_path, default={
        "total_runs": 0, "completed_runs": 0, 
        "total_id_tests": 0, "passed": 0, "failed": 0
    })
    
    return render_template('dashboard.html', 
                          automation_enabled=status, 
                          schedule=schedule,
                          daily=daily)

@admin_bp.route('/ids')
def manage_ids():
    ids = get_all_ids()
    return render_template('ids.html', ids=ids)

@admin_bp.route('/schedule')
def manage_schedule():
    schedule = get_schedule()
    return render_template('schedule.html', schedule=schedule)

@admin_bp.route('/results')
def results():
    csv_path = RESULTS_DIR / "test_results.csv"
    results_data = []
    
    # Simple CSV read for the UI
    if csv_path.exists():
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                # Reverse to show latest first
                results_data = list(reader)[::-1]
        except Exception as e:
            pass
            
    return render_template('results.html', results=results_data)

# --- API ENDPOINTS ---

@admin_bp.route('/api/toggle_automation', methods=['POST'])
def toggle_automation():
    data = request.json
    enabled = data.get('enabled', False)
    set_automation_status(enabled)
    return jsonify({"success": True, "enabled": enabled})

@admin_bp.route('/api/run_now', methods=['POST'])
def run_now():
    # Start automation batch async to not block UI
    from runner import run_automation_batch
    threading.Thread(target=run_automation_batch, daemon=True, kwargs={'run_type': 'MANUAL'}).start()
    return jsonify({"success": True, "message": "Manual run started."})

@admin_bp.route('/api/ids', methods=['POST'])
def api_add_id():
    data = request.form
    student_id = data.get('student_id')
    enabled = data.get('enabled') == 'on'
    if student_id:
        add_id(student_id.strip(), enabled)
    return redirect(url_for('admin.manage_ids'))

@admin_bp.route('/api/ids/<student_id>/delete', methods=['POST'])
def api_delete_id(student_id):
    delete_id(student_id)
    return redirect(url_for('admin.manage_ids'))

@admin_bp.route('/api/ids/<student_id>/toggle', methods=['POST'])
def api_toggle_id(student_id):
    data = request.json
    enabled = data.get('enabled', False)
    set_id_enabled(student_id, enabled)
    return jsonify({"success": True})

@admin_bp.route('/api/schedule', methods=['POST'])
def api_update_schedule():
    data = request.form
    times_raw = data.get('times', '')
    times = [t.strip() for t in times_raw.split(',') if t.strip()]
    enabled = data.get('enabled') == 'on'
    
    set_schedule(times=times, enabled=enabled, timezone="Asia/Kolkata")
    return redirect(url_for('admin.manage_schedule'))
