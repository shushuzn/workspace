"""Stock PRO v12.0 - Test Suite"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from stock_pro import analyze, analyze_multiple, StockScreener, PortfolioManager
from stock_pro.core import A, F, P

def test_analyze():
    """Test single stock analysis"""
    print("Testing analyze()...")
    result = analyze("NVDA")
    assert result["symbol"] == "NVDA"
    assert result["score"] > 0
    assert result["price"] > 0
    assert "fetched_at" in result, "Missing fetched_at timestamp"
    assert "price_source" in result, "Missing price_source"
    print(f"  PASS: NVDA score={result['score']}, upside={result['upside']:.1f}%")
    print(f"  Data: fetched_at={result['fetched_at']}, source={result['price_source']}")
    return True

def test_analyze_multiple():
    """Test multiple stocks"""
    print("Testing analyze_multiple()...")
    results = analyze_multiple(["NVDA", "META", "JPM"])
    assert len(results) == 3
    print(f"  PASS: Analyzed {len(results)} stocks")
    return True

def test_screener():
    """Test screener"""
    print("Testing StockScreener...")
    s = StockScreener(min_score=60, min_upside=15, max_pe=40)
    results = s.screen()
    assert len(results) > 0
    print(f"  PASS: Found {len(results)} stocks matching criteria")
    return True

def test_portfolio():
    """Test portfolio"""
    print("Testing PortfolioManager...")
    pm = PortfolioManager()
    # Just test instantiation
    assert hasattr(pm, 'positions')
    print("  PASS: PortfolioManager initialized")
    return True

def test_data_coverage():
    """Test data coverage"""
    print("Testing data coverage...")
    print(f"  Stocks: {len(F)}")
    print(f"  Analysts: {len(A)}")
    print(f"  Prices: {len(P)}")
    assert len(F) == len(A) == len(P)
    print(f"  PASS: All data sets aligned ({len(F)} stocks)")
    return True

def run_all():
    """Run all tests"""
    print("=" * 50)
    print("Stock PRO v12.0 - Test Suite")
    print("=" * 50)
    print()

    tests = [test_data_coverage, test_analyze, test_analyze_multiple, test_screener, test_portfolio]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            failed += 1
        print()

    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    return failed == 0

if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
