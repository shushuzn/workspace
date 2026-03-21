# OpenClaw Workflow Completion for PowerShell
$commands = @("dev", "full", "plan", "security", "quick", "research", "arxiv", "classify", "trends", "optimize", "backup", "deploy", "test")

Register-ArgumentCompleter -CommandName workflow.bat -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $commands | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}
