"""
Chatbot Service
Handles conversation flow, user state management, and order processing
UPDATED VERSION - Works with both Twilio and Meta WhatsApp
"""
from app.utils.supabase_client import supabase_client
from typing import Dict, List, Optional
import json
import os

# Import appropriate messaging service based on configuration
if os.getenv('USE_TWILIO', 'false').lower() == 'true':
    from app.services.twilio_service import twilio_whatsapp_service as messaging_service
    print("✅ Using Twilio WhatsApp Service")
else:
    from app.services.whatsapp_service import whatsapp_service as messaging_service
    print("✅ Using Meta WhatsApp Service")

# Import notification service
from app.services.notification_service import notification_service


class ChatbotService:
    """
    Manages chatbot conversation logic and state
    Compatible with both Twilio and Meta WhatsApp APIs
    """
    
    # Conversation states
    STATE_IDLE = 'idle'
    STATE_BROWSING_MENU = 'browsing_menu'
    STATE_VIEWING_CATEGORY = 'viewing_category'
    STATE_ADDING_TO_CART = 'adding_to_cart'
    STATE_VIEWING_CART = 'viewing_cart'
    STATE_CONFIRMING_ORDER = 'confirming_order'
    STATE_PAYMENT = 'payment'
    
    def __init__(self):
        self.supabase = supabase_client
        self.messaging = messaging_service
    
    
    def process_message(self, from_number: str, message_text: str, message_type: str = 'text') -> Dict:
        """
        Main entry point for processing incoming messages
        
        Args:
            from_number: User's WhatsApp number
            message_text: The message content
            message_type: Type of message (text, interactive, etc.)
        
        Returns:
            Response dictionary with status and actions taken
        """
        try:
            # Get or create user
            student = self._get_or_create_student(from_number)
            
            # Get user session
            session = self._get_or_create_session(student['id'])
            
            # Process based on message content
            message_lower = message_text.lower().strip()
            
            # Handle main menu commands
            if message_lower in ['hi', 'hello', 'start', 'menu', 'order']:
                return self._send_main_menu(from_number, student)
            
            elif message_lower in ['cart', 'view cart', 'my cart']:
                return self._send_cart(from_number, session)
            
            elif message_lower in ['help', 'commands']:
                return self._send_help(from_number)
            
            elif message_lower.startswith('cancel'):
                return self._cancel_order(from_number, session)
            
            # Handle order tracking
            elif message_lower.startswith('track') or message_lower.startswith('status'):
                return self._handle_track_command(from_number, message_lower, student)
            
            # Handle "my orders"
            elif message_lower in ['my orders', 'orders', 'history']:
                return self._send_order_history(from_number, student)
            
            # Handle based on current state
            current_state = session.get('current_state', self.STATE_IDLE)
            
            if current_state == self.STATE_IDLE:
                return self._send_main_menu(from_number, student)
            
            elif current_state == self.STATE_BROWSING_MENU:
                return self._handle_menu_selection(from_number, message_text, session)
            
            elif current_state == self.STATE_VIEWING_CATEGORY:
                return self._handle_item_selection(from_number, message_text, session)
            
            elif current_state == self.STATE_ADDING_TO_CART:
                return self._handle_quantity_selection(from_number, message_text, session)
            
            elif current_state == self.STATE_VIEWING_CART:
                return self._handle_cart_action(from_number, message_text, session)
            
            elif current_state == self.STATE_CONFIRMING_ORDER:
                return self._handle_order_confirmation(from_number, message_text, session)
            
            else:
                return self._send_main_menu(from_number, student)
        
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            import traceback
            traceback.print_exc()
            self.messaging.send_text_message(
                from_number,
                "Sorry, something went wrong. Please try again or type 'menu' to start over."
            )
            return {'status': 'error', 'message': str(e)}
    
    
    def _get_or_create_student(self, whatsapp_number: str) -> Dict:
        """Get existing student or create new one"""
        try:
            # Check if student exists
            response = self.supabase.table('students').select('*').eq(
                'whatsapp_number', whatsapp_number
            ).execute()
            
            if response.data:
                return response.data[0]
            
            # Create new student
            new_student = {
                'whatsapp_number': whatsapp_number,
                'name': None
            }
            response = self.supabase.table('students').insert(new_student).execute()
            return response.data[0]
        
        except Exception as e:
            print(f"Error getting/creating student: {str(e)}")
            raise
    
    
    def _get_or_create_session(self, student_id: int) -> Dict:
        """Get existing session or create new one"""
        try:
            # Check if session exists
            response = self.supabase.table('user_sessions').select('*').eq(
                'student_id', student_id
            ).execute()
            
            if response.data:
                return response.data[0]
            
            # Create new session
            new_session = {
                'student_id': student_id,
                'current_state': self.STATE_IDLE,
                'cart': [],
                'session_data': {}
            }
            response = self.supabase.table('user_sessions').insert(new_session).execute()
            return response.data[0]
        
        except Exception as e:
            print(f"Error getting/creating session: {str(e)}")
            raise
    
    
    def _update_session(self, session_id: int, updates: Dict) -> Dict:
        """Update session data"""
        try:
            response = self.supabase.table('user_sessions').update(updates).eq(
                'id', session_id
            ).execute()
            return response.data[0]
        except Exception as e:
            print(f"Error updating session: {str(e)}")
            raise
    
    
    def _send_main_menu(self, to_number: str, student: Dict) -> Dict:
        """Send main menu with categories"""
        try:
            # Get all categories
            response = self.supabase.table('menu_items').select('category').execute()
            
            categories = list(set([item['category'] for item in response.data]))
            
            # Prepare message
            greeting = f"Welcome to University Café! 🍔☕\n\n"
            if student.get('name'):
                greeting = f"Hi {student['name']}! Welcome back! 🍔☕\n\n"
            
            message = greeting + "What would you like to order today?\n\nSelect a category:\n\n"
            
            # Add categories as numbered list
            for i, category in enumerate(categories, 1):
                message += f"{i}. {category}\n"
            
            message += "\nReply with number or category name"
            
            # Send message
            self.messaging.send_text_message(to_number, message)
            
            # Update session state
            self._update_session(
                self._get_or_create_session(student['id'])['id'],
                {'current_state': self.STATE_BROWSING_MENU}
            )
            
            return {'status': 'success', 'action': 'main_menu_sent'}
        
        except Exception as e:
            print(f"Error sending main menu: {str(e)}")
            raise
    
    
    def _handle_menu_selection(self, to_number: str, selection: str, session: Dict) -> Dict:
        """Handle category selection"""
        try:
            # Get all categories
            response = self.supabase.table('menu_items').select('category').execute()
            categories = list(set([item['category'] for item in response.data]))
            
            # Parse selection (number or name)
            category = None
            try:
                # Try as number first
                index = int(selection.strip()) - 1
                if 0 <= index < len(categories):
                    category = categories[index]
            except ValueError:
                # Try as category name
                for cat in categories:
                    if selection.lower() in cat.lower():
                        category = cat
                        break
            
            if not category:
                self.messaging.send_text_message(
                    to_number,
                    "Invalid selection. Please type 'menu' to see categories again."
                )
                return {'status': 'error', 'message': 'Invalid category'}
            
            # Get menu items for selected category
            response = self.supabase.table('menu_items').select('*').eq(
                'category', category
            ).eq('available', True).execute()
            
            if not response.data:
                self.messaging.send_text_message(
                    to_number,
                    f"No items found in {category}. Please select another category or type 'menu'."
                )
                return {'status': 'error', 'message': 'No items found'}
            
            # Format menu items
            message = f"📋 {category}\n\n"
            
            for i, item in enumerate(response.data, 1):
                message += f"{i}. {item['name']} - PKR {item['price']}\n"
                if item.get('description'):
                    message += f"   {item['description']}\n"
                message += "\n"
            
            message += "💡 Reply with number or item name to add to cart\n"
            message += "Or type 'menu' to see all categories"
            
            self.messaging.send_text_message(to_number, message)
            
            # Update session
            self._update_session(session['id'], {
                'current_state': self.STATE_VIEWING_CATEGORY,
                'session_data': {'current_category': category, 'items': response.data}
            })
            
            return {'status': 'success', 'action': 'category_items_sent'}
        
        except Exception as e:
            print(f"Error handling menu selection: {str(e)}")
            raise
    
    
    def _handle_item_selection(self, to_number: str, selection: str, session: Dict) -> Dict:
        """Handle item selection from category"""
        try:
            session_data = session.get('session_data', {})
            items = session_data.get('items', [])
            
            # Find selected item (by number or name)
            selected_item = None
            
            try:
                # Try as number first
                index = int(selection.strip()) - 1
                if 0 <= index < len(items):
                    selected_item = items[index]
            except ValueError:
                # Try as item name
                for item in items:
                    if selection.lower() in item['name'].lower():
                        selected_item = item
                        break
            
            if not selected_item:
                self.messaging.send_text_message(
                    to_number,
                    "Item not found. Please reply with the correct item number or name."
                )
                return {'status': 'error', 'message': 'Item not found'}
            
            # Ask for quantity
            message = f"Great choice! 🎉\n\n"
            message += f"📦 {selected_item['name']}\n"
            message += f"💰 PKR {selected_item['price']}\n\n"
            message += "How many would you like? (Reply with a number)"
            
            self.messaging.send_text_message(to_number, message)
            
            # Update session
            session_data['selected_item'] = selected_item
            self._update_session(session['id'], {
                'current_state': self.STATE_ADDING_TO_CART,
                'session_data': session_data
            })
            
            return {'status': 'success', 'action': 'quantity_requested'}
        
        except Exception as e:
            print(f"Error handling item selection: {str(e)}")
            raise
    
    
    def _handle_quantity_selection(self, to_number: str, quantity_text: str, session: Dict) -> Dict:
        """Handle quantity input and add to cart"""
        try:
            # Parse quantity
            try:
                quantity = int(quantity_text.strip())
                if quantity <= 0:
                    raise ValueError
            except ValueError:
                self.messaging.send_text_message(
                    to_number,
                    "Please enter a valid number (e.g., 1, 2, 3)"
                )
                return {'status': 'error', 'message': 'Invalid quantity'}
            
            # Get selected item from session
            session_data = session.get('session_data', {})
            selected_item = session_data.get('selected_item')
            
            if not selected_item:
                return self._send_main_menu(to_number, self._get_or_create_student(to_number))
            
            # Add to cart
            cart = session.get('cart', [])
            if isinstance(cart, str):
                cart = json.loads(cart)
            
            # Check if item already in cart
            item_exists = False
            for cart_item in cart:
                if cart_item['menu_item_id'] == selected_item['id']:
                    cart_item['quantity'] += quantity
                    cart_item['subtotal'] = cart_item['quantity'] * selected_item['price']
                    item_exists = True
                    break
            
            if not item_exists:
                cart.append({
                    'menu_item_id': selected_item['id'],
                    'name': selected_item['name'],
                    'price': selected_item['price'],
                    'quantity': quantity,
                    'subtotal': quantity * selected_item['price']
                })
            
            # Update session
            self._update_session(session['id'], {
                'cart': cart,
                'current_state': self.STATE_IDLE,
                'session_data': {}
            })
            
            # Send confirmation
            message = f"✅ Added to cart!\n\n"
            message += f"{quantity}x {selected_item['name']} - PKR {quantity * selected_item['price']}\n\n"
            message += "What would you like to do next?\n\n"
            message += "Type:\n"
            message += "'menu' - Continue ordering\n"
            message += "'cart' - View your cart\n"
            message += "'checkout' - Place order"
            
            self.messaging.send_text_message(to_number, message)
            
            return {'status': 'success', 'action': 'item_added_to_cart'}
        
        except Exception as e:
            print(f"Error handling quantity: {str(e)}")
            raise
    
    
    def _send_cart(self, to_number: str, session: Dict) -> Dict:
        """Display current cart"""
        try:
            cart = session.get('cart', [])
            if isinstance(cart, str):
                cart = json.loads(cart)
            
            if not cart:
                message = "🛒 Your cart is empty!\n\nType 'menu' to start ordering."
                self.messaging.send_text_message(to_number, message)
                return {'status': 'success', 'action': 'empty_cart_sent'}
            
            # Format cart
            message = "🛒 Your Cart:\n\n"
            total = 0
            
            for item in cart:
                message += f"🔹 {item['quantity']}x {item['name']}\n"
                message += f"   PKR {item['subtotal']}\n\n"
                total += item['subtotal']
            
            message += f"━━━━━━━━━━━━━━━━━━━\n"
            message += f"💰 Total: PKR {total}\n\n"
            message += "What would you like to do?\n\n"
            message += "Type:\n"
            message += "'checkout' - Place order\n"
            message += "'menu' - Add more items\n"
            message += "'clear cart' - Empty cart"
            
            self.messaging.send_text_message(to_number, message)
            
            # Update state
            self._update_session(session['id'], {
                'current_state': self.STATE_VIEWING_CART
            })
            
            return {'status': 'success', 'action': 'cart_sent'}
        
        except Exception as e:
            print(f"Error sending cart: {str(e)}")
            raise
    
    
    def _handle_cart_action(self, to_number: str, action: str, session: Dict) -> Dict:
        """Handle actions from cart view"""
        action_lower = action.lower().strip()
        
        if action_lower in ['checkout', 'order', 'confirm']:
            return self._start_checkout(to_number, session)
        
        elif action_lower in ['clear', 'clear cart', 'empty']:
            self._update_session(session['id'], {
                'cart': [],
                'current_state': self.STATE_IDLE
            })
            self.messaging.send_text_message(
                to_number,
                "🗑️ Cart cleared! Type 'menu' to start a new order."
            )
            return {'status': 'success', 'action': 'cart_cleared'}
        
        elif action_lower in ['menu', 'add more']:
            student = self._get_or_create_student(to_number)
            return self._send_main_menu(to_number, student)
        
        else:
            return self._send_cart(to_number, session)
    
    
    def _start_checkout(self, to_number: str, session: Dict) -> Dict:
        """Start checkout process"""
        try:
            cart = session.get('cart', [])
            if isinstance(cart, str):
                cart = json.loads(cart)
            
            if not cart:
                self.messaging.send_text_message(
                    to_number,
                    "Your cart is empty! Type 'menu' to start ordering."
                )
                return {'status': 'error', 'message': 'Empty cart'}
            
            # Calculate total
            total = sum(item['subtotal'] for item in cart)
            
            # Send order summary
            message = "📋 Order Summary:\n\n"
            for item in cart:
                message += f"{item['quantity']}x {item['name']} - PKR {item['subtotal']}\n"
            message += f"\n💰 Total: PKR {total}\n\n"
            message += "Confirm your order?\n\n"
            message += "Type 'YES' to confirm or 'NO' to cancel"
            
            self.messaging.send_text_message(to_number, message)
            
            # Update state
            self._update_session(session['id'], {
                'current_state': self.STATE_CONFIRMING_ORDER
            })
            
            return {'status': 'success', 'action': 'checkout_started'}
        
        except Exception as e:
            print(f"Error starting checkout: {str(e)}")
            raise
    
    
    def _handle_order_confirmation(self, to_number: str, response: str, session: Dict) -> Dict:
        """Handle order confirmation"""
        try:
            response_lower = response.lower().strip()
            
            if response_lower in ['yes', 'confirm', 'ok', 'y']:
                return self._create_order(to_number, session)
            
            elif response_lower in ['no', 'cancel', 'n']:
                self.messaging.send_text_message(
                    to_number,
                    "Order cancelled. Type 'cart' to modify or 'menu' to continue shopping."
                )
                self._update_session(session['id'], {
                    'current_state': self.STATE_VIEWING_CART
                })
                return {'status': 'success', 'action': 'order_cancelled'}
            
            else:
                self.messaging.send_text_message(
                    to_number,
                    "Please type 'YES' to confirm or 'NO' to cancel."
                )
                return {'status': 'pending', 'action': 'awaiting_confirmation'}
        
        except Exception as e:
            print(f"Error handling confirmation: {str(e)}")
            raise
    
    
    def _create_order(self, to_number: str, session: Dict) -> Dict:
        """Create order in database"""
        try:
            cart = session.get('cart', [])
            if isinstance(cart, str):
                cart = json.loads(cart)
            
            student = self._get_or_create_student(to_number)
            total = sum(item['subtotal'] for item in cart)
            
            # Create order
            order_data = {
                'student_id': student['id'],
                'total': total,
                'status': 'pending'
            }
            
            order_response = self.supabase.table('orders').insert(order_data).execute()
            order = order_response.data[0]
            
            # Create order items
            order_items = []
            for item in cart:
                order_items.append({
                    'order_id': order['id'],
                    'menu_item_id': item['menu_item_id'],
                    'quantity': item['quantity'],
                    'subtotal': item['subtotal']
                })
            
            self.supabase.table('order_items').insert(order_items).execute()
            
            # Send confirmation message
            message = f"✅ Order Placed Successfully!\n\n"
            message += f"🔖 Order ID: #{order['id']}\n"
            message += f"💰 Total: PKR {total}\n\n"
            message += f"Your order is being prepared! 👨‍🍳\n"
            message += f"We'll notify you when it's ready for pickup.\n\n"
            message += f"💡 Track your order: type 'track {order['id']}'\n"
            message += f"Thank you for ordering! 🙏"
            
            self.messaging.send_text_message(to_number, message)
            
            # Clear cart and reset state
            self._update_session(session['id'], {
                'cart': [],
                'current_state': self.STATE_IDLE,
                'session_data': {}
            })
            
            # Notify staff about new order
            notification_service.notify_staff_new_order(order['id'])
            
            return {
                'status': 'success',
                'action': 'order_created',
                'order_id': order['id']
            }
        
        except Exception as e:
            print(f"Error creating order: {str(e)}")
            import traceback
            traceback.print_exc()
            self.messaging.send_text_message(
                to_number,
                "Sorry, there was an error processing your order. Please try again."
            )
            raise
    
    
    def _handle_track_command(self, to_number: str, message: str, student: Dict) -> Dict:
        """Handle order tracking command"""
        try:
            # Extract order ID if provided
            parts = message.split()
            order_id = None
            
            if len(parts) > 1:
                try:
                    order_id = int(parts[1])
                except ValueError:
                    pass
            
            # If no order ID, get latest order
            if not order_id:
                response = self.supabase.table('orders').select('id').eq(
                    'student_id', student['id']
                ).order('created_at', desc=True).limit(1).execute()
                
                if not response.data:
                    self.messaging.send_text_message(
                        to_number,
                        "You haven't placed any orders yet.\n\nType 'menu' to start ordering!"
                    )
                    return {'status': 'success', 'action': 'no_orders'}
                
                order_id = response.data[0]['id']
            
            # Send tracking info
            notification_service.send_order_tracking_info(to_number, order_id)
            
            return {'status': 'success', 'action': 'tracking_sent', 'order_id': order_id}
            
        except Exception as e:
            print(f"Error handling track command: {str(e)}")
            import traceback
            traceback.print_exc()
            self.messaging.send_text_message(
                to_number,
                "Sorry, couldn't retrieve order status. Please try again."
            )
            return {'status': 'error', 'message': str(e)}
    
    
    def _send_order_history(self, to_number: str, student: Dict) -> Dict:
        """Send user's order history"""
        try:
            # Get last 5 orders
            response = self.supabase.table('orders').select(
                'id, total, status, created_at'
            ).eq('student_id', student['id']).order(
                'created_at', desc=True
            ).limit(5).execute()
            
            orders = response.data
            
            if not orders:
                message = "📦 You haven't placed any orders yet.\n\n"
                message += "Type 'menu' to start your first order!"
                self.messaging.send_text_message(to_number, message)
                return {'status': 'success', 'action': 'no_history'}
            
            message = "📜 Your Recent Orders:\n\n"
            
            status_emoji = {
                'pending': '⏳',
                'confirmed': '✅',
                'preparing': '👨‍🍳',
                'ready': '🎉',
                'completed': '✅',
                'cancelled': '❌'
            }
            
            for order in orders:
                emoji = status_emoji.get(order['status'], '📦')
                message += f"{emoji} Order #{order['id']}\n"
                message += f"   PKR {order['total']} • {order['status'].upper()}\n\n"
            
            message += "💡 Type 'track [order_id]' to see details\n"
            message += "Example: track " + str(orders[0]['id'])
            
            self.messaging.send_text_message(to_number, message)
            
            return {'status': 'success', 'action': 'history_sent'}
            
        except Exception as e:
            print(f"Error sending order history: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'status': 'error', 'message': str(e)}
    
    
    def _cancel_order(self, to_number: str, session: Dict) -> Dict:
        """Cancel current order/session"""
        self._update_session(session['id'], {
            'cart': [],
            'current_state': self.STATE_IDLE,
            'session_data': {}
        })
        
        self.messaging.send_text_message(
            to_number,
            "Order cancelled. Type 'menu' to start a new order."
        )
        
        return {'status': 'success', 'action': 'order_cancelled'}
    
    
    def _send_help(self, to_number: str) -> Dict:
        """Send help message"""
        message = "🤖 University Café Bot Help\n\n"
        message += "Available commands:\n\n"
        message += "📋 'menu' - View menu categories\n"
        message += "🛒 'cart' - View your cart\n"
        message += "💳 'checkout' - Place order\n"
        message += "📍 'track [id]' - Track order status\n"
        message += "📜 'my orders' - View order history\n"
        message += "❌ 'cancel' - Cancel current order\n"
        message += "❓ 'help' - Show this message\n\n"
        message += "Just chat naturally and I'll guide you through! 😊"
        
        self.messaging.send_text_message(to_number, message)
        
        return {'status': 'success', 'action': 'help_sent'}


# Create singleton instance
chatbot_service = ChatbotService()