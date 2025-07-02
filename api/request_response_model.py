from pydantic import BaseModel,Field
from typing import List,Dict

class UserRequest(BaseModel):
    email_address:str
    password:str

class ResetPasswordRequest(BaseModel):
    token:str
    new_password:str

class DateRequest(BaseModel):
    start_date:str
    end_date:str

class SearchRequest(BaseModel):
    start_date:str
    end_date:str
    file_description:str
    location:str

class EmailRequest(BaseModel):
    email_address:str

class RegistrationRequest(BaseModel):
    name:str
    email:str
    password:str
    confirmPassword:str
    locations:List[str]


class CheckoutRequest(BaseModel):
    amount: int
    currency: str = "usd"
    email_address: str
    product: str

class ValidProductsResponse(BaseModel):
    valid_products: List[str]
    max_file_size:int



