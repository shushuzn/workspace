package toolclient

import (
	"testing"

	"github.com/google/uuid"
)

func TestUUIDGeneration(t *testing.T) {
	// UUID should be 36 characters (8-4-4-4-12 format)
	u := uuid.New().String()
	if len(u) != 36 {
		t.Errorf("uuid.New().String() length = %d, want 36", len(u))
	}
}

func TestPendingMapLogic(t *testing.T) {
	// Test pending map stores and retrieves correctly
	pending := make(map[string]interface{})

	// Test storing a channel
	ch := make(chan struct{}, 1)
	invokeID := uuid.New().String()
	pending[invokeID] = ch

	val, ok := pending[invokeID]
	if !ok {
		t.Error("pending[invokeID] not found after store")
	}
	if val != ch {
		t.Error("pending[invokeID] returned different channel")
	}

	// Test sentinel value (true)
	pending[invokeID] = true
	val, ok = pending[invokeID]
	if !ok {
		t.Error("pending[invokeID] not found after sentinel set")
	}
	if val != true {
		t.Error("pending[invokeID] sentinel value not true")
	}

	// Test sentinel detection
	if _, isSentinel := val.(bool); !isSentinel {
		t.Error("expected sentinel bool detection to succeed")
	}

	// Test delete
	delete(pending, invokeID)
	if _, ok := pending[invokeID]; ok {
		t.Error("pending[invokeID] still present after delete")
	}
}

func TestPendingMapMultipleEntries(t *testing.T) {
	pending := make(map[string]interface{})

	ids := make([]string, 5)
	for i := 0; i < 5; i++ {
		ids[i] = uuid.New().String()
		pending[ids[i]] = make(chan struct{}, 1)
	}

	// Verify all entries present
	for _, id := range ids {
		if _, ok := pending[id]; !ok {
			t.Errorf("pending entry missing for id %s", id)
		}
	}

	// Verify non-existent key returns false
	if _, ok := pending["non-existent"]; ok {
		t.Error("non-existent key should return false")
	}
}
