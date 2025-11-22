from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .logging_citizens import log_api_call
from routers.certificate_router import logger
from db.db import get_session
from routers.auth import get_current_user

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования действий API."""    
    async def dispatch(self, request: Request, call_next):
        if any(path in request.url.path for path in ['/docs', '/redoc', '/openapi.json', '/favicon.ico']):
            return await call_next(request)
        
        session = next(get_session())
        request.state.session = session
        
        user = None
        try:
            authorization = request.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer "):
                token = authorization.replace("Bearer ", "")
                user = get_current_user(token, session)
        except Exception as e:
            logger.debug(f"User not authenticated: {e}")
            user = None
        
        request.state.user = user
        
        logger.info(f"State after setup: {request.state.__dict__}")
        
        try:
            response = await call_next(request)
            
            if hasattr(request.state, "user") and hasattr(request.state, "session"):
                logger.info('!!!!!!!!!!!!!!!!!! Logging event !!!!!!!!!!!!!!!!!!')
                user = request.state.user
                session = request.state.session
                path_parts = [p for p in request.url.path.split('/') if p]
                action = request.method.lower()
                object_type = "api_call"
                object_id = None
                
                if len(path_parts) >= 2:
                    object_type = path_parts[-2] if len(path_parts) > 2 else path_parts[-1]
                    object_id = path_parts[-1] if path_parts[-1].isdigit() else None
                log_api_call(
                    session=session,
                    user=user,
                    request=request,
                    action=action,
                    object_type=object_type,
                    object_id=object_id
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in logging middleware: {e}")
            return await call_next(request)
        finally:
            if hasattr(request.state, "session") and request.state.session:
                request.state.session.close()