from pydantic import BaseModel,Field,EmailStr,computed_field
from typing import List,Dict,Optional,Annotated
from fastapi import FastAPI,Path,HTTPException
from fastapi.responses import JSONResponse
import json
app=FastAPI()

#include pydantic model for the data creation and modifictaion

class User(BaseModel):
     id:Annotated[int,Field(...,description="id of the user",examples=[1,2])]
     name:Annotated[str,Field(...,description="enter the name of the  user",examples=["abhinav"])]
     email:Annotated[EmailStr,Field(...,description="enter the email of the user",examples=["abc@gmail.com"])]
     is_active:Annotated[bool,Field(description="user active status",default=False)]

def load_data():
    with open("database.json","r") as f:
        data=json.load(f)
        
    '''data.setdefault("users", [])
    data.setdefault("products", [])
    data.setdefault("orders", [])'''
    return data

def save_data(data):
     with open("database.json","w") as f:
          json.dump(data,f,indent = 4)
    
#print the active customer

@app.get("/active")
def active_users():
    ans=list()
    data=load_data()
    for li in data["users"]:
        if li["is_active"]==True:
            ans.append(li)
    
    return ans
#end point to get user by id

@app.get("/get_user/{uid}")
def get_details(uid:int = Path(...,description="numerical value of uid",example='1')):
    ans=dict()
    data=load_data()
    for li in data["users"]:
        if(li["id"]==uid):
            ans=li
            break
    if not ans:
         raise HTTPException(status_code=404,detail="USER NOT FOUND")
    else:
        return ans
    
#end point to get user order details
@app.get("/get_order/{uid}")
def get_orderdetail(uid : int = Path(...,description="enter intger value",example=123)):
        product_ids=list()
        data=load_data()
        if "users" not in data and "orders" not in data:
             raise HTTPException(status_code=404,detail="data not found")
        for li in data["orders"]:
            if li["user_id"] == uid:
                for l2 in li["items"]:
                        product_ids.append(l2["product_id"])
        ans=list()
        for li in data["products"]:
            if li["id"] in product_ids:
                ans.append(li["name"])
        return ans

#end point to add any user to database

@app.post("/create_user")
def insert_user(user :User):
     data=load_data()
     li=data["users"]
     for li1 in li:
          if li1["id"]==user.id:
               raise HTTPException(status_code=409,detail="user alerady exist")
     data["users"].append(user.model_dump())
     save_data(data)
     return JSONResponse(status_code=201,
                    content={"message":"new user entered succesfully"}
                    )
#end point to add product
class product(BaseModel):
     id:Annotated[int,Field(...,description="enter the unique product id",examples=[111])]
     name:Annotated[str,Field(...,description="enter the product name",examples=["mouse"])]
     price:Annotated[int,Field(...,description="enter the price",examples=[4200])]
     in_stock:bool

@app.post("/add_product")
def add_product(pr:product):
     data=load_data()
     for li in data["products"]:
          if pr.id==li["id"]:
               raise HTTPException(status_code=409,detail="data alerady exists")
     dt=pr.model_dump()
     data["products"].append(dt)
     save_data(data)
     return JSONResponse(
          status_code=201,
          content={"message":"new product inserted"}
     )

#api end point to place order

class items(BaseModel):
     product_id:Annotated[int,Field(...,description="enter the product_id",examples=[101,102])]
     quantity:Annotated[int,Field(...,gt=0,description="enter the quatity")]

class Order(BaseModel):
     id: Annotated[int,Field(default=0)]
     user_id:Annotated[int,Field(...,description="enter the unique id",examples=[1])]
     status:Annotated[bool,Field(default=None)]
     item:Annotated[Optional[List[items]],Field(Default=None)]
     
     def model_post_init(self, context):
        data=load_data()
        num1=data["orders"]
        index=num1[-1]["id"]
        self.id=index+1

     @computed_field
     @property
     def total_price(self)->int:
        data=load_data()
        li=set()
        for it in self.item:
             li.add(it.product_id)
        sum1=0
        dt=data["products"]
        for lt in dt:
            if lt["id"] in li:
                sum1+=lt["price"]
        return sum1
        

@app.post("/place_order")
def order_place(ord:Order):
     data=load_data()
     dt=ord.model_dump()
     data["orders"].append(dt)
     save_data(data)
     return JSONResponse(
          status_code=201,
          content={"message":"order placed successfully"}
     )
#updating the orders and user details

#updating user details
class update_u(BaseModel):
     id: Annotated[int,Field(...,description="enter the user id to be updated",examples=[1,2])]
     name:Annotated[Optional[str],Field(...,description="enter the user name to be updated")]
     email:Annotated[Optional[EmailStr],Field(...,description="enter the users email id to be updated",examples=["sks@gmail.com"])]
     is_active:Annotated[Optional[bool],Field(...,description="please enter the user is active or not",examples=["true","false"])]

@app.put("update_user_details/{uid}")
def update_user(user:update_u):
     data = load_data()
     for li in data["users"]:
          if user.id not in li.id:
               raise HTTPException(status_code=404
                                   ,detail="user details not found")
     