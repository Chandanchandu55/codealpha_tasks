from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from database import User, CapabilityCode, SQLInjectionAttempt, AccessLog, SecurityEvent
from security import security_manager
from schemas import UserCreate, UserUpdate, CapabilityCodeCreate, SecurityEventCreate

class CRUDOperations:
    def create_user(self, db: Session, user: UserCreate) -> User:
        """Create a new user with encrypted credentials"""
        # Hash password
        hashed_password = security_manager.hash_password(user.password)
        encrypted_password = security_manager.encrypt_data(hashed_password)
        
        # Generate API key
        api_key = security_manager.generate_api_key()
        encrypted_api_key = security_manager.encrypt_data(api_key)
        
        db_user = User(
            username=user.username,
            email=user.email,
            encrypted_password=encrypted_password,
            encrypted_api_key=encrypted_api_key,
            is_admin=user.is_admin
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Decrypt API key for return
        db_user.api_key = api_key
        return db_user
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        user = self.get_user_by_username(db, username)
        if not user:
            return None
        
        try:
            # Decrypt and verify password
            decrypted_password = security_manager.decrypt_data(user.encrypted_password)
            hashed_input = security_manager.hash_password(password)
            
            if decrypted_password == hashed_input:
                return user
        except Exception:
            pass
        
        return None
    
    def update_user(self, db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user information"""
        db_user = self.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(db_user, field):
                setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    def create_capability_code(self, db: Session, user_id: int, capability_data: CapabilityCodeCreate) -> CapabilityCode:
        """Create a new capability code"""
        code, code_hash = security_manager.generate_capability_code(
            user_id, 
            capability_data.permissions, 
            capability_data.expires_in_minutes
        )
        
        # Encrypt the code
        encrypted_code = security_manager.encrypt_data(code)
        
        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(minutes=capability_data.expires_in_minutes)
        
        db_capability = CapabilityCode(
            code_hash=code_hash,
            encrypted_code=encrypted_code,
            user_id=user_id,
            permissions=json.dumps(capability_data.permissions),
            expires_at=expires_at,
            max_uses=capability_data.max_uses
        )
        
        db.add(db_capability)
        db.commit()
        db.refresh(db_capability)
        
        return db_capability
    
    def verify_capability_code(self, db: Session, code: str) -> Optional[Dict[str, Any]]:
        """Verify and return capability code data"""
        # Generate hash to find in database
        code_hash = security_manager.hash_password(code)
        
        db_capability = db.query(CapabilityCode).filter(
            and_(
                CapabilityCode.code_hash == code_hash,
                CapabilityCode.is_active == True
            )
        ).first()
        
        if not db_capability:
            return None
        
        try:
            # Verify and decrypt the code
            code_data = security_manager.verify_capability_code(
                code, 
                code_hash, 
                db_capability.encrypted_code
            )
            
            if not code_data:
                return None
            
            # Check expiration
            if datetime.utcnow() > db_capability.expires_at:
                return None
            
            # Check usage limits
            if db_capability.use_count >= db_capability.max_uses:
                return None
            
            # Update usage
            db_capability.use_count += 1
            if db_capability.used_at is None:
                db_capability.used_at = datetime.utcnow()
            
            # Deactivate if max uses reached
            if db_capability.use_count >= db_capability.max_uses:
                db_capability.is_active = False
            
            db.commit()
            
            return code_data
            
        except Exception:
            return None
    
    def create_sql_injection_attempt(self, db: Session, user_id: Optional[int], ip_address: str, 
                                   query_attempt: str, detection_result: Dict[str, Any]) -> SQLInjectionAttempt:
        """Log SQL injection attempt"""
        db_attempt = SQLInjectionAttempt(
            user_id=user_id,
            ip_address=ip_address,
            query_attempt=query_attempt,
            detected_patterns=json.dumps(detection_result["detected_patterns"]),
            risk_score=detection_result["risk_score"],
            is_blocked=detection_result["risk_score"] >= 50,
            blocked_reason=f"Risk score: {detection_result['risk_score']}, Severity: {detection_result['severity']}"
        )
        
        db.add(db_attempt)
        db.commit()
        db.refresh(db_attempt)
        
        return db_attempt
    
    def create_access_log(self, db: Session, user_id: Optional[int], ip_address: str, 
                        endpoint: str, method: str, status_code: int, 
                        response_time_ms: Optional[int], user_agent: Optional[str],
                        capability_code_used: Optional[str] = None) -> AccessLog:
        """Create access log entry"""
        db_log = AccessLog(
            user_id=user_id,
            ip_address=ip_address,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            user_agent=user_agent,
            capability_code_used=capability_code_used
        )
        
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        
        return db_log
    
    def create_security_event(self, db: Session, event: SecurityEventCreate, user_id: Optional[int] = None) -> SecurityEvent:
        """Create security event"""
        db_event = SecurityEvent(
            event_type=event.event_type,
            severity=event.severity,
            description=event.description,
            ip_address=event.ip_address,
            user_id=user_id,
            details=json.dumps(event.details) if event.details else None
        )
        
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        return db_event
    
    def get_users(self, db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[User]:
        """Get users with pagination"""
        query = db.query(User)
        if active_only:
            query = query.filter(User.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    def get_capability_codes(self, db: Session, user_id: Optional[int] = None, 
                           active_only: bool = True) -> List[CapabilityCode]:
        """Get capability codes"""
        query = db.query(CapabilityCode)
        
        if user_id:
            query = query.filter(CapabilityCode.user_id == user_id)
        
        if active_only:
            query = query.filter(
                and_(
                    CapabilityCode.is_active == True,
                    CapabilityCode.expires_at > datetime.utcnow()
                )
            )
        
        return query.all()
    
    def get_sql_injection_attempts(self, db: Session, skip: int = 0, limit: int = 100, 
                                   blocked_only: bool = False, risk_score_min: int = 0) -> List[SQLInjectionAttempt]:
        """Get SQL injection attempts"""
        query = db.query(SQLInjectionAttempt)
        
        if blocked_only:
            query = query.filter(SQLInjectionAttempt.is_blocked == True)
        
        if risk_score_min > 0:
            query = query.filter(SQLInjectionAttempt.risk_score >= risk_score_min)
        
        return query.order_by(desc(SQLInjectionAttempt.created_at)).offset(skip).limit(limit).all()
    
    def get_security_events(self, db: Session, event_type: Optional[str] = None, 
                           severity: Optional[str] = None, unresolved_only: bool = False,
                           skip: int = 0, limit: int = 100) -> List[SecurityEvent]:
        """Get security events"""
        query = db.query(SecurityEvent)
        
        if event_type:
            query = query.filter(SecurityEvent.event_type == event_type)
        
        if severity:
            query = query.filter(SecurityEvent.severity == severity)
        
        if unresolved_only:
            query = query.filter(SecurityEvent.is_resolved == False)
        
        return query.order_by(desc(SecurityEvent.created_at)).offset(skip).limit(limit).all()
    
    def get_access_logs(self, db: Session, user_id: Optional[int] = None, 
                       endpoint: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[AccessLog]:
        """Get access logs"""
        query = db.query(AccessLog)
        
        if user_id:
            query = query.filter(AccessLog.user_id == user_id)
        
        if endpoint:
            query = query.filter(AccessLog.endpoint.contains(endpoint))
        
        return query.order_by(desc(AccessLog.created_at)).offset(skip).limit(limit).all()
    
    def get_system_stats(self, db: Session) -> Dict[str, Any]:
        """Get system statistics"""
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        
        total_capability_codes = db.query(CapabilityCode).count()
        active_capability_codes = db.query(CapabilityCode).filter(
            and_(
                CapabilityCode.is_active == True,
                CapabilityCode.expires_at > datetime.utcnow()
            )
        ).count()
        
        total_injection_attempts = db.query(SQLInjectionAttempt).count()
        blocked_attempts = db.query(SQLInjectionAttempt).filter(SQLInjectionAttempt.is_blocked == True).count()
        
        # Recent events
        recent_events = db.query(SecurityEvent).filter(
            SecurityEvent.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).order_by(desc(SecurityEvent.created_at)).limit(10).all()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_capability_codes": total_capability_codes,
            "active_capability_codes": active_capability_codes,
            "total_injection_attempts": total_injection_attempts,
            "blocked_attempts": blocked_attempts,
            "recent_events": recent_events
        }
    
    def resolve_security_event(self, db: Session, event_id: int) -> bool:
        """Resolve a security event"""
        db_event = db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()
        if not db_event:
            return False
        
        db_event.is_resolved = True
        db_event.resolved_at = datetime.utcnow()
        db.commit()
        
        return True

# Create a singleton instance
crud = CRUDOperations()
