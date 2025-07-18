# 🚀 Deployment Guide

Complete deployment guide for Bitrix24 AI Assistant across different environments.

## 🏠 Local Development

### **Quick Start**
```bash
# Clone and setup
git clone https://github.com/yourusername/bitrix24-ai-assistant.git
cd bitrix24-ai-assistant

# Environment setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run development server
python main.py
```

### **Development Configuration**
```env
# .env for development
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=sqlite:///calendar.db
OPENAI_API_KEY=your_openai_key_here
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## 🐳 Docker Deployment

### **Local Docker**
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### **Production Docker**
```bash
# Build production image
docker build -t bitrix24-ai-assistant:latest .

# Run with production settings
docker run -d \
  --name bitrix24-ai-assistant \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DATABASE_URL=postgresql://user:pass@db:5432/bitrix24 \
  -e OPENAI_API_KEY=your_real_key \
  -v /app/data:/app/data \
  bitrix24-ai-assistant:latest
```

### **docker-compose.yml for Production**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/bitrix24
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=bitrix24
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:
```

## ☁️ Cloud Deployment

### **AWS ECS**
```bash
# Create ECR repository
aws ecr create-repository --repository-name bitrix24-ai-assistant

# Build and push image
docker build -t bitrix24-ai-assistant .
docker tag bitrix24-ai-assistant:latest YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/bitrix24-ai-assistant:latest
docker push YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/bitrix24-ai-assistant:latest

# Deploy with ECS Task Definition
aws ecs create-service --cluster production --service-name bitrix24-ai-assistant \
  --task-definition bitrix24-ai-assistant --desired-count 2
```

### **Google Cloud Run**
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/bitrix24-ai-assistant

# Deploy to Cloud Run
gcloud run deploy bitrix24-ai-assistant \
  --image gcr.io/PROJECT_ID/bitrix24-ai-assistant \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production,OPENAI_API_KEY=your_key
```

### **Azure Container Instances**
```bash
# Create resource group
az group create --name bitrix24-rg --location eastus

# Deploy container
az container create \
  --resource-group bitrix24-rg \
  --name bitrix24-ai-assistant \
  --image yourusername/bitrix24-ai-assistant:latest \
  --port 8000 \
  --dns-name-label bitrix24-ai-assistant \
  --environment-variables ENVIRONMENT=production OPENAI_API_KEY=your_key
```

### **Heroku**
```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create bitrix24-ai-assistant

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set ENVIRONMENT=production
heroku config:set OPENAI_API_KEY=your_key

# Deploy
git push heroku main
```

## 🔧 Production Configuration

### **Environment Variables**
```env
# Production .env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your_long_random_secret_key_here
DATABASE_URL=postgresql://user:password@host:5432/database
REDIS_URL=redis://host:6379/0

# API Keys
OPENAI_API_KEY=sk-proj-your-real-openai-key
BITRIX24_DOMAIN=your-company.bitrix24.com
BITRIX24_API_KEY=your_bitrix24_api_key

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=True

# Security
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Performance
WORKERS=4
MAX_REQUESTS=1000
TIMEOUT=30
```

### **Database Migration**
```bash
# For PostgreSQL production
pip install psycopg2-binary

# Create tables
python -c "
from app.core.database import init_db
import asyncio
asyncio.run(init_db())
"

# Or use migration scripts
python migrate.py
```

## 🔒 Security Hardening

### **SSL/TLS Certificate**
```bash
# Using Let's Encrypt with Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **Nginx Configuration**
```nginx
# /etc/nginx/sites-available/bitrix24-ai-assistant
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    client_max_body_size 20M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **Firewall Configuration**
```bash
# UFW firewall setup
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Fail2ban for SSH protection
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
```

## 📊 Monitoring & Logging

### **Application Logs**
```bash
# View logs
docker-compose logs -f app

# Log rotation
echo "
/var/log/bitrix24-ai-assistant/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 www-data www-data
}
" | sudo tee /etc/logrotate.d/bitrix24-ai-assistant
```

### **Health Checks**
```bash
# Health check endpoint
curl -f http://localhost:8000/health || exit 1

# Database health
curl -f http://localhost:8000/health/database || exit 1

# AI service health
curl -f http://localhost:8000/health/ai || exit 1
```

### **Monitoring with Prometheus**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'bitrix24-ai-assistant'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
```

## 🔄 Backup & Recovery

### **Database Backup**
```bash
# PostgreSQL backup
pg_dump -h localhost -U postgres bitrix24 > backup_$(date +%Y%m%d).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U postgres bitrix24 > $BACKUP_DIR/bitrix24_$DATE.sql
find $BACKUP_DIR -type f -name "*.sql" -mtime +7 -delete
```

### **File Backup**
```bash
# Backup uploaded files and configurations
tar -czf backup_files_$(date +%Y%m%d).tar.gz \
  /app/data \
  /app/.env \
  /app/static/uploads
```

## 🚀 Performance Optimization

### **Caching**
```python
# Redis caching configuration
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600
CACHE_KEY_PREFIX=bitrix24_ai_
```

### **Database Optimization**
```sql
-- Create indexes for better performance
CREATE INDEX idx_calendar_events_start_datetime ON calendar_events(start_datetime);
CREATE INDEX idx_calendar_events_user_id ON calendar_events(user_id);
CREATE INDEX idx_calendar_events_created_by_ai ON calendar_events(created_by_ai);
```

### **Load Balancing**
```nginx
# Nginx load balancer
upstream bitrix24_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location / {
        proxy_pass http://bitrix24_backend;
    }
}
```

## 🔧 Troubleshooting

### **Common Issues**

**Issue**: Database connection errors
```bash
# Check database status
docker-compose exec db psql -U postgres -d bitrix24 -c "SELECT 1;"

# Reset database
docker-compose down -v
docker-compose up -d
```

**Issue**: AI not responding
```bash
# Check OpenAI API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Check API quota
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/dashboard/billing/usage
```

**Issue**: High memory usage
```bash
# Check container stats
docker stats bitrix24-ai-assistant

# Adjust memory limits
docker run -m 512m bitrix24-ai-assistant
```

## 📋 Deployment Checklist

### **Pre-deployment**
- [ ] Environment variables configured
- [ ] Database migration completed
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Monitoring setup
- [ ] Backup strategy implemented

### **Post-deployment**
- [ ] Health checks passing
- [ ] AI functionality tested
- [ ] Email notifications working
- [ ] Performance metrics collected
- [ ] Security scan completed
- [ ] Documentation updated

---

## 🏆 Production Ready

Your Bitrix24 AI Assistant is now production-ready with:
- ✅ Secure SSL/TLS encryption
- ✅ Database backup strategy
- ✅ Monitoring and logging
- ✅ Performance optimization
- ✅ Security hardening
- ✅ Scalable architecture

For enterprise deployment support, contact: support@technosoft.dev

---

*Last updated: July 19, 2025*