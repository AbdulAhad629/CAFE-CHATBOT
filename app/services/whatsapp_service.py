"""
WhatsApp Service
Handles sending messages via WhatsApp Cloud API
"""
import requests
import os
from typing import Dict, List

class WhatsAppService:
    """Service for interacting with WhatsApp Cloud API"""
    
    def __init__(self):
        self.api_url = os.getenv('WHATSAPP_API_URL')
        self.access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def send_text_message(self, to: str, message: str) -> Dict:
        """
        Send a text message
        
        Args:
            to: Recipient phone number
            message: Message text
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()
    
    def send_interactive_buttons(self, to: str, body_text: str, buttons: List[Dict]) -> Dict:
        """
        Send interactive button message
        
        Args:
            to: Recipient phone number
            body_text: Message body
            buttons: List of button objects [{"id": "btn_1", "title": "Button 1"}, ...]
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        button_components = []
        for btn in buttons[:3]:  # WhatsApp allows max 3 buttons
            button_components.append({
                "type": "reply",
                "reply": {
                    "id": btn['id'],
                    "title": btn['title']
                }
            })
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body_text
                },
                "action": {
                    "buttons": button_components
                }
            }
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()
    
    def send_interactive_list(self, to: str, body_text: str, button_text: str, sections: List[Dict]) -> Dict:
        """
        Send interactive list message
        
        Args:
            to: Recipient phone number
            body_text: Message body
            button_text: Text for the list button
            sections: List of sections with rows
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body_text
                },
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()
    
    def send_template_message(self, to: str, template_name: str, language_code: str = "en") -> Dict:
        """
        Send a template message
        
        Args:
            to: Recipient phone number
            template_name: Name of the approved template
            language_code: Language code (default: en)
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()


# Create singleton instance
whatsapp_service = WhatsAppService()
