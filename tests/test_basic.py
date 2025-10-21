"""
Basic unit tests for the AI Agent Workflow System
Tests individual components and basic functionality
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch
from config.config_manager import ConfigManager
from agents.hubspot_agent import HubSpotAgent, Contact, Deal
from agents.email_agent import EmailAgent, EmailMessage


class TestConfigManager:
    """Test cases for ConfigManager"""
    
    def test_config_manager_initialization(self):
        """Test ConfigManager initialization with valid config"""
        config_data = {
            "openai": {"api_key": "test-key", "model": "gpt-4"},
            "hubspot": {"api_key": "test-key", "base_url": "https://api.hubapi.com"},
            "email": {"username": "test@example.com", "password": "test-pass"},
            "logging": {"level": "INFO", "format": "test"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            config_manager = ConfigManager(config_path)
            assert config_manager is not None
            assert config_manager.get("openai.api_key") == "test-key"
            assert config_manager.get("hubspot.base_url") == "https://api.hubapi.com"
        finally:
            os.unlink(config_path)
    
    def test_config_manager_missing_file(self):
        """Test ConfigManager with missing config file"""
        config_manager = ConfigManager("nonexistent_config.json")
        assert config_manager is not None
        # Should create default config
        assert config_manager.config is not None
    
    def test_config_manager_get_method(self):
        """Test ConfigManager get method with dot notation"""
        config_data = {
            "openai": {"api_key": "test-key", "model": "gpt-4"},
            "hubspot": {"api_key": "test-key"},
            "email": {"username": "test@example.com"},
            "logging": {"level": "INFO"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            config_manager = ConfigManager(config_path)
            
            # Test valid keys
            assert config_manager.get("openai.api_key") == "test-key"
            assert config_manager.get("openai.model") == "gpt-4"
            
            # Test default values
            assert config_manager.get("nonexistent.key", "default") == "default"
            assert config_manager.get("openai.temperature", 0.7) == 0.7
            
        finally:
            os.unlink(config_path)
    
    def test_config_manager_is_configured(self):
        """Test configuration validation"""
        # Test with valid config
        config_data = {
            "openai": {"api_key": "sk-real-key"},
            "hubspot": {"api_key": "pat-real-key"},
            "email": {"username": "real@example.com"},
            "logging": {"level": "INFO"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            config_manager = ConfigManager(config_path)
            assert config_manager.is_configured() is True
        finally:
            os.unlink(config_path)
        
        # Test with placeholder config
        config_data["openai"]["api_key"] = "your-openai-api-key-here"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            config_manager = ConfigManager(config_path)
            assert config_manager.is_configured() is False
        finally:
            os.unlink(config_path)


class TestContact:
    """Test cases for Contact dataclass"""
    
    def test_contact_creation(self):
        """Test Contact object creation"""
        contact = Contact(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="123-456-7890",
            company="TestCorp"
        )
        
        assert contact.email == "test@example.com"
        assert contact.first_name == "John"
        assert contact.last_name == "Doe"
        assert contact.phone == "123-456-7890"
        assert contact.company == "TestCorp"
        assert contact.properties is None
    
    def test_contact_creation_minimal(self):
        """Test Contact object creation with minimal data"""
        contact = Contact(email="test@example.com")
        
        assert contact.email == "test@example.com"
        assert contact.first_name is None
        assert contact.last_name is None
        assert contact.phone is None
        assert contact.company is None


class TestDeal:
    """Test cases for Deal dataclass"""
    
    def test_deal_creation(self):
        """Test Deal object creation"""
        deal = Deal(
            deal_name="Test Deal",
            amount=5000.0,
            stage="appointmentscheduled",
            close_date="2024-12-31",
            contact_email="test@example.com"
        )
        
        assert deal.deal_name == "Test Deal"
        assert deal.amount == 5000.0
        assert deal.stage == "appointmentscheduled"
        assert deal.close_date == "2024-12-31"
        assert deal.contact_email == "test@example.com"
        assert deal.properties is None
    
    def test_deal_creation_minimal(self):
        """Test Deal object creation with minimal data"""
        deal = Deal(deal_name="Test Deal")
        
        assert deal.deal_name == "Test Deal"
        assert deal.amount is None
        assert deal.stage is None
        assert deal.close_date is None
        assert deal.contact_email is None


class TestEmailMessage:
    """Test cases for EmailMessage dataclass"""
    
    def test_email_message_creation(self):
        """Test EmailMessage object creation"""
        message = EmailMessage(
            to="recipient@example.com",
            subject="Test Subject",
            body="Test body",
            html_body="<p>Test HTML body</p>",
            cc=["cc@example.com"],
            bcc=["bcc@example.com"]
        )
        
        assert message.to == "recipient@example.com"
        assert message.subject == "Test Subject"
        assert message.body == "Test body"
        assert message.html_body == "<p>Test HTML body</p>"
        assert message.cc == ["cc@example.com"]
        assert message.bcc == ["bcc@example.com"]
    
    def test_email_message_creation_minimal(self):
        """Test EmailMessage object creation with minimal data"""
        message = EmailMessage(
            to="recipient@example.com",
            subject="Test Subject",
            body="Test body"
        )
        
        assert message.to == "recipient@example.com"
        assert message.subject == "Test Subject"
        assert message.body == "Test body"
        assert message.html_body is None
        assert message.cc is None
        assert message.bcc is None


class TestHubSpotAgent:
    """Test cases for HubSpotAgent"""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for HubSpot agent"""
        config_data = {
            "hubspot": {
                "api_key": "test-hubspot-key",
                "base_url": "https://api.hubapi.com"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        config_manager = ConfigManager(config_path)
        
        yield config_manager
        
        os.unlink(config_path)
    
    def test_hubspot_agent_initialization(self, mock_config):
        """Test HubSpotAgent initialization"""
        agent = HubSpotAgent(mock_config)
        
        assert agent.api_key == "test-hubspot-key"
        assert agent.base_url == "https://api.hubapi.com"
        assert "Authorization" in agent.headers
        assert "Content-Type" in agent.headers
    
    def test_hubspot_agent_missing_api_key(self, mock_config):
        """Test HubSpotAgent with missing API key"""
        # Remove API key from config
        mock_config.config["hubspot"]["api_key"] = "your-hubspot-api-key-here"
        
        with pytest.raises(ValueError, match="HubSpot API key not configured"):
            HubSpotAgent(mock_config)
    
    @patch('agents.hubspot_agent.requests.post')
    def test_create_contact_success(self, mock_post, mock_config):
        """Test successful contact creation"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"id": "contact123", "properties": {"email": "test@example.com"}}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        agent = HubSpotAgent(mock_config)
        contact = Contact(email="test@example.com", first_name="John")
        
        result = agent.create_contact(contact)
        
        assert result["id"] == "contact123"
        mock_post.assert_called_once()
    
    @patch('agents.hubspot_agent.requests.post')
    def test_create_contact_failure(self, mock_post, mock_config):
        """Test contact creation failure"""
        # Mock failure response
        mock_post.side_effect = Exception("API Error")
        
        agent = HubSpotAgent(mock_config)
        contact = Contact(email="test@example.com")
        
        with pytest.raises(Exception, match="API Error"):
            agent.create_contact(contact)


class TestEmailAgent:
    """Test cases for EmailAgent"""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for Email agent"""
        config_data = {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "test@example.com",
                "password": "test-password"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        config_manager = ConfigManager(config_path)
        
        yield config_manager
        
        os.unlink(config_path)
    
    def test_email_agent_initialization(self, mock_config):
        """Test EmailAgent initialization"""
        agent = EmailAgent(mock_config)
        
        assert agent.smtp_server == "smtp.gmail.com"
        assert agent.smtp_port == 587
        assert agent.username == "test@example.com"
        assert agent.password == "test-password"
    
    def test_email_agent_missing_credentials(self, mock_config):
        """Test EmailAgent with missing credentials"""
        # Remove credentials from config
        mock_config.config["email"]["username"] = "your-email@gmail.com"
        
        with pytest.raises(ValueError, match="Email credentials not configured"):
            EmailAgent(mock_config)
    
    @patch('agents.email_agent.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp, mock_config):
        """Test successful email sending"""
        # Mock SMTP
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        agent = EmailAgent(mock_config)
        message = EmailMessage(
            to="recipient@example.com",
            subject="Test Subject",
            body="Test body"
        )
        
        result = agent.send_email(message)
        
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@example.com", "test-password")
        mock_server.send_message.assert_called_once()
    
    @patch('agents.email_agent.smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp, mock_config):
        """Test email sending failure"""
        # Mock SMTP failure
        mock_smtp.side_effect = Exception("SMTP Error")
        
        agent = EmailAgent(mock_config)
        message = EmailMessage(
            to="recipient@example.com",
            subject="Test Subject",
            body="Test body"
        )
        
        result = agent.send_email(message)
        
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
