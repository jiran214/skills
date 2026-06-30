# DDD Tactical Patterns Reference

## Pattern Priority

| Priority | Pattern | Use When |
|----------|---------|----------|
| Must | Entities | Objects with identity and lifecycle |
| Must | Value Objects | Immutable attributes (Money, Address) |
| Must | Aggregates | Consistency boundaries |
| Must | Repository Interfaces | Persistence decoupling |
| Recommended | Domain Services | Cross-aggregate logic |
| Recommended | Domain Exceptions | Business rule expression |
| Optional | Domain Events | Cross-module communication |
| Optional | ACL | External system integration |

## Entities

### Characteristics
- Has unique identity (ID)
- Has lifecycle (created, modified, archived)
- Identity persists across state changes
- Equality based on identity, not attributes

### Implementation

```python
class Order:  # Entity
    def __init__(self, order_id: str, customer_id: str):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items = []
        self.status = OrderStatus.DRAFT
    
    def add_item(self, product_id: str, quantity: int, price: Money):
        if self.status != OrderStatus.DRAFT:
            raise DomainException("Cannot add items to non-pending order")
        self.items.append(OrderItem(product_id, quantity, price))
    
    def __eq__(self, other):
        if not isinstance(other, Order):
            return False
        return self.order_id == other.order_id
```

## Value Objects

### Characteristics
- No identity
- Immutable
- Equality based on attributes
- Self-validating

### Implementation

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be 3-letter ISO code")
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def __mul__(self, quantity: int) -> 'Money':
        return Money(self.amount * quantity, self.currency)

@dataclass(frozen=True)
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    
    def __post_init__(self):
        if not self.zip_code.isdigit() or len(self.zip_code) != 5:
            raise ValueError("Invalid zip code")
```

## Aggregates

### Characteristics
- Cluster of objects treated as a unit
- Has aggregate root (entry point)
- Enforces invariants
- Transactional boundary

### Design Rules

1. **Reference other aggregates by ID only**
2. **One aggregate per transaction**
3. **Keep aggregates small**
4. **Root entity controls all modifications**

### Implementation

```python
class Order:  # Aggregate Root
    def __init__(self, order_id: str, customer_id: str):
        self.order_id = order_id
        self.customer_id = customer_id  # Reference by ID
        self._items: List[OrderItem] = []
        self.status = OrderStatus.DRAFT
    
    @property
    def items(self) -> List[OrderItem]:
        return self._items.copy()  # Defensive copy
    
    def add_item(self, product_id: str, quantity: int, price: Money):
        # Invariant: Cannot exceed 100 items
        if len(self._items) >= 100:
            raise DomainException("Cart cannot have more than 100 items")
        
        # Invariant: Cannot exceed $10,000 total
        new_total = self._calculate_total() + (price * quantity)
        if new_total > Money(Decimal('10000'), 'USD'):
            raise DomainException("Cart total cannot exceed $10,000")
        
        self._items.append(OrderItem(product_id, quantity, price))
    
    def place(self):
        # Invariant: Cannot place empty order
        if not self._items:
            raise DomainException("Cannot place empty order")
        self.status = OrderStatus.PLACED
    
    def _calculate_total(self) -> Money:
        return sum((item.price * item.quantity for item in self._items), 
                   Money(Decimal('0'), 'USD'))
```

## Domain Services

### When to Use
- Operation doesn't belong to a single entity
- Cross-aggregate operations
- External system integration

### Implementation

```python
class PricingService:  # Domain Service
    def calculate_discount(self, order: Order, customer: Customer) -> Money:
        if customer.is_vip():
            return order.total * Decimal('0.1')
        return Money(Decimal('0'), 'USD')

class TransferService:  # Domain Service
    def __init__(self, account_repo: AccountRepository):
        self.account_repo = account_repo
    
    def transfer(self, from_id: str, to_id: str, amount: Money):
        from_account = self.account_repo.find(from_id)
        to_account = self.account_repo.find(to_id)
        
        from_account.debit(amount)
        to_account.credit(amount)
        
        self.account_repo.save(from_account)
        self.account_repo.save(to_account)
```

## Domain Exceptions

### Implementation

```python
class DomainException(Exception):
    """Base exception for domain errors"""
    pass

class BusinessRuleViolation(DomainException):
    """Raised when a business rule is violated"""
    pass

class InsufficientStockException(DomainException):
    def __init__(self, product_id: str, requested: int, available: int):
        super().__init__(
            f"Insufficient stock for {product_id}: "
            f"requested {requested}, available {available}"
        )
```

## Domain Events (Optional)

### When to Use
- Cross-module communication needed
- Audit logging required
- Eventual consistency acceptable

### Implementation

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class DomainEvent:
    event_id: str
    occurred_on: datetime
    aggregate_id: str

@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    customer_id: str
    total_amount: Money
    item_count: int

class EventPublisher:
    def __init__(self):
        self._handlers: Dict[type, List[Callable]] = {}
    
    def subscribe(self, event_type: type, handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def publish(self, event: DomainEvent):
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(event)
```

## Repository Pattern

### Interface (Domain Layer)

```python
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

### Implementation (Infrastructure Layer)

```python
class SqlAlchemyOrderRepository(OrderRepository):
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
    
    def _to_domain(self, model: OrderModel) -> Order:
        order = Order(model.order_id, model.customer_id)
        order.status = OrderStatus(model.status)
        for item_model in model.items:
            order._items.append(OrderItem(
                product_id=item_model.product_id,
                quantity=item_model.quantity,
                price=Money(item_model.amount, item_model.currency)
            ))
        return order
```

## Anti-Patterns

### 1. Anemic Domain Model
```python
# Bad - no business logic in entity
class Order:
    def __init__(self):
        self.items = []
        self.total = Money(0, 'USD')

# Good - rich domain model
class Order:
    def add_item(self, product_id: str, quantity: int, price: Money):
        if quantity <= 0:
            raise DomainException("Quantity must be positive")
        self.items.append(OrderItem(product_id, quantity, price))
```

### 2. Large Aggregates
```python
# Bad - too many responsibilities
class Order:
    def __init__(self):
        self.items = []
        self.payments = []
        self.shipments = []
        self.invoices = []

# Good - focused aggregate
class Order:
    def __init__(self):
        self.items = []
        self.status = "draft"
```

### 3. Lazy-Loading Aggregate
```python
# Bad - lazy loading breaks consistency
class Order:
    @property
    def items(self):
        return self._load_items_from_db()

# Good - eager loading within aggregate
class Order:
    def __init__(self, items: List[OrderItem]):
        self._items = items
```
