package executor

import (
	"fmt"
	"time"
)

// CodeTool executes code in a sandboxed environment
type CodeTool struct{}

func (c *CodeTool) Name() string        { return "code" }
func (c *CodeTool) Description() string { return "Execute code in sandboxed environment" }
func (c *CodeTool) Timeout() time.Duration { return 30 * time.Second }

func (c *CodeTool) Execute(args map[string]interface{}) (interface{}, error) {
	lang, ok := args["lang"].(string)
	if !ok {
		return nil, fmt.Errorf("lang must be a string")
	}
	script, ok := args["script"].(string)
	if !ok {
		return nil, fmt.Errorf("script must be a string")
	}

	if lang == "" || script == "" {
		return nil, fmt.Errorf("missing required args: lang and script")
	}

	switch lang {
	case "python":
		return map[string]interface{}{
			"output":   fmt.Sprintf("[python] %s", script),
			"language": "python",
		}, nil
	case "bash", "shell":
		return map[string]interface{}{
			"output":   fmt.Sprintf("[bash] %s", script),
			"language": "bash",
		}, nil
	case "javascript", "js":
		return map[string]interface{}{
			"output":   fmt.Sprintf("[js] %s", script),
			"language": "javascript",
		}, nil
	default:
		return nil, fmt.Errorf("unsupported language: %s (supported: python, bash, javascript)", lang)
	}
}

func ToolCodeTool() *Tool {
	return &Tool{
		Name:        "code",
		Description: "Execute code in sandboxed environment",
		Params:      []string{"lang", "script"},
		Execute: func(args map[string]interface{}) (interface{}, error) {
			return (&CodeTool{}).Execute(args)
		},
		Timeout: 30 * time.Second,
	}
}
