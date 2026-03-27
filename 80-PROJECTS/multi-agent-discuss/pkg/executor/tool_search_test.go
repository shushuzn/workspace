package executor

import (
	"testing"
)

func TestSearchTool_Execute(t *testing.T) {
	tool := &SearchTool{}
	result, err := tool.Execute(map[string]interface{}{
		"query": "test query",
		"limit": float64(5),
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	m := result.(map[string]interface{})
	if m["query"] != "test query" {
		t.Errorf("expected query 'test query', got '%v'", m["query"])
	}
}