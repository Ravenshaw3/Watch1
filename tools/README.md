# Watch1 Testing & Feature Mapping System

A comprehensive testing framework for the Watch1 Media Server that validates features, tracks mappings, and ensures consistency between frontend and backend components.

## 🎯 Overview

This testing system provides:
- **Comprehensive Integration Testing** - Tests all API endpoints and frontend functionality
- **Feature Mapping Validation** - Ensures frontend routes map correctly to backend endpoints
- **Link Consistency Checking** - Validates navigation and API consistency
- **Performance Benchmarking** - Tracks response times and performance metrics
- **Development Tracking** - Manages feature lifecycle and dependencies

## 📁 Files Structure

```
tools/
├── comprehensive-test-suite.py    # Main integration test suite
├── feature-mapper.py             # Feature mapping and link validator
├── run-tests.py                  # Master test orchestrator
├── add-feature.py                # Tool to add new features
├── test-config.yaml              # Test configuration and rules
├── test-frontend-backend-integration.py  # Existing integration test
└── README.md                     # This documentation
```

## 🚀 Quick Start

### Run All Tests
```bash
# Run complete test suite
python tools/run-tests.py

# This will execute:
# 1. Feature mapping validation
# 2. Comprehensive integration tests
# 3. Frontend-backend integration tests
# 4. Generate master report
```

### Run Individual Test Suites
```bash
# Feature mapping validation only
python tools/feature-mapper.py

# Integration tests only
python tools/comprehensive-test-suite.py

# Original integration test
python tools/test-frontend-backend-integration.py
```

## 🔧 Configuration

### Test Configuration (`test-config.yaml`)

The main configuration file defines:
- **Feature Mappings** - Links between frontend routes and backend endpoints
- **Test Rules** - Validation criteria and performance benchmarks
- **Dependencies** - Feature dependency chains
- **Performance Benchmarks** - Expected response times

Example feature mapping:
```yaml
feature_mappings:
  media_management:
    frontend_routes:
      - "/"
      - "/library"
    backend_endpoints:
      - "GET /api/v1/media/"
      - "GET /api/v1/media/categories"
    dependencies: ["authentication"]
```

## 📊 Test Categories

### 1. Service Availability
- Backend health check
- Frontend accessibility
- Docker container status

### 2. Authentication Flow
- Login functionality
- Token validation
- User profile access
- Admin privilege checking

### 3. Media Management
- Media listing and filtering
- Category management
- Media scanning functionality
- File metadata extraction

### 4. Admin Features
- Database maintenance
- Worker health monitoring
- Job history tracking
- System information

### 5. Feature Integration
- Playlist management
- Settings configuration
- Analytics dashboard
- System monitoring

## 🗺️ Feature Mapping System

### Adding New Features

```bash
# Interactive feature addition
python tools/add-feature.py add

# List all features
python tools/add-feature.py list

# Remove a feature
python tools/add-feature.py remove feature_name

# Update feature status
python tools/add-feature.py status feature_name completed_features
```

### Feature Lifecycle

Features progress through these stages:
1. **planned_features** - Planned for development
2. **in_development** - Currently being developed
3. **completed_features** - Fully implemented and tested
4. **deprecated_features** - No longer supported

### Dependency Management

The system automatically validates:
- Circular dependency detection
- Missing dependency identification
- Dependency chain integrity

## 📈 Performance Monitoring

### Response Time Benchmarks

Default benchmarks (configurable in `test-config.yaml`):
- Health check: 100ms
- Authentication: 1000ms
- Media listing: 2000ms
- Media scanning: 30000ms
- Admin operations: 500ms

### Performance Validation

Tests automatically:
- Compare actual vs expected response times
- Identify performance regressions
- Track performance trends over time

## 🔗 Link Validation Rules

### API Consistency Rules
- All endpoints use kebab-case naming
- Collection endpoints end with `/`
- Admin endpoints start with `/admin/`
- Consistent error response format

### Navigation Consistency
- All routes accessible via navigation
- Admin routes only visible to superusers
- Proper route protection and guards

### Frontend-Backend Mapping
- Frontend routes map to correct backend endpoints
- All required endpoints are implemented
- Proper authentication flow

## 📋 Reports and Output

### Test Reports Generated

