package orchestrator

import (
	"context"
	"fmt"
	"testing"
	"time"
)

func TestRaceResults_FirstResultWins(t *testing.T) {
	invokeFn := func(peerID, tool string, args map[string]string) (map[string]interface{}, error) {
		if peerID == "fast" {
			time.Sleep(10 * time.Millisecond)
		} else {
			time.Sleep(100 * time.Millisecond)
		}
		return map[string]interface{}{"result": "response from " + peerID}, nil
	}

	requests := []TaskRequest{
		{PeerID: "slow1", Tool: "code", Args: map[string]string{}},
		{PeerID: "slow2", Tool: "code", Args: map[string]string{}},
		{PeerID: "fast", Tool: "code", Args: map[string]string{}},
	}

	ctx := context.Background()
	result, err := raceResults(ctx, requests, invokeFn, 5*time.Second)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result != "response from fast" {
		t.Errorf("expected 'response from fast', got '%s'", result)
	}
}

func TestRaceResults_AllError(t *testing.T) {
	invokeFn := func(peerID, tool string, args map[string]string) (map[string]interface{}, error) {
		return nil, fmt.Errorf("error from %s", peerID)
	}

	requests := []TaskRequest{
		{PeerID: "peer1", Tool: "code", Args: map[string]string{}},
	}

	ctx := context.Background()
	_, err := raceResults(ctx, requests, invokeFn, 100*time.Millisecond)
	if err == nil {
		t.Error("expected error when all requests fail")
	}
}

func TestRaceResults_EmptyRequests(t *testing.T) {
	invokeFn := func(peerID, tool string, args map[string]string) (map[string]interface{}, error) {
		return nil, nil
	}

	ctx := context.Background()
	_, err := raceResults(ctx, []TaskRequest{}, invokeFn, time.Second)
	if err == nil {
		t.Error("expected error for empty requests")
	}
}
