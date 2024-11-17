# Architecture Overview

This document provides a comprehensive overview of the Cyber Training Platform's architecture.

## System Architecture

### High-Level Overview

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│    Frontend     │────▶│    Backend   │────▶│    Database     │
│    (React)      │     │   (FastAPI)  │     │  (PostgreSQL)   │
└─────────────────┘     └──────────────┘     └─────────────────┘
                              │
                              │
                        ┌─────▼─────┐
                        │ VirtualBox │
                        │    API    │
                        └───────────┘
```

The platform is built on a modern, scalable architecture with four main components:

1. **Frontend**: React-based SPA with TypeScript
2. **Backend**: FastAPI application
3. **Database**: PostgreSQL for data persistence
4. **VM Management**: VirtualBox API integration

## Component Details

### 1. Frontend Architecture

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   ├── pages/           # Route-based page components
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API integration
│   ├── store/           # State management
│   └── utils/           # Helper functions
└── public/              # Static assets
```

#### Key Features:
- React with TypeScript for type safety
- Redux for state management
- React Router for navigation
- Material-UI for consistent styling
- WebSocket integration for real-time updates

### 2. Backend Architecture

```
backend/
├── app/
│   ├── api/            # REST endpoints
│   ├── core/           # Core business logic
│   ├── models/         # Database models
│   ├── services/       # External service integration
│   └── utils/          # Helper functions
└── tests/              # Test suite
```

#### Key Features:
- FastAPI for high-performance async operations
- SQLAlchemy for ORM
- Pydantic for data validation
- JWT-based authentication
- Role-based access control

### 3. Database Schema

```sql
-- Core Tables
users
├── id          (PK)
├── username
├── email
└── role

labs
├── id          (PK)
├── name
├── user_id     (FK → users.id)
├── status
└── created_at

vms
├── id          (PK)
├── lab_id      (FK → labs.id)
├── name
└── status

-- Association Tables
lab_templates
├── id          (PK)
├── name
└── config

user_labs
├── user_id     (FK → users.id)
└── lab_id      (FK → labs.id)
```

### 4. VM Management System

```
┌────────────────┐     ┌───────────────┐
│   VM Manager   │────▶│   VirtualBox  │
└────────────────┘     └───────────────┘
        │
        │
┌───────▼────────┐
│  VM Templates  │
└────────────────┘
```

#### Features:
- Isolated network environments
- Resource management
- Snapshot capabilities
- Template management

## Security Architecture

### Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│   JWT    │────▶│ Resource │
└──────────┘     └──────────┘     └──────────┘
```

1. User authentication via JWT
2. Role-based access control
3. Resource isolation
4. Network security

### Network Security

```
┌────────────┐     ┌─────────────┐     ┌──────────┐
│ Public Net │────▶│   Firewall  │────▶│ Lab Net  │
└────────────┘     └─────────────┘     └──────────┘
```

- Isolated lab networks
- Firewall rules
- VPN access (optional)
- HTTPS enforcement

## Scalability

### Horizontal Scaling

```
┌─────────────┐
│ Load        │
│ Balancer    │
└─────────────┘
      │
    ┌─┴─┐
┌───┴─┐ ├───┐
│ App │ │App │
└─────┘ └───┘
```

- Container-based deployment
- Load balancing
- Database replication
- Caching strategy

### Resource Management

- Dynamic resource allocation
- Auto-scaling capabilities
- Resource quotas
- Performance monitoring

## Data Flow

### Request Flow

```
Client Request
     │
     ▼
Load Balancer
     │
     ▼
API Gateway
     │
     ▼
Authentication
     │
     ▼
Business Logic
     │
     ▼
Database/VM
```

### WebSocket Flow

```
Client
  │
  ▼
WebSocket Server
  │
  ▼
Event Handler
  │
  ▼
VM Status Updates
```

## Monitoring and Logging

### System Monitoring

- Prometheus metrics
- Grafana dashboards
- Resource utilization
- Performance metrics

### Logging

- Centralized logging
- Error tracking
- Audit trails
- Performance monitoring

## Deployment Architecture

### Production Environment

```
┌─────────────┐     ┌─────────────┐
│   CI/CD     │────▶│  Production │
└─────────────┘     └─────────────┘
                          │
                    ┌─────┴─────┐
                    │  Staging  │
                    └───────────┘
```

- Containerized deployment
- Blue-green deployment
- Automated testing
- Rolling updates

### High Availability

- Multiple availability zones
- Database replication
- Failover mechanisms
- Backup strategies

## Integration Points

### External Services

- Authentication providers
- Storage services
- Monitoring services
- Backup services

### APIs

- REST API
- WebSocket API
- VirtualBox API
- Management API

## Future Considerations

### Planned Improvements

1. Microservices architecture
2. Kubernetes orchestration
3. Enhanced monitoring
4. AI-powered assistance

### Scalability Roadmap

1. Multi-region support
2. Enhanced caching
3. Improved resource management
4. Advanced analytics

## Technical Decisions

### Technology Choices

1. **Frontend**: React + TypeScript
   - Type safety
   - Component reusability
   - Rich ecosystem

2. **Backend**: FastAPI
   - Async support
   - High performance
   - OpenAPI documentation

3. **Database**: PostgreSQL
   - ACID compliance
   - Rich feature set
   - Reliability

4. **VM Management**: VirtualBox
   - Open source
   - Rich API
   - Cross-platform support

## Conclusion

This architecture is designed to be:
- Scalable
- Maintainable
- Secure
- Performance-oriented

The modular design allows for future improvements and modifications while maintaining system stability and security.
