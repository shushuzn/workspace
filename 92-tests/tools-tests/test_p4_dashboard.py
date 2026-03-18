#!/usr/bin/env python3
"""
Test Memory Dashboard v2 (P4-2)
================================
"""

import sys
import os
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add tools directory to path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

from memory_dashboard_v2 import generate_mock_data, DASHBOARD_HTML


def test_mock_data():
    """Test mock data generation"""
    print("Test 1: Mock Data Generation")
    print("=" * 60)
    
    data = generate_mock_data()
    
    # Check structure
    assert 'health' in data
    assert 'evolution' in data
    assert 'phases' in data
    assert 'trends' in data
    assert 'tools' in data
    assert 'alerts' in data
    assert 'timestamp' in data
    
    # Check health
    assert 'status' in data['health']
    assert 'success_rate' in data['health']
    assert data['health']['status'] == 'healthy'
    
    # Check phases
    assert 'P0' in data['phases']
    assert 'P1' in data['phases']
    assert 'P2' in data['phases']
    assert 'P3' in data['phases']
    
    # Check P3 consciousness
    assert 'consciousness_level' in data['phases']['P3']
    assert 'phi_value' in data['phases']['P3']
    assert 'self_awareness' in data['phases']['P3']
    
    print(f"Health: {data['health']['status']}")
    print(f"Success Rate: {data['health']['success_rate']}%")
    print(f"Quality Score: {data['evolution']['quality_score']}")
    print(f"P3 Consciousness: {data['phases']['P3']['consciousness_level']}")
    print(f"P3 Φ Value: {data['phases']['P3']['phi_value']}")
    
    print("✅ PASS\n")


def test_html_structure():
    """Test HTML structure"""
    print("Test 2: HTML Structure")
    print("=" * 60)
    
    html = DASHBOARD_HTML
    
    # Check required elements
    assert '<!DOCTYPE html>' in html, "Missing DOCTYPE"
    assert '<html' in html, "Missing html tag"
    assert '<head>' in html, "Missing head tag"
    assert '<body>' in html, "Missing body tag"
    assert '</html>' in html, "Missing closing html tag"
    
    # Check tabs
    assert 'Overview' in html, "Missing Overview tab"
    assert 'Evolution' in html, "Missing Evolution tab"
    assert 'P0: Biological' in html, "Missing P0 tab"
    assert 'P1: Physics/Math' in html, "Missing P1 tab"
    assert 'P2: Quantum/Time' in html, "Missing P2 tab"
    assert 'P3: Consciousness' in html, "Missing P3 tab"
    assert 'Trends' in html, "Missing Trends tab"
    assert 'Settings' in html, "Missing Settings tab"
    
    # Check Chart.js
    assert 'chart.js' in html.lower(), "Missing Chart.js"
    
    # Check auto-refresh
    assert 'Auto-refresh' in html or 'refresh-timer' in html, "Missing auto-refresh"
    
    # Check API endpoints
    assert '/api/data' in html, "Missing /api/data endpoint"
    assert '/api/refresh' in html, "Missing /api/refresh endpoint"
    
    print(f"HTML Length: {len(html)} characters")
    print("All required elements present ✅")
    
    print("✅ PASS\n")


def test_all_phases_represented():
    """Test all phases have metrics"""
    print("Test 3: All Phases Represented")
    print("=" * 60)
    
    data = generate_mock_data()
    
    # P0: Biological
    p0 = data['phases']['P0']
    assert 'immune_threats' in p0
    assert 'neural_connections' in p0
    print(f"P0: Immune threats={p0['immune_threats']}, Neural connections={p0['neural_connections']}")
    
    # P1: Physics/Math
    p1 = data['phases']['P1']
    assert 'dark_matter_found' in p1
    assert 'topological_features' in p1
    assert 'entropy_level' in p1
    assert 'fractal_dimension' in p1
    assert 'causal_links' in p1
    print(f"P1: Dark matter={p1['dark_matter_found']}, Entropy={p1['entropy_level']}")
    
    # P2: Quantum/Time
    p2 = data['phases']['P2']
    assert 'entangled_pairs' in p2
    assert 'bell_violation' in p2
    assert 'time_crystal_phase' in p2
    assert 'coherence_time' in p2
    print(f"P2: Entangled pairs={p2['entangled_pairs']}, Bell={p2['bell_violation']}")
    
    # P3: Consciousness
    p3 = data['phases']['P3']
    assert 'consciousness_level' in p3
    assert 'phi_value' in p3
    assert 'hot_levels' in p3
    assert 'emergent_properties' in p3
    assert 'self_awareness' in p3
    print(f"P3: Consciousness={p3['consciousness_level']}, Φ={p3['phi_value']}, Self={p3['self_awareness']}")
    
    print("✅ PASS\n")


