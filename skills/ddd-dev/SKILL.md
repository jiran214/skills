---
name: ddd-dev
description: Domain-Driven Design development for strategic design, tactical design, bounded contexts, aggregates, entities, value objects, domain events, domain services, and repository pattern implementation.
---

# DDD Development Skill

Use this skill when designing or implementing domain-driven design patterns.

## Quick Assessment

First determine project complexity to choose the right approach:

| Aspect | Simple (1-5 people) | Complex (5+ people) |
|--------|---------------------|---------------------|
| Contexts | Single | Multiple |
| Layers | 2-3 | 4 |
| Patterns | Selective | Full |
| Events | Optional | Required |

**Decision Guide:**
- Simple CRUD, no complex rules → Skip DDD
- Moderate complexity, small team → Simplified DDD
- High complexity, multiple domains → Full DDD

## Workflow

### 1. Domain Analysis

1. **Identify Core Business Concepts**
   - What are the main business entities?
   - What business rules exist?
   - What operations are performed?

2. **Define Boundaries** (if complex)
   - Identify subdomains (core, supporting, generic)
   - Map relationships between contexts

### 2. Model Design

1. **Identify Domain Objects**
   - **Entities**: Objects with identity (Order, Customer)
   - **Value Objects**: Immutable attributes (Money, Address)
   - **Aggregates**: Consistency boundaries (Order + OrderItems)

2. **Define Aggregates**
   - Choose aggregate root
   - Define invariants (business rules)
   - Keep small and focused

3. **Design Services** (if needed)
   - Domain services for cross-aggregate logic
   - Application services for use cases

### 3. Implementation

**Choose Architecture:**

**Simplified (2-3 layers):**
```
┌─────────────────────────────────────┐
│           API / Interface           │
├─────────────────────────────────────┤
│         Services (Use Cases)        │
├─────────────────────────────────────┤
│    Domain (Models + Repositories)   │
└─────────────────────────────────────┘
```

**Full (4 layers):**
```
┌─────────────────────────────────────┐
│         User Interface Layer        │
├─────────────────────────────────────┤
│         Application Layer           │
├─────────────────────────────────────┤
│           Domain Layer              │
├─────────────────────────────────────┤
│       Infrastructure Layer          │
└─────────────────────────────────────┘
```

## Core Patterns Priority

### Must Use (Core Value)

1. **Entities + Value Objects**
   - Business logic has a home
   - Self-validating objects
   - Clear identity vs attributes

2. **Aggregate Root**
   - Consistency boundary
   - Entry point for modifications
   - Transaction boundary

3. **Repository Interface**
   - Decouples persistence from domain
   - Testable without database

### Recommended (Medium+ Projects)

4. **Domain Services**
   - Cross-aggregate operations
   - Stateless business logic

5. **Domain Exceptions**
   - Business rule expression
   - Clear error messages

### Optional (Skip Unless Needed)

6. **Domain Events**
   - Cross-module communication
   - Audit logging
   - Eventual consistency

7. **Anti-Corruption Layer**
   - External system integration

8. **Published Language**
   - Multi-team coordination

## Key Principles

1. **Ubiquitous Language**: Code uses business terms, not technical terms
2. **Model-Driven Design**: Business logic in domain models, not services
3. **Aggregate Boundaries**: Clear what must be modified together

## Resources

- For tactical patterns, read references/tactical-patterns.md
- For aggregate design, read references/aggregate-design.md
- For bounded contexts, read references/bounded-context.md
- For code examples, read examples/
- For project templates, read templates/

## Common Pitfalls

1. **Anemic Domain Model**: Entities with only getters/setters, logic in services
2. **Large Aggregates**: Aggregates that try to maintain too many invariants
3. **Leaky Abstractions**: Infrastructure concerns in domain layer
4. **Missing Ubiquitous Language**: Technical terms instead of business terms
5. **Wrong Aggregate Boundaries**: Putting everything in one aggregate
6. **Over-Engineering**: Adding patterns without clear need
