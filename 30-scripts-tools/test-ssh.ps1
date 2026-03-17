$password = "20051104sS" | ConvertTo-SecureString -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential("root", $password)

# Test connection
Write-Host "Testing SSH connection to 8.208.30.28..."
try {
    $session = New-PSSession -HostName "8.208.30.28" -Credential $credential -ErrorAction Stop
    Write-Host "Connected successfully!"
    Invoke-Command -Session $session -ScriptBlock { whoami; hostname; pwd }
    Remove-PSSession $session
} catch {
    Write-Host "Connection failed: $_"
}
