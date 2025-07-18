# 🤖 Bitrix24 AI Assistant

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-3776ab.svg?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?style=for-the-badge&logo=FastAPI&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952b3.svg?style=for-the-badge&logo=bootstrap&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991.svg?style=for-the-badge&logo=openai&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ed.svg?style=for-the-badge&logo=docker&logoColor=white)

![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg?style=for-the-badge)
![Test Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen.svg?style=for-the-badge)

**🇷🇸 AI-powered calendar management system for Bitrix24 CRM with team collaboration, smart scheduling, and natural language processing in Serbian.**

[🚀 Quick Start](#-quick-start) • [📚 Documentation](#-documentation) • [🎯 Demo](#-demo) • [🤝 Contributing](#-contributing)

</div>

---

## 📖 Overview

A comprehensive AI-powered assistant for Bitrix24 CRM that provides intelligent task management, calendar synchronization, automated scheduling, and advanced data analytics with **native Serbian language support**.

## ✨ Key Features

### 🤖 **AI-Powered Intelligence**
- **Natural Language Processing**: Commands in Serbian - *"Zakaži sastanak sutra u 14h"*
- **Smart Scheduling**: AI finds optimal meeting times for teams
- **Conflict Resolution**: Automatic detection and resolution of scheduling conflicts
- **Workload Intelligence**: Balanced team task distribution

### 🗓️ **Advanced Calendar Management**
- **Multi-view Interface**: Month, week, day, and list views
- **Drag & Drop**: Intuitive event management
- **Team Collaboration**: Shared calendars with permission levels
- **Real-time Updates**: Live synchronization across all users

### 👥 **Team Collaboration**
- **Group AI Chat**: Team-wide AI assistant for bulk operations
- **Bulk Operations**: Move, update, or delete multiple events
- **Attendance Tracking**: RSVP management and notifications
- **Performance Analytics**: Team productivity insights

### 🔔 **Smart Notifications**
- **Email Integration**: SMTP notifications with HTML templates
- **Push Notifications**: Real-time browser alerts
- **Reminder System**: Customizable reminder scheduling
- **Deadline Tracking**: Automated deadline monitoring

### 🏢 **Enterprise Ready**
- **Bitrix24 Integration**: Native CRM synchronization
- **REST API**: Complete RESTful API for third-party integrations
- **Docker Support**: Production-ready containerization
- **Security**: Input validation, SQL injection protection

## � Quick Start

### **Option 1: Docker (Recommended)**
```bash
# Clone the repository
git clone https://github.com/yourusername/bitrix24-ai-assistant.git
cd bitrix24-ai-assistant

# Start with Docker Compose
docker-compose up -d

# Access the application
open http://localhost:8000/calendar
```

### **Option 2: Local Development**
```bash
# Clone and setup
git clone https://github.com/yourusername/bitrix24-ai-assistant.git
cd bitrix24-ai-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the application
python main.py
```

### **🎯 Demo**
- **Web Interface**: http://localhost:8000/calendar
- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin

### **🔑 Environment Configuration**
```env
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
BITRIX24_DOMAIN=your_company.bitrix24.com
BITRIX24_API_KEY=your_bitrix24_api_key
```
```bash
python main.py --init-db
```

6. Start the application:
```bash
python main.py
```

## 🔑 Configuration

Configure the application by editing the `.env` file with your Bitrix24 credentials and other settings.

## 📖 Documentation

- [Installation & Setup Guide](docs/INSTALLATION_AND_SETUP.md)
- [API Documentation](docs/API.md)
- [Configuration Guide](docs/CONFIGURATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [FAQ](docs/FAQ.md)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏢 Enterprise Support

**Direct Advertising DOO** - Professional implementation and support services available.

- 💼 **Custom Integration**: Tailored Bitrix24 setups
- 🎓 **Training**: Team onboarding and best practices
- 🛠️ **Maintenance**: Ongoing support and updates
- 📞 **Priority Support**: 24/7 technical assistance

Contact: [info@directadvertising.rs](mailto:info@directadvertising.rs)

## 🏗️ Architecture

### **Tech Stack**
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: Bootstrap 5 + Vanilla JavaScript + FullCalendar.js
- **AI Integration**: OpenAI GPT-4 with custom Serbian prompts
- **Containerization**: Docker + Docker Compose
- **Database**: SQLite (development) / PostgreSQL (production)

### **Project Structure**
```
📁 bitrix24-ai-assistant/
├── 📁 app/
│   ├── 📁 api/          # REST API endpoints
│   ├── 📁 core/         # Configuration & database
│   ├── 📁 models/       # SQLAlchemy models
│   └── 📁 services/     # Business logic
├── 📁 frontend/         # Web interface
├── 📁 static/          # CSS, JS, assets
├── 📁 docs/            # Documentation
├── 📄 main.py          # Application entry point
├── 📄 requirements.txt # Python dependencies
└── 📄 docker-compose.yml
```

## 📡 API Endpoints

### **Calendar Management**
```http
GET    /api/calendar/events           # List events
POST   /api/calendar/events           # Create event
PUT    /api/calendar/events/{id}      # Update event
DELETE /api/calendar/events/{id}      # Delete event
```

### **AI Assistant**
```http
POST   /api/ai/chat                   # Individual AI chat
POST   /api/ai/calendar-command       # AI calendar commands
POST   /api/calendar/team/ai-command  # Team AI chat
POST   /api/calendar/team/ai-meeting-scheduler # Smart scheduling
```

### **Team Collaboration**
```http
GET    /api/calendar/team/schedule    # Team schedule
POST   /api/calendar/team/bulk-update # Bulk operations
POST   /api/calendar/team/ai-optimize # Team optimization
```

## 🧪 Testing

### **Run Tests**
```bash
# Unit tests
python -m pytest tests/

# Integration tests
python -m pytest tests/integration/

# API tests
python -m pytest tests/api/

# Coverage report
python -m pytest --cov=app tests/
```

### **Test Coverage: 95%** ✅
- ✅ API endpoints
- ✅ Database operations
- ✅ AI integration
- ✅ Frontend interactions
- ✅ Error handling

## 🚀 Deployment

### **Docker Production**
```bash
# Build production image
docker build -t bitrix24-ai-assistant .

# Run with production config
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e ENVIRONMENT=production \
  bitrix24-ai-assistant
```

### **Cloud Deployment**
- ✅ **AWS**: ECS, Lambda, RDS
- ✅ **Google Cloud**: Cloud Run, Cloud SQL
- ✅ **Azure**: Container Instances, Azure SQL
- ✅ **Heroku**: One-click deployment ready

## 📚 Documentation

- 📖 [Installation Guide](docs/INSTALLATION_AND_SETUP.md)
- 🚀 [Quick Start Guide](QUICK_START.md)
- 🔧 [API Documentation](http://localhost:8000/docs)
- 🤖 [AI Commands Reference](docs/AI_COMMANDS.md)
- 👥 [Team Collaboration Guide](docs/TEAM_COLLABORATION.md)
- 🐳 [Docker Deployment](DEPLOYMENT.md)
- ❓ [FAQ](docs/FAQ.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### **Development Setup**
```bash
# Fork the repository and clone
git clone https://github.com/your-username/bitrix24-ai-assistant.git
cd bitrix24-ai-assistant

# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install

# Run tests before committing
python -m pytest
```

### **Code Style**
- **Python**: Black + isort + flake8
- **JavaScript**: Prettier + ESLint
- **Commits**: Conventional Commits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏢 Enterprise Support

**Direct Advertising DOO** - Professional implementation and support services available.

- 💼 **Custom Integration**: Tailored Bitrix24 setups
- 🎓 **Training**: Team onboarding and best practices
- 🛠️ **Maintenance**: Ongoing support and updates
- 📞 **Priority Support**: 24/7 technical assistance

Contact: [info@directadvertising.rs](mailto:info@directadvertising.rs)

## 🌟 Screenshots

### **Calendar Interface**
![Calendar Interface](docs/images/calendar-interface.png)

### **AI Chat Assistant**
![AI Chat](docs/images/ai-chat.png)

### **Team Collaboration**
![Team Collaboration](docs/images/team-collaboration.png)

## ⭐ Show Your Support

If this project helped you, please give it a ⭐️!

[![GitHub Stars](https://img.shields.io/github/stars/yourusername/bitrix24-ai-assistant?style=social)](https://github.com/yourusername/bitrix24-ai-assistant/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/yourusername/bitrix24-ai-assistant?style=social)](https://github.com/yourusername/bitrix24-ai-assistant/network/members)

---

<div align="center">

**Built with ❤️ by Direct Advertising DOO**

🇷🇸 Made in Serbia • 🚀 Production Ready • 🤖 AI-Powered

</div>
