import os
import asyncio
import httpx
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn

# Configuration
class Config:
    # The Graph API credentials (replace with your actual values)
    GRAPH_API_KEY = "server_051c84a4913a66795ff4139a1fc98e86"
    GRAPH_JWT_TOKEN = "eyJhbGciOiJLTVNFUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3OTUwMDc1ODIsImp0aSI6IjJlODI5NzAxLWYzNDYtNDE1NC04YTQ0LTYyNjU3Y2NiNmJkNSIsImlhdCI6MTc1OTAwNzU4MiwiaXNzIjoiZGZ1c2UuaW8iLCJzdWIiOiIwc2ltZWNjYWJjMTc5ZTQ0YzRlZmQiLCJ2IjoyLCJha2kiOiJlZGQyYzBmN2EwMWZlOGJiYmM5MWE3Y2QwZGMzNDkxZmRlYzczZTVhZDg0YTM0ZjdiMmIzMDBhNmIyMzIxY2E2IiwidWlkIjoiMHNpbWVjY2FiYzE3OWU0NGM0ZWZkIiwic3Vic3RyZWFtc19wbGFuX3RpZXIiOiJGUkVFIiwiY2ZnIjp7IlNVQlNUUkVBTVNfTUFYX1JFUVVFU1RTIjoiMiIsIlNVQlNUUkVBTVNfUEFSQUxMRUxfSk9CUyI6IjUiLCJTVUJTVFJFQU1TX1BBUkFMTEVMX1dPUktFUlMiOiI1In19.CEF9j0FD224mRQNm9B3vH5F_AI_-Y6cF9WL2Sclg_kiK1ekvq0VtAu9Ay1RaRo2EEvoAn8ZBKSm0oNfn7Vgvmg"
    
    # Telegram Bot Token (you'll need to create this with @BotFather)
    TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    
    # Replicate API Token (for AI analysis)
    REPLICATE_API_TOKEN = "YOUR_REPLICATE_API_TOKEN"
    
    # The Graph endpoints
    GRAPH_TOKEN_API_URL = "https://api.thegraph.com/token/v1"
    GRAPH_SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name"

# Data models
class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[Dict] = None

class ContractAnalysis(BaseModel):
    contract_address: str
    risk_score: int  # 0-100
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    summary: str
    details: List[str]
    analyzed_at: datetime

@dataclass
class TokenData:
    address: str
    name: str
    symbol: str
    total_supply: Optional[str]
    holders_count: int
    transfers_count: int
    price_usd: Optional[float]

class ContractAuditorService:
    def __init__(self):
        self.http_client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {Config.GRAPH_JWT_TOKEN}",
                "Content-Type": "application/json"
            }
        )
    
    async def get_token_data(self, contract_address: str, chain: str = "ethereum") -> TokenData:
        """Fetch token data from The Graph Token API"""
        try:
            url = f"{Config.GRAPH_TOKEN_API_URL}/{chain}/{contract_address}"
            response = await self.http_client.get(url)
            response.raise_for_status()
            
            data = response.json()
            return TokenData(
                address=contract_address,
                name=data.get("name", "Unknown"),
                symbol=data.get("symbol", "Unknown"),
                total_supply=data.get("totalSupply"),
                holders_count=data.get("holdersCount", 0),
                transfers_count=data.get("transfersCount", 0),
                price_usd=data.get("priceUsd")
            )
        except httpx.HTTPError as e:
            print(f"Error fetching token data: {e}")
            # Return basic data if API fails
            return TokenData(
                address=contract_address,
                name="Unknown",
                symbol="Unknown",
                total_supply=None,
                holders_count=0,
                transfers_count=0,
                price_usd=None
            )
    
    async def get_transaction_patterns(self, contract_address: str) -> Dict:
        """Query transaction patterns from subgraphs"""
        # Example GraphQL query for Ethereum mainnet transfers
        query = """
        {
          transfers(
            first: 100,
            where: {token: "%s"},
            orderBy: blockNumber,
            orderDirection: desc
          ) {
            id
            from
            to
            value
            blockNumber
            blockTimestamp
          }
        }
        """ % contract_address.lower()
        
        try:
            # Using a general Ethereum transfers subgraph
            url = f"{Config.GRAPH_SUBGRAPH_URL}/ethereum/ethereum-transfers"
            response = await self.http_client.post(
                url,
                json={"query": query}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"data": {"transfers": []}}
                
        except Exception as e:
            print(f"Error fetching transaction patterns: {e}")
            return {"data": {"transfers": []}}
    
    async def analyze_with_ai(self, token_data: TokenData, transactions: List[Dict]) -> ContractAnalysis:
        """Analyze contract data using AI (Replicate API)"""
        
        # Prepare data summary for AI analysis
        analysis_prompt = f"""
        Analyze this smart contract for potential risks:
        
        Token: {token_data.name} ({token_data.symbol})
        Address: {token_data.address}
        Total Supply: {token_data.total_supply}
        Holders: {token_data.holders_count}
        Transfers: {token_data.transfers_count}
        Price: ${token_data.price_usd}
        
        Recent Transactions: {len(transactions)} transfers analyzed
        
        Red flags to check:
        1. Low holder count vs high transfers (potential wash trading)
        2. Large token concentration in few wallets
        3. Unusual transfer patterns
        4. No price data or extreme volatility
        5. Very new token with high activity
        
        Provide a risk score (0-100) and explanation in plain English.
        """
        
        # For demo purposes, we'll create a simple risk assessment
        # In production, you'd call Replicate API here
        risk_score = self._calculate_risk_score(token_data, transactions)
        risk_level = self._get_risk_level(risk_score)
        
        details = []
        
        # Basic risk checks
        if token_data.holders_count < 100:
            details.append("⚠️ Low number of token holders - potential for price manipulation")
        
        if token_data.transfers_count > token_data.holders_count * 10:
            details.append("🔴 High transfer to holder ratio - possible wash trading")
        
        if not token_data.price_usd:
            details.append("⚠️ No price data available - token may not be trading")
        
        if len(transactions) == 0:
            details.append("ℹ️ No recent transaction data available")
        
        # Analyze transaction patterns
        if transactions:
            unique_addresses = set()
            for tx in transactions:
                unique_addresses.add(tx.get('from', ''))
                unique_addresses.add(tx.get('to', ''))
            
            if len(unique_addresses) < 10:
                details.append("🔴 Very few unique addresses in recent transactions")
        
        summary = f"Risk Level: {risk_level}. "
        if risk_score < 30:
            summary += "This token appears relatively safe based on available data."
        elif risk_score < 70:
            summary += "Some concerning patterns detected. Proceed with caution."
        else:
            summary += "Multiple red flags detected. High risk of scam or manipulation."
        
        return ContractAnalysis(
            contract_address=token_data.address,
            risk_score=risk_score,
            risk_level=risk_level,
            summary=summary,
            details=details,
            analyzed_at=datetime.now()
        )
    
    def _calculate_risk_score(self, token_data: TokenData, transactions: List[Dict]) -> int:
        """Simple risk scoring algorithm"""
        score = 0
        
        # Low holders
        if token_data.holders_count < 50:
            score += 30
        elif token_data.holders_count < 200:
            score += 15
        
        # High transfer/holder ratio
        if token_data.holders_count > 0:
            ratio = token_data.transfers_count / token_data.holders_count
            if ratio > 20:
                score += 25
            elif ratio > 10:
                score += 15
        
        # No price data
        if not token_data.price_usd:
            score += 20
        
        # Few recent transactions
        if len(transactions) < 5:
            score += 10
        
        return min(score, 100)
    
    def _get_risk_level(self, score: int) -> str:
        """Convert risk score to level"""
        if score < 25:
            return "LOW"
        elif score < 50:
            return "MEDIUM"
        elif score < 75:
            return "HIGH"
        else:
            return "CRITICAL"

