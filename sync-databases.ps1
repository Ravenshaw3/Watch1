# Synchronize SQLite and PostgreSQL Databases for Watch1 v3.0.2
param(
    [string]$UnraidIP = "192.168.254.14",
    [string]$Password = "videosmile"
)

Write-Host "Database Synchronization for Watch1 v3.0.2" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host "Target: $UnraidIP" -ForegroundColor Cyan
Write-Host ""

Write-Host "CURRENT DATABASE SITUATION:" -ForegroundColor Yellow
Write-Host "- Docker Compose has PostgreSQL configured" -ForegroundColor Gray
Write-Host "- Backend is likely using SQLite" -ForegroundColor Gray
Write-Host "- Databases are not synchronized" -ForegroundColor Gray
Write-Host "- This causes missing navigation tabs and no media display" -ForegroundColor Red
Write-Host ""

Write-Host "WHAT THIS SCRIPT WILL DO:" -ForegroundColor Cyan
Write-Host "1. Set up PostgreSQL with proper schema" -ForegroundColor White
Write-Host "2. Populate PostgreSQL with sample data" -ForegroundColor White
Write-Host "3. Create/sync SQLite database with same data" -ForegroundColor White
Write-Host "4. Ensure both databases have identical content" -ForegroundColor White
Write-Host "5. Test both database connections" -ForegroundColor White
Write-Host ""

# Copy the synchronization script
Write-Host "Copying database synchronization script..." -ForegroundColor Yellow
scp sync-databases-v302.sh root@${UnraidIP}:/mnt/user/appdata/watch1/

Write-Host "Script copied successfully!" -ForegroundColor Green
Write-Host ""

Write-Host "SSH to Unraid and run the synchronization:" -ForegroundColor Cyan
Write-Host ""
Write-Host "ssh root@$UnraidIP" -ForegroundColor White
Write-Host "cd /mnt/user/appdata/watch1" -ForegroundColor White
Write-Host "chmod +x sync-databases-v302.sh" -ForegroundColor White
Write-Host "./sync-databases-v302.sh" -ForegroundColor White
Write-Host ""
Write-Host "Password: $Password" -ForegroundColor Yellow

Write-Host ""
Write-Host "EXPECTED RESULTS:" -ForegroundColor Green
Write-Host "=================" -ForegroundColor Green
Write-Host "After synchronization:" -ForegroundColor White
Write-Host ""
Write-Host "POSTGRESQL DATABASE:" -ForegroundColor Cyan
Write-Host "- Complete schema with users, media_files, playlists tables" -ForegroundColor Gray
Write-Host "- 1 test user: test@example.com / testpass123" -ForegroundColor Gray
Write-Host "- 7 sample media files (movies, TV, documentaries, music)" -ForegroundColor Gray
Write-Host "- 1 sample playlist with 3 movies" -ForegroundColor Gray
Write-Host ""
Write-Host "SQLITE DATABASE:" -ForegroundColor Cyan
Write-Host "- Identical schema and data as PostgreSQL" -ForegroundColor Gray
Write-Host "- Same test user and media files" -ForegroundColor Gray
Write-Host "- Synchronized for consistent behavior" -ForegroundColor Gray
Write-Host ""

Write-Host "SAMPLE DATA INCLUDED:" -ForegroundColor Yellow
Write-Host "=====================" -ForegroundColor Yellow
Write-Host "Movies:" -ForegroundColor White
Write-Host "- The Matrix (1999)" -ForegroundColor Gray
Write-Host "- Inception (2010)" -ForegroundColor Gray
Write-Host "- Interstellar (2014)" -ForegroundColor Gray
Write-Host ""
Write-Host "TV Shows:" -ForegroundColor White
Write-Host "- Breaking Bad S01E01" -ForegroundColor Gray
Write-Host "- Game of Thrones S01E01" -ForegroundColor Gray
Write-Host ""
Write-Host "Documentaries:" -ForegroundColor White
Write-Host "- Planet Earth Documentary" -ForegroundColor Gray
Write-Host ""
Write-Host "Music Videos:" -ForegroundColor White
Write-Host "- Live Concert Performance" -ForegroundColor Gray

Write-Host ""
Write-Host "AFTER RUNNING THE SCRIPT:" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host "1. Go to http://192.168.254.14:3000" -ForegroundColor Cyan
Write-Host "2. Login with test@example.com / testpass123" -ForegroundColor Cyan
Write-Host "3. Navigation tabs (Settings, Analytics) should appear" -ForegroundColor Green
Write-Host "4. Library should show 7 media files" -ForegroundColor Green
Write-Host "5. Playlists should show 'My Favorite Movies'" -ForegroundColor Green
Write-Host "6. All categories should have content" -ForegroundColor Green

Write-Host ""
Write-Host "DATABASE CONFIGURATION:" -ForegroundColor Yellow
Write-Host "PostgreSQL: watch1-db container" -ForegroundColor Gray
Write-Host "- Database: watch1" -ForegroundColor Gray
Write-Host "- User: watch1_user" -ForegroundColor Gray
Write-Host "- Password: watch1_password" -ForegroundColor Gray
Write-Host ""
Write-Host "SQLite: /app/data/watch1.db" -ForegroundColor Gray
Write-Host "- File-based database" -ForegroundColor Gray
Write-Host "- Same schema as PostgreSQL" -ForegroundColor Gray
