# Installation and Setup Guide

This guide will help you set up and configure the Bitrix24 AI Assistant application.

## Prerequisites

Before installing the application, ensure you have the following:

- **Python 3.8 or higher**
- **PostgreSQL 12 or higher** (or MySQL 8.0+)
- **Redis 6.0 or higher**
- **Bitrix24 CRM account** with API access
- **OpenAI API key** (optional, for AI features)
- **Email server access** (SMTP)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bitrix24-ai-assistant.git
cd bitrix24-ai-assistant
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### PostgreSQL Setup

1. Create a new database:
```sql
CREATE DATABASE bitrix24_ai_assistant;
CREATE USER bitrix24_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE bitrix24_ai_assistant TO bitrix24_user;
```

2. Update the database URL in your `.env` file:
```
DATABASE_URL=postgresql://bitrix24_user:your_password@localhost:5432/bitrix24_ai_assistant
```

#### MySQL Setup (Alternative)

1. Create a new database:
```sql
CREATE DATABASE bitrix24_ai_assistant;
CREATE USER 'bitrix24_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON bitrix24_ai_assistant.* TO 'bitrix24_user'@'localhost';
```

2. Update the database URL in your `.env` file:
```
DATABASE_URL=mysql://bitrix24_user:your_password@localhost:3306/bitrix24_ai_assistant
```

### 5. Redis Setup

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS
```bash
brew install redis
brew services start redis
```

#### Windows
Download and install Redis from the official website or use WSL.

### 6. Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your configuration:

```env
# Application Settings
APP_NAME=Bitrix24 AI Assistant
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=False

# Database Configuration
DATABASE_URL=postgresql://bitrix24_user:your_password@localhost:5432/bitrix24_ai_assistant

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Bitrix24 API Configuration
BITRIX24_WEBHOOK_URL=https://your-domain.bitrix24.com/rest/1/your-webhook-key/
BITRIX24_DOMAIN=your-domain.bitrix24.com

# OpenAI Configuration (Optional)
OPENAI_API_KEY=your-openai-api-key

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com

# Security Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
```

### 7. Bitrix24 Configuration

#### Option 1: Using Webhook (Recommended)

1. Go to your Bitrix24 account
2. Navigate to **Settings** → **Developer resources** → **Other**
3. Click **Inbound webhook**
4. Select required permissions:
   - CRM
   - Calendar
   - Tasks
   - Users
5. Copy the webhook URL and paste it in your `.env` file

#### Option 2: Using OAuth App

1. Go to your Bitrix24 account
2. Navigate to **Settings** → **Developer resources** → **Other**
3. Click **OAuth application**
4. Create a new application with:
   - Name: Bitrix24 AI Assistant
   - Handler URL: `http://your-domain.com/api/v1/auth/bitrix24/callback`
   - Permissions: crm,calendar,tasks,user
5. Copy the Client ID and Client Secret to your `.env` file

### 8. Initialize Database

```bash
python main.py --init-db
```

### 9. Start the Application

#### Development Mode
```bash
python main.py --reload
```

#### Production Mode
```bash
python main.py
```

The application will be available at `http://localhost:8000`

## Email Configuration

### Gmail Setup

1. Enable 2-factor authentication in your Google account
2. Generate an app password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
3. Use the app password in your `.env` file

### Other Email Providers

#### Outlook/Hotmail
```env
EMAIL_HOST=smtp.live.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

#### Yahoo
```env
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

#### Custom SMTP
```env
EMAIL_HOST=your-smtp-server.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USERNAME=your-username
EMAIL_PASSWORD=your-password
```

## Docker Setup (Optional)

### Using Docker Compose

1. Create a `docker-compose.yml` file:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://bitrix24_user:password@db:5432/bitrix24_ai_assistant
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=bitrix24_ai_assistant
      - POSTGRES_USER=bitrix24_user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

2. Start the services:
```bash
docker-compose up -d
```

### Using Docker

1. Build the image:
```bash
docker build -t bitrix24-ai-assistant .
```

2. Run the container:
```bash
docker run -p 8000:8000 --env-file .env bitrix24-ai-assistant
```

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `APP_NAME` | Application name | No | Bitrix24 AI Assistant |
| `APP_HOST` | Host to bind to | No | 0.0.0.0 |
| `APP_PORT` | Port to bind to | No | 8000 |
| `APP_DEBUG` | Debug mode | No | False |
| `DATABASE_URL` | Database connection URL | Yes | - |
| `REDIS_URL` | Redis connection URL | No | redis://localhost:6379/0 |
| `BITRIX24_WEBHOOK_URL` | Bitrix24 webhook URL | Yes | - |
| `BITRIX24_DOMAIN` | Bitrix24 domain | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key | No | - |
| `EMAIL_HOST` | SMTP host | Yes | - |
| `EMAIL_PORT` | SMTP port | Yes | - |
| `EMAIL_USERNAME` | SMTP username | Yes | - |
| `EMAIL_PASSWORD` | SMTP password | Yes | - |
| `SECRET_KEY` | Secret key for JWT | Yes | - |

## Troubleshooting

### Common Issues

#### Database Connection Issues
- Check database credentials
- Ensure database server is running
- Verify network connectivity
- Check firewall settings

#### Redis Connection Issues
- Ensure Redis server is running
- Check Redis configuration
- Verify Redis URL format

#### Bitrix24 API Issues
- Verify webhook URL format
- Check API permissions
- Ensure webhook is active
- Test API connectivity

#### Email Issues
- Check SMTP credentials
- Verify email server settings
- Check firewall/security settings
- Test email connectivity

### Logs

Application logs are stored in the `logs/` directory. Check these files for detailed error information:

- `app.log` - Application logs
- `error.log` - Error logs
- `access.log` - Access logs

### Debug Mode

Enable debug mode for detailed error messages:

```env
APP_DEBUG=True
LOG_LEVEL=DEBUG
```

## Next Steps

1. **Configure Bitrix24 Integration**: Set up webhook or OAuth app
2. **Test API Endpoints**: Use the API documentation at `/docs`
3. **Set Up Monitoring**: Configure logging and monitoring
4. **Deploy to Production**: Follow the deployment guide
5. **Configure Backups**: Set up database and file backups

For more information, see:
- [API Documentation](API.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Configuration Guide](CONFIGURATION.md)
- [FAQ](FAQ.md)
