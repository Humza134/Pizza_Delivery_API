from fastapi import FastAPI
from auth_routes import auth_router
from order_routes import order_router

app = FastAPI(
    title="Pizza Delivery API",
    description="An API For A Pizza Delivery Service",
    version="1.0.0",
)
app.include_router(auth_router)
app.include_router(order_router)