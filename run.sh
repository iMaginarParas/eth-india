#!/bin/bash

# AI Portfolio Agent - Run Script
# Quick script to run the application

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting AI Portfolio Agent...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Run setup.sh first.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating template...${NC}"
    cp .env.example .env 2>/dev/null || echo "THE_GRAPH_API_KEY=your_key_here" > .env
    echo -e "${YELLOW}⚠️  Please edit .env file with your API keys${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ main.py not found in current directory${NC}"
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    echo -e "${BLUE}⚙️  Loading environment variables...${NC}"
    export $(cat .env | grep -v '#' | xargs)
fi

# Run the application
echo -e "${GREEN}✅ Starting FastAPI server...${NC}"
echo -e "${BLUE}📡 Server will be available at: http://localhost:${PORT:-8000}${NC}"
echo -e "${BLUE}📋 API Documentation: http://localhost:${PORT:-8000}/docs${NC}"
echo -e "${BLUE}🔍 Health Check: http://localhost:${PORT:-8000}/health${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Run with uvicorn
python main.py

echo -e "${GREEN}👋 Server stopped. Goodbye!${NC}"