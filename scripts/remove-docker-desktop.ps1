# Remove Docker Desktop Development Dependencies
# This script cleans up Docker Desktop specific configurations

Write-Host "🧹 Removing Docker Desktop Development Dependencies" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Stop any running Docker Desktop containers
Write-Host "🛑 Stopping Docker Desktop containers..." -ForegroundColor Yellow
try {
    docker-compose -f docker-compose.dev.yml down --remove-orphans
    Write-Host "✅ Docker Desktop containers stopped" -ForegroundColor Green
} catch {
    Write-Host "⚠️ No running containers or Docker Desktop not available" -ForegroundColor Yellow
}

# Remove Docker Desktop specific files
Write-Host "🗑️ Removing Docker Desktop specific files..." -ForegroundColor Yellow

$filesToRemove = @(
    "docker-compose.dev.yml",
    ".env.local",
    "scripts\dev-start.ps1",
    "scripts\dev-stop.ps1",
    "scripts\dev-reset.ps1",
    "scripts\dev-health.ps1"
)

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Write-Host "  Removing: $file" -ForegroundColor Red
        # Move to backup instead of delete
        $backupName = "$file.docker-desktop-backup"
        Move-Item $file $backupName -Force
        Write-Host "  Backed up to: $backupName" -ForegroundColor Gray
    }
}

# Update .gitignore to exclude Docker Desktop files
Write-Host "Updating .gitignore..." -ForegroundColor Yellow
$gitignoreContent = @"
# Docker Desktop Development (deprecated)
docker-compose.dev.yml
.env.local
scripts/dev-*.ps1
*.docker-desktop-backup

# Unraid Development
.env.unraid.dev
unraid/secrets/

# Development artifacts
logs/
thumbnails/
uploads/
*.log
"@

$gitignoreContent | Out-File -FilePath ".gitignore" -Append -Encoding UTF8
Write-Host ".gitignore updated" -ForegroundColor Green

# Create migration notice
Write-Host "Creating migration notice..." -ForegroundColor Yellow
$migrationNotice = @"
# Docker Desktop to Unraid Migration Complete

## What was removed:
- docker-compose.dev.yml (backed up)
- .env.local (backed up)
- Docker Desktop specific scripts (backed up)

## New Unraid Development:
- Use: docker-compose.unraid.yml
- Environment: .env.unraid.dev
- SSH Development: unraid/setup-ssh-dev.sh

## Next Steps:
1. Run setup-ssh-dev.sh on your Unraid server
2. Configure VS Code Remote-SSH
3. Start development with direct media access

## Benefits:
✅ Direct access to 18,509+ media files
✅ Native Docker performance
✅ Production-like environment
✅ No Windows virtualization overhead
"@

$migrationNotice | Out-File -FilePath "DOCKER_DESKTOP_MIGRATION.md" -Encoding UTF8
Write-Host "Migration notice created: DOCKER_DESKTOP_MIGRATION.md" -ForegroundColor Green

Write-Host ""
Write-Host "Docker Desktop cleanup complete!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Copy unraid/setup-ssh-dev.sh to your Unraid server" -ForegroundColor White
Write-Host "  2. Run the setup script on Unraid" -ForegroundColor White
Write-Host "  3. Configure VS Code Remote-SSH" -ForegroundColor White
Write-Host "  4. Start developing with native Unraid performance!" -ForegroundColor White
