import argparse
import sys
from logger import logger
from runner import run_automation_batch
from scheduler import Scheduler

def main():
    parser = argparse.ArgumentParser(description="Automated Attendance Tester")
    parser.add_argument("--admin", action="store_true", help="Start the Flask admin dashboard")
    parser.add_argument("--schedule", action="store_true", help="Start the automated scheduler loop")
    parser.add_argument("--run-now", action="store_true", help="Run a manual test cycle immediately")
    parser.add_argument("--dry-run", action="store_true", help="Run a test cycle without clicking submit")
    parser.add_argument("--test-id", type=str, help="Run a test cycle for a specific single ID")
    
    args = parser.parse_args()
    
    if args.admin:
        logger.info("Starting Admin Dashboard...")
        from admin.app import create_app
        app = create_app()
        # use threaded=True by default for Werkzeug to not block our async runs
        app.run(host="127.0.0.1", port=5000, threaded=True)
        
    elif args.schedule:
        logger.info("Starting Background Scheduler...")
        scheduler = Scheduler(run_callback=run_automation_batch)
        scheduler.start()
        
    elif args.run_now:
        logger.info("Triggering Manual Run...")
        run_automation_batch(run_type="MANUAL_CLI", specific_id=args.test_id)
        
    elif args.dry_run:
        logger.info("Triggering DRY RUN...")
        run_automation_batch(run_type="DRY_RUN", dry_run=True, specific_id=args.test_id)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application exited by user.")
        sys.exit(0)
