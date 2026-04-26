#!/usr/bin/env python3
"""
API Test Script for Data Redundancy Removal System
Tests all endpoints to ensure they work correctly
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, params=None):
    """Test an API endpoint"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, params=params)
        elif method == "PUT":
            response = requests.put(f"{BASE_URL}{endpoint}", json=data)
        elif method == "DELETE":
            response = requests.delete(f"{BASE_URL}{endpoint}")
        else:
            return False, f"Unknown method: {method}"
        
        return response.status_code, response.json()
    except Exception as e:
        return False, str(e)

def print_test_result(test_name, status_code, response_data, expected_status=200):
    """Print test result in a formatted way"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"Expected Status: {expected_status}, Got: {status_code}")
    
    if status_code == expected_status:
        print("✅ PASSED")
    else:
        print("❌ FAILED")
    
    if isinstance(response_data, dict):
        print("Response:")
        print(json.dumps(response_data, indent=2)[:500] + "..." if len(json.dumps(response_data)) > 500 else json.dumps(response_data, indent=2))
    else:
        print(f"Response: {response_data}")
    
    return status_code == expected_status

def main():
    """Run all API tests"""
    print("🧪 Testing Data Redundancy Removal System API")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = 0
    
    # Test 1: Root endpoint
    total_tests += 1
    status, data = test_endpoint("GET", "/")
    if print_test_result("Root Endpoint", status, data):
        passed_tests += 1
    
    # Test 2: Validate unique entry
    total_tests += 1
    test_entry = {
        "content": "This is a unique test entry for API testing",
        "data_type": "api_test",
        "source": "test_script"
    }
    status, data = test_endpoint("POST", "/validate", test_entry)
    if print_test_result("Validate Unique Entry", status, data):
        passed_tests += 1
    
    # Test 3: Add unique entry
    total_tests += 1
    status, data = test_endpoint("POST", "/add", test_entry)
    if print_test_result("Add Unique Entry", status, data):
        passed_tests += 1
        entry_id = data.get("id") if isinstance(data, dict) else None
    
    # Test 4: Try to add exact duplicate
    total_tests += 1
    status, data = test_endpoint("POST", "/add", test_entry)
    if print_test_result("Add Exact Duplicate (should fail)", status, data, expected_status=400):
        passed_tests += 1
    
    # Test 5: Add similar entry (should be detected as similar)
    total_tests += 1
    similar_entry = {
        "content": "This is a unique test entry for API testing!",  # Added exclamation
        "data_type": "api_test",
        "source": "test_script"
    }
    status, data = test_endpoint("POST", "/add", similar_entry)
    if print_test_result("Add Similar Entry (should fail)", status, data, expected_status=400):
        passed_tests += 1
    
    # Test 6: Add different type entry
    total_tests += 1
    different_entry = {
        "content": "Completely different content for testing",
        "data_type": "different_type",
        "source": "test_script"
    }
    status, data = test_endpoint("POST", "/add", different_entry)
    if print_test_result("Add Different Type Entry", status, data):
        passed_tests += 1
    
    # Test 7: Get all entries
    total_tests += 1
    status, data = test_endpoint("GET", "/entries")
    if print_test_result("Get All Entries", status, data):
        passed_tests += 1
    
    # Test 8: Get unique entries only
    total_tests += 1
    status, data = test_endpoint("GET", "/entries", params={"unique_only": "true"})
    if print_test_result("Get Unique Entries Only", status, data):
        passed_tests += 1
    
    # Test 9: Search entries
    total_tests += 1
    status, data = test_endpoint("GET", "/search", params={"query": "unique test"})
    if print_test_result("Search Entries", status, data):
        passed_tests += 1
    
    # Test 10: Get statistics
    total_tests += 1
    status, data = test_endpoint("GET", "/statistics")
    if print_test_result("Get Statistics", status, data):
        passed_tests += 1
    
    # Test 11: Force add duplicate
    total_tests += 1
    status, data = test_endpoint("POST", "/add", test_entry, params={"force_add": "true"})
    if print_test_result("Force Add Duplicate", status, data):
        passed_tests += 1
        duplicate_id = data.get("id") if isinstance(data, dict) else None
    
    # Test 12: Update entry (if we have an entry ID)
    if 'entry_id' in locals() and entry_id:
        total_tests += 1
        update_data = {"content": "Updated test content", "data_type": "updated_test"}
        status, data = test_endpoint("PUT", f"/entries/{entry_id}", update_data)
        if print_test_result("Update Entry", status, data):
            passed_tests += 1
    
    # Test 13: Mark as duplicate (if we have duplicate ID)
    if 'duplicate_id' in locals() and duplicate_id and 'entry_id' in locals() and entry_id:
        total_tests += 1
        status, data = test_endpoint("POST", f"/entries/{duplicate_id}/mark-duplicate", 
                                   params={"original_id": entry_id, "similarity_score": "0.95"})
        if print_test_result("Mark as Duplicate", status, data):
            passed_tests += 1
    
    # Test 14: Get specific entry
    if 'entry_id' in locals() and entry_id:
        total_tests += 1
        status, data = test_endpoint("GET", f"/entries/{entry_id}")
        if print_test_result("Get Specific Entry", status, data):
            passed_tests += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print("🏁 TEST SUMMARY")
    print(f"Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! The system is working correctly.")
    else:
        print(f"⚠️  {total_tests - passed_tests} test(s) failed. Please check the issues above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n💥 Test script error: {str(e)}")
        exit(1)
