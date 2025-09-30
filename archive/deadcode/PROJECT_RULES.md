# Watch1 Project Development Rules

## 🎯 Core Principles
These rules are derived from real debugging experiences and project evolution to prevent recurring issues and maintain code quality.

---

## 📋 **RULE 1: Integration-First Analysis**

### **Problem Prevented:** 
Frontend-backend data structure mismatches, runtime errors that static analysis misses

### **Rules:**
- ✅ **ALWAYS test actual API calls from frontend context before declaring "working"**
- ✅ **Trace data flow: API Response → Store Processing → Component Usage**
- ✅ **Validate TypeScript interfaces against actual runtime data**
- ❌ **NEVER assume static file analysis is sufficient for integration issues**

### **Required Checks:**
```bash
# Test actual integration
python test_frontend_backend_connection.py

# Validate API response structure
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/media/ | jq .

# Check TypeScript compilation
npm run type-check
```

---

## 📋 **RULE 2: Data Contract Validation**

### **Problem Prevented:** 
`response.media` vs `response.items` mismatches, missing required properties

### **Rules:**
- ✅ **Backend response structure MUST match frontend TypeScript interfaces**
- ✅ **Document all API response formats in code comments**
- ✅ **Make properties optional in TypeScript if backend doesn't guarantee them**
- ❌ **NEVER assume property names without cross-referencing**

### **Required Documentation:**
```typescript
// API Contract: /api/v1/media/
interface MediaSearchResponse {
  items: MediaFile[]        // ✅ Backend returns "items"
  media?: MediaFile[]       // ❌ Legacy - backend doesn't use this
  total: number            // ✅ Required
  page: number            // ✅ Required
  page_size: number       // ✅ Required
}

// Backend actual response example:
// {
//   "items": [...],
//   "total": 102,
//   "page": 1,
//   "page_size": 24
// }
```

---

## 📋 **RULE 3: Runtime Error Handling**

### **Problem Prevented:** 
Uncaught TypeErrors, chunk loading errors, undefined property access

### **Rules:**
- ✅ **All API responses MUST be validated before use**
- ✅ **Use optional chaining (`?.`) for potentially undefined properties**
- ✅ **Provide fallback values for missing data**
- ❌ **NEVER access nested properties without null checks**

### **Required Patterns:**
```typescript
// ✅ GOOD: Safe property access
const videoFiles = computed(() => 
  mediaFiles.value.filter(file => 
    file.mime_type?.startsWith('video/') || 
    file.category === 'movies' ||
    /\.(mp4|mkv|avi)$/i.test(file.filename)
  )
)

// ❌ BAD: Unsafe property access
const videoFiles = computed(() => 
  mediaFiles.value.filter(file => file.mime_type.startsWith('video/'))
)
```

---

## 📋 **RULE 4: Development Environment Consistency**

### **Problem Prevented:** 
Docker volume mount issues, environment inconsistencies, constant setbacks

### **Rules:**
- ✅ **Use standardized Docker development environment**
- ✅ **All developers MUST use same startup scripts**
- ✅ **Document all environment dependencies**
- ❌ **NEVER rely on individual developer machine configurations**

### **Required Workflow:**
```bash
# Start development environment
make dev-start  # or .\scripts\dev-start.ps1

# Monitor system health
make dev-health

# Reset if issues occur
make dev-reset

# Stop gracefully
make dev-stop
```

---

## 📋 **RULE 5: Testing Strategy**

### **Problem Prevented:** 
Production bugs, integration failures, regression issues

### **Rules:**
- ✅ **Write integration tests for all API endpoints**
- ✅ **Test frontend-backend communication explicitly**
- ✅ **Validate user workflows end-to-end**
- ❌ **NEVER deploy without comprehensive testing**

### **Required Test Coverage:**
```bash
# Backend API tests
python test_backend_api.py

# Frontend integration tests  
python test_frontend_backend_connection.py

# End-to-end user workflows
python test_user_workflows.py

# System health validation
python tools/health-monitor.py
```

---

## 📋 **RULE 6: Code Architecture Standards**

### **Problem Prevented:** 
Monolithic files, tight coupling, maintenance nightmares

### **Rules:**
- ✅ **Separate concerns: API, Store, Components, Types**
- ✅ **Keep files under 500 lines when possible**
- ✅ **Use consistent naming conventions**
- ❌ **NEVER put everything in one massive file**

### **Required Structure:**
```
frontend/src/
├── api/          # API client functions
├── stores/       # Pinia state management  
├── components/   # Reusable Vue components
├── views/        # Page-level components
├── types/        # TypeScript interfaces
└── utils/        # Helper functions

backend/
├── app/
│   ├── api/      # API endpoints
│   ├── core/     # Configuration, security
│   ├── crud/     # Database operations
│   └── models/   # Data models
```

---

## 📋 **RULE 7: Database & Migration Management**

### **Problem Prevented:** 
Data loss, schema mismatches, migration failures

### **Rules:**
- ✅ **Always create migration scripts for schema changes**
- ✅ **Test migrations on sample data before production**
- ✅ **Document database schema changes**
- ❌ **NEVER modify production database directly**

### **Required Process:**
```bash
# Create migration script
python create_migration.py "add_new_field"

# Test migration
python test_migration.py

# Apply migration
python apply_migration.py

# Backup before major changes
python backup_database.py
```

---

## 📋 **RULE 8: Error Debugging Protocol**

### **Problem Prevented:** 
Time wasted on debugging, repeated issues, unclear error sources

### **Rules:**
- ✅ **Check browser console FIRST for frontend issues**
- ✅ **Verify Docker container health before debugging code**
- ✅ **Test API endpoints independently before blaming frontend**
- ❌ **NEVER assume the problem is where you think it is**

### **Required Debug Sequence:**
```bash
# 1. Check system health
docker-compose ps
make dev-health

# 2. Check container logs
docker logs watch1-frontend-dev
docker logs watch1-backend-dev

# 3. Test API independently
python test_backend_api.py

# 4. Test frontend-backend integration
python test_frontend_backend_connection.py

# 5. Check browser console for JS errors
# Open DevTools (F12) → Console tab
```

---

## 📋 **RULE 9: Version Control & Branching**

### **Problem Prevented:** 
Lost work, conflicting changes, deployment issues

### **Rules:**
- ✅ **Use feature branches for all changes**
- ✅ **Test thoroughly before merging to main**
- ✅ **Tag stable versions for easy rollback**
- ❌ **NEVER commit directly to main branch**

### **Required Workflow:**
```bash
# Create feature branch
git checkout -b feature/fix-media-store

# Make changes and test
make test

# Commit with descriptive message
git commit -m "Fix media store response.items vs response.media mismatch"

# Push and create PR
git push origin feature/fix-media-store
```

---

## 📋 **RULE 10: Documentation & Knowledge Transfer**

### **Problem Prevented:** 
Repeated debugging, knowledge loss, onboarding difficulties

### **Rules:**
- ✅ **Document all debugging solutions in memories/wiki**
- ✅ **Update README after major changes**
- ✅ **Create troubleshooting guides for common issues**
- ❌ **NEVER fix issues without documenting the solution**

### **Required Documentation:**
```markdown
# In TROUBLESHOOTING.md
## Frontend Shows "Nothing Works"
**Symptoms:** Navigation tabs don't load, JavaScript errors
**Root Cause:** API response structure mismatch
**Solution:** Check media.ts store for response.items vs response.media
**Prevention:** Follow RULE 1 - Integration-First Analysis
```

---

## 📋 **RULE 11: Command Line String Safety**

### **Problem Prevented:** 
Unterminated string literal errors, PowerShell syntax issues, command execution failures

### **Rules:**
- ✅ **NEVER use complex Python one-liners in command line**
- ✅ **Create separate .py test files for multi-line code**
- ✅ **Use simple commands for quick tests only**
- ❌ **NEVER embed quotes within f-strings in command line**

### **Required Patterns:**
```bash
# ❌ BAD: Complex one-liner with nested quotes
python -c "import requests; r = requests.get('url'); print(f'Result: {r.json()['key']}')"

# ✅ GOOD: Simple test file
# Create test_api.py
python test_api.py

# ✅ GOOD: Simple one-liner without nested quotes
python -c "import requests; print('Testing API')"
```

### **Debugging Protocol:**
```bash
# When you see "SyntaxError: unterminated string literal"
# 1. Create a separate .py file instead
# 2. Use proper escaping for quotes
# 3. Test complex logic in files, not command line
```

---

## 📋 **RULE 12: Unicode and Character Encoding Safety**

### **Problem Prevented:** 
UnicodeEncodeError in Windows terminals, script execution failures, cross-platform compatibility issues

### **Rules:**
- ✅ **NEVER use Unicode emojis in Python scripts or test files**
- ✅ **Use ASCII characters only for console output**
- ✅ **Test scripts on Windows command prompt before deployment**
- ❌ **NEVER assume Unicode support in all terminal environments**

### **Required Patterns:**
```python
# ❌ BAD: Unicode emojis cause encoding errors
print("🎉 SUCCESS! All tests passed!")
print("❌ ERROR: Authentication failed")

# ✅ GOOD: ASCII-safe alternatives
print("SUCCESS! All tests passed!")
print("ERROR: Authentication failed")
print("TESTING POSTER DISPLAY FIX")

# ✅ GOOD: Use simple symbols if needed
print("* SUCCESS: All tests passed!")
print("X ERROR: Authentication failed")
print("+ INFO: Starting test...")
```

### **Debugging Protocol:**
```bash
# When you see "UnicodeEncodeError: 'charmap' codec can't encode"
# 1. Remove all Unicode emojis from the script
# 2. Use ASCII alternatives (SUCCESS, ERROR, INFO)
# 3. Test on Windows command prompt
# 4. Consider adding encoding declaration if needed
```

### **Safe Alternatives:**
- 🎉 → SUCCESS! or COMPLETE!
- ✅ → SUCCESS or OK
- ❌ → ERROR or FAILED
- ⚠️ → WARNING
- 🔧 → CONFIG or SETUP
- 📊 → STATS or DATA
- 🚀 → READY or LAUNCH

---

## 🚨 **CRITICAL CHECKPOINTS**

Before any deployment or major change:

1. **[ ] All tests passing** (`make test`)
2. **[ ] Docker containers healthy** (`make dev-health`)
3. **[ ] Frontend-backend integration verified** (`python test_frontend_backend_connection.py`)
4. **[ ] User workflows tested** (login → navigate → view media)
5. **[ ] Browser console clean** (no JavaScript errors)
6. **[ ] Documentation updated** (README, API docs, troubleshooting)

---

## 🎯 **SUCCESS METRICS**

- **Zero** "nothing works" incidents
- **< 30 minutes** to resolve integration issues
- **100%** test coverage for API endpoints
- **Consistent** development environment across team
- **Documented** solutions for all major debugging sessions

---

*These rules are living documents - update them as we learn from new debugging experiences.*
