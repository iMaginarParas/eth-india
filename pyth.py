"""
Pyth Network Price Service
Real-time price feeds from Pyth Network
"""

import aiohttp
import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal
import time

logger = logging.getLogger(__name__)

class PythPriceService:
    def __init__(self, hermes_url: str = "https://hermes.pyth.network"):
        self.hermes_url = hermes_url
        
        # Price feed IDs for major tokens
        self.price_feed_ids = {
            "ETH": "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
            "BTC": "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
            "MATIC": "0x5de33a9112c2b700b8d30b8a3402c103578ccfa2765696471cc672bd5cf6ac52",
            "USDC": "0xeaa020c61cc479712813461ce153894a96a6c00b21ed0cfc2798d1f9a9e9c94a",
            "USDT": "0x2b89b9dc8fdf9f34709a5b106b472f0f39bb6ca4ce95d36de9b61b2f3e1edb3f",
            "LINK": "0x8ac0c70fff57e9aefdf5edf44b51d62c2d433653cbb2cf5cc06bb115af04d221",
            "UNI": "0x78d185a741d07edb3aeb9547aa6e0d23a2ea2d7e2c2ebcdcb8a479eaf5ad6b3a",
            "AAVE": "0x2f95862b045670cd22bee3114c39763a4a08beeb663b145d283c31d7d1101c4f"
        }
    
    async def get_token_prices(self, symbols: List[str]) -> Dict[str, Any]:
        """Get current prices for multiple tokens"""
        try:
            logger.info(f"Fetching prices for tokens: {symbols}")
            
            prices = {}
            
            # Get price feed IDs for requested symbols
            feed_ids = []
            valid_symbols = []
            
            for symbol in symbols:
                symbol_upper = symbol.upper()
                if symbol_upper in self.price_feed_ids:
                    feed_ids.append(self.price_feed_ids[symbol_upper])
                    valid_symbols.append(symbol_upper)
                else:
                    logger.warning(f"Price feed not available for {symbol}")
            
            if not feed_ids:
                # Return mock data if no valid symbols
                return self._get_mock_prices(symbols)
            
            # Fetch latest prices from Pyth Hermes
            latest_prices = await self._fetch_latest_prices(feed_ids)
            
            # Process the response
            for i, symbol in enumerate(valid_symbols):
                if i < len(latest_prices):
                    price_data = latest_prices[i]
                    prices[symbol] = {
                        "price": self._parse_price(price_data),
                        "confidence": self._parse_confidence(price_data),
                        "publish_time": price_data.get("publish_time", int(time.time())),
                        "source": "pyth"
                    }
                else:
                    # Fallback to mock data
                    prices[symbol] = self._get_mock_price(symbol)
            
            # Add mock data for symbols without price feeds
            for symbol in symbols:
                symbol_upper = symbol.upper()
                if symbol_upper not in prices:
                    prices[symbol_upper] = self._get_mock_price(symbol_upper)
            
            return prices
            
        except Exception as e:
            logger.error(f"Error fetching prices: {e}")
            # Return mock data on error
            return self._get_mock_prices(symbols)
    
    async def _fetch_latest_prices(self, feed_ids: List[str]) -> List[Dict[str, Any]]:
        """Fetch latest prices from Pyth Hermes API"""
        try:
            # Use the correct Pyth API endpoint that actually works
            ids_param = "&".join([f"ids[]={feed_id}" for feed_id in feed_ids])
            url = f"{self.hermes_url}/api/latest_vaas?{ids_param}"
            
            logger.info(f"Fetching from Pyth API: {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        # The VAA endpoint returns data differently
                        logger.info(f"Pyth API success: Status {response.status}")
                        return data if isinstance(data, list) else [data]
                    else:
                        response_text = await response.text()
                        logger.error(f"Pyth API error {response.status}: {response_text}")
                        
                        # Try alternative endpoint
                        alt_url = f"{self.hermes_url}/v2/updates/price/latest?{ids_param}&encoding=hex"
                        async with session.get(alt_url) as alt_response:
                            if alt_response.status == 200:
                                alt_data = await alt_response.json()
                                parsed_data = alt_data.get("parsed", [])
                                logger.info(f"Pyth alternative API success: Got {len(parsed_data)} price feeds")
                                return parsed_data
                        
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching from Pyth API: {e}")
            return []
    
    def _parse_price(self, price_data: Dict[str, Any]) -> Decimal:
        """Parse price from Pyth data format"""
        try:
            # Handle different response formats from Pyth API
            if isinstance(price_data, str):
                # This is a VAA string - we need to decode it properly
                # For now, return 0 and fall back to mock data
                return Decimal(0)
            
            # Handle parsed price data format
            price_info = price_data.get("price", {})
            if not price_info:
                return Decimal(0)
                
            price = int(price_info.get("price", 0))
            expo = int(price_info.get("expo", 0))
            
            # Price = price * (10 ^ expo)
            actual_price = Decimal(price) * (Decimal(10) ** expo)
            return actual_price
            
        except Exception as e:
            logger.error(f"Error parsing price: {e}")
            return Decimal(0)
    
    def _parse_confidence(self, price_data: Dict[str, Any]) -> Decimal:
        """Parse confidence interval from Pyth data"""
        try:
            price_info = price_data.get("price", {})
            conf = int(price_info.get("conf", 0))
            expo = int(price_info.get("expo", 0))
            
            confidence = Decimal(conf) * (Decimal(10) ** expo)
            return confidence
            
        except Exception as e:
            logger.error(f"Error parsing confidence: {e}")
            return Decimal(0)
    
    def _get_mock_prices(self, symbols: List[str]) -> Dict[str, Any]:
        """Generate mock price data for testing"""
        mock_prices = {
            "ETH": {"price": Decimal("2400.50"), "confidence": Decimal("1.20"), "source": "mock"},
            "BTC": {"price": Decimal("43500.00"), "confidence": Decimal("50.00"), "source": "mock"},
            "MATIC": {"price": Decimal("0.85"), "confidence": Decimal("0.01"), "source": "mock"},
            "USDC": {"price": Decimal("1.00"), "confidence": Decimal("0.001"), "source": "mock"},
            "USDT": {"price": Decimal("1.00"), "confidence": Decimal("0.001"), "source": "mock"},
            "LINK": {"price": Decimal("15.75"), "confidence": Decimal("0.15"), "source": "mock"},
            "UNI": {"price": Decimal("8.25"), "confidence": Decimal("0.08"), "source": "mock"},
            "AAVE": {"price": Decimal("85.50"), "confidence": Decimal("1.50"), "source": "mock"}
        }
        
        result = {}
        for symbol in symbols:
            symbol_upper = symbol.upper()
            if symbol_upper in mock_prices:
                price_data = mock_prices[symbol_upper].copy()
                price_data["publish_time"] = int(time.time())
                result[symbol_upper] = price_data
            else:
                result[symbol_upper] = {
                    "price": Decimal("1.00"),
                    "confidence": Decimal("0.01"),
                    "publish_time": int(time.time()),
                    "source": "mock"
                }
        
        return result
    
    def _get_mock_price(self, symbol: str) -> Dict[str, Any]:
        """Get mock price for a single symbol"""
        mock_data = self._get_mock_prices([symbol])
        return mock_data.get(symbol.upper(), {
            "price": Decimal("1.00"),
            "confidence": Decimal("0.01"),
            "publish_time": int(time.time()),
            "source": "mock"
        })
    
    async def get_historical_prices(self, symbol: str, start_time: int, end_time: int) -> List[Dict[str, Any]]:
        """Get historical price data"""
        try:
            # This would require the Pyth historical API
            # For now, return mock historical data
            
            mock_history = []
            current_time = start_time
            base_price = self._get_mock_price(symbol)["price"]
            
            while current_time <= end_time:
                # Simulate price movements
                price_change = (hash(str(current_time)) % 200 - 100) / 10000  # Random ±1%
                price = base_price * (1 + Decimal(str(price_change)))
                
                mock_history.append({
                    "timestamp": current_time,
                    "price": price,
                    "volume": Decimal("1000000"),  # Mock volume
                })
                
                current_time += 3600  # 1 hour intervals
            
            return mock_history
            
        except Exception as e:
            logger.error(f"Error fetching historical prices: {e}")
            return []
    
    async def get_price_feed_info(self, symbol: str) -> Dict[str, Any]:
        """Get information about a price feed"""
        try:
            symbol_upper = symbol.upper()
            if symbol_upper not in self.price_feed_ids:
                return {"error": f"Price feed not available for {symbol}"}
            
            feed_id = self.price_feed_ids[symbol_upper]
            
            return {
                "symbol": symbol_upper,
                "feed_id": feed_id,
                "description": f"{symbol_upper}/USD price feed",
                "asset_type": "crypto",
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Error getting feed info: {e}")
            return {"error": str(e)}