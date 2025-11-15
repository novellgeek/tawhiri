#!/bin/bash
# TAWHIRI Quick Start Script
# Run this to set up the modular template

echo "🛰️  TAWHIRI Space Domain Awareness Platform"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+ first."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Create config.json if it doesn't exist
if [ ! -f "config.json" ]; then
    echo "📝 Creating config.json from example..."
    cp config.example.json config.json
    echo "⚠️  Please edit config.json with your actual paths!"
    echo ""
else
    echo "✓ config.json already exists"
    echo ""
fi

# Create virtual environment (recommended)
read -p "Create Python virtual environment? (recommended) [y/n]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        echo "✓ Virtual environment created"
        echo ""
        echo "To activate it:"
        echo "  Windows: venv\\Scripts\\activate"
        echo "  Linux/Mac: source venv/bin/activate"
        echo ""
    else
        echo "✓ Virtual environment already exists"
        echo ""
    fi
fi

# Install package
read -p "Install TAWHIRI package and dependencies? [y/n]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing package in development mode..."
    pip install -e .
    echo ""
    echo "✓ Installation complete!"
    echo ""
fi

# Create data directories
echo "Creating data directories..."
mkdir -p data/earth data/skyfield_cache data/3d logs
echo "✓ Data directories created"
echo ""

# Run tests
read -p "Run tests to verify installation? [y/n]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running tests..."
    pytest tests/ -v
    echo ""
fi

echo "=========================================="
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.json with your data paths"
echo "2. Copy your data files to the data/ directory"
echo "3. Start migrating your modules (see MIGRATION_GUIDE.md)"
echo ""
echo "Quick test:"
echo "  python -m tawhiri.space_weather.app"
echo "  python -m tawhiri.orbit_viz.app"
echo ""
echo "Documentation:"
echo "  README.md - Project overview"
echo "  MIGRATION_GUIDE.md - How to migrate your code"
echo ""