class TelegramBot:
    def __init__(self, auditor_service: ContractAuditorService):
        self.auditor = auditor_service
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
    
    async def send_message(self, chat_id: int, text: str):
        """Send message to Telegram chat"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        async with httpx.AsyncClient() as client:
            await client.post(url, json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            })
    
    async def process_message(self, message: Dict):
        """Process incoming Telegram message"""
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if text.startswith("/start"):
            welcome_msg = """
🔍 <b>Smart Contract Auditor Bot</b>

Send me a contract address and I'll analyze it for potential risks!

Example: 0x1234567890123456789012345678901234567890

⚡ Powered by The Graph Protocol & AI
            """
            await self.send_message(chat_id, welcome_msg)
            return
        
        # Check if message looks like a contract address
        if text.startswith("0x") and len(text) == 42:
            await self.send_message(chat_id, "🔍 Analyzing contract... Please wait.")
            
            try:
                analysis = await self.analyze_contract(text)
                response = self._format_analysis(analysis)
                await self.send_message(chat_id, response)
            except Exception as e:
                await self.send_message(chat_id, f"❌ Error analyzing contract: {str(e)}")
        else:
            await self.send_message(chat_id, "Please send a valid Ethereum contract address (0x...)")
    
    async def analyze_contract(self, contract_address: str) -> ContractAnalysis:
        """Analyze a contract address"""
        # Get token data
        token_data = await self.auditor.get_token_data(contract_address)
        
        # Get transaction patterns
        tx_data = await self.auditor.get_transaction_patterns(contract_address)
        transactions = tx_data.get("data", {}).get("transfers", [])
        
        # Analyze with AI
        analysis = await self.auditor.analyze_with_ai(token_data, transactions)
        
        return analysis
    
    def _format_analysis(self, analysis: ContractAnalysis) -> str:
        """Format analysis results for Telegram"""
        risk_emoji = {
            "LOW": "🟢",
            "MEDIUM": "🟡", 
            "HIGH": "🟠",
            "CRITICAL": "🔴"
        }
        
        result = f"""
🔍 <b>Contract Analysis Results</b>

📋 <b>Contract:</b> <code>{analysis.contract_address}</code>

{risk_emoji.get(analysis.risk_level, "⚪")} <b>Risk Level:</b> {analysis.risk_level}
📊 <b>Risk Score:</b> {analysis.risk_score}/100

💡 <b>Summary:</b>
{analysis.summary}

🔍 <b>Details:</b>
"""
        
        for detail in analysis.details:
            result += f"\n• {detail}"
        
        result += f"\n\n⏰ <i>Analyzed at {analysis.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')} UTC</i>"
        
        return result

# FastAPI app
app = FastAPI(title="Smart Contract Auditor Bot")

# Services
auditor_service = ContractAuditorService()
telegram_bot = TelegramBot(auditor_service)

@app.get("/")
async def root():
    return {"message": "Smart Contract Auditor Bot is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/webhook")
async def telegram_webhook(update: TelegramUpdate, background_tasks: BackgroundTasks):
    """Handle Telegram webhook"""
    if update.message:
        background_tasks.add_task(telegram_bot.process_message, update.message)
    
    return {"ok": True}

@app.post("/analyze")
async def analyze_contract_endpoint(contract_address: str):
    """Direct API endpoint for contract analysis"""
    try:
        analysis = await telegram_bot.analyze_contract(contract_address)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)