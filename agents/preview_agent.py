"""
Preview Agent for Dynamic Overview and Editing
Shows a preview of what will be created and allows editing before confirmation
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from agents.hubspot_agent import Contact, Deal

logger = logging.getLogger(__name__)


@dataclass
class PreviewItem:
    """Represents a preview item that can be edited"""
    type: str  # "contact" or "deal"
    data: Dict[str, Any]
    original_input: str


class PreviewAgent:
    """Agent for handling dynamic previews and user confirmations"""
    
    def __init__(self):
        """Initialize the preview agent"""
        self.preview_items: List[PreviewItem] = []
    
    def create_contact_preview(self, entities: Dict[str, Any], original_input: str) -> PreviewItem:
        """Create a preview for contact creation"""
        preview_data = {
            "email": entities.get("email", ""),
            "first_name": entities.get("first_name", ""),
            "last_name": entities.get("last_name", ""),
            "phone": entities.get("phone", ""),
            "company": entities.get("company", ""),
            "properties": entities.get("properties", {})
        }
        
        return PreviewItem(
            type="contact",
            data=preview_data,
            original_input=original_input
        )
    
    def create_deal_preview(self, entities: Dict[str, Any], original_input: str) -> PreviewItem:
        """Create a preview for deal creation"""
        amount = entities.get("amount")
        if amount:
            try:
                amount = float(amount)
            except (ValueError, TypeError):
                amount = None
        
        preview_data = {
            "deal_name": entities.get("deal_name") or entities.get("name") or f"Deal with {entities.get('first_name', '')} {entities.get('last_name', '')} from {entities.get('company', '')}".strip(),
            "amount": amount,
            "stage": entities.get("stage", "appointmentscheduled"),
            "close_date": entities.get("close_date", ""),
            "contact_email": entities.get("contact_email") or entities.get("email", ""),
            "contact_name": entities.get("contact_name") or f"{entities.get('first_name', '')} {entities.get('last_name', '')}".strip(),
            "company": entities.get("company", ""),
            "properties": entities.get("properties", {})
        }
        
        return PreviewItem(
            type="deal",
            data=preview_data,
            original_input=original_input
        )
    
    def display_preview(self, preview_item: PreviewItem) -> None:
        """Display a formatted preview of the item"""
        print("\n" + "="*60)
        print("PREVIEW - Review Before Creating")
        print("="*60)
        
        if preview_item.type == "contact":
            self._display_contact_preview(preview_item)
        elif preview_item.type == "deal":
            self._display_deal_preview(preview_item)
        
        print("="*60)
    
    def _display_contact_preview(self, preview_item: PreviewItem) -> None:
        """Display contact preview"""
        print("CONTACT TO BE CREATED:")
        print()
        data = preview_item.data
        
        print(f"Email:          {data.get('email', 'Not provided')}")
        print(f"First Name:     {data.get('first_name', 'Not provided')}")
        print(f"Last Name:      {data.get('last_name', 'Not provided')}")
        print(f"Phone:          {data.get('phone', 'Not provided')}")
        print(f"Company:        {data.get('company', 'Not provided')}")
        
        if data.get('properties'):
            print("\nAdditional Properties:")
            for key, value in data['properties'].items():
                print(f"   {key}: {value}")
    
    def _display_deal_preview(self, preview_item: PreviewItem) -> None:
        """Display deal preview"""
        print("DEAL TO BE CREATED:")
        print()
        data = preview_item.data
        
        print(f"Deal Name:      {data.get('deal_name', 'Not provided')}")
        if data.get('amount'):
            print(f"Amount:         ${data.get('amount', 0):,.2f}")
        else:
            print("Amount:         Not specified")
        print(f"Stage:          {data.get('stage', 'appointmentscheduled')}")
        print(f"Close Date:     {data.get('close_date', 'Not specified')}")
        print(f"Contact:        {data.get('contact_name', 'Not specified')}")
        print(f"Contact Email:  {data.get('contact_email', 'Not specified')}")
        print(f"Company:        {data.get('company', 'Not specified')}")
        
        if data.get('properties'):
            print("\nAdditional Properties:")
            for key, value in data['properties'].items():
                print(f"   {key}: {value}")
    
    def get_user_confirmation(self) -> bool:
        """Get user confirmation to proceed"""
        while True:
            response = input("\nDo you want to create this? (y/n/edit): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            elif response in ['e', 'edit']:
                return 'edit'
            else:
                print("Please enter 'y' for yes, 'n' for no, or 'edit' to modify")
    
    def edit_preview(self, preview_item: PreviewItem) -> PreviewItem:
        """Allow user to edit the preview"""
        print("\nEDITING MODE")
        print("Enter new values or press Enter to keep current values")
        print()
        
        data = preview_item.data
        
        if preview_item.type == "contact":
            data = self._edit_contact_data(data)
        elif preview_item.type == "deal":
            data = self._edit_deal_data(data)
        
        # Create new preview item with edited data
        return PreviewItem(
            type=preview_item.type,
            data=data,
            original_input=preview_item.original_input
        )
    
    def _edit_contact_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Edit contact data"""
        print("Email:")
        new_email = input(f"   Current: {data.get('email', '')} → New: ").strip()
        if new_email:
            data['email'] = new_email
        
        print("\nFirst Name:")
        new_first = input(f"   Current: {data.get('first_name', '')} → New: ").strip()
        if new_first:
            data['first_name'] = new_first
        
        print("\nLast Name:")
        new_last = input(f"   Current: {data.get('last_name', '')} → New: ").strip()
        if new_last:
            data['last_name'] = new_last
        
        print("\nPhone:")
        new_phone = input(f"   Current: {data.get('phone', '')} → New: ").strip()
        if new_phone:
            data['phone'] = new_phone
        
        print("\nCompany:")
        new_company = input(f"   Current: {data.get('company', '')} → New: ").strip()
        if new_company:
            data['company'] = new_company
        
        return data
    
    def _edit_deal_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Edit deal data"""
        print("Deal Name:")
        new_name = input(f"   Current: {data.get('deal_name', '')} → New: ").strip()
        if new_name:
            data['deal_name'] = new_name
        
        print("\nAmount:")
        current_amount = f"${data.get('amount', 0):,.2f}" if data.get('amount') else "Not specified"
        new_amount = input(f"   Current: {current_amount} → New: ").strip()
        if new_amount:
            try:
                # Remove currency symbols and parse
                clean_amount = new_amount.replace('$', '').replace(',', '').strip()
                data['amount'] = float(clean_amount)
            except ValueError:
                print("   Invalid amount format, keeping current value")
        
        print("\nStage:")
        new_stage = input(f"   Current: {data.get('stage', '')} → New: ").strip()
        if new_stage:
            data['stage'] = new_stage
        
        print("\nClose Date (YYYY-MM-DD):")
        new_date = input(f"   Current: {data.get('close_date', '')} → New: ").strip()
        if new_date:
            data['close_date'] = new_date
        
        print("\nContact Name:")
        new_contact = input(f"   Current: {data.get('contact_name', '')} → New: ").strip()
        if new_contact:
            data['contact_name'] = new_contact
        
        print("\nContact Email:")
        new_email = input(f"   Current: {data.get('contact_email', '')} → New: ").strip()
        if new_email:
            data['contact_email'] = new_email
        
        print("\nCompany:")
        new_company = input(f"   Current: {data.get('company', '')} → New: ").strip()
        if new_company:
            data['company'] = new_company
        
        return data
    
    def create_contact_from_preview(self, preview_item: PreviewItem) -> Contact:
        """Create a Contact object from preview data"""
        data = preview_item.data
        return Contact(
            email=data['email'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            company=data.get('company'),
            properties=data.get('properties')
        )
    
    def create_deal_from_preview(self, preview_item: PreviewItem) -> Deal:
        """Create a Deal object from preview data"""
        data = preview_item.data
        return Deal(
            deal_name=data['deal_name'],
            amount=data.get('amount'),
            stage=data.get('stage'),
            close_date=data.get('close_date'),
            contact_email=data.get('contact_email'),
            properties=data.get('properties')
        )
