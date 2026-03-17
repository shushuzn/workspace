$data = Get-Content "D:\OpenClaw\workspace\knowledge-graph\enhanced-v3\graph" | ConvertFrom-Json
$orgs = $data.entities | Where-Object { $_.type -eq "Organization" }
Write-Host "Organizations ($($orgs.Count)):"
$orgs | ForEach-Object { Write-Host "  - $($_.properties.name)" }

$rels = $data.relations | Where-Object { $_.type -eq "affiliated_with" }
Write-Host "`naffiliated_with relations ($($rels.Count)):"
$rels | ForEach-Object { Write-Host "  $($_.source) -> $($_.target)" }
