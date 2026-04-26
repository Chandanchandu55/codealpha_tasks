from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import time
import logging
import json

from database import get_db, create_tables, User
from crud import crud
from security import security_manager
from schemas import (
    UserCreate, UserUpdate, UserResponse, UserLogin, Token,
    CapabilityCodeCreate, CapabilityCodeResponse,
    SQLQueryRequest, SQLQueryResponse,
    SecurityEventCreate, SecurityEventResponse,
    AccessLogResponse, SQLInjectionAttemptResponse,
    SystemStats, SecurityDashboard
)
from config import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SQL Injection Detection & Prevention System",
    description="A cloud system that secures user data against SQL injection attacks with AES-256 encryption and double-layer security",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("SQL Injection Security System started successfully")

class RateLimiter:
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, ip: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        now = time.time()
        if ip not in self.requests:
            self.requests[ip] = []
        
        # Remove old requests
        self.requests[ip] = [req_time for req_time in self.requests[ip] if now - req_time < window_seconds]
        
        # Check if under limit
        if len(self.requests[ip]) < max_requests:
            self.requests[ip].append(now)
            return True
        
        return False

rate_limiter = RateLimiter()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # For simplicity, we'll use the token as an API key
        # In production, you'd decode JWT tokens
        
        # Find user by API key (simplified approach)
        users = crud.get_users(db)
        for user in users:
            try:
                decrypted_api_key = security_manager.decrypt_data(user.encrypted_api_key)
                if decrypted_api_key == token:
                    return user
            except:
                continue
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    # Check for forwarded IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check for real IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to client host
    return request.client.host

