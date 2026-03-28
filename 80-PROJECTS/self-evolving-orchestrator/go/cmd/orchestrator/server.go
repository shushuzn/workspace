package main

import (
	"encoding/json"
	"net/http"

	"github.com/openclaw/self-evolving-orchestrator/go/orchestrator"
)

// Server wraps the orchestrator with HTTP endpoints
type Server struct {
	orch  *orchestrator.Orchestrator
	mux   *http.ServeMux
}

// NewServer creates a new HTTP server
func NewServer(orch *orchestrator.Orchestrator) *Server {
	s := &Server{
		orch: orch,
		mux:  http.NewServeMux(),
	}

	s.mux.HandleFunc("/api/v1/orchestrate", s.handleOrchestrate)
	s.mux.HandleFunc("/api/v1/orchestrate/evolve", s.handleEvolve)
	s.mux.HandleFunc("/api/v1/peers", s.handlePeers)
	s.mux.HandleFunc("/api/v1/status", s.handleStatus)

	return s
}

func (s *Server) handleOrchestrate(w http.ResponseWriter, r *http.Request) {
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

	result, err := s.orch.Process(r.Context(), req.Task, &orchestrator.EvolutionOptions{
		MaxIterations:    3,
		QualityThreshold: 0.7,
	})

	if err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	json.NewEncoder(w).Encode(result)
}

func (s *Server) handleEvolve(w http.ResponseWriter, r *http.Request) {
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

	opts := &orchestrator.EvolutionOptions{
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

func (s *Server) handlePeers(w http.ResponseWriter, r *http.Request) {
	peers := s.orch.Registry().List()
	json.NewEncoder(w).Encode(map[string]interface{}{
		"peers": peers,
		"total": len(peers),
	})
}

func (s *Server) handleStatus(w http.ResponseWriter, r *http.Request) {
	json.NewEncoder(w).Encode(map[string]interface{}{
		"ready": true,
		"peers": len(s.orch.Registry().List()),
		"version": "0.1.0",
	})
}

func (s *Server) Serve(addr string) error {
	return http.ListenAndServe(addr, s.mux)
}