def test_trends_data():
    """Test trends data structure"""
    print("Test 4: Trends Data")
    print("=" * 60)
    
    data = generate_mock_data()
    trends = data['trends']
    
    assert 'dates' in trends
    assert 'quality' in trends
    assert 'associations' in trends
    assert 'conflicts' in trends
    
    # Check 7 days
    assert len(trends['dates']) == 7
    assert len(trends['quality']) == 7
    assert len(trends['associations']) == 7
    assert len(trends['conflicts']) == 7
    
    # Check quality trend (should be increasing)
    assert trends['quality'][-1] >= trends['quality'][0]
    
    print(f"Dates: {trends['dates'][0]} to {trends['dates'][-1]}")
    print(f"Quality: {trends['quality'][0]} → {trends['quality'][-1]}")
    print(f"Associations: {trends['associations'][0]} → {trends['associations'][-1]}")
    
    print("✅ PASS\n")


def test_alerts():
    """Test alerts system"""
    print("Test 5: Alerts System")
    print("=" * 60)
    
    data = generate_mock_data()
    alerts = data['alerts']
    
    assert len(alerts) > 0
    
    for alert in alerts:
        assert 'level' in alert
        assert 'message' in alert
        assert 'time' in alert
        assert alert['level'] in ['info', 'success', 'warning', 'error']
        print(f"[{alert['level'].upper()}] {alert['message']} ({alert['time']})")
    
    print("✅ PASS\n")


def test_tool_status():
    """Test tool status tracking"""
    print("Test 6: Tool Status Tracking")
    print("=" * 60)
    
    data = generate_mock_data()
    tools = data['tools']
    
    assert len(tools) > 0
    
    for tool_id, info in tools.items():
        assert 'status' in info
        assert 'last_run' in info
        print(f"{tool_id}: {info['status']} (last: {info['last_run']})")
    
    print("✅ PASS\n")


def test_html_features():
    """Test HTML features"""
    print("Test 7: HTML Features")
    print("=" * 60)
    
    html = DASHBOARD_HTML
    
    # Check CSS features
    assert 'gradient' in html
    assert 'chart-container' in html
    assert 'tab-btn' in html
    assert 'card' in html
    assert 'alert' in html
    
    # Check JavaScript features
    assert 'fetchData' in html
    assert 'updateDashboard' in html
    assert 'updateCharts' in html
    assert 'exportData' in html
    assert 'showTab' in html
    
    # Check Chart.js integration
    assert 'new Chart' in html
    assert 'getContext' in html
    
    print("CSS Features: Gradient, Cards, Tabs, Alerts ✅")
    print("JavaScript Features: Fetch, Update, Charts, Export ✅")
    print("Chart.js Integration ✅")
    
    print("✅ PASS\n")


def test_data_consistency():
    """Test data consistency"""
    print("Test 8: Data Consistency")
    print("=" * 60)
    
    # Generate multiple times
    data1 = generate_mock_data()
    data2 = generate_mock_data()
    
    # Structure should be same
    assert set(data1.keys()) == set(data2.keys())
    assert set(data1['health'].keys()) == set(data2['health'].keys())
    assert set(data1['phases'].keys()) == set(data2['phases'].keys())
    
    # Values can differ (real-time data)
    print("Structure consistent across multiple generations ✅")
    
    print("✅ PASS\n")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Memory Dashboard v2 (P4-2) - Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_mock_data,
        test_html_structure,
        test_all_phases_represented,
        test_trends_data,
        test_alerts,
        test_tool_status,
        test_html_features,
        test_data_consistency,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAIL: {e}\n")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"Tests: {passed + failed} total, {passed} passed, {failed} failed")
    print(f"Success Rate: {passed/(passed+failed)*100:.1f}%")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
