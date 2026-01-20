"""
WhatsApp Webhook Routes
Handles incoming messages from WhatsApp Cloud API
"""
from flask import Blueprint, request, jsonify
from app.services.chatbot_service import chatbot_service
import os

whatsapp_bp = Blueprint('whatsapp', __name__)

@whatsapp_bp.route('/whatsapp', methods=['GET'])
def verify_webhook():
    """
    Verify webhook endpoint for WhatsApp Cloud API
    This is called by Meta to verify your webhook URL
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN')
    
    if mode == 'subscribe' and token == verify_token:
        print("✅ Webhook verified successfully!")
        return challenge, 200
    else:
        print("❌ Webhook verification failed!")
        return 'Forbidden', 403


@whatsapp_bp.route('/whatsapp', methods=['POST'])
def webhook():
    """
    Handle incoming WhatsApp messages
    This endpoint receives all messages sent to your WhatsApp Business number
    """
    try:
        data = request.get_json()
        
        # Log incoming webhook data for debugging
        print("📥 Incoming webhook:", data)
        
        # Check if it's a WhatsApp Business Account event
        if data.get('object') != 'whatsapp_business_account':
            return jsonify({'status': 'ignored', 'reason': 'not_whatsapp_event'}), 200
        
        entries = data.get('entry', [])
        
        for entry in entries:
            changes = entry.get('changes', [])
            
            for change in changes:
                value = change.get('value', {})
                
                # Handle status updates (message delivered, read, etc.)
                if 'statuses' in value:
                    statuses = value.get('statuses', [])
                    for status in statuses:
                        print(f"📊 Message status: {status.get('status')} for {status.get('id')}")
                    continue
                
                # Handle incoming messages
                messages = value.get('messages', [])
                
                for message in messages:
                    # Extract message details
                    from_number = message.get('from')
                    message_id = message.get('id')
                    message_type = message.get('type')
                    timestamp = message.get('timestamp')
                    
                    print(f"📨 Message from {from_number} (type: {message_type})")
                    
                    # Handle text messages
                    if message_type == 'text':
                        text_body = message.get('text', {}).get('body', '')
                        print(f"💬 Text: {text_body}")
                        
                        # Process message with chatbot
                        chatbot_service.process_message(
                            from_number=from_number,
                            message_text=text_body,
                            message_type='text'
                        )
                    
                    # Handle interactive messages (button clicks, list selections)
                    elif message_type == 'interactive':
                        interactive = message.get('interactive', {})
                        interactive_type = interactive.get('type')
                        
                        if interactive_type == 'button_reply':
                            # User clicked a button
                            button_reply = interactive.get('button_reply', {})
                            button_id = button_reply.get('id', '')
                            button_title = button_reply.get('title', '')
                            
                            print(f"🔘 Button clicked: {button_title} (ID: {button_id})")
                            
                            # Process button click
                            chatbot_service.process_message(
                                from_number=from_number,
                                message_text=button_title,
                                message_type='interactive'
                            )
                        
                        elif interactive_type == 'list_reply':
                            # User selected from a list
                            list_reply = interactive.get('list_reply', {})
                            list_id = list_reply.get('id', '')
                            list_title = list_reply.get('title', '')
                            
                            print(f"📋 List item selected: {list_title} (ID: {list_id})")
                            
                            # Process list selection
                            chatbot_service.process_message(
                                from_number=from_number,
                                message_text=list_id if list_id else list_title,
                                message_type='interactive'
                            )
                    
                    # Handle image messages (optional - for future features)
                    elif message_type == 'image':
                        image = message.get('image', {})
                        image_id = image.get('id', '')
                        caption = image.get('caption', '')
                        
                        print(f"🖼️ Image received: {image_id}")
                        # For now, just acknowledge
                        # TODO: Handle image uploads if needed
                    
                    # Handle location messages (optional - for delivery features)
                    elif message_type == 'location':
                        location = message.get('location', {})
                        latitude = location.get('latitude')
                        longitude = location.get('longitude')
                        
                        print(f"📍 Location received: {latitude}, {longitude}")
                        # TODO: Handle location if implementing delivery
                    
                    else:
                        print(f"⚠️ Unsupported message type: {message_type}")
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@whatsapp_bp.route('/test-message', methods=['POST'])
def test_message():
    """
    Test endpoint to simulate incoming messages
    Use this for testing without actual WhatsApp setup
    
    Example request:
    POST /webhook/test-message
    {
        "from": "+923001234567",
        "message": "menu"
    }
    """
    try:
        data = request.get_json()
        from_number = data.get('from', '+923001234567')
        message_text = data.get('message', 'menu')
        
        print(f"🧪 Test message from {from_number}: {message_text}")
        
        result = chatbot_service.process_message(
            from_number=from_number,
            message_text=message_text,
            message_type='text'
        )
        
        return jsonify({
            'status': 'success',
            'result': result,
            'message': 'Test message processed'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@whatsapp_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring
    """
    return jsonify({
        'status': 'healthy',
        'service': 'WhatsApp Webhook',
        'version': '1.0.0'
    }), 200