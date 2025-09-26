"""
ASI Alliance Agent Reasoning
AI-powered portfolio analysis and recommendations
"""

import aiohttp
import logging
import json
import random
from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)

class ASIAgentReasoning:
    def __init__(self, endpoint: str = ""):
        self.endpoint = endpoint
        self.agent_id = "portfolio_advisor_agent"
        
        # Risk assessment parameters
        self.risk_thresholds = {
            "conservative": {"max_allocation": 5, "min_confidence": 0.8},
            "moderate": {"max_allocation": 10, "min_confidence": 0.7},
            "aggressive": {"max_allocation": 20, "min_confidence": 0.6}
        }
    
    async def generate_insight(
        self, 
        token_symbol: str,
        portfolio_data: Dict[str, Any],
        market_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI-powered portfolio insight"""
        try:
            logger.info(f"Generating insight for {token_symbol}")
            
            # If we have a real ASI Alliance endpoint, use it
            if self.endpoint and self.endpoint != "":
                real_insight = await self._fetch_asi_insight(token_symbol, portfolio_data, market_data, user_context)
                if real_insight:
                    return real_insight
            
            # Generate mock AI insight for testing
            insight = await self._generate_mock_insight(token_symbol, portfolio_data, market_data, user_context)
            return insight
            
        except Exception as e:
            logger.error(f"Error generating insight: {e}")
            return self._generate_fallback_insight(token_symbol)
    
    def _generate_fallback_insight(self, token_symbol: str) -> Dict[str, Any]:
        """Generate fallback insight when other methods fail"""
        return {
            "token_symbol": token_symbol,
            "action": "hold",
            "confidence": 0.5,
            "reasoning": f"Unable to generate detailed analysis for {token_symbol}. Recommending hold position.",
            "risk_assessment": "moderate",
            "suggested_amount_percentage": 0.0,
            "price_target": None,
            "stop_loss": None,
            "timeframe": "short-term",
            "source": "fallback"
        }
    
    async def batch_analyze_portfolio(self, portfolio_tokens: List[str], portfolio_data: Dict[str, Any], market_data: Dict[str, Any], user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze multiple tokens in a portfolio"""
        try:
            insights = []
            
            for token_symbol in portfolio_tokens:
                insight = await self.generate_insight(
                    token_symbol=token_symbol,
                    portfolio_data=portfolio_data,
                    market_data=market_data,
                    user_context=user_context
                )
                insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            return []
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get ASI Alliance agent status"""
        try:
            if not self.endpoint:
                return {
                    "status": "mock_mode",
                    "agent_id": self.agent_id,
                    "capabilities": ["portfolio_analysis", "risk_assessment", "market_sentiment"],
                    "version": "1.0.0"
                }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.endpoint}/api/agent/status") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            return {"status": "error", "message": str(e)}

    async def _fetch_asi_insight(
        self,
        token_symbol: str,
        portfolio_data: Dict[str, Any],
        market_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Fetch insight from real ASI Alliance agent"""
        try:
            # Prepare the request payload for ASI Alliance
            payload = {
                "agent_id": self.agent_id,
                "task": "portfolio_analysis",
                "data": {
                    "token": token_symbol,
                    "portfolio": portfolio_data,
                    "market": market_data,
                    "user": user_context
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.endpoint}/api/agent/analyze",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_asi_response(data)
                    else:
                        logger.error(f"ASI API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching ASI insight: {e}")
            return None
    
    def _parse_asi_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse ASI Alliance agent response"""
        try:
            # Parse the agent's response into our standard format
            result = response.get("result", {})
            
            return {
                "action": result.get("recommendation", "hold"),
                "confidence": float(result.get("confidence", 0.7)),
                "reasoning": result.get("analysis", "AI analysis completed"),
                "risk_assessment": result.get("risk", "moderate"),
                "suggested_amount_percentage": float(result.get("allocation", 5.0)),
                "price_target": result.get("price_target"),
                "stop_loss": result.get("stop_loss"),
                "timeframe": result.get("timeframe", "medium-term"),
                "source": "asi_alliance"
            }
            
        except Exception as e:
            logger.error(f"Error parsing ASI response: {e}")
            return self._generate_fallback_insight("UNKNOWN")
    
    async def _generate_mock_insight(
        self,
        token_symbol: str,
        portfolio_data: Dict[str, Any],
        market_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate sophisticated mock AI insight"""
        try:
            # Analyze current portfolio allocation
            current_allocation = self._analyze_portfolio_allocation(token_symbol, portfolio_data)
            
            # Analyze market conditions
            market_sentiment = self._analyze_market_sentiment(token_symbol, market_data)
            
            # Get user risk profile
            risk_tolerance = user_context.get("risk_tolerance", "moderate")
            
            # Generate recommendation based on analysis
            recommendation = self._generate_recommendation(
                token_symbol,
                current_allocation,
                market_sentiment,
                risk_tolerance
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating mock insight: {e}")
            return self._generate_fallback_insight(token_symbol)
    
    def _analyze_portfolio_allocation(self, token_symbol: str, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current portfolio allocation"""
        try:
            tokens = portfolio_data.get("tokens", [])
            total_value = Decimal("0")
            token_value = Decimal("0")
            
            # Calculate total portfolio value and token allocation
            for token in tokens:
                value = Decimal(token.get("value_usd", "0"))
                total_value += value
                
                if token.get("symbol", "").upper() == token_symbol.upper():
                    token_value = value
            
            allocation_percentage = float((token_value / total_value * 100) if total_value > 0 else 0)
            
            return {
                "current_allocation": allocation_percentage,
                "token_value": float(token_value),
                "total_portfolio_value": float(total_value),
                "is_overallocated": allocation_percentage > 15,  # Arbitrary threshold
                "is_underallocated": allocation_percentage < 2
            }
            
        except Exception as e:
            logger.error(f"Error analyzing allocation: {e}")
            return {"current_allocation": 0, "token_value": 0, "total_portfolio_value": 0}
    
    def _analyze_market_sentiment(self, token_symbol: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market sentiment and conditions"""
        try:
            token_data = market_data.get(token_symbol.upper(), {})
            price = token_data.get("price", Decimal("0"))
            confidence = token_data.get("confidence", Decimal("0"))
            
            # Mock technical analysis
            technical_score = random.uniform(0.3, 0.9)  # Simulate technical analysis
            momentum_score = random.uniform(0.2, 0.8)   # Simulate momentum analysis
            volatility_score = float(confidence / price) if price > 0 else 0.5
            
            # Overall sentiment
            overall_sentiment = (technical_score + momentum_score + (1 - volatility_score)) / 3
            
            return {
                "sentiment_score": overall_sentiment,
                "technical_score": technical_score,
                "momentum_score": momentum_score,
                "volatility_score": volatility_score,
                "current_price": float(price),
                "price_confidence": float(confidence)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {"sentiment_score": 0.5, "technical_score": 0.5, "momentum_score": 0.5}
    
    def _generate_recommendation(
        self,
        token_symbol: str,
        allocation_analysis: Dict[str, Any],
        market_analysis: Dict[str, Any],
        risk_tolerance: str
    ) -> Dict[str, Any]:
        """Generate trading recommendation based on analysis"""
        try:
            current_allocation = allocation_analysis["current_allocation"]
            sentiment_score = market_analysis["sentiment_score"]
            risk_params = self.risk_thresholds.get(risk_tolerance, self.risk_thresholds["moderate"])
            
            # Decision logic
            action = "hold"
            confidence = 0.6
            reasoning_parts = []
            suggested_percentage = 0.0
            
            # Buy signals
            if sentiment_score > 0.7 and current_allocation < risk_params["max_allocation"]:
                action = "buy"
                confidence = min(0.95, sentiment_score + 0.1)
                suggested_percentage = min(5.0, risk_params["max_allocation"] - current_allocation)
                reasoning_parts.append(f"Strong market sentiment ({sentiment_score:.2f})")
                reasoning_parts.append(f"Current allocation ({current_allocation:.1f}%) below target")
            
            # Sell signals
            elif sentiment_score < 0.4 or current_allocation > risk_params["max_allocation"] * 1.5:
                action = "sell"
                confidence = min(0.9, 1 - sentiment_score + 0.2)
                suggested_percentage = min(current_allocation * 0.3, 10.0)  # Sell up to 30% or 10%
                
                if sentiment_score < 0.4:
                    reasoning_parts.append(f"Weak market sentiment ({sentiment_score:.2f})")
                if current_allocation > risk_params["max_allocation"] * 1.5:
                    reasoning_parts.append(f"Overallocated ({current_allocation:.1f}%)")
            
            # Hold signals
            else:
                reasoning_parts.append(f"Balanced allocation ({current_allocation:.1f}%)")
                reasoning_parts.append(f"Neutral market conditions ({sentiment_score:.2f})")
                confidence = 0.7
            
            # Generate reasoning text
            reasoning = f"Analysis for {token_symbol}: " + ". ".join(reasoning_parts)
            
            # Risk assessment
            risk_level = "low" if confidence > 0.8 else "moderate" if confidence > 0.6 else "high"
            
            # Price targets (mock)
            current_price = market_analysis.get("current_price", 100)
            price_target = None
            stop_loss = None
            
            if action == "buy":
                price_target = current_price * random.uniform(1.05, 1.25)  # 5-25% upside
                stop_loss = current_price * random.uniform(0.85, 0.95)     # 5-15% downside
            elif action == "sell":
                stop_loss = current_price * random.uniform(0.80, 0.90)     # 10-20% stop loss
            
            return {
                "token_symbol": token_symbol,
                "action": action,
                "confidence": confidence,
                "reasoning": reasoning,
                "risk_assessment": risk_level,
                "suggested_amount_percentage": suggested_percentage,
                "price_target": price_target,
                "stop_loss": stop_loss,
                "timeframe": "medium-term",
                "source": "asi_mock",
                "analysis_details": {
                    "portfolio_allocation": allocation_analysis,
                    "market_sentiment": market_analysis,
                    "risk_tolerance": risk_tolerance
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return self._generate_fallback_insight(token_symbol)