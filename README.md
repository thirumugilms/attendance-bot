# Automated Attendance Tester

A file-based Python application for automated functional testing of a QR-based attendance workflow using Playwright.

## Architecture

This application does **NOT** use a database. It relies completely on a file-based structure:
- **Configurations and State:** Stored in `config/` (`ids.json`, `schedule.json`, `settings.json`)
- **Results:** Stored in `results/` (`test_results.csv`, `daily_summary.json`)
- **Screenshots:** Stored in `results/screenshots/` (on failure)

### Major Components
1. **Playwright Automation** (`browser.py`, `qr_handler.py`, `attendance.py`, `verifier.py`): Replicates real user action, waits for load states, and verifies the DOM response.
2. **Batch Runner** (`runner.py`): Orchestrates fetching the current active session, iterating over enabled IDs, capturing screenshots, and writing to the CSV and logger.
3. **Admin Dashboard** (`admin/`): A Flask application to visually toggle automation, manage IDs, schedules, and view results.
4. **Scheduler** (`scheduler.py`): A lightweight background loop that checks time schedules every 30s.

---

## Installation & Setup

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies and Playwright browser:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Configure Environment Variables:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   **Important:** You do not add IDs to the `.env` file. You add them via the Flask Dashboard.

---

## Running the Application

This utility is managed via one central CLI script: `main.py`.

### 1. Flask Admin Dashboard
```bash
python main.py --admin
```
- Access it at `http://127.0.0.1:5000`
- From here, you can **Manage Test IDs** (add/remove/enable), configure the **Schedule**, toggle Automation on/off globally, and view **Results**.

### 2. Manual Run
```bash
python main.py --run-now
```
- Will obtain the *current active session URL* through the QR display page, and attempt submission for all enabled IDs.

### 3. Start Background Scheduler
```bash
python main.py --schedule
```
- Must be left running in the background. It will execute `run_now` automatically at the times defined in the schedule (configurable via the UI). 

### 4. Dry Run Mode
```bash
python main.py --dry-run
```
- Simulates the entire browser flow but stops exactly before clicking the real `Submit` button. Critical for verifying your selectors.

### 5. Running Mock Interface for Testing
If you want to test the automation without slamming the real server, start the mock application:
```bash
python tests/mock_app.py
```
- Make sure `.env` contains `DISPLAY_URL=http://localhost:5000/mock-qr`

---

## 🛠️ CRITICAL: Adapting Selectors

Because the real application's structure was not provided, you *must* adapt the Playwright selectors in `config.py` to match the actual application. Look for the `Config` class placeholder:

### 1. `config.py` - Core Selectors
- `QR_SELECTOR`: CSS selector pointing to the QR element on the display screen.
- `QR_DESTINATION_ATTR`: The attribute (e.g., `src` or `data-url`) containing the session link. If the original application doesn't expose this cleanly in the DOM, you must adapt the logic inside `qr_handler.py`.
- `ATTENDANCE_ID_INPUT_SELECTOR`: Selects the input field where the Student ID is pasted.
- `ATTENDANCE_SUBMIT_SELECTOR`: Selects the submit button.
- `SUCCESS_MESSAGE_SELECTOR` / `FAILURE_MESSAGE_SELECTOR`: Selectors used by `verifier.py` to dictate whether a test passed or failed.

### 2. `verifier.py` - Validation Logic
The `verify_response()` function dictates what happens after the Submit button is clicked. It will look for Success or Failure selectors, or fallback to body text parsing. Update its success keywords (`"marked"`, `"success"`) to precisely match your target application.

---

## Result Logging
- Every single ID tested creates an entry in `results/test_results.csv`.
- Each time a batch is finished, `results/daily_summary.json` is updated with aggregate metrics (counts and durations).
- If an individual test fails (FAIL, TIMEOUT, ERROR), Playwright captures a full-page screenshot inside `results/screenshots/`.
