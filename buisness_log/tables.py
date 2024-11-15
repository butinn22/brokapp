from sqlalchemy import MetaData,Table,Column,Integer,String,DateTime,Boolean,Float,JSON,ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from asyncio import run
from baseenter import data_for_enter

Base = declarative_base()

eng=create_async_engine(data_for_enter)  #Notice, serializable isolation level is used and = SERIALIZABLE ; File "baseenter.py" is added to .gitignore for security reasons!


async def create_tables():
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

run(create_tables())



class UserDB(Base):
    __tablename__ = "users"
    user_id = Column(String,primary_key=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    wallet_id = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class AdminDB(UserDB):
    __tablename__ = "admins"
    admin_id = Column(Integer,primary_key=True)
    admin_code = Column(String)


class UserWalletDB(Base):
    __tablename__ = "user_wallets"
    wallet_id = Column(Integer,primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    balance = Column(Float)
    assets = Column(JSON)
    shorted_assets = Column(JSON)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class AssetDB(Base):
    __tablename__ = "assets"
    asset_id = Column(Integer,primary_key=True)
    asset_name = Column(String)
    price = Column(Float)
    is_shortable = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


