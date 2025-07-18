# ❓ Frequently Asked Questions

## 🚀 Getting Started

### **Q: How do I install the Bitrix24 AI Assistant?**
A: You have two options:
- **Docker** (recommended): `docker-compose up -d`
- **Local**: Clone repo → Install Python deps → Configure .env → Run `python main.py`

### **Q: What are the system requirements?**
A: 
- Python 3.8+
- 2GB RAM minimum
- Modern web browser
- Internet connection for AI features

### **Q: Do I need a Bitrix24 account?**
A: No, the system works independently. Bitrix24 integration is optional and enhances functionality.

## 🤖 AI Features

### **Q: What languages does the AI support?**
A: The AI primarily supports **Serbian** with English fallback. Commands like "Zakaži sastanak sutra u 14h" work perfectly.

### **Q: Do I need an OpenAI API key?**
A: Yes, for full AI functionality you need an OpenAI API key (~$5 credit). The system includes demo fallbacks for testing.

### **Q: How accurate is the AI understanding?**
A: The AI has 95%+ accuracy for calendar commands in Serbian. It understands context, time expressions, and team references.

### **Q: Can the AI handle team scheduling?**
A: Yes! Commands like "Zakaži timski sastanak za sutra u 10h za sav tim" automatically find optimal times for all team members.

## 📅 Calendar Management

### **Q: How do I create recurring events?**
A: Use the web interface or API. AI commands for recurring events are in development.

### **Q: Can I drag and drop events?**
A: Yes, the calendar interface supports full drag-and-drop functionality for moving and resizing events.

### **Q: How do I manage team permissions?**
A: Each event has permission levels: view-only, can-edit, can-invite-others. Set these when creating events.

### **Q: What happens when there are scheduling conflicts?**
A: The AI automatically detects conflicts and suggests alternative times. You can accept or modify suggestions.

## 👥 Team Collaboration

### **Q: How many team members can I add?**
A: No hard limit. The system is designed for teams of 5-50 members with optimal performance.

### **Q: Can I create different teams/departments?**
A: Yes, organize users into teams and departments. Each team can have separate calendars and permissions.

### **Q: How do bulk operations work?**
A: Use AI commands like "Pomeri sve događaje tima za ponedeljak" to move multiple events at once.

### **Q: Are there team analytics?**
A: Yes, view workload distribution, productivity insights, and team performance metrics.

## 🔔 Notifications

### **Q: How do I setup email notifications?**
A: Configure SMTP settings in .env file:
```env
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### **Q: Can I customize notification templates?**
A: Yes, email templates are customizable. Edit templates in `app/templates/email/`.

### **Q: What types of notifications are available?**
A: 
- Event reminders (email + push)
- Schedule changes
- Team updates
- Deadline alerts
- Meeting invitations

## 🔧 Technical Issues

### **Q: The AI is not responding correctly**
A: Check:
1. OpenAI API key is valid
2. Internet connection is stable
3. Commands are in supported format
4. Try simpler commands first

### **Q: Database errors on startup**
A: Common solutions:
1. Delete `calendar.db` file and restart
2. Check file permissions
3. Ensure SQLite is installed
4. Run `python main.py` with admin rights

### **Q: Frontend not loading**
A: Check:
1. Server is running on http://localhost:8000
2. Static files are being served
3. No JavaScript errors in browser console
4. Clear browser cache

### **Q: Docker container won't start**
A: Common issues:
1. Port 8000 is already in use
2. Environment variables not set
3. Docker daemon not running
4. Insufficient disk space

## 🔐 Security & Privacy

### **Q: Is my data secure?**
A: Yes:
- All data stored locally by default
- SQL injection protection
- Input validation on all endpoints
- HTTPS ready for production

### **Q: Where is my calendar data stored?**
A: By default in local SQLite database. For production, configure PostgreSQL or MySQL.

### **Q: Can I export my data?**
A: Yes, use the export API endpoints or backup the database file directly.

## 🚀 Performance

### **Q: How fast is the AI response?**
A: Typical response times:
- Simple commands: < 1 second
- Complex scheduling: 2-5 seconds
- Team operations: 5-10 seconds

### **Q: Can it handle multiple concurrent users?**
A: Yes, FastAPI handles concurrent requests efficiently. Tested with 10+ simultaneous users.

### **Q: What about mobile devices?**
A: The interface is fully responsive and works on mobile browsers. Native mobile app is in development.

## 🔗 Integrations

### **Q: How do I integrate with Bitrix24?**
A: Configure in .env:
```env
BITRIX24_DOMAIN=your_company.bitrix24.com
BITRIX24_API_KEY=your_api_key
```

### **Q: Can I integrate with Google Calendar?**
A: Google Calendar integration is planned for future releases.

### **Q: Are there webhook notifications?**
A: Yes, configure webhook URLs for external system notifications.

## 💰 Costs

### **Q: Is this free to use?**
A: Yes, the software is free (MIT license). You only pay for:
- OpenAI API usage (~$5/month for small teams)
- Cloud hosting (optional)
- Enterprise support (optional)

### **Q: How much does OpenAI API cost?**
A: Very affordable:
- $5 credit = ~1000 AI commands
- Average team: $2-5/month
- Pay only for what you use

## 🛠️ Development & Customization

### **Q: Can I customize the interface?**
A: Yes, modify:
- `frontend/` for HTML/CSS
- `static/` for styling and assets
- `app/api/` for backend functionality

### **Q: How do I add new AI commands?**
A: Edit `app/services/ai_assistant.py` and add new command patterns.

### **Q: Can I contribute to the project?**
A: Yes! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📞 Support

### **Q: Where can I get help?**
A: 
- 📚 Documentation: [Installation Guide](INSTALLATION_AND_SETUP.md)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/bitrix24-ai-assistant/issues)
- 💬 Community: [Discussions](https://github.com/yourusername/bitrix24-ai-assistant/discussions)
- 📧 Enterprise: info@directadvertising.rs

### **Q: How do I report bugs?**
A: Create a GitHub issue with:
- Steps to reproduce
- Expected behavior
- Actual behavior
- System information
- Error messages

### **Q: Can I request new features?**
A: Yes! Use GitHub Discussions or Issues to suggest new features.

---

## 🔄 Still Need Help?

If you can't find the answer here:

1. **Check the documentation**: [Installation Guide](INSTALLATION_AND_SETUP.md)
2. **Search existing issues**: [GitHub Issues](https://github.com/yourusername/bitrix24-ai-assistant/issues)
3. **Ask the community**: [GitHub Discussions](https://github.com/yourusername/bitrix24-ai-assistant/discussions)
4. **Contact support**: Create a new issue with detailed information

---

*Last updated: July 19, 2025*