# Cyber Training Platform

A comprehensive platform for cybersecurity training, featuring isolated lab environments and virtual machine management.

## 🚀 Features

- **VM Management**
  - Create and manage virtual machines
  - Start/stop VM instances
  - Monitor VM status and resources
  - Secure remote access (RDP/SSH)

- **Lab Environments**
  - Pre-configured security lab templates
  - Isolated networking
  - Multi-VM lab scenarios
  - Progress tracking

- **Security**
  - JWT-based authentication
  - Role-based access control
  - Secure remote connections
  - Network isolation

## 🏗 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/         # API endpoints
│   ├── core/              # Core functionality
│   └── services/          # Business logic
├── tests/                 # Test cases
└── scripts/              # Utility scripts
```

## 🛠 Prerequisites

- Python 3.7+
- VirtualBox 7.0+
- 8GB+ RAM
- 50GB+ free disk space
- Windows/Linux host OS

## 📦 Installation

1. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Install VirtualBox**
```bash
# Windows
./scripts/install_virtualbox.bat

# Linux
./scripts/install_virtualbox.sh
```

## 🚀 Quick Start

1. **Start the backend**
```bash
python -m uvicorn app.main:app --reload
```

2. **Create your first lab**
```bash
# Get auth token
curl -X POST http://localhost:8000/api/auth/token -d "username=admin&password=admin123"

# Create a lab
curl -X POST http://localhost:8000/api/labs -H "Authorization: Bearer YOUR_TOKEN"
```

## 📚 Documentation

- [API Documentation](./docs/api.md)
- [Architecture Overview](./docs/architecture.md)
- [Development Guide](./docs/development.md)
- [Deployment Guide](./docs/deployment.md)
- [Security Guide](./docs/security.md)

## 🧪 Testing

```bash
pytest
pytest --cov=app tests/
```

## 🔒 Security

- Change default credentials in production
- Use HTTPS in production
- Follow security guidelines in [Security Guide](./docs/security.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🗺 Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features and development timeline.