def log_access(request: Request, response, user_id: int = None, capability_code: str = None):
    """Log access for monitoring"""
    try:
        start_time = getattr(request.state, "start_time", time.time())
        response_time = int((time.time() - start_time) * 1000)
        
        crud.create_access_log(
            db=request.state.db,
            user_id=user_id,
            ip_address=get_client_ip(request),
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            response_time_ms=response_time,
            user_agent=request.headers.get("User-Agent"),
            capability_code_used=capability_code
        )
    except Exception as e:
        logger.error(f"Access logging error: {str(e)}")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time and rate limiting"""
    # Rate limiting
    client_ip = get_client_ip(request)
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    # Add start time for response time calculation
    request.state.start_time = time.time()
    
    # Store database session for logging
    db = next(get_db())
    request.state.db = db
    response = await call_next(request)
    
    # Log access
    log_access(request, response)
    
    # Close database session
    db.close()
    
    response.headers["X-Process-Time"] = str(time.time() - request.state.start_time)
    return response

# Root endpoint with web interface
@app.get("/", response_class=HTMLResponse)
async def root():
    """Main web interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SQL Injection Detection & Prevention System</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            h1 {
                text-align: center;
                margin-bottom: 30px;
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature {
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .feature h3 {
                color: #ffd700;
                margin-bottom: 10px;
            }
            .api-docs {
                text-align: center;
                margin: 30px 0;
            }
            .api-docs a {
                background: #4CAF50;
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 25px;
                font-weight: bold;
                display: inline-block;
                transition: all 0.3s ease;
            }
            .api-docs a:hover {
                background: #45a049;
                transform: translateY(-2px);
            }
            .status {
                text-align: center;
                margin: 20px 0;
                padding: 15px;
                background: rgba(76, 175, 80, 0.2);
                border-radius: 10px;
                border: 1px solid rgba(76, 175, 80, 0.3);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ SQL Injection Detection & Prevention System</h1>
            
            <div class="status">
                <h3>✅ System Status: Online and Secure</h3>
                <p>Advanced SQL injection detection with AES-256 encryption</p>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🔐 AES-256 Encryption</h3>
                    <p>Military-grade encryption for user credentials and sensitive data</p>
                </div>
                <div class="feature">
                    <h3>🛡️ Double-Layer Security</h3>
                    <p>Advanced pattern detection with capability code verification</p>
                </div>
                <div class="feature">
                    <h3>🔍 Real-time Detection</h3>
                    <p>Instant SQL injection attempt detection and blocking</p>
                </div>
                <div class="feature">
                    <h3>📊 Security Dashboard</h3>
                    <p>Comprehensive monitoring and analytics</p>
                </div>
                <div class="feature">
                    <h3>🌐 Cloud Ready</h3>
                    <p>Deploy anywhere with minimal system requirements</p>
                </div>
                <div class="feature">
                    <h3>🔑 Capability Codes</h3>
                    <p>Secure token-based access control system</p>
                </div>
            </div>
            
            <div class="api-docs">
                <h3>🚀 Explore the API</h3>
                <a href="/docs" target="_blank">📖 Interactive API Documentation</a>
                <p style="margin-top: 15px;">Test all endpoints with our interactive Swagger UI</p>
            </div>
            
            <div style="text-align: center; margin-top: 30px; opacity: 0.8;">
                <p>Built with FastAPI • SQLAlchemy • AES-256 Encryption</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    db_user = crud.create_user(db, user)
    
    # Log security event
    crud.create_security_event(
        db=db,
        event=SecurityEventCreate(
            event_type="user_registration",
            severity="info",
            description=f"New user registered: {user.username}",
            ip_address="registration_endpoint"
        )
    )
    
    return db_user

@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return token"""
    user = crud.authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        crud.create_security_event(
            db=db,
            event=SecurityEventCreate(
                event_type="failed_login",
                severity="medium",
                description=f"Failed login attempt for: {user_credentials.username}",
                ip_address="login_endpoint"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Return API key as token (simplified)
    try:
        api_key = security_manager.decrypt_data(user.encrypted_api_key)
        return Token(
            access_token=api_key,
            token_type="bearer",
            expires_in=1800,  # 30 minutes
            user=UserResponse.from_orm(user)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating token"
        )

# Capability code endpoints
@app.post("/capability-codes", response_model=CapabilityCodeResponse)
async def create_capability_code(
    capability_data: CapabilityCodeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new capability code"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    db_capability = crud.create_capability_code(db, current_user.id, capability_data)
    
    # Decrypt code for response
    try:
        code = security_manager.decrypt_data(db_capability.encrypted_code)
        db_capability.code = code
    except:
        pass
    
    return db_capability

# SQL injection detection endpoints
@app.post("/sql/validate", response_model=SQLQueryResponse)
async def validate_sql_query(
    query_request: SQLQueryRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Validate SQL query for injection attempts"""
    client_ip = get_client_ip(request)
    
    # Double-layer security validation
    user_permissions = ["read"]  # Default permissions for validation
    
    if query_request.capability_code:
        # Verify capability code
        capability_data = crud.verify_capability_code(db, query_request.capability_code)
        if capability_data:
            user_permissions = capability_data.get("permissions", ["read"])
    
    security_result = security_manager.double_layer_validation(query_request.query, user_permissions)
    
    # Log the attempt
    crud.create_sql_injection_attempt(
        db=db,
        user_id=None,  # Anonymous for validation endpoint
        ip_address=client_ip,
        query_attempt=query_request.query,
        detection_result=security_result["layer1"]
    )
    
    # Create security event for high-risk attempts
    if security_result["combined_risk"] >= 70:
        crud.create_security_event(
            db=db,
            event=SecurityEventCreate(
                event_type="sql_injection",
                severity="high" if security_result["combined_risk"] >= 80 else "medium",
                description=f"High-risk SQL injection attempt detected",
                ip_address=client_ip,
                details={
                    "query": query_request.query,
                    "risk_score": security_result["combined_risk"],
                    "detected_patterns": security_result["layer1"]["detected_patterns"]
                }
            )
        )
    
    return SQLQueryResponse(
        is_safe=security_result["is_safe"],
        risk_score=security_result["combined_risk"],
        severity=security_result["layer1"]["severity"],
        detected_patterns=security_result["layer1"]["detected_patterns"],
        sanitized_query=security_manager.sanitize_query(query_request.query) if not security_result["is_safe"] else None,
        blocked_reason=f"Risk score: {security_result['combined_risk']}" if not security_result["is_safe"] else None
    )

@app.get("/security/attempts", response_model=list[SQLInjectionAttemptResponse])
async def get_injection_attempts(
    skip: int = 0,
    limit: int = 100,
    blocked_only: bool = False,
    risk_score_min: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get SQL injection attempts (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    attempts = crud.get_sql_injection_attempts(db, skip, limit, blocked_only, risk_score_min)
    return attempts

@app.get("/security/events", response_model=list[SecurityEventResponse])
async def get_security_events(
    skip: int = 0,
    limit: int = 100,
    event_type: str = None,
    severity: str = None,
    unresolved_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get security events (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    events = crud.get_security_events(db, event_type, severity, unresolved_only, skip, limit)
    return events

@app.post("/security/events/{event_id}/resolve")
async def resolve_security_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve a security event (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    success = crud.resolve_security_event(db, event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return {"message": "Event resolved successfully"}

@app.get("/dashboard", response_model=SecurityDashboard)
async def get_security_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get security dashboard (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get system stats
    stats = crud.get_system_stats(db)
    
    # Get recent attempts
    recent_attempts = crud.get_sql_injection_attempts(db, skip=0, limit=10)
    
    # Get recent logs
    recent_logs = crud.get_access_logs(db, skip=0, limit=10)
    
    # Get high-risk events
    high_risk_events = crud.get_security_events(
        db, 
        severity="high", 
        unresolved_only=True, 
        skip=0, 
        limit=10
    )
    
    return SecurityDashboard(
        stats=SystemStats(**stats),
        recent_attempts=recent_attempts,
        recent_logs=recent_logs,
        high_risk_events=high_risk_events
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "security_level": "maximum"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
