"""
AI Portfolio Agent Backend - main.py (Simplified)
Focus on testing core integrations:
- The Graph: fetching wallet data
- Pyth: market feed integration  
- Polygon: deployment chain
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
from decimal import Decimal

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from web3 import Web3

# Import our custom modules
from thegraph import GraphDataFetcher
from pyth import PythPriceService
from polygon import PolygonConnector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    THE_GRAPH_API_KEY: str = os.getenv("THE_GRAPH_API_KEY", "demo-key")
    PYTH_HERMES_URL: str = "https://hermes.pyth.network"
    POLYGON_RPC_URL: str = "https://polygon-rpc.com"
    POLYGON_CHAIN_ID: int = 137

config = Config()

# Pydantic Models
class WalletRequest(BaseModel):
    address: str

# FastAPI App
app = FastAPI(title="AI Portfolio Agent - Core Testing", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
graph_fetcher: Optional[GraphDataFetcher] = None
pyth_service: Optional[PythPriceService] = None
polygon_connector: Optional[PolygonConnector] = None

@app.on_event("startup")
async def startup_event():
    """Initialize all services"""
    global graph_fetcher, pyth_service, polygon_connector
    
    logger.info("🚀 Starting AI Portfolio Agent Core Services...")
    
    try:
        # Initialize The Graph data fetcher
        graph_fetcher = GraphDataFetcher(api_key=config.THE_GRAPH_API_KEY)
        logger.info("✅ The Graph service initialized")
        
        # Initialize Pyth price service
        pyth_service = PythPriceService(hermes_url=config.PYTH_HERMES_URL)
        logger.info("✅ Pyth service initialized")
        
        # Initialize Polygon connector
        polygon_connector = PolygonConnector(
            rpc_url=config.POLYGON_RPC_URL,
            chain_id=config.POLYGON_CHAIN_ID
        )
        logger.info("✅ Polygon service initialized")
        
        logger.info("🎉 All services initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise

# 1. THE GRAPH - Test wallet data fetching
@app.get("/test/thegraph/{address}")
async def test_thegraph(address: str):
    """Test The Graph wallet data fetching"""
    try:
        logger.info(f"📊 Testing The Graph for address: {address}")
        
        # Fetch portfolio data from The Graph
        portfolio_data = await graph_fetcher.get_user_portfolio(address)
        
        return {
            "service": "The Graph",
            "status": "success",
            "address": address,
            "data": portfolio_data
        }
        
    except Exception as e:
        logger.error(f"❌ The Graph test failed: {e}")
        raise HTTPException(status_code=500, detail=f"The Graph error: {str(e)}")

# 2. PYTH - Test market feed integration
@app.get("/test/pyth/{symbols}")
async def test_pyth(symbols: str):
    """Test Pyth price feeds (comma-separated symbols like ETH,BTC,MATIC)"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        logger.info(f"💰 Testing Pyth price feeds for: {symbol_list}")
        
        # Get current prices from Pyth
        prices = await pyth_service.get_token_prices(symbol_list)
        
        return {
            "service": "Pyth Network",
            "status": "success",
            "symbols": symbol_list,
            "prices": prices
        }
        
    except Exception as e:
        logger.error(f"❌ Pyth test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pyth error: {str(e)}")

# 3. POLYGON - Test blockchain connection
@app.get("/test/polygon")
async def test_polygon():
    """Test Polygon blockchain connection"""
    try:
        logger.info("⛓️ Testing Polygon blockchain connection")
        
        # Test blockchain connection
        block_info = await polygon_connector.get_latest_block()
        network_info = await polygon_connector.get_network_info()
        
        return {
            "service": "Polygon",
            "status": "success",
            "latest_block": block_info,
            "network_info": network_info
        }
        
    except Exception as e:
        logger.error(f"❌ Polygon test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Polygon error: {str(e)}")

# Get wallet balance on Polygon
@app.get("/test/polygon/balance/{address}")
async def test_polygon_balance(address: str):
    """Test getting wallet balance on Polygon"""
    try:
        logger.info(f"💰 Testing Polygon balance for address: {address}")
        
        # Get MATIC balance
        balance_info = await polygon_connector.get_balance(address)
        
        return {
            "service": "Polygon Balance",
            "status": "success",
            "address": address,
            "balance": balance_info
        }
        
    except Exception as e:
        logger.error(f"❌ Polygon balance test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Polygon balance error: {str(e)}")

# Get token balance on Polygon
@app.get("/test/polygon/token/{token_address}/{user_address}")
async def test_polygon_token_balance(token_address: str, user_address: str):
    """Test getting ERC20 token balance on Polygon"""
    try:
        logger.info(f"🪙 Testing token balance for {token_address} and user {user_address}")
        
        # Get token balance
        token_balance = await polygon_connector.get_token_balance(token_address, user_address)
        
        return {
            "service": "Polygon Token Balance",
            "status": "success",
            "token_address": token_address,
            "user_address": user_address,
            "balance": token_balance
        }
        
    except Exception as e:
        logger.error(f"❌ Token balance test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Token balance error: {str(e)}")

# COMPREHENSIVE TEST - Test all services together
@app.post("/test/all")
async def test_all_services(wallet: WalletRequest):
    """Test all services in a complete workflow"""
    try:
        address = wallet.address
        logger.info(f"🔥 Running comprehensive test for address: {address}")
        
        results = {}
        
        # 1. Test The Graph - Get portfolio
        try:
            portfolio = await graph_fetcher.get_user_portfolio(address)
            results["thegraph"] = {"status": "success", "data": portfolio}
        except Exception as e:
            results["thegraph"] = {"status": "failed", "error": str(e)}
        
        # 2. Test Pyth - Get prices for common tokens
        try:
            prices = await pyth_service.get_token_prices(["ETH", "BTC", "MATIC", "USDC"])
            results["pyth"] = {"status": "success", "prices": prices}
        except Exception as e:
            results["pyth"] = {"status": "failed", "error": str(e)}
        
        # 3. Test Polygon - Get network status and balance
        try:
            block_info = await polygon_connector.get_latest_block()
            network_info = await polygon_connector.get_network_info()
            balance_info = await polygon_connector.get_balance(address)
            
            results["polygon"] = {
                "status": "success", 
                "block": block_info,
                "network": network_info,
                "balance": balance_info
            }
        except Exception as e:
            results["polygon"] = {"status": "failed", "error": str(e)}
        
        # Calculate success rate
        successful_tests = len([r for r in results.values() if r["status"] == "success"])
        total_tests = len(results)
        success_rate = (successful_tests / total_tests) * 100
        
        return {
            "comprehensive_test": True,
            "address": address,
            "success_rate": f"{success_rate:.1f}%",
            "successful_services": successful_tests,
            "total_services": total_tests,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Comprehensive test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Comprehensive test error: {str(e)}")

# Portfolio Analysis - Combine data from all services
@app.post("/portfolio/analyze")
async def analyze_portfolio(wallet: WalletRequest):
    """Analyze portfolio by combining data from all services"""
    try:
        address = wallet.address
        logger.info(f"🔍 Analyzing portfolio for address: {address}")
        
        # Get portfolio data from The Graph
        portfolio_data = await graph_fetcher.get_user_portfolio(address)
        
        # Get current prices for portfolio tokens
        token_symbols = [token["symbol"] for token in portfolio_data.get("tokens", [])]
        if token_symbols:
            prices = await pyth_service.get_token_prices(token_symbols)
        else:
            prices = {}
        
        # Get network status
        network_info = await polygon_connector.get_network_info()
        balance_info = await polygon_connector.get_balance(address)
        
        # Calculate portfolio values
        total_value_usd = Decimal('0')
        enriched_tokens = []
        
        for token in portfolio_data.get("tokens", []):
            symbol = token["symbol"]
            balance = Decimal(str(token["balance"]))
            
            # Add price data if available
            if symbol in prices:
                current_price = prices[symbol]["price"]
                token_value_usd = balance * current_price
                total_value_usd += token_value_usd
                
                enriched_tokens.append({
                    **token,
                    "current_price_usd": str(current_price),
                    "value_usd": str(token_value_usd),
                    "price_source": prices[symbol]["source"]
                })
            else:
                enriched_tokens.append({
                    **token,
                    "current_price_usd": "0",
                    "value_usd": "0",
                    "price_source": "unavailable"
                })
        
        # Calculate portfolio allocation percentages
        for token in enriched_tokens:
            if total_value_usd > 0:
                allocation_pct = (Decimal(token["value_usd"]) / total_value_usd) * 100
                token["allocation_percentage"] = str(allocation_pct.quantize(Decimal('0.01')))
            else:
                token["allocation_percentage"] = "0"
        
        return {
            "address": address,
            "analysis_timestamp": "2024-01-01T00:00:00Z",
            "network_info": network_info,
            "native_balance": balance_info,
            "portfolio_summary": {
                "total_value_usd": str(total_value_usd),
                "token_count": len(enriched_tokens),
                "positions_count": len(portfolio_data.get("positions", []))
            },
            "tokens": enriched_tokens,
            "positions": portfolio_data.get("positions", []),
            "price_data_sources": {
                symbol: data.get("source", "unknown") 
                for symbol, data in prices.items()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Portfolio analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Portfolio analysis error: {str(e)}")

# Health Check
@app.get("/health")
async def health_check():
    """Service health check"""
    services_status = {
        "thegraph": graph_fetcher is not None,
        "pyth": pyth_service is not None,
        "polygon": polygon_connector is not None
    }
    
    all_healthy = all(services_status.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": services_status,
        "initialized_services": sum(services_status.values()),
        "total_services": len(services_status)
    }

# Root endpoint with instructions
@app.get("/")
async def root():
    """API instructions"""
    return {
        "message": "AI Portfolio Agent - Core Testing API",
        "endpoints": {
            "test_thegraph": "GET /test/thegraph/{address} - Test wallet data fetching",
            "test_pyth": "GET /test/pyth/{symbols} - Test price feeds (ETH,BTC,MATIC)",
            "test_polygon": "GET /test/polygon - Test blockchain connection",
            "test_polygon_balance": "GET /test/polygon/balance/{address} - Test wallet balance",
            "test_polygon_token": "GET /test/polygon/token/{token_address}/{user_address} - Test token balance",
            "test_all": "POST /test/all - Test all services together",
            "analyze_portfolio": "POST /portfolio/analyze - Comprehensive portfolio analysis",
            "health": "GET /health - Service health check"
        },
        "example_usage": {
            "wallet_test": "POST /test/all with {\"address\": \"0x...\"}",
            "price_test": "GET /test/pyth/ETH,BTC,MATIC",
            "blockchain_test": "GET /test/polygon",
            "portfolio_analysis": "POST /portfolio/analyze with {\"address\": \"0x...\"}"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )