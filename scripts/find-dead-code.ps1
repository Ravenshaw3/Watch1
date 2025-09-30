param(
    [switch]$Execute
)

$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $here '..')).ProviderPath
$archiveRoot = Join-Path $repoRoot 'archive'

# Dead code candidates to archive
$deadCodeFiles = @(
    # Root level diagnostic/test scripts
    'database_manager.py',
    'media_fix_summary.py', 
    'preload_posters_and_titles.py',
    'setup_media_directories.py',
    'trigger_scan.py',
    'media_scanner.py',
    'start_production_servers.py',
    
    # Legacy deployment scripts
    'build-and-deploy.sh',
    'deploy-cors-fix.ps1',
    'deploy-images.sh', 
    'deploy.sh',
    'fix-sqlite-login.sh',
    'install-docker-compose.sh',
    'manage.sh',
    'quick-deploy.ps1',
    'quick-unraid-debug.ps1',
    'scan_trigger.sh',
    'start-clean.ps1',
    'start-simple.ps1',
    'start_servers.bat',
    'start_servers.ps1',
    'troubleshoot-watch1.sh',
    'update-docker-hub.ps1',
    'update.sh',
    'watch1-unraid-template.xml',
    
    # Legacy docs
    'DEBUGGING_CHECKLIST.md',
    'DEPLOYMENT-UNRAID.md', 
    'DEV_ENVIRONMENT_RESTRUCTURE.md',
    'ENVIRONMENT_SETUP.md',
    'FUTURE_ENHANCEMENTS.md',
    'PROJECT_RULES.md'
)

# Backend dead code (unused API endpoints/models)
$backendDeadCode = @(
    'backend\app\api\api_v1\endpoints\version.py',  # Duplicate version endpoint
    'backend\routes\*'  # Old routing system replaced by app/api/v1
)

Write-Host "Dead Code Analysis for Watch1" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$pending = @()

# Check root level files
foreach ($file in $deadCodeFiles) {
    $fullPath = Join-Path $repoRoot $file
    if (Test-Path $fullPath) {
        $pending += [PSCustomObject]@{
            Type = 'RootFile'
            Source = $fullPath
            RelativePath = $file
        }
    }
}

# Check backend dead code
foreach ($pattern in $backendDeadCode) {
    $fullPattern = Join-Path $repoRoot $pattern
    $matches = Get-ChildItem -Path $fullPattern -ErrorAction SilentlyContinue
    foreach ($match in $matches) {
        if ($match.PSIsContainer -eq $false) {
            $relative = $match.FullName.Substring($repoRoot.Length + 1)
            $pending += [PSCustomObject]@{
                Type = 'BackendFile'
                Source = $match.FullName
                RelativePath = $relative
            }
        }
    }
}

if (-not $pending) {
    Write-Host 'No dead code files found.' -ForegroundColor Yellow
    return
}

if (-not $Execute) {
    Write-Host "Found $($pending.Count) dead code files:" -ForegroundColor Yellow
    $pending | Group-Object Type | ForEach-Object {
        Write-Host "`n$($_.Name) ($($_.Count) files):" -ForegroundColor Magenta
        $_.Group | ForEach-Object {
            Write-Host "  $($_.RelativePath)" -ForegroundColor Gray
        }
    }
    Write-Host "`nUse -Execute to move these files to archive/deadcode/" -ForegroundColor Cyan
    return
}

# Create archive structure
$deadCodeArchive = Join-Path $archiveRoot 'deadcode'
if (-not (Test-Path $deadCodeArchive)) {
    New-Item -ItemType Directory -Path $deadCodeArchive -Force | Out-Null
}

$movedCount = 0
foreach ($item in $pending) {
    $destination = Join-Path $deadCodeArchive (Split-Path $item.Source -Leaf)
    
    # Handle duplicates by adding suffix
    $counter = 1
    $originalDest = $destination
    while (Test-Path $destination) {
        $ext = [System.IO.Path]::GetExtension($originalDest)
        $name = [System.IO.Path]::GetFileNameWithoutExtension($originalDest)
        $destination = Join-Path $deadCodeArchive "$name-$counter$ext"
        $counter++
    }
    
    try {
        Move-Item -LiteralPath $item.Source -Destination $destination -Force
        Write-Host "Moved $($item.RelativePath) -> archive/deadcode/" -ForegroundColor Green
        $movedCount++
    } catch {
        Write-Error "Failed to move '$($item.RelativePath)': $_"
    }
}

Write-Host "`nDead code cleanup complete. Moved $movedCount files to archive/deadcode/" -ForegroundColor Green
