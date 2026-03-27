package executor

import (
	"fmt"
	"os"
	"time"
)

type FileReadTool struct{}

func (f *FileReadTool) Name() string        { return "file_read" }
func (f *FileReadTool) Description() string { return "Read file contents" }
func (f *FileReadTool) Timeout() time.Duration { return 10 * time.Second }

func (f *FileReadTool) Execute(args map[string]interface{}) (interface{}, error) {
	// Note: paths are treated as absolute; WorkingDir from context is NOT applied.
	// Callers must resolve relative paths before invoking this tool.
	path, ok := args["path"].(string)
	if !ok || path == "" {
		return nil, fmt.Errorf("missing required arg: path (must be a string)")
	}

	content, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read file: %w", err)
	}

	return map[string]interface{}{
		"path":    path,
		"content": string(content),
		"size":    len(content),
	}, nil
}

type FileWriteTool struct{}

func (f *FileWriteTool) Name() string        { return "file_write" }
func (f *FileWriteTool) Description() string { return "Write content to file" }
func (f *FileWriteTool) Timeout() time.Duration { return 10 * time.Second }

func (f *FileWriteTool) Execute(args map[string]interface{}) (interface{}, error) {
	// Note: paths are treated as absolute; WorkingDir from context is NOT applied.
	// Callers must resolve relative paths before invoking this tool.
	path, ok := args["path"].(string)
	if !ok || path == "" {
		return nil, fmt.Errorf("missing required arg: path (must be a string)")
	}

	content, ok := args["content"].(string)
	if !ok {
		return nil, fmt.Errorf("missing required arg: content (must be a string)")
	}

	if err := os.WriteFile(path, []byte(content), 0600); err != nil {
		return nil, fmt.Errorf("failed to write file: %w", err)
	}

	return map[string]interface{}{
		"path":  path,
		"bytes": len(content),
	}, nil
}

func ToolFileReadTool() *Tool {
	return &Tool{
		Name:        "file_read",
		Description: "Read file contents",
		Params:      []string{"path"},
		Execute: func(args map[string]interface{}) (interface{}, error) {
			return (&FileReadTool{}).Execute(args)
		},
		Timeout: 10 * time.Second,
	}
}

func ToolFileWriteTool() *Tool {
	return &Tool{
		Name:        "file_write",
		Description: "Write content to file",
		Params:      []string{"path", "content"},
		Execute: func(args map[string]interface{}) (interface{}, error) {
			return (&FileWriteTool{}).Execute(args)
		},
		Timeout: 10 * time.Second,
	}
}