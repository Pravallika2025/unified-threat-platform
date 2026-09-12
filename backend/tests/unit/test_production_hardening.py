import pytest
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import Settings
from app.core.middleware.security_headers import SecurityHeadersMiddleware


@pytest.mark.asyncio
async def test_security_headers_middleware():
    middleware = SecurityHeadersMiddleware(app=None)

    async def mock_call_next(request: Request) -> Response:
        return Response("OK")

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/health",
        "headers": [],
    }
    request = Request(scope)
    response = await middleware.dispatch(request, mock_call_next)

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "accelerometer=()" in response.headers["Permissions-Policy"]


def test_production_settings_validation():
    # Should raise error when default insecure secret is used in production
    with pytest.raises(ValueError, match="SECRET_KEY must be set to a cryptographically secure"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="dev-secret-change-me",
            FIRST_ADMIN_PASSWORD="StrongProdPassword!987",
        )

    # Should raise error when default seed password is used in production
    with pytest.raises(ValueError, match="Default seed password must be changed"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a-very-secure-random-production-key-value-12345",
            FIRST_ADMIN_PASSWORD="Admin@12345",
        )

    # Should pass when valid production values are supplied
    prod_settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a-very-secure-random-production-key-value-12345",
        FIRST_ADMIN_PASSWORD="CustomSecurePassword!2026",
    )
    assert prod_settings.ENVIRONMENT == "production"
    assert prod_settings.DB_POOL_SIZE == 20
