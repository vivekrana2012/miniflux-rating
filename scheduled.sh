#!/bin/bash
# scheduled.sh
# Description: Activates a Python virtual environment and runs the Miniflux rating script.

# Exit immediately if a command exits with a non-zero status
set -e

# Path to your virtual environment (adjust as needed)
VENV_PATH="/home/vivek/Workspace/miniflux-venv"

# Path to your Python script
SCRIPT_PATH="/home/vivek/Workspace/miniflux-rating/miniflux.py"

# Activate the virtual environment
source "${VENV_PATH}/bin/activate"

# Log which Python is being used
echo "[$(date)] Running script with $(which python)"

# Run the Python script and log output
"${VENV_PATH}/bin/python" "${SCRIPT_PATH}"

# Deactivate the venv after running
deactivate

echo "[$(date)] Script execution completed."
