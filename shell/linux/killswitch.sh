#!/bin/bash

# Define the path to the Desktop and the hidden file name
DESKTOP_PATH="${HOME}/Desktop"
HIDDEN_FILE="${DESKTOP_PATH}/.killswitch"

# Create the hidden file on the Desktop if it doesn't already exist
if [ ! -f "${HIDDEN_FILE}" ]; then
    # Ensure the Desktop directory exists
    mkdir -p "${DESKTOP_PATH}"
    touch "${HIDDEN_FILE}"
    echo "Hidden file '${HIDDEN_FILE}' created successfully on your Desktop."
else
    echo "Hidden file '${HIDDEN_FILE}' already exists on your Desktop."
fi