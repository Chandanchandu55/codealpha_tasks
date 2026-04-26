#!/usr/bin/env python3
"""
Example usage of the Data Redundancy Removal System

This script demonstrates how to use the API to:
1. Validate entries before adding
2. Add unique entries
3. Handle duplicates
4. Search and manage entries
"""

import requests
import json
import time
import random

# Configuration
BASE_URL = "http://localhost:8000"

def print_response(response, title="Response"):
    """Pretty print API response"""
    print(f"\n=== {title} ===")
    print(f"Status Code: {response.status_code}")
    if response.headers.get('content-type', '').startswith('application/json'):
        print(json.dumps(response.json(), indent=2))
    else:
        print(response.text)
    print("=" * 50)

def validate_entry(content, data_type="text", source=None):
    """Validate if an entry can be added"""
    payload = {
        "content": content,
        "data_type": data_type
    }
    if source:
        payload["source"] = source
    
    response = requests.post(f"{BASE_URL}/validate", json=payload)
    return response

def add_entry(content, data_type="text", source=None, force_add=False):
    """Add a new data entry"""
    payload = {
        "content": content,
        "data_type": data_type
    }
    if source:
        payload["source"] = source
    
    params = {}
    if force_add:
        params["force_add"] = "true"
    
    response = requests.post(f"{BASE_URL}/add", json=payload, params=params)
    return response

def get_entries(unique_only=False):
    """Get all entries"""
    params = {}
    if unique_only:
        params["unique_only"] = "true"
    
    response = requests.get(f"{BASE_URL}/entries", params=params)
    return response

def search_entries(query, data_type=None):
    """Search entries"""
    params = {"query": query}
    if data_type:
        params["data_type"] = data_type
    
    response = requests.get(f"{BASE_URL}/search", params=params)
    return response

def get_statistics():
    """Get database statistics"""
    response = requests.get(f"{BASE_URL}/statistics")
    return response

def main():
    """Main demonstration function"""
    print("Data Redundancy Removal System - Example Usage")
    print("=" * 60)
    
    # Sample data for testing
    sample_entries = [
        "The quick brown fox jumps over the lazy dog",
        "A quick brown fox jumps over a lazy dog",  # Similar
        "The quick brown fox jumps over the lazy dog",  # Exact duplicate
        "Python is a powerful programming language",
        "Python programming is very powerful",  # Similar
        "Machine learning requires large datasets",
        "JavaScript is popular for web development",
        "Data science involves statistics and programming"
    ]
    
    try:
        # 1. Get initial statistics
        print("\n1. Getting initial statistics...")
        response = get_statistics()
        print_response(response, "Initial Statistics")
        
        # 2. Validate and add entries
        print("\n2. Adding sample entries...")
        for i, content in enumerate(sample_entries):
            print(f"\nProcessing entry {i+1}: {content[:50]}...")
            
            # Validate first
            validation = validate_entry(content, "example", f"sample_source_{i}")
            print_response(validation, f"Validation {i+1}")
            
            # Check if we can add it
            if validation.status_code == 200:
                validation_data = validation.json()
                if validation_data.get("can_add", False):
                    # Add the entry
                    add_response = add_entry(content, "example", f"sample_source_{i}")
                    print_response(add_response, f"Added Entry {i+1}")
                else:
                    print(f"Cannot add entry {i+1}: {validation_data.get('message', 'Unknown reason')}")
            
            time.sleep(0.5)  # Small delay between requests
        
        # 3. Get updated statistics
        print("\n3. Getting updated statistics...")
        response = get_statistics()
        print_response(response, "Updated Statistics")
        
        # 4. Get all entries
        print("\n4. Getting all entries...")
        response = get_entries()
        print_response(response, "All Entries")
        
        # 5. Get only unique entries
        print("\n5. Getting unique entries only...")
        response = get_entries(unique_only=True)
        print_response(response, "Unique Entries Only")
        
        # 6. Search for entries
        print("\n6. Searching for entries containing 'python'...")
        response = search_entries("python")
        print_response(response, "Search Results for 'python'")
        
        # 7. Demonstrate force adding a duplicate
        print("\n7. Demonstrating force add of duplicate...")
        duplicate_content = "This is a forced duplicate entry"
        
        # Add first entry
        add_response = add_entry(duplicate_content, "force_test", "demo_source")
        print_response(add_response, "First Entry Added")
        
        # Try to add duplicate (should fail)
        validation = validate_entry(duplicate_content, "force_test", "demo_source")
        print_response(validation, "Duplicate Validation")
        
        # Force add the duplicate
        force_add_response = add_entry(duplicate_content, "force_test", "demo_source", force_add=True)
        print_response(force_add_response, "Force Added Duplicate")
        
        # 8. Final statistics
        print("\n8. Final statistics...")
        response = get_statistics()
        print_response(response, "Final Statistics")
        
        print("\n" + "=" * 60)
        print("Example usage completed successfully!")
        print("Check the API documentation at http://localhost:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Start it with: python main.py")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
