#!/bin/bash

# AI Portfolio Agent - Setup Script
# This script sets up the development environment

echo "🚀 Setting up AI Portfolio Agent Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python 3.8+ is installed
echo -e "${BLUE}📋 Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo -e "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}"
    
    # Check if version is 3.8+
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
        echo -e "${GREEN}✅ Python version is compatible${NC}"
    else
        echo -e "${RED}❌ Python 3.8+ required. Current version: ${PYTHON_VERSION}${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Python3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${BLUE}🔧 Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}📦 Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${BLUE}📚 Installing requirements...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Requirements installed successfully${NC}"
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

# Create .env file if it doesn't exist
echo -e "${BLUE}⚙️  Setting up environment configuration...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || cat > .env << 'EOF'
# AI Portfolio Agent Environment Configuration
THE_GRAPH_API_KEY=your_thegraph_api_key_here
ONEINCH_API_KEY=your_1inch_api_key_here
ASI_AGENT_ENDPOINT=your_asi_agent_endpoint_here
POLYGON_RPC_URL=https://polygon-rpc.com
POLYGON_CHAIN_ID=137
PYTH_HERMES_URL=https://hermes.pyth.network
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=INFO
JWT_SECRET_KEY=your_jwt_secret_key_here
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
TEST_WALLET_ADDRESS=0x742d35Cc6634C0532925a3b8D0C026Ba85C5d9C6
EOF
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env file with your actual API keys${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
fi

# Create project structure
echo -e "${BLUE}📁 Creating project structure...${NC}"
mkdir -p logs
mkdir -p tests
touch __init__.py

echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo -e "${YELLOW}1. Edit .env file with your API keys:${NC}"
echo -e "   - Get The Graph API key from: https://thegraph.com/studio/"
echo -e "   - Get 1inch API key from: https://portal.1inch.dev/"
echo -e "   - Configure ASI Alliance endpoint"
echo ""
echo -e "${YELLOW}2. Activate virtual environment:${NC}"
echo -e "   source venv/bin/activate"
echo ""
echo -e "${YELLOW}3. Run the application:${NC}"
echo -e "   python main.py"
echo ""
echo -e "${YELLOW}4. Test the API:${NC}"
echo -e "   curl http://localhost:8000/health"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"