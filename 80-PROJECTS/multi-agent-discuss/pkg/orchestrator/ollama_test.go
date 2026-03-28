package orchestrator

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestOllamaDecomposer_Decompose(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(`{"response": "[\"subtask 1\", \"subtask 2\", \"subtask 3\"]"}`))
	}))
	defer ts.Close()

	decomposer := NewOllamaDecomposer(ts.URL)
	subtasks, err := decomposer.Decompose(context.Background(), "do something")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(subtasks) != 3 {
		t.Errorf("expected 3 subtasks, got %d", len(subtasks))
	}
}

func TestOllamaDecomposer_ServiceUnavailable(t *testing.T) {
	decomposer := NewOllamaDecomposer("http://localhost:99999")
	_, err := decomposer.Decompose(context.Background(), "test")
	if err == nil {
		t.Error("expected error for unavailable service")
	}
}
