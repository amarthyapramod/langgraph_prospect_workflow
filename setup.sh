#!/usr/bin/env bash

# Setup script for LangGraph Prospect-to-Lead Workflow
# This script automates the initial setup process

set -e  # Exit on error

echo "=================================="
echo "LangGraph Workflow Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

#if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
#    echo -e "${RED}Error: Python 3.8 or higher is required${NC}"
#    exit 1
#fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
    read -p "Remove and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
    fi
else
    python3 -m venv venv
fi
echo -e "${GREEN}✓ Virtual environment created${NC}"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Setup .env file
echo ""
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file already exists${NC}"
else
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and add your API keys${NC}"
fi

# Create agents directory if it doesn't exist
echo ""
echo "Setting up project structure..."
mkdir -p agents
mkdir -p tests
mkdir -p logs

# Create __init__.py files
touch agents/__init__.py
touch tests/__init__.py

echo -e "${GREEN}✓ Project structure created${NC}"

# Verify workflow.json exists
echo ""
if [ -f "workflow.json" ]; then
    echo -e "${GREEN}✓ workflow.json found${NC}"
else
    echo -e "${RED}✗ workflow.json not found${NC}"
    echo "Please ensure workflow.json is in the project root"
fi

# Summary
echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OpenAI API key"
echo "   OPENAI_API_KEY=sk-your-key-here"
echo ""
echo "2. (Optional) Add other API keys for full functionality:"
echo "   - APOLLO_API_KEY"
echo "   - CLAY_API_KEY"
echo "   - CLEARBIT_KEY"
echo ""
echo "3. Run the workflow:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "4. For help, see:"
echo "   - README.md (full documentation)"
echo "   - QUICKSTART.md (quick start guide)"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"