# Feishu Webhook Event Filter - Integration Guide

**Date:** 2026-03-17  
**Status:** ✅ Complete  
**Tool:** `feishu_webhook_filter.py`

---

## 🎯 Problem Solved

**Error:**
```
[Lark] [ERROR] handle message failed, message_type: event, 
err: processor not found, type: im.message.reaction.created_v1
```

**Cause:** Feishu webhook receives emoji reaction events but has no processor for them.

**Solution:** Filter out unwanted event types before they reach the processor.

---

## 🛠️ Tool Created

### feishu_webhook_filter.py (9.7 KB)

**Features:**
- Event type filtering (4 default filters)
- Configurable filter list (JSON config)
- Logger patching (suppresses errors)
- Test mode
- Easy integration

**Default Filters:**
- `im.message.reaction.created_v1` - Emoji reactions
- `im.message.reaction.deleted_v1` - Reaction removals
- `im.chat.updated_v1` - Chat updates
- `im.chat.member.updated_v1` - Member changes

---

## 📋 Usage

### 1. Test Filter
```bash
python feishu_webhook_filter.py --test
```

**Output:**
```
🧪 Testing Event Filter
============================================================
  🚫 FILTERED: im.message.reaction.created_v1
  🚫 FILTERED: im.message.reaction.deleted_v1
  ✅ PASSED: im.message.receive_v1
  🚫 FILTERED: im.chat.updated_v1
  ✅ PASSED: unknown_event
============================================================
✅ Test complete!
```

### 2. List Active Filters
```bash
python feishu_webhook_filter.py --list-filters
```

**Output:**
```
📋 Active Filters (4):
============================================================
  • im.chat.member.updated_v1
  • im.chat.updated_v1
  • im.message.reaction.created_v1
  • im.message.reaction.deleted_v1
============================================================
```

### 3. Add Custom Filter
```bash
python feishu_webhook_filter.py --add-filter "custom.event.type_v1"
```

### 4. Patch Logger (Suppress Errors)
```bash
python feishu_webhook_filter.py --patch-logger
```

---

## 🔗 Integration Options

### Option 1: Standalone Filter (Recommended)

**In your Feishu webhook handler:**

```python
from feishu_webhook_filter import FeishuEventFilter

# Initialize filter
event_filter = FeishuEventFilter()

@app.route('/feishu/webhook', methods=['POST'])
def webhook():
    event_data = request.json
    event_type = event_data.get('type', '')
    
    # Check if event should be filtered
    if event_filter.should_filter(event_type):
        logger.debug(f"Filtered event: {event_type}")
        return json.dumps({'status': 'filtered'}), 200
    
    # Process event normally
    return handle_event(event_data)
```

### Option 2: Logger Patching

**Suppress 'processor not found' errors:**

```python
from feishu_webhook_filter import patch_lark_oapi_logger

# Patch logger at application startup
patch_lark_oapi_logger()

# Now filtered events won't log errors
```

### Option 3: Event Processor Function

**Use provided processor:**

```python
from feishu_webhook_filter import FeishuEventFilter, create_event_processor

event_filter = FeishuEventFilter()
process_event = create_event_processor(event_filter)

@app.route('/feishu/webhook', methods=['POST'])
def webhook():
    event_data = request.json
    processed = process_event(event_data)
    
    if processed is None:
        return json.dumps({'status': 'filtered'}), 200
    
    return handle_event(processed)
```

---

## 📁 Configuration

**Config File:** `30-scripts-tools/feishu-tools/feishu-event-filters.json`

**Format:**
```json
{
  "filters": [
    "im.message.reaction.created_v1",
    "im.message.reaction.deleted_v1",
    "im.chat.updated_v1",
    "im.chat.member.updated_v1"
  ],
  "description": "Feishu webhook event filters - events to ignore"
}
```

**Auto-created:** First time you run the tool

---

## 🎯 Integration with Existing Feishu Tools

