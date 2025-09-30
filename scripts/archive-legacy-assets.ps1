param(
    [switch]$Execute
)

$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRootInfo = Resolve-Path (Join-Path $here '..')
$repoRoot = $repoRootInfo.ProviderPath
$archiveRoot = Join-Path $repoRoot 'archive'

if (-not (Test-Path $archiveRoot)) {
    Write-Verbose "Creating archive root at $archiveRoot"
    New-Item -ItemType Directory -Path $archiveRoot | Out-Null
}

$groups = @(
    @{ 
        Name = 'scripts'
        Items = @(
            'clean-and-update-v303.ps1',
            'clean-and-update-v303.sh',
            'final-fixes-v303.sh',
            'fix-docker-git-sync.ps1',
            'fix-docker-git-issues-v303.sh',
            'fix-build-issues-v303.sh',
            'quick-build-fix-v303.sh',
            'fix-all-errors-final.ps1',
            'fix-all-errors-final-v302.sh',
            'fix-all-issues-v302.sh',
            'fix-api-auth.ps1',
            'fix-api-auth-v302.sh',
            'fix-login-token.ps1',
            'fix-login-token-v302.sh',
            'fix-tabs-media.ps1',
            'fix-permissions-policy.sh',
            'production-postgresql-only.ps1',
            'production-postgresql-only-v302.sh',
            'permanent-fix.ps1',
            'permanent-fix-v302.sh',
            'permanent-frontend-auth-fix.ps1',
            'permanent-frontend-auth-fix-v302.sh',
            'sync-databases.ps1',
            'sync-databases-v302.sh',
            'deploy-to-unraid.ps1',
            'deploy-to-unraid.sh',
            'deploy-to-unraid-final.ps1',
            'deploy-to-unraid-simple.ps1',
            'deploy-unraid-clean.ps1',
            'deploy-unraid-fixed.ps1',
            'deploy-v3.0.2-unraid.ps1',
            'deploy-v302-clean.ps1',
            'dev-deploy.sh',
            'fix-unraid-deployment.sh',
            'fix-unraid-login.sh',
            'fix-unraid-simple.ps1',
            'fix-cors-unraid.sh',
            'fix-postgres-auth.ps1',
            'fix-postgres-auth-v302.sh',
            'fix-postgres-schema.ps1',
            'fix-postgres-schema-v302.sh',
            'fix-build-add-db-info.ps1',
            'fix-build-add-db-info-v302.sh',
            'fix-frontend-errors.ps1',
            'fix-frontend-errors-v302.sh',
            'fix-missing-tabs-login.sh',
            'fix-navigation-media-v302.sh',
            'fix-404-login.sh',
            'debug-404-login.sh',
            'fix-all-unraid-issues.ps1',
            'permanent-frontend-auth-fix-v302.sh'
        )
        Patterns = @(
            '*-v302.*',
            '*-v303.*'
        )
    },
    @{ 
        Name = 'docs'
        Items = @(
            'CHANGELOG_v3.0.1.md',
            'CHANGELOG_v3.0.2.md',
            'CURRENT_STATUS_REPORT.md',
            'FINAL_STATUS_REPORT.md',
            'SYSTEM_STATUS.md',
            'SYSTEM_READY.md',
            'NEXT_PHASE_PLAN.md',
            'PRODUCTION_COMPATIBILITY_REPORT.md',
            'PRODUCTION_UPDATE_CHECKLIST.md',
            'RESTRUCTURE_COMPLETE.md',
            'SERVER_STARTUP_README.md',
            'NAVIGATION_TABS_STATUS.md',
            'UNRAID-DEPLOYMENT.md',
            'UNRAID_DEPLOYMENT_GUIDE.md',
            'UNRAID-CONFIG.md',
            'MANUAL_UNRAID_DEPLOYMENT.md',
            'MANUAL_UNRAID_FIX.md',
            'QUICK-SETUP-UNRAID.md',
            'README-PRODUCTION.md',
            'SYSTEM_READY.md',
            'SYSTEM_STATUS.md',
            'FINAL_STATUS_REPORT.md'
        )
        Patterns = @(
            'SYSTEM_*.md',
            'UNRAID-*.md'
        )
    },
    @{ 
        Name = 'tests'
        Items = @(
            'browser_console_debug.js',
            'frontend_debug.html',
            'test_frontend_api_calls.html',
            'test_frontend_interface.html',
            'test_library_posters.html'
        )
        Patterns = @(
            'debug_*.*',
            'diagnose_*.py',
            'test_*.*',
            'check_*.*',
            'simple_*test*.py'
        )
    },
    @{ 
        Name = 'misc'
        Items = @(
            'python-installer.exe',
            'mobile-app',
            'unraid-docker-compose.yml',
            'unraid-deploy-commands.txt',
            'unraid-setup.sh',
            'deployment'
        )
        Patterns = @()
    }
)

