# DDD Project Structure Templates

## Simplified Structure (Recommended for Small-Medium Projects)

```
src/
├── domain/                # Domain Layer
│   ├── models.py          # Entities + Value Objects + Aggregates
│   ├── services.py        # Domain Services
│   ├── repositories.py    # Repository Interfaces
│   └── exceptions.py      # Domain Exceptions
│
├── services/              # Application Layer (Use Cases)
│   └── order_service.py   # Application Services
│
├── persistence/           # Infrastructure Layer
│   └── order_repository.py
│
└── api/                   # Interface Layer
    └── order_routes.py
```

### Layer Dependencies
```
API → Services → Domain ← Persistence
```

- Domain Layer: No dependencies
- Services Layer: Depends on Domain
- Persistence Layer: Implements Domain interfaces
- API Layer: Depends on Services

### Implementation Example

```python
# domain/models.py
from dataclasses import dataclass
from typing import List
from decimal import Decimal

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

class OrderItem:
    def __init__(self, product_id: str, quantity: int, price: Money):
        self.product_id = product_id
        self.quantity = quantity
        self.price = price

class Order:  # Aggregate Root
    def __init__(self, order_id: str, customer_id: str):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items: List[OrderItem] = []
        self.status = "draft"
    
    def add_item(self, product_id: str, quantity: int, price: Money):
        if self.status != "draft":
            raise DomainException("Can only add items to draft orders")
        self.items.append(OrderItem(product_id, quantity, price))
    
    def place(self):
        if not self.items:
            raise DomainException("Cannot place empty order")
        self.status = "placed"

# domain/exceptions.py
class DomainException(Exception):
    pass

# domain/repositories.py
from abc import ABC, abstractmethod
from typing import Optional

class OrderRepository(ABC):
    @abstractmethod
    def find(self, order_id: str) -> Optional[Order]:
        pass
    
    @abstractmethod
    def save(self, order: Order) -> None:
        pass

# services/order_service.py
from domain.models import Order, Money
from domain.repositories import OrderRepository

class OrderService:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo
    
    def create_order(self, customer_id: str) -> str:
        order_id = generate_id()
        order = Order(order_id, customer_id)
        self.order_repo.save(order)
        return order_id
    
    def add_item(self, order_id: str, product_id: str, 
                 quantity: int, price: Money):
        order = self.order_repo.find(order_id)
        if not order:
            raise ValueError("Order not found")
        
        order.add_item(product_id, quantity, price)
        self.order_repo.save(order)

# persistence/order_repository.py
from typing import Optional
from domain.models import Order
from domain.repositories import OrderRepository

class SqlOrderRepository(OrderRepository):
    def __init__(self, session):
        self.session = session
    
    def find(self, order_id: str) -> Optional[Order]:
        # Query database and convert to domain model
        pass
    
    def save(self, order: Order) -> None:
        # Convert to database model and persist
        pass

# api/order_routes.py
from fastapi import APIRouter, Depends
from services.order_service import OrderService

router = APIRouter()

@router.post("/orders")
def create_order(customer_id: str, 
                 service: OrderService = Depends()):
    return service.create_order(customer_id)
```

## Full Structure (For Complex Projects)

```
src/
├── domain/                    # Domain Layer
│   ├── model/                 # Domain models
│   │   ├── entities.py        # Entity classes
│   │   ├── value_objects.py   # Value object classes
│   │   ├── aggregates.py      # Aggregate root classes
│   │   └── events.py          # Domain events
│   ├── services/              # Domain services
│   │   └── order_service.py
│   ├── repositories/          # Repository interfaces
│   │   └── order_repository.py
│   └── exceptions.py          # Domain exceptions
│
├── application/               # Application Layer
│   ├── services/              # Application services
│   │   └── order_app_service.py
│   ├── commands/              # Command handlers
│   │   └── place_order.py
│   └── queries/               # Query handlers
│       └── get_order.py
│
├── infrastructure/            # Infrastructure Layer
│   ├── persistence/           # Database implementations
│   │   ├── models/            # ORM models
│   │   │   └── order_model.py
│   │   └── repositories/      # Repository implementations
│   │       └── sql_order_repository.py
│   ├── messaging/             # Message broker implementations
│   │   └── event_publisher.py
│   └── external/              # External service adapters
│       └── payment_gateway.py
│
├── interfaces/                # Interface Layer
│   ├── api/                   # REST API
│   │   ├── routes/
│   │   │   └── order_routes.py
│   │   └── schemas/
│   │       └── order_schema.py
│   └── cli/                   # CLI interface
│       └── order_commands.py
│
└── shared/                    # Shared kernel
    ├── events/                # Event infrastructure
    │   └── event_bus.py
    └── exceptions/            # Shared exceptions
        └── base_exception.py
```

### Layer Dependencies
```
Interfaces → Application → Domain ← Infrastructure
```

## Testing Structure

```
tests/
├── unit/
│   ├── domain/
│   │   ├── test_models.py
│   │   └── test_services.py
│   └── services/
│       └── test_order_service.py
├── integration/
│   └── persistence/
│       └── test_order_repository.py
└── conftest.py
```

## Implementation Checklist

### Simplified (Start Here)
- [ ] Define domain models (entities, value objects, aggregates)
- [ ] Create repository interfaces
- [ ] Implement domain exceptions
- [ ] Create application services
- [ ] Implement persistence layer
- [ ] Build API layer
- [ ] Write unit tests for domain logic
- [ ] Write integration tests for repositories

### Full (Add When Needed)
- [ ] Implement domain events
- [ ] Create domain services for complex logic
- [ ] Add anti-corruption layers for external systems
- [ ] Split into bounded contexts
- [ ] Add event sourcing (if needed)
