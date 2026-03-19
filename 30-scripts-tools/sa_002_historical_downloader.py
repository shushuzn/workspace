#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis - SA-002: Historical Data Downloader
Download historical K-line data with multiple timeframes and adjustment
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import random

class HistoricalDataDownloader:
    """Download and manage historical stock data"""
    
    def __init__(self, data_dir: str = "60-DATA/stock_historical"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.timeframes = {
            "1d": {"name": "Daily", "interval": 86400},
            "1w": {"name": "Weekly", "interval": 604800},
            "1mo": {"name": "Monthly", "interval": 2592000},
        }
        
        self.adjustment_types = ["none", "forward", "backward"]
        
        self.download_log = self._load_download_log()
    
    def _load_download_log(self) -> Dict:
        """Load download log"""
        log_file = self.data_dir / "download_log.json"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "version": "1.0",
            "downloads": [],
            "stats": {
                "total_downloads": 0,
                "successful": 0,
                "failed": 0,
                "total_records": 0,
            }
        }
    
    def _save_download_log(self):
        """Save download log"""
        log_file = self.data_dir / "download_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.download_log, f, ensure_ascii=False, indent=2)
    
    def download_history(self, symbol: str, timeframe: str = "1d",
                        start_date: str = None, end_date: str = None,
                        adjustment: str = "forward") -> Optional[Dict]:
        """
        Download historical data for a stock
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe (1d/1w/1mo)
            start_date: Start date (YYYY-MM-DD), default 1 year ago
            end_date: End date (YYYY-MM-DD), default today
            adjustment: Adjustment type (none/forward/backward)
            
        Returns:
            Dict with historical data or None if failed
        """
        if timeframe not in self.timeframes:
            print(f"[ERROR] Unknown timeframe: {timeframe}")
            return None
        
        if adjustment not in self.adjustment_types:
            print(f"[ERROR] Unknown adjustment: {adjustment}")
            return None
        
        # Set default dates
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        # Check cache
        cache_key = f"{symbol}_{timeframe}_{adjustment}_{start_date}_{end_date}"
        cache_file = self.data_dir / f"{cache_key.replace('-', '_')}.json"
        
        if cache_file.exists():
            print(f"[INFO] Loading from cache: {cache_file.name}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Generate simulated data
        print(f"[INFO] Downloading {symbol} {timeframe} data from {start_date} to {end_date}")
        data = self._generate_historical_data(
            symbol, timeframe, start_date, end_date, adjustment
        )
        
        if data:
            # Save to cache
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Log download
            self._log_download(symbol, timeframe, len(data["candles"]), success=True)
            
            return data
        else:
            self._log_download(symbol, timeframe, 0, success=False)
            return None
    
    def _generate_historical_data(self, symbol: str, timeframe: str,
                                  start_date: str, end_date: str,
                                  adjustment: str) -> Dict:
        """Generate simulated historical data"""
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        candles = []
        
        # Base price (random based on symbol)
        base_price = 100 + (hash(symbol) % 200)
        current_price = base_price
        
        current = start
        while current <= end:
            # Skip weekends for daily data
            if timeframe == "1d" and current.weekday() >= 5:
                current += timedelta(days=1)
                continue
            
            # Generate OHLCV
            daily_change = random.uniform(-0.03, 0.03)
            open_price = current_price
            close_price = current_price * (1 + daily_change)
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.02))
            volume = int(random.uniform(5000000, 50000000))
            
            candle = {
                "date": current.strftime("%Y-%m-%d"),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume,
                "amount": round(volume * close_price, 2)
            }
            
            candles.append(candle)
            
            current_price = close_price
            
            # Move to next period
            if timeframe == "1d":
                current += timedelta(days=1)
            elif timeframe == "1w":
                current += timedelta(weeks=1)
            elif timeframe == "1mo":
                current += timedelta(days=30)
        
        # Apply adjustment if needed
        if adjustment != "none":
            candles = self._apply_adjustment(candles, adjustment)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "adjustment": adjustment,
            "start_date": start_date,
            "end_date": end_date,
            "candle_count": len(candles),
            "candles": candles,
            "downloaded_at": datetime.now().isoformat()
        }
    
    def _apply_adjustment(self, candles: List[Dict], adjustment: str) -> List[Dict]:
        """Apply forward or backward adjustment"""
        if not candles:
            return candles
        
        if adjustment == "forward":
            # Forward adjustment (adjust historical prices to current)
            # Simulate a split factor
            split_factor = 1.0 + (hash(str(len(candles))) % 10) / 100
            
            for candle in candles:
                candle["open"] = round(candle["open"] * split_factor, 2)
                candle["high"] = round(candle["high"] * split_factor, 2)
                candle["low"] = round(candle["low"] * split_factor, 2)
                candle["close"] = round(candle["close"] * split_factor, 2)
        
        elif adjustment == "backward":
            # Backward adjustment (adjust current prices to historical)
            split_factor = 1.0 - (hash(str(len(candles))) % 10) / 200
            
            for candle in candles:
                candle["open"] = round(candle["open"] * split_factor, 2)
                candle["high"] = round(candle["high"] * split_factor, 2)
                candle["low"] = round(candle["low"] * split_factor, 2)
                candle["close"] = round(candle["close"] * split_factor, 2)
        
        return candles
    
    def get_latest_candle(self, symbol: str, timeframe: str = "1d") -> Optional[Dict]:
        """Get the latest candle for a symbol"""
        # Find most recent cache file
        pattern = f"*{symbol}*{timeframe}*.json"
        cache_files = list(self.data_dir.glob(pattern))
        
        if not cache_files:
            return None
        
        # Get most recent
        latest_file = max(cache_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data["candles"]:
            return data["candles"][-1]
        
        return None
    
    def get_statistics(self, symbol: str, timeframe: str = "1d") -> Optional[Dict]:
        """Calculate statistics from historical data"""
        # Find cache file
        pattern = f"*{symbol}*{timeframe}*.json"
        cache_files = list(self.data_dir.glob(pattern))
        
        if not cache_files:
            return None
        
        latest_file = max(cache_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        candles = data["candles"]
        if not candles:
            return None
        
        closes = [c["close"] for c in candles]
        volumes = [c["volume"] for c in candles]
        
        # Calculate statistics
        stats = {
            "symbol": symbol,
            "timeframe": timeframe,
            "period": f"{data['start_date']} to {data['end_date']}",
            "candle_count": len(candles),
            "price_stats": {
                "current": closes[-1],
                "open_period": candles[0]["open"],
                "high": max(c["high"] for c in candles),
                "low": min(c["low"] for c in candles),
                "change": closes[-1] - candles[0]["open"],
                "change_percent": ((closes[-1] - candles[0]["open"]) / candles[0]["open"]) * 100
            },
            "volume_stats": {
                "average": sum(volumes) / len(volumes),
                "max": max(volumes),
                "min": min(volumes),
                "total": sum(volumes)
            }
        }
        
        return stats
    
    def _log_download(self, symbol: str, timeframe: str, records: int, success: bool):
        """Log download attempt"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "timeframe": timeframe,
            "records": records,
            "success": success
        }
        
        self.download_log["downloads"].append(log_entry)
        self.download_log["stats"]["total_downloads"] += 1
        self.download_log["stats"]["total_records"] += records
        
        if success:
            self.download_log["stats"]["successful"] += 1
        else:
            self.download_log["stats"]["failed"] += 1
        
        # Keep only last 500 entries
        self.download_log["downloads"] = self.download_log["downloads"][-500:]
        
        self._save_download_log()
    
    def get_stats(self) -> Dict:
        """Get download statistics"""
        return self.download_log["stats"].copy()
    
    def display_status(self) -> str:
        """Display downloader status"""
        stats = self.get_stats()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 16 + "Historical Data Downloader Status")
        output.append("=" * 70)
        
        output.append(f"\n[Timeframes]")
        for tf_id, tf in self.timeframes.items():
            output.append(f"  {tf_id:5} - {tf['name']}")
        
        output.append(f"\n[Adjustment Types]")
        for adj in self.adjustment_types:
            output.append(f"  - {adj}")
        
        output.append(f"\n[Statistics]")
        output.append(f"  Total Downloads:  {stats['total_downloads']}")
        output.append(f"  Successful:       {stats['successful']}")
        output.append(f"  Failed:           {stats['failed']}")
        output.append(f"  Total Records:    {stats['total_records']:,}")
        
        output.append("\n" + "=" * 70 + "\n")
        
        return "\n".join(output)


def main():
    """Test entry point"""
    print("=" * 70)
    print(" " * 13 + "SA-002: Historical Data Downloader")
    print("=" * 70)
    
    downloader = HistoricalDataDownloader()
    
    # Test 1: Display status
    print(downloader.display_status())
    
    # Test 2: Download daily data
    print("\n[Test 1] Download Daily Data (AAPL, 1 year)")
    print("-" * 70)
    data = downloader.download_history("AAPL", timeframe="1d", adjustment="forward")
    if data:
        print(f"  Symbol:       {data['symbol']}")
        print(f"  Timeframe:    {data['timeframe']}")
        print(f"  Adjustment:   {data['adjustment']}")
        print(f"  Period:       {data['start_date']} to {data['end_date']}")
        print(f"  Candle Count: {data['candle_count']}")
        print(f"\n  First Candle: {data['candles'][0]}")
        print(f"  Last Candle:  {data['candles'][-1]}")
    
    # Test 3: Download weekly data
    print("\n[Test 2] Download Weekly Data (600519.SS, 2 years)")
    print("-" * 70)
    start = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
    data = downloader.download_history("600519.SS", timeframe="1w", start_date=start, adjustment="none")
    if data:
        print(f"  Candle Count: {data['candle_count']}")
        print(f"  First:        {data['candles'][0]['date']} - {data['candles'][0]['close']}")
        print(f"  Last:         {data['candles'][-1]['date']} - {data['candles'][-1]['close']}")
    
    # Test 4: Get statistics
    print("\n[Test 3] Get Statistics")
    print("-" * 70)
    stats = downloader.get_statistics("AAPL", timeframe="1d")
    if stats:
        print(f"  Symbol:           {stats['symbol']}")
        print(f"  Period:           {stats['period']}")
        print(f"  Candle Count:     {stats['candle_count']}")
        print(f"\n  Price Statistics:")
        print(f"    Current:        {stats['price_stats']['current']:.2f}")
        print(f"    Period Open:    {stats['price_stats']['open_period']:.2f}")
        print(f"    High:           {stats['price_stats']['high']:.2f}")
        print(f"    Low:            {stats['price_stats']['low']:.2f}")
        print(f"    Change:         {stats['price_stats']['change']:+.2f} ({stats['price_stats']['change_percent']:+.2f}%)")
        print(f"\n  Volume Statistics:")
        print(f"    Average:        {stats['volume_stats']['average']:,.0f}")
        print(f"    Max:            {stats['volume_stats']['max']:,}")
        print(f"    Total:          {stats['volume_stats']['total']:,}")
    
    # Test 5: Get latest candle
    print("\n[Test 4] Get Latest Candle")
    print("-" * 70)
    latest = downloader.get_latest_candle("AAPL", timeframe="1d")
    if latest:
        print(f"  Date:   {latest['date']}")
        print(f"  Open:   {latest['open']}")
        print(f"  High:   {latest['high']}")
        print(f"  Low:    {latest['low']}")
        print(f"  Close:  {latest['close']}")
        print(f"  Volume: {latest['volume']:,}")
    
    # Test 6: Final stats
    print("\n[Test 5] Final Statistics")
    print("-" * 70)
    stats = downloader.get_stats()
    print(f"  Total Downloads:  {stats['total_downloads']}")
    print(f"  Successful:       {stats['successful']}")
    print(f"  Failed:           {stats['failed']}")
    print(f"  Total Records:    {stats['total_records']:,}")
    
    print("\n[OK] SA-002 Historical Data Downloader test completed")

if __name__ == "__main__":
    main()
