"""
Twilio WhatsApp Webhook Routes
Handles incoming messages from Twilio
"""
from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from app.services.chatbot_service import chatbot_service

twilio_bp = Blueprint('twilio', __name__)


@twilio_bp.route('/twilio', methods=['POST'])
def twilio_webhook():
    """
    Handle incoming WhatsApp messages from Twilio
    
    Twilio sends POST request with form data:
    - From: Sender's WhatsApp number (whatsapp:+923001234567)
    - Body: Message text
    - MessageSid: Unique message ID
    """
    try:
        # Get message data from Twilio
        from_number = request.form.get('From', '')  # whatsapp:+923001234567
        message_body = request.form.get('Body', '')
        message_sid = request.form.get('MessageSid', '')
        
        # Clean phone number (remove 'whatsapp:' prefix)
        clean_number = from_number.replace('whatsapp:', '')
        
        print(f"📨 Incoming WhatsApp message from {clean_number}")
        print(f"💬 Message: {message_body}")
        print(f"🆔 Message SID: {message_sid}")
        
        # Process message with chatbot
        chatbot_service.process_message(
            from_number=clean_number,
            message_text=message_body,
            message_type='text'
        )
        
        # Twilio expects TwiML response (empty is fine, we send messages separately)
        resp = MessagingResponse()
        
        # Return empty TwiML (200 OK tells Twilio we received it)
        return str(resp), 200
        
    except Exception as e:
        print(f"❌ Error processing Twilio webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Still return 200 to Twilio to avoid retries
        resp = MessagingResponse()
        return str(resp), 200


@twilio_bp.route('/twilio/status', methods=['POST'])
def twilio_status_callback():
    """
    Handle message status callbacks from Twilio
    
    Optional endpoint for tracking message delivery status
    """
    try:
        message_sid = request.form.get('MessageSid', '')
        message_status = request.form.get('MessageStatus', '')
        
        print(f"📊 Message {message_sid} status: {message_status}")
        
        # You can update database here to track delivery status
        
        return '', 200
        
    except Exception as e:
        print(f"❌ Error processing status callback: {str(e)}")
        return '', 200


@twilio_bp.route('/twilio/test', methods=['POST'])
def twilio_test():
    """
    Test endpoint to simulate Twilio webhook
    
    POST /webhook/twilio/test
    {
        "from": "+923001234567",
        "message": "hi"
    }
    """
    try:
        data = request.get_json()
        from_number = data.get('from', '+923001234567')
        message = data.get('message', 'test')
        
        print(f"🧪 Test message from {from_number}: {message}")
        
        result = chatbot_service.process_message(
            from_number=from_number,
            message_text=message,
            message_type='text'
        )
        
        return {
            'status': 'success',
            'result': result,
            'message': 'Test message processed'
        }, 200
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }, 500


@twilio_bp.route('/twilio/health', methods=['GET'])
def twilio_health():
    """Health check for Twilio webhook"""
    return {
        'status': 'healthy',
        'service': 'Twilio WhatsApp Webhook',
        'version': '1.0.0'
    }, 200