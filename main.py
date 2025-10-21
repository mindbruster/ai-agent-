"""
Main Entry Point for AI Agent Workflow System
CLI application for interacting with the AI agent workflow
"""

import logging
import sys
import argparse
from typing import Optional
from config.config_manager import ConfigManager
from agents.orchestrator import AIAgentOrchestrator, WorkflowResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ai_agent_workflow.log')
    ]
)

logger = logging.getLogger(__name__)


class AIAgentWorkflowApp:
    """Main application class for the AI Agent Workflow System"""
    
    def __init__(self):
        """Initialize the application"""
        self.config_manager = None
        self.orchestrator = None
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the application components
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing AI Agent Workflow System...")
            
            # Load configuration
            self.config_manager = ConfigManager()
            
            # Check if configuration is complete
            if not self.config_manager.is_configured():
                logger.error("Configuration incomplete. Please update config.json with your API credentials.")
                return False
            
            # Initialize orchestrator
            self.orchestrator = AIAgentOrchestrator(self.config_manager)
            
            self.initialized = True
            logger.info("AI Agent Workflow System initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def run_interactive_mode(self) -> None:
        """Run the application in interactive mode"""
        if not self.initialized:
            logger.error("Application not initialized")
            return
        
        print("\n" + "="*60)
        print("🤖 AI Agent Workflow System")
        print("="*60)
        print("Welcome! I can help you manage your CRM operations.")
        print("\nAvailable actions:")
        for i, action in enumerate(self.orchestrator.get_available_actions(), 1):
            print(f"  {i}. {action}")
        
        print("\nExamples:")
        print("  • Create a contact: 'Add John Doe, john@example.com, to Acme Corp'")
        print("  • Create a deal: 'Create a deal for $5000 with John from Acme Corp'")
        print("  • Type 'quit' or 'exit' to stop")
        print("="*60)
        
        while True:
            try:
                user_input = input("\n💬 Your request: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if not user_input:
                    print("Please enter a request.")
                    continue
                
                # Process the request
                result = self.process_request(user_input)
                self.display_result(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"❌ Error: {e}")
    
    def process_request(self, user_input: str) -> WorkflowResult:
        """
        Process a user request
        
        Args:
            user_input: User's request
            
        Returns:
            WorkflowResult with the outcome
        """
        if not self.initialized:
            return WorkflowResult(
                success=False,
                message="Application not initialized",
                error="Application not initialized"
            )
        
        return self.orchestrator.process_request(user_input)
    
    def display_result(self, result: WorkflowResult) -> None:
        """
        Display the result of a workflow execution
        
        Args:
            result: WorkflowResult to display
        """
        if result.success:
            print(f"SUCCESS: {result.message}")
            
            if result.data:
                if result.data.get("email_sent"):
                    print("Email notification sent")
                else:
                    print("Email notification not sent")
        else:
            print(f"ERROR: {result.message}")
            if result.error:
                print(f"   Error: {result.error}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI Agent Workflow System - CRM Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Run in interactive mode
  python main.py -q "Create contact John Doe, john@example.com"  # Single query
  python main.py --test                    # Run test mode
        """
    )
    
    parser.add_argument(
        '-q', '--query',
        type=str,
        help='Process a single query and exit'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode with sample data'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.json',
        help='Path to configuration file (default: config/config.json)'
    )
    
    args = parser.parse_args()
    
    # Create and initialize the application
    app = AIAgentWorkflowApp()
    
    if not app.initialize():
        print("ERROR: Failed to initialize the application.")
        print("Please check your configuration and try again.")
        sys.exit(1)
    
    try:
        if args.test:
            # Run test mode
            print("Running in test mode...")
            test_requests = [
                "Create a contact John Smith, john.smith@example.com, at TechCorp",
                "Create a deal for $10,000 with John Smith from TechCorp"
            ]
            
            for request in test_requests:
                print(f"\nTest request: {request}")
                result = app.process_request(request)
                app.display_result(result)
        
        elif args.query:
            # Process single query
            print(f"Processing query: {args.query}")
            result = app.process_request(args.query)
            app.display_result(result)
        
        else:
            # Run in interactive mode
            app.run_interactive_mode()
    
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"ERROR: Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
