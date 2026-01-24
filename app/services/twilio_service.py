"""
Twilio WhatsApp Service
Handles sending WhatsApp messages via Twilio API
"""
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from typing import Dict, List, Optional


class TwilioWhatsAppService:
    """
    Service for sending WhatsApp messages using Twilio
    """
    
    def __init__(self):
        """Initialize Twilio client"""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        
        # Check if credentials are provided
        if not self.account_sid or not self.auth_token:
            print("[WARN] WARNING: Twilio credentials not configured!")
            print("Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env")
            self.client = None
        else:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                print("[OK] Twilio WhatsApp Service initialized")
            except Exception as e:
                print(f"[ERROR] Error initializing Twilio client: {str(e)}")
                self.client = None
    
    
    def send_text_message(self, to: str, message: str) -> Dict:
        """
        Send a text message via WhatsApp
        
        Args:
            to: Recipient WhatsApp number (e.g., '+923001234567')
            message: Message text to send
            
        Returns:
            Response dictionary with status and message_id
        """
        try:
            # Ensure 'to' number has whatsapp: prefix
            if not to.startswith('whatsapp:'):
                to = f'whatsapp:{to}'
            
            # If no client (test mode), just log
            if not self.client:
                print(f"[TEST] Would send to {to}:")
                print(f"   {message[:100]}...")
                return {
                    'success': True,
                    'test_mode': True,
                    'message_id': 'test_' + str(hash(message))[:10]
                }
            
            # Send actual message
            twilio_message = self.client.messages.create(
                from_=self.from_number,
                body=message,
                to=to
            )
            
            print(f"[OK] Message sent to {to} (SID: {twilio_message.sid})")
            
            return {
                'success': True,
                'message_id': twilio_message.sid,
                'status': twilio_message.status,
                'to': to
            }
            
        except TwilioRestException as e:
            print(f"[ERROR] Twilio error sending to {to}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': e.code
            }
        except Exception as e:
            print(f"[ERROR] Error sending message to {to}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    
    def send_message_with_buttons(self, to: str, message: str, buttons: List[str]) -> Dict:
        """
        Send message with quick reply buttons
        
        Note: Twilio doesn't support interactive buttons like Meta API
        Instead, we append button options to the message
        
        Args:
            to: Recipient number
            message: Message text
            buttons: List of button texts (max 3)
            
        Returns:
            Response dictionary
        """
        # Format message with buttons as options
        formatted_message = message + "\n\n"
        
        for i, button in enumerate(buttons[:3], 1):
            formatted_message += f"{i}. {button}\n"
        
        formatted_message += "\nReply with number or text"
        
        return self.send_text_message(to, formatted_message)
    
    
    def send_message_with_list(self, to: str, header: str, items: List[Dict]) -> Dict:
        """
        Send message with list of options
        
        Args:
            to: Recipient number
            header: Message header
            items: List of items with 'title' and optional 'description'
            
        Returns:
            Response dictionary
        """
        # Format as numbered list
        formatted_message = header + "\n\n"
        
        for i, item in enumerate(items, 1):
            title = item.get('title', f'Option {i}')
            description = item.get('description', '')
            
            formatted_message += f"{i}. {title}\n"
            if description:
                formatted_message += f"   {description}\n"
            formatted_message += "\n"
        
        formatted_message += "Reply with number or item name"
        
        return self.send_text_message(to, formatted_message)
    
    
    def send_media_message(self, to: str, message: str, media_url: str) -> Dict:
        """
        Send message with media (image, video, document)
        
        Args:
            to: Recipient number
            message: Caption/message text
            media_url: Public URL of media file
            
        Returns:
            Response dictionary
        """
        try:
            if not to.startswith('whatsapp:'):
                to = f'whatsapp:{to}'
            
            if not self.client:
                print(f"📤 [TEST MODE] Would send media to {to}")
                print(f"   Message: {message}")
                print(f"   Media: {media_url}")
                return {'success': True, 'test_mode': True}
            
            twilio_message = self.client.messages.create(
                from_=self.from_number,
                body=message,
                media_url=[media_url],
                to=to
            )
            
            print(f"✅ Media message sent to {to}")
            
            return {
                'success': True,
                'message_id': twilio_message.sid,
                'status': twilio_message.status
            }
            
        except Exception as e:
            print(f"❌ Error sending media to {to}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    
    def get_message_status(self, message_sid: str) -> Optional[str]:
        """
        Get status of a sent message
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            Message status or None
        """
        try:
            if not self.client:
                return 'test_mode'
            
            message = self.client.messages(message_sid).fetch()
            return message.status
            
        except Exception as e:
            print(f"❌ Error fetching message status: {str(e)}")
            return None


# Create singleton instance
twilio_whatsapp_service = TwilioWhatsAppService()