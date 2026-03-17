# Integration Test Report

**Date:** 2026-03-07  
**Test Environment:** Python 3.13, Windows  
**Test Result:** ✅ PASSED

---

## Test Overview

| Test Item | Status | Description |
|-----------|--------|-------------|
| Intent Schema | ✅ | Creation and configuration |
| Alignment Calculator | ✅ | Single and batch calculation |
| Mock Execution | ⏸️ | Requires probe files (optional) |

---

## Test Details

### 1. Intent Schema Test

**Test Content:**
- Create search intent
- Create math intent
- Create creative intent
- Verify belief config defaults

**Test Result:**
```
[OK] Intent Schema test passed
```

**Verified:**
- ✅ `search` intent threshold = 0.8
- ✅ `math` intent threshold = 0.9
- ✅ `creative` intent threshold = 0.7

### 2. Alignment Calculator Test

**Test Content:**
- Single alignment calculation
- Batch calculation statistics
- Weight verification

**Test Result:**
```
[OK] Alignment Calculator test passed
```

**Verified:**
- ✅ Single calculation alignment in valid range
- ✅ Efficiency calculation correct (12/24 = 0.5)
- ✅ Batch statistics count = 3

### 3. Mock Execution Test

**Test Content:**
- Belief-aware executor initialization
- Early exit logic verification

**Test Result:**
```
[SKIP] Probe files not found, skipping executor test
```

**Note:** This test requires 24-layer probe files in `belief-probes-v2/` directory.

---

## Test Environment

- **Python Version:** 3.13
- **Operating System:** Windows
- **Pydantic Version:** V2 (warning but functional)
- **Test Directory:** `30-scripts/intent-belief-integration/`

---

## Warnings

```
UserWarning: Valid config keys have changed in V2:
* 'schema_extra' has been renamed to 'json_schema_extra'
```

**Note:** Pydantic V2 config warning, does not affect functionality. Will be fixed in future version.

---

## Conclusion

✅ **Core integration tests PASSED!**

- Intent Schema extension working correctly
- Alignment Calculator fully functional
- Executor requires probe files for complete testing

---

## Next Steps

1. ✅ Basic integration test - Completed
2. ⏳ Real model integration test - Pending probe files
3. ⏳ Performance benchmark test - Pending
4. ⏳ Submit PR to intentkit upstream - Pending

---

*Generated: 2026-03-07 22:20*
