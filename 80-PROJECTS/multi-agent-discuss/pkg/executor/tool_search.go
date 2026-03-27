package executor

import (
	"fmt"
	"time"
)

type SearchTool struct{}

func (s *SearchTool) Name() string        { return "search" }
func (s *SearchTool) Description() string { return "Search web or knowledge base" }
func (s *SearchTool) Timeout() time.Duration { return 30 * time.Second }

func (s *SearchTool) Execute(args map[string]interface{}) (interface{}, error) {
	query, _ := args["query"].(string)
	limit, _ := args["limit"].(float64)

	if query == "" {
		return nil, fmt.Errorf("missing required arg: query")
	}
	if limit == 0 {
		limit = 5
	}

	results := make([]map[string]string, 0)
	for i := 0; i < int(limit); i++ {
		results = append(results, map[string]string{
			"title":   fmt.Sprintf("Result %d for: %s", i+1, query),
			"url":     fmt.Sprintf("https://example.com/result/%d", i+1),
			"snippet": fmt.Sprintf("This is a simulated search result for '%s' (#%d)", query, i+1),
		})
	}

	return map[string]interface{}{
		"query":   query,
		"results": results,
		"count":   len(results),
	}, nil
}

func ToolSearchTool() *Tool {
	return &Tool{
		Name:        "search",
		Description: "Search web or knowledge base",
		Params:      []string{"query", "limit"},
		Execute: func(args map[string]interface{}) (interface{}, error) {
			return (&SearchTool{}).Execute(args)
		},
		Timeout: 30 * time.Second,
	}
}