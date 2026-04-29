import jwt
from jwt import PyJWKClient
from fastapi import HTTPException
from core.config import settings

def decode_supabase_token(token: str) -> dict:
    """
    Decode and validate a Supabase Bearer token.
    """
    try:
        # Decode without verification first to inspect headers
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg")
        
        if not settings.SUPABASE_URL:
            raise HTTPException(status_code=500, detail="SUPABASE_URL is not configured.")

        # Resolve signing key from Supabase JWKS
        jwks_url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # Expected values
        expected_issuer = f"{settings.SUPABASE_URL}/auth/v1"
        expected_audience = settings.SUPABASE_JWT_AUDIENCE

        # Verify and decode the token
        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=[alg] if alg else ["RS256"],
            issuer=expected_issuer,
            audience=expected_audience,
            options={"verify_aud": True}
        )
        
        return decoded

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidIssuerError:
        raise HTTPException(status_code=401, detail="Invalid token issuer")
    except jwt.InvalidAudienceError:
        raise HTTPException(status_code=401, detail="Invalid token audience")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")
