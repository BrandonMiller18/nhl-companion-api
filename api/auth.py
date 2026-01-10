"""Bearer token authentication for API endpoints."""
import logging
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from nhl_db.config import get_env

logger = logging.getLogger(__name__)

# Security scheme for bearer token
security = HTTPBearer()


def get_api_token() -> str:
    """Get the API bearer token from environment variable."""
    try:
        return get_env("API_BEARER_TOKEN")
    except RuntimeError:
        logger.error("API_BEARER_TOKEN environment variable is not set")
        raise


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Verify the bearer token from the request.
    
    Args:
        credentials: HTTP authorization credentials from the request
        
    Returns:
        The token if valid
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    expected_token = get_api_token()
    
    if credentials.credentials != expected_token:
        logger.warning("Invalid bearer token attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return credentials.credentials

