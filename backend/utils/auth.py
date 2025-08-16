import httpx
import os
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.database import get_database

security = HTTPBearer()

async def verify_clerk_token(token: str) -> dict:
    """Verify Clerk JWT token"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.clerk.com/v1/sessions/verify",
                headers={
                    "Authorization": f"Bearer {os.getenv('CLERK_SECRET_KEY')}",
                    "Content-Type": "application/json"
                },
                json={"token": token}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=401, detail="Invalid token")
                
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token verification failed")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token"""
    token = credentials.credentials
    
    # For development, you can use a simple mock
    if os.getenv("ENVIRONMENT") == "development":
        # Mock user for development
        mock_user = {
            "user_id": "user_test123",
            "email": "test@libripal.com",
            "first_name": "Test",
            "last_name": "User"
        }
        clerk_id = mock_user["user_id"]
    else:
        # Verify token with Clerk
        token_data = await verify_clerk_token(token)
        clerk_id = token_data["user_id"]
        mock_user = token_data
    
    # Get or create user in database
    db = await get_database()
    try:
        user = await db.fetchrow("SELECT * FROM users WHERE clerk_id = $1", clerk_id)
        
        if not user:
            # Create user if doesn't exist
            user_id = await db.fetchval("""
                INSERT INTO users (clerk_id, email, first_name, last_name) 
                VALUES ($1, $2, $3, $4) RETURNING id
            """, 
            clerk_id,
            mock_user.get("email", ""),
            mock_user.get("first_name", ""),
            mock_user.get("last_name", "")
            )
            
            user = await db.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        
        return dict(user)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def require_admin(current_user: dict = Depends(get_current_user)):
    """Require admin role (placeholder for future implementation)"""
    # TODO: Implement admin role checking
    # For now, assume all authenticated users can perform admin actions
    return current_user

def get_user_permissions(user: dict) -> list:
    """Get user permissions (placeholder for future implementation)"""
    # Basic permissions for all users
    permissions = ["read_books", "borrow_books", "view_profile"]
    
    # TODO: Add role-based permissions
    # if user.get("role") == "admin":
    #     permissions.extend(["manage_books", "view_all_users", "manage_settings"])
    
    return permissions