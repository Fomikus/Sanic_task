from sanic import Request, response
from sanic.exceptions import InvalidUsage
import jwt
from datetime import datetime, timedelta
from functools import wraps

from sqlalchemy import select

from .models.models import User, Admin
import os

SECRET_KEY = os.getenv("SANIC_JWT_SECRET_KEY", "gfdmhghif38yrf9ew0jkf32")


async def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


async def verify_jwt(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return response.json({"status": "error", "message": "Authorization header is missing"}, status=400)

    token = auth_header.split("Bearer ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        role = payload.get("role")
        if not user_id or not role:
            raise InvalidUsage("Invalid token")
        return int(user_id), role
    except jwt.exceptions.ExpiredSignatureError:
        raise InvalidUsage("Token has expired")
    except Exception as e:
        raise InvalidUsage(f"Token validation failed: {e}")


def authorize(role):
    @wraps(role)
    def wrapper(func):
        @wraps(func)
        async def inner(request: Request, *args, **kwargs):
            user_id, user_role = await verify_jwt(request)
            session = request.ctx.session
            async with session.begin():
                if user_role != role:
                    raise InvalidUsage(f"invalid role {user_role}")
                role_model = User if role == "user" else Admin

                stmt = select(role_model).where(role_model.id == user_id)
                res = await session.execute(stmt)
                result = res.scalar()
                if not result:
                    raise InvalidUsage(f"{role} not found")
                setattr(request.ctx, role, result)
            return await func(request, *args, **kwargs)
        return inner
    return wrapper
