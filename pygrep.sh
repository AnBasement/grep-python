#!/bin/bash

# Wrapper script that calls the Python implementation
# This allows the program to be called as ./pygrep.sh

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the Python script
python3 "$SCRIPT_DIR/src/main.py" "$@"
