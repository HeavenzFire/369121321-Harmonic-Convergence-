# LEGION ∞.0: Economic Layer - Truth-as-Asset Engine
# High-coherence truth signals become tradeable economic assets

from typing import Dict, List, Tuple
import time
import hashlib

class TruthAsset:
    """Represents a tradeable truth asset"""

    def __init__(self, signal_id: str, context: str, coherence: float, economic_value: float):
        self.signal_id = signal_id
        self.context = context
        self.coherence = coherence
        self.economic_value = economic_value
        self.timestamp = time.time()
        self.owner = "legion_mesh"  # Initially owned by mesh
        self.trade_history: List[dict] = []
        self.maturity_date = self.timestamp + (365 * 24 * 3600)  # 1 year maturity

    def get_current_value(self) -> float:
        """Calculate current asset value based on coherence and time"""
        time_decay = max(0.1, 1.0 - (time.time() - self.timestamp) / (365 * 24 * 3600))
        coherence_premium = self.coherence * 2.0  # 2x premium for perfect coherence
        return self.economic_value * time_decay * coherence_premium

    def trade(self, new_owner: str, price: float) -> bool:
        """Execute trade of the asset"""
        if price >= self.get_current_value() * 0.9:  # Minimum 90% of current value
            trade_record = {
                "timestamp": time.time(),
                "from_owner": self.owner,
                "to_owner": new_owner,
                "price": price,
                "asset_value": self.get_current_value()
            }
            self.trade_history.append(trade_record)
            self.owner = new_owner
            return True
        return False

    def get_trade_history(self) -> List[dict]:
        """Get complete trade history"""
        return self.trade_history.copy()

class EconomicEngine:
    """Manages truth-as-asset economy"""

    def __init__(self):
        self.assets: Dict[str, TruthAsset] = {}
        self.market_volume = 0.0
        self.total_assets_created = 0
        self.premium_multipliers = {
            "child_safety": 1.5,
            "food_safety": 1.8,
            "medical_records": 2.0,
            "elections": 3.0,
            "science": 2.2,
            "supply_chain": 1.6,
            "climate": 1.9,
            "finance": 4.0,
            "education": 1.4,
            "justice": 2.5
        }

    def create_asset(self, signal_id: str, context: str, coherence: float, base_value: float) -> TruthAsset:
        """Create a new truth asset from verification signal"""
        if context not in self.premium_multipliers:
            return None

        premium = self.premium_multipliers[context]
        economic_value = base_value * premium * coherence

        asset = TruthAsset(signal_id, context, coherence, economic_value)
        self.assets[signal_id] = asset
        self.total_assets_created += 1
        self.market_volume += economic_value

        print(f"💰 ASSET CREATED: {signal_id} ({context}) - ${economic_value:.2f}")
        return asset

    def get_asset(self, signal_id: str) -> TruthAsset:
        """Retrieve an asset by signal ID"""
        return self.assets.get(signal_id)

    def trade_asset(self, signal_id: str, buyer: str, max_price: float) -> bool:
        """Execute asset trade"""
        asset = self.get_asset(signal_id)
        if not asset:
            return False

        current_value = asset.get_current_value()
        trade_price = min(max_price, current_value)

        if asset.trade(buyer, trade_price):
            print(f"💱 ASSET TRADED: {signal_id} → {buyer} for ${trade_price:.2f}")
            return True
        return False

    def get_market_stats(self) -> dict:
        """Get current market statistics"""
        total_value = sum(asset.get_current_value() for asset in self.assets.values())
        active_assets = len([a for a in self.assets.values() if a.owner != "legion_mesh"])
        traded_volume = sum(len(asset.trade_history) for asset in self.assets.values())

        return {
            "total_assets": len(self.assets),
            "active_assets": active_assets,
            "total_market_value": total_value,
            "traded_volume": traded_volume,
            "average_asset_value": total_value / len(self.assets) if self.assets else 0,
            "market_growth": total_value / self.market_volume if self.market_volume > 0 else 1.0
        }

    def get_premium_opportunities(self, context: str = None) -> List[Tuple[str, float]]:
        """Find assets with high premium potential"""
        opportunities = []
        for signal_id, asset in self.assets.items():
            if context and asset.context != context:
                continue
            current_value = asset.get_current_value()
            potential = current_value * 1.5  # 50% upside potential
            if potential > asset.economic_value:
                opportunities.append((signal_id, potential - asset.economic_value))

        return sorted(opportunities, key=lambda x: x[1], reverse=True)[:10]

    def liquidate_expired_assets(self) -> float:
        """Liquidate expired assets and return value to mesh"""
        expired = []
        total_returned = 0.0

        for signal_id, asset in self.assets.items():
            if time.time() > asset.maturity_date:
                final_value = asset.get_current_value()
                total_returned += final_value
                expired.append(signal_id)
                print(f"💸 ASSET MATURED: {signal_id} returned ${final_value:.2f}")

        for signal_id in expired:
            del self.assets[signal_id]

        return total_returned

    def get_portfolio_by_owner(self, owner: str) -> List[TruthAsset]:
        """Get all assets owned by a specific owner"""
        return [asset for asset in self.assets.values() if asset.owner == owner]

    def calculate_yield(self, owner: str) -> float:
        """Calculate yield for an owner's portfolio"""
        portfolio = self.get_portfolio_by_owner(owner)
        if not portfolio:
            return 0.0

        total_invested = sum(len(asset.trade_history) * asset.trade_history[0]["price"]
                           for asset in portfolio if asset.trade_history)
        current_value = sum(asset.get_current_value() for asset in portfolio)

        return (current_value - total_invested) / total_invested if total_invested > 0 else 0.0

