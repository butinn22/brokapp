from datetime import datetime
from fastapi import HTTPException # for custom exceptions 
from fastapi.responses import JSONResponse # for custom exceptions json response
from pydantic import BaseModel,EmailStr, validator,constr


class ABCUser(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class AdminPydantic(ABCUser):
    admin_id:str
    admin_code: str


class BrokerUserPydantic(ABCUser):
    wallet_id:str
    created_at:datetime
    updated_at:datetime

class UserIn(BaseModel):
    username:str
    password:constr(min_length=8)


   

class AssetPydantic(BaseModel):
    asset_name:str
    asset_id: str
    price:float
    is_shortable: bool
    created_at:datetime
    updated_at:datetime




class WalletPydantic(BaseModel):
    wallet_id:str
    


class PersonalWalletPydantic(BaseModel,WalletPydantic):
    user_id:str
    balance:float
    created_at:datetime
    updated_at:datetime
    assets:dict
    shorted_assets:dict



class Resultofwallet(BaseModel):
    wallet_id:str
    user_id:str
    balance:float
    assets:dict
    shorted_assets:dict

    @validator('balance')
    def validate_balance(cls, v):
        if v < 0:
            raise ValueError('Balance cannot be negative')
        return v