### feishu_api.py Integration

**Add to `feishu_api.py`:**

```python
# At the top of the file
from feishu_webhook_filter import FeishuEventFilter

# In the FeishuClient class
class FeishuClient:
    def __init__(self, app_id=None, app_secret=None):
        # ... existing code ...
        
        # Initialize event filter
        self.event_filter = FeishuEventFilter()
    
    def handle_webhook(self, event_data):
        # Check filter first
        if self.event_filter.should_filter(event_data.get('type', '')):
            logger.debug(f"Filtered event: {event_data.get('type')}")
            return {'status': 'filtered'}
        
        # Process normally
        return self._process_event(event_data)
```

### Enhanced Version (feishu_api_enhanced.py)

Already includes filter support - just need to enable it:

```python
# In feishu_api_enhanced.py
ENABLE_EVENT_FILTER = True  # Set to True to enable filtering
```

---

## 🧪 Testing

### Test Script
```bash
python feishu_webhook_filter.py --test
```

### Test Integration
```python
from feishu_webhook_filter import FeishuEventFilter

event_filter = FeishuEventFilter()

# Test reaction event (should be filtered)
result = event_filter.process_event({
    'type': 'im.message.reaction.created_v1',
    'data': {'emoji': '👍'}
})
assert result is None, "Reaction should be filtered"

# Test message event (should pass)
result = event_filter.process_event({
    'type': 'im.message.receive_v1',
    'data': {'text': 'Hello'}
})
assert result is not None, "Message should pass"

print("✅ All tests passed!")
```

---

## 📊 Expected Results

### Before Filter
```
[Lark] [ERROR] handle message failed, message_type: event, 
message_id: 68a6b83a-48ea-4ab9-89f3-fd0737b49e84, 
err: processor not found, type: im.message.reaction.created_v1
```

**Frequency:** Every time someone reacts to a message

### After Filter
```
(No error logs for filtered events)
```

**Result:** Clean logs, no false errors

---

## 🎓 Best Practices

1. **Enable at Startup:** Initialize filter when application starts
2. **Log Filtered Events:** Use DEBUG level to track filtered events
3. **Review Periodically:** Check if new event types need filtering
4. **Test Integration:** Always test after adding new filters
5. **Document Custom Filters:** Keep track of why filters were added

---

## 🚀 Deployment

### Development
```bash
# Enable filter in dev
python feishu_webhook_filter.py --add-filter "dev.event.type_v1"
```

### Production
```bash
# Patch logger to suppress errors
python feishu_webhook_filter.py --patch-logger
```

### Cron/Scheduled Tasks
```bash
# Add to startup script
python 30-scripts-tools/feishu-tools/feishu_webhook_filter.py --patch-logger
```

---

## ✅ Verification Checklist

- [x] Filter tool created ✅
- [x] Default filters configured ✅
- [x] Test mode working ✅
- [x] Config file auto-created ✅
- [x] Integration examples provided ✅
- [x] Logger patching implemented ✅
- [x] Documentation complete ✅

---

## 🎯 Next Steps

1. **Integrate with feishu_api.py** - Add filter to main client
2. **Update feishu_api_enhanced.py** - Enable filter by default
3. **Add to HEARTBEAT** - Run filter check periodically
4. **Monitor Logs** - Verify errors are suppressed

---

## 📝 Quick Start

```bash
# 1. Test filter
python feishu_webhook_filter.py --test

# 2. List filters
python feishu_webhook_filter.py --list-filters

# 3. Patch logger (optional)
python feishu_webhook_filter.py --patch-logger

# 4. Integrate into your webhook handler
# (See integration examples above)
```

---

**Status:** ✅ Ready for Integration  
**Impact:** Eliminates false error logs from Feishu webhook  
**Priority:** High (improves log quality)

---

*Generated by OpenClaw 🐾 | Feishu Webhook Filter Guide*
