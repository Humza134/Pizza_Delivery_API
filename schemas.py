from pydantic import BaseModel
from typing import Optional
from enums import PizzaSize, OrderStatus

class SignUpModel(BaseModel):
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'username': 'jhondoe',
                'email': 'johndoe@example.com',
                'password': 'password',
                'is_staff': False,
                'is_active': True,
            }
        }

class LogInModel(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'username': 'XXXXXXX',
                'password': 'XXXXXXXX',
            }
        }

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str

class TokenData(BaseModel):
    username: Optional[str] = None
    id: int | None = None

class OrderModel(BaseModel):
    quantity : int
    order_status : Optional[OrderStatus] = OrderStatus.Pending
    pizza_size : Optional[PizzaSize] = PizzaSize.Small 
    

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'pizza_size': 'Large',
                'quantity': 2,
            }
        }

class OrderStatusUpdate(BaseModel):
    order_status: Optional[OrderStatus] = OrderStatus.Pending

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'order_status': 'Pending',
            }
        }
