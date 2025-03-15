#!/bin/bash
set -e

echo "===== NASA Exoplanet Data Analysis Tool - Installation Script ====="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created successfully."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install required packages
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download NASA exoplanet data
echo "Downloading NASA exoplanet data..."
python src/download_data.py

# Initialize database (assuming you have a script for this)
echo "Initializing database..."
if [ -f "src/init_database.py" ]; then
    python src/init_database.py
else
    echo "Warning: Database initialization script not found."
    echo "You may need to manually set up the database."
fi

echo "===== Installation Complete ====="
echo ""
echo "To run the program:"
echo "1. Make sure you're in the project directory"
echo "2. Activate the virtual environment with: source venv/bin/activate"
echo "3. Run the main script with: python src/app.py"
echo ""
echo "Would you like to run the program now? (y/n) [Y]"
read -r choice
choice=${choice:-y}  # Set default to 'y' if input is empty

if [[ $choice == "y" || $choice == "Y" ]]; then
    if [ -f "src/app.py" ]; then
        echo "Running program..."
        python src/app.py
    else
        echo "Error: Main script not found at src/app.py"
        echo "You may need to specify the correct path to your main script."
    fi
else
    echo "You can run the program later using the instructions above."
fi

# Deactivate virtual environment
deactivate

echo "Script completed."