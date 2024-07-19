from sqlalchemy import INTEGER, Column, ForeignKey, String, Integer
from sqlalchemy.orm import declarative_base, relationship, validates, Mapped, mapped_column
import re

Base = declarative_base()


class Account(Base):
    __abstract__ = True

    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    full_name: Mapped[str]

    def verify_password(self, password):
        return self.password == password

    @validates("password")
    def validate_password(self, key, password):
        if len(password) < 8:
            raise ValueError("The password must contain at least 8 characters")
        return password

    @validates("email")
    def validate_email(self, key, email):
        regex = r'^[\w\.]+@([\w-]+\.)+[\w-]{2,7}$'
        match = re.match(regex, email)
        if not bool(match):
            raise ValueError("Email must contain '@' and '.' symbols")
        return email

    def to_dict(self):
        return {"id": self.id, "email": self.email, "full_name": self.full_name}


class User(Account):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    accounts: Mapped[list["BankAccounts"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class BankAccounts(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)

    account_id: Mapped[int] = mapped_column(unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    balance: Mapped[int] = mapped_column(default=0)
    user: Mapped["User"] = relationship(back_populates="accounts")


class Admin(Account):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(primary_key=True)


class Transactions(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    transaction_id: Mapped[str] = mapped_column(unique=True)
    account_id: Mapped[int] = mapped_column(ForeignKey('bank_accounts.account_id', ondelete='CASCADE'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    amount: Mapped[int]
    signature: Mapped[str]

    def to_dict(self):
        return {"id": self.id, "transaction_id": self.transaction_id, "account_id": self.account_id, "amount": self.amount, "signature": self.signature}
