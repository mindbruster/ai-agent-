"""
Email Agent for Sending Notifications
Handles email notifications using SMTP
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from config.config_manager import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    """Represents an email message"""
    to: str
    subject: str
    body: str
    html_body: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None


class EmailAgent:
    """Agent for sending email notifications"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the email agent
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.smtp_server = config_manager.get("email.smtp_server", "smtp.gmail.com")
        self.smtp_port = config_manager.get("email.smtp_port", 587)
        self.username = config_manager.get("email.username")
        self.password = config_manager.get("email.password")
        
        if not self.username or not self.password:
            raise ValueError("Email credentials not configured")
        
        if self.username.startswith("your-") or self.password.startswith("your-"):
            raise ValueError("Email credentials not configured")
    
    def send_email(self, message: EmailMessage) -> bool:
        """
        Send an email message
        
        Args:
            message: EmailMessage object to send
            
        Returns:
            True if email sent successfully, False otherwise
        """
        logger.info(f"Sending email to: {message.to}")
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = message.to
            msg['Subject'] = message.subject
            
            if message.cc:
                msg['Cc'] = ', '.join(message.cc)
            
            # Create text and HTML parts
            text_part = MIMEText(message.body, 'plain')
            msg.attach(text_part)
            
            if message.html_body:
                html_part = MIMEText(message.html_body, 'html')
                msg.attach(html_part)
            
            # Connect to server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                
                # Prepare recipients
                recipients = [message.to]
                if message.cc:
                    recipients.extend(message.cc)
                if message.bcc:
                    recipients.extend(message.bcc)
                
                server.send_message(msg, to_addrs=recipients)
            
            logger.info(f"Email sent successfully to: {message.to}")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def send_contact_created_notification(self, contact_email: str, contact_name: str = None) -> bool:
        """
        Send notification when a new contact is created
        
        Args:
            contact_email: Email address of the new contact
            contact_name: Name of the new contact
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "New Contact Created in CRM"
        
        body = f"""
Hello,

A new contact has been created in your CRM system.

Contact Details:
- Email: {contact_email}
- Name: {contact_name or 'Not provided'}

This contact was automatically added to your HubSpot CRM.

Best regards,
AI Agent Workflow System
        """.strip()
        
        html_body = f"""
<html>
<body>
    <h2>New Contact Created in CRM</h2>
    <p>Hello,</p>
    <p>A new contact has been created in your CRM system.</p>
    
    <h3>Contact Details:</h3>
    <ul>
        <li><strong>Email:</strong> {contact_email}</li>
        <li><strong>Name:</strong> {contact_name or 'Not provided'}</li>
    </ul>
    
    <p>This contact was automatically added to your HubSpot CRM.</p>
    
    <p>Best regards,<br>
    AI Agent Workflow System</p>
</body>
</html>
        """.strip()
        
        message = EmailMessage(
            to=self.username,  # Send to the configured email address
            subject=subject,
            body=body,
            html_body=html_body
        )
        
        return self.send_email(message)
    
    def send_deal_created_notification(self, deal_name: str, amount: float = None, 
                                     contact_email: str = None) -> bool:
        """
        Send notification when a new deal is created
        
        Args:
            deal_name: Name of the new deal
            amount: Deal amount
            contact_email: Associated contact email
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "New Deal Created in CRM"
        
        amount_text = f"${amount:,.2f}" if amount else "Not specified"
        
        body = f"""
Hello,

A new deal has been created in your CRM system.

Deal Details:
- Deal Name: {deal_name}
- Amount: {amount_text}
- Associated Contact: {contact_email or 'Not specified'}

This deal was automatically added to your HubSpot CRM.

Best regards,
AI Agent Workflow System
        """.strip()
        
        html_body = f"""
<html>
<body>
    <h2>New Deal Created in CRM</h2>
    <p>Hello,</p>
    <p>A new deal has been created in your CRM system.</p>
    
    <h3>Deal Details:</h3>
    <ul>
        <li><strong>Deal Name:</strong> {deal_name}</li>
        <li><strong>Amount:</strong> {amount_text}</li>
        <li><strong>Associated Contact:</strong> {contact_email or 'Not specified'}</li>
    </ul>
    
    <p>This deal was automatically added to your HubSpot CRM.</p>
    
    <p>Best regards,<br>
    AI Agent Workflow System</p>
</body>
</html>
        """.strip()
        
        message = EmailMessage(
            to=self.username,  # Send to the configured email address
            subject=subject,
            body=body,
            html_body=html_body
        )
        
        return self.send_email(message)
    
    def send_workflow_completion_notification(self, workflow_type: str, 
                                            details: Dict[str, Any]) -> bool:
        """
        Send notification when a workflow is completed
        
        Args:
            workflow_type: Type of workflow completed
            details: Additional details about the workflow
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"Workflow Completed: {workflow_type}"
        
        details_text = "\n".join([f"- {k}: {v}" for k, v in details.items()])
        
        body = f"""
Hello,

A workflow has been completed successfully.

Workflow Details:
- Type: {workflow_type}
{details_text}

The workflow was executed by the AI Agent Workflow System.

Best regards,
AI Agent Workflow System
        """.strip()
        
        html_body = f"""
<html>
<body>
    <h2>Workflow Completed: {workflow_type}</h2>
    <p>Hello,</p>
    <p>A workflow has been completed successfully.</p>
    
    <h3>Workflow Details:</h3>
    <ul>
        <li><strong>Type:</strong> {workflow_type}</li>
        {''.join([f'<li><strong>{k}:</strong> {v}</li>' for k, v in details.items()])}
    </ul>
    
    <p>The workflow was executed by the AI Agent Workflow System.</p>
    
    <p>Best regards,<br>
    AI Agent Workflow System</p>
</body>
</html>
        """.strip()
        
        message = EmailMessage(
            to=self.username,  # Send to the configured email address
            subject=subject,
            body=body,
            html_body=html_body
        )
        
        return self.send_email(message)
    
    def send_error_notification(self, error_message: str, context: str = None) -> bool:
        """
        Send notification when an error occurs
        
        Args:
            error_message: Error message
            context: Additional context about the error
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "Error in AI Agent Workflow System"
        
        body = f"""
Hello,

An error has occurred in the AI Agent Workflow System.

Error Details:
- Message: {error_message}
- Context: {context or 'Not provided'}

Please check the system logs for more details.

Best regards,
AI Agent Workflow System
        """.strip()
        
        html_body = f"""
<html>
<body>
    <h2>Error in AI Agent Workflow System</h2>
    <p>Hello,</p>
    <p>An error has occurred in the AI Agent Workflow System.</p>
    
    <h3>Error Details:</h3>
    <ul>
        <li><strong>Message:</strong> {error_message}</li>
        <li><strong>Context:</strong> {context or 'Not provided'}</li>
    </ul>
    
    <p>Please check the system logs for more details.</p>
    
    <p>Best regards,<br>
    AI Agent Workflow System</p>
</body>
</html>
        """.strip()
        
        message = EmailMessage(
            to=self.username,  # Send to the configured email address
            subject=subject,
            body=body,
            html_body=html_body
        )
        
        return self.send_email(message)
