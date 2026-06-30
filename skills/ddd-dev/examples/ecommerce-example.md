# E-Commerce DDD Example

## Simplified Implementation

This example shows a simplified DDD approach suitable for small-medium projects.

### Project Structure
```
src/
├── domain/
│   ├── models.py
│   ├── repositories.py
│   └── exceptions.py
├── services/
│   └── order_service.py
├── persistence/
│   └── order_repository.py
└── api/
    └── order_routes.py
```

### Domain Layer

```python
# domain/models.py
from dataclasses import dataclass
from typing import List
from decimal import Decimal
from enum import Enum

class OrderStatus(Enum):
    DRAFT = "draft"
    PLACED = "placed"
    CANCELLED = "cancelled"

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
    
    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def __mul__(self, quantity: int) -> 'Money':
        return Money(self.amount * Decimal(quantity), self.currency)

@dataclass(frozen=True)
class OrderItem:
    product_id: str
    product_name: str
    quantity: int
    unit_price: Money
    
    @property
    def subtotal(self) -> Money:
        return self.unit_price * self.quantity

class Order:  # Aggregate Root
    def __init__(self, order_id: str, customer_id: str):
        self.order_id = order_id
        self.customer_id = customer_id
        self.status = OrderStatus.DRAFT
        self._items: List[OrderItem] = []
    
    @property
    def items(self) -> List[OrderItem]:
        return self._items.copy()
    
    @property
    def total(self) -> Money:
        if not self._items:
            return Money(Decimal('0'), 'USD')
        return sum(item.subtotal for item in self._items, 
                   Money(Decimal('0'), 'USD'))
    
    def add_item(self, product_id: str, product_name: str, 
                 quantity: int, unit_price: Money) -> None:
        if self.status != OrderStatus.DRAFT:
            raise DomainException("Can only add items to draft orders")
        
        if quantity <= 0:
            raise DomainException("Quantity must be positive")
        
        if quantity > 100:
            raise DomainException("Cannot order more than 100 of a single item")
        
        # Check if product already exists
        existing = next((item for item in self._items 
                        if item.product_id == product_id), None)
        if existing:
            self._items.remove(existing)
            new_quantity = existing.quantity + quantity
            if new_quantity > 100:
                raise DomainException("Cannot order more than 100 of a single item")
            self._items.append(OrderItem(product_id, product_name, 
                                        new_quantity, unit_price))
        else:
            self._items.append(OrderItem(product_id, product_name, 
                                        quantity, unit_price))
    
    def remove_item(self, product_id: str) -> None:
        if self.status != OrderStatus.DRAFT:
            raise DomainException("Can only remove items from draft orders")
        
        self._items = [item for item in self._items 
                      if item.product_id != product_id]
    
    def place(self) -> None:
        if self.status != OrderStatus.DRAFT:
            raise DomainException("Can only place draft orders")
        
        if not self._items:
            raise DomainException("Cannot place order without items")
        
        if self.total < Money(Decimal('10'), 'USD'):
            raise DomainException("Order total must be at least $10")
        
        self.status = OrderStatus.PLACED
    
    def cancel(self, reason: str) -> None:
        if self.status not in [OrderStatus.PLACED]:
            raise DomainException("Cannot cancel order in current status")
        
        self.status = OrderStatus.CANCELLED

# domain/exceptions.py
class DomainException(Exception):
    pass

# domain/repositories.py
from abc import ABC, abstractmethod
from typing import Optional, List

class OrderRepository(ABC):
    @abstractmethod
    def find(self, order_id: str) -> Optional[Order]:
        pass
    
    @abstractmethod
    def save(self, order: Order) -> None:
        pass
    
    @abstractmethod
    def find_by_customer(self, customer_id: str) -> List[Order]:
        pass
```

### Application Layer

```python
# services/order_service.py
from typing import List
from domain.models import Order, Money
from domain.repositories import OrderRepository
from domain.exceptions import DomainException
from decimal import Decimal

class OrderService:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo
    
    def create_order(self, customer_id: str) -> str:
        order_id = generate_uuid()
        order = Order(order_id, customer_id)
        self.order_repo.save(order)
        return order_id
    
    def add_item_to_order(self, order_id: str, product_id: str,
                         product_name: str, quantity: int, 
                         price: Decimal) -> None:
        order = self.order_repo.find(order_id)
        if not order:
            raise ValueError("Order not found")
        
        money = Money(price, 'USD')
        order.add_item(product_id, product_name, quantity, money)
        self.order_repo.save(order)
    
    def place_order(self, order_id: str) -> None:
        order = self.order_repo.find(order_id)
        if not order:
            raise ValueError("Order not found")
        
        order.place()
        self.order_repo.save(order)
    
    def cancel_order(self, order_id: str, reason: str) -> None:
        order = self.order_repo.find(order_id)
        if not order:
            raise ValueError("Order not found")
        
        order.cancel(reason)
        self.order_repo.save(order)
    
    def get_order(self, order_id: str) -> Order:
        order = self.order_repo.find(order_id)
        if not order:
            raise ValueError("Order not found")
        return order
    
    def get_customer_orders(self, customer_id: str) -> List[Order]:
        return self.order_repo.find_by_customer(customer_id)
```

