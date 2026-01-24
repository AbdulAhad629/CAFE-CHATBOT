"""
Chatbot Service - COMPLETE WITH PAYMENT INTEGRATION
Location: app/services/chatbot_service.py

FEATURES:
- Groq AI with conversation memory
- Natural language understanding
- Payment integration (Cash, JazzCash, EasyPaisa, Card)
- Order management
- Staff dashboard support
- Bilingual (English + Roman Urdu)

REPLACE YOUR CURRENT chatbot_service.py WITH THIS FILE
"""

from app.utils.supabase_client import supabase_client
from typing import Dict, List, Optional
import json
import os
import re
import time
import threading

# Import appropriate messaging service based on configuration
if os.getenv('USE_TWILIO', 'false').lower() == 'true':
    from app.services.twilio_service import twilio_whatsapp_service as messaging_service
    print("[OK] Using Twilio WhatsApp Service")
else:
    from app.services.whatsapp_service import whatsapp_service as messaging_service
    print("[OK] Using Meta WhatsApp Service")

# Import notification service
from app.services.notification_service import notification_service

# Import Groq service
try:
    from app.services.groq_service import groq_service
    GROQ_AVAILABLE = True
    print("[OK] Groq service loaded")
except ImportError:
    GROQ_AVAILABLE = False
    print("[WARN] Groq service not available - using rule-based only")

# Import Payment service
try:
    from app.services.payment_service import payment_service
    PAYMENT_AVAILABLE = True
    print("[✅ OK] Payment service loaded successfully")
except ImportError as e:
    PAYMENT_AVAILABLE = False
    print(f"[⚠️  WARN] Payment service import failed: {str(e)}")
except Exception as e:
    PAYMENT_AVAILABLE = False
    print(f"[❌ ERROR] Payment service error: {str(e)}")


