# -*- coding: utf-8 -*-
"""
Today Live Publishing Tracker (K-Market & EasyTax Global Orchestrator)
"""

import sys
import datetime
import logging
from typing import Dict, Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from brands.aura.aura_live_tracker import AuraLiveTracker
except ImportError:
    AuraLiveTracker = None

try:
    from brands.insurance.insurance_live_tracker import InsuranceLiveTracker
except ImportError:
    InsuranceLiveTracker = None

try:
    from brands.stock.stock_live_tracker import StockLiveTracker
except ImportError:
    StockLiveTracker = None

logger = logging.getLogger("TodayLiveTracker")


class TodayLiveTracker:
    """Live Tracker Orchestrator"""

    def __init__(self):
        self.aura_tracker = AuraLiveTracker() if AuraLiveTracker else None
        self.insurance_tracker = InsuranceLiveTracker() if InsuranceLiveTracker else None
        self.stock_tracker = StockLiveTracker() if StockLiveTracker else None

    def get_all_live_feed(self) -> Dict[str, Any]:
        now = datetime.datetime.now()
        today_str = now.strftime("%Y-%m-%d")

        aura_data = self.aura_tracker.get_live_status() if self.aura_tracker else {"status": "inactive"}
        insurance_data = self.insurance_tracker.get_live_status() if self.insurance_tracker else {"status": "inactive"}
        stock_data = self.stock_tracker.get_live_status() if self.stock_tracker else {"status": "inactive"}

        return {
            "date": today_str,
            "brands": {
                "aura": aura_data,
                "insurance": insurance_data,
                "stock": stock_data
            }
        }
