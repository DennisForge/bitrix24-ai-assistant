# 🛠️ Installation and Setup Guide

Complete installation and setup guide for Bitrix24 AI Assistant.

## 📋 System Requirements

### **Minimum Requirements**
- **Operating System**: Windows 10+, macOS 12+, or Linux Ubuntu 20.04+
- **Python**: Version 3.8 or newer
- **RAM**: 2GB minimum (4GB recommended)
- **Disk**: 1GB free space
- **Internet**: Stable connection for AI features

### **Recommended**
- **RAM**: 4GB or more
- **CPU**: 2+ cores
- **SSD**: For better performance
- **Docker**: For easier deployment

## 🚀 Method 1: Quick Installation with Docker (Recommended)

### **Step 1: Install Docker**
```bash
# Windows/Mac: Download Docker Desktop from https://docker.com
# Ubuntu:
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER
```

### **Step 2: Clone Repository**
```bash
git clone https://github.com/yourusername/bitrix24-ai-assistant.git
cd bitrix24-ai-assistant
```

### **Step 3: Configure Environment (Optional)**
```bash
# Copy template
cp .env.example .env

# Edit with your API keys (optional for demo)
nano .env
```

### **Step 4: Start Application**
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### **Step 5: Test Installation**
- **Web Interface**: http://localhost:8000/calendar
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

🎉 **Done! Your AI Assistant is ready to use!**

---

## 🐍 Method 2: Local Python Installation

### **Step 1: Check Python Version**
```bash
python --version  # Must be 3.8+
# or
python3 --version
```

### **Step 2: Clone Repository**
```bash
git clone https://github.com/yourusername/bitrix24-ai-assistant.git
cd bitrix24-ai-assistant
```

### **Step 3: Create Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Confirm activation (should see (venv) in terminal)
which python
```

### **Step 4: Install Dependencies**
```bash
# Upgrade pip
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

### **Step 5: Configure Environment**
```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env  # or any text editor
```

### **Step 6: Initialize Database**
```bash
# Database will be automatically created on first run
python -c "
from app.core.database import init_db
import asyncio
asyncio.run(init_db())
print('Database successfully initialized!')
"
```

### **Step 7: Start Application**
```bash
# Start development server
python main.py

# You should see messages like:
# "Starting Bitrix24 AI Assistant..."
# "Application started successfully!"
# "Uvicorn running on http://0.0.0.0:8000"
```

### **Step 8: Test Installation**
- **Web Interface**: http://localhost:8000/calendar
- **API Documentation**: http://localhost:8000/docs

---

## 🔑 Environment Variables Configuration

### **Basic Settings (.env file)**
```env
# Basic environment
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# Database (SQLite for development)
DATABASE_URL=sqlite:///calendar.db

# AI Configuration
OPENAI_API_KEY=your_openai_api_key_here
AI_MODEL=gpt-4
AI_MAX_TOKENS=1000
AI_TEMPERATURE=0.7

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_USE_TLS=True

# Bitrix24 Integration (optional)
BITRIX24_DOMAIN=your_company.bitrix24.com
BITRIX24_API_KEY=your_bitrix24_api_key
BITRIX24_USER_ID=1

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=1
RELOAD=True

# Security
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
ALLOWED_HOSTS=localhost,127.0.0.1

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Scheduler
SCHEDULER_ENABLED=True
NOTIFICATION_INTERVAL=300
```

### **How to Get API Keys**

#### **OpenAI API Key**
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key and add to .env
4. Add credit to account (~$5 is sufficient)

#### **Gmail App Password**
1. Enable 2-factor authentication
2. Go to Google Account Settings
3. Security → App passwords
4. Generate app password
5. Use this password in .env

#### **Bitrix24 API Key**
1. Log into your Bitrix24
2. Applications → Developer resources
3. Other → Inbound webhook
4. Copy webhook URL and API key

---

## 🗄️ Database Configuration

### **SQLite (Default - Development)**
```env
DATABASE_URL=sqlite:///calendar.db
```

### **PostgreSQL (Production)**
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE bitrix24_ai;
CREATE USER bitrix24_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE bitrix24_ai TO bitrix24_user;
\q

# Update .env
DATABASE_URL=postgresql://bitrix24_user:your_password@localhost/bitrix24_ai
```

### **MySQL (Production)**
```bash
# Install MySQL
sudo apt install mysql-server

