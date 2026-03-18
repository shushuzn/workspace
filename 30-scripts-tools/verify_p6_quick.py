"""
P6 System Quick Verification
Fast status check without running full test suite
"""
import sys
import json
from pathlib import Path

# Fix Windows UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def verify_p6_system():
    """Quick verification of P6 systems"""
    
    print("=" * 60)
    print("🔍 P6 AUTONOMY - QUICK VERIFICATION")
    print("=" * 60)
    
    results = []
    
    # 1. Check files exist
    print("\n📁 Checking files...")
    required_files = [
        'memory_engine_autonomous.py',
        'memory_persona.py',
        'test_p6_autonomy.py',
        'P6-AUTONOMY-REPORT.md',
        'P6-MERGED-COMPLETE.md'
    ]
    
    for f in required_files:
        if Path(f).exists():
            size = Path(f).stat().st_size / 1024
            print(f"  ✅ {f} ({size:.1f} KB)")
            results.append(True)
        else:
            print(f"  ❌ {f} - MISSING")
            results.append(False)
    
    # 2. Import test
    print("\n📦 Testing imports...")
    try:
        from memory_engine_autonomous import AutonomousDecisionEngine
        print("  ✅ AutonomousDecisionEngine imported")
        results.append(True)
    except Exception as e:
        print(f"  ❌ AutonomousDecisionEngine import failed: {e}")
        results.append(False)
    
    try:
        from memory_persona import PersonaAgentSystem
        print("  ✅ PersonaAgentSystem imported")
        results.append(True)
    except Exception as e:
        print(f"  ❌ PersonaAgentSystem import failed: {e}")
        results.append(False)
    
    # 3. Initialize and check status
    print("\n🔧 Testing initialization...")
    try:
        engine = AutonomousDecisionEngine('.')
        status = engine.get_status()
        print(f"  ✅ Engine: mode={status['mode']}, health={status['health']}, score={status['autonomy_score']}")
        results.append(status['health'] == 'healthy')
    except Exception as e:
        print(f"  ❌ Engine status check failed: {e}")
        results.append(False)
    
    try:
        agents = PersonaAgentSystem('.')
        status = agents.get_system_status()
        print(f"  ✅ Agents: {status['total_agents']} total, {status['active_agents']} active, health={status['average_health']}")
        results.append(status['active_agents'] == 7)
    except Exception as e:
        print(f"  ❌ Agent status check failed: {e}")
        results.append(False)
    
    # 4. Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    if percentage >= 90:
        print(f"✅ VERIFICATION PASSED: {passed}/{total} checks ({percentage:.0f}%)")
        print("🎉 P6 SYSTEM OPERATIONAL!")
    else:
        print(f"⚠️ VERIFICATION: {passed}/{total} checks ({percentage:.0f}%)")
        print("Some checks failed - review needed")
    
    print("=" * 60)
    
    return percentage >= 90

if __name__ == '__main__':
    success = verify_p6_system()
    sys.exit(0 if success else 1)
