from fastapi import APIRouter, HTTPException, status, Depends
from app.models.user import UserRegister, UserLogin, Token, UserResponse
from app.config.supabase import supabase
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    """Register a new user"""
    try:
        # Create user with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {
                "data": {
                    "full_name": user.full_name
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )
        
        # Check if session exists (email confirmation may be required)
        if not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration successful, but email confirmation is required. Please check your email."
            )
        
        # Return user data and tokens
        return Token(
            access_token=auth_response.session.access_token,
            token_type="bearer",
            refresh_token=auth_response.session.refresh_token,
            user=UserResponse(
                id=auth_response.user.id,
                email=auth_response.user.email,
                full_name=user.full_name,
                created_at=auth_response.user.created_at.isoformat() if auth_response.user.created_at else None
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """Login user"""
    try:
        # Sign in with Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Get user metadata
        full_name = auth_response.user.user_metadata.get("full_name")
        
        return Token(
            access_token=auth_response.session.access_token,
            token_type="bearer",
            refresh_token=auth_response.session.refresh_token,
            user=UserResponse(
                id=auth_response.user.id,
                email=auth_response.user.email,
                full_name=full_name,
                created_at=auth_response.user.created_at.isoformat() if auth_response.user.created_at else None
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user - JWT tokens are stateless, so logout is handled client-side"""
    # Since we're using JWT tokens which are stateless, 
    # the actual logout happens on the client side by removing the token
    # This endpoint just validates that the user is authenticated
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    try:
        # Get user from Supabase
        user_response = supabase.auth.get_user()
        
        if not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        full_name = user_response.user.user_metadata.get("full_name")
        
        return UserResponse(
            id=user_response.user.id,
            email=user_response.user.email,
            full_name=full_name,
            created_at=user_response.user.created_at.isoformat() if user_response.user.created_at else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
