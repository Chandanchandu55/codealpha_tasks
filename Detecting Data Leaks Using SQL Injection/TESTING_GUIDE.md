# SQL Injection Detection & Prevention System - Testing Guide

## 🧪 Comprehensive Testing Instructions

This guide provides step-by-step instructions to test all features of the SQL Injection Detection & Prevention System.

## 🚀 Quick Start Testing

### Step 1: Start the Server

```bash
cd "Detecting Data Leaks Using SQL Injection"
pip install -r requirements.txt
python main.py
```

**Expected Output:**
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup
INFO:__main__:SQL Injection Security System started successfully
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Verify System Health

Open your browser and navigate to:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔍 Core Functionality Testing

### Test 1: SQL Injection Detection

#### Method 1: Using curl (Command Line)

**Safe Query Test:**
```bash
curl -X POST "http://localhost:8000/sql/validate" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM users WHERE id = 1"}'
```

**Expected Response:**
```json
{
  "is_safe": true,
  "can_add": true,
  "risk_score": 10,
  "severity": "info",
  "detected_patterns": [],
  "blocked_reason": null
}
```

**Malicious Query Test:**
```bash
curl -X POST "http://localhost:8000/sql/validate" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM users WHERE id = 1 OR 1=1"}'
```

**Expected Response:**
```json
{
  "is_safe": false,
  "can_add": false,
  "risk_score": 40,
  "severity": "medium",
  "detected_patterns": ["OR 1=1", "SELECT"],
  "blocked_reason": "Risk score: 40"
}
```

#### Method 2: Using Python Script

```python
import requests

# Test safe query
response = requests.post('http://localhost:8000/sql/validate', json={
    'query': 'SELECT * FROM users WHERE id = 1'
})
result = response.json()
print(f"Safe Query - Risk: {result['risk_score']}, Safe: {result['is_safe']}")

# Test malicious query
response = requests.post('http://localhost:8000/sql/validate', json={
    'query': 'SELECT * FROM users WHERE id = 1 OR 1=1'
})
result = response.json()
print(f"Malicious Query - Risk: {result['risk_score']}, Safe: {result['is_safe']}")
```

### Test 2: Advanced SQL Injection Patterns

Test these injection patterns to verify detection:

| Pattern Type | Query | Expected Risk Score | Expected Safe |
|-------------|-------|-------------------|---------------|
| Union Attack | `SELECT * FROM users WHERE id = 1 UNION SELECT password FROM admin` | 80 | False |
| Comment Attack | `SELECT * FROM users WHERE id = 1 -- DROP TABLE users` | 100 | False |
| Time-based Attack | `SELECT * FROM users WHERE id = 1 AND SLEEP(5)` | 40 | False |
| String-based Attack | `SELECT * FROM users WHERE username = 'admin' OR '1'='1'` | 40+ | False |
| Advanced Attack | `'; DROP TABLE users; SELECT * FROM data WHERE '1'='1` | 100 | False |

### Test 3: Non-SQL Content

```bash
curl -X POST "http://localhost:8000/sql/validate" \
  -H "Content-Type: application/json" \
  -d '{"query": "This is just regular text without SQL commands"}'
```

**Expected Response:**
```json
{
  "is_safe": true,
  "can_add": true,
  "risk_score": 0,
  "severity": "info",
  "detected_patterns": [],
  "blocked_reason": null
}
```

## 🔐 Authentication & Authorization Testing

### Test 4: User Registration

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "is_admin": false
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-04-26T...",
  "api_key": "f7JCP8EWG_eJ5rE0O3n6..."
}
```

### Test 5: User Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

**Expected Response:**
```json
{
  "access_token": "f7JCP8EWG_eJ5rE0O3n6...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_active": true,
    "is_admin": false
  }
}
```

## 🌐 Web Interface Testing

### Test 6: Web Interface Access

1. **Main Dashboard**: Open http://localhost:8000
   - Should show a beautiful security dashboard
   - Display system status as "Online and Secure"
   - Show all security features

2. **API Documentation**: Open http://localhost:8000/docs
   - Should display interactive Swagger UI
   - All endpoints should be documented
   - Test endpoints directly from the interface

3. **Health Check**: Open http://localhost:8000/health
   - Should return system health status
   - Show version information

## 🧪 Automated Testing

### Test 7: Run Comprehensive Test Suite

```bash
python test_api.py
```

**Expected Output:**
```
🧪 Testing Data Redundancy Removal System API
============================================================
✅ PASSED: Root Endpoint
✅ PASSED: Validate Unique Entry
✅ PASSED: Add Unique Entry
...
🏁 TEST SUMMARY
Passed: X/X
Success Rate: 100%
🎉 ALL TESTS PASSED!
```

### Test 8: Run Example Usage Demo

```bash
python example_usage.py
```

**Expected Output:**
```
🛡️ SQL Injection Detection & Prevention System - Complete Demo
============================================================
✅ System Health: System is running and healthy
✅ SQL Test: Safe Query - Status: SAFE | Risk: 10 | Severity: info
✅ SQL Test: Basic SQL Injection - Status: BLOCKED | Risk: 40 | Severity: medium
...
🎉 SQL Injection Security System Demo Complete!
```

## 🔧 Advanced Testing Scenarios

### Test 9: Capability Code System

1. **Create Admin User:**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "AdminPass123!",
    "is_admin": true
  }'
```

