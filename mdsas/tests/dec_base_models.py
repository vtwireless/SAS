from datetime import datetime

from sqlalchemy import Integer, String, \
    Column, DateTime, ForeignKey, Numeric, SmallInteger
from sqlalchemy.orm import relationship


class models:
    Base = None

    def __init__(self, base):
        self.Base = base

    class Customer(Base):
        __tablename__ = 'customers'
        id = Column(Integer(), primary_key=True)
        first_name = Column(String(100), nullable=False)
        last_name = Column(String(100), nullable=False)
        username = Column(String(50), nullable=False)
        email = Column(String(200), nullable=False)
        created_on = Column(DateTime(), default=datetime.now)
        updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
        orders = relationship("Order", backref='customer')

    class Item(Base):
        __tablename__ = 'items'
        id = Column(Integer(), primary_key=True)
        name = Column(String(200), nullable=False)
        cost_price = Column(Numeric(10, 2), nullable=False)
        selling_price = Column(Numeric(10, 2), nullable=False)

    #     orders = relationship("Order", backref='customer')

    class Order(Base):
        __tablename__ = 'orders'
        id = Column(Integer(), primary_key=True)
        customer_id = Column(Integer(), ForeignKey('customers.id'))
        date_placed = Column(DateTime(), default=datetime.now)
        line_items = relationship("OrderLine", secondary="order_lines", backref='order')

    class OrderLine(Base):
        __tablename__ = 'order_lines'
        id = Column(Integer(), primary_key=True)
        order_id = Column(Integer(), ForeignKey('orders.id'))
        item_id = Column(Integer(), ForeignKey('items.id'))
        quantity = Column(SmallInteger())
        item = relationship("Item")
