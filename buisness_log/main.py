from datetime import datetime
from fastapi import FastAPI,HTTPException,JSONResponse
from fastapi.params import Depends
from pydantic import EmailStr
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from redis.sentinel import Sentinel
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy
from buisness_log.auth import create_jwt_token
import tables.py
from buisness_log.pydantic_models import AdminPydantic,BrokerUserPydantic,AssetPydantic,PersonalWalletPydantic,Resultofwallet, UserIn
import models
import buisness_log.pydantic_models as pydantic_models
from buisness_log.auth import get_user_from_token
from __future__ import annotations
from contextlib import asynccontextmanager
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    app.state.redis = Redis(
        host="localhost",
        port=6379,
        db=0,
        password='qweasd123',
        decode_responses=True
    )
    yield
    await app.state.redis.close()

app = FastAPI(lifespan=lifespan)


@app.post("/login")
async def login(user_in: UserIn):
   async with tables.eng.begin() as conn:
        try:
            result = await conn.execute(select(tables.UserDB).where(tables.UserDB.username == user_in.username))
            user = result.first()
            if user and user.password == user_in.password:
                new_jwt={"access_token": create_jwt_token({"sub": user.user_id}), "token_type": "bearer"}
                return new_jwt
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Error logging in: {e}")

    



@app.post("/new_user", response_model=BrokerUserPydantic)
async def create_broker_user(username:str,email:EmailStr,password:str):
    new_user = models.BrokerUser(username,email,password)
    pduser = pydantic_models.BrokerUserPydantic(**new_user.__dict__)
    new_wallet = models.PersonalWallet(new_user._wallet_id,new_user._user_id,0,{},{},datetime.now(),datetime.now())
    newbduser =tables.UserDB(**new_user.__dict__)
    app.state.redis.set(new_user._user_id,pduser.model_dump_json(), ex=60*5)
    async with tables.eng.begin() as conn:
        try: 
            await conn.execute(tables.UserDB.insert().values(newbduser))
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating user: {e}")
        try: 
            await conn.execute(tables.UserWalletDB.insert().values(new_wallet.__dict__))
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating user wallet: {e}")
    return pduser

    
@app.get("/get_user_by_id")
async def get_user_by_id(user_id:str):
    user_json = app.state.redis.get(user_id)
    if user_json != None:
        return pydantic_models.BrokerUserPydantic.model_validate_json(user_json)
    else:
        async with tables.eng.begin() as conn:
            result = await conn.execute(select(tables.UserDB).where(tables.UserDB.user_id == user_id))
            user = result.first()
            if user:
                app.state.redis.set(user_id,pydantic_models.BrokerUserPydantic(**user.__dict__).model_dump_json(), ex=60*5)
                return pydantic_models.BrokerUserPydantic(**user.__dict__)
            else:
                raise HTTPException(status_code=404, detail="User not found")


@app.get("/get_user_wallet_by_user_id")
async def get_user_wallet_by_user_id(user_id:str = Depends(get_user_from_token)):
    async with tables.eng.begin() as conn:
        walresult = await conn.execute(select(tables.UserWalletDB).where(tables.UserWalletDB.user_id == user_id))
        user_wallet = walresult.first()
        if user_wallet:
            return pydantic_models.PersonalWalletPydantic(**user_wallet.__dict__)
        else:
            raise HTTPException(status_code=404, detail="User wallet not found, Did you call /login first?")



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.53",
        port=8080,
        reload=True
    )

