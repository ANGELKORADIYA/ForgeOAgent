#!/bin/bash

# Get selected text from primary clipboard, handle errors
SELECTED_TEXT=$(xclip -selection primary -o 2>/dev/null || echo "")

# Define Python and script paths dynamically based on current script location
# SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="../../main.py"
SCRIPT_PATH="python"

# Determine context content based on selected text
if [ -n "$SELECTED_TEXT" ]; then
    # Check if selected text is a file path
    if [ -f "$SELECTED_TEXT" ]; then
        # Try to read file content
        if [ -r "$SELECTED_TEXT" ]; then
            CONTEXT_CONTENT=$(cat "$SELECTED_TEXT")
            DISPLAY_INFO="File: $SELECTED_TEXT (content will be used as context)"
        else
            # File not readable, use path only
            CONTEXT_CONTENT="$SELECTED_TEXT"
            DISPLAY_INFO="File: $SELECTED_TEXT (path only - not readable)"
        fi
    else
        # Selected text is not a file, use as-is
        CONTEXT_CONTENT="$SELECTED_TEXT"
        DISPLAY_INFO="Selected text: $SELECTED_TEXT"
    fi
else
    # No selected text
    CONTEXT_CONTENT=""
    DISPLAY_INFO="No text selected. Enter your prompt:"
fi

# Show context preview if there's content, then show input dialog
if [ -n "$CONTEXT_CONTENT" ]; then
    # Show context in scrollable preview window first
    echo "$CONTEXT_CONTENT" | zenity --text-info \
        --title="Context Preview" \
        --width=700 \
        --height=400 \
        --editable=false \
        --ok-label="Continue to Input" > /dev/null 2>&1
    
    # Check if user cancelled the preview
    if [ $? -ne 0 ]; then
        notify-send "Cancelled" "Preview cancelled"
        exit 1
    fi
    
    # Show input dialog
    USER_INPUT=$(zenity --entry \
        --title="Enter Your Prompt" \
        --text="Context loaded. Enter your prompt:" \
        --entry-text="" \
        --width=600)
else
    # No context, show normal input dialog
    USER_INPUT=$(zenity --entry \
        --title="Enter Your Prompt" \
        --text="$DISPLAY_INFO" \
        --entry-text="" \
        --width=600)
fi

# Check if user cancelled the dialog
if [ $? -ne 0 ] || [ -z "$USER_INPUT" ]; then
    notify-send "Cancelled" "No input provided"
    exit 1
fi

# Format the final text: input_text \n <context>selected_text_or_file_content</context>
if [ -n "$CONTEXT_CONTENT" ]; then
    FINAL_TEXT="$USER_INPUT
<context>$CONTEXT_CONTENT</context>"
else
    FINAL_TEXT="$USER_INPUT"
fi

# Call Python script with final text
RESULT=$("$PYTHON_BIN" "$SCRIPT_PATH" "$FINAL_TEXT" --main)

# Display result in a dialog and notify
if [ $? -eq 0 ]; then
    # For long results, use scrollable text-info dialog
    if [ ${#RESULT} -gt 500 ]; then
        echo "$RESULT" | zenity --text-info \
            --title="Result" \
            --width=800 \
            --height=600 \
            --editable=false
    else
        zenity --info --title="Result" --text="$RESULT" --width=600
    fi
    notify-send "Success" "Prompt processed"
else
    notify-send "Error" "Failed to process prompt"
    exit 1
fi