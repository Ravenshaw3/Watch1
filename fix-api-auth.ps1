# Fix API Authorization and Chunk Errors for v3.0.2
param(
    [string]$UnraidIP = "192.168.254.14",
    [string]$Password = "videosmile"
)

Write-Host "Fix API Authorization and Chunk Errors" -ForegroundColor Red
Write-Host "======================================" -ForegroundColor Red
Write-Host "Target: $UnraidIP" -ForegroundColor Cyan
Write-Host ""

Write-Host "CRITICAL ISSUES IDENTIFIED:" -ForegroundColor Red
Write-Host "- API endpoints requiring authorization" -ForegroundColor Yellow
Write-Host "- 'ty chunk' loading errors in frontend" -ForegroundColor Yellow
Write-Host "- Missing JWT tokens in API requests" -ForegroundColor Yellow
Write-Host "- Frontend not handling 401 authorization errors" -ForegroundColor Yellow
Write-Host ""

Write-Host "ROOT CAUSES:" -ForegroundColor Yellow
Write-Host "1. Frontend API client not sending Authorization headers" -ForegroundColor Gray
Write-Host "2. Backend requiring JWT tokens for all protected endpoints" -ForegroundColor Gray
Write-Host "3. Chunk loading errors due to authentication failures" -ForegroundColor Gray
Write-Host "4. Auth store not properly managing JWT tokens" -ForegroundColor Gray
Write-Host ""

Write-Host "COMPREHENSIVE AUTHORIZATION FIX:" -ForegroundColor Cyan
Write-Host "1. Update API client to automatically add Authorization headers" -ForegroundColor White
Write-Host "2. Fix auth store to properly manage JWT tokens" -ForegroundColor White
Write-Host "3. Add proper error handling for 401 authorization errors" -ForegroundColor White
Write-Host "4. Fix chunk loading errors with global error handlers" -ForegroundColor White
Write-Host "5. Update backend to handle CORS and authorization properly" -ForegroundColor White
Write-Host "6. Test complete authentication flow" -ForegroundColor White
Write-Host ""

# Copy the authorization fix script
Write-Host "Copying comprehensive authorization fix..." -ForegroundColor Yellow
scp fix-api-auth-v302.sh root@${UnraidIP}:/mnt/user/appdata/watch1/

Write-Host "Authorization fix script copied!" -ForegroundColor Green
Write-Host ""

Write-Host "SSH to Unraid and run the authorization fix:" -ForegroundColor Cyan
Write-Host ""
Write-Host "ssh root@$UnraidIP" -ForegroundColor White
Write-Host "cd /mnt/user/appdata/watch1" -ForegroundColor White
Write-Host "chmod +x fix-api-auth-v302.sh" -ForegroundColor White
Write-Host "./fix-api-auth-v302.sh" -ForegroundColor White
Write-Host ""
Write-Host "Password: $Password" -ForegroundColor Yellow

Write-Host ""
Write-Host "WHAT THIS FIX ADDRESSES:" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host ""
Write-Host "API CLIENT FIXES:" -ForegroundColor Cyan
Write-Host "- Automatically adds Authorization: Bearer <token> headers" -ForegroundColor White
Write-Host "- Handles 401 errors by redirecting to login" -ForegroundColor White
Write-Host "- Adds proper CORS headers for cross-origin requests" -ForegroundColor White
Write-Host "- Logs all API requests for debugging" -ForegroundColor White
Write-Host ""
Write-Host "AUTH STORE FIXES:" -ForegroundColor Cyan
Write-Host "- Better JWT token management and storage" -ForegroundColor White
Write-Host "- Automatic user profile fetching after login" -ForegroundColor White
Write-Host "- Proper authentication state initialization" -ForegroundColor White
Write-Host "- Clear tokens on authorization failures" -ForegroundColor White
Write-Host ""
Write-Host "CHUNK ERROR FIXES:" -ForegroundColor Cyan
Write-Host "- Global error handler for chunk loading errors" -ForegroundColor White
Write-Host "- Automatic page reload on chunk failures" -ForegroundColor White
Write-Host "- Unhandled promise rejection handling" -ForegroundColor White
Write-Host "- Prevents 'ty chunk' errors from breaking the app" -ForegroundColor White

Write-Host ""
Write-Host "EXPECTED SUCCESS INDICATORS:" -ForegroundColor Yellow
Write-Host "============================" -ForegroundColor Yellow
Write-Host "✅ 'Authentication successful'" -ForegroundColor Green
Write-Host "✅ 'Media API (authorized): 200'" -ForegroundColor Green
Write-Host "✅ 'Categories API (authorized): 200'" -ForegroundColor Green
Write-Host "✅ 'Media API (no auth): 401' (should be 401)" -ForegroundColor Green
Write-Host "✅ 'AUTHORIZATION ISSUES RESOLVED!'" -ForegroundColor Green

Write-Host ""
Write-Host "AFTER THE FIX:" -ForegroundColor Yellow
Write-Host "==============" -ForegroundColor Yellow
Write-Host "1. Go to http://192.168.254.14:3000" -ForegroundColor Cyan
Write-Host "2. Login with test@example.com / testpass123" -ForegroundColor Cyan
Write-Host "3. All API calls should work with proper authorization" -ForegroundColor Green
Write-Host "4. No more 401 authorization errors" -ForegroundColor Green
Write-Host "5. No more 'ty chunk' loading errors" -ForegroundColor Green
Write-Host "6. Navigation tabs should appear and work properly" -ForegroundColor Green

Write-Host ""
Write-Host "TROUBLESHOOTING:" -ForegroundColor Red
Write-Host "If authorization issues persist:" -ForegroundColor Gray
Write-Host "- Check browser Network tab for API requests" -ForegroundColor Gray
Write-Host "- Verify Authorization header is being sent" -ForegroundColor Gray
Write-Host "- Check if JWT token is stored in localStorage" -ForegroundColor Gray
Write-Host "- Look for CORS errors in browser console" -ForegroundColor Gray
