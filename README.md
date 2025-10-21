 # 🤖 AI Agent Workflow System

A comprehensive AI-powered workflow system that automates CRM operations using LangGraph, Google Gemini AI, and HubSpot integration. This system can parse natural language requests and automatically create contacts, deals, and send email notifications.

## ✨ Features

- **Natural Language Processing**: Parse user requests in plain English
- **CRM Integration**: Automatically create contacts and deals in HubSpot
- **Email Notifications**: Send automated notifications for all operations
- **Workflow Orchestration**: Powered by LangGraph for complex workflow management
- **Error Handling**: Comprehensive error handling and notifications
- **Testing Suite**: Complete test coverage for all components
- **CLI Interface**: Easy-to-use command-line interface

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google Gemini API key
- HubSpot account with API access
- Gmail account with App Password (for email notifications)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ai-agent-workflow
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API credentials**
   
   **Option A: Quick Setup (Recommended)**
   ```bash
   python setup_env.py
   ```
   
   **Option B: Manual Setup**
   
   Create a `.env` file in the project root:
   ```bash
   # Copy the example file
   cp env.example .env
   
   # Edit .env with your credentials
   nano .env  # or use your preferred editor
   ```
   
   Your `.env` file should contain:
   ```
   GEMINI_API_KEY=your-gemini-api-key-here
   HUBSPOT_API_KEY=your-hubspot-api-key-here
   EMAIL_USERNAME=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   ```

5. **Run the system**
   ```bash
   python main.py
   ```

## 🔑 Getting API Credentials

### 1. Google Gemini API Key (5 minutes)
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the key (starts with `AIza`)

### 2. HubSpot API Key (10 minutes)
1. Go to your HubSpot account
2. Navigate to Settings → Integrations → Private Apps
3. Create a new private app
4. Add these scopes:
   - `crm.objects.contacts.read`
   - `crm.objects.contacts.write`
   - `crm.objects.deals.read`
   - `crm.objects.deals.write`
5. Copy the access token (starts with `pat-`)

### 3. Gmail App Password (10 minutes)
1. Enable 2-factor authentication on your Google account
2. Go to [Google Account Security](https://myaccount.google.com/security)
3. Click "App passwords"
4. Generate a new app password for "Mail"
5. Use this 16-character password (not your regular Gmail password)

## 💻 Usage

### Interactive Mode
```bash
python main.py
```

Example interactions:
```
💬 Your request: Create a contact John Doe, john@example.com, at Acme Corp
✅ Contact created successfully for john@example.com
📧 Email notification sent

💬 Your request: Create a deal for $5000 with John from Acme Corp
✅ Deal created successfully: $5000 Deal
📧 Email notification sent
```

### Single Query Mode
```bash
python main.py -q "Create a contact Jane Smith, jane@example.com, at TechCorp"
```

### Test Mode
```bash
python main.py --test
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   Orchestrator   │───▶│   HubSpot API   │
│                 │    │   (LangGraph)    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Email Agent    │    │   Gemini AI     │
                       │   (SMTP/Gmail)   │    │   (NLP Engine)  │
                       └──────────────────┘    └─────────────────┘
```

### Components

1. **Orchestrator**: Main workflow engine using LangGraph
2. **Gemini AI Integration**: Natural language processing and intent recognition
3. **HubSpot Agent**: Handles CRM operations
4. **Email Agent**: Manages email notifications
5. **Config Manager**: Handles configuration and API keys
6. **Main App**: CLI interface and application entry point

## 🧪 Testing

Run the complete test suite:
```bash
pytest tests/ -v
```

Run specific test files:
```bash
pytest tests/test_basic.py -v
pytest tests/test_orchestrator.py -v
```

## 📁 Project Structure

```
ai-agent-workflow/
├── agents/
│   ├── orchestrator.py      # Main workflow orchestrator
│   ├── hubspot_agent.py     # HubSpot CRM integration
│   └── email_agent.py       # Email notification system
├── config/
│   ├── config_manager.py    # Configuration management
│   └── config.json          # API credentials (DO NOT COMMIT)
├── tests/
│   ├── test_basic.py        # Basic unit tests
│   └── test_orchestrator.py # Comprehensive workflow tests
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables
You can also use environment variables instead of config.json:
```bash
export GEMINI_API_KEY="your-key"
export HUBSPOT_API_KEY="your-key"
export EMAIL_USERNAME="your-email"
export EMAIL_PASSWORD="your-password"
```

### Custom Configuration
Edit `config/config.json` to customize:
- Gemini model and parameters
- HubSpot API settings
- Email server configuration
- Logging levels

## 🚨 Troubleshooting

### Common Issues

1. **"API key not configured" error**
   - Ensure your API keys are properly set in `config/config.json`
   - Check that the keys don't start with "your-" placeholder text

2. **Email sending fails**
   - Verify your Gmail app password (not regular password)
   - Ensure 2-factor authentication is enabled
   - Check SMTP settings in configuration

3. **HubSpot API errors**
   - Verify your private app has the correct scopes
   - Check that the API token is valid and not expired

4. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.10+ required)

### Debug Mode
Enable debug logging by setting the log level to DEBUG in `config/config.json`:
```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

## 📊 Example Workflows

### Contact Creation
```
Input: "Add John Smith, john.smith@example.com, phone 555-1234, to Acme Corporation"
Output: Contact created in HubSpot + Email notification sent
```

### Deal Creation
```
Input: "Create a $10,000 deal with John Smith from Acme Corp, close date 2024-12-31"
Output: Deal created in HubSpot + Email notification sent
```

### Complex Request
```
Input: "I need to add a new prospect Sarah Johnson, sarah@techcorp.com, she's interested in our premium package worth $15,000"
Output: Contact created + Deal created + Both associated + Email notifications sent
```

## 🔒 Security

- API keys are stored locally in `config/config.json`
- The config file is gitignored and should never be committed
- All API communications use HTTPS
- Email credentials are handled securely through SMTP

## 🚀 Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp config/config.json.example config/config.json
# Edit config.json with your credentials

# Run tests
pytest tests/ -v

# Start the application
python main.py
```

### Production Considerations
- Use environment variables for API keys in production
- Set up proper logging and monitoring
- Consider rate limiting for API calls
- Implement proper error handling and retry logic

## 📈 Performance

- Typical response time: 2-5 seconds
- Supports concurrent requests (with proper rate limiting)
- Efficient API usage with batching where possible
- Comprehensive caching for configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the logs in `ai_agent_workflow.log`
3. Run the test suite to verify installation
4. Check your API credentials and permissions

## 🎯 Roadmap

- [ ] Web interface for easier interaction
- [ ] Additional CRM integrations (Salesforce, Pipedrive)
- [ ] Advanced workflow templates
- [ ] Real-time notifications
- [ ] Analytics and reporting dashboard
- [ ] Multi-language support
- [ ] Advanced AI capabilities (sentiment analysis, lead scoring)

---

**Built with ❤️ using Python, LangGraph, Google Gemini AI, and HubSpot**