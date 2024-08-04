from enum import Enum

class OrderStatus(Enum):
    Pending = "Pending"
    In_transit = "In_transit"
    Delivered = "Delivered"

class PizzaSize(Enum):
    Small = "Small"
    Medium = "Medium"
    Large = "Large"
    Extra_large = "Extra_large"
