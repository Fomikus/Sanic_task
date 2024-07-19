import hashlib

from sanic import Blueprint, response
from sanic.request import Request
from sqlalchemy.exc import IntegrityError
from ..models.models import User, Transactions, BankAccounts
from sqlalchemy import select
import os

SANIC_JWT_SECRET_KEY = os.getenv("SANIC_JWT_SECRET_KEY", "gfdmhghif38yrf9ew0jkf32")

transactions_bp = Blueprint("webhook", url_prefix="/webhook")


@transactions_bp.route("/", methods=['POST'])
async def handle_transactions(request: Request):
    session = request.ctx.session

    if not request.json:
        return response.json({"status": "error", "message": "Request body is missing"}, status=400)

    data = request.json

    transaction_id = data.get("transaction_id")
    amount = data.get("amount")
    account_id = data.get("account_id")
    user_id = data.get("user_id")
    signature = data.get("signature")

    if not all([transaction_id, amount, account_id, user_id, signature]):
        return response.json({"status": "error", "message": "Missing required data in request"}, status=400)
    expected_signature = hashlib.sha256(f"{account_id}{amount}{transaction_id}{user_id}{SANIC_JWT_SECRET_KEY}".encode()).hexdigest()

    if expected_signature != signature:
        return response.json({"status": "error", "message": "Invalid signature"}, status=400)

    async with session.begin():
        stmt_existing_transaction = select(Transactions).where(Transactions.transaction_id == transaction_id)
        existing_transaction = (await session.execute(stmt_existing_transaction)).scalar()
        if existing_transaction:
            return response.json({"status": "error", "message": "Transaction already processed"}, status=400)

        stmt_bank_account = select(BankAccounts).where(BankAccounts.account_id == account_id)
        account = (await session.execute(stmt_bank_account)).scalar()

        if not account:
            stmt_user = select(User).where(User.id == user_id)
            user = (await session.execute(stmt_user)).scalar()

            if not user:
                return response.json({"status": "error", "message": "User not found"}, status=400)

            account = BankAccounts(user_id=user_id, account_id=account_id, balance=0)
            session.add(account)

        transaction = Transactions(transaction_id=transaction_id, account_id=account_id, user_id=user_id, amount=amount, signature=signature)
        session.add(transaction)

        if account.user_id != user_id:
            await session.commit()
            return response.json({"status": "error", "message": "User ID mismatch"}, status=400)

        try:
            account.balance += amount
            await session.commit()
        except IntegrityError:
            return response.json({"status": "error", "message": "Transaction already processed"}, status=400)

    return response.json({"status": "success", "message": "Transaction successfully processed"})