2. **Login as Admin:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "AdminPass123!"
  }'
```

3. **Create Capability Code:**
```bash
curl -X POST "http://localhost:8000/capability-codes" \
  -H "Authorization: Bearer ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "permissions": ["read", "write"],
    "expires_in_minutes": 60,
    "max_uses": 5
  }'
```

### Test 10: Security Monitoring

1. **View Security Events:**
```bash
curl -H "Authorization: Bearer ADMIN_API_KEY" \
  "http://localhost:8000/security/events"
```

2. **View Injection Attempts:**
```bash
curl -H "Authorization: Bearer ADMIN_API_KEY" \
  "http://localhost:8000/security/attempts"
```

3. **View Security Dashboard:**
```bash
curl -H "Authorization: Bearer ADMIN_API_KEY" \
  "http://localhost:8000/dashboard"
```

## 🐛 Troubleshooting Common Issues

### Issue 1: Server Won't Start

**Problem:** Port 8000 already in use

**Solution:**
```bash
# Kill process using port 8000
taskkill /F /IM python.exe

# Or use different port
python -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8001)"
```

### Issue 2: Database Errors

**Problem:** Database file locked or corrupted

**Solution:**
```bash
# Delete and recreate database
rm sql_injection_security.db
python main.py
```

### Issue 3: Import Errors

**Problem:** Missing dependencies

**Solution:**
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue 4: Permission Errors

**Problem:** Access denied to endpoints

**Solution:**
- Use correct API key in Authorization header
- Ensure user has proper permissions
- Check if user is active

## 📊 Testing Checklist

### Core Functionality
- [ ] Server starts successfully
- [ ] Health check endpoint works
- [ ] Web interface loads
- [ ] API documentation accessible
- [ ] SQL injection detection works
- [ ] Safe queries pass validation
- [ ] Malicious queries are blocked

### Authentication
- [ ] User registration works
- [ ] User login works
- [ ] API keys are generated
- [ ] Tokens are valid
- [ ] Access control works

### Security Features
- [ ] AES-256 encryption works
- [ ] Capability codes work
- [ ] Rate limiting works
- [ ] Security events logged
- [ ] Risk assessment accurate

### Advanced Features
- [ ] Security monitoring works
- [ ] Dashboard accessible
- [ ] Logs are created
- [ ] Statistics accurate

## 🎯 Performance Testing

### Test 11: Load Testing

```python
import requests
import time
import concurrent.futures

def test_sql_validation():
    response = requests.post('http://localhost:8000/sql/validate', json={
        'query': 'SELECT * FROM users WHERE id = 1'
    })
    return response.status_code == 200

# Test 100 concurrent requests
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(test_sql_validation) for _ in range(100)]
    results = [f.result() for f in futures]

success_rate = sum(results) / len(results) * 100
print(f"Success Rate: {success_rate:.1f}%")
```

## 📈 Expected Results Summary

### SQL Injection Detection Results
| Query Type | Risk Score | Is Safe | Status |
|------------|------------|---------|---------|
| Safe Query | 0-10 | True | ✅ PASSED |
| Basic Injection | 40-60 | False | ❌ BLOCKED |
| Union Attack | 80-100 | False | ❌ BLOCKED |
| Advanced Attack | 100 | False | ❌ BLOCKED |
| Non-SQL Text | 0 | True | ✅ PASSED |

### System Performance
- **Response Time**: < 100ms for SQL validation
- **Concurrent Users**: 100+ supported
- **Memory Usage**: < 100MB
- **CPU Usage**: < 10% under normal load

## 🎉 Testing Complete!

If all tests pass, your SQL Injection Detection & Prevention System is fully operational and ready for production use!

## 📞 Support

For issues or questions:
1. Check this testing guide
2. Review the main README.md
3. Check server logs for error details
4. Run the automated test suite for diagnostics
