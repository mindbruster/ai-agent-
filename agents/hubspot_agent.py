"""
HubSpot Agent for CRM Operations
Handles contact and deal management in HubSpot
"""

import requests
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from config.config_manager import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class Contact:
    """Represents a HubSpot contact"""
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


@dataclass
class Deal:
    """Represents a HubSpot deal"""
    deal_name: str
    amount: Optional[float] = None
    stage: Optional[str] = None
    close_date: Optional[str] = None
    contact_email: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class HubSpotAgent:
    """Agent for interacting with HubSpot CRM"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the HubSpot agent
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.api_key = config_manager.get("hubspot.api_key")
        self.base_url = config_manager.get("hubspot.base_url", "https://api.hubapi.com")
        
        if not self.api_key or self.api_key.startswith("your-"):
            raise ValueError("HubSpot API key not configured")
        
        # Check if this is a private app token (starts with pat-) or legacy hapikey
        if self.api_key.startswith("pat-"):
            # Private app token - use Bearer authentication
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            self.api_key_param = {}
        else:
            # Legacy hapikey - use hapikey parameter
            self.headers = {
                "Content-Type": "application/json"
            }
            self.api_key_param = {"hapikey": self.api_key}
    
    def create_contact(self, contact: Contact) -> Dict[str, Any]:
        """
        Create a new contact in HubSpot
        
        Args:
            contact: Contact object to create
            
        Returns:
            Dict containing the created contact data
        """
        logger.info(f"Creating contact: {contact.email}")
        
        properties = {
            "email": contact.email
        }
        
        if contact.first_name:
            properties["firstname"] = contact.first_name
        if contact.last_name:
            properties["lastname"] = contact.last_name
        if contact.phone:
            properties["phone"] = contact.phone
        if contact.company:
            properties["company"] = contact.company
        
        # Add any additional properties
        if contact.properties:
            properties.update(contact.properties)
        
        payload = {"properties": properties}
        
        try:
            response = requests.post(
                f"{self.base_url}/crm/v3/objects/contacts",
                headers=self.headers,
                params=self.api_key_param,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Contact created successfully: {result.get('id')}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating contact: {e}")
            raise
    
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """
        Get a contact by ID
        
        Args:
            contact_id: HubSpot contact ID
            
        Returns:
            Dict containing the contact data
        """
        logger.info(f"Getting contact: {contact_id}")
        
        try:
            response = requests.get(
                f"{self.base_url}/crm/v3/objects/contacts/{contact_id}",
                headers=self.headers,
                params=self.api_key_param
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Contact retrieved successfully: {result.get('properties', {}).get('email')}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting contact: {e}")
            raise
    
    def search_contacts(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for contacts
        
        Args:
            query: Search query
            
        Returns:
            List of matching contacts
        """
        logger.info(f"Searching contacts: {query}")
        
        # HubSpot search endpoint
        search_payload = {
            "query": query,
            "filterGroups": [],
            "sorts": [],
            "limit": 10
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/crm/v3/objects/contacts/search",
                headers=self.headers,
                params=self.api_key_param,
                json=search_payload
            )
            response.raise_for_status()
            
            result = response.json()
            contacts = result.get("results", [])
            logger.info(f"Found {len(contacts)} contacts")
            return contacts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching contacts: {e}")
            raise
    
    def update_contact(self, contact_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a contact's properties
        
        Args:
            contact_id: HubSpot contact ID
            properties: Properties to update
            
        Returns:
            Updated contact data
        """
        logger.info(f"Updating contact: {contact_id}")
        
        payload = {"properties": properties}
        
        try:
            response = requests.patch(
                f"{self.base_url}/crm/v3/objects/contacts/{contact_id}",
                headers=self.headers,
                params=self.api_key_param,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Contact updated successfully: {contact_id}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating contact: {e}")
            raise
    
    def create_deal(self, deal: Deal) -> Dict[str, Any]:
        """
        Create a new deal in HubSpot
        
        Args:
            deal: Deal object to create
            
        Returns:
            Dict containing the created deal data
        """
        logger.info(f"Creating deal: {deal.deal_name}")
        
        properties = {
            "dealname": deal.deal_name
        }
        
        if deal.amount:
            properties["amount"] = str(deal.amount)
        if deal.stage:
            properties["dealstage"] = deal.stage
        if deal.close_date:
            properties["closedate"] = deal.close_date
        
        # Add any additional properties
        if deal.properties:
            properties.update(deal.properties)
        
        payload = {"properties": properties}
        
        try:
            response = requests.post(
                f"{self.base_url}/crm/v3/objects/deals",
                headers=self.headers,
                params=self.api_key_param,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            deal_id = result.get('id')
            
            # Associate deal with contact if email provided
            if deal.contact_email:
                self.associate_deal_with_contact(deal_id, deal.contact_email)
            
            logger.info(f"Deal created successfully: {deal_id}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating deal: {e}")
            raise
    
    def associate_deal_with_contact(self, deal_id: str, contact_email: str) -> None:
        """
        Associate a deal with a contact
        
        Args:
            deal_id: HubSpot deal ID
            contact_email: Contact email address
        """
        logger.info(f"Associating deal {deal_id} with contact {contact_email}")
        
        # First, find the contact by email
        contacts = self.search_contacts(contact_email)
        if not contacts:
            logger.warning(f"Contact not found for email: {contact_email}")
            return
        
        contact_id = contacts[0]['id']
        
        # Create association
        association_payload = {
            "inputs": [{
                "from": {"id": deal_id},
                "to": {"id": contact_id},
                "type": "deal_to_contact"
            }]
        }
        
        try:
            response = requests.put(
                f"{self.base_url}/crm/v3/objects/deals/{deal_id}/associations/contacts/{contact_id}",
                headers=self.headers,
                params=self.api_key_param,
                json=association_payload
            )
            response.raise_for_status()
            
            logger.info(f"Deal {deal_id} associated with contact {contact_id}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error associating deal with contact: {e}")
            raise
    
    def get_deals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent deals
        
        Args:
            limit: Maximum number of deals to return
            
        Returns:
            List of deals
        """
        logger.info(f"Getting {limit} recent deals")
        
        try:
            response = requests.get(
                f"{self.base_url}/crm/v3/objects/deals?limit={limit}",
                headers=self.headers,
                params=self.api_key_param
            )
            response.raise_for_status()
            
            result = response.json()
            deals = result.get("results", [])
            logger.info(f"Retrieved {len(deals)} deals")
            return deals
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting deals: {e}")
            raise
    
    def update_deal_stage(self, deal_id: str, stage: str) -> Dict[str, Any]:
        """
        Update a deal's stage
        
        Args:
            deal_id: HubSpot deal ID
            stage: New deal stage
            
        Returns:
            Updated deal data
        """
        logger.info(f"Updating deal {deal_id} stage to: {stage}")
        
        payload = {"properties": {"dealstage": stage}}
        
        try:
            response = requests.patch(
                f"{self.base_url}/crm/v3/objects/deals/{deal_id}",
                headers=self.headers,
                params=self.api_key_param,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Deal stage updated successfully: {deal_id}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating deal stage: {e}")
            raise
