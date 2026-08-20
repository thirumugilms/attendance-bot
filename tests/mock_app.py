from flask import Flask, request, jsonify, render_template_string
import uuid

app = Flask(__name__)

QR_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Mock QR Display</title></head>
<body>
    <h1>QR Display Dashboard</h1>
    <img id="qr-code" src="{{ session_url }}" alt="QR Code">
    <p>Session ID: {{ session_id }}</p>
</body>
</html>
"""

ATTENDANCE_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Submit Attendance</title></head>
<body>
    <h1>Mark Attendance</h1>
    <form method="POST" action="/submit/{{ session_id }}">
        <input type="text" name="student_id" placeholder="Student ID">
        <button type="submit">Submit</button>
    </form>
</body>
</html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Success</title></head>
<body>
    <div class="alert-success">Attendance marked successfully for {{ student_id }}</div>
</body>
</html>
"""

@app.route('/mock-qr')
def display_qr():
    # Rotate the session occasionally for testing or just generate a live one
    session_id = str(uuid.uuid4())[:8]
    session_url = f"http://localhost:5000/mock-session/{session_id}"
    return render_template_string(QR_PAGE, session_url=session_url, session_id=session_id)

@app.route('/mock-session/<session_id>')
def attendance_form(session_id):
    return render_template_string(ATTENDANCE_PAGE, session_id=session_id)

@app.route('/submit/<session_id>', methods=['POST'])
def submit(session_id):
    student_id = request.form.get('student_id', 'Unknown')
    # Simulate a successful response
    return render_template_string(SUCCESS_PAGE, student_id=student_id)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