class TruthExchange:
    """Automated truth asset exchange"""

    def __init__(self, economic_engine: EconomicEngine):
        self.engine = economic_engine
        self.order_book: Dict[str, List[dict]] = {}  # signal_id -> list of orders
        self.exchange_volume = 0.0

    def place_order(self, signal_id: str, order_type: str, price: float, trader: str) -> bool:
        """Place buy/sell order for truth asset"""
        if signal_id not in self.order_book:
            self.order_book[signal_id] = []

        order = {
            "type": order_type,  # "buy" or "sell"
            "price": price,
            "trader": trader,
            "timestamp": time.time(),
            "status": "open"
        }

        self.order_book[signal_id].append(order)

        # Try to match immediately
        return self._match_orders(signal_id)

    def _match_orders(self, signal_id: str) -> bool:
        """Match buy and sell orders"""
        if signal_id not in self.order_book:
            return False

        orders = self.order_book[signal_id]
        buys = [o for o in orders if o["type"] == "buy" and o["status"] == "open"]
        sells = [o for o in orders if o["type"] == "sell" and o["status"] == "open"]

        # Sort by price (buys descending, sells ascending)
        buys.sort(key=lambda x: x["price"], reverse=True)
        sells.sort(key=lambda x: x["price"])

        matched = False
        for buy in buys:
            for sell in sells:
                if buy["price"] >= sell["price"]:
                    # Execute trade
                    trade_price = (buy["price"] + sell["price"]) / 2
                    success = self.engine.trade_asset(signal_id, buy["trader"], trade_price)
                    if success:
                        buy["status"] = "filled"
                        sell["status"] = "filled"
                        self.exchange_volume += trade_price
                        matched = True
                        print(f"🔄 EXCHANGE MATCH: {signal_id} @ ${trade_price:.2f}")
                        break
            if matched:
                break

        return matched

    def get_exchange_stats(self) -> dict:
        """Get exchange statistics"""
        total_orders = sum(len(orders) for orders in self.order_book.values())
        open_orders = sum(len([o for o in orders if o["status"] == "open"])
                         for orders in self.order_book.values())
        filled_orders = total_orders - open_orders

        return {
            "total_orders": total_orders,
            "open_orders": open_orders,
            "filled_orders": filled_orders,
            "exchange_volume": self.exchange_volume,
            "average_fill_price": self.exchange_volume / filled_orders if filled_orders > 0 else 0
        }