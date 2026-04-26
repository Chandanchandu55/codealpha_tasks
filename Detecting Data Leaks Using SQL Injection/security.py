import re
import hashlib
import secrets
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from config import settings, encryption_cipher, CAPABILITY_CODE_LENGTH, CAPABILITY_EXPIRE_MINUTES

class SecurityManager:
    def __init__(self):
        self.encryption_cipher = encryption_cipher
        self.capability_secret = settings.capability_secret
        
        # SQL Injection patterns
        self.sql_injection_patterns = [
            # Basic SQL injection patterns
            r"('|(\\')|(;)|(\\|)|(\*)|(7c)|(7C))",
            r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|EXECUTE)\b",
            r"\b(OR|AND)\s+\d+\s*=\s*\d+",
            r"\b(OR|AND)\s+['\"]\w+['\"]\s*=\s*['\"]\w+['\"]",
            r"(--|#|\/\*|\*\/)",
            r"\b(WAITFOR|DELAY|BENCHMARK)\b",
            r"\b(INFORMATION_SCHEMA|SYS|MASTER|MSDB)\b",
            r"\b(HEX|CHAR|ASCII|ORD|CONCAT)\s*\(",
            r"\b(USER|VERSION|DATABASE)\s*\(\s*\)",
            r"\b(CAST|CONVERT)\s*\(",
            r"\b(LOAD_FILE|INTO\s+OUTFILE|INTO\s+DUMPFILE)\b",
            r"\b(SLEEP|BENCHMARK)\s*\(",
            r"\b(XOR|NOT|IN|LIKE|REGEXP)\b",
            r"\b(0x[0-9a-fA-F]+)\b",
            r"\b(UNION\s+ALL|UNION\s+SELECT)\b",
            r"\b(GROUP\s+BY|ORDER\s+BY|HAVING)\b",
            r"\b(LIMIT|OFFSET)\s+\d+",
            r"\b(CASE|WHEN|THEN|ELSE|END)\b",
            r"\b(IF|IFNULL|NULLIF|COALESCE)\b",
            r"\b(EXISTS|NOT\s+EXISTS)\b",
            r"\b(SUBSTRING|SUBSTR|MID)\s*\(",
            r"\b(LENGTH|CHAR_LENGTH)\s*\(",
            r"\b(CONCAT_WS|GROUP_CONCAT)\s*\(",
            r"\b(LEFT|RIGHT|LTRIM|RTRIM|TRIM)\s*\(",
            r"\b(UPPER|LOWER|UCASE|LCASE)\s*\(",
            r"\b(REPLACE|INSERT|STR_REPLACE)\s*\(",
            r"\b(FIND_IN_SET|FIELD)\s*\(",
            r"\b(ELT|MAKE_SET)\s*\(",
            r"\b(EXPORT_SET)\s*\(",
            r"\b(QUOTE)\s*\(",
            r"\b(VALUES)\s*\(",
            r"\b(TABLE|TEMPORARY)\b",
            r"\b(INDEX|KEY)\b",
            r"\b(PRIMARY|FOREIGN)\s+KEY\b",
            r"\b(REFERENCES|CONSTRAINT)\b",
            r"\b(TRIGGER|PROCEDURE|FUNCTION)\b",
            r"\b(CURSOR|DECLARE)\b",
            r"\b(COMMIT|ROLLBACK|TRANSACTION)\b",
            r"\b(LOCK|UNLOCK)\s+TABLES\b",
            r"\b(SHOW|DESCRIBE|EXPLAIN)\b",
            r"\b(HELP)\b",
            r"\b(ANALYZE|OPTIMIZE|CHECK|REPAIR)\b",
            r"\b(FLUSH|RESET)\b",
            r"\b(KILL)\s+\d+",
            r"\b(SET)\s+@\w+",
            r"\b(PREPARE|EXECUTE|DEALLOCATE)\b",
            r"\b(HANDLER)\s+\w+\s+(OPEN|CLOSE|READ)\b",
            r"\b(LOAD\s+DATA|REPLACE\s+INTO)\b",
            r"\b(START\s+TRANSACTION|BEGIN)\b",
            r"\b(SAVEPOINT|ROLLBACK\s+TO\s+SAVEPOINT)\b",
            r"\b(RELEASE\s+SAVEPOINT)\b",
            r"\b(LOCK\s+TABLES|UNLOCK\s+TABLES)\b",
            r"\b(XA\s+START|XA\s+END|XA\s+PREPARE|XA\s+COMMIT|XA\s+ROLLBACK)\b",
            r"\b(PURGE\s+BINARY\s+LOGS)\b",
            r"\b(CHANGE\s+MASTER\s+TO)\b",
            r"\b(SLAVE\s+START|SLAVE\s+STOP)\b",
            r"\b(INSTALL\s+PLUGIN|UNINSTALL\s+PLUGIN)\b",
            r"\b(CREATE\s+USER|DROP\s+USER|RENAME\s+USER|GRANT|REVOKE)\b",
            r"\b(ALTER\s+USER|SET\s+PASSWORD)\b",
            r"\b(CREATE\s+ROLE|DROP\s+ROLE)\b",
            r"\b(CREATE\s+VIEW|DROP\s+VIEW|ALTER\s+VIEW)\b",
            r"\b(CREATE\s+TRIGGER|DROP\s+TRIGGER|ALTER\s+TRIGGER)\b",
            r"\b(CREATE\s+PROCEDURE|DROP\s+PROCEDURE|ALTER\s+PROCEDURE)\b",
            r"\b(CREATE\s+FUNCTION|DROP\s+FUNCTION|ALTER\s+FUNCTION)\b",
            r"\b(CREATE\s+EVENT|DROP\s+EVENT|ALTER\s+EVENT)\b",
            r"\b(CREATE\s+DATABASE|DROP\s+DATABASE|ALTER\s+DATABASE)\b",
            r"\b(CREATE\s+TABLESPACE|DROP\s+TABLESPACE|ALTER\s+TABLESPACE)\b",
            r"\b(CREATE\s+SERVER|DROP\s+SERVER|ALTER\s+SERVER)\b",
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.sql_injection_patterns]
    
    def encrypt_data(self, data: str) -> bytes:
        """Encrypt sensitive data using AES-256"""
        if isinstance(data, str):
            data = data.encode()
        return self.encryption_cipher.encrypt(data)
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data using AES-256"""
        decrypted = self.encryption_cipher.decrypt(encrypted_data)
        return decrypted.decode()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_capability_code(self, user_id: int, permissions: List[str], expires_in_minutes: int = CAPABILITY_EXPIRE_MINUTES) -> Tuple[str, str]:
        """Generate a capability code for secure SQL operations"""
        # Generate random code
        code = secrets.token_urlsafe(CAPABILITY_CODE_LENGTH)
        
        # Create code data
        code_data = {
            "user_id": user_id,
            "permissions": permissions,
            "expires_at": (datetime.utcnow() + timedelta(minutes=expires_in_minutes)).isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "nonce": secrets.token_hex(16)
        }
        
        # Encrypt the code data
        code_json = json.dumps(code_data)
        encrypted_code = self.encrypt_data(code_json)
        
        # Generate hash for verification
        code_hash = hashlib.sha256(f"{code}{self.capability_secret}".encode()).hexdigest()
        
        return code, code_hash
    
    def verify_capability_code(self, code: str, code_hash: str, encrypted_code: bytes) -> Optional[Dict[str, Any]]:
        """Verify and decrypt capability code"""
        try:
            # Verify hash
            expected_hash = hashlib.sha256(f"{code}{self.capability_secret}".encode()).hexdigest()
            if expected_hash != code_hash:
                return None
            
            # Decrypt and parse code data
            decrypted_data = self.decrypt_data(encrypted_code)
            code_data = json.loads(decrypted_data)
            
            # Check expiration
            expires_at = datetime.fromisoformat(code_data["expires_at"])
            if datetime.utcnow() > expires_at:
                return None
            
            return code_data
            
        except Exception:
            return None
    
    def detect_sql_injection(self, query: str) -> Dict[str, Any]:
        """Detect SQL injection patterns in query"""
        detected_patterns = []
        risk_score = 0
        is_suspicious = False
        
        # Check for basic SQL keywords first
        sql_keywords = re.findall(r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|EXEC|EXECUTE)\b', query, re.IGNORECASE)
        
        # If no SQL keywords, it's probably safe
        if not sql_keywords:
            return {
                "is_suspicious": False,
                "risk_score": 0,
                "severity": "info",
                "detected_patterns": [],
                "sql_keywords": [],
                "suspicious_chars": []
            }
        
        # Check each pattern for suspicious combinations
        for pattern in self.compiled_patterns:
            matches = pattern.findall(query)
            if matches:
                # Handle both string and tuple matches
                actual_matches = []
                for match in matches:
                    if isinstance(match, tuple):
                        # Take the first non-empty element from tuple
                        match = next((m for m in match if m and m.strip()), '')
                    if match and match.strip():
                        actual_matches.append(match)
                
                detected_patterns.extend(actual_matches)
                if actual_matches:
                    risk_score += len(actual_matches) * 5
                    is_suspicious = True
        
        # Additional checks for high-risk patterns
        high_risk_patterns = [
            r'\b(OR|AND)\s+\d+\s*=\s*\d+',
            r'\b(OR|AND)\s+[\'\"][^\'\"]*[\'\"]\s*=\s*[\'\"][^\'\"]*[\'\"]',
            r'--.*$',
            r'/\*.*?\*/',
            r'\b(UNION\s+ALL|UNION\s+SELECT)\b',
            r'\b(DROP|DELETE|TRUNCATE)\b',
            r'\b(INSERT\s+INTO)\b',
            r'\b(UPDATE\s+\w+\s+SET)\b',
            r'\b(EXEC|EXECUTE)\b',
            r'\b(WAITFOR|DELAY|SLEEP)\b'
        ]
        
        for pattern in high_risk_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                risk_score += 25
                is_suspicious = True
                detected_patterns.append(pattern)
        
        # Check for suspicious characters in dangerous contexts
        dangerous_chars = re.findall(r'[\'";\\]', query)
        if dangerous_chars and sql_keywords:
            risk_score += len(dangerous_chars) * 2
            is_suspicious = True
        
        # Check for encoded content
        if re.search(r'%[0-9a-fA-F]{2}', query):
            risk_score += 15
            is_suspicious = True
            detected_patterns.append("URL encoding detected")
        
        # Multiple SQL keywords increase risk
        if len(sql_keywords) > 1:
            risk_score += len(sql_keywords) * 10
            is_suspicious = True
        
        # Cap risk score at 100
        risk_score = min(risk_score, 100)
        
        # Determine severity
        if risk_score >= 80:
            severity = "critical"
        elif risk_score >= 60:
            severity = "high"
        elif risk_score >= 40:
            severity = "medium"
        elif risk_score >= 20:
            severity = "low"
        else:
            severity = "info"
        
        return {
            "is_suspicious": is_suspicious,
            "risk_score": risk_score,
            "severity": severity,
            "detected_patterns": [str(pattern) if not isinstance(pattern, tuple) else str(pattern[0]) if pattern and pattern[0] else str(pattern) for pattern in detected_patterns],
            "sql_keywords": sql_keywords,
            "suspicious_chars": dangerous_chars
        }
    
    def sanitize_query(self, query: str) -> str:
        """Sanitize query to prevent SQL injection"""
        # Remove or escape dangerous characters
        sanitized = re.sub(r'[\'";\\]', '', query)
        
        # Remove SQL keywords (for safety)
        sanitized = re.sub(r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|EXEC|EXECUTE)\b', '', sanitized, flags=re.IGNORECASE)
        
        # Remove comments
        sanitized = re.sub(r'--.*$', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'/\*.*?\*/', '', sanitized, flags=re.DOTALL)
        
        return sanitized.strip()
    
    def validate_input(self, input_data: str, max_length: int = 1000) -> Dict[str, Any]:
        """Validate input for security"""
        issues = []
        
        # Check length
        if len(input_data) > max_length:
            issues.append(f"Input too long: {len(input_data)} > {max_length}")
        
        # Check for null bytes
        if '\x00' in input_data:
            issues.append("Null bytes detected")
        
        # Check for control characters
        if re.search(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', input_data):
            issues.append("Control characters detected")
        
        # Check for path traversal
        if '../' in input_data or '..\\' in input_data:
            issues.append("Path traversal attempt detected")
        
        # Check for XSS patterns
        xss_patterns = [r'<script', r'onload=', r'onerror=', r'javascript:', r'vbscript:']
        for pattern in xss_patterns:
            if re.search(pattern, input_data, re.IGNORECASE):
                issues.append(f"XSS pattern detected: {pattern}")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }
    
    def generate_api_key(self) -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)
    
    def double_layer_validation(self, query: str, user_permissions: List[str]) -> Dict[str, Any]:
        """Double-layer security validation"""
        layer1_result = self.detect_sql_injection(query)
        layer2_result = self.validate_input(query)
        
        # Check permissions
        required_permissions = []
        if "SELECT" in query.upper():
            required_permissions.append("read")
        if any(keyword in query.upper() for keyword in ["INSERT", "UPDATE", "DELETE"]):
            required_permissions.append("write")
        if any(keyword in query.upper() for keyword in ["DROP", "CREATE", "ALTER"]):
            required_permissions.append("admin")
        
        permission_valid = all(perm in user_permissions for perm in required_permissions)
        
        # Combined risk assessment
        combined_risk = layer1_result["risk_score"]
        if not layer2_result["is_valid"]:
            combined_risk += 30
        if not permission_valid:
            combined_risk += 40
        
        combined_risk = min(combined_risk, 100)
        
        return {
            "layer1": layer1_result,
            "layer2": layer2_result,
            "permission_check": {
                "valid": permission_valid,
                "required": required_permissions,
                "user_has": user_permissions
            },
            "combined_risk": combined_risk,
            "is_safe": combined_risk < 50 and layer1_result["severity"] in ["info", "low"]
        }

# Global security manager instance
security_manager = SecurityManager()
