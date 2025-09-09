#!/bin/bash

# -----------------------------
# Shell script to run main.py
# using Conda environment in cron
# -----------------------------

# Full path to Conda Python
PYTHON="/opt/anaconda3/envs/quantastic/bin/python"

# Path to your script
SCRIPT="/Users/adnankarol/Desktop/Quantastic/src/main.py"

# Log directory and file
LOG_DIR="/Users/adnankarol/Desktop/Quantastic/logs"
LOG_FILE="$LOG_DIR/alerts.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Add timestamp and run script
echo "----- Script run at $(date) -----" >> "$LOG_FILE"
$PYTHON "$SCRIPT" >> "$LOG_FILE" 2>&1
echo "----- End of run -----" >> "$LOG_FILE"