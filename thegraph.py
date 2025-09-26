"""
The Graph Data Fetcher
Fetches on-chain wallet data using The Graph Protocol
"""

import aiohttp
import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)

class GraphDataFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://gateway.thegraph.com/api"
        
        # Common subgraph endpoints
        self.subgraphs = {
            "uniswap_v3": f"{self.base_url}/{api_key}/subgraphs/id/HUZDsRpEVP2AvzBbkhGXgnl9nUV3M6GcNk4AKzSPqBLs",
            "ethereum_blocks": f"{self.base_url}/{api_key}/subgraphs/id/QmSdR4TLqJf8aWW9gaBjNUq3eiWgXBKbFRbqjdwgBwJu69",
            "erc20_tokens": f"{self.base_url}/{api_key}/subgraphs/id/Qmb3r6Q5VqF7Qx4GnGfJBq8BKBgYx9P2VqW3MbXs8Gv4Dk"
        }
        
    async def get_user_portfolio(self, address: str) -> Dict[str, Any]:
        """Fetch comprehensive portfolio data for a user address"""
        try:
            logger.info(f"Fetching portfolio for address: {address}")
            
            # If API key is not demo, try to fetch real data first
            if self.api_key != "demo-key":
                real_data = await self._fetch_real_portfolio_data(address)
                if real_data:
                    logger.info("Using real data from The Graph")
                    return real_data
            
            # For demo purposes, we'll return mock data as fallback
            # In production, you'd query actual subgraphs
            portfolio_data = {
                "address": address.lower(),
                "tokens": [
                    {
                        "symbol": "ETH",
                        "name": "Ethereum",
                        "balance": "2.5",
                        "contract_address": "0x0000000000000000000000000000000000000000",
                        "decimals": 18
                    },
                    {
                        "symbol": "USDC",
                        "name": "USD Coin",
                        "balance": "1500.50",
                        "contract_address": "0xa0b86a33e6086aada5a9e5aa3b5b8a0a0d9b1c2d",
                        "decimals": 6
                    },
                    {
                        "symbol": "MATIC",
                        "name": "Polygon",
                        "balance": "100.0",
                        "contract_address": "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0",
                        "decimals": 18
                    }
                ],
                "positions": [
                    {
                        "protocol": "Uniswap V3",
                        "type": "liquidity_pool",
                        "token0": "ETH",
                        "token1": "USDC",
                        "liquidity": "50000.0",
                        "fees_earned": "125.50"
                    }
                ],
                "transactions": [],
                "last_updated": "2024-01-01T00:00:00Z",
                "data_source": "mock"
            }
            
            logger.info("Using mock data as fallback")
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Error fetching portfolio for {address}: {e}")
            # Return minimal data on error
            return {
                "address": address.lower(),
                "tokens": [],
                "positions": [],
                "transactions": [],
                "error": str(e)
            }
    
    async def _fetch_real_portfolio_data(self, address: str) -> Optional[Dict[str, Any]]:
        """Fetch real data from The Graph (when API key is provided)"""
        try:
            # Use a real Polygon token balances subgraph
            # This is an example - you might need to find the correct subgraph for your use case
            url = f"https://gateway.thegraph.com/api/{self.api_key}/subgraphs/id/HdVdERFUe8h61vm2fDyycHgxjsde5PbB832NHgJfZNqK"
            
            # GraphQL query for user token balances
            query = """
            {
              accounts(where: {id: "%s"}) {
                id
                balances {
                  amount
                  token {
                    id
                    symbol
                    name
                    decimals
                  }
                }
              }
            }
            """ % address.lower()
            
            logger.info(f"Querying The Graph with real API key: {url[:50]}...")
            
            async with aiohttp.ClientSession() as session:
                payload = {"query": query}
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"The Graph API response status: {response.status}")
                        
                        if "errors" in data:
                            logger.error(f"The Graph API errors: {data['errors']}")
                            return None
                            
                        parsed_data = self._parse_graph_response(data)
                        if parsed_data:
                            parsed_data["data_source"] = "thegraph_real"
                            return parsed_data
                        else:
                            logger.info("No data found for this address in The Graph")
                            return None
                    else:
                        response_text = await response.text()
                        logger.error(f"The Graph API error {response.status}: {response_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching real data from The Graph: {e}")
            return None
    
    def _parse_graph_response(self, response: Dict) -> Dict[str, Any]:
        """Parse The Graph API response into our standard format"""
        try:
            if "data" not in response:
                return None
                
            user_data = response["data"].get("user")
            if not user_data:
                return None
            
            tokens = []
            for balance in user_data.get("balances", []):
                token = balance["token"]
                tokens.append({
                    "symbol": token["symbol"],
                    "name": token["name"],
                    "balance": str(Decimal(balance["balance"]) / (10 ** int(token["decimals"]))),
                    "contract_address": token["id"],
                    "decimals": int(token["decimals"])
                })
            
            return {
                "address": user_data["id"],
                "tokens": tokens,
                "positions": [],  # Would parse LP positions, etc.
                "transactions": []
            }
            
        except Exception as e:
            logger.error(f"Error parsing Graph response: {e}")
            return None

    async def get_token_transfers(self, address: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent token transfers for an address"""
        try:
            # Mock data for demo
            transfers = [
                {
                    "hash": "0x1234567890abcdef...",
                    "from": "0x742d35Cc6634C0532925a3b8D0C026Ba85C5d9C6",
                    "to": address.lower(),
                    "token": "USDC",
                    "amount": "100.0",
                    "timestamp": "2024-01-01T12:00:00Z",
                    "block_number": 50000000
                }
            ]
            
            return transfers
            
        except Exception as e:
            logger.error(f"Error fetching transfers: {e}")
            return []

    async def get_protocol_positions(self, address: str) -> List[Dict[str, Any]]:
        """Get DeFi protocol positions"""
        try:
            # Mock positions data
            positions = [
                {
                    "protocol": "Uniswap V3",
                    "type": "liquidity_position",
                    "token_pair": "ETH/USDC",
                    "liquidity_usd": "5000.0",
                    "fees_earned_usd": "125.50",
                    "apr": "12.5"
                },
                {
                    "protocol": "Aave",
                    "type": "lending",
                    "token": "USDC",
                    "supplied_amount": "1000.0",
                    "apr": "4.2"
                }
            ]
            
            return positions
            
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []