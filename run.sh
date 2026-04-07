#!/bin/bash

# RealE Tube - Launch Script
# Copyright © 2024 RealE Technology Solutions. All rights reserved.

echo "=========================================="
echo "  RealE Tube - YouTube Automation"
echo "  Copyright © 2024 RealE Technology Solutions"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.9 or later from https://www.python.org"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import customtkinter" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Launch application
echo "Launching RealE Tube..."
python3 main.py
