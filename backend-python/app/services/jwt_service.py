import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from uuid import UUID
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class JWTService:
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.expiration_hours = settings.JWT_EXPIRATION_HOURS
    
    def generate_token(self, user_id: UUID, email: str) -> str:
        """Generate a JWT token for a user"""
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=self.expiration_hours)
        
        payload = {
            "iss": "student-risk-prediction",
            "sub": str(user_id),
            "email": email,
            "iat": now,
            "exp": expires_at
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """Validate a JWT token and return claims"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer="student-risk-prediction"
            )
            
            return {
                "user_id": UUID(payload["sub"]),
                "email": payload["email"]
            }
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return None
    
    def refresh_token(self, old_token: str) -> Optional[str]:
        """Refresh a JWT token"""
        claims = self.validate_token(old_token)
        if claims:
            return self.generate_token(claims["user_id"], claims["email"])
        return None


# Singleton instance
jwt_service = JWTService()
