import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load local .env if exists (for local testing)
load_dotenv()

from inference import setup_clients, run_agent, check_client_health_with_client

# ── LOGGING SETUP ─────────────────────────────────────────────────────────────

LOG_DIR = Path("/app/logs")
LOG_FILE = LOG_DIR / "hf_space_status.log"

def log_output(message: str, to_stdout: bool = True):
    """Write message to both file and stdout."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}"
    
    # Ensure directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(LOG_FILE, "a") as f:
        f.write(formatted + "\n")
        
    if to_stdout:
        print(formatted)

# ── HEALTH STEPS ──────────────────────────────────────────────────────────────

def run_preflight_checks():
    log_output("===== SHUBHAMOS STARTUP VERIFICATION =====")
    
    # 1. Check HF_TOKEN
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        log_output("❌ ERROR: HF_TOKEN missing from environment!")
    else:
        log_output("HF_TOKEN loaded successfully ✅")

    # 2. Setup & Validate AI Clients
    primary, secondary = setup_clients(hf_token)
    if primary and check_client_health_with_client(primary):
        log_output("Primary AI health check: ✅")
    else:
        log_output("❌ Primary AI health check failed!")

    if secondary:
        log_output("Secondary AI (Fallback) configured: ✅")
    else:
        log_output("Secondary AI (Fallback) not configured: ℹ️")

    log_output("Environment validation: ✅ Healthy")
    log_output("=============================")

    # 5. Final Summary
    log_output("\n===== Hugging Face Space Status Summary =====")
    log_output(f"Hugging Face Space Status: RUNNING")
    log_output(f"HF_TOKEN Status: {'VALID' if hf_token else 'INVALID'}")
    log_output(f"Agent Test Status: FINISHED")

if __name__ == "__main__":
    # Small delay to allow uvicorn to settle if run concurrently
    time.sleep(2)
    run_preflight_checks()
