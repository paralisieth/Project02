# Development Guide

This guide provides instructions and best practices for developing the Cyber Training Platform.

## Development Environment Setup

### Prerequisites
- Python 3.7+
- VirtualBox 7.0+
- Git
- PostgreSQL
- Node.js and npm (for frontend development)
- Your favorite IDE (VS Code recommended)

### Initial Setup

1. **Clone the Repository**
```bash
git clone https://github.com/your-org/cyber-training-platform.git
cd cyber-training-platform
```

2. **Set Up Python Environment**
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Database Setup**
```bash
# Create development database
createdb cyberlab_dev

# Run migrations
alembic upgrade head
```

4. **Environment Configuration**
```bash
# Copy example environment file
cp example.env .env

# Edit .env with your development settings
# Make sure to set DEBUG=True for development
```

5. **Frontend Setup**
```bash
cd frontend
npm install
```

## Development Workflow

### Backend Development

1. **Running the Development Server**
```bash
# From the project root
python -m uvicorn app.main:app --reload
```

2. **Creating Database Migrations**
```bash
# After making model changes
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

3. **Running Tests**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_specific.py
```

### Frontend Development

1. **Running the Development Server**
```bash
cd frontend
npm start
```

2. **Building for Production**
```bash
npm run build
```

## Code Style Guidelines

### Python Code Style
- Follow PEP 8 guidelines
- Use type hints
- Maximum line length: 88 characters (Black formatter)
- Use docstrings for functions and classes

Example:
```python
def get_user_labs(user_id: int) -> List[Lab]:
    """
    Retrieve all labs associated with a user.

    Args:
        user_id: The ID of the user

    Returns:
        List of Lab objects associated with the user
    """
    return Lab.query.filter_by(user_id=user_id).all()
```

### Frontend Code Style
- Use ESLint configuration
- Follow React best practices
- Use TypeScript for type safety
- Use functional components with hooks

Example:
```typescript
interface LabProps {
  labId: string;
  name: string;
}

const Lab: React.FC<LabProps> = ({ labId, name }) => {
  const [status, setStatus] = useState<string>('');

  useEffect(() => {
    // Effect logic here
  }, [labId]);

  return (
    <div>
      <h2>{name}</h2>
      <p>Status: {status}</p>
    </div>
  );
};
```

## Project Structure

```
├── app/
│   ├── api/            # API endpoints
│   ├── core/           # Core functionality
│   ├── models/         # Database models
│   └── services/       # Business logic
├── frontend/
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── hooks/      # Custom hooks
│   │   └── services/   # API services
│   └── public/         # Static files
└── tests/              # Test files
```

## Testing Guidelines

### Backend Testing
- Write unit tests for all new features
- Maintain test coverage above 80%
- Use pytest fixtures for common setup
- Mock external services

Example:
```python
def test_create_lab(client, auth_headers):
    response = client.post(
        "/api/labs",
        json={"name": "Test Lab", "template": "ubuntu"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Lab"
```

### Frontend Testing
- Use React Testing Library
- Write tests for critical user paths
- Test component behavior, not implementation

Example:
```typescript
test('renders lab details', () => {
  render(<Lab labId="123" name="Test Lab" />);
  expect(screen.getByText('Test Lab')).toBeInTheDocument();
});
```

## API Documentation

- All new endpoints must be documented using FastAPI's built-in documentation
- Include request/response examples
- Document all possible response codes

Example:
```python
@router.post("/labs", response_model=LabResponse)
async def create_lab(
    lab: LabCreate,
    current_user: User = Depends(get_current_user)
) -> LabResponse:
    """
    Create a new lab instance.

    Args:
        lab: Lab creation parameters
        current_user: Currently authenticated user

    Returns:
        Created lab details

    Raises:
        HTTPException: If lab creation fails
    """
    # Implementation
```

## Git Workflow

1. **Branch Naming**
   - Feature branches: `feature/description`
   - Bug fixes: `fix/description`
   - Hotfixes: `hotfix/description`

2. **Commit Messages**
   - Use present tense
   - Be descriptive
   - Reference issues when applicable

Example:
```bash
git commit -m "Add user authentication endpoint (#123)"
```

3. **Pull Requests**
   - Create PR from your branch to master
   - Include description of changes
   - Reference related issues
   - Ensure CI passes
   - Get code review approval

## Debugging Tips

1. **Backend Debugging**
   - Use FastAPI's debug mode
   - Check logs in `logs/app.log`
   - Use pdb for Python debugging
   ```python
   import pdb; pdb.set_trace()
   ```

2. **Frontend Debugging**
   - Use React Developer Tools
   - Check browser console
   - Use debugger statement
   ```javascript
   debugger;
   ```

## Common Issues and Solutions

1. **Database Migrations**
   ```bash
   # Reset migrations
   alembic downgrade base
   alembic upgrade head
   ```

2. **Virtual Environment**
   ```bash
   # Recreate environment
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Frontend Build Issues**
   ```bash
   # Clear npm cache
   npm cache clean --force
   rm -rf node_modules
   npm install
   ```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Project Wiki](https://github.com/your-org/cyber-training-platform/wiki)

## Getting Help

- Check existing issues on GitHub
- Ask in the development channel
- Contact the tech lead
- Review the troubleshooting guide

Remember to keep this guide updated as development practices evolve!
