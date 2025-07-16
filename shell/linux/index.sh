#!/bin/bash

# Get selected text from primary clipboard
SELECTED_TEXT=$(xclip -selection primary -o)

# Define Python and script paths dynamically based on current script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="$SCRIPT_DIR/../../.venv/bin/python"
SCRIPT_PATH="$SCRIPT_DIR/../../main.py"

# Get prompt type list using -l and clean the output
PROMPT_TYPES_RAW=$("$PYTHON_BIN" "$SCRIPT_PATH" -l)
PROMPT_TYPES=$(echo "$PROMPT_TYPES_RAW" | grep "_SYSTEM_INSTRUCTION" | sed 's/_SYSTEM_INSTRUCTION$//' | tr '[:upper:]' '[:lower:]')

# Use zenity for graphical prompt selection
SELECTED_TYPE=$(echo "$PROMPT_TYPES" | sed 's/^[-[:space:]]*//' | zenity --list --column="Prompt Types" --title="Select Prompt Type" --height=300)

# User cancelled or closed prompt
if [ -z "$SELECTED_TYPE" ]; then
    notify-send "Cancelled" "No prompt type selected"
    exit 1
fi

# Ensure selected text exists
if [ -z "$SELECTED_TEXT" ]; then
    notify-send "Error" "No text selected"
    exit 1
fi

# Call Python script with selected type and selected text
RESULT=$("$PYTHON_BIN" "$SCRIPT_PATH" -p "$SELECTED_TYPE" "$SELECTED_TEXT")

# Copy to clipboard and notify
if [ $? -eq 0 ]; then
    echo "$RESULT" | xclip -selection clipboard
    notify-send "Success" "Prompt processed and copied to clipboard $SELECTED_TYPE"
else
    notify-send "Error" "Failed to process prompt"
    exit 1
fi
