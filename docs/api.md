# API Documentation

## Overview

The Cyber Training Platform provides a RESTful API for managing virtual machines, labs, and user interactions. This documentation covers all available endpoints, authentication, and usage examples.

## Base URL

Production: `https://api.cybertraining.com/v1`
Staging: `https://api-staging.cybertraining.com/v1`

## Authentication

All API requests require authentication using JWT tokens.

### Getting a Token

```http
POST /api/auth/token
Content-Type: application/x-www-form-urlencoded

username=admin&password=your_password
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

Use this token in subsequent requests:
```http
GET /api/labs
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## API Endpoints

### Labs

#### List Labs

```http
GET /api/labs
Authorization: Bearer YOUR_TOKEN
```

Response:
```json
{
  "labs": [
    {
      "id": "123",
      "name": "Penetration Testing Lab",
      "status": "running",
      "created_at": "2023-01-01T12:00:00Z"
    }
  ]
}
```

#### Create Lab

```http
POST /api/labs
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "name": "New Security Lab",
  "template": "ubuntu-20.04"
}
```

Response:
```json
{
  "id": "124",
  "name": "New Security Lab",
  "status": "creating",
  "created_at": "2023-01-02T12:00:00Z"
}
```

#### Get Lab Details

```http
GET /api/labs/{lab_id}
Authorization: Bearer YOUR_TOKEN
```

Response:
```json
{
  "id": "123",
  "name": "Penetration Testing Lab",
  "status": "running",
  "created_at": "2023-01-01T12:00:00Z",
  "vms": [
    {
      "id": "vm-1",
      "name": "target-machine",
      "status": "running"
    }
  ]
}
```

#### Delete Lab

```http
DELETE /api/labs/{lab_id}
Authorization: Bearer YOUR_TOKEN
```

Response:
```json
{
  "message": "Lab deleted successfully"
}
```

### Virtual Machines

#### List VMs

```http
GET /api/labs/{lab_id}/vms
Authorization: Bearer YOUR_TOKEN
```

Response:
```json
{
  "vms": [
    {
      "id": "vm-1",
      "name": "target-machine",
      "status": "running",
      "ip_address": "192.168.1.100"
    }
  ]
}
```

#### Create VM

```http
POST /api/labs/{lab_id}/vms
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "name": "new-target",
  "template": "kali-2023.1"
}
```

Response:
```json
{
  "id": "vm-2",
  "name": "new-target",
  "status": "creating",
  "ip_address": null
}
```

#### Control VM

```http
POST /api/vms/{vm_id}/action
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "action": "start|stop|restart"
}
```

Response:
```json
{
  "message": "VM action initiated successfully"
}
```

### Users

#### Get Current User

```http
GET /api/users/me
Authorization: Bearer YOUR_TOKEN
```

Response:
```json
{
  "id": "user-1",
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin"
}
```

#### Update User

```http
PATCH /api/users/me
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "email": "newemail@example.com"
}
```

Response:
```json
{
  "id": "user-1",
  "username": "admin",
  "email": "newemail@example.com",
  "role": "admin"
}
```

## Error Handling

The API uses conventional HTTP response codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error Response Format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message"
  }
}
```

## Rate Limiting

API requests are limited to:
- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated requests

Rate limit headers are included in all responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination using `limit` and `offset` parameters:

```http
GET /api/labs?limit=10&offset=0
```

Response includes pagination metadata:
```json
{
  "labs": [...],
  "pagination": {
    "total": 100,
    "limit": 10,
    "offset": 0,
    "next": "/api/labs?limit=10&offset=10",
    "previous": null
  }
}
```

## Filtering and Sorting

List endpoints support filtering and sorting:

```http
GET /api/labs?status=running&sort=-created_at
```

Common filter parameters:
- `status`: Filter by status
- `created_at`: Filter by creation date
- `name`: Filter by name (supports partial matches)

Sort parameter:
- Use `sort` parameter
- Prefix with `-` for descending order
- Multiple sort fields supported: `sort=-created_at,name`

## WebSocket API

Real-time updates are available through WebSocket connections:

```javascript
const ws = new WebSocket('wss://api.cybertraining.com/v1/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received update:', data);
};
```

### Event Types

- `lab.status_changed`
- `vm.status_changed`
- `lab.deleted`
- `vm.deleted`

Example event:
```json
{
  "type": "vm.status_changed",
  "data": {
    "vm_id": "vm-1",
    "status": "running"
  }
}
```

## SDK Support

Official SDKs are available for:
- Python
- JavaScript
- Go
- Java

Example using Python SDK:
```python
from cybertraining import Client

client = Client(api_key='your-token')
labs = client.labs.list()
```

## Support

For API support:
- Email: api-support@cybertraining.com
- Documentation Issues: Create a GitHub issue
- Status Page: status.cybertraining.com
