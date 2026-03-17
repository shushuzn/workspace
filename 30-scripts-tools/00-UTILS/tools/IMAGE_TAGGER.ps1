#!/usr/bin/env pwsh
# 图片标签管理 v2 - 支持父子标签
# 用法：.\IMAGE_TAGGER.ps1 -Add "文件" -Tags "标签" -Parent "父标签" -Desc "描述"

param(
    [string]$Add,
    [string]$Tags,
    [string]$Parent,
    [string]$Desc,
    [string]$Project,
    [switch]$List,
    [switch]$Tree,
    [string]$Search,
    [string]$Import
)

$TagFile = "D:\OpenClaw\workspace\30-scripts\IMAGE_TAGS.csv"

function Show-TagTree {
    $tags = Import-Csv $TagFile | ForEach-Object { $_.Tags -split ';' } | Flatten | Sort-Object -Unique
    $parents = Import-Csv $TagFile | ForEach-Object { $_.ParentTags -split ';' } | Flatten | Sort-Object -Unique
    
    Write-Host "`n标签层级树:" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    foreach ($parent in $parents) {
        if ($parent) {
            Write-Host "`n📁 $parent" -ForegroundColor Yellow
            $children = Import-Csv $TagFile | Where-Object { $_.ParentTags -like "*$parent*" } | ForEach-Object { $_.Tags -split ';' } | Flatten | Sort-Object -Unique
            foreach ($child in $children) {
                Write-Host "   └── 🏷️  $child" -ForegroundColor Green
            }
        }
    }
}

function Flatten {
    process { $_ }
}

if ($Tree) {
    Show-TagTree
    exit
}

if ($Import) {
    # 批量导入 CSV
    if (Test-Path $Import) {
        Import-Csv $Import | ForEach-Object {
            $_ | Export-Csv -Path $TagFile -Append -NoTypeInformation -Encoding UTF8
        }
        Write-Host "已批量导入：$Import" -ForegroundColor Green
    } else {
        Write-Host "文件不存在：$Import" -ForegroundColor Red
    }
    exit
}

if ($List) {
    # 列出所有标签
    Write-Host "`n所有标签:" -ForegroundColor Cyan
    Import-Csv $TagFile | Format-Table FilePath, Tags, ParentTags, Description -AutoSize
    exit
}

if ($Search) {
    # 搜索标签
    $results = Import-Csv $TagFile | Where-Object { 
        $_.Tags -like "*$Search*" -or 
        $_.ParentTags -like "*$Search*" -or 
        $_.Description -like "*$Search*" 
    }
    if ($results) {
        Write-Host "找到 $($results.Count) 个结果:" -ForegroundColor Green
        $results | Format-Table FilePath, Tags, ParentTags, Description -AutoSize
    } else {
        Write-Host "未找到结果" -ForegroundColor Yellow
    }
    exit
}

if ($Add) {
    # 添加标签
    $FilePath = $Add.Replace("D:\OpenClaw\workspace\", "")
    $Date = Get-Date -Format "yyyy-MM-dd"
    
    if (-not $Project) {
        if ($FilePath -like "*CNT*") { $Project = "CNT" }
        elseif ($FilePath -like "*LIG*") { $Project = "LIG" }
        else { $Project = "Other" }
    }
    
    $newTag = [PSCustomObject]@{
        FilePath = $FilePath
        Tags = $Tags
        ParentTags = $Parent
        Description = $Desc
        Project = $Project
        Date = $Date
    }
    
    $newTag | Export-Csv -Path $TagFile -Append -NoTypeInformation -Encoding UTF8
    Write-Host "已添加标签：$FilePath (父标签：$Parent)" -ForegroundColor Green
    exit
}

Write-Host "用法:" -ForegroundColor Yellow
Write-Host "  添加标签：.\IMAGE_TAGGER.ps1 -Add `"文件`" -Tags `"标签 1;标签 2`" -Parent `"父标签`" -Desc `"描述`""
Write-Host "  列出所有：.\IMAGE_TAGGER.ps1 -List"
Write-Host "  标签树：.\IMAGE_TAGGER.ps1 -Tree"
Write-Host "  搜索标签：.\IMAGE_TAGGER.ps1 -Search `"关键词`""
Write-Host "  批量导入：.\IMAGE_TAGGER.ps1 -Import `"CSV 文件`""
