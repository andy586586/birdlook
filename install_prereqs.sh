#!/bin/bash

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found in the current directory. The requirements.txt should be in the github repo."
    exit 1
fi

# Install packages using pip
echo "Installing Python packages from requirements.txt or checking if they're already present..."
pip install -r requirements.txt --user

# Check if the installation was successful
if [ $? -eq 0 ]; then
    echo "Packages installed successfully. App can now run."
    exit 0
else
    echo "Error: Package installation failed."
    exit 1
fi
