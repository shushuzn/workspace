package orchestrator

import (
	"context"
	"encoding/json"
	"net/http"
	"time"
)

// HTTPServer wraps the orchestrator with standard HTTP endpoints
type HTTPServer struct {
	orch  *Orchestrator
	mux   *http.ServeMux
}

// NewHTTPServer creates a new HTTP server
func NewHTTPServer(orch *Orchestrator) *HTTPServer {
	s := &HTTPServer{
		orch: orch,
		mux:  http.NewServeMux(),
	}

	// Standard endpoints
	s.mux.HandleFunc("/run", s.handleRun)
	s.mux.HandleFunc("/health", s.handleHealth)

	// API v1 endpoints
	s.mux.HandleFunc("/api/v1/orchestrate", s.handleOrchestrate)
	s.mux.HandleFunc("/api/v1/orchestrate/evolve", s.handleEvolve)
	s.mux.HandleFunc("/api/v1/peers", s.handlePeers)
	s.mux.HandleFunc("/api/v1/status", s.handleStatus)

	return s
}

// Serve starts the HTTP server
func (s *HTTPServer) Serve(addr string) error {
	return http.ListenAndServe(addr, s.mux)
}

func (s *HTTPServer) handleRun(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "POST only", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Task          string  `json:"task"`
		MaxIterations int     `json:"maxIterations"`
		Threshold     float64 `json:"threshold"`
		TimeoutSec    int     `json:"timeoutSec"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	opts := &EvolutionOptions{
		MaxIterations:    req.MaxIterations,
		QualityThreshold: req.Threshold,
	}
	if req.TimeoutSec > 0 {
		opts.Timeout = time.Duration(req.TimeoutSec) * time.Second
	}

	result, err := s.orch.Process(context.Background(), req.Task, opts)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	json.NewEncoder(w).Encode(result)
}

func (s *HTTPServer) handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":  "ok",
		"version": "0.1.0",
		"peers":   len(s.orch.Registry().List()),
	})
}

func (s *HTTPServer) handleOrchestrate(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "POST only", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Task string `json:"task"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	result, err := s.orch.Process(r.Context(), req.Task, &EvolutionOptions{
		MaxIterations:    3,
		QualityThreshold: 0.7,
	})
	if err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	json.NewEncoder(w).Encode(result)
}

func (s *HTTPServer) handleEvolve(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "POST only", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Task          string  `json:"task"`
		MaxIterations int     `json:"maxIterations"`
		Threshold     float64 `json:"threshold"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	opts := &EvolutionOptions{
		MaxIterations:    req.MaxIterations,
		QualityThreshold: req.Threshold,
	}

	result, err := s.orch.Process(r.Context(), req.Task, opts)
	if err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	json.NewEncoder(w).Encode(result)
}

func (s *HTTPServer) handlePeers(w http.ResponseWriter, r *http.Request) {
	peers := s.orch.Registry().List()
	json.NewEncoder(w).Encode(map[string]interface{}{
		"peers": peers,
		"total": len(peers),
	})
}

func (s *HTTPServer) handleStatus(w http.ResponseWriter, r *http.Request) {
	json.NewEncoder(w).Encode(map[string]interface{}{
		"ready":   true,
		"peers":   len(s.orch.Registry().List()),
		"version": "0.1.0",
	})
}
