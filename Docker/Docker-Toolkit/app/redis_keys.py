# Single source of truth for all Redis key names.
# Import this in app.py and scanner.py — never hardcode strings elsewhere.

SCAN_QUEUE      = "scan_queue"
SCAN_RESULTS    = "scan_results"
TOTAL_SCANS     = "total_scans"
PENDING_SCANS   = "pending_scans"
RUNNING_SCANS   = "running_scans"
PASSED_SCANS    = "passed_scans"
FAILED_SCANS    = "failed_scans"
ACTIVE_SCANNERS = "active_scanners"
VISITS          = "visits"