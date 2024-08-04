from database import Base
from sqlalchemy import Column, Integer, String, Boolean,Text,Enum as SQLAlchemyEnum
from sqlalchemy_utils.types import ChoiceType
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from enums import OrderStatus, PizzaSize

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True)
    email = Column(String(80), unique=True)
    password = Column(Text,nullable=True)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    orders = relationship('Order', back_populates='user')

    def __repr__(self):
        return f"<User {self.username}"
    
class Order(Base):

    # ORDER_STATUS = (
    #     ('PENDING', 'pending'),
    #     ('IN_TRANSIT', 'in_transit'),
    #     ('DELIVERED', 'delivered'),
    # )

    # PIZZA_SIZES = (
    #     ('SMALL', 'small'),
    #     ('MEDIUM', 'medium'),
    #     ('LARGE', 'large'),
    #     ('EXTRA_LARGE', 'extra_large'),
    # )

    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=True)
    order_status = Column(SQLAlchemyEnum(OrderStatus), default=OrderStatus.Pending)  # Use the Enum with default
    pizza_size = Column(SQLAlchemyEnum(PizzaSize), default=PizzaSize.Small)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='orders')

    def __repr__(self):
        return f"<Order {self.id}"
