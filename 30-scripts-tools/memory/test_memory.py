# -*- coding: utf-8 -*-
"""Test script for dual-layer memory"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory import (
    DualLayerMemory,
    WorkingMemory,
    ArchiveMemory,
    ImportanceScorer,
    ForgettingMechanism,
    SessionBridge
)
import traceback

def test_import():
    print("[TEST] Import modules...")
    assert DualLayerMemory is not None
    assert WorkingMemory is not None
    assert ArchiveMemory is not None
    assert ImportanceScorer is not None
    assert ForgettingMechanism is not None
    assert SessionBridge is not None
    print("  PASS - All imports OK")

def test_importance_scorer():
    print("[TEST] ImportanceScorer...")
    scorer = ImportanceScorer()

    # Test basic scoring
    score1 = scorer.calculate("我更喜欢简洁的代码风格", "preference", {})
    assert 0 <= score1 <= 1, f"Score out of range: {score1}"
    print(f"  Preference score: {score1:.2f}")

    score2 = scorer.calculate("hello world", "conversation", {})
    assert 0 <= score2 <= 1
    print(f"  Conversation score: {score2:.2f}")

    # Test ranking
    items = [
        {"content": "我想要蓝色", "type": "preference", "metadata": {}},
        {"content": "今天天气好", "type": "conversation", "metadata": {}},
        {"content": "决定使用方案A", "type": "decision", "metadata": {}},
    ]
    ranked = scorer.rank_items(items, top_k=3)
    assert len(ranked) == 3
    ranking_scores = [r['importance_score'] for r in ranked]
    print(f"  Ranking: {ranking_scores}")
    print("  PASS")

def test_working_memory():
    print("[TEST] WorkingMemory...")
    wm = WorkingMemory(token_budget=1000, max_items=10)

    from memory.dual_layer_memory import MemoryItem

    item1 = MemoryItem(
        id="test1",
        content="这是一条测试记忆",
        type="conversation",
        importance=0.5,
        created_at="2026-03-20T10:00:00"
    )

    wm.add(item1)
    assert wm.count() == 1
    print(f"  Count after add: {wm.count()}")

    items = wm.get_all()
    assert len(items) == 1

    # Test compression
    compressed = wm.compress()
    print(f"  Compressed: {compressed} items")
    print("  PASS")

def test_archive_memory():
    print("[TEST] ArchiveMemory...")
    import tempfile
    import os

    # Use temp file
    temp_db = tempfile.mktemp(suffix=".db")

    try:
        archive = ArchiveMemory(temp_db)

        from memory.dual_layer_memory import MemoryItem

        item = MemoryItem(
            id="archive_test1",
            content="这是一条归档记忆",
            type="preference",
            importance=0.8,
            created_at="2026-03-20T10:00:00"
        )

        archive.store(item)
        print(f"  Stored item, count: {archive.count()}")

        # Retrieve
        retrieved = archive.retrieve("archive_test1")
        assert retrieved is not None
        assert retrieved.content == "这是一条归档记忆"
        print("  Retrieve OK")

        # Search
        results = archive.search("归档", top_k=5)
        print(f"  Search results: {len(results)}")

        print("  PASS")
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)

def test_forgetting_mechanism():
    print("[TEST] ForgettingMechanism...")
    fm = ForgettingMechanism()

    # Test decay calculation
    decay = fm.calculate_decay(0.7, 7)  # 7 days old, importance 0.7
    print(f"  Decay after 7 days: {decay:.3f}")
    assert decay < 0.7, "Should decay"

    # Test should_forget
    should_forget = fm.should_forget(0.2, "conversation", 30)
    print(f"  Should forget (low importance, old): {should_forget}")

    should_not_forget = fm.should_forget(0.8, "preference", 30)
    print(f"  Should forget (high importance, preference): {should_not_forget}")
    assert not should_not_forget, "Protected types should not forget"

    # Test retention suggestion
    retention = fm.suggest_retention(0.7, "preference")
    print(f"  Retention suggestion: {retention['recommended_retention_days']} days")

    print("  PASS")

def test_dual_layer():
    print("[TEST] DualLayerMemory...")
    import tempfile
    import os

    temp_db = tempfile.mktemp(suffix=".db")

    try:
        dlm = DualLayerMemory(token_budget=2000, db_path=temp_db)

        # Add some memories
        item1 = dlm.add("我更喜欢简洁的代码", "preference")
        print(f"  Added preference, importance: {item1.importance:.2f}")

        item2 = dlm.add("今天天气不错", "conversation")
        print(f"  Added conversation, importance: {item2.importance:.2f}")

        item3 = dlm.add("决定使用方案A", "decision")
        print(f"  Added decision, importance: {item3.importance:.2f}")

        # Get stats
        stats = dlm.get_stats()
        print(f"  Stats: working={stats['working_count']}, archive={stats['archive_count']}")

        # Test compress
        result = dlm.compress()
        print(f"  Compress result: {result}")

        print("  PASS")
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)

def test_session_bridge():
    print("[TEST] SessionBridge...")
    import tempfile
    import os

    temp_db = tempfile.mktemp(suffix=".db")

    try:
        from memory.dual_layer_memory import MemoryItem

        # Create working memory with some items
        wm = WorkingMemory()
        wm.add(MemoryItem(
            id="pref1",
            content="我想要蓝色主题",
            type="preference",
            importance=0.8,
            created_at="2026-03-20T10:00:00"
        ))
        wm.add(MemoryItem(
            id="dec1",
            content="决定用PostgreSQL",
            type="decision",
            importance=0.9,
            created_at="2026-03-20T10:00:00"
        ))

        # Create archive
        archive = ArchiveMemory(temp_db)
        archive.store(MemoryItem(
            id="pref2",
            content="我喜欢夜间模式",
            type="preference",
            importance=0.7,
            created_at="2026-03-20T09:00:00"
        ))

        # Test bridge
        bridge = SessionBridge()
        essential = bridge.export_essential(wm, archive, "new_session_001")

        print(f"  Exported: {essential['stats']['total_exported']} items")
        print(f"  Preferences: {len(essential['preferences'])}")
        print(f"  Decisions: {len(essential['decisions'])}")

        # Test import
        imported = bridge.import_essential(essential)
        print(f"  Imported: {len(imported)} items")

        print("  PASS")
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)

def main():
    print("=" * 50)
    print("Running Dual-Layer Memory Tests")
    print("=" * 50)

    tests = [
        test_import,
        test_importance_scorer,
        test_working_memory,
        test_archive_memory,
        test_forgetting_mechanism,
        test_dual_layer,
        test_session_bridge,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            traceback.print_exc()
            failed += 1

    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)

    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)