from fastapi import APIRouter,Depends,HTTPException, status
from auth_routes import get_current_user
from typing import Annotated
from model import Order
from schemas import OrderModel,OrderStatusUpdate
from database import get_db
import logging
from sqlalchemy.exc import SQLAlchemyError


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

order_router = APIRouter(prefix="/order", tags=["order"])

@order_router.get("/")
async def hello(current_user = Depends(get_current_user)):
    return {"message": "Hello World"}

# order place
@order_router.post("/order", status_code=status.HTTP_201_CREATED)
async def place_order(order: OrderModel, current_user = Depends(get_current_user), db = Depends(get_db)):
    try:
        user_id = current_user.id
        new_order = Order(
            pizza_size=order.pizza_size, 
            quantity=order.quantity, 
            user_id=user_id,
            order_status=order.order_status
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return new_order
    
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# user all orders
@order_router.get("/user/orders")
async def get_user_orders(current_user = Depends(get_current_user), db = Depends(get_db)):
    try:
        user_id = current_user.id
        user_orders = db.query(Order).filter(Order.user_id == user_id).all()
        return user_orders
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# user specific order by id
@order_router.get("/user/order/{order_id}")
async def get_user_order_by_id(order_id: int, current_user = Depends(get_current_user), db = Depends(get_db)):
    try:
        user_id = current_user.id
        user_order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).one()
        return user_order
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# update order
@order_router.patch("/order/update/{order_id}")
async def update_order(order_id: int, order: OrderModel, current_user = Depends(get_current_user), db = Depends(get_db)):
    try:
        user_id = current_user.id
        db_order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).one()
        db_order.quantity = order.quantity
        db_order.pizza_size = order.pizza_size
        db.commit()
        return {"Message": "Order updated successfully"}
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# delete order
@order_router.delete("/order/delete/{order_id}")
async def delete_order(order_id: int, current_user = Depends(get_current_user), db = Depends(get_db)):
    try:
        user_id = current_user.id
        db_order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).one()
        db.delete(db_order)
        db.commit()
        return {"Message": "Order deleted successfully"}
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# get all orders
@order_router.get("/all/orders")
async def get_all_orders(current_user = Depends(get_current_user), db = Depends(get_db)):
    try:
        if current_user.is_staff:
            all_orders = db.query(Order).all()
            return all_orders
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="only staff member get all orders")
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


 # get order by id
@order_router.get("/order/{order_id}")
async def get_order_by_id(order_id: int, current_user = Depends(get_current_user), db = Depends(get_db)):
    try:
        if current_user.is_staff:
            order = db.query(Order).filter(Order.id == order_id).one()
            return order
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="only staff member get order")
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    

# order status change 
@order_router.patch("/order/status/{order_id}")
async def update_order_status(order_id: int, order: OrderStatusUpdate, current_user = Depends(get_current_user), db = Depends(get_db)):
    try:
        if current_user.is_staff:
            db_order = db.query(Order).filter(Order.id == order_id).one()
            db_order.order_status = order.order_status
            db.commit()
            return {"Message": "Order status updated successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="only staff member can change order status")
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")