class ChatbotService:
    """
    Manages chatbot conversation with AI enhancement via Groq API
    Compatible with both Twilio and Meta WhatsApp APIs
    Now includes payment integration
    """
    
    # Conversation states
    STATE_IDLE = 'idle'
    STATE_BROWSING_MENU = 'browsing_menu'
    STATE_VIEWING_CATEGORY = 'viewing_category'
    STATE_ADDING_TO_CART = 'adding_to_cart'
    STATE_VIEWING_CART = 'viewing_cart'
    STATE_SELECTING_PAYMENT = 'selecting_payment'
    STATE_CONFIRMING_ORDER = 'confirming_order'
    STATE_PROCESSING_PAYMENT = 'processing_payment'
    
    def __init__(self):
        self.supabase = supabase_client
        self.messaging = messaging_service
        
        # Check if we should use Groq
        self.use_groq = (
            GROQ_AVAILABLE and 
            os.getenv('USE_GROQ_API', 'true').lower() == 'true' and
            groq_service.is_available()
        )
        
        # Check if payment is available
        self.use_payment = PAYMENT_AVAILABLE
        
        # Menu mapping for quick lookups
        self.menu_keywords = {
            'burger': ['burger', 'chicken burger', 'beef burger', 'zinger'],
            'coffee': ['coffee', 'cold coffee', 'chai', 'tea'],
            'pizza': ['pizza', 'margherita', 'pepperoni'],
            'fries': ['fries', 'french fries'],
            'nuggets': ['nuggets', 'chicken nuggets']
        }
        
        print(f"[BOT] Chatbot Service initialized")
        print(f"   Groq API: {'Enabled ✅' if self.use_groq else 'Disabled ⚠️'}")
        print(f"   Payment: {'Enabled ✅' if self.use_payment else 'Cash Only ⚠️'}")
    
    
    def get_health_status(self) -> Dict:
        """
        Get health status of chatbot service
        Used by health check endpoint
        """
        groq_health = groq_service.health_check() if self.use_groq else {'status': 'disabled'}
        
        return {
            'chatbot': 'healthy',
            'groq': groq_health['status'],
            'payment': 'healthy' if self.use_payment else 'disabled',
            'messaging': 'healthy',
            'database': 'healthy'
        }
    
    
    def process_message(self, from_number: str, message_text: str, message_type: str = 'text') -> Dict:
        """
        Main entry point for processing incoming messages
        Prioritizes natural conversation via Groq AI while handling orders intelligently
        """
        try:
            # Get or create user
            student = self._get_or_create_student(from_number)
            
            # Get user session
            session = self._get_or_create_session(student['id'])
            
            # Clean message
            message_text = message_text.strip()
            message_lower = message_text.lower()
            
            print(f"📨 Message from {from_number}: {message_text}")
            
            # ========================================
            # PRIORITY 1: CRITICAL COMMANDS (Always rule-based)
            # ========================================
            
            # Cart operations
            if message_lower in ['cart', 'view cart', 'my cart']:
                return self._send_cart(from_number, session)
            
            # Checkout operations
            elif message_lower in ['checkout', 'place order', 'order now']:
                return self._start_checkout(from_number, session)
            
            # Cancel
            elif message_lower.startswith('cancel'):
                return self._cancel_order(from_number, session)
            
            # Track order
            elif message_lower.startswith('track') or message_lower.startswith('status'):
                return self._handle_track_command(from_number, message_lower, student)
            
            # Order history
            elif message_lower in ['my orders', 'orders', 'history']:
                return self._send_order_history(from_number, student)
            
            # Menu command
            elif message_lower in ['menu', 'categories']:
                return self._send_main_menu(from_number, student)
            
            # Help command
            elif message_lower in ['help', 'commands']:
                return self._send_help(from_number)
            
            
            # ========================================
            # PRIORITY 2: STATE-BASED HANDLING
            # ========================================
            
            current_state = session.get('current_state', self.STATE_IDLE)
            
            if current_state == self.STATE_BROWSING_MENU:
                if self._looks_like_menu_response(message_lower):
                    return self._handle_menu_selection(from_number, message_text, session)
                else:
                    self._update_session(session['id'], {'current_state': self.STATE_IDLE})
            
            elif current_state == self.STATE_VIEWING_CATEGORY:
                if self._looks_like_item_response(message_lower):
                    return self._handle_item_selection(from_number, message_text, session)
                else:
                    self._update_session(session['id'], {'current_state': self.STATE_IDLE})
            
            elif current_state == self.STATE_ADDING_TO_CART:
                if self._looks_like_quantity_response(message_lower):
                    return self._handle_quantity_selection(from_number, message_text, session)
                else:
                    self._update_session(session['id'], {'current_state': self.STATE_IDLE})
            
            elif current_state == self.STATE_VIEWING_CART:
                if message_lower in ['checkout', 'place order', 'order now', 'clear', 'clear cart', 'empty', 'menu', 'add more']:
                    return self._handle_cart_action(from_number, message_text, session)
                else:
                    self._update_session(session['id'], {'current_state': self.STATE_IDLE})
            
            elif current_state == self.STATE_SELECTING_PAYMENT:
                # Handle payment method selection
                if message_lower in ['1', '2', '3', '4']:
                    return self._handle_payment_selection(from_number, message_text, session)
                else:
                    self._update_session(session['id'], {'current_state': self.STATE_IDLE})
            
            elif current_state == self.STATE_CONFIRMING_ORDER:
                if message_lower in ['yes', 'no', 'confirm', 'cancel', 'y', 'n']:
                    return self._handle_order_confirmation(from_number, message_text, session)
                else:
                    self._update_session(session['id'], {'current_state': self.STATE_IDLE})
            
            
            # ========================================
            # PRIORITY 3: NATURAL CONVERSATION VIA GROQ
            # ========================================
            
            if self.use_groq:
                try:
                    print("[BOT] Using Groq AI for natural conversation...")
                    
                    # Use chat_with_memory for better context
                    ai_response = groq_service.chat_with_memory(message_text, from_number)
                    
                    if ai_response:
                        # Check if the message had ordering intent
                        has_order_intent = self._is_order_intent(message_lower)
                        
                        # If ordering intent, also try to parse items
                        if has_order_intent:
                            items = self._parse_items_from_text(message_text)
                            
                            if items:
                                # Add items to cart AND send AI response
                                print(f"[BOT] Parsed {len(items)} items from message")
                                self.messaging.send_text_message(from_number, ai_response)
                                return self._add_items_to_cart(from_number, session, items)
                        
                        # If no order or couldn't parse, just send the conversational response
                        hint = ""
                        if has_order_intent:
                            hint = "\n\nType 'menu' to browse our menu, or just tell me what you want!"
                        else:
                            hint = "\n\n💡 Want to order? Type 'menu' or just say 'I want 2 burgers'!"
                        
                        self.messaging.send_text_message(from_number, ai_response + hint)
                        
                        return {'status': 'success', 'action': 'natural_conversation'}
                
                except Exception as e:
                    print(f"[WARN] Groq error: {e}")
                    import traceback
                    traceback.print_exc()
            
            
            # ========================================
            # FALLBACK: Rule-based handling
            # ========================================
            
            print("[BOT] Groq unavailable, using rule-based handling...")
            
            if self._is_order_intent(message_lower):
                items = self._parse_items_from_text(message_text)
                
                if items:
                    return self._add_items_to_cart(from_number, session, items)
                else:
                    return self._send_ordering_help(from_number)
            
            # Default: Show menu
            return self._send_main_menu(from_number, student)
        
        except Exception as e:
            print(f"❌ Error processing message: {str(e)}")
            import traceback
            traceback.print_exc()
            
            self.messaging.send_text_message(
                from_number,
                "Sorry, something went wrong. Please try again or type 'menu' to start over."
            )
            return {'status': 'error', 'message': str(e)}
    
    
    # ========================================
    # HELPER METHODS
    # ========================================
    
    def _looks_like_menu_response(self, message_lower: str) -> bool:
        """Check if message looks like response to 'select a category'"""
        if re.match(r'^\d+$', message_lower.strip()):
            return True
        
        category_keywords = ['burger', 'coffee', 'pizza', 'fries', 'drink', 'food', 'snack', 'dessert', 'beverage']
        return any(keyword in message_lower for keyword in category_keywords)
    
    
    def _looks_like_item_response(self, message_lower: str) -> bool:
        """Check if message looks like response to 'which item do you want'"""
        if re.match(r'^\d+$', message_lower.strip()):
            return True
        
        item_keywords = ['burger', 'pizza', 'coffee', 'tea', 'chai', 'fries', 'nuggets', 'cola', 'juice']
        return any(keyword in message_lower for keyword in item_keywords)
    
    
    def _looks_like_quantity_response(self, message_lower: str) -> bool:
        """Check if message looks like response to 'how many'"""
        if re.match(r'^\d+$', message_lower.strip()):
            return True
        
        urdu_numbers = ['ek', 'aik', 'do', 'teen', 'char', 'paanch', 'chah', 'saat', 'aath']
        return any(num in message_lower for num in urdu_numbers)
    
    
    def _is_order_intent(self, message_lower: str) -> bool:
        """Detect if message contains ordering intent"""
        
        if re.search(r'\d+\s*(burger|coffee|pizza|fries|tea|chai|nuggets)', message_lower):
            return True
        
        if re.search(r'(burger|coffee|pizza|fries|tea|chai|nuggets)\s*\d+', message_lower):
            return True
        
        urdu_numbers = r'(ek|aik|do|teen|char|paanch)'
        if re.search(urdu_numbers + r'\s*(burger|coffee|pizza)', message_lower):
            return True
        
        order_keywords = ['want', 'chahiye', 'dedo', 'lena', 'order', 'get me', 'dena']
        item_keywords = list(self.menu_keywords.keys())
        
        has_order_word = any(word in message_lower for word in order_keywords)
        has_item_word = any(item in message_lower for item in item_keywords)
        
        if has_order_word and has_item_word:
            return True
        
        return False
    
    
    def _parse_items_from_text(self, text: str) -> List[Dict]:
        """Parse items and quantities from natural language"""
        
        text_lower = text.lower()
        items = []
        
        urdu_numbers = {
            'ek': 1, 'aik': 1, 'ayk': 1,
            'do': 2, 'dou': 2,
            'teen': 3, 'tin': 3,
            'char': 4, 'chaar': 4,
            'paanch': 5, 'panch': 5,
        }
        
        try:
            menu_response = self.supabase.table('menu_items').select('*').eq('available', True).execute()
            menu_items = {item['name'].lower(): item for item in menu_response.data}
        except:
            menu_items = {
                'chicken burger': {'id': 1, 'name': 'Chicken Burger', 'price': 250},
                'burger': {'id': 1, 'name': 'Chicken Burger', 'price': 250},
                'coffee': {'id': 8, 'name': 'Coffee', 'price': 100},
                'pizza': {'id': 5, 'name': 'Margherita Pizza', 'price': 450},
                'fries': {'id': 12, 'name': 'Fries', 'price': 120},
                'tea': {'id': 10, 'name': 'Tea', 'price': 80},
            }
        
        parts = re.split(r'\s+(?:aur|and|or)\s+|,', text_lower)
        
        parsed_items = {}
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            qty = 1
            item_str = part
            
            match = re.match(r'^(\d+)\s+([a-z\s]+)$', part)
            if match:
                qty = int(match.group(1))
                item_str = match.group(2).strip()
            else:
                match = re.match(r'^([a-z\s]+)\s+(\d+)$', part)
                if match:
                    item_str = match.group(1).strip()
                    qty = int(match.group(2))
                else:
                    match = re.match(r'^(ek|aik|ayk|do|dou|teen|tin|char|chaar|paanch|panch)\s+([a-z\s]+)$', part)
                    if match:
                        qty = urdu_numbers.get(match.group(1), 1)
                        item_str = match.group(2).strip()
                    else:
                        item_str = part
                        qty = 1
            
            menu_item = self._find_menu_item(item_str, menu_items)
            
            if menu_item:
                item_id = menu_item['id']
                if item_id not in parsed_items:
                    parsed_items[item_id] = {
                        'menu_item_id': menu_item['id'],
                        'name': menu_item['name'],
                        'price': menu_item['price'],
                        'quantity': qty,
                        'subtotal': menu_item['price'] * qty
                    }
                else:
                    parsed_items[item_id]['quantity'] += qty
                    parsed_items[item_id]['subtotal'] = parsed_items[item_id]['price'] * parsed_items[item_id]['quantity']
        
        return list(parsed_items.values())
    
    
    def _find_menu_item(self, item_str: str, menu_items: Dict) -> Optional[Dict]:
        """Find menu item from user input"""
        
        if item_str in menu_items:
            return menu_items[item_str]
        
        for key, item in menu_items.items():
            if key in item_str or item_str in key:
                return item
        
        for key, item in menu_items.items():
            for keyword in ['burger', 'coffee', 'pizza', 'fries', 'tea']:
                if keyword in item_str and keyword in key:
                    return item
        
        return None
    
    
    def _add_items_to_cart(self, from_number: str, session: Dict, items: List[Dict], 
                          ai_message: str = None) -> Dict:
        """Add items to cart and send confirmation"""
        
        try:
            cart = session.get('cart', [])
            if isinstance(cart, str):
                cart = json.loads(cart)
            
            for new_item in items:
                item_exists = False
                for cart_item in cart:
                    if cart_item['menu_item_id'] == new_item['menu_item_id']:
                        cart_item['quantity'] += new_item['quantity']
                        cart_item['subtotal'] = cart_item['quantity'] * cart_item['price']
                        item_exists = True
                        break
                
                if not item_exists:
                    cart.append(new_item)
            
            self._update_session(session['id'], {'cart': cart})
            
            total = sum(item['subtotal'] for item in cart)
            
            message = ""
            
            if ai_message and self.use_groq:
                message = f"{ai_message}\n\n"
            else:
                message = "✅ Added to cart!\n\n"
            
            for item in items:
                message += f"• {item['quantity']}x {item['name']} - PKR {item['subtotal']}\n"
            
            message += f"\n━━━━━━━━━━━━━━━━━━\n"
            message += f"💰 Cart Total: PKR {total}\n\n"
            message += "What's next?\n"
            message += "• 'checkout' - Place order\n"
            message += "• 'cart' - View full cart\n"
            message += "• 'menu' - Add more items"
            
            self.messaging.send_text_message(from_number, message)
            
            return {'status': 'success', 'action': 'items_added_to_cart'}
        
        except Exception as e:
            print(f"❌ Error adding to cart: {e}")
            raise
    
    
    def _send_ordering_help(self, from_number: str) -> Dict:
        """Send help for natural language ordering"""
        
        message = "I didn't quite catch that! 🤔\n\n"
        message += "To order, try saying:\n"
        message += "• '2 burger and 1 coffee'\n"
        message += "• '2 burger aur 1 coffee'\n"
        message += "• 'I want 3 pizza'\n\n"
        message += "Or type 'menu' to browse!"
        
        self.messaging.send_text_message(from_number, message)
        
        return {'status': 'success', 'action': 'ordering_help_sent'}
    
    
    # ========================================
    # DATABASE METHODS
    # ========================================
    
    def _get_or_create_student(self, whatsapp_number: str) -> Dict:
        """Get existing student or create new one"""
        try:
            response = self.supabase.table('students').select('*').eq(
                'whatsapp_number', whatsapp_number
            ).execute()
            
            if response.data:
                return response.data[0]
            
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
            response = self.supabase.table('user_sessions').select('*').eq(
                'student_id', student_id
            ).execute()
            
            if response.data:
                return response.data[0]
            
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
    
    
    # ========================================
    # MENU METHODS
    # ========================================
    
    def _send_main_menu(self, to_number: str, student: Dict) -> Dict:
        """Send main menu with categories"""
        try:
            response = self.supabase.table('menu_items').select('category').execute()
            categories = sorted(list(set([item['category'] for item in response.data])))
            
            if not categories:
                print("[ERROR] No categories found in database!")
                self.messaging.send_text_message(
                    to_number,
                    "Sorry, the menu is temporarily unavailable. Please try again later."
                )
                return {'status': 'error', 'message': 'No categories found'}
            
            greeting = f"Welcome to University Café! 🍔☕\n\n"
            if student.get('name'):
                greeting = f"Hi {student['name']}! Welcome back! 🍔☕\n\n"
            
            message = greeting + "What would you like to order today?\n\nSelect a category:\n\n"
            
            for i, category in enumerate(categories, 1):
                message += f"{i}. {category}\n"
            
            message += "\nReply with number or category name\n"
            message += "💡 Or just say: '2 burger and 1 coffee'"
            
            self.messaging.send_text_message(to_number, message)
            
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
            response = self.supabase.table('menu_items').select('category').execute()
            categories = sorted(list(set([item['category'] for item in response.data])))
            
            if not categories:
                self.messaging.send_text_message(
                    to_number,
                    "Sorry, no menu categories available right now. Please try again later."
                )
                return {'status': 'error', 'message': 'No categories in database'}
            
            category = None
            try:
                index = int(selection.strip()) - 1
                if 0 <= index < len(categories):
                    category = categories[index]
            except ValueError:
                selection_lower = selection.lower().strip()
                for cat in categories:
                    if cat.lower() == selection_lower:
                        category = cat
                        break
                
                if not category:
                    for cat in categories:
                        if selection_lower in cat.lower():
                            category = cat
                            break
            
            if not category:
                self.messaging.send_text_message(
                    to_number,
                    "Invalid selection. Please type 'menu' to see categories again."
                )
                return {'status': 'error', 'message': 'Invalid category'}
            
            response = self.supabase.table('menu_items').select('*').eq(
                'category', category
            ).eq('available', True).execute()
            
            if not response.data:
                self.messaging.send_text_message(
                    to_number,
                    f"No items found in {category}. Please select another category or type 'menu'."
                )
                return {'status': 'error', 'message': 'No items found'}
            
            message = f"📋 {category}\n\n"
            
            for i, item in enumerate(response.data, 1):
                message += f"{i}. {item['name']} - PKR {item['price']}\n"
                if item.get('description'):
                    message += f"   {item['description']}\n"
                message += "\n"
            
            message += "💡 Reply with number or item name to add to cart\n"
            message += "Or type 'menu' to see all categories"
            
            self.messaging.send_text_message(to_number, message)
            
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
            
            selected_item = None
            
            try:
                index = int(selection.strip()) - 1
                if 0 <= index < len(items):
                    selected_item = items[index]
            except ValueError:
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
            
            message = f"Great choice! 🎉\n\n"
            message += f"📦 {selected_item['name']}\n"
            message += f"💰 PKR {selected_item['price']}\n\n"
            message += "How many would you like? (Reply with a number)"
            
            self.messaging.send_text_message(to_number, message)
            
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
            
            session_data = session.get('session_data', {})
            selected_item = session_data.get('selected_item')
            
            if not selected_item:
                return self._send_main_menu(to_number, self._get_or_create_student(to_number))
            
            cart = session.get('cart', [])
            if isinstance(cart, str):
                cart = json.loads(cart)
            
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
            
            self._update_session(session['id'], {
                'cart': cart,
                'current_state': self.STATE_IDLE,
                'session_data': {}
            })
            
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
    
    
    # ========================================
    # CART METHODS
    # ========================================
    
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
    
    
    # ========================================
    # CHECKOUT & PAYMENT METHODS
    # ========================================
    
    def _start_checkout(self, to_number: str, session: Dict) -> Dict:
        """Start checkout process with payment method selection"""
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
            
            total = sum(item['subtotal'] for item in cart)
            
            message = "📋 Order Summary:\n\n"
            for item in cart:
                message += f"{item['quantity']}x {item['name']} - PKR {item['subtotal']}\n"
            message += f"\n💰 Total: PKR {total}\n\n"
            message += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            if self.use_payment:
                message += "Select Payment Method:\n\n"
                message += "1️⃣ Cash on Pickup\n"
                message += "2️⃣ JazzCash\n"
                message += "3️⃣ EasyPaisa\n"
                message += "4️⃣ Credit/Debit Card\n\n"
                message += "Reply with number (1-4)"
                
                # Store cart total in session for payment
                session_data = session.get('session_data', {})
                session_data['checkout_total'] = total
                
                self._update_session(session['id'], {
                    'current_state': self.STATE_SELECTING_PAYMENT,
                    'session_data': session_data
                })
            else:
                # No payment service - direct to confirmation
                message += "Confirm your order?\n\n"
                message += "Type 'YES' to confirm or 'NO' to cancel"
                
                self._update_session(session['id'], {
                    'current_state': self.STATE_CONFIRMING_ORDER
                })
            
            self.messaging.send_text_message(to_number, message)
            
            return {'status': 'success', 'action': 'checkout_started'}
        
        except Exception as e:
            print(f"Error starting checkout: {str(e)}")
            raise
    
    
    def _handle_payment_selection(self, to_number: str, selection: str, session: Dict) -> Dict:
        """Handle payment method selection"""
        try:
            # Map selection to payment method
            payment_methods = {
                '1': 'cash',
                '2': 'jazzcash',
                '3': 'easypaisa',
                '4': 'card'
            }
            
            payment_method = payment_methods.get(selection.strip())
            
            if not payment_method:
                self.messaging.send_text_message(
                    to_number,
                    "Invalid selection. Please reply with 1, 2, 3, or 4."
                )
                return {'status': 'error', 'message': 'Invalid payment method'}
            
            # Get cart and total
            cart = session.get('cart', [])
            if isinstance(cart, str):
                cart = json.loads(cart)
            
            session_data = session.get('session_data', {})
            total = session_data.get('checkout_total', sum(item['subtotal'] for item in cart))
            
            # Store payment method in session
            session_data['payment_method'] = payment_method
            
            self._update_session(session['id'], {
                'session_data': session_data
            })
            
            # Show confirmation
            method_names = {
                'cash': 'Cash on Pickup',
                'jazzcash': 'JazzCash',
                'easypaisa': 'EasyPaisa',
                'card': 'Credit/Debit Card'
            }
            
            message = f"✅ Payment Method: {method_names[payment_method]}\n\n"
            message += f"💰 Total Amount: PKR {total}\n\n"
            message += "Confirm your order?\n\n"
            message += "Type 'YES' to confirm or 'NO' to cancel"
            
            self.messaging.send_text_message(to_number, message)
            
            self._update_session(session['id'], {
                'current_state': self.STATE_CONFIRMING_ORDER
            })
            
            return {'status': 'success', 'action': 'awaiting_order_confirmation'}
        
        except Exception as e:
            print(f"Error handling payment selection: {str(e)}")
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
        """Create order in database with payment"""
        try:
            cart = session.get('cart', [])
            if isinstance(cart, str):
                cart = json.loads(cart)
            
            student = self._get_or_create_student(to_number)
            total = sum(item['subtotal'] for item in cart)
            
            # Get payment method from session
            session_data = session.get('session_data', {})
            payment_method = session_data.get('payment_method', 'cash')
            
            # Create order
            order_data = {
                'student_id': student['id'],
                'total': total,
                'status': 'pending',
                'payment_method': payment_method,
                'payment_status': 'pending'
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
            
            # Create payment if payment service available
            payment_id = None
            print(f"[ORDER] Creating order #{order['id']}, use_payment={self.use_payment}")
            
            if self.use_payment:
                print(f"[PAYMENT] Attempting to create payment for order #{order['id']}, PKR {total}, method: {payment_method}")
                payment = payment_service.create_payment(
                    order_id=order['id'],
                    amount=total,
                    payment_method=payment_method
                )
                
                if payment:
                    payment_id = str(payment.get('id'))  # Convert ID to string for storage
                    print(f"[PAYMENT] Payment created: ID {payment_id}")
                    
                    # Update order with payment ID
                    self.supabase.table('orders').update({
                        'payment_id': payment_id
                    }).eq('id', order['id']).execute()
                else:
                    print(f"[PAYMENT] Payment creation returned None")
            else:
                print(f"[PAYMENT] Payment service not available (use_payment=False)")


            
            # Send order confirmation
            message = f"✅ Order Placed Successfully!\n\n"
            message += f"🔖 Order ID: #{order['id']}\n"
            message += f"💰 Total: PKR {total}\n\n"
            
            # Payment-specific message
            if payment_method == 'cash':
                message += f"💵 Payment Method: Cash on Pickup\n"
                message += f"Please pay PKR {total} at the counter when collecting your order.\n\n"
            elif self.use_payment and payment_id:
                # For online payment methods
                payment_msg = payment_service.format_payment_message(payment_id)
                message += payment_msg + "\n\n"
                
                # Auto-simulate payment after 30 seconds (for demo)
                def auto_complete_payment():
                    time.sleep(30)
                    success = payment_service.simulate_payment_success(payment_id)
                    if success:
                        # Update order payment status
                        self.supabase.table('orders').update({
                            'payment_status': 'completed'
                        }).eq('id', order['id']).execute()
                        
                        # Send confirmation
                        self.messaging.send_text_message(
                            to_number,
                            f"✅ Payment Received!\n\nOrder #{order['id']} is confirmed and being prepared! 👨‍🍳"
                        )
                
                threading.Thread(target=auto_complete_payment, daemon=True).start()
            
            message += f"We'll notify you when your order is ready! 👨‍🍳\n\n"
            message += f"💡 Track: type 'track {order['id']}'\n"
            message += f"Thank you! 🙏"
            
            self.messaging.send_text_message(to_number, message)
            
            # Clear cart and session
            self._update_session(session['id'], {
                'cart': [],
                'current_state': self.STATE_IDLE,
                'session_data': {}
            })
            
            # Clear conversation memory
            if self.use_groq:
                groq_service.clear_memory(to_number)
            
            # Notify staff
            notification_service.notify_staff_new_order(order['id'])
            
            return {
                'status': 'success',
                'action': 'order_created',
                'order_id': order['id'],
                'payment_id': payment_id
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
    
    
    # ========================================
    # ORDER TRACKING METHODS
    # ========================================
    
    def _handle_track_command(self, to_number: str, message: str, student: Dict) -> Dict:
        """Handle order tracking command"""
        try:
            parts = message.split()
            order_id = None
            
            if len(parts) > 1:
                try:
                    order_id = int(parts[1])
                except ValueError:
                    pass
            
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
        
        # Clear conversation memory
        if self.use_groq:
            groq_service.clear_memory(to_number)
        
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
        message += "💡 Or just say naturally:\n"
        message += "'2 burger and 1 coffee'\n"
        message += "'2 burger aur 1 coffee'\n\n"
        message += "I'll understand! 😊"
        
        self.messaging.send_text_message(to_number, message)
        
        return {'status': 'success', 'action': 'help_sent'}


# Create singleton instance
chatbot_service = ChatbotService()