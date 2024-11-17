# Cyber Training Platform Backend

A FastAPI-based backend service for managing virtual machines and lab environments in a cybersecurity training platform.

## Features

- VM Management (Mock implementation)
  - List, start, stop, and get info about VMs
  - Create and delete VMs
  - Monitor VM status
- Lab Environment Management
  - Create and manage lab environments
  - Start/stop entire lab environments
  - Track lab progress and status
- JWT-based Authentication
  - Secure token-based authentication
  - Password hashing with bcrypt
  - Role-based access control (planned)

## Prerequisites

- Python 3.7+
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the backend directory with the following settings:

```env
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:3000"]
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## Running the Server

Start the development server:
```bash
uvicorn app.main:app --reload --port 8000
```

## API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- POST `/api/auth/token` - Get access token

### VMs
- GET `/api/vms` - List all VMs
- GET `/api/vms/{vm_id}` - Get VM details
- POST `/api/vms/{vm_id}/start` - Start a VM
- POST `/api/vms/{vm_id}/stop` - Stop a VM
- POST `/api/vms` - Create a new VM
- DELETE `/api/vms/{vm_id}` - Delete a VM

### Labs
- GET `/api/labs` - List all labs
- GET `/api/labs/{lab_id}` - Get lab details
- POST `/api/labs` - Create a new lab
- POST `/api/labs/{lab_id}/start` - Start a lab
- POST `/api/labs/{lab_id}/stop` - Stop a lab
- DELETE `/api/labs/{lab_id}` - Delete a lab

## Development

Current implementation uses mock data for development. To implement real VM management:

1. Install necessary VM management libraries (e.g., libvirt, VirtualBox)
2. Update VM service with real implementation
3. Add proper error handling and logging
4. Implement database integration for persistent storage

## Security Considerations

- Change the default SECRET_KEY in production
- Implement proper rate limiting
- Add input validation and sanitization
- Use HTTPS in production
- Implement proper access control
- Monitor and log security events

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
