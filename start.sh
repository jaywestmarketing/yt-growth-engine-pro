#!/bin/bash
# RealE Tube - Quick Start Script
# Installs dependencies and launches the app

cd "$(dirname "$0")"

echo "=================================="
echo "  RealE Tube - Starting Up"
echo "=================================="

# Check for Node.js
if ! command -v node &>/dev/null; then
    echo ""
    echo "Node.js not found. Falling back to browser mode..."
    echo ""
    PYTHON=$(command -v python3.11 || command -v python3.10 || command -v python3.9 || command -v python3 || command -v python)
    if [ -z "$PYTHON" ]; then
        echo "ERROR: Python 3 is required. Install from https://www.python.org/downloads/"
        exit 1
    fi
    echo "Using $PYTHON"
    $PYTHON web_app.py
    exit 0
fi

# Install npm deps if needed
if [ ! -d "node_modules" ]; then
    echo "Installing Electron (first run only)..."
    npm install
fi

# Launch Electron app
echo "Launching RealE Tube..."
npm start
