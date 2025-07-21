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

# First get the selection without any custom buttons to ensure we capture the selected item
TEMP_SELECTION=$(echo "$PROMPT_TYPES" | sed 's/^[-[:space:]]*//' | zenity --list \
    --column="Prompt Types" \
    --title="Select Prompt Type" \
    --height=300 2>/dev/null)

# Check if user cancelled the selection
if [ $? -ne 0 ] || [ -z "$TEMP_SELECTION" ]; then
    notify-send "Cancelled" "No prompt type selected"
    exit 1
fi

# Now show action dialog with the selected type
zenity --question \
    --title="Process: $TEMP_SELECTION" \
    --text="How do you want to process '$TEMP_SELECTION'?" \
    --ok-label="Process Normal" \
    --cancel-label="Process New" 2>/dev/null

# Get the exit code to determine which button was pressed
ZENITY_EXIT_CODE=$?

# Handle button selection
case $ZENITY_EXIT_CODE in
    0)  # OK button pressed (Process Normal)
        SELECTED_TYPE="$TEMP_SELECTION"
        USE_NEW_FLAG=""
        BUTTON_TYPE=""
        ;;
    1)  # Cancel button pressed (Process New)
        SELECTED_TYPE="$TEMP_SELECTION"
        USE_NEW_FLAG="--new"
        BUTTON_TYPE="(NEW)"
        ;;
    *)  # Dialog closed with X or ESC
        notify-send "Cancelled" "Dialog cancelled"
        exit 1
        ;;
esac

# Check if a selection was made (this check is now redundant but kept for safety)
if [ -z "$SELECTED_TYPE" ]; then
    notify-send "Cancelled" "No prompt type selected"
    exit 1
fi

# Ensure selected text exists
if [ -z "$SELECTED_TEXT" ]; then
    notify-send "Error" "No text selected"
    exit 1
fi

# Call Python script with selected type, selected text, and optional --new flag
if [ -n "$USE_NEW_FLAG" ]; then
    RESULT=$("$PYTHON_BIN" "$SCRIPT_PATH" -p "$SELECTED_TYPE" "$SELECTED_TEXT" "$USE_NEW_FLAG")
    BUTTON_TYPE="(NEW)"
else
    RESULT=$("$PYTHON_BIN" "$SCRIPT_PATH" -p "$SELECTED_TYPE" "$SELECTED_TEXT")
    BUTTON_TYPE=""
fi

# Copy to clipboard and notify
if [ $? -eq 0 ]; then
    echo "$RESULT" | xclip -selection clipboard
    notify-send "Success" "Prompt processed and copied to clipboard: $SELECTED_TYPE $BUTTON_TYPE"
else
    notify-send "Error" "Failed to process prompt"
    exit 1
fi