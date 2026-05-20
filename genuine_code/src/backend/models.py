from sqlalchemy import Column, Integer, String, Enum, Numeric, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class AccountType(str, enum.Enum):
    checking = "checking"
    savings = "savings"
    gold = "gold"
    investment = "investment"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    password_hash = Column(String)
    tckn = Column(String(11), unique=True)

    accounts = relationship("Account", back_populates="owner")
    profile = relationship("UserProfile", back_populates="user", uselist=False)


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    account_type = Column(Enum(AccountType))
    balance = Column(Numeric(15, 2))
    iban = Column(String(26), unique=True)

    owner = relationship("User", back_populates="accounts")
    outgoing_transactions = relationship("Transaction", foreign_keys="Transaction.from_account_id", back_populates="sender")
    incoming_transactions = relationship("Transaction", foreign_keys="Transaction.to_account_id", back_populates="receiver")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(Integer, ForeignKey("accounts.id"))
    to_account_id = Column(Integer, ForeignKey("accounts.id"))
    amount = Column(Numeric(15, 2))
    description = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    sender = relationship("Account", foreign_keys=[from_account_id], back_populates="outgoing_transactions")
    receiver = relationship("Account", foreign_keys=[to_account_id], back_populates="incoming_transactions")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    interaction_count = Column(Integer, default=0)
    financial_literacy_score = Column(Integer, default=50)
    preferred_tone = Column(String, default="formal")
    last_topic = Column(String)

    user = relationship("User", back_populates="profile")

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_tckn = Column(String)
    bot_message = Column(Text)
    category = Column(String)
    value = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
