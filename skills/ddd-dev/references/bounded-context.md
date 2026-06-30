# Bounded Context Reference

## What is a Bounded Context?

A Bounded Context is a clear boundary within which a particular domain model is defined and applicable. It's the central pattern in DDD's strategic design.

## Identifying Bounded Contexts

### Step 1: Analyze the Business Domain

Ask these questions:
1. What are the main business capabilities?
2. Where do terms have different meanings?
3. Where are the natural organizational boundaries?

### Step 2: Identify Subdomains

**Core Domain**: The primary business differentiator
- Most valuable, deserves most attention
- Example: Recommendation algorithm for Netflix

**Supporting Domain**: Necessary but not differentiating
- Can be built in-house or outsourced
- Example: User management, billing

**Generic Domain**: Commodity functionality
- Buy or use open-source solutions
- Example: Email sending, payment processing

### Step 3: Draw Context Boundaries

```
┌─────────────────────────────────────────────────────┐
│                   E-Commerce System                  │
├──────────────┬──────────────┬───────────────────────┤
│   Order      │  Inventory   │      Payment          │
│  Context     │  Context     │      Context          │
│              │              │                       │
│ - Order      │ - Product    │ - Payment             │
│ - OrderItem  │ - Stock      │ - Transaction         │
│ - Customer   │ - Warehouse  │ - Refund              │
│ (by ID)      │              │                       │
└──────────────┴──────────────┴───────────────────────┘
```

## Context Mapping Patterns

### 1. Shared Kernel
Two contexts share a subset of the model.

```
┌─────────────┐     ┌─────────────┐
│  Context A  │─────│  Context B  │
│             │  ▼  │             │
│  ┌─────────┴─────┴─────────┐  │
│  │     Shared Kernel       │  │
│  └──────────────────────────┘  │
└──────────────────────────────┘
```

**When to use:**
- Small team
- Closely related contexts
- High trust between teams

**Risks:**
- Changes affect both contexts
- Requires coordination

### 2. Customer-Supplier
One context depends on another.

```
┌─────────────┐     ┌─────────────┐
│  Customer   │◀────│  Supplier   │
│  Context    │     │  Context    │
└─────────────┘     └─────────────┘
```

**When to use:**
- Upstream context provides services
- Downstream context consumes them
- Upstream team prioritizes downstream needs

### 3. Conformist
Downstream accepts upstream model as-is.

```
┌─────────────┐     ┌─────────────┐
│ Conformist  │────▶│  Upstream   │
│  Context    │     │  Context    │
└─────────────┘     └─────────────┘
```

**When to use:**
- Upstream is external (third-party API)
- No influence on upstream model
- Must accept their terms

### 4. Anti-Corruption Layer (ACL)
Translator between contexts.

```
┌─────────────┐     ┌─────────────┐
│  Context A  │────▶│     ACL     │────▶│  Context B  │
└─────────────┘     └─────────────┘     └─────────────┘
```

**When to use:**
- Legacy system integration
- External system with different model
- Need to protect domain model

**Implementation:**
```python
class LegacyOrderACL:
    def __init__(self, legacy_api: LegacyOrderAPI):
        self.legacy_api = legacy_api
    
    def translate_to_domain(self, legacy_order: dict) -> Order:
        return Order(
            order_id=legacy_order['ORDER_NUM'],
            customer_id=legacy_order['CUST_ID'],
            status=self._map_status(legacy_order['STATUS']),
            items=[self._translate_item(item) 
                   for item in legacy_order['LINE_ITEMS']]
        )
    
    def _map_status(self, legacy_status: str) -> OrderStatus:
        mapping = {
            'A': OrderStatus.ACTIVE,
            'X': OrderStatus.CANCELLED,
            'C': OrderStatus.COMPLETED
        }
        return mapping.get(legacy_status, OrderStatus.UNKNOWN)
```

### 5. Open Host Service (OHS)
Context provides protocol for others to use.

```
┌─────────────┐
│  Context A  │
│             │
│   ┌─────────┴─────────┐
│   │  Open Host Service │
│   │  (API, Events)     │
│   └─────────┬─────────┘
└─────────────┼─────────────┐
              │             │
    ┌─────────▼───┐ ┌───────▼─────┐
    │  Context B  │ │  Context C  │
    └─────────────┘ └─────────────┘
```

**When to use:**
- Many consumers
- Need stable interface
- Can version the API

### 6. Published Language
Shared language for communication.

