"""
Tenant Middleware for Multi-Tenancy
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.services.auth_service import AuthService
from app.utils.logger import logger
from typing import Callable


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and set tenant context"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip tenant extraction for auth endpoints
        if request.url.path.startswith("/api/v1/auth"):
            return await call_next(request)
        
        # Extract operator_id from JWT token
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            payload = AuthService.verify_token(token)
            
            if payload and payload.get("type") == "access":
                operator_id = payload.get("operator_id")
                if operator_id:
                    # Set tenant context in request state
                    request.state.operator_id = int(operator_id)
                    request.state.user_id = int(payload.get("sub"))
                    
                    # Set PostgreSQL session variable for RLS
                    # This will be handled in database dependency
                    logger.debug("Tenant context set", operator_id=operator_id)
        
        response = await call_next(request)
        return response
