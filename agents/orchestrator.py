"""
Main Orchestrator using LangGraph for AI Agent Workflow
Coordinates between different agents and manages the workflow
"""

import logging
from typing import Dict, List, Any, Optional, TypedDict
from dataclasses import dataclass
import google.generativeai as genai
from langgraph.graph import StateGraph, END
from config.config_manager import ConfigManager
from agents.hubspot_agent import HubSpotAgent, Contact, Deal
from agents.email_agent import EmailAgent
from agents.preview_agent import PreviewAgent

logger = logging.getLogger(__name__)


class WorkflowState(TypedDict):
    """State object for the workflow"""
    user_input: str
    intent: Optional[str]
    entities: Dict[str, Any]
    preview_item: Optional[Any]
    user_confirmed: Optional[bool]
    contact_data: Optional[Dict[str, Any]]
    deal_data: Optional[Dict[str, Any]]
    hubspot_result: Optional[Dict[str, Any]]
    email_result: Optional[bool]
    error: Optional[str]
    workflow_completed: bool


@dataclass
class WorkflowResult:
    """Result of a workflow execution"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AIAgentOrchestrator:
    """Main orchestrator for AI agent workflows"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the orchestrator
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.llm = self._initialize_llm()
        self.hubspot_agent = HubSpotAgent(config_manager)
        self.email_agent = EmailAgent(config_manager)
        self.preview_agent = PreviewAgent()
        self.workflow_graph = self._build_workflow_graph()
    
    def _initialize_llm(self) -> genai.GenerativeModel:
        """Initialize the Gemini LLM"""
        gemini_config = self.config_manager.get_gemini_config()
        
        # Configure the Gemini API
        genai.configure(api_key=gemini_config["api_key"])
        
        # Initialize the model
        model = genai.GenerativeModel(
            model_name=gemini_config.get("model", "gemini-pro"),
            generation_config=genai.types.GenerationConfig(
                temperature=gemini_config.get("temperature", 0.7),
                max_output_tokens=gemini_config.get("max_tokens", 1000)
            )
        )
        
        return model
    
    def _build_workflow_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("parse_input", self._parse_input)
        workflow.add_node("create_preview", self._create_preview)
        workflow.add_node("show_preview", self._show_preview)
        workflow.add_node("create_contact", self._create_contact)
        workflow.add_node("create_deal", self._create_deal)
        workflow.add_node("send_notification", self._send_notification)
        workflow.add_node("handle_error", self._handle_error)
        
        # Set entry point
        workflow.set_entry_point("parse_input")
        
        # Add edges
        workflow.add_conditional_edges(
            "parse_input",
            self._route_workflow,
            {
                "create_preview": "create_preview",
                "error": "handle_error"
            }
        )
        
        workflow.add_edge("create_preview", "show_preview")
        workflow.add_conditional_edges(
            "show_preview",
            self._route_after_preview,
            {
                "create_contact": "create_contact",
                "create_deal": "create_deal",
                "handle_error": "handle_error"
            }
        )
        
        workflow.add_edge("create_contact", "send_notification")
        workflow.add_edge("create_deal", "send_notification")
        workflow.add_edge("send_notification", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()
    
    def _parse_input(self, state: WorkflowState) -> WorkflowState:
        """Parse user input to determine intent and extract entities"""
        logger.info("Parsing user input")
        
        try:
            # Use LLM to parse the input
            system_prompt = """
            You are an AI assistant that helps parse user requests for CRM operations.
            
            Analyze the user input and determine:
            1. The intent (create_contact, create_deal, or unknown)
            2. Extract relevant entities (names, emails, phone numbers, companies, deal amounts, etc.)
            
            Return your analysis in this format:
            INTENT: [intent]
            ENTITIES: [key:value pairs separated by commas]
            
            Example:
            INTENT: create_contact
            ENTITIES: email:john@example.com, first_name:John, last_name:Doe, company:Acme Corp
            """
            
            # Create the prompt for Gemini
            prompt = f"{system_prompt}\n\nUser input: {state['user_input']}"
            
            response = self.llm.generate_content(prompt)
            result = response.text
            
            # Parse the response
            lines = result.strip().split('\n')
            intent = "unknown"
            entities = {}
            
            for line in lines:
                if line.startswith("INTENT:"):
                    intent = line.split(":", 1)[1].strip()
                elif line.startswith("ENTITIES:"):
                    entities_str = line.split(":", 1)[1].strip()
                    if entities_str:
                        for pair in entities_str.split(','):
                            if ':' in pair:
                                key, value = pair.strip().split(':', 1)
                                entities[key.strip()] = value.strip()
            
            state["intent"] = intent
            state["entities"] = entities
            
            logger.info(f"Parsed intent: {intent}, entities: {entities}")
            
        except Exception as e:
            logger.error(f"Error parsing input: {e}")
            state["error"] = f"Error parsing input: {str(e)}"
        
        return state
    
    def _route_workflow(self, state: WorkflowState) -> str:
        """Route the workflow based on parsed intent"""
        intent = state.get("intent", "unknown")
        
        if intent in ["create_contact", "create_deal"]:
            return "create_preview"
        else:
            return "error"
    
    def _route_after_preview(self, state: WorkflowState) -> str:
        """Route after preview based on user confirmation and intent"""
        if not state.get("user_confirmed"):
            return "handle_error"
        
        intent = state.get("intent", "unknown")
        if intent == "create_contact":
            return "create_contact"
        elif intent == "create_deal":
            return "create_deal"
        else:
            return "handle_error"
    
    def _create_preview(self, state: WorkflowState) -> WorkflowState:
        """Create a preview of what will be created"""
        logger.info("Creating preview")
        
        try:
            entities = state.get("entities", {})
            intent = state.get("intent", "unknown")
            original_input = state.get("user_input", "")
            
            if intent == "create_contact":
                preview_item = self.preview_agent.create_contact_preview(entities, original_input)
            elif intent == "create_deal":
                preview_item = self.preview_agent.create_deal_preview(entities, original_input)
            else:
                state["error"] = f"Unknown intent: {intent}"
                return state
            
            state["preview_item"] = preview_item
            
        except Exception as e:
            logger.error(f"Error creating preview: {e}")
            state["error"] = f"Error creating preview: {str(e)}"
        
        return state
    
    def _show_preview(self, state: WorkflowState) -> WorkflowState:
        """Show preview and get user confirmation"""
        logger.info("Showing preview to user")
        
        try:
            preview_item = state.get("preview_item")
            if not preview_item:
                state["error"] = "No preview item found"
                return state
            
            # Display the preview
            self.preview_agent.display_preview(preview_item)
            
            # Get user confirmation
            while True:
                confirmation = self.preview_agent.get_user_confirmation()
                
                if confirmation is True:
                    # User confirmed, proceed
                    state["user_confirmed"] = True
                    break
                elif confirmation is False:
                    # User declined, cancel
                    state["user_confirmed"] = False
                    state["error"] = "User cancelled the operation"
                    break
                elif confirmation == 'edit':
                    # User wants to edit, show edit mode
                    edited_item = self.preview_agent.edit_preview(preview_item)
                    state["preview_item"] = edited_item
                    # Show the updated preview
                    self.preview_agent.display_preview(edited_item)
                    # Continue the loop to get confirmation again
            
        except Exception as e:
            logger.error(f"Error showing preview: {e}")
            state["error"] = f"Error showing preview: {str(e)}"
        
        return state
    
    def _create_contact(self, state: WorkflowState) -> WorkflowState:
        """Create a contact in HubSpot"""
        logger.info("Creating contact")
        
        try:
            preview_item = state.get("preview_item")
            if not preview_item:
                state["error"] = "No preview item found for contact creation"
                return state
            
            # Create contact from preview data
            contact = self.preview_agent.create_contact_from_preview(preview_item)
            
            # Create contact in HubSpot
            result = self.hubspot_agent.create_contact(contact)
            state["contact_data"] = result
            state["hubspot_result"] = result
            
            logger.info(f"Contact created successfully: {result.get('id')}")
            
        except Exception as e:
            logger.error(f"Error creating contact: {e}")
            state["error"] = f"Error creating contact: {str(e)}"
        
        return state
    
    def _create_deal(self, state: WorkflowState) -> WorkflowState:
        """Create a deal in HubSpot"""
        logger.info("Creating deal")
        
        try:
            preview_item = state.get("preview_item")
            if not preview_item:
                state["error"] = "No preview item found for deal creation"
                return state
            
            # Create deal from preview data
            deal = self.preview_agent.create_deal_from_preview(preview_item)
            
            # Create deal in HubSpot
            result = self.hubspot_agent.create_deal(deal)
            state["deal_data"] = result
            state["hubspot_result"] = result
            
            logger.info(f"Deal created successfully: {result.get('id')}")
            
        except Exception as e:
            logger.error(f"Error creating deal: {e}")
            state["error"] = f"Error creating deal: {str(e)}"
        
        return state
    
    def _send_notification(self, state: WorkflowState) -> WorkflowState:
        """Send email notification"""
        logger.info("Sending notification")
        
        try:
            intent = state.get("intent")
            entities = state.get("entities", {})
            
            if intent == "create_contact":
                email = entities.get("email")
                name = f"{entities.get('first_name', '')} {entities.get('last_name', '')}".strip()
                success = self.email_agent.send_contact_created_notification(email, name)
                
            elif intent == "create_deal":
                deal_name = entities.get("deal_name") or entities.get("name")
                amount = None
                if "amount" in entities:
                    try:
                        amount = float(entities["amount"].replace("$", "").replace(",", ""))
                    except ValueError:
                        pass
                
                contact_email = entities.get("contact_email")
                success = self.email_agent.send_deal_created_notification(
                    deal_name, amount, contact_email
                )
            
            else:
                success = False
            
            state["email_result"] = success
            
            if success:
                logger.info("Notification sent successfully")
            else:
                logger.warning("Failed to send notification")
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            state["email_result"] = False
        
        # Mark workflow as completed
        state["workflow_completed"] = True
        
        return state
    
    def _handle_error(self, state: WorkflowState) -> WorkflowState:
        """Handle errors in the workflow"""
        logger.error(f"Workflow error: {state.get('error')}")
        
        try:
            # Send error notification
            error_message = state.get("error", "Unknown error")
            self.email_agent.send_error_notification(
                error_message, 
                f"User input: {state.get('user_input', 'N/A')}"
            )
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
        
        state["workflow_completed"] = True
        return state
    
    def process_request(self, user_input: str) -> WorkflowResult:
        """
        Process a user request through the workflow
        
        Args:
            user_input: User's request
            
        Returns:
            WorkflowResult with the outcome
        """
        logger.info(f"Processing request: {user_input}")
        
        # Initialize state
        initial_state = WorkflowState(
            user_input=user_input,
            intent=None,
            entities={},
            preview_item=None,
            user_confirmed=None,
            contact_data=None,
            deal_data=None,
            hubspot_result=None,
            email_result=None,
            error=None,
            workflow_completed=False
        )
        
        try:
            # Execute the workflow
            final_state = self.workflow_graph.invoke(initial_state)
            
            # Check for errors
            if final_state.get("error"):
                return WorkflowResult(
                    success=False,
                    message=f"Workflow failed: {final_state['error']}",
                    error=final_state["error"]
                )
            
            # Determine success message based on intent
            intent = final_state.get("intent")
            if intent == "create_contact":
                message = f"Contact created successfully for {final_state['entities'].get('email')}"
            elif intent == "create_deal":
                message = f"Deal created successfully: {final_state['entities'].get('deal_name', 'Unknown')}"
            else:
                message = "Workflow completed successfully"
            
            return WorkflowResult(
                success=True,
                message=message,
                data={
                    "hubspot_result": final_state.get("hubspot_result"),
                    "email_sent": final_state.get("email_result", False),
                    "entities": final_state.get("entities")
                }
            )
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return WorkflowResult(
                success=False,
                message=f"Workflow execution failed: {str(e)}",
                error=str(e)
            )
    
    def get_available_actions(self) -> List[str]:
        """Get list of available actions"""
        return [
            "Create a new contact with email, name, and company",
            "Create a new deal with name, amount, and associated contact",
            "Search for contacts by email or name",
            "Update contact information",
            "Update deal stages"
        ]
