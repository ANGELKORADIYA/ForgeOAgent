#!/bin/bash

# Get selected text from clipboard
SELECTED_TEXT=$(xclip -selection primary -o)

# Check if text was selected
if [ -z "$SELECTED_TEXT" ]; then
    notify-send "Error" "No text selected"
    exit 1
fi

# Call the Python script with selected text
RESULT=$(/home/userpc/workspace/odoo_17/community/odoo_venv_17/bin/python /home/userpc/29/ForgeOAgent/main.py "$SELECTED_TEXT")

# Check if the Python script executed successfully
if [ $? -eq 0 ]; then
    # Copy result to clipboard
    echo "$RESULT" | xclip -selection clipboard
    notify-send "Success" "Enhanced prompt copied to clipboard"
else
    notify-send "Error" "Failed to enhance prompt"
    exit 1
fi