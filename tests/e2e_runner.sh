#!/bin/bash
# E2E Runner Script for SHUBHAMOS (Phase 8 Validation)

set -e

# Constraints: Read HF_TOKEN or NVIDIA_API_KEY from environment
if [ -z "$HF_TOKEN" ] && [ -z "$NVIDIA_API_KEY" ]; then
    echo "❌ ERROR: Neither HF_TOKEN nor NVIDIA_API_KEY environment variable is set."
    echo "Usage: export HF_TOKEN='...' or export NVIDIA_API_KEY='...' && ./tests/e2e_runner.sh"
    exit 1
fi

mkdir -p logs
mkdir -p tests

SUMMARY_FILE="tests/summary_report.txt"
echo "SHUBHAMOS E2E Validation Report" > $SUMMARY_FILE
echo "===============================" >> $SUMMARY_FILE
date >> $SUMMARY_FILE
echo "" >> $SUMMARY_FILE

# Function to run, validate, and extract metrics for a task
run_and_validate() {
    local task=$1
    local log="logs/${task}.log"
    
    echo "Running E2E for TASK=${task}... (This may take several minutes)"
    # We allow the python script to fail naturally without breaking the wrapper
    python3 -u inference.py --task $task > $log 2>&1 || true

    echo "Analyzing $log..."
    
    # 1. Check for crashes (Traceback)
    if grep -q "Traceback (most recent call last):" "$log"; then
        echo "❌ FAIL: Unhandled Traceback Exception found in log!"
        echo "Task: $task | Status: FAIL | Reason: Runtime Crash" >> $SUMMARY_FILE
        return 1
    fi
    
    # 2. Check for FINAL SCORE signature
    if ! grep -q "FINAL SCORE ($task):" "$log"; then
        echo "❌ FAIL: 'FINAL SCORE ($task):' signature missing from log!"
        echo "Task: $task | Status: FAIL | Reason: Missing Score Output" >> $SUMMARY_FILE
        return 1
    fi
    
    # 3. Extract final score and validate boundaries (0.0 to 1.0)
    local score=$(grep "FINAL SCORE ($task):" "$log" | awk -F': ' '{print $2}')
    local is_valid_score=$(echo "$score" | awk '{if ($1 >= 0.0 && $1 <= 1.0) print "yes"; else print "no"}')

    if [ "$is_valid_score" != "yes" ]; then
        echo "❌ FAIL: Final Score ($score) is outside bound [0.0 - 1.0]!"
        echo "Task: $task | Score: $score | Status: FAIL | Reason: Out of Bounds" >> $SUMMARY_FILE
        return 1
    fi

    # 4. Fallback Metrics extraction
    local total_steps=$(grep -c "^\[STEP " "$log" || echo "0")
    local fallbacks=$(grep -c "^Fallback: YES" "$log" || echo "0")
    
    local fallback_rate=$(awk -v f="$fallbacks" -v t="$total_steps" 'BEGIN { if (t > 0) printf "%.2f", (f / t) * 100; else print "0.00" }')

    echo "✅ PASS: $task executed successfully."
    echo "  - Total Steps: $total_steps"
    echo "  - Fallbacks:   $fallbacks ($fallback_rate%)"
    echo "  - Final Score: $score"
    
    echo "Task: $task | Score: $score | Fallback Rate: $fallback_rate% | Status: PASS" >> $SUMMARY_FILE
    return 0
}

# Run tasks
FAILED=0

run_and_validate "easy"
if [ $? -ne 0 ]; then FAILED=1; fi

echo "-----------------------------------"

run_and_validate "medium"
if [ $? -ne 0 ]; then FAILED=1; fi

echo "==============================="
cat $SUMMARY_FILE

if [ $FAILED -eq 1 ]; then
    echo "❌ E2E Validation Failed."
    exit 1
else
    echo "✅ All E2E checks passed perfectly."
    exit 0
fi
