from datetime import datetime
from abc import ABC,abstractmethod
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import uuid
from __future__ import annotations
from httpx import AsyncClient()


class CommonUser():
    def __init__(self,user_id:str,username:str,email:str,password:str,admin_id:str,admin_code:str):
        self._user_id = user_id
        self._username = username
        self._email = email
        self._password = password

class Admin(CommonUser):
    def __init__(self,user_id:str,username:str,email:str,password:str,admin_id:str,admin_code:str):
        self._admin_id = admin_id
        self._admin_code = admin_code

class BrokerUser(CommonUser):
    def __init__(self,username:str,email:str,password:str):
        self._user_id = str(uuid.uuid4())
        self._username = username
        self._email = email
        self._password = password
        self._wallet_id = str(uuid.uuid4())
        self._created_at = datetime.now()
        self._updated_at = datetime.now()


class CommonAsset():
    def __init__(self,asset_name:str,asset_id:str,price:float,is_shortable:bool,created_at:datetime,updated_at:datetime):
        self._asset_name = asset_name
        self._asset_id = str(uuid.uuid4())+asset_name
        self._price = price
        self._is_shortable = is_shortable
        self._created_at = created_at
        self._updated_at = updated_at
    
    def get_price_by_asset_name(self) -> float:
        return self._price

    def get_asset_id(self) -> str:
        return self._asset_id

    def is_shortable(self) -> bool:
        return self._is_shortable
    
    def get_last_update(self) -> datetime:
        return self._updated_at


class GetterInterface(ABC):
    @abstractmethod
    async def get_current_price(ticker:str) -> float:
        pass

class GetterBinance(GetterInterface):
    async def get_current_price(ticker:str) -> float:
        async with AsyncClient() as client:
            response = await client.get(f"https://api.binance.com/api/v3/ticker/price?symbol={ticker}")
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get price, probably wrong ticker")
            return response.json()["price"]
        


    class AssetTransaction(ABC):
        @abstractmethod
        def execute(self, wallet: PersonalWallet, asset_name: str, amount: int) -> None:
            pass

    class BuyTransaction(AssetTransaction):
        def execute(self, wallet: PersonalWallet, asset_name: str, amount: int) -> None:
            if wallet._balance < CommonAsset.get_price_by_asset_name(asset_name) * amount:
                raise HTTPException(status_code=400, detail="Insufficient balance")
            wallet._balance = wallet._balance - wallet.get_price_by_asset_name(asset_name) * amount
            if asset_name in wallet._assets:
                wallet._assets.get(asset_name) += amount
            else:
                wallet._assets.get(asset_name) = amount

    class SellTransaction(AssetTransaction):
        def execute(self, wallet: PersonalWallet, asset_name: str, amount: int) -> None:
            if asset_name not in wallet._assets:
                raise HTTPException(status_code=400, detail="Asset not found")
            wallet._balance = wallet._balance + CommonAsset.get_price_by_asset_name(asset_name) * amount
            wallet._assets.get(asset_name) -= amount

    class ShortTransaction(AssetTransaction):
        def execute(self, wallet: PersonalWallet, asset_name: str, amount: int) -> None:
            if wallet._balance * 0.5 < CommonAsset.get_price_by_asset_name(asset_name) * amount:
                raise HTTPException(status_code=400, detail="Insufficient balance")
            wallet._balance = wallet._balance - wallet.get_price_by_asset_name(asset_name) * amount
            if asset_name in wallet._assets:
                raise HTTPException(status_code=400, detail="Sell your assets first")
            else:
                wallet._assets.get(asset_name) -= amount
                wallet._shorted_assets.get(asset_name) = amount


    class CloseShortTransaction(AssetTransaction):
        def execute(self, wallet: PersonalWallet, asset_name: str, amount: int) -> None:
            if asset_name not in wallet._shorted_assets:
                raise HTTPException(status_code=400, detail="No short position found")
            wallet._balance = wallet._balance + CommonAsset.get_price_by_asset_name(asset_name) * amount
            wallet._assets.get(asset_name) = wallet._assets.get(asset_name) + amount
            wallet._shorted_assets.pop(asset_name)
            
    


class Wallet():
    def __init__(self,wallet_id:str):
        self._wallet_id = wallet_id

class PersonalWallet(Wallet):
    def __init__(self,wallet_id:str,user_id:str,balance:float,assets:dict,shorted_assets:dict,created_at:datetime,updated_at:datetime):
        self._wallet_id = wallet_id
        self._user_id = user_id
        self._balance = balance
        self._assets = assets
        self._shorted_assets = shorted_assets
        self._created_at = created_at
        self._updated_at = updated_at

        
    def create_wallet(self,user_id:str):
        self._wallet_id = str(uuid.uuid4())
        self._user_id = user_id
        self._balance = 0
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        

    def update_wallet(self,user_id:str,amount:int,wallet_id:str):
        self._user_id = user_id
        self._wallet_id = wallet_id
        self._updated_at = datetime.now()
        self._balance = self._balance + amount

    def get_balance(self, user_id:str,wallet_id:str):
        return self.balance
    
    def get_size_of_all_assets(self,user_id:str,wallet_id:str):
        return sum(self._assets.values()*get_price_by_asset_name(asset_name) for asset_name in self._assets)
    
    def work_with_assets(self, user_id: str, amount: int, asset_name: str, action: str, wallet_id: str):
        transactions = {
            "buy": BuyTransaction(),
            "sell": SellTransaction(), 
            "short": ShortTransaction(),
            "close_short": CloseShortTransaction()
        }
        
        if action not in transactions:
            raise HTTPException(status_code=400, detail="Invalid transaction type")
            
        transactions[action].execute(self, asset_name, amount)

    
    def get_all_assets(self,user_id:str,wallet_id:str) -> dict():
        return self._assets



    def get_minimal_margin(self,user_id:str,wallet_id:str):
        if self._balance < self._balance*0.25 and len(self._shorted_assets) > 0 and get_size_of_all_assets(self._user_id) > self._balance*0.75:
            return JSONResponse(status_code=400, content={"message": "Margin call"})


