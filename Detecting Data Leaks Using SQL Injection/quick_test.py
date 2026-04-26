#!/usr/bin/env python3
"""
Quick Test Script for SQL Injection Detection System
Run this script to quickly validate all system functionality
"""

import requests
import json
import time

def test_system():
    """Quick comprehensive test of the SQL Injection Detection System"""
    
    print("🚀 SQL Injection Detection System - Quick Test")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health Check
    print("\n1️⃣ Testing System Health...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Check: PASSED")
            print(f"   Status: {data['status']}")
        else:
            print("❌ Health Check: FAILED")
            return False
    except Exception as e:
        print(f"❌ Health Check: ERROR - {str(e)}")
        return False
    
    # Test 2: SQL Injection Detection
    print("\n2️⃣ Testing SQL Injection Detection...")
    
    test_cases = [
        ("Safe Query", "SELECT * FROM users WHERE id = 1", True),
        ("Basic Injection", "SELECT * FROM users WHERE id = 1 OR 1=1", False),
        ("Union Attack", "SELECT * FROM users WHERE id = 1 UNION SELECT password FROM admin", False),
        ("Comment Attack", "SELECT * FROM users WHERE id = 1 -- DROP TABLE users", False),
        ("Non-SQL Text", "This is just regular text without SQL", True)
    ]
    
    all_passed = True
    for name, query, expected_safe in test_cases:
        try:
            response = requests.post(f"{base_url}/sql/validate", json={'query': query})
            if response.status_code == 200:
                result = response.json()
                is_safe = result['is_safe']
                if is_safe == expected_safe:
                    print(f"✅ {name}: PASSED (Risk: {result['risk_score']})")
                else:
                    print(f"❌ {name}: FAILED (Expected Safe: {expected_safe}, Got Safe: {is_safe})")
                    all_passed = False
            else:
                print(f"❌ {name}: FAILED (Status: {response.status_code})")
                all_passed = False
        except Exception as e:
            print(f"❌ {name}: ERROR - {str(e)}")
            all_passed = False
    
    # Test 3: User Registration
    print("\n3️⃣ Testing User Registration...")
    try:
        response = requests.post(f"{base_url}/auth/register", json={
            'username': f'testuser_{int(time.time())}',
            'email': f'test_{int(time.time())}@example.com',
            'password': 'TestPass123!',
            'is_admin': False
        })
        if response.status_code == 200:
            user = response.json()
            print("✅ User Registration: PASSED")
            print(f"   Username: {user['username']}")
            api_key = user['api_key']
        else:
            print("❌ User Registration: FAILED")
            all_passed = False
    except Exception as e:
        print(f"❌ User Registration: ERROR - {str(e)}")
        all_passed = False
    
    # Test 4: Web Interface
    print("\n4️⃣ Testing Web Interface...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200 and 'SQL Injection Detection' in response.text:
            print("✅ Web Interface: PASSED")
        else:
            print("❌ Web Interface: FAILED")
            all_passed = False
    except Exception as e:
        print(f"❌ Web Interface: ERROR - {str(e)}")
        all_passed = False
    
    # Test 5: API Documentation
    print("\n5️⃣ Testing API Documentation...")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ API Documentation: PASSED")
        else:
            print("❌ API Documentation: FAILED")
            all_passed = False
    except Exception as e:
        print(f"❌ API Documentation: ERROR - {str(e)}")
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! System is fully operational!")
        print("\n🌐 Access Points:")
        print(f"   📊 Web Interface: {base_url}")
        print(f"   📖 API Documentation: {base_url}/docs")
        print(f"   💚 Health Check: {base_url}/health")
        print(f"   🧪 SQL Validation: POST {base_url}/sql/validate")
        print("\n✨ Your SQL Injection Detection System is ready for production!")
    else:
        print("⚠️  Some tests failed. Please check the system.")
    
    return all_passed

if __name__ == "__main__":
    test_system()
