"""
Groq Service - COMPLETE VERSION WITH ENHANCEMENTS
Location: app/services/groq_service.py

Free AI API for Natural Language Understanding
Uses LLaMA 3.3 model for restaurant chatbot with:
- Dynamic menu loading from database
- Conversation memory
- Rate limiting protection
- Health monitoring

REPLACE YOUR CURRENT groq_service.py WITH THIS FILE
"""

import os
import time
import json
from groq import Groq
from typing import Dict, Optional, List
from collections import deque
from dotenv import load_dotenv

load_dotenv()


class GroqService:
    """
    Enhanced Groq service with all production features
    """
    
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        
        if not api_key:
            print("[WARN] GROQ_API_KEY not found in environment variables")
            print("   Get your free key from: https://console.groq.com")
            self.client = None
            self.available = False
        else:
            try:
                self.client = Groq(api_key=api_key)
                self.available = True
                print("[OK] Groq Service initialized successfully")
            except Exception as e:
                print(f"[ERROR] Error initializing Groq: {e}")
                self.client = None
                self.available = False
        
        # Business configuration (customize for your café!)
        self.business_config = {
            'name': 'University Café',
            'location': 'Campus',
            'hours': '9:00 AM - 6:00 PM',
            'phone': 'WhatsApp only',
            'currency': 'PKR',
            'special_instructions': 'We accept orders via WhatsApp. Fast delivery available on campus!',
        }
        
        # Dynamic menu cache
        self.menu_cache = None
        self.menu_last_updated = 0
        self.menu_cache_ttl = 300  # Refresh every 5 minutes
        
        # Conversation memory for context-aware responses
        self.conversation_memory = {}  # {phone_number: [messages]}
        self.max_memory = 5  # Keep last 5 exchanges
        
        # Rate limiting (Groq free tier: 30 requests/minute)
        self.request_times = deque(maxlen=30)
        self.rate_limit_window = 60  # seconds
        
        # System prompt (will be built dynamically)
        self.system_prompt = self._build_system_prompt()
    
    
    def _get_menu_from_db(self) -> Optional[List[Dict]]:
        """
        Fetch menu items from database
        Implements caching to reduce database calls
        """
        try:
            # Check cache
            current_time = time.time()
            if self.menu_cache and (current_time - self.menu_last_updated < self.menu_cache_ttl):
                return self.menu_cache
            
            # Fetch from database
            from app.utils.supabase_client import supabase_client
            
            response = supabase_client.table('menu_items').select('*').eq('available', True).execute()
            
            if response.data:
                self.menu_cache = response.data
                self.menu_last_updated = current_time
                print(f"[OK] Loaded {len(response.data)} menu items from database")
                return response.data
        
        except Exception as e:
            print(f"[WARN] Could not load menu from database: {e}")
            # Return cached data if available
            if self.menu_cache:
                print("[OK] Using cached menu data")
                return self.menu_cache
        
        return None
    
    
    def _format_menu_for_prompt(self, menu_items: List[Dict]) -> str:
        """Format menu items for the system prompt"""
        if not menu_items:
            return "Menu items not available"
        
        # Group by category
        categories = {}
        for item in menu_items:
            cat = item.get('category', 'Other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)
        
        # Format nicely
        menu_text = ""
        for category, items in sorted(categories.items()):
            menu_text += f"\n{category.upper()}:\n"
            for item in items:
                name = item.get('name', 'Unknown')
                price = item.get('price', '?')
                desc = item.get('description', '')
                if desc:
                    menu_text += f"  • {name} (PKR {price}) - {desc}\n"
                else:
                    menu_text += f"  • {name} (PKR {price})\n"
        
        return menu_text
    
    
    def _build_system_prompt(self) -> str:
        """Build customizable system prompt with business data and menu"""
        
        # Try to get menu from database
        menu_items = self._get_menu_from_db()
        if menu_items:
            menu_text = self._format_menu_for_prompt(menu_items)
        else:
            # Fallback menu
            menu_text = """
BURGERS:
  • Chicken Burger (PKR 250)
  • Beef Burger (PKR 280)
  • Zinger Burger (PKR 300)

PIZZAS:
  • Margherita Pizza (PKR 450)
  • Pepperoni Pizza (PKR 550)

BEVERAGES:
  • Coffee (PKR 100)
  • Cold Coffee (PKR 120)
  • Tea (PKR 80)

SIDES:
  • Fries (PKR 120)
  • Chicken Nuggets (PKR 180)
"""
        
        prompt = f"""You are a friendly and helpful chatbot for {self.business_config['name']}.

ABOUT US:
- Name: {self.business_config['name']}
- Location: {self.business_config['location']}
- Hours: {self.business_config['hours']}
- Contact: {self.business_config['phone']}
- Special Info: {self.business_config['special_instructions']}

MENU:{menu_text}

YOUR RESPONSIBILITIES:
1. Understand customer orders in English and Roman Urdu
2. Be friendly, warm, and helpful in your responses
3. Keep responses concise (1-3 sentences max)
4. Answer menu and price questions accurately
5. Guide users through ordering process naturally
6. When users want to order, acknowledge and help them

COMMUNICATION STYLE:
- Use emojis naturally (🍔 ☕ 🍕 etc.) but don't overdo it
- Be conversational and natural, not robotic
- Adapt to user's language (English or Roman Urdu)
- Show enthusiasm about food!
- Be helpful without being pushy

LANGUAGES YOU SUPPORT:
- English: "I want 2 burgers and 1 coffee"
- Roman Urdu: "2 burger aur 1 coffee chahiye", "mujhe ek pizza do"
- Mixed: "2 burger and coffee bhi"

IMPORTANT RULES:
- Always mention prices in PKR
- Be honest if we don't have something
- Suggest similar items if requested item not available
- Keep conversations natural and flowing
- Don't push sales too hard, just be helpful
- If someone asks about an item not on menu, politely say we don't have it

EXAMPLES OF GOOD RESPONSES:
User: "Hi"
You: "Hey! Welcome to University Café! 🍔 What can I get you today?"

User: "Menu kya hai?"
You: "We've got burgers, pizzas, coffee, and more! Want to see a specific category or just tell me what you're craving? 😊"

User: "2 burger aur 1 coffee"
You: "Great choice! 🍔☕ That's 2 Chicken Burgers and 1 Coffee. Let me add those to your cart!"

User: "Burger kitna hai?"
You: "Chicken Burger is PKR 250. Want to order some?"

Remember: You're talking to a student at a university café. Be friendly, quick, and make them feel welcome!"""
        
        return prompt
    
    
    def refresh_menu(self):
        """Force refresh menu from database"""
        self.menu_cache = None
        self.menu_last_updated = 0
        self.system_prompt = self._build_system_prompt()
        print("[OK] Menu refreshed from database")
    
    
    def update_business_config(self, config: Dict) -> None:
        """Update business information dynamically"""
        self.business_config.update(config)
        self.system_prompt = self._build_system_prompt()
        print(f"[OK] Business config updated")
    
    
    def is_available(self) -> bool:
        """Check if Groq service is available"""
        return self.available and self.client is not None
    
    
    def _check_rate_limit(self) -> bool:
        """
        Check if we're within rate limits
        Groq free tier: 30 requests per minute
        """
        now = time.time()
        
        # Remove requests older than 1 minute
        while self.request_times and now - self.request_times[0] > self.rate_limit_window:
            self.request_times.popleft()
        
        # If we have 30 requests in last minute, we're at limit
        if len(self.request_times) >= 30:
            print("[WARN] Groq rate limit reached (30/min), using fallback")
            return False
        
        # Record this request
        self.request_times.append(now)
        return True
    
    
    def chat(self, user_message: str, conversation_history: list = None) -> Optional[str]:
        """
        Send message to Groq and get response
        Basic chat without memory
        
        Args:
            user_message: User's message
            conversation_history: Optional list of previous messages
            
        Returns:
            AI response or None if failed
        """
        
        if not self.is_available():
            print("[WARN] Groq service not available")
            return None
        
        # Check rate limit
        if not self._check_rate_limit():
            return None
        
        try:
            # Build messages
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                temperature=0.7,  # Balanced: creative but consistent
                max_tokens=200,  # Keep responses concise
                top_p=1,
                stream=False
            )
            
            # Extract response
            response = chat_completion.choices[0].message.content
            
            return response.strip()
        
        except Exception as e:
            print(f"[ERROR] Groq API error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    
    def chat_with_memory(self, user_message: str, phone_number: str) -> Optional[str]:
        """
        Chat with conversation memory for more natural flow
        
        This allows the chatbot to remember context:
        User: "What's the price of burger?"
        Bot: "Chicken Burger is PKR 250"
        User: "I'll take 2" ← Bot remembers we're talking about burgers!
        Bot: "Great! Adding 2 Chicken Burgers..."
        
        Args:
            user_message: User's message
            phone_number: User's phone number (for memory key)
            
        Returns:
            AI response or None if failed
        """
        
        if not self.is_available():
            return None
        
        # Check rate limit
        if not self._check_rate_limit():
            return None
        
        try:
            # Get conversation history for this user
            history = self.conversation_memory.get(phone_number, [])
            
            # Build messages with history
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(history)  # Add previous conversation
            messages.append({"role": "user", "content": user_message})
            
            # Call Groq
            response = self.client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=200,
            ).choices[0].message.content.strip()
            
            # Update memory
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": response})
            
            # Keep only last N exchanges (prevent context from getting too long)
            if len(history) > self.max_memory * 2:
                history = history[-self.max_memory * 2:]
            
            self.conversation_memory[phone_number] = history
            
            return response
        
        except Exception as e:
            print(f"[ERROR] Groq error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    
    def clear_memory(self, phone_number: str):
        """Clear conversation memory for a user"""
        if phone_number in self.conversation_memory:
            del self.conversation_memory[phone_number]
            print(f"[OK] Cleared conversation memory for {phone_number}")
    
    
    def clear_all_memory(self):
        """Clear all conversation memory"""
        self.conversation_memory.clear()
        print("[OK] Cleared all conversation memory")
    
    
    def understand_order(self, user_message: str) -> Dict:
        """
        Use Groq to understand ordering intent
        Returns structured understanding
        
        Args:
            user_message: User's message
            
        Returns:
            Dict with 'intent', 'items', 'response'
        """
        
        if not self.is_available():
            return {
                'intent': 'unknown',
                'items': [],
                'response': None
            }
        
        # Check rate limit
        if not self._check_rate_limit():
            return {
                'intent': 'unknown',
                'items': [],
                'response': None
            }
        
        try:
            prompt = f"""You are helping a café understand what a customer wants.

Customer said: "{user_message}"

Respond with:
1. A natural, friendly response (1-2 sentences)
2. List any items they mentioned (or "none")
3. Their likely intent

Format:
RESPONSE: [your friendly reply]
ITEMS: [items mentioned, or "none"]
INTENT: [order/menu/price/general]

Example:
Customer: "2 burger aur coffee"
RESPONSE: Great choice! Adding 2 burgers and coffee to your cart.
ITEMS: burger, coffee
INTENT: order
"""
            
            response = self.client.chat.completions.create(
                messages=[{"role": "system", "content": self.system_prompt},
                         {"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_tokens=150
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse response
            lines = result.split('\n')
            intent = 'general'
            items = []
            ai_response = None
            
            for line in lines:
                if line.startswith('INTENT:'):
                    intent = line.split(':', 1)[1].strip().lower()
                elif line.startswith('ITEMS:'):
                    items_text = line.split(':', 1)[1].strip()
                    if items_text.lower() != 'none':
                        items = [i.strip() for i in items_text.split(',')]
                elif line.startswith('RESPONSE:'):
                    ai_response = line.split(':', 1)[1].strip()
            
            return {
                'intent': intent,
                'items': items,
                'response': ai_response
            }
        
        except Exception as e:
            print(f"[ERROR] Error understanding order: {e}")
            return {
                'intent': 'unknown',
                'items': [],
                'response': None
            }
    
    
    def get_menu_response(self, user_message: str) -> Optional[str]:
        """Get response for menu-related queries"""
        return self.chat(user_message)
    
    
    def get_price_response(self, item_name: str) -> Optional[str]:
        """Get response for price queries"""
        prompt = f"What's the price of {item_name}? Give a brief response."
        return self.chat(prompt)
    
    
    def health_check(self) -> Dict:
        """
        Check Groq service health
        Returns status dict
        """
        
        if not self.is_available():
            return {
                'status': 'unavailable',
                'message': 'Groq API key not configured',
                'available': False
            }
        
        try:
            # Try a simple call
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": "ping"}],
                model="llama-3.3-70b-versatile",
                max_tokens=5,
                timeout=5
            )
            
            return {
                'status': 'healthy',
                'message': 'Groq API responding normally',
                'model': 'llama-3.3-70b-versatile',
                'available': True,
                'rate_limit_remaining': 30 - len(self.request_times)
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'available': False
            }
    
    
    def get_stats(self) -> Dict:
        """Get service statistics"""
        return {
            'available': self.is_available(),
            'requests_last_minute': len(self.request_times),
            'rate_limit_remaining': 30 - len(self.request_times),
            'conversations_in_memory': len(self.conversation_memory),
            'menu_cached': self.menu_cache is not None,
            'menu_items_count': len(self.menu_cache) if self.menu_cache else 0
        }


# Create singleton instance
groq_service = GroqService()


# Test function
if __name__ == "__main__":
    print("\n" + "="*60)
    print("GROQ SERVICE TEST")
    print("="*60)
    
    if groq_service.is_available():
        print("\n✅ Service available! Testing...\n")
        
        # Test health
        health = groq_service.health_check()
        print(f"Health: {health['status']}")
        print(f"Message: {health['message']}\n")
        
        # Test stats
        stats = groq_service.get_stats()
        print(f"Stats: {stats}\n")
        
        # Test messages
        test_messages = [
            "Hi",
            "Menu kya hai?",
            "2 burger aur 1 coffee",
            "Burger kitna hai?",
        ]
        
        for msg in test_messages:
            print(f"User: {msg}")
            response = groq_service.chat(msg)
            print(f"Bot:  {response}\n")
    else:
        print("\n❌ Service not available")
        print("   Set GROQ_API_KEY in .env file")
        print("   Get free key from: https://console.groq.com")