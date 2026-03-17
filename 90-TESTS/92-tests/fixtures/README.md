# Test Fixtures
# 测试数据

## Sample Papers
### papers.json
```json
[
  {
    "arxiv_id": "2603.00267",
    "title": "Test Paper Title",
    "abstract": "This is a test abstract with sufficient length for validation purposes",
    "categories": ["cs.AI"]
  },
  {
    "arxiv_id": "2603.00268",
    "title": "Another Test Paper",
    "abstract": "Another test abstract",
    "categories": ["cs.LG"]
  }
]
```

### Expected Results
### expected_quality.json
```json
{
  "valid_count": 2,
  "invalid_count": 0,
  "quality_score": {
    "score": 1.0,
    "level": "A"
  }
}
```
