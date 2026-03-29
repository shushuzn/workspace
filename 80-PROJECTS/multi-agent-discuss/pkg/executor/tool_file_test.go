package executor

import (
	"os"
	"testing"
)

func TestFileReadTool_Execute(t *testing.T) {
	tmp, _ := os.CreateTemp("", "test")
	tmp.WriteString("hello world")
	tmp.Close()
	defer os.Remove(tmp.Name())

	tool := &FileReadTool{}
	result, err := tool.Execute(map[string]interface{}{
		"path": tmp.Name(),
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	m := result.(map[string]interface{})
	if m["content"] != "hello world" {
		t.Errorf("expected 'hello world', got '%v'", m["content"])
	}
}