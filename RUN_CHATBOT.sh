#!/bin/bash
# Easy Chatbot Launcher for Linux/Mac
# Run: bash RUN_CHATBOT.sh

echo "================================================================"
echo "  AI CHATBOT - Starting..."
echo "================================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ first"
    exit 1
fi

# Run the launcher script
python3 run_chatbot.py

echo
read -p "Press Enter to exit..."
