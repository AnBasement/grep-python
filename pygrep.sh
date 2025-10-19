#!/bin/bash

# Wrapper script that calls the Python implementation
# This allows the program to be called as ./pygrep.sh

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the Python module from the project directory
cd "$SCRIPT_DIR"
python3 -m src.main "$@"