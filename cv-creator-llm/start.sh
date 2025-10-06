#!/bin/bash

echo "========================================"
echo "CV Creator using LLMs - Quick Start"
echo "========================================"
echo

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo

# Check if requirements are installed
echo "Checking dependencies..."
if ! pip show fastapi &> /dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo
fi

# Check Ollama
echo "Checking Ollama status..."
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo
    echo "⚠️  WARNING: Ollama may not be running!"
    echo "Please make sure Ollama is started: ollama serve"
    echo
    read -p "Press Enter to continue anyway..."
fi

# Start the application
echo
echo "Starting CV Creator LLM..."
echo
echo "Access the app at: http://localhost:8000"
echo "Press Ctrl+C to stop"
echo
python run.py
