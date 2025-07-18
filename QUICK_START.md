# ⚡ Quick Start Guide

Get your Bitrix24 AI Assistant up and running in under 5 minutes!

## 🚀 Option 1: Docker (Recommended)

### **Step 1: Prerequisites**
```bash
# Ensure you have Docker installed
docker --version
docker-compose --version
```

### **Step 2: Clone & Start**
```bash
# Clone the repository
git clone https://github.com/yourusername/bitrix24-ai-assistant.git
cd bitrix24-ai-assistant

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### **Step 3: Access the Application**
- **Web Interface**: http://localhost:8000/calendar
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

🎉 **That's it! Your AI Assistant is running!**

---

## 🐍 Option 2: Local Python Setup

### **Step 1: Clone Repository**
```bash
git clone https://github.com/yourusername/bitrix24-ai-assistant.git
cd bitrix24-ai-assistant
```

### **Step 2: Environment Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 4: Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit .env file (optional for demo)
nano .env  # or use your favorite editor
```

### **Step 5: Run Application**
```bash
python main.py
```

### **Step 6: Access Application**
- **Web Interface**: http://localhost:8000/calendar
- **API Documentation**: http://localhost:8000/docs

---

## 🎯 First Steps

### **1. Create Your First Event**
1. Open http://localhost:8000/calendar
2. Click anywhere on the calendar
3. Fill in event details
4. Click "Save Event"

### **2. Try AI Commands**
1. Click "AI Assistant" button
2. Type: `"Dodaj sastanak sutra u 14h"`
3. Watch the AI create the event automatically!

### **3. Test Team Features**
1. Click "Team AI" button
2. Type: `"Zakaži timski sastanak za ponedeljak u 10h"`
3. See the AI coordinate team scheduling

---

## 🔑 Configuration (Optional)

### **Basic Configuration**
The system works out-of-the-box with demo settings. For full functionality, configure:

```env
# .env file
OPENAI_API_KEY=your_openai_key_here
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### **Get OpenAI API Key**
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Add $5 credit to your account
4. Add key to .env file

### **Email Notifications**
1. Enable 2-factor authentication in Gmail
2. Generate App Password
3. Add credentials to .env file

---

## 🧪 Test Features

### **Calendar Features**
- ✅ Create events by clicking calendar
- ✅ Drag & drop to move events
- ✅ Resize events to change duration
- ✅ Switch between month/week/day views
- ✅ Search and filter events

### **AI Features (Serbian)**
```
Try these commands:
"Dodaj sastanak sutra u 14h"
"Pomeri moj sastanak za ponedeljak"
"Pronađi mi slobodan termin za 2 sata"
"Zakaži timski sastanak za sledeću nedelju"
```

### **Team Features**
- ✅ Multi-user calendar views
- ✅ Team member selection
- ✅ Bulk operations
- ✅ Conflict detection
- ✅ Smart scheduling

---

## 🎨 Interface Overview

### **Calendar View**
- **Monthly View**: Overview of entire month
- **Weekly View**: Detailed week schedule
- **Daily View**: Hour-by-hour day planning
- **List View**: Event list with search

### **AI Assistant Panel**
- **Individual Chat**: Personal AI commands
- **Team Chat**: Group coordination
- **Smart Suggestions**: AI recommendations
- **Command History**: Previous interactions

### **Event Management**
- **Quick Create**: Click calendar to create
- **Detailed Form**: Full event information
- **Team Invites**: Multi-user events
- **Reminders**: Notification settings

---

## 🔍 Verify Installation

### **Health Checks**
```bash
# Check if server is running
curl http://localhost:8000/health

# Check database connection
curl http://localhost:8000/health/database

# Check AI service (requires OpenAI key)
curl http://localhost:8000/health/ai
```

### **Expected Responses**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-19T12:00:00Z",
  "version": "1.0.0"
}
```

---

## 🛠️ Common Issues & Solutions

### **Issue: Port 8000 already in use**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
docker-compose up -d --env PORT=8001
```

### **Issue: Docker not starting**
```bash
# Check Docker daemon
docker info

# Restart Docker service
sudo systemctl restart docker  # Linux
# or restart Docker Desktop
```

### **Issue: AI not responding**
```bash
# Check OpenAI API key
echo $OPENAI_API_KEY

# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

### **Issue: Database errors**
```bash
# Reset database
rm calendar.db  # Local setup
# or
docker-compose down -v && docker-compose up -d  # Docker
```

---

## 📚 Next Steps

### **Learn More**
- 📖 [Full Documentation](README.md)
- 🤖 [AI Commands Reference](COMMANDS_EN.md)
- 🚀 [Deployment Guide](DEPLOYMENT.md)
- ❓ [FAQ](FAQ_EN.md)

### **Customize Your Setup**
- 🎨 Modify UI in `frontend/` directory
- 🔧 Configure settings in `.env` file
- 📊 Set up monitoring and logging
- 🔐 Enable SSL for production

### **Get Support**
- 🐛 [Report Issues](https://github.com/yourusername/bitrix24-ai-assistant/issues)
- 💬 [Join Discussions](https://github.com/yourusername/bitrix24-ai-assistant/discussions)
- 📧 [Enterprise Support](mailto:info@directadvertising.rs)

---

## 🏆 Success!

Your Bitrix24 AI Assistant is now running! 🎉

**Key URLs:**
- 🗓️ **Calendar**: http://localhost:8000/calendar
- 📚 **API Docs**: http://localhost:8000/docs
- 🏥 **Health**: http://localhost:8000/health

**Try your first AI command:**
```
"Dodaj sastanak sutra u 14h sa timom"
```

**Happy scheduling!** 🚀

---

*Need help? Check our [FAQ](FAQ_EN.md) or [create an issue](https://github.com/yourusername/bitrix24-ai-assistant/issues).*