$pending = [System.Collections.Generic.List[object]]::new()
$archiveRootPath = $archiveRoot

function Get-RelativePath([string]$basePath, [string]$targetPath) {
    try {
        $baseResolved = (Resolve-Path -LiteralPath $basePath).ProviderPath
        $targetResolved = (Resolve-Path -LiteralPath $targetPath).ProviderPath

        $method = [System.IO.Path].GetMethod('GetRelativePath', [Type[]]@([string], [string]))
        if ($method) {
            return [System.IO.Path]::GetRelativePath($baseResolved, $targetResolved)
        }

        $baseUri = [System.Uri]::new($baseResolved + [IO.Path]::DirectorySeparatorChar)
        $targetUri = [System.Uri]::new($targetResolved)
        return $baseUri.MakeRelativeUri($targetUri).ToString().Replace('/', [IO.Path]::DirectorySeparatorChar)
    } catch {
        return $targetPath
    }
}

foreach ($group in $groups) {
    $targetDir = Join-Path $archiveRoot $group.Name
    if (-not (Test-Path $targetDir)) {
        Write-Verbose "Creating archive subdirectory $targetDir"
        New-Item -ItemType Directory -Path $targetDir | Out-Null
    }

    $seen = @{}

    Write-Verbose "Scanning explicit items for group '$($group.Name)'"

    foreach ($relative in $group.Items) {
        $source = Join-Path $repoRoot $relative
        if (Test-Path $source -PathType Any) {
            $full = (Resolve-Path $source -ErrorAction Stop).ProviderPath
            if (-not $full.StartsWith($archiveRootPath, [System.StringComparison]::OrdinalIgnoreCase)) {
                if (-not $seen.ContainsKey($full)) {
                    $pending.Add([PSCustomObject]@{
                        Group = $group.Name
                        Source = $full
                        Destination = $targetDir
                    })
                    $seen[$full] = $true
                }
            }
        }
    }

    Write-Verbose "Scanning patterns for group '$($group.Name)'"
    foreach ($pattern in $group.Patterns) {
        $matches = Get-ChildItem -Path $repoRoot -Recurse -Force -Include $pattern -ErrorAction SilentlyContinue |
            Where-Object { $_.PSIsContainer -eq $false } |
            Where-Object { $_.FullName -notlike "*$([IO.Path]::DirectorySeparatorChar)archive$([IO.Path]::DirectorySeparatorChar)*" }

        foreach ($match in $matches) {
            $full = $match.FullName
            if (-not $seen.ContainsKey($full)) {
                $pending.Add([PSCustomObject]@{
                    Group = $group.Name
                    Source = $full
                    Destination = $targetDir
                })
                $seen[$full] = $true
            }
        }
    }
}

if (-not $pending) {
    Write-Host 'No matching legacy files were found.' -ForegroundColor Yellow
    return
}

if (-not $Execute) {
    Write-Host 'Preview (use -Execute to move items):' -ForegroundColor Cyan
    $pending | ForEach-Object {
        $relative = Get-RelativePath $repoRoot $_.Source
        Write-Host ("[" + $_.Group + "] " + $relative)
    }
    return
}

$movedCount = 0
foreach ($item in $pending) {
    $destination = Join-Path $item.Destination (Split-Path $item.Source -Leaf)
    try {
        Move-Item -Force -LiteralPath $item.Source -Destination $destination
        $relative = Get-RelativePath $repoRoot $destination
        Write-Host ("Moved " + $relative) -ForegroundColor Green
        $movedCount++
    } catch {
        Write-Error "Failed to move '$($item.Source)' -> '$destination': $_"
    }
}

Write-Host ("Archival complete. Moved $movedCount item(s).") -ForegroundColor Green