### Infrastructure Layer

```python
# persistence/order_repository.py
from typing import Optional, List
from domain.models import Order, OrderItem, Money, OrderStatus
from domain.repositories import OrderRepository
from decimal import Decimal

class SqlOrderRepository(OrderRepository):
    def __init__(self, session):
        self.session = session
    
    def find(self, order_id: str) -> Optional[Order]:
        model = self.session.query(OrderModel).filter_by(
            order_id=order_id
        ).first()
        return self._to_domain(model) if model else None
    
    def save(self, order: Order) -> None:
        model = self._to_model(order)
        self.session.merge(model)
        self.session.commit()
    
    def find_by_customer(self, customer_id: str) -> List[Order]:
        models = self.session.query(OrderModel).filter_by(
            customer_id=customer_id
        ).all()
        return [self._to_domain(m) for m in models]
    
    def _to_domain(self, model) -> Order:
        order = Order(model.order_id, model.customer_id)
        order.status = OrderStatus(model.status)
        for item_model in model.items:
            order._items.append(OrderItem(
                product_id=item_model.product_id,
                product_name=item_model.product_name,
                quantity=item_model.quantity,
                unit_price=Money(Decimal(str(item_model.unit_price)), 
                                item_model.currency)
            ))
        return order
    
    def _to_model(self, order: Order):
        return OrderModel(
            order_id=order.order_id,
            customer_id=order.customer_id,
            status=order.status.value,
            items=[OrderItemModel(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=float(item.unit_price.amount),
                currency=item.unit_price.currency
            ) for item in order.items]
        )
```

### Interface Layer

```python
# api/order_routes.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from decimal import Decimal
from services.order_service import OrderService

router = APIRouter()

class OrderItemRequest(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: Decimal

class OrderResponse(BaseModel):
    order_id: str
    customer_id: str
    status: str
    items: List[dict]
    total: Decimal

@router.post("/orders", response_model=dict)
def create_order(customer_id: str, 
                 service: OrderService = Depends()):
    order_id = service.create_order(customer_id)
    return {"order_id": order_id}

@router.post("/orders/{order_id}/items")
def add_item(order_id: str, item: OrderItemRequest,
             service: OrderService = Depends()):
    try:
        service.add_item_to_order(
            order_id, item.product_id, item.product_name,
            item.quantity, item.price
        )
        return {"message": "Item added"}
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/orders/{order_id}/place")
def place_order(order_id: str, service: OrderService = Depends()):
    try:
        service.place_order(order_id)
        return {"message": "Order placed"}
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, service: OrderService = Depends()):
    try:
        order = service.get_order(order_id)
        return OrderResponse(
            order_id=order.order_id,
            customer_id=order.customer_id,
            status=order.status.value,
            items=[{
                "product_id": item.product_id,
                "product_name": item.product_name,
                "quantity": item.quantity,
                "subtotal": float(item.subtotal.amount)
            } for item in order.items],
            total=float(order.total.amount)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

## Testing

```python
# tests/unit/test_order.py
import pytest
from decimal import Decimal
from domain.models import Order, Money, OrderStatus
from domain.exceptions import DomainException

class TestOrder:
    def test_create_order(self):
        order = Order("order-1", "customer-1")
        assert order.status == OrderStatus.DRAFT
        assert len(order.items) == 0
    
    def test_add_item(self):
        order = Order("order-1", "customer-1")
        order.add_item("prod-1", "Widget", 2, Money(Decimal('10'), 'USD'))
        
        assert len(order.items) == 1
        assert order.items[0].quantity == 2
        assert order.total == Money(Decimal('20'), 'USD')
    
    def test_cannot_add_item_to_placed_order(self):
        order = Order("order-1", "customer-1")
        order.add_item("prod-1", "Widget", 2, Money(Decimal('10'), 'USD'))
        order.place()
        
        with pytest.raises(DomainException):
            order.add_item("prod-2", "Gadget", 1, Money(Decimal('25'), 'USD'))
    
    def test_place_empty_order_fails(self):
        order = Order("order-1", "customer-1")
        
        with pytest.raises(DomainException):
            order.place()
    
    def test_place_order_below_minimum_fails(self):
        order = Order("order-1", "customer-1")
        order.add_item("prod-1", "Widget", 1, Money(Decimal('5'), 'USD'))
        
        with pytest.raises(DomainException):
            order.place()
    
    def test_cancel_placed_order(self):
        order = Order("order-1", "customer-1")
        order.add_item("prod-1", "Widget", 2, Money(Decimal('10'), 'USD'))
        order.place()
        order.cancel("Customer requested")
        
        assert order.status == OrderStatus.CANCELLED
```

## Key Takeaways

1. **Domain logic in models**: Business rules are in Order, not OrderService
2. **Value objects for validation**: Money validates amount and currency
3. **Aggregate root controls access**: All modifications go through Order
4. **Repository decouples persistence**: Domain doesn't know about database
5. **Services orchestrate**: Application services coordinate, not contain logic
