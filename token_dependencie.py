#The goal of this file is to check whether the request is authorized or not [ verification of the protected route]

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from token_handler import decode_token, is_token_blacklisted


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(status_code=403, detail="Authenticate failed: Bad credentials scheme used")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Authorization expired or invalid! Please login again")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Authenticate failed : No credentials")

    def verify_jwt(self, jwtoken: str) -> bool:
        is_token_valid: bool = False
        if(is_token_blacklisted(jwtoken)):
            is_token_valid = False
        else:
            try:
                payload = decode_token(jwtoken)
            except Exception:
                payload = None
            if payload:
                is_token_valid = True
                
        return is_token_valid
