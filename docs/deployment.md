# Deployment Guide

This guide walks through the process of deploying the Cyber Training Platform in a production environment.

## Prerequisites

- Python 3.7+
- VirtualBox 7.0+
- PostgreSQL 13+
- Minimum 16GB RAM recommended for production
- 100GB+ storage space
- Linux server (recommended) or Windows Server

## Production Setup

### 1. System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system dependencies
sudo apt install -y python3-pip python3-venv postgresql nginx
```

### 2. Database Setup

```bash
# Create production database
sudo -u postgres createdb cyberlab_prod
sudo -u postgres createuser cyberlab_user

# Set up database password (make sure to use a strong password)
sudo -u postgres psql
postgres=# ALTER USER cyberlab_user WITH PASSWORD 'your_secure_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE cyberlab_prod TO cyberlab_user;
```

### 3. Application Setup

```bash
# Clone the repository
git clone https://github.com/your-org/cyber-training-platform.git
cd cyber-training-platform

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install production dependencies
pip install -r requirements.txt

# Configure environment variables
cp example.env .env
# Edit .env with production settings
```

### 4. Database Migration

```bash
# Run database migrations
alembic upgrade head
```

### 5. Gunicorn Setup

Create a systemd service file for the application:

```ini
# /etc/systemd/system/cyberlab.service
[Unit]
Description=Cyber Training Platform
After=network.target

[Service]
User=cyberlab
Group=cyberlab
WorkingDirectory=/path/to/cyber-training-platform
Environment="PATH=/path/to/cyber-training-platform/venv/bin"
ExecStart=/path/to/cyber-training-platform/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

### 6. Nginx Configuration

```nginx
# /etc/nginx/sites-available/cyberlab
server {
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 7. SSL Setup

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 8. Start Services

```bash
# Start and enable services
sudo systemctl start cyberlab
sudo systemctl enable cyberlab
sudo systemctl restart nginx
```

## Security Considerations

1. **Firewall Configuration**
   - Configure UFW or iptables to allow only necessary ports
   - Enable rate limiting for API endpoints

2. **VM Network Isolation**
   - Ensure proper VLAN configuration
   - Set up network policies for lab environments

3. **Monitoring**
   - Set up log rotation
   - Configure monitoring tools (e.g., Prometheus + Grafana)
   - Enable error reporting

## Backup Strategy

1. **Database Backups**
   ```bash
   # Set up daily backups
   pg_dump cyberlab_prod > backup_$(date +%Y%m%d).sql
   ```

2. **VM Template Backups**
   - Regular backups of VM templates
   - Automated snapshot management

## Troubleshooting

Common issues and their solutions:

1. **Database Connection Issues**
   - Check PostgreSQL logs
   - Verify connection strings
   - Ensure proper permissions

2. **VM Management Issues**
   - Check VirtualBox logs
   - Verify VirtualBox permissions
   - Check resource availability

3. **Performance Issues**
   - Monitor system resources
   - Check nginx access logs
   - Review database query performance

## Maintenance

1. **Regular Updates**
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade -y
   
   # Update Python packages
   pip install -r requirements.txt --upgrade
   
   # Run database migrations
   alembic upgrade head
   ```

2. **Health Checks**
   - Monitor system resources
   - Check application logs
   - Review security alerts

## Support

For additional support:
- Create an issue in the GitHub repository
- Contact the development team
- Check the troubleshooting guide

Remember to always test deployment procedures in a staging environment before applying to production.
