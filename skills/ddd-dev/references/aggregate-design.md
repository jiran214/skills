# Aggregate Design Guidelines

## Core Principles

### 1. Protect Business Invariants
Aggregates exist to enforce business rules that must always be true within their boundary.

```python
class BankAccount:  # Aggregate Root
    def withdraw(self, amount: Money):
        # Invariant: Balance cannot be negative
        if self.balance < amount:
            raise DomainException("Insufficient funds")
        self.balance = self.balance - amount
        self.transactions.append(Transaction(amount, TransactionType.WITHDRAWAL))
```

### 2. Design Small Aggregates
Large aggregates cause performance issues and concurrency problems.

**Bad Example:**
```python
# Too large - contains too many entities
class Order:
    def __init__(self):
        self.items = []           # Entity
        self.payments = []        # Entity
        self.shipments = []       # Entity
        self.invoices = []        # Entity
        self.refunds = []         # Entity
```

**Good Example:**
```python
# Small, focused aggregate
class Order:
    def __init__(self):
        self.items = []           # Value Objects
        self.status = OrderStatus
        self.total = Money

# Separate aggregates
class Payment:
    def __init__(self):
        self.order_id = str       # Reference by ID
        self.amount = Money
        self.status = PaymentStatus

class Shipment:
    def __init__(self):
        self.order_id = str       # Reference by ID
        self.address = Address
        self.status = ShipmentStatus
```

### 3. Reference Other Aggregates by ID
Never hold direct references to other aggregates.

**Bad Example:**
```python
class Order:
    def __init__(self, customer: Customer):  # Direct reference
        self.customer = customer
```

**Good Example:**
```python
class Order:
    def __init__(self, customer_id: str):  # Reference by ID
        self.customer_id = customer_id
```

### 4. One Aggregate Per Transaction
Each transaction should modify only one aggregate.

**Bad Example:**
```python
def place_order(order_id: str, customer_id: str):
    order = order_repo.find(order_id)
    customer = customer_repo.find(customer_id)
    
    order.place()
    customer.add_order(order_id)  # Modifies another aggregate in same transaction
    
    order_repo.save(order)
    customer_repo.save(customer)
```

**Good Example:**
```python
def place_order(order_id: str, customer_id: str):
    order = order_repo.find(order_id)
    order.place()
    order_repo.save(order)
    
    # Use domain event for cross-aggregate communication
    event_publisher.publish(OrderPlaced(order_id, customer_id))
```

## Aggregate Boundary Identification

### Step 1: Identify Business Invariants
Ask: "What rules must always be true?"

For an e-commerce system:
- Order total must equal sum of item prices
- Cannot order more than available inventory
- Customer credit limit cannot be exceeded

### Step 2: Group Related Entities
Ask: "Which entities must be consistent together?"

```python
# These belong together - changing one affects the other
class Order:
    items: List[OrderItem]      # Changing items affects total
    total: Money                # Must be consistent with items
    discount: Discount          # Affects total calculation
```

### Step 3: Identify Transaction Boundaries
Ask: "What must be saved atomically?"

```python
# Must be saved together
order = Order()
order.add_item(product_id, quantity, price)  # Changes total
order.apply_discount(discount_code)           # Changes total
order_repo.save(order)  # Atomic save
```

### Step 4: Consider Performance
Ask: "Will this aggregate be too large?"

```python
# Problematic - loads too much data
class Customer:
    orders: List[Order]           # Could be thousands
    reviews: List[Review]         # Could be hundreds
    wishlists: List[Wishlist]     # Growing over time

# Better - separate aggregates
class Customer:
    customer_id: str
    name: str
    email: str
    # References by count, not full objects
    order_count: int
    review_count: int
```

## Aggregate Design Patterns

### Pattern: Aggregate Root with Child Entities
```python
class Order:  # Aggregate Root
    def __init__(self, order_id: str):
        self.order_id = order_id
        self._items: List[OrderItem] = []
    
    def add_item(self, product_id: str, quantity: int, price: Money):
        item = OrderItem(product_id, quantity, price)
        self._items.append(item)
        self._recalculate_total()
    
    def remove_item(self, product_id: str):
        self._items = [i for i in self._items if i.product_id != product_id]
        self._recalculate_total()

class OrderItem:  # Child Entity
    def __init__(self, product_id: str, quantity: int, price: Money):
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
```

### Pattern: Aggregate with Value Objects
```python
class Address:  # Value Object
    def __init__(self, street: str, city: str, state: str, zip_code: str):
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
    
    def __eq__(self, other):
        return (self.street == other.street and
                self.city == other.city and
                self.state == other.state and
                self.zip_code == other.zip_code)

class Customer:  # Aggregate Root
    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        self.shipping_address: Optional[Address] = None
        self.billing_address: Optional[Address] = None
```

### Pattern: Aggregate with Domain Events
```python
class Order:  # Aggregate Root
    def __init__(self, order_id: str):
        self.order_id = order_id
        self._events: List[DomainEvent] = []
    
    def place(self):
        self.status = OrderStatus.PLACED
        self._events.append(OrderPlaced(
            event_id=generate_id(),
            occurred_on=datetime.now(),
            aggregate_id=self.order_id,
            customer_id=self.customer_id,
            total_amount=self.total
        ))
    
    def get_events(self) -> List[DomainEvent]:
        events = self._events.copy()
        self._events.clear()
        return events
```

## Common Anti-Patterns

### 1. Anemic Aggregate
```python
# Bad - no business logic
class Order:
    def __init__(self):
        self.items = []
        self.total = Money(0, 'USD')
    
    def get_items(self):
        return self.items
    
    def set_total(self, total):
        self.total = total

# Good - rich domain model
class Order:
    def add_item(self, product_id: str, quantity: int, price: Money):
        if quantity <= 0:
            raise DomainException("Quantity must be positive")
        self.items.append(OrderItem(product_id, quantity, price))
        self._recalculate_total()
```

### 2. God Aggregate
```python
# Bad - too many responsibilities
class Order:
    def __init__(self):
        self.items = []
        self.payments = []
        self.shipments = []
        self.invoices = []
        self.refunds = []
        self.customer = None
        self.warehouse = None
    
    def place_order(self): pass
    def process_payment(self): pass
    def create_shipment(self): pass
    def generate_invoice(self): pass
    def process_refund(self): pass

# Good - focused aggregates
class Order: pass
class Payment: pass
class Shipment: pass
```

### 3. Lazy-Loading Aggregate
```python
# Bad - lazy loading breaks transactional consistency
class Order:
    @property
    def items(self):
        # Loads from database on access
        return self._load_items_from_db()

# Good - eager loading within aggregate
class Order:
    def __init__(self, items: List[OrderItem]):
        self._items = items  # Loaded with aggregate
```
