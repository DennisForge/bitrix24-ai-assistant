# Contributing to Bitrix24 AI Assistant

We love your input! We want to make contributing to this project as easy and transparent as possible.

## 🚀 Quick Start for Contributors

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔧 Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/bitrix24-ai-assistant.git
cd bitrix24-ai-assistant

# Set up development environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Start development server
python main.py
```

## 📋 Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the version numbers in any examples files and the README.md
3. Ensure all tests pass
4. Make sure your code follows the project's coding standards
5. Update documentation if needed

## 🎯 Types of Contributions

### **Bug Reports**
- Use the GitHub issue tracker
- Include steps to reproduce
- Include expected vs actual behavior
- Include system information

### **Feature Requests**
- Use GitHub Discussions for new ideas
- Explain the problem you're solving
- Provide examples of desired behavior

### **Code Contributions**
- Follow Python PEP 8 style guide
- Write tests for new functionality
- Update documentation
- Keep pull requests focused and small

## 🔍 Code Review Process

1. All submissions require review
2. We use GitHub pull requests for this process
3. Core team will review and provide feedback
4. Changes may be requested before merging

## 📝 Coding Standards

### **Python Code**
```python
# Use type hints
def create_event(title: str, start: datetime) -> Event:
    pass

# Use docstrings
def process_ai_command(command: str) -> dict:
    """Process AI command and return response.
    
    Args:
        command: Natural language command in Serbian
        
    Returns:
        Dictionary with response and actions
    """
    pass
```

### **Commit Messages**
```
feat: add Serbian language support for AI commands
fix: resolve calendar timezone issues
docs: update installation guide
test: add unit tests for AI service
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test file
python -m pytest tests/test_ai_service.py
```

## 📚 Documentation

- Keep README.md updated
- Update API documentation
- Add examples for new features
- Translate important docs to Serbian

## 🔐 Security

- Never commit secrets or API keys
- Report security vulnerabilities privately
- Follow security best practices

## 🏷️ Versioning

We use [SemVer](http://semver.org/) for versioning:
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

## 📞 Community

- 💬 [GitHub Discussions](https://github.com/yourusername/bitrix24-ai-assistant/discussions)
- 🐛 [Issues](https://github.com/yourusername/bitrix24-ai-assistant/issues)
- 📧 [Email](mailto:support@technosoft.dev)

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing! 🚀
