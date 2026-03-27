package executor

import (
	"testing"
	"time"
)

func TestCodeTool_Execute(t *testing.T) {
	tool := &CodeTool{}
	result, err := tool.Execute(map[string]interface{}{
		"lang":   "python",
		"script": "print(1 + 1)",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result == nil {
		t.Fatal("expected non-nil result")
	}
	m, ok := result.(map[string]interface{})
	if !ok {
		t.Fatal("expected result to be map[string]interface{}")
	}
	if m["output"] == "" {
		t.Error("expected non-empty output")
	}
}

func TestCodeTool_Execute_MissingLang(t *testing.T) {
	tool := &CodeTool{}
	_, err := tool.Execute(map[string]interface{}{
		"script": "print(1 + 1)",
	})
	if err == nil {
		t.Error("expected error when lang is missing")
	}
}

func TestCodeTool_Execute_MissingScript(t *testing.T) {
	tool := &CodeTool{}
	_, err := tool.Execute(map[string]interface{}{
		"lang": "python",
	})
	if err == nil {
		t.Error("expected error when script is missing")
	}
}

func TestCodeTool_Execute_InvalidLangType(t *testing.T) {
	tool := &CodeTool{}
	_, err := tool.Execute(map[string]interface{}{
		"lang":   123,
		"script": "print(1 + 1)",
	})
	if err == nil {
		t.Error("expected error when lang is not a string")
	}
}

func TestCodeTool_Execute_InvalidScriptType(t *testing.T) {
	tool := &CodeTool{}
	_, err := tool.Execute(map[string]interface{}{
		"lang":   "python",
		"script": 456,
	})
	if err == nil {
		t.Error("expected error when script is not a string")
	}
}

func TestCodeTool_Execute_Bash(t *testing.T) {
	tool := &CodeTool{}
	result, err := tool.Execute(map[string]interface{}{
		"lang":   "bash",
		"script": "echo hello",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result == nil {
		t.Fatal("expected non-nil result")
	}
	m, ok := result.(map[string]interface{})
	if !ok {
		t.Fatal("expected result to be map[string]interface{}")
	}
	if m["language"] != "bash" {
		t.Errorf("expected language bash, got %v", m["language"])
	}
}

func TestCodeTool_Execute_JavaScript(t *testing.T) {
	tool := &CodeTool{}
	result, err := tool.Execute(map[string]interface{}{
		"lang":   "javascript",
		"script": "console.log(1)",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result == nil {
		t.Fatal("expected non-nil result")
	}
	m, ok := result.(map[string]interface{})
	if !ok {
		t.Fatal("expected result to be map[string]interface{}")
	}
	if m["language"] != "javascript" {
		t.Errorf("expected language javascript, got %v", m["language"])
	}
}

func TestCodeTool_Execute_UnsupportedLanguage(t *testing.T) {
	tool := &CodeTool{}
	_, err := tool.Execute(map[string]interface{}{
		"lang":   "ruby",
		"script": "puts 1",
	})
	if err == nil {
		t.Error("expected error for unsupported language")
	}
}

func TestCodeTool_Timeout(t *testing.T) {
	tool := &CodeTool{}
	if tool.Timeout() != 30*time.Second {
		t.Errorf("expected 30s timeout, got %v", tool.Timeout())
	}
}