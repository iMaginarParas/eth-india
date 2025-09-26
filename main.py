"""
AI Portfolio Agent Backend - main.py (Simplified)
Focus on testing core integrations:
- The Graph: fetching wallet data
- Pyth: market feed integration  
- ASI Alliance: AI agent reasoning
- 1inch: trade execution
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
from asi_alliance import ASIAgentReasoning
from oneinch import OneInchExecutor
from polygon import PolygonConnector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    THE_GRAPH_API_KEY: str = os.getenv("THE_GRAPH_API_KEY", "demo-key")
    PYTH_HERMES_URL: str = "https://hermes.pyth.network"
    ASI_AGENT_ENDPOINT: str = os.getenv("ASI_AGENT_ENDPOINT", "")
    ONEINCH_API_KEY: str = os.getenv("ONEINCH_API_KEY", "")
    POLYGON_RPC_URL: str = "https://polygon-rpc.com"
    POLYGON_CHAIN_ID: int = 137

config = Config()

# Pydantic Models
class WalletRequest(BaseModel):
    address: str

class TradeRequest(BaseModel):
    token_from: str
    token_to: str
    amount: str
    user_address: str

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
asi_agent: Optional[ASIAgentReasoning] = None
oneinch_executor: Optional[OneInchExecutor] = None
polygon_connector: Optional[PolygonConnector] = None

@app.on_event("startup")
async def startup_event():
    """Initialize all services"""
    global graph_fetcher, pyth_service, asi_agent, oneinch_executor, polygon_connector
    
    logger.info("🚀 Starting AI Portfolio Agent Core Services...")
    
    try:
        # Initialize The Graph data fetcher
        graph_fetcher = GraphDataFetcher(api_key=config.THE_GRAPH_API_KEY)
        logger.info("✅ The Graph service initialized")
        
        # Initialize Pyth price service
        pyth_service = PythPriceService(hermes_url=config.PYTH_HERMES_URL)
        logger.info("✅ Pyth service initialized")
        
        # Initialize ASI Alliance agent
        asi_agent = ASIAgentReasoning(endpoint=config.ASI_AGENT_ENDPOINT)
        logger.info("✅ ASI Alliance service initialized")
        
        # Initialize 1inch executor
        oneinch_executor = OneInchExecutor(
            api_key=config.ONEINCH_API_KEY,
            chain_id=config.POLYGON_CHAIN_ID
        )
        logger.info("✅ 1inch service initialized")
        
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

# 3. ASI ALLIANCE - Test AI agent reasoning
@app.post("/test/asi")
async def test_asi_agent(request: dict):
    """Test ASI Alliance AI reasoning"""
    try:
        logger.info("🤖 Testing ASI Alliance AI agent reasoning")
        
        # Generate AI insight
        insight = await asi_agent.generate_insight(
            token_symbol=request.get("token", "ETH"),
            portfolio_data=request.get("portfolio", {}),
            market_data=request.get("market", {}),
            user_context=request.get("context", {})
        )
        
        return {
            "service": "ASI Alliance",
            "status": "success",
            "insight": insight
        }
        
    except Exception as e:
        logger.error(f"❌ ASI Alliance test failed: {e}")
        raise HTTPException(status_code=500, detail=f"ASI Alliance error: {str(e)}")

# 4. 1INCH - Test trade execution
@app.post("/test/1inch/quote")
async def test_1inch_quote(trade: TradeRequest):
    """Test 1inch trade quote"""
    try:
        logger.info(f"🔄 Testing 1inch quote: {trade.token_from} -> {trade.token_to}")
        
        # Get swap quote from 1inch
        quote = await oneinch_executor.get_swap_quote(
            token_from=trade.token_from,
            token_to=trade.token_to,
            amount=trade.amount,
            user_address=trade.user_address
        )
        
        return {
            "service": "1inch",
            "status": "success",
            "quote": quote
        }
        
    except Exception as e:
        logger.error(f"❌ 1inch test failed: {e}")
        raise HTTPException(status_code=500, detail=f"1inch error: {str(e)}")

# 5. POLYGON - Test blockchain connection
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
            prices = await pyth_service.get_token_prices(["ETH", "BTC", "MATIC"])
            results["pyth"] = {"status": "success", "prices": prices}
        except Exception as e:
            results["pyth"] = {"status": "failed", "error": str(e)}
        
        # 3. Test ASI Alliance - Generate insight
        try:
            insight = await asi_agent.generate_insight(
                token_symbol="ETH",
                portfolio_data=results.get("thegraph", {}).get("data", {}),
                market_data=results.get("pyth", {}).get("prices", {}),
                user_context={"address": address}
            )
            results["asi_alliance"] = {"status": "success", "insight": insight}
        except Exception as e:
            results["asi_alliance"] = {"status": "failed", "error": str(e)}
        
        # 4. Test 1inch - Get a sample quote
        try:
            quote = await oneinch_executor.get_swap_quote(
                token_from="0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",  # WETH on Polygon
                token_to="0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",   # WMATIC
                amount="100000000000000000",  # 0.1 ETH
                user_address=address
            )
            results["oneinch"] = {"status": "success", "quote": quote}
        except Exception as e:
            results["oneinch"] = {"status": "failed", "error": str(e)}
        
        # 5. Test Polygon - Get network status
        try:
            block_info = await polygon_connector.get_latest_block()
            results["polygon"] = {"status": "success", "block": block_info}
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

# Health Check
@app.get("/health")
async def health_check():
    """Service health check"""
    services_status = {
        "thegraph": graph_fetcher is not None,
        "pyth": pyth_service is not None,
        "asi_alliance": asi_agent is not None,
        "oneinch": oneinch_executor is not None,
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
            "test_asi": "POST /test/asi - Test AI reasoning",
            "test_1inch": "POST /test/1inch/quote - Test trade quotes",
            "test_polygon": "GET /test/polygon - Test blockchain connection",
            "test_all": "POST /test/all - Test all services together",
            "health": "GET /health - Service health check"
        },
        "example_usage": {
            "wallet_test": "POST /test/all with {\"address\": \"0x...\"}",
            "price_test": "GET /test/pyth/ETH,BTC,MATIC",
            "blockchain_test": "GET /test/polygon"
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