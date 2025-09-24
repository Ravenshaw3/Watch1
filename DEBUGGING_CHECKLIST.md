# Watch1 Debugging Checklist

## 🚨 **When "Nothing Works" in Frontend**

### **Immediate Actions (5 minutes)**
- [ ] Check browser console (F12) for JavaScript errors
- [ ] Verify containers are running: `docker-compose ps`
- [ ] Test backend health: `curl http://localhost:8000/api/v1/settings/test`
- [ ] Test frontend accessibility: `curl http://localhost:3000`

### **API Integration Check (10 minutes)**
- [ ] Run integration test: `python test_frontend_backend_connection.py`
- [ ] Verify API response structure matches TypeScript interfaces
- [ ] Check for `response.items` vs `response.media` mismatches
- [ ] Validate authentication token flow

### **Common Culprits**
- [ ] **Data Structure Mismatch**: Backend returns `items`, frontend expects `media`
- [ ] **Missing Properties**: TypeScript requires fields backend doesn't provide
- [ ] **Chunk Loading Errors**: Dynamic imports failing in Vue router
- [ ] **Authentication Issues**: Token not being passed or expired
- [ ] **CORS Problems**: Frontend can't communicate with backend

---

## 🔧 **Before Making Changes**

### **Pre-Development Check**
- [ ] Pull latest changes: `git pull origin main`
- [ ] Start clean environment: `make dev-reset && make dev-start`
- [ ] Verify baseline functionality: `make test`
- [ ] Create feature branch: `git checkout -b feature/your-change`

### **During Development**
- [ ] Test changes incrementally
- [ ] Check browser console after each change
- [ ] Verify API responses match expectations
- [ ] Update TypeScript interfaces if backend changes

### **Before Committing**
- [ ] All tests pass: `make test`
- [ ] No TypeScript errors: `npm run type-check`
- [ ] Browser console clean
- [ ] Integration test passes: `python test_frontend_backend_connection.py`

---

## 📊 **API Response Validation**

### **Check Response Structure**
```bash
# Login and get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"testpass123"}' \
  | jq -r .access_token)

# Test media API
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/media/ | jq .
```

### **Expected Structure**
```json
{
  "items": [...],     // ✅ Frontend expects this
  "total": 102,       // ✅ Required
  "page": 1,          // ✅ Required  
  "page_size": 24     // ✅ Required
}
```

---

## 🐛 **Common Error Patterns**

### **TypeError: Cannot read property 'X' of undefined**
- **Cause**: Accessing nested properties without null checks
- **Fix**: Use optional chaining `object?.property?.nested`
- **Prevention**: Make properties optional in TypeScript interfaces

### **Chunk loading failed**
- **Cause**: Dynamic imports in Vue router failing
- **Fix**: Check if imported files exist and have correct syntax
- **Prevention**: Test all routes after changes

### **Network Error / CORS**
- **Cause**: Frontend can't communicate with backend
- **Fix**: Check CORS configuration in backend
- **Prevention**: Test API calls from frontend context

### **401 Unauthorized**
- **Cause**: Authentication token issues
- **Fix**: Check token storage and API client interceptors
- **Prevention**: Test auth flow end-to-end

---

## 🎯 **Quick Fixes**

### **Frontend Not Loading**
```bash
# Restart frontend container
docker-compose -f docker-compose.dev.yml restart frontend

# Or rebuild if needed
docker-compose -f docker-compose.dev.yml up -d --force-recreate frontend
```

### **Backend API Issues**
```bash
# Check backend logs
docker logs watch1-backend-dev --tail=50

# Restart backend
docker-compose -f docker-compose.dev.yml restart backend
```

### **Database Problems**
```bash
# Check database connection
docker exec watch1-backend-dev python -c "import sqlite3; print('DB OK')"

# Reset database if needed
python setup_media_directories.py
```

---

## 📝 **Documentation Updates**

### **After Fixing Issues**
- [ ] Update this checklist with new patterns
- [ ] Add solution to PROJECT_RULES.md
- [ ] Create memory with solution details
- [ ] Update README if architecture changed

### **Knowledge Capture**
```markdown
## New Issue Pattern
**Symptoms:** [What user sees]
**Root Cause:** [Technical reason]
**Solution:** [How to fix]
**Prevention:** [How to avoid in future]
**Rule Reference:** [Which project rule applies]
```

---

## 🚀 **Emergency Recovery**

### **Complete System Reset**
```bash
# Nuclear option - reset everything
make dev-stop
docker system prune -f
make dev-start
python setup_media_directories.py
make test
```

### **Rollback to Last Working State**
```bash
# Find last working commit
git log --oneline -10

# Reset to working commit
git reset --hard <commit-hash>

# Force restart environment
make dev-reset
```

---

*Keep this checklist handy during development - it's designed for quick reference during debugging sessions.*
