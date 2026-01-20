"""
WhatsApp Service via Twilio
Handles sending messages via Twilio WhatsApp API
"""
from twilio.rest import Client
import os
from typing import Dict, List

class WhatsAppService:
    """Service for interacting with Twilio WhatsApp API"""
    
    def __init__(self):
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.client = Client(account_sid, auth_token)
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
    
    def send_text_message(self, to: str, message: str) -> Dict:
        """
        Send a text message via Twilio WhatsApp
        
        Args:
            to: Recipient phone number (format: +1234567890 or whatsapp:+1234567890)
            message: Message text
        
        Returns:
            Dict with message SID or error details
        """
        try:
            # Format phone number if needed
            if not to.startswith('whatsapp:'):
                to = f'whatsapp:{to}'
            
            message_obj = self.client.messages.create(
                from_=self.whatsapp_number,
                body=message,
                to=to
            )
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': 'sent'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }
    
    def send_interactive_buttons(self, to: str, body_text: str, buttons: List[Dict]) -> Dict:
        """
        Send interactive button message via Twilio
        
        Args:
            to: Recipient phone number
            body_text: Message body
            buttons: List of button objects [{"id": "btn_1", "title": "Button 1"}, ...]
        
        Returns:
            Dict with message SID or error details
        """
        try:
            if not to.startswith('whatsapp:'):
                to = f'whatsapp:{to}'
            
            # Twilio uses different format for interactive messages
            # Build the button payload
            button_text = "\n".join([f"{i+1}. {btn['title']}" for i, btn in enumerate(buttons[:3])])
            full_message = f"{body_text}\n\n{button_text}"
            
            message_obj = self.client.messages.create(
                from_=self.whatsapp_number,
                body=full_message,
                to=to
            )
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': 'sent'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }
    
    def send_interactive_list(self, to: str, body_text: str, button_text: str, sections: List[Dict]) -> Dict:
        """
        Send interactive list message via Twilio
        
        Args:
            to: Recipient phone number
            body_text: Message body
            button_text: Text for the list button
            sections: List of sections with rows
        
        Returns:
            Dict with message SID or error details
        """
        try:
            if not to.startswith('whatsapp:'):
                to = f'whatsapp:{to}'
            
            # Build list as numbered text for Twilio
            message_lines = [body_text, ""]
            
            for section in sections[:3]:  # Limit sections
                section_title = section.get('title', '')
                if section_title:
                    message_lines.append(f"**{section_title}**")
                
                rows = section.get('rows', [])
                for i, row in enumerate(rows[:10], 1):  # Limit rows
                    title = row.get('title', '')
                    description = row.get('description', '')
                    message_lines.append(f"{i}. {title}")
                    if description:
                        message_lines.append(f"   {description}")
                message_lines.append("")
            
            full_message = "\n".join(message_lines)
            
            message_obj = self.client.messages.create(
                from_=self.whatsapp_number,
                body=full_message,
                to=to
            )
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': 'sent'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }
    
    def send_template_message(self, to: str, template_name: str, parameters: List[str] = None) -> Dict:
        """
        Send a template message via Twilio
        Note: Twilio's template system works differently from Meta
        
        Args:
            to: Recipient phone number
            template_name: Name of the template (we'll use it as the message)
            parameters: Optional parameters to include
        
        Returns:
            Dict with message SID or error details
        """
        try:
            if not to.startswith('whatsapp:'):
                to = f'whatsapp:{to}'
            
            # For Twilio, we'll send a simple message
            # In production, you'd handle templates differently
            message_text = template_name
            if parameters:
                for param in parameters:
                    message_text += f"\n{param}"
            
            message_obj = self.client.messages.create(
                from_=self.whatsapp_number,
                body=message_text,
                to=to
            )
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': 'sent'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }


# Create singleton instance
whatsapp_service = WhatsAppService()
