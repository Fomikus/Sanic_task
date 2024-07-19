from sanic import Blueprint, response
from sanic.request import Request
from sqlalchemy.exc import IntegrityError
from ..models.models import User, Admin
from sqlalchemy import select, delete
from ..auth import authorize, create_access_token

admins_bp = Blueprint("admins", url_prefix="/admins")


@admins_bp.route("/auth", methods=['POST'])
async def auth_admin(request: Request):
    session = request.ctx.session

    if not request.json:
        return response.json({"status": "error", "message": "Request body is missing"}, status=400)

    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return response.json({"status": "error", "message": f"Email and password are required"}, status=400)

    async with session.begin():
        stmt = select(Admin).where(Admin.email == email)
        result: Admin = (await session.execute(stmt)).scalar()

        if result is None or not result.verify_password(password):
            return response.json({"status": "error", "message": "Invalid credentials"}, status=400)

    access_token = await create_access_token({"sub": str(result.id), "role": "admin"})

    return response.json({"access_token": access_token})


@admins_bp.route("/me", methods=["GET"])
@authorize("admin")
async def get_me(request: Request):
    return response.json(request.ctx.admin.to_dict())


@admins_bp.route("/users", methods=["DELETE"])
@authorize("admin")
async def delete_user(request: Request):
    session = request.ctx.session

    if not request.json:
        return response.json({"status": "error", "message": "Request body is missing"}, status=400)

    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return response.json({"status": "error", "message": "Field user_id is required"}, status=400)

    if not isinstance(user_id, int):
        return response.json({"status": "error", "message": "Field user_id must be an integer"}, status=400)

    async with session.begin():
        stmt = delete(User).where(User.id == user_id)
        result = await session.execute(stmt)

        if result.rowcount == 0:
            return response.json({"status": "error", "message": f"User with id == {user_id} doesn't exists"}, status=400)

        return response.json({"result": True})


@admins_bp.route("/users", methods=["POST"])
@authorize("admin")
async def admin_create_user(request: Request):
    session = request.ctx.session

    if not request.json:
        return response.json({"status": "error", "message": "Request body is missing"}, status=400)

    data = request.json

    required_fields = ['email', 'full_name', 'password']

    for field in required_fields:
        if field not in data:
            return response.json({"status": "error", "message": f"Field {field} is required"}, status=400)

    async with session.begin():
        try:
            new_user = User(email=data.get('email'), password=data.get('password'), full_name=data.get('full_name'))
            session.add(new_user)
            await session.commit()
        except IntegrityError:
            return response.json({"status": "error", "message": f"User with email {data.get('email')} already exists"}, status=400)
        except ValueError as ex:
            return response.json({"status": "error", "message": ex}, status=400)

    return response.json(new_user.to_dict())


@admins_bp.route("/users/<user_id:int>", methods=["GET"], name='admin_get_user')
@admins_bp.route("/users/", methods=["GET"], name='admin_get_all_users')
@authorize("admin")
async def admin_get_user(request: Request, user_id=None):
    session = request.ctx.session

    async with session.begin():
        if user_id is not None:
            stmt = select(User).where(User.id == int(user_id))
            result = (await session.execute(stmt)).scalar()

            if not result:
                return response.json({"status": "error", "message": f"User with id {user_id} does not exists"}, status=400)

            return response.json(result.to_dict())

        result = (await session.execute(select(User))).scalars().all()
        answer = []
        for user in result:
            answer.append(user.to_dict())
        return response.json(answer)


@admins_bp.route("/users/", methods=["PATCH"])
@authorize("admin")
async def admin_full_update_user(request: Request):
    session = request.ctx.session

    if not request.json:
        return response.json({"status": "error", "message": "Request body is missing"}, status=400)

    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return response.json({"status": "error", "message": "Field user_id is required"}, status=400)

    data.pop("user_id")

    if not isinstance(user_id, int):
        return response.json({"status": "error", "message": "Field user_id must be an integer"}, status=400)

    async with session.begin():
        stmt = select(User).where(User.id == int(user_id))
        result = (await session.execute(stmt)).scalar()

        if not result:
            return response.json({"status": "error", "message": f"User with id {user_id} does not exists"}, status=400)

        valid_fields = {k: v for k, v in data.items() if hasattr(User, k)}

        for field, value in valid_fields.items():
            try:
                setattr(result, field, value)
            except ValueError as ex:
                return response.json({"status": "error", "message": ex}, status=400)

    return response.json({"result": True})
