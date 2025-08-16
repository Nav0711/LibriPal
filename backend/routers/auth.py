from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import os
from models.database import get_database
from models.pydantic_models import User, UserCreate, APIResponse
from utils.auth import verify_clerk_token, get_current_user

router = APIRouter()
security = HTTPBearer()

@router.post("/verify", response_model=APIResponse)
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Clerk token and return user info"""
    try:
        user_data = await verify_clerk_token(credentials.credentials)
        return APIResponse(
            success=True,
            message="Token verified successfully",
            data={"user": user_data}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/register", response_model=APIResponse)
async def register_user(
    user_data: UserCreate,
    db = Depends(get_database)
):
    """Register a new user (called automatically on first login)"""
    try:
        # Check if user already exists
        existing_user = await db.fetchrow(
            "SELECT id FROM users WHERE clerk_id = $1",
            user_data.clerk_id
        )
        
        if existing_user:
            return APIResponse(
                success=False,
                message="User already exists"
            )
        
        # Create new user
        user_id = await db.fetchval("""
            INSERT INTO users (clerk_id, email, first_name, last_name)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """, user_data.clerk_id, user_data.email, user_data.first_name, user_data.last_name)
        
        return APIResponse(
            success=True,
            message="User registered successfully",
            data={"user_id": user_id}
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.delete("/account", response_model=APIResponse)
async def delete_account(current_user: dict = Depends(get_current_user)):
    """Delete user account and all associated data"""
    db = await get_database()
    try:
        # Delete user and cascade to related tables
        await db.execute("DELETE FROM users WHERE id = $1", current_user["id"])
        
        return APIResponse(
            success=True,
            message="Account deleted successfully"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Account deletion failed: {str(e)}"
        )