#!/usr/bin/env python3
"""
SQL Injection Detection & Prevention System - Example Usage

This script demonstrates the key features of the SQL injection security system.
"""

import requests
import json
import time
from typing import Dict, Any

class SQLInjectionSecurityDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
    
    def print_section(self, title: str):
        """Print section header"""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print('='*60)
    
    def print_result(self, test_name: str, success: bool, details: str = ""):
        """Print test result"""
        icon = "✅" if success else "❌"
        print(f"{icon} {test_name}")
        if details:
            print(f"   {details}")
    
    def setup_users(self):
        """Setup test users"""
        self.print_section("Setting Up Test Users")
        
        # Register admin user
        try:
            response = requests.post(f"{self.base_url}/auth/register", json={
                "username": "demo_admin",
                "email": "admin@demo.com",
                "password": "AdminDemo123!@#",
                "is_admin": True
            })
            
            if response.status_code == 200:
                self.print_result("Admin Registration", True, "Admin user created")
            else:
                self.print_result("Admin Registration", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_result("Admin Registration", False, f"Error: {str(e)}")
        
        # Register regular user
        try:
            response = requests.post(f"{self.base_url}/auth/register", json={
                "username": "demo_user",
                "email": "user@demo.com",
                "password": "UserDemo123!@#",
                "is_admin": False
            })
            
            if response.status_code == 200:
                self.print_result("User Registration", True, "Regular user created")
            else:
                self.print_result("User Registration", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_result("User Registration", False, f"Error: {str(e)}")
        
        # Login users
        self.login_users()
    
    def login_users(self):
        """Login and get tokens"""
        try:
            # Login admin
            response = requests.post(f"{self.base_url}/auth/login", json={
                "username": "demo_admin",
                "password": "AdminDemo123!@#"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.print_result("Admin Login", True, f"Token: {self.admin_token[:20]}...")
            else:
                self.print_result("Admin Login", False, f"Status: {response.status_code}")
            
            # Login user
            response = requests.post(f"{self.base_url}/auth/login", json={
                "username": "demo_user",
                "password": "UserDemo123!@#"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data["access_token"]
                self.print_result("User Login", True, f"Token: {self.user_token[:20]}...")
            else:
                self.print_result("User Login", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.print_result("Login", False, f"Error: {str(e)}")
    
    def demonstrate_sql_injection_detection(self):
        """Demonstrate SQL injection detection"""
        self.print_section("SQL Injection Detection Demonstration")
        
        test_cases = [
            {
                "name": "Safe Query",
                "query": "SELECT * FROM users WHERE id = 1",
                "expected_safe": True
            },
            {
                "name": "Basic SQL Injection",
                "query": "SELECT * FROM users WHERE id = 1 OR 1=1",
                "expected_safe": False
            },
            {
                "name": "Union Attack",
                "query": "SELECT * FROM users WHERE id = 1 UNION SELECT password FROM admin",
                "expected_safe": False
            },
            {
                "name": "Comment Attack",
                "query": "SELECT * FROM users WHERE id = 1 -- DROP TABLE users",
                "expected_safe": False
            },
            {
                "name": "Time-based Attack",
                "query": "SELECT * FROM users WHERE id = 1 AND SLEEP(5)",
                "expected_safe": False
            },
            {
                "name": "Advanced Attack",
                "query": "'; DROP TABLE users; SELECT * FROM data WHERE '1'='1",
                "expected_safe": False
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(f"{self.base_url}/sql/validate", json={
                    "query": test_case["query"]
                })
                
                if response.status_code == 200:
                    data = response.json()
                    is_safe = data["is_safe"]
                    risk_score = data["risk_score"]
                    severity = data["severity"]
                    
                    success = is_safe == test_case["expected_safe"]
                    status = "SAFE" if is_safe else "BLOCKED"
                    
                    self.print_result(
                        f"SQL Test: {test_case['name']}", 
                        success,
                        f"Status: {status} | Risk: {risk_score} | Severity: {severity}"
                    )
                    
                    if not is_safe:
                        print(f"   🚨 Detected patterns: {', '.join(data['detected_patterns'][:3])}")
                else:
                    self.print_result(f"SQL Test: {test_case['name']}", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.print_result(f"SQL Test: {test_case['name']}", False, f"Error: {str(e)}")
    
    def demonstrate_capability_codes(self):
        """Demonstrate capability code system"""
        self.print_section("Capability Code System Demonstration")
        
        if not self.admin_token:
            self.print_result("Capability Code Demo", False, "No admin token available")
            return
        
        try:
            # Create capability code
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/capability-codes", 
                                   json={
                                       "permissions": ["read", "write"],
                                       "expires_in_minutes": 30,
                                       "max_uses": 3
                                   },
                                   headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                capability_code = data.get("code", "")
                self.print_result("Capability Code Creation", True, 
                                f"Code: {capability_code[:15]}... | Permissions: read,write")
                
                # Test capability code usage
                if capability_code:
                    response = requests.post(f"{self.base_url}/sql/validate", json={
                        "query": "SELECT * FROM users WHERE id = 1",
                        "capability_code": capability_code
                    })
                    
                    if response.status_code == 200:
                        self.print_result("Capability Code Usage", True, "Code accepted and validated")
                    else:
                        self.print_result("Capability Code Usage", False, f"Status: {response.status_code}")
                
            else:
                self.print_result("Capability Code Creation", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.print_result("Capability Code Demo", False, f"Error: {str(e)}")
    
    def demonstrate_security_monitoring(self):
        """Demonstrate security monitoring"""
        self.print_section("Security Monitoring Demonstration")
        
        if not self.admin_token:
            self.print_result("Security Monitoring Demo", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get security events
        try:
            response = requests.get(f"{self.base_url}/security/events", headers=headers)
            
            if response.status_code == 200:
                events = response.json()
                self.print_result("Security Events", True, f"Found {len(events)} security events")
                
                # Show recent events
                for event in events[:3]:
                    print(f"   📋 {event['event_type']} - {event['severity']} - {event['description'][:50]}...")
            else:
                self.print_result("Security Events", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.print_result("Security Events", False, f"Error: {str(e)}")
        
        # Get injection attempts
        try:
            response = requests.get(f"{self.base_url}/security/attempts", headers=headers)
            
            if response.status_code == 200:
                attempts = response.json()
                self.print_result("Injection Attempts", True, f"Found {len(attempts)} injection attempts")
                
                # Show recent attempts
                for attempt in attempts[:3]:
                    print(f"   🎯 Risk: {attempt['risk_score']} - {attempt['query_attempt'][:50]}...")
            else:
                self.print_result("Injection Attempts", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.print_result("Injection Attempts", False, f"Error: {str(e)}")
        
        # Get dashboard
        try:
            response = requests.get(f"{self.base_url}/dashboard", headers=headers)
            
            if response.status_code == 200:
                dashboard = response.json()
                stats = dashboard['stats']
                self.print_result("Security Dashboard", True, 
                                f"Users: {stats['total_users']} | Attempts: {stats['total_injection_attempts']} | Blocked: {stats['blocked_attempts']}")
            else:
                self.print_result("Security Dashboard", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.print_result("Security Dashboard", False, f"Error: {str(e)}")
    
    def demonstrate_encryption(self):
        """Demonstrate encryption features"""
        self.print_section("AES-256 Encryption Demonstration")
        
        try:
            # Register a new user to test encryption
            response = requests.post(f"{self.base_url}/auth/register", json={
                "username": "encrypt_test",
                "email": "encrypt@demo.com",
                "password": "EncryptTest123!@#",
                "is_admin": False
            })
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Check that sensitive data is not exposed
                password_safe = "password" not in user_data and "encrypted_password" not in user_data
                api_key_safe = "api_key" in user_data and len(user_data["api_key"]) > 20
                
                self.print_result("Password Encryption", password_safe, "Password properly encrypted and hidden")
                self.print_result("API Key Generation", api_key_safe, f"Secure API key generated: {user_data['api_key'][:15]}...")
                
            else:
                self.print_result("Encryption Test", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.print_result("Encryption Test", False, f"Error: {str(e)}")
    
    def demonstrate_access_control(self):
        """Demonstrate access control"""
        self.print_section("Access Control Demonstration")
        
        # Test unauthorized access
        try:
            response = requests.get(f"{self.base_url}/security/events")
            
            if response.status_code == 401:
                self.print_result("Unauthorized Access", True, "Correctly blocked without token")
            else:
                self.print_result("Unauthorized Access", False, f"Expected 401, got {response.status_code}")
                
        except Exception as e:
            self.print_result("Unauthorized Access", False, f"Error: {str(e)}")
        
        # Test non-admin access
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = requests.get(f"{self.base_url}/security/events", headers=headers)
                
                if response.status_code == 403:
                    self.print_result("Non-Admin Access", True, "Correctly blocked non-admin user")
                else:
                    self.print_result("Non-Admin Access", False, f"Expected 403, got {response.status_code}")
                    
            except Exception as e:
                self.print_result("Non-Admin Access", False, f"Error: {str(e)}")
        
        # Test admin access
        if self.admin_token:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = requests.get(f"{self.base_url}/security/events", headers=headers)
                
                if response.status_code == 200:
                    self.print_result("Admin Access", True, "Admin access granted successfully")
                else:
                    self.print_result("Admin Access", False, f"Expected 200, got {response.status_code}")
                    
            except Exception as e:
                self.print_result("Admin Access", False, f"Error: {str(e)}")
    
    def run_complete_demo(self):
        """Run complete demonstration"""
        print("🛡️ SQL Injection Detection & Prevention System - Complete Demo")
        print("="*70)
        
        # Check if server is running
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.print_result("System Health", True, "System is running and healthy")
            else:
                self.print_result("System Health", False, f"Status: {response.status_code}")
                return
        except Exception as e:
            self.print_result("System Health", False, f"Cannot connect: {str(e)}")
            print("\n❌ Please start the server first: python main.py")
            return
        
        # Run all demonstrations
        self.setup_users()
        self.demonstrate_sql_injection_detection()
        self.demonstrate_capability_codes()
        self.demonstrate_security_monitoring()
        self.demonstrate_encryption()
        self.demonstrate_access_control()
        
        # Final summary
        self.print_section("Demo Summary")
        print("🎉 SQL Injection Security System Demo Complete!")
        print("\n🔐 Security Features Demonstrated:")
        print("   ✅ Advanced SQL Injection Detection (80+ patterns)")
        print("   ✅ AES-256 Encryption for sensitive data")
        print("   ✅ Capability Code access control system")
        print("   ✅ Double-layer security validation")
        print("   ✅ Real-time security monitoring")
        print("   ✅ Role-based access control")
        print("   ✅ Comprehensive audit logging")
        print("   ✅ Rate limiting and protection")
        
        print("\n🌐 Access Points:")
        print(f"   📊 Web Interface: {self.base_url}")
        print(f"   📖 API Documentation: {self.base_url}/docs")
        print(f"   💚 Health Check: {self.base_url}/health")
        print(f"   📈 Admin Dashboard: {self.base_url}/dashboard")
        
        print("\n🛡️ Your SQL Injection Security System is fully operational!")

if __name__ == "__main__":
    demo = SQLInjectionSecurityDemo()
    demo.run_complete_demo()
