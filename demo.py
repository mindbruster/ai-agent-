#!/usr/bin/env python3
"""
Demo script for AI Agent Workflow System
Shows the system capabilities with sample data
"""

import logging
import sys
from config.config_manager import ConfigManager
from agents.orchestrator import AIAgentOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def demo_contact_creation():
    """Demo contact creation workflow"""
    print("\n" + "="*50)
    print("📞 DEMO: Contact Creation")
    print("="*50)
    
    demo_requests = [
        "Create a contact John Smith, john.smith@example.com, at TechCorp",
        "Add Sarah Johnson, sarah@techcorp.com, phone 555-1234, to Acme Inc",
        "New prospect: Mike Wilson, mike@startup.com, from Innovation Labs"
    ]
    
    for request in demo_requests:
        print(f"\n💬 Request: {request}")
        print("   Expected: Contact created in HubSpot + Email notification")


def demo_deal_creation():
    """Demo deal creation workflow"""
    print("\n" + "="*50)
    print("💰 DEMO: Deal Creation")
    print("="*50)
    
    demo_requests = [
        "Create a deal for $5,000 with John Smith from TechCorp",
        "New $15,000 opportunity with Sarah Johnson at Acme Inc",
        "Deal worth $25,000 with Mike Wilson from Innovation Labs, close date 2024-12-31"
    ]
    
    for request in demo_requests:
        print(f"\n💬 Request: {request}")
        print("   Expected: Deal created in HubSpot + Email notification")


def demo_complex_workflows():
    """Demo complex workflow scenarios"""
    print("\n" + "="*50)
    print("🔄 DEMO: Complex Workflows")
    print("="*50)
    
    demo_requests = [
        "Add new prospect Lisa Chen, lisa@enterprise.com, she's interested in our premium package worth $50,000",
        "Create contact and deal: Tom Brown, tom@corporation.com, $30,000 enterprise solution",
        "New lead: Emma Davis, emma@company.com, phone 555-9876, interested in $10,000 basic package"
    ]
    
    for request in demo_requests:
        print(f"\n💬 Request: {request}")
        print("   Expected: Contact + Deal created + Both associated + Email notifications")


def show_system_architecture():
    """Show system architecture"""
    print("\n" + "="*50)
    print("🏗️ SYSTEM ARCHITECTURE")
    print("="*50)
    
    print("""
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   Orchestrator   │───▶│   HubSpot API   │
│                 │    │   (LangGraph)    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Email Agent    │
                       │   (SMTP/Gmail)   │
                       └──────────────────┘

Components:
• Orchestrator: Main workflow engine using LangGraph
• HubSpot Agent: Handles CRM operations (contacts, deals)
• Email Agent: Manages email notifications
• Config Manager: Handles configuration and API keys
• Main App: CLI interface and application entry point
    """)


def show_technology_stack():
    """Show technology stack"""
    print("\n" + "="*50)
    print("🛠️ TECHNOLOGY STACK")
    print("="*50)
    
    print("""
Backend:
• Python 3.10+ - Core language
• LangChain - LLM orchestration framework
• LangGraph - Workflow execution engine
• OpenAI API - GPT-4 for natural language processing
• Requests - HTTP client for API calls

Integrations:
• HubSpot API - CRM operations
• Gmail SMTP - Email notifications

Testing & Tools:
• Pytest - Testing framework
• Git - Version control
• Structlog - Structured logging
    """)


def show_features():
    """Show system features"""
    print("\n" + "="*50)
    print("✨ FEATURES")
    print("="*50)
    
    features = [
        "Natural Language Processing - Parse user requests in plain English",
        "CRM Integration - Automatically create contacts and deals in HubSpot",
        "Email Notifications - Send automated notifications for all operations",
        "Workflow Orchestration - Powered by LangGraph for complex workflows",
        "Error Handling - Comprehensive error handling and notifications",
        "Testing Suite - Complete test coverage for all components",
        "CLI Interface - Easy-to-use command-line interface",
        "Configuration Management - Secure API key management",
        "Logging - Comprehensive logging throughout the system"
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"{i:2}. {feature}")


def main():
    """Main demo function"""
    print("🤖 AI Agent Workflow System - Demo")
    print("="*60)
    print("This demo shows the capabilities of the AI Agent Workflow System")
    print("without requiring actual API credentials.")
    print()
    
    show_features()
    show_system_architecture()
    show_technology_stack()
    demo_contact_creation()
    demo_deal_creation()
    demo_complex_workflows()
    
    print("\n" + "="*60)
    print("🚀 READY TO GET STARTED?")
    print("="*60)
    print()
    print("1. Run the quick start script:")
    print("   python quick_start.py")
    print()
    print("2. Update your API credentials in config/config.json")
    print()
    print("3. Start the system:")
    print("   python main.py")
    print()
    print("4. Try some of the demo requests above!")
    print()
    print("📖 For detailed instructions, see README.md")


if __name__ == "__main__":
    main()