# Create database
mysql -u root -p
CREATE DATABASE bitrix24_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bitrix24_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON bitrix24_ai.* TO 'bitrix24_user'@'localhost';
FLUSH PRIVILEGES;
exit;

# Update .env
DATABASE_URL=mysql://bitrix24_user:your_password@localhost/bitrix24_ai
```

---

## 🔧 Additional Configuration

### **SSL/HTTPS Configuration**
```bash
# For production with nginx
sudo apt install nginx certbot python3-certbot-nginx

# Configure nginx
sudo nano /etc/nginx/sites-available/bitrix24-ai-assistant

# Content:
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Activate configuration
sudo ln -s /etc/nginx/sites-available/bitrix24-ai-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### **Systemd Service (Linux)**
```bash
# Create service file
sudo nano /etc/systemd/system/bitrix24-ai-assistant.service

# Content:
[Unit]
Description=Bitrix24 AI Assistant
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/bitrix24-ai-assistant
Environment=PATH=/path/to/bitrix24-ai-assistant/venv/bin
ExecStart=/path/to/bitrix24-ai-assistant/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target

# Activate service
sudo systemctl daemon-reload
sudo systemctl enable bitrix24-ai-assistant
sudo systemctl start bitrix24-ai-assistant
```

### **Firewall Configuration**
```bash
# Ubuntu UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# CentOS firewalld
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

---

## 🧪 Installation Verification

### **Basic Tests**
```bash
# Test server health
curl http://localhost:8000/health

# Test API
curl http://localhost:8000/docs

# Test database
curl http://localhost:8000/api/calendar/events

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-07-19T12:00:00Z",
  "database": "connected",
  "ai_service": "ready"
}
```

### **Test AI Functionality**
```bash
# Test AI chat (requires OpenAI API key)
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

### **Test Email Functionality**
```bash
# Test email (requires SMTP configuration)
curl -X POST http://localhost:8000/notifications/test-email \
  -H "Content-Type: application/json"
```

---

## 🛠️ Common Problems and Solutions

### **Problem: Port 8000 is busy**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
HOST=0.0.0.0 PORT=8001 python main.py
```

### **Problem: Python version too low**
```bash
# Ubuntu - install newer Python
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv

# Use specific version
python3.11 -m venv venv
```

### **Problem: Permission denied on Linux**
```bash
# Give permissions
chmod +x main.py

# Or run with python
python main.py
```

### **Problem: Cannot connect to database**
```bash
# SQLite - check permissions
ls -la calendar.db
chmod 664 calendar.db

# PostgreSQL - check connection
pg_isready -h localhost -p 5432
```

### **Problem: OpenAI API errors**
```bash
# Check API key
echo $OPENAI_API_KEY

# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

---

## 📊 Monitoring and Logging

### **Log Files**
```bash
# Create log directory
mkdir logs

# Run with logging
python main.py > logs/app.log 2>&1 &

# Follow logs
tail -f logs/app.log
```

### **Health Monitoring**
```bash
# Automatic health check
#!/bin/bash
while true; do
  if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "$(date): Service is healthy"
  else
    echo "$(date): Service is down! Restarting..."
    systemctl restart bitrix24-ai-assistant
  fi
  sleep 60
done
```

---

## 🚀 Finalization

### **Production Checklist**
- [ ] Environment variables configured
- [ ] Production database set up
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Backup strategy implemented
- [ ] Monitoring set up
- [ ] Documentation updated

### **Testing Before Production**
```bash
# Run all tests
python -m pytest tests/

# Performance test
ab -n 100 -c 10 http://localhost:8000/

# Security scan
bandit -r app/
```

### **Backup Strategy**
```bash
# Database backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# SQLite backup
cp calendar.db $BACKUP_DIR/calendar_$DATE.db

# PostgreSQL backup
pg_dump bitrix24_ai > $BACKUP_DIR/bitrix24_ai_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

---

## 🎉 Congratulations!

Your Bitrix24 AI Assistant has been successfully installed and configured! 🚀

### **Next Steps:**
1. **Test basic functionality**
2. **Add team members**
3. **Configure AI API key for full functionality**
4. **Set up backup routine**
5. **Start using AI commands!**

### **First AI Command for Testing:**
```
"Add meeting tomorrow at 2pm with development team"
```

**Need help?** Check the [FAQ](FAQ_EN.md) or [User Guide](USER_GUIDE.md).

---

*Last updated: July 19, 2025.*