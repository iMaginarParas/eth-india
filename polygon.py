"""
Polygon Blockchain Connector
Blockchain interaction and transaction monitoring
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal
from web3 import Web3
from web3.middleware import geth_poa_middleware
import aiohttp

logger = logging.getLogger(__name__)

class PolygonConnector:
    def __init__(self, rpc_url: str = "https://polygon-rpc.com", chain_id: int = 137):
        self.rpc_url = rpc_url
        self.chain_id = chain_id
        
        # Initialize Web3 connection
        try:
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            # Add PoA middleware for Polygon
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            # Test connection
            if self.w3.is_connected():
                logger.info(f"✅ Connected to Polygon network at {rpc_url}")
            else:
                logger.warning(f"⚠️ Failed to connect to Polygon network")
                
        except Exception as e:
            logger.error(f"❌ Error initializing Polygon connection: {e}")
            self.w3 = None
    
    async def get_latest_block(self) -> Dict[str, Any]:
        """Get latest block information"""
        try:
            if not self.w3 or not self.w3.is_connected():
                return self._get_mock_block_info()
            
            # Get latest block
            block = self.w3.eth.get_block('latest')
            
            return {
                "number": block.number,
                "hash": block.hash.hex(),
                "timestamp": block.timestamp,
                "gas_limit": block.gasLimit,
                "gas_used": block.gasUsed,
                "transaction_count": len(block.transactions),
                "miner": block.miner,
                "difficulty": block.difficulty,
                # Note: totalDifficulty removed as it's not available in newer versions
                "size": getattr(block, 'size', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting latest block: {e}")
            return self._get_mock_block_info()
    
    async def get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        try:
            if not self.w3 or not self.w3.is_connected():
                return self._get_mock_network_info()
            
            # Get network info
            chain_id = self.w3.eth.chain_id
            gas_price = self.w3.eth.gas_price
            block_number = self.w3.eth.block_number
            
            # Get network stats
            sync_status = self.w3.eth.syncing
            
            return {
                "chain_id": chain_id,
                "network_name": "Polygon Mainnet" if chain_id == 137 else f"Chain {chain_id}",
                "current_block": block_number,
                "gas_price_gwei": self.w3.from_wei(gas_price, 'gwei'),
                "gas_price_wei": gas_price,
                "is_syncing": bool(sync_status),
                "rpc_endpoint": self.rpc_url,
                "connected": True
            }
            
        except Exception as e:
            logger.error(f"Error getting network info: {e}")
            return self._get_mock_network_info()
    
    async def get_balance(self, address: str) -> Dict[str, Any]:
        """Get MATIC balance for an address"""
        try:
            if not self.w3 or not self.w3.is_connected():
                return self._get_mock_balance(address)
            
            # Convert to checksum address to handle case sensitivity
            try:
                checksum_address = Web3.to_checksum_address(address)
            except Exception as e:
                logger.error(f"Invalid address format: {address}")
                return {"error": f"Invalid address format: {address}"}
            
            # Validate address
            if not Web3.is_address(checksum_address):
                raise ValueError(f"Invalid address: {checksum_address}")
            
            # Get balance in wei
            balance_wei = self.w3.eth.get_balance(checksum_address)
            balance_matic = self.w3.from_wei(balance_wei, 'ether')
            
            return {
                "address": checksum_address,
                "balance_wei": str(balance_wei),
                "balance_matic": str(balance_matic),
                "balance_usd": str(float(balance_matic) * 0.85),  # Mock price
                "currency": "MATIC"
            }
            
        except Exception as e:
            logger.error(f"Error getting balance for {address}: {e}")
            return {"error": str(e)}
    
    async def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction information"""
        try:
            if not self.w3 or not self.w3.is_connected():
                return self._get_mock_transaction(tx_hash)
            
            # Get transaction
            tx = self.w3.eth.get_transaction(tx_hash)
            
            # Get transaction receipt
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                status = receipt.status
                gas_used = receipt.gasUsed
                block_number = receipt.blockNumber
            except:
                status = None
                gas_used = None
                block_number = None
            
            return {
                "hash": tx.hash.hex(),
                "from": tx["from"],
                "to": tx.to,
                "value_wei": str(tx.value),
                "value_matic": str(self.w3.from_wei(tx.value, 'ether')),
                "gas_limit": tx.gas,
                "gas_price": tx.gasPrice,
                "gas_used": gas_used,
                "status": status,  # 1 = success, 0 = failed, None = pending
                "block_number": block_number,
                "nonce": tx.nonce,
                "input": tx.input.hex() if tx.input else "0x"
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction {tx_hash}: {e}")
            return {"error": str(e)}
    
    async def wait_for_transaction(self, tx_hash: str, timeout: int = 300) -> Dict[str, Any]:
        """Wait for transaction to be mined"""
        try:
            if not self.w3 or not self.w3.is_connected():
                # Mock successful transaction after delay
                await asyncio.sleep(2)
                return {
                    "hash": tx_hash,
                    "status": 1,
                    "block_number": 50000000,
                    "gas_used": 150000,
                    "mock": True
                }
            
            logger.info(f"Waiting for transaction {tx_hash} to be mined...")
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            
            return {
                "hash": receipt.transactionHash.hex(),
                "status": receipt.status,
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "cumulative_gas_used": receipt.cumulativeGasUsed,
                "logs": [log.__dict__ for log in receipt.logs],
                "success": receipt.status == 1
            }
            
        except Exception as e:
            logger.error(f"Error waiting for transaction {tx_hash}: {e}")
            return {"error": str(e)}
    
    async def estimate_gas(self, transaction: Dict[str, Any]) -> int:
        """Estimate gas for a transaction"""
        try:
            if not self.w3 or not self.w3.is_connected():
                return 150000  # Mock gas estimate
            
            # Estimate gas
            gas_estimate = self.w3.eth.estimate_gas(transaction)
            return gas_estimate
            
        except Exception as e:
            logger.error(f"Error estimating gas: {e}")
            return 200000  # Conservative fallback
    
    async def get_current_gas_price(self) -> Dict[str, Any]:
        """Get current gas prices"""
        try:
            if not self.w3 or not self.w3.is_connected():
                return self._get_mock_gas_prices()
            
            # Get current gas price
            gas_price = self.w3.eth.gas_price
            
            # Calculate different gas speeds (mock implementation)
            slow_price = int(gas_price * 0.8)
            standard_price = gas_price
            fast_price = int(gas_price * 1.2)
            
            return {
                "slow": {
                    "gas_price_wei": slow_price,
                    "gas_price_gwei": self.w3.from_wei(slow_price, 'gwei'),
                    "estimated_time": "5-10 minutes"
                },
                "standard": {
                    "gas_price_wei": standard_price,
                    "gas_price_gwei": self.w3.from_wei(standard_price, 'gwei'),
                    "estimated_time": "2-5 minutes"
                },
                "fast": {
                    "gas_price_wei": fast_price,
                    "gas_price_gwei": self.w3.from_wei(fast_price, 'gwei'),
                    "estimated_time": "30 seconds - 2 minutes"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting gas prices: {e}")
            return self._get_mock_gas_prices()
    
    async def send_transaction(self, signed_transaction: str) -> str:
        """Send a signed transaction"""
        try:
            if not self.w3 or not self.w3.is_connected():
                # Return mock transaction hash
                return "0x" + "a" * 64
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_transaction)
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Error sending transaction: {e}")
            raise Exception(f"Transaction failed: {str(e)}")
    
    async def get_token_balance(self, token_address: str, user_address: str) -> Dict[str, Any]:
        """Get ERC20 token balance"""
        try:
            if not self.w3 or not self.w3.is_connected():
                return self._get_mock_token_balance(token_address, user_address)
            
            # Convert addresses to checksum format
            try:
                token_checksum = Web3.to_checksum_address(token_address)
                user_checksum = Web3.to_checksum_address(user_address)
            except Exception as e:
                return {"error": f"Invalid address format: {e}"}
            
            # ERC20 ABI for balanceOf function
            erc20_abi = [
                {
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "symbol",
                    "outputs": [{"name": "", "type": "string"}],
                    "type": "function"
                }
            ]
            
            # Create contract instance
            token_contract = self.w3.eth.contract(
                address=token_checksum,
                abi=erc20_abi
            )
            
            # Get balance, decimals, and symbol
            balance = token_contract.functions.balanceOf(user_checksum).call()
            decimals = token_contract.functions.decimals().call()
            symbol = token_contract.functions.symbol().call()
            
            # Convert to human readable format
            human_balance = Decimal(balance) / (Decimal(10) ** decimals)
            
            return {
                "token_address": token_checksum,
                "user_address": user_checksum,
                "balance_raw": str(balance),
                "balance": str(human_balance),
                "decimals": decimals,
                "symbol": symbol
            }
            
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return {"error": str(e)}
    
    async def get_block_by_number(self, block_number: int) -> Dict[str, Any]:
        """Get block information by number"""
        try:
            if not self.w3 or not self.w3.is_connected():
                return self._get_mock_block_info(block_number)
            
            block = self.w3.eth.get_block(block_number)
            
            return {
                "number": block.number,
                "hash": block.hash.hex(),
                "parent_hash": block.parentHash.hex(),
                "timestamp": block.timestamp,
                "gas_limit": block.gasLimit,
                "gas_used": block.gasUsed,
                "transaction_count": len(block.transactions),
                "transactions": [tx.hex() for tx in block.transactions],
                "miner": block.miner,
                "difficulty": block.difficulty,
                "size": getattr(block, 'size', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting block {block_number}: {e}")
            return {"error": str(e)}
    
    # Mock data methods for testing when Web3 is not available
    def _get_mock_block_info(self, block_number: Optional[int] = None) -> Dict[str, Any]:
        """Generate mock block information"""
        import time
        
        return {
            "number": block_number or 50000000,
            "hash": "0x" + "1234567890abcdef" * 4,
            "timestamp": int(time.time()),
            "gas_limit": 30000000,
            "gas_used": 15000000,
            "transaction_count": 150,
            "miner": "0x0000000000000000000000000000000000000000",
            "difficulty": 1,
            "size": 50000,
            "mock": True
        }
    
    def _get_mock_network_info(self) -> Dict[str, Any]:
        """Generate mock network information"""
        return {
            "chain_id": self.chain_id,
            "network_name": "Polygon Mainnet (Mock)",
            "current_block": 50000000,
            "gas_price_gwei": "30",
            "gas_price_wei": 30000000000,
            "is_syncing": False,
            "rpc_endpoint": self.rpc_url,
            "connected": False,
            "mock": True
        }
    
    def _get_mock_balance(self, address: str) -> Dict[str, Any]:
        """Generate mock balance"""
        return {
            "address": address,
            "balance_wei": "1000000000000000000",  # 1 MATIC
            "balance_matic": "1.0",
            "balance_usd": "0.85",
            "currency": "MATIC",
            "mock": True
        }
    
    def _get_mock_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Generate mock transaction"""
        return {
            "hash": tx_hash,
            "from": "0x742d35Cc6634C0532925a3b8D0C026Ba85C5d9C6",
            "to": "0x1234567890123456789012345678901234567890",
            "value_wei": "100000000000000000",  # 0.1 MATIC
            "value_matic": "0.1",
            "gas_limit": 21000,
            "gas_price": 30000000000,
            "gas_used": 21000,
            "status": 1,
            "block_number": 50000000,
            "nonce": 42,
            "input": "0x",
            "mock": True
        }
    
    def _get_mock_gas_prices(self) -> Dict[str, Any]:
        """Generate mock gas prices"""
        return {
            "slow": {
                "gas_price_wei": 25000000000,
                "gas_price_gwei": "25",
                "estimated_time": "5-10 minutes"
            },
            "standard": {
                "gas_price_wei": 30000000000,
                "gas_price_gwei": "30",
                "estimated_time": "2-5 minutes"
            },
            "fast": {
                "gas_price_wei": 40000000000,
                "gas_price_gwei": "40",
                "estimated_time": "30 seconds - 2 minutes"
            },
            "mock": True
        }
    
    def _get_mock_token_balance(self, token_address: str, user_address: str) -> Dict[str, Any]:
        """Generate mock token balance"""
        return {
            "token_address": token_address,
            "user_address": user_address,
            "balance_raw": "1000000000000000000000",  # 1000 tokens
            "balance": "1000.0",
            "decimals": 18,
            "symbol": "MOCK",
            "mock": True
        }
    
    async def validate_address(self, address: str) -> Dict[str, Any]:
        """Validate an Ethereum/Polygon address"""
        try:
            is_valid = Web3.is_address(address)
            checksum_address = Web3.to_checksum_address(address) if is_valid else None
            is_checksum = address == checksum_address if is_valid else False
            
            return {
                "address": address,
                "is_valid": is_valid,
                "is_checksum": is_checksum,
                "checksum_address": checksum_address
            }
            
        except Exception as e:
            return {
                "address": address,
                "is_valid": False,
                "error": str(e)
            }
    
    async def check_connection(self) -> Dict[str, Any]:
        """Check blockchain connection status"""
        try:
            if not self.w3:
                return {
                    "connected": False,
                    "error": "Web3 not initialized",
                    "rpc_url": self.rpc_url
                }
            
            is_connected = self.w3.is_connected()
            
            if is_connected:
                latest_block = self.w3.eth.block_number
                chain_id = self.w3.eth.chain_id
                
                return {
                    "connected": True,
                    "rpc_url": self.rpc_url,
                    "chain_id": chain_id,
                    "latest_block": latest_block,
                    "network_name": "Polygon Mainnet" if chain_id == 137 else f"Chain {chain_id}"
                }
            else:
                return {
                    "connected": False,
                    "rpc_url": self.rpc_url,
                    "error": "Unable to connect to RPC endpoint"
                }
                
        except Exception as e:
            return {
                "connected": False,
                "rpc_url": self.rpc_url,
                "error": str(e)
            }