#!/bin/bash
# VARIOSYNC Setup Script

echo "Setting up VARIOSYNC..."

# Check Python version
python3 --version

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Create config file if it doesn't exist
if [ ! -f config.json ]; then
    echo "Creating config.json from example..."
    cp config.example.json config.json
    echo "✓ Config file created. Edit config.json if needed."
else
    echo "✓ Config file already exists."
fi

# Create data directory
mkdir -p data

echo ""
echo "✓ Setup complete!"
echo ""
echo "To run VARIOSYNC:"
echo "  python3 main.py --process-file sample_data.json"
echo ""
