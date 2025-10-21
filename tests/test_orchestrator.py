"""
Comprehensive tests for the AI Agent Orchestrator
Tests the complete workflow functionality
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from config.config_manager import ConfigManager
from agents.orchestrator import AIAgentOrchestrator, WorkflowState
from agents.hubspot_agent import Contact, Deal
from agents.email_agent import EmailMessage


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing"""
    config_data = {
        "openai": {
            "api_key": "test-openai-key",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000
        },
        "hubspot": {
            "api_key": "test-hubspot-key",
            "base_url": "https://api.hubapi.com"
        },
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "test@example.com",
            "password": "test-password"
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        config_path = f.name
    
    config_manager = ConfigManager(config_path)
    
    yield config_manager
    
    # Cleanup
    os.unlink(config_path)


@pytest.fixture
def mock_orchestrator(mock_config):
    """Create a mock orchestrator for testing"""
    with patch('agents.orchestrator.ChatOpenAI') as mock_llm, \
         patch('agents.orchestrator.HubSpotAgent') as mock_hubspot, \
         patch('agents.orchestrator.EmailAgent') as mock_email:
        
        # Setup mock LLM
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.return_value.content = """
        INTENT: create_contact
        ENTITIES: email:test@example.com, first_name:John, last_name:Doe, company:TestCorp
        """
        mock_llm.return_value = mock_llm_instance
        
        # Setup mock HubSpot agent
        mock_hubspot_instance = Mock()
        mock_hubspot_instance.create_contact.return_value = {"id": "contact123", "properties": {"email": "test@example.com"}}
        mock_hubspot_instance.create_deal.return_value = {"id": "deal123", "properties": {"dealname": "Test Deal"}}
        mock_hubspot.return_value = mock_hubspot_instance
        
        # Setup mock Email agent
        mock_email_instance = Mock()
        mock_email_instance.send_contact_created_notification.return_value = True
        mock_email_instance.send_deal_created_notification.return_value = True
        mock_email.return_value = mock_email_instance
        
        orchestrator = AIAgentOrchestrator(mock_config)
        
        yield orchestrator, mock_llm_instance, mock_hubspot_instance, mock_email_instance


class TestAIAgentOrchestrator:
    """Test cases for AIAgentOrchestrator"""
    
    def test_orchestrator_initialization(self, mock_config):
        """Test orchestrator initialization"""
        with patch('agents.orchestrator.ChatOpenAI'), \
             patch('agents.orchestrator.HubSpotAgent'), \
             patch('agents.orchestrator.EmailAgent'):
            
            orchestrator = AIAgentOrchestrator(mock_config)
            assert orchestrator is not None
            assert orchestrator.config_manager == mock_config
    
    def test_parse_input_create_contact(self, mock_orchestrator):
        """Test parsing input for contact creation"""
        orchestrator, mock_llm, _, _ = mock_orchestrator
        
        state = WorkflowState(
            user_input="Create a contact John Doe, john@example.com, at TestCorp",
            intent=None,
            entities={},
            contact_data=None,
            deal_data=None,
            hubspot_result=None,
            email_result=None,
            error=None,
            workflow_completed=False
        )
        
        result_state = orchestrator._parse_input(state)
        
        assert result_state["intent"] == "create_contact"
        assert result_state["entities"]["email"] == "test@example.com"
        assert result_state["entities"]["first_name"] == "John"
        assert result_state["entities"]["last_name"] == "Doe"
        assert result_state["entities"]["company"] == "TestCorp"
    
    def test_parse_input_create_deal(self, mock_orchestrator):
        """Test parsing input for deal creation"""
        orchestrator, mock_llm, _, _ = mock_orchestrator
        
        # Mock LLM response for deal creation
        mock_llm.invoke.return_value.content = """
        INTENT: create_deal
        ENTITIES: deal_name:Test Deal, amount:5000, contact_email:john@example.com
        """
        
        state = WorkflowState(
            user_input="Create a deal for $5000 with John from TestCorp",
            intent=None,
            entities={},
            contact_data=None,
            deal_data=None,
            hubspot_result=None,
            email_result=None,
            error=None,
            workflow_completed=False
        )
        
        result_state = orchestrator._parse_input(state)
        
        assert result_state["intent"] == "create_deal"
        assert result_state["entities"]["deal_name"] == "Test Deal"
        assert result_state["entities"]["amount"] == "5000"
        assert result_state["entities"]["contact_email"] == "john@example.com"
    
    def test_route_workflow(self, mock_orchestrator):
        """Test workflow routing"""
        orchestrator, _, _, _ = mock_orchestrator
        
        # Test contact creation route
        state = WorkflowState(
            user_input="",
            intent="create_contact",
            entities={},
            contact_data=None,
            deal_data=None,
            hubspot_result=None,
            email_result=None,
            error=None,
            workflow_completed=False
        )
        
        route = orchestrator._route_workflow(state)
        assert route == "create_contact"
        
        # Test deal creation route
        state["intent"] = "create_deal"
        route = orchestrator._route_workflow(state)
        assert route == "create_deal"
        
        # Test error route
        state["intent"] = "unknown"
        route = orchestrator._route_workflow(state)
        assert route == "error"
    
    def test_create_contact(self, mock_orchestrator):
        """Test contact creation workflow"""
        orchestrator, _, mock_hubspot, _ = mock_orchestrator
        
        state = WorkflowState(
            user_input="",
            intent="create_contact",
            entities={
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "company": "TestCorp"
            },
            contact_data=None,
            deal_data=None,
            hubspot_result=None,
            email_result=None,
            error=None,
            workflow_completed=False
        )
        
        result_state = orchestrator._create_contact(state)
        
        assert result_state["contact_data"] is not None
        assert result_state["hubspot_result"] is not None
        assert result_state["error"] is None
        
        # Verify HubSpot agent was called correctly
        mock_hubspot.create_contact.assert_called_once()
        call_args = mock_hubspot.create_contact.call_args[0][0]
        assert isinstance(call_args, Contact)
        assert call_args.email == "test@example.com"
        assert call_args.first_name == "John"
        assert call_args.last_name == "Doe"
        assert call_args.company == "TestCorp"
    
    def test_create_contact_missing_email(self, mock_orchestrator):
        """Test contact creation with missing email"""
        orchestrator, _, _, _ = mock_orchestrator
        
        state = WorkflowState(
            user_input="",
            intent="create_contact",
            entities={
                "first_name": "John",
                "last_name": "Doe"
            },
            contact_data=None,
            deal_data=None,
            hubspot_result=None,
            email_result=None,
            error=None,
            workflow_completed=False
        )
        
        result_state = orchestrator._create_contact(state)
        
        assert result_state["error"] == "Email is required to create a contact"
        assert result_state["contact_data"] is None
    
    def test_create_deal(self, mock_orchestrator):
        """Test deal creation workflow"""
        orchestrator, _, mock_hubspot, _ = mock_orchestrator
        
        state = WorkflowState(
            user_input="",
            intent="create_deal",
            entities={
                "deal_name": "Test Deal",
                "amount": "5000",
                "contact_email": "john@example.com"
            },
            contact_data=None,
            deal_data=None,
            hubspot_result=None,
            email_result=None,
            error=None,
            workflow_completed=False
        )
        
        result_state = orchestrator._create_deal(state)
        
        assert result_state["deal_data"] is not None
        assert result_state["hubspot_result"] is not None
        assert result_state["error"] is None
        
        # Verify HubSpot agent was called correctly
        mock_hubspot.create_deal.assert_called_once()
        call_args = mock_hubspot.create_deal.call_args[0][0]
        assert isinstance(call_args, Deal)
        assert call_args.deal_name == "Test Deal"
        assert call_args.amount == 5000.0
        assert call_args.contact_email == "john@example.com"
    
    def test_create_deal_missing_name(self, mock_orchestrator):
        """Test deal creation with missing name"""
        orchestrator, _, _, _ = mock_orchestrator
        
        state = WorkflowState(
            user_input="",
            intent="create_deal",
            entities={
                "amount": "5000"
            },
            contact_data=None,
            deal_data=None,
            hubspot_result=None,
            email_result=None,
            error=None,
            workflow_completed=False
        )
        
        result_state = orchestrator._create_deal(state)
        
        assert result_state["error"] == "Deal name is required"
        assert result_state["deal_data"] is None
    
    def test_send_notification_contact(self, mock_orchestrator):
        """Test sending notification for contact creation"""
        orchestrator, _, _, mock_email = mock_orchestrator
        
        state = WorkflowState(
            user_input="",
            intent="create_contact",
            entities={
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe"
            },
            contact_data={"id": "contact123"},
            deal_data=None,
            hubspot_result={"id": "contact123"},
            email_result=None,
            error=None,
            workflow_completed=False
        )
        
        result_state = orchestrator._send_notification(state)
        
        assert result_state["email_result"] is True
        assert result_state["workflow_completed"] is True
        
        # Verify email agent was called correctly
        mock_email.send_contact_created_notification.assert_called_once_with(
            "test@example.com", "John Doe"
        )
    
    def test_send_notification_deal(self, mock_orchestrator):
        """Test sending notification for deal creation"""
        orchestrator, _, _, mock_email = mock_orchestrator
        
        state = WorkflowState(
            user_input="",
            intent="create_deal",
            entities={
                "deal_name": "Test Deal",
                "amount": "5000",
                "contact_email": "john@example.com"
            },
            contact_data=None,
            deal_data={"id": "deal123"},
            hubspot_result={"id": "deal123"},
            email_result=None,
            error=None,
            workflow_completed=False
        )
        
        result_state = orchestrator._send_notification(state)
        
        assert result_state["email_result"] is True
        assert result_state["workflow_completed"] is True
        
        # Verify email agent was called correctly
        mock_email.send_deal_created_notification.assert_called_once_with(
            "Test Deal", 5000.0, "john@example.com"
        )
    
    def test_handle_error(self, mock_orchestrator):
        """Test error handling"""
        orchestrator, _, _, mock_email = mock_orchestrator
        
        state = WorkflowState(
            user_input="test input",
            intent="unknown",
            entities={},
            contact_data=None,
            deal_data=None,
            hubspot_result=None,
            email_result=None,
            error="Test error",
            workflow_completed=False
        )
        
        result_state = orchestrator._handle_error(state)
        
        assert result_state["workflow_completed"] is True
        
        # Verify error notification was sent
        mock_email.send_error_notification.assert_called_once_with(
            "Test error", "User input: test input"
        )
    
    def test_process_request_success(self, mock_orchestrator):
        """Test successful request processing"""
        orchestrator, _, _, _ = mock_orchestrator
        
        result = orchestrator.process_request("Create a contact John Doe, john@example.com, at TestCorp")
        
        assert result.success is True
        assert "Contact created successfully" in result.message
        assert result.data is not None
        assert result.error is None
    
    def test_process_request_failure(self, mock_orchestrator):
        """Test failed request processing"""
        orchestrator, mock_llm, _, _ = mock_orchestrator
        
        # Mock LLM to raise an exception
        mock_llm.invoke.side_effect = Exception("LLM error")
        
        result = orchestrator.process_request("Create a contact John Doe, john@example.com, at TestCorp")
        
        assert result.success is False
        assert "Workflow execution failed" in result.message
        assert result.error is not None
    
    def test_get_available_actions(self, mock_orchestrator):
        """Test getting available actions"""
        orchestrator, _, _, _ = mock_orchestrator
        
        actions = orchestrator.get_available_actions()
        
        assert isinstance(actions, list)
        assert len(actions) > 0
        assert "Create a new contact" in actions[0]
        assert "Create a new deal" in actions[1]


class TestWorkflowState:
    """Test cases for WorkflowState"""
    
    def test_workflow_state_creation(self):
        """Test WorkflowState creation"""
        state = WorkflowState(
            user_input="test input",
            intent="create_contact",
            entities={"email": "test@example.com"},
            contact_data=None,
            deal_data=None,
            hubspot_result=None,
            email_result=None,
            error=None,
            workflow_completed=False
        )
        
        assert state["user_input"] == "test input"
        assert state["intent"] == "create_contact"
        assert state["entities"]["email"] == "test@example.com"
        assert state["workflow_completed"] is False


if __name__ == "__main__":
    pytest.main([__file__])