1. **master-test-report.json** - Overall test execution summary
2. **test-report.json** - Detailed integration test results
3. **feature-mapping-report.json** - Feature validation results

### Report Contents

Each report includes:
- Test execution summary
- Performance metrics
- Failed test details
- Recommendations for fixes
- Historical trend data

## 🛠️ Development Workflow

### Adding a New Feature

1. **Plan the Feature**
   ```bash
   python tools/add-feature.py add
   # Follow interactive prompts
   ```

2. **Validate Mapping**
   ```bash
   python tools/feature-mapper.py
   # Check for mapping issues
   ```

3. **Implement Feature**
   - Create frontend routes
   - Implement backend endpoints
   - Add tests as needed

4. **Test Integration**
   ```bash
   python tools/run-tests.py
   # Verify everything works
   ```

5. **Update Status**
   ```bash
   python tools/add-feature.py status feature_name completed_features
   ```

### Continuous Integration

Recommended CI pipeline:
```bash
# Pre-commit hooks
python tools/feature-mapper.py  # Validate mappings
python tools/comprehensive-test-suite.py  # Quick smoke tests

# Full CI pipeline
python tools/run-tests.py  # Complete test suite
```

## 🔍 Troubleshooting

### Common Issues

1. **Service Not Available**
   - Check Docker containers: `docker-compose -f docker-compose.dev.yml ps`
   - Restart services: `docker-compose -f docker-compose.dev.yml restart`

2. **Authentication Failures**
   - Verify test credentials in `test-config.yaml`
   - Check user exists in database
   - Validate superuser permissions

3. **Feature Mapping Errors**
   - Check route format (must start with `/`)
   - Verify endpoint format (METHOD /api/v1/path)
   - Validate dependencies exist

4. **Performance Issues**
   - Review benchmark thresholds
   - Check for network latency
   - Monitor resource usage

### Debug Mode

Enable verbose output:
```bash
# Set environment variable for detailed logging
export WATCH1_TEST_DEBUG=1
python tools/run-tests.py
```

## 📚 API Reference

### Test Configuration Schema

```yaml
test_environment:
  backend_url: string
  frontend_url: string
  timeout_seconds: integer

feature_mappings:
  feature_name:
    frontend_routes: [string]
    backend_endpoints: [string]
    dependencies: [string]
    requires_admin: boolean

test_rules:
  response_time:
    max_acceptable_ms: integer
  success_criteria:
    minimum_pass_rate: integer
```

### Command Line Interface

```bash
# Master test runner
python tools/run-tests.py

# Feature mapper
python tools/feature-mapper.py

# Feature management
python tools/add-feature.py [add|list|remove|status] [args...]

# Comprehensive tests
python tools/comprehensive-test-suite.py [backend_url] [frontend_url]
```

## 🤝 Contributing

### Adding New Test Categories

1. Edit `comprehensive-test-suite.py`
2. Add new test method following naming convention: `test_category_name()`
3. Update `run_all_tests()` to include new category
4. Add configuration to `test-config.yaml`

### Extending Feature Validation

1. Edit `feature-mapper.py`
2. Add new validation method: `validate_new_rule()`
3. Call from `run_all_validations()`
4. Update configuration schema

### Performance Benchmarks

1. Add benchmarks to `test-config.yaml`
2. Update validation logic in test suites
3. Document expected performance characteristics

## 📊 Metrics and KPIs

### Success Metrics
- **Test Pass Rate**: >90% for production readiness
- **Feature Coverage**: All features have mappings and tests
- **Response Time**: Within configured benchmarks
- **Link Consistency**: 100% valid mappings

### Quality Gates
- All critical features must pass
- No circular dependencies
- All admin features properly protected
- Performance within acceptable limits

## 🔄 Maintenance

### Regular Tasks
- Update performance benchmarks as system evolves
- Review and update feature mappings
- Clean up deprecated features
- Monitor test execution times

### Version Updates
- Update test credentials when changed
- Adjust benchmarks for performance improvements
- Add new features to tracking system
- Archive old test reports

---

## 📞 Support

For issues with the testing system:
1. Check the troubleshooting section
2. Review generated reports for detailed error information
3. Validate configuration files are properly formatted
4. Ensure all services are running and accessible

The testing system is designed to grow with your application - add new features, update mappings, and maintain quality as you develop!