```
┌─────────────┐     ┌─────────────┐
│  Context A  │────▶│  Published  │◀────│  Context B  │
│             │     │  Language   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Examples:**
- JSON Schema
- Protocol Buffers
- XML Schema
- Domain Events format

## Context Map Example

### E-Commerce System

```
┌──────────────────────────────────────────────────────────────┐
│                      E-Commerce Platform                      │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   Catalog    │   Order      │  Inventory   │   Payment      │
│   Context    │   Context    │  Context     │   Context      │
│              │              │              │                │
│  [Core]      │  [Core]      │ [Supporting] │  [Generic]     │
│              │              │              │                │
│  Product     │  Order       │  Stock       │  Payment       │
│  Category    │  OrderItem   │  Warehouse   │  Transaction   │
│  Brand       │  Customer    │  Reservation │  Refund        │
│              │  (by ID)     │              │                │
└──────┬───────┴──────┬───────┴──────┬───────┴────────┬───────┘
       │              │              │                │
       │   Customer-  │   Customer-  │    ACL         │
       │   Supplier   │   Supplier   │                │
       │              │              │                │
       ▼              ▼              ▼                ▼
┌──────────────────────────────────────────────────────────────┐
│                    External Systems                           │
├──────────────┬──────────────┬──────────────────────────────┤
│   Payment    │   Shipping   │     CRM                      │
│   Gateway    │   Provider   │     System                   │
└──────────────┴──────────────┴──────────────────────────────┘
```

## Implementation Guidelines

### 1. Define Context Boundaries in Code

```python
# Each context is a separate module/package
# src/contexts/order/
# src/contexts/inventory/
# src/contexts/payment/

# Context-specific models
class OrderContext:
    """Order context boundary"""
    
    class Order:
        def __init__(self, order_id: str, customer_id: str):
            # Customer is referenced by ID, not full object
            self.customer_id = customer_id
```

### 2. Use ACL for External Integration

```python
class PaymentGatewayACL:
    """Anti-Corruption Layer for payment gateway"""
    
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway
    
    def process_payment(self, order_id: str, amount: Money) -> PaymentResult:
        # Translate domain model to gateway format
        gateway_request = {
            'transaction_id': generate_id(),
            'amount': str(amount.amount),
            'currency': amount.currency,
            'reference': order_id
        }
        
        # Call external gateway
        response = self.gateway.charge(gateway_request)
        
        # Translate response back to domain model
        return PaymentResult(
            success=response['status'] == 'success',
            transaction_id=response['transaction_id'],
            error_message=response.get('error')
        )
```

### 3. Use Events for Cross-Context Communication

```python
# Order context publishes event
class OrderPlacedEvent(DomainEvent):
    def __init__(self, order_id: str, customer_id: str, total: Money):
        super().__init__()
        self.order_id = order_id
        self.customer_id = customer_id
        self.total = total

# Inventory context subscribes to event
class InventoryEventHandler:
    def handle_order_placed(self, event: OrderPlacedEvent):
        # Reserve inventory
        self.inventory_service.reserve(event.order_id, event.items)
```

### 4. Maintain Ubiquitous Language per Context

```python
# Order Context
class Order:
    def place(self):
        """Place the order - Order context language"""
        pass

# Payment Context  
class Payment:
    def capture(self):
        """Capture the payment - Payment context language"""
        pass

# Shipping Context
class Shipment:
    def dispatch(self):
        """Dispatch the shipment - Shipping context language"""
        pass
```

## Common Mistakes

### 1. One Big Model
```python
# Bad - single model for entire system
class SystemModel:
    orders: List[Order]
    products: List[Product]
    payments: List[Payment]
    shipments: List[Shipment]
```

### 2. Leaking Domain Models
```python
# Bad - exposing internal model
class OrderController:
    def get_order(self, order_id: str) -> OrderEntity:
        return self.order_repo.find(order_id)  # Returns domain entity
```

### 3. Tight Coupling
```python
# Bad - direct dependency on another context's model
class OrderService:
    def __init__(self, inventory_repo: InventoryRepository):
        self.inventory_repo = inventory_repo  # Direct dependency
```

### 4. Missing Translation
```python
# Bad - using same model across contexts
class Customer:  # Same model in Order and CRM contexts
    pass
```

## Context Evolution

### When to Split a Context
- Model becomes too complex
- Team grows too large
- Different rates of change
- Different scalability needs

### When to Merge Contexts
- Too much cross-context communication
- Shared model makes more sense
- Team is small enough
- Similar rate of change

### Versioning Context Boundaries
```python
# Version 1
class OrderV1:
    pass

# Version 2 - backward compatible
class OrderV2(OrderV1):
    pass
```
