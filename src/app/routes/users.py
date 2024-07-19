from sanic import Blueprint, response
from sanic.request import Request
from ..models.models import User, Transactions
from sqlalchemy import select
from ..auth import authorize, create_access_token

users_bp = Blueprint("users", url_prefix="/users")


@users_bp.route("/auth", methods=['POST'])
async def auth_user(request: Request):
    session = request.ctx.session

    if not request.json:
        return response.json({"status": "error", "message": "Request body is missing"}, status=400)

    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return response.json({"status": "error", "message": "Email and password required"}, status=400)

    async with session.begin():
        stmt = select(User).where(User.email == email)
        result: User = (await session.execute(stmt)).scalar()

        if result is None or not result.verify_password(password):
            return response.json({"status": "error", "message": "Invalid credentials"}, status=400)

    access_token = await create_access_token({"sub": str(result.id), "role": "user"})

    return response.json({"access_token": access_token})


@users_bp.route("/me", methods=["GET"])
@authorize("user")
async def get_me(request: Request):
    return response.json(request.ctx.user.to_dict())


@users_bp.route("/accounts", methods=["GET"])
@authorize("user")
async def get_user(request: Request):
    session = request.ctx.session

    await session.refresh(request.ctx.user, ["accounts"])

    result = []
    for account in request.ctx.user.accounts:
        result.append({"account_id": account.account_id, "balance": account.balance})
    return response.json(result)


@users_bp.route("/transactions", methods=["GET"])
@authorize("user")
async def get_transactions(request: Request):
    session = request.ctx.session
    method_result = []

    async with session.begin():
        stmt = select(Transactions).where(Transactions.user_id == request.ctx.user.id)
        res = await session.execute(stmt)
        result: list[Transactions] = res.scalars().all()

        for i in result:
            method_result.append(i.to_dict())

    return response.json(method_result)
