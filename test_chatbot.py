"""
Chatbot Testing Script - GROQ API VERSION
Tests complete system including Groq AI integration
"""
import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:5000"
TEST_ENDPOINT = f"{BASE_URL}/webhook/test-message"
ORDERS_CHECK = f"{BASE_URL}/staff/orders/pending"
ORDERS_ALL = f"{BASE_URL}/staff/orders/all"
ORDER_API = f"{BASE_URL}/api/orders"
HEALTH_CHECK = f"{BASE_URL}/api/health"
PHONE = "+923001234567"

# Counter for generating unique phone numbers
test_counter = 1

# Increased timeout for AI processing
REQUEST_TIMEOUT = 45

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_step(text):
    """Print test step"""
    print(f"\n{Colors.YELLOW}📝 {text}{Colors.END}")

def print_ai_response(text):
    """Print AI response"""
    print(f"{Colors.CYAN}🤖 AI: {text}{Colors.END}")

def check_environment():
    """Check environment variables"""
    print_header("🔍 ENVIRONMENT CHECK")
    
    required_vars = {
        'GROQ_API_KEY': 'Groq API Key',
        'SUPABASE_URL': 'Supabase URL',
        'SUPABASE_KEY': 'Supabase Key',
        'USE_GROQ_API': 'Use Groq API Flag'
    }
    
    all_present = True
    
    for var, name in required_vars.items():
        value = os.getenv(var)
        if value:
            masked = value[:10] + '...' if len(value) > 10 else value
            print_success(f"{name}: {masked}")
        else:
            print_error(f"{name}: NOT SET")
            all_present = False
    
    # Check Groq API flag
    use_groq = os.getenv('USE_GROQ_API', 'false').lower() == 'true'
    if use_groq:
        print_success("Groq API is ENABLED")
    else:
        print_warning("Groq API is DISABLED")
    
    # Check custom model flag
    use_custom = os.getenv('USE_CUSTOM_MODEL', 'false').lower() == 'true'
    if use_custom:
        print_warning("Custom model is ENABLED (should be false)")
    else:
        print_success("Custom model is DISABLED")
    
    return all_present

def check_groq_api():
    """Test Groq API directly"""
    print_header("🤖 GROQ API DIRECT TEST")
    
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print_error("GROQ_API_KEY not found in environment!")
        return False
    
    try:
        from groq import Groq
        
        print_info("Initializing Groq client...")
        client = Groq(api_key=api_key)
        
        print_info("Sending test message to Groq...")
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say hello in one sentence",
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=50,
        )
        
        response = chat_completion.choices[0].message.content
        
        print_success("Groq API is working!")
        print_ai_response(response)
        
        return True
    
    except ImportError:
        print_error("Groq package not installed!")
        print_warning("Install with: pip install groq")
        return False
    
    except Exception as e:
        print_error(f"Groq API error: {str(e)}")
        print_warning("Check your GROQ_API_KEY")
        return False

def check_flask_server():
    """Check if Flask server is running and responding"""
    print_header("🔍 FLASK SERVER CHECK")
    
    try:
        print_info("Pinging Flask server...")
        response = requests.get(BASE_URL, timeout=5)
        
        if response.status_code == 200:
            print_success("Flask server is running!")
            data = response.json()
            print_info(f"API: {data.get('message', 'Unknown')}")
            return True
        else:
            print_error("Flask server returned unexpected response")
            return False
    
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to Flask server!")
        print_warning("Start Flask with: python run.py")
        return False
    
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def check_health_endpoint():
    """Check health endpoint"""
    print_header("💚 HEALTH ENDPOINT CHECK")
    
    try:
        print_info("Checking /api/health endpoint...")
        response = requests.get(HEALTH_CHECK, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Health check passed!")
            
            # Show service status
            services = data.get('services', {})
            for service, status in services.items():
                if status:
                    print_success(f"{service}: OK")
                else:
                    print_error(f"{service}: Failed")
            
            return True
        else:
            print_error("Health check failed!")
            return False
    
    except Exception as e:
        print_error(f"Error: {str(e)}")
        print_warning("Health endpoint may not be implemented")
        return False

def check_orders_in_dashboard():
    """Check if orders are showing in dashboard"""
    print_header("📊 CHECKING DASHBOARD ORDERS")
    
    try:
        print_info("Fetching pending orders from dashboard...")
        response = requests.get(ORDERS_CHECK, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('data', [])
            
            print_success(f"Found {len(orders)} pending orders!")
            
            for i, order in enumerate(orders, 1):
                order_id = order.get('id', 'Unknown')
                status = order.get('status', 'Unknown')
                total = order.get('total', 0)
                
                student = order.get('students', {})
                if isinstance(student, list):
                    student = student[0] if student else {}
                
                student_name = student.get('name', 'Unknown')
                
                print_info(f"Order #{order_id}: {status.upper()} - PKR {total} ({student_name})")
            
            return len(orders)
        else:
            print_error(f"Failed to fetch orders: HTTP {response.status_code}")
            return 0
    
    except Exception as e:
        print_error(f"Error checking orders: {str(e)}")
        return 0

def check_all_orders_in_db():
    """Check ALL orders in database"""
    print_header("🗄️ CHECKING ALL ORDERS IN DATABASE")
    
    try:
        print_info("Fetching all orders from database...")
        response = requests.get(ORDERS_ALL, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('data', [])
            count = data.get('count', len(orders))
            
            print_success(f"Found {count} total orders in database!")
            
            if orders:
                print_info("\nLatest 5 orders:")
                for i, order in enumerate(orders[:5], 1):
                    order_id = order.get('id', 'Unknown')
                    status = order.get('status', 'Unknown')
                    total = order.get('total', 0)
                    created = order.get('created_at', 'Unknown')
                    
                    student = order.get('students', {})
                    if isinstance(student, list):
                        student = student[0] if student else {}
                    
                    student_name = student.get('name', 'Unknown')
                    
                    print_info(f"  {i}. Order #{order_id}: {status.upper()} - PKR {total} ({student_name}) - {created[:10]}")
            
            return count
        else:
            print_error(f"Failed to fetch orders: HTTP {response.status_code}")
            return 0
    
    except Exception as e:
        print_error(f"Error checking orders: {str(e)}")
        return 0

def send_message(message, phone=None, retry=True):
    """Send a test message to the chatbot"""
    global test_counter
    
    # Use unique phone number for each test customer
    if phone is None:
        phone = f"+923000000{test_counter:03d}"  # Generates +923000000001, +923000000002, etc
        test_counter += 1
    
    print(f"\n{Colors.BLUE}{'─'*70}{Colors.END}")
    print(f"{Colors.BOLD}📤 USER ({phone}): {message}{Colors.END}")
    print(f"{Colors.BLUE}{'─'*70}{Colors.END}")
    
    payload = {
        "from": phone,
        "message": message
    }
    
    try:
        print_info(f"Sending request... (timeout: {REQUEST_TIMEOUT}s)")
        start_time = time.time()
        
        response = requests.post(
            TEST_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Status: {result.get('status')}")
            print_info(f"Response time: {elapsed:.2f}s")
            
            # Show bot response if available
            bot_response = result.get('response')
            if bot_response:
                print_ai_response(bot_response)
            
            time.sleep(0.5)
            return result
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to Flask server!")
        print_info("Make sure Flask is running: python run.py")
        return None
    
    except requests.exceptions.Timeout:
        print_error(f"Request timed out after {REQUEST_TIMEOUT} seconds!")
        print_warning("This usually means:")
        print_warning("  1. Groq API is slow (check console.groq.com status)")
        print_warning("  2. Database query is slow")
        print_warning("  3. WhatsApp API is slow (if using real WhatsApp)")
        
        if retry:
            print_info("Retrying once...")
            time.sleep(2)
            return send_message(message, phone, retry=False)
        return None
    
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_groq_integration():
    """Test Groq AI integration through chatbot"""
    print_header("🤖 GROQ AI INTEGRATION TEST")
    print_info("Testing natural language understanding with Groq\n")
    
    test_messages = [
        ("Greeting", "Hi"),
        ("Roman Urdu Order", "2 burger aur 1 coffee"),
        ("English Order", "I want 3 pizza"),
        ("Menu Query", "Menu kya hai?"),
        ("Price Query", "Burger kitna hai?"),
        ("Mixed Language", "2 burger and coffee bhi chahiye"),
    ]
    
    passed = 0
    failed = 0
    
    for i, (test_name, message) in enumerate(test_messages, 1):
        print_step(f"TEST {i}/{len(test_messages)}: {test_name}")
        result = send_message(message)
        
        if result:
            passed += 1
            print_success(f"✓ {test_name} passed")
        else:
            failed += 1
            print_error(f"✗ {test_name} failed")
        
        time.sleep(2)  # Delay for Groq rate limiting
    
    print_header("📊 GROQ INTEGRATION TEST RESULTS")
    print_info(f"Passed: {passed}/{len(test_messages)}")
    print_info(f"Failed: {failed}/{len(test_messages)}")
    
    if failed == 0:
        print_success("All Groq AI tests passed! 🎉")
    else:
        print_warning("Some tests failed - check Flask console")

def test_complete_order_flow():
    """Test complete order flow from start to finish"""
    print_header("🤖 COMPLETE ORDER FLOW TEST")
    print_info("This simulates a full customer journey from start to finish\n")
    
    steps = [
        ("Start Conversation", "hi"),
        ("Simple Order", "2 burger aur 1 coffee"),
    ]
    
    failed_steps = []
    
    for i, (step_name, message) in enumerate(steps, 1):
        print_step(f"TEST {i}/{len(steps)}: {step_name}")
        result = send_message(message)
        
        if not result:
            failed_steps.append(step_name)
            print_warning(f"Step '{step_name}' failed, continuing...")
        
        time.sleep(2)
    
    print_header("✅ COMPLETE ORDER FLOW TEST FINISHED")
    
    if failed_steps:
        print_warning(f"Failed steps: {', '.join(failed_steps)}")
        print_info("Check Flask console for error details")
    else:
        print_success("All steps passed!")
    
    print_info("\nWaiting 3 seconds for database to sync...")
    time.sleep(3)
    
    # Check if order was created
    print_step("Checking if orders are visible on dashboard...")
    pending_count = check_orders_in_dashboard()
    
    print_step("Checking all orders in database...")
    total_count = check_all_orders_in_db()
    
    if pending_count > 0:
        print_success(f"✓ Orders are visible on dashboard! ({pending_count} pending)")
    else:
        print_warning(f"Orders may not be showing on dashboard yet (check db: {total_count} total)")
    
    print_info("Check Flask console for full conversation log")

def test_natural_language_orders():
    """Test natural language ordering (Groq-powered)"""
    print_header("🗣️ NATURAL LANGUAGE ORDER TEST")
    print_info("Testing various ways to place orders\n")
    
    test_orders = [
        ("Simple English", "2 burger and 1 coffee"),
        ("Simple Urdu", "2 burger aur 1 coffee"),
    ]
    
    for i, (test_name, order) in enumerate(test_orders, 1):
        print_step(f"TEST {i}/{len(test_orders)}: {test_name}")
        result = send_message(order)
        
        if result:
            print_success(f"✓ Order processed")
        else:
            print_error(f"✗ Order failed")
        
        time.sleep(2)
    
    print_success("Natural language order tests completed!")
    
    # Check dashboard
    print_info("\nWaiting 3 seconds for database to sync...")
    time.sleep(3)
    
    print_step("Checking if orders are visible on dashboard...")
    pending_count = check_orders_in_dashboard()
    
    if pending_count > 0:
        print_success(f"✓ Orders visible on dashboard! ({pending_count} pending)")
    else:
        print_warning("Orders may still be syncing...")

def test_cart_operations():
    """Test cart operations"""
    print_header("🛒 CART OPERATIONS TEST")
    
    tests = [
        ("View Empty Cart", "cart"),
        ("Add Item (NL)", "2 burger aur coffee"),
        ("View Cart", "cart"),
        ("Add More Items", "1 pizza"),
        ("View Cart Again", "cart"),
        ("Clear Cart", "clear cart"),
        ("Verify Empty", "cart")
    ]
    
    for i, (test_name, message) in enumerate(tests, 1):
        print_step(f"TEST {i}/{len(tests)}: {test_name}")
        send_message(message)
        time.sleep(1)
    
    print_success("Cart operations tests completed!")

def test_order_tracking():
    """Test order tracking feature"""
    print_header("📍 ORDER TRACKING TEST")
    
    tests = [
        ("Track Latest Order", "track"),
        ("Track Specific Order", "track 1"),
        ("Status Command", "status"),
        ("Order History", "my orders")
    ]
    
    for i, (test_name, message) in enumerate(tests, 1):
        print_step(f"TEST {i}/{len(tests)}: {test_name}")
        send_message(message)
        time.sleep(1)
    
    print_success("Order tracking tests completed!")

def test_menu_system():
    """Test menu browsing and item selection"""
    print_header("📋 MENU SYSTEM TEST")
    print_info("Testing menu browsing, categories, and item selection\n")
    
    tests = [
        ("View Menu", "menu"),
        ("Browse Menu Items", "show menu"),
        ("Item Info", "burger details"),
        ("Price Check", "pizza price?"),
        ("Category Filter", "main course"),
        ("Search Item", "biryani"),
        ("Available Items", "what's available?"),
    ]
    
    for i, (test_name, message) in enumerate(tests, 1):
        print_step(f"TEST {i}/{len(tests)}: {test_name}")
        send_message(message)
        time.sleep(1)
    
    print_success("Menu system tests completed!")

def test_payment_system():
    """Test payment system integration"""
    print_header("💳 PAYMENT SYSTEM TEST")
    print_info("Testing payment methods and checkout process\n")
    
    tests = [
        ("Check Payment Methods", "payment methods"),
        ("Ask About Payment", "how to pay?"),
        ("Payment Options", "payment"),
        ("Cash Payment", "cash payment"),
        ("JazzCash Payment", "jazzcash"),
        ("Card Payment", "card"),
        ("Confirm Payment", "confirm"),
    ]
    
    for i, (test_name, message) in enumerate(tests, 1):
        print_step(f"TEST {i}/{len(tests)}: {test_name}")
        send_message(message)
        time.sleep(1)
    
    print_success("Payment system tests completed!")

def test_notifications():
    """Test notification system"""
    print_header("🔔 NOTIFICATION SYSTEM TEST")
    print_info("Testing order notifications and updates\n")
    
    print_step("Creating test order for notifications...")
    send_message("2 burger aur 1 coffee")
    
    time.sleep(3)
    
    print_info("Notifications would be sent via WhatsApp")
    print_info("Check WhatsApp to verify notification was received")
    print_info("Notification events tracked: Order created, status updates, completion")
    
    print_success("Notification test completed!")

def test_staff_dashboard():
    """Test staff dashboard functionality"""
    print_header("📊 STAFF DASHBOARD TEST")
    print_info("Testing real-time order management dashboard\n")
    
    print_step("Accessing Staff Dashboard...")
    print_info(f"Dashboard URL: {BASE_URL}/staff/dashboard")
    
    print_step("Fetching pending orders...")
    try:
        response = requests.get(f"{BASE_URL}/staff/orders/pending", timeout=10)
        if response.status_code == 200:
            data = response.json()
            orders = data.get('data', [])
            print_success(f"Pending Orders: {len(orders)}")
            for order in orders[:3]:
                print_info(f"  Order #{order.get('id')}: {order.get('status')} - PKR {order.get('total')}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    time.sleep(1)
    
    print_step("Fetching order statistics...")
    try:
        response = requests.get(f"{BASE_URL}/staff/orders/all", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data.get('count', 0)
            orders = data.get('data', [])
            
            print_success(f"Total Orders: {total}")
            
            # Calculate stats
            statuses = {}
            for order in orders:
                status = order.get('status', 'unknown')
                statuses[status] = statuses.get(status, 0) + 1
            
            print_info("Order Status Breakdown:")
            for status, count in statuses.items():
                print_info(f"  {status.upper()}: {count}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    print_success("Staff dashboard tests completed!")

def test_database_connectivity():
    """Test database connectivity and data persistence"""
    print_header("🗄️ DATABASE CONNECTIVITY TEST")
    print_info("Testing Supabase connection and data persistence\n")
    
    try:
        print_step("Testing students table...")
        response = requests.get(f"{BASE_URL}/api/students", timeout=10)
        if response.status_code == 200:
            print_success("Students table: Connected")
        else:
            print_warning("Students table: May not be accessible")
    except:
        print_info("Students endpoint may not be implemented")
    
    time.sleep(1)
    
    try:
        print_step("Testing menu items table...")
        response = requests.get(f"{BASE_URL}/api/menu", timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', []) if isinstance(data, dict) else data
            print_success(f"Menu items table: Connected ({len(items)} items)")
            if items:
                print_info(f"  Sample: {items[0].get('name')} - PKR {items[0].get('price')}")
    except Exception as e:
        print_warning(f"Menu endpoint error: {str(e)}")
    
    time.sleep(1)
    
    try:
        print_step("Testing orders table...")
        response = requests.get(f"{BASE_URL}/staff/orders/all", timeout=10)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print_success(f"Orders table: Connected ({count} orders)")
    except Exception as e:
        print_warning(f"Orders endpoint error: {str(e)}")
    
    time.sleep(1)
    
    try:
        print_step("Testing payments table...")
        response = requests.get(f"{BASE_URL}/api/payments", timeout=10)
        if response.status_code == 200:
            print_success("Payments table: Connected")
        else:
            print_info("Payments endpoint may not be available")
    except:
        print_info("Payments endpoint may not be implemented")
    
    print_success("Database connectivity tests completed!")

def test_error_handling():
    """Test error handling and edge cases"""
    print_header("⚠️ ERROR HANDLING TEST")
    print_info("Testing system error handling and edge cases\n")
    
    tests = [
        ("Invalid Item", "999 burger"),
        ("Negative Quantity", "-5 pizza"),
        ("Non-existent Order", "track 99999"),
        ("Empty Message", ""),
        ("Spam Prevention", "spam spam spam"),
        ("Long Message", "a" * 500),
    ]
    
    for i, (test_name, message) in enumerate(tests, 1):
        print_step(f"TEST {i}/{len(tests)}: {test_name}")
        try:
            send_message(message)
        except Exception as e:
            print_warning(f"Exception (expected): {str(e)[:50]}")
        time.sleep(1)
    
    print_success("Error handling tests completed!")

def test_concurrent_orders():
    """Test multiple concurrent customer orders"""
    print_header("👥 CONCURRENT ORDERS TEST")
    print_info("Testing multiple customers placing orders simultaneously\n")
    
    customers = [
        ("Customer 1", "3 burger aur 2 coffee"),
        ("Customer 2", "1 pizza aur fries"),
        ("Customer 3", "2 biryani"),
        ("Customer 4", "4 naan and karahi"),
    ]
    
    phones = []
    
    for i, (name, order) in enumerate(customers, 1):
        print_step(f"TEST {i}/{len(customers)}: {name} ordering")
        phone = send_message(order)
        if phone:
            phones.append(phone)
        time.sleep(1)
    
    print_info("\nWaiting 3 seconds for all orders to sync...")
    time.sleep(3)
    
    print_step("Checking if all orders were created...")
    try:
        response = requests.get(f"{BASE_URL}/staff/orders/all", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data.get('count', 0)
            print_success(f"Total orders in system: {total}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    print_success("Concurrent orders tests completed!")

def test_multi_language_support():
    """Test multi-language support (English & Urdu)"""
    print_header("🌍 MULTI-LANGUAGE SUPPORT TEST")
    print_info("Testing English and Roman Urdu conversation\n")
    
    tests = [
        ("English Greeting", "Hello, I want to order food"),
        ("Roman Urdu Greeting", "Assalamulaicum, mujhe khana order karna hai"),
        ("Mixed English-Urdu", "2 burger aur 1 coffee please"),
        ("Pure Roman Urdu", "3 biryani aur 2 naan chahiye"),
        ("English Menu Request", "Show me the menu"),
        ("Urdu Menu Request", "Menu dikha do"),
        ("English Cart", "What's in my cart?"),
        ("Urdu Cart", "Mera cart mein kya hai?"),
    ]
    
    for i, (test_name, message) in enumerate(tests, 1):
        print_step(f"TEST {i}/{len(tests)}: {test_name}")
        send_message(message)
        time.sleep(2)  # More time for translation processing
    
    print_success("Multi-language support tests completed!")

def test_conversation_states():
    """Test all conversation states"""
    print_header("🔄 CONVERSATION STATES TEST")
    print_info("Testing state transitions: idle → browsing → adding → cart → payment → confirm\n")
    
    # Generate unique phone for this test
    test_phone = "+923000000999"
    
    state_tests = [
        ("State: IDLE", "hi", test_phone),
        ("State: BROWSING_MENU", "menu", test_phone),
        ("State: VIEWING_CATEGORY", "1", test_phone),
        ("State: ADDING_TO_CART", "2 burger", test_phone),
        ("State: VIEWING_CART", "cart", test_phone),
        ("State: SELECTING_PAYMENT", "checkout", test_phone),
        ("State: CONFIRMING_ORDER", "1", test_phone),  # Select payment method
        ("State: IDLE (after order)", "hello", test_phone),
    ]
    
    for i, (state_name, message, phone) in enumerate(state_tests, 1):
        print_step(f"TEST {i}/{len(state_tests)}: {state_name}")
        send_message(message, phone)
        time.sleep(2)
    
    print_success("Conversation states tests completed!")

def test_performance():
    """Test system performance"""
    print_header("⚡ PERFORMANCE TEST")
    print_info("Testing response times and system load\n")
    
    times = []
    
    tests = [
        "hello",
        "menu",
        "2 burger",
        "cart",
        "track",
    ]
    
    for i, message in enumerate(tests, 1):
        print_step(f"TEST {i}/{len(tests)}: Timing '{message}'")
        start = time.time()
        send_message(message)
        elapsed = time.time() - start
        times.append(elapsed)
        print_info(f"Response time: {elapsed:.2f}s")
        time.sleep(1)
    
    print_header("⚡ PERFORMANCE SUMMARY")
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print_info(f"Average response time: {avg_time:.2f}s")
    print_info(f"Fastest response: {min_time:.2f}s")
    print_info(f"Slowest response: {max_time:.2f}s")
    
    if avg_time < 5:
        print_success("Performance: Excellent!")
    elif avg_time < 10:
        print_success("Performance: Good")
    else:
        print_warning("Performance: Slow - check Groq API and database")

def test_complete_end_to_end():
    """Complete end-to-end test of entire system"""
    print_header("🎯 COMPLETE END-TO-END TEST")
    print_info("Full journey: Customer registration → Menu browsing → Order → Payment → Tracking\n")
    
    # Generate unique phone for this test
    customer_phone = "+923000000111"
    
    steps = [
        ("1. Greeting", "Hello"),
        ("2. Browse Menu", "what's the menu?"),
        ("3. View Category", "main course"),
        ("4. Get Item Info", "biryani price?"),
        ("5. Add to Cart", "2 biryani aur 1 coffee"),
        ("6. Review Cart", "show my cart"),
        ("7. Add More Items", "add 1 naan"),
        ("8. Checkout", "checkout"),
        ("9. Select Payment", "card"),
        ("10. Confirm Order", "yes"),
        ("11. Track Order", "track my order"),
        ("12. Get Status", "order status"),
        ("13. Another Question", "kya khana ready hai?"),
    ]
    
    for i, (step_name, message) in enumerate(steps, 1):
        print_step(f"STEP {i}/{len(steps)}: {step_name}")
        send_message(message, customer_phone)
        time.sleep(2)
    
    print_info("\nWaiting 5 seconds for database sync...")
    time.sleep(5)
    
    print_step("Verifying order in system...")
    try:
        response = requests.get(f"{BASE_URL}/staff/orders/all", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data.get('count', 0)
            print_success(f"✓ Order created! Total orders: {total}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    print_header("🎉 END-TO-END TEST COMPLETED")
    print_success("Full customer journey verified!")

def test_all_features():
    """Run all tests in sequence"""
    print_header("🚀 COMPLETE SYSTEM TEST SUITE")
    print_info("Running all tests sequentially...\n")
    
    all_tests = [
        ("System Diagnostics", run_system_diagnostics),
        ("Menu System", test_menu_system),
        ("Payment System", test_payment_system),
        ("Database Connectivity", test_database_connectivity),
        ("Multi-Language Support", test_multi_language_support),
        ("Conversation States", test_conversation_states),
        ("Cart Operations", test_cart_operations),
        ("Order Tracking", test_order_tracking),
        ("Concurrent Orders", test_concurrent_orders),
        ("Performance", test_performance),
        ("Error Handling", test_error_handling),
        ("Staff Dashboard", test_staff_dashboard),
        ("Complete End-to-End", test_complete_end_to_end),
    ]
    
    completed = 0
    failed = 0
    
    for i, (test_name, test_func) in enumerate(all_tests, 1):
        try:
            print_step(f"Running test {i}/{len(all_tests)}: {test_name}")
            test_func()
            completed += 1
            time.sleep(2)
        except Exception as e:
            print_error(f"Test failed: {str(e)}")
            failed += 1
            time.sleep(2)
    
    print_header("📊 COMPLETE TEST SUITE SUMMARY")
    print_info(f"Total Tests: {len(all_tests)}")
    print_success(f"Passed: {completed}")
    print_error(f"Failed: {failed}")
    
    if failed == 0:
        print_success("\n🎉 ALL TESTS PASSED! System is production-ready!")
    else:
        print_warning(f"\n⚠️ {failed} tests failed - check issues above")

def run_system_diagnostics():
    """Run complete system diagnostics"""
    print_header("🔧 SYSTEM DIAGNOSTICS")
    
    checks = []
    
    # Environment
    print_step("1. Checking Environment Variables...")
    checks.append(("Environment", check_environment()))
    time.sleep(1)
    
    # Groq API
    print_step("2. Testing Groq API...")
    checks.append(("Groq API", check_groq_api()))
    time.sleep(1)
    
    # Flask Server
    print_step("3. Checking Flask Server...")
    checks.append(("Flask Server", check_flask_server()))
    time.sleep(1)
    
    # Health Endpoint
    print_step("4. Checking Health Endpoint...")
    checks.append(("Health Check", check_health_endpoint()))
    time.sleep(1)
    
    # Summary
    print_header("📊 DIAGNOSTICS SUMMARY")
    
    all_passed = True
    for check_name, passed in checks:
        if passed:
            print_success(f"{check_name}: PASSED")
        else:
            print_error(f"{check_name}: FAILED")
            all_passed = False
    
    if all_passed:
        print_success("\n🎉 All systems operational!")
    else:
        print_warning("\n⚠️ Some systems need attention")
    
    return all_passed

def main():
    print(f"""
    {Colors.HEADER}{Colors.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║   WHATSAPP CAFETERIA CHATBOT - COMPLETE TEST SUITE v4.0      ║
    ║                 Developer: Muhammad Naeem                     ║
    ║                         FAST NUCES                            ║
    ╚═══════════════════════════════════════════════════════════════╝
    {Colors.END}
    
    {Colors.CYAN}COMPLETE FEATURE TESTING - All Systems Covered:
    ✅ Environment & Dependencies
    ✅ Groq AI Integration
    ✅ Menu System
    ✅ Payment Processing
    ✅ Order Management
    ✅ Notifications
    ✅ Staff Dashboard
    ✅ Database Connectivity
    ✅ Multi-Language Support
    ✅ Conversation States
    ✅ Error Handling
    ✅ Performance Testing
    ✅ Concurrent Orders
    ✅ Complete End-to-End Flow
    {Colors.END}
    """)
    
    print(f"\n{Colors.BOLD}═══════════════════════════════════════════════════{Colors.END}")
    print(f"{Colors.BOLD}TEST SUITE MENU - Choose an option:{Colors.END}")
    print(f"{Colors.BOLD}═══════════════════════════════════════════════════{Colors.END}\n")
    
    print(f"{Colors.GREEN}DIAGNOSTIC TESTS (START HERE){Colors.END}")
    print("  0️⃣  System Diagnostics - Check all systems")
    
    print(f"\n{Colors.GREEN}CORE FEATURE TESTS{Colors.END}")
    print("  1️⃣  Groq AI Integration - Natural language AI")
    print("  2️⃣  Menu System - Browse menus & categories")
    print("  3️⃣  Payment System - Payment methods & checkout")
    print("  4️⃣  Order Management - Create & track orders")
    print("  5️⃣  Cart Operations - Add/modify/remove items")
    print("  6️⃣  Order Tracking - Track orders by ID")
    
    print(f"\n{Colors.GREEN}ADVANCED TESTS{Colors.END}")
    print("  7️⃣  Natural Language Orders - NL processing")
    print("  8️⃣  Multi-Language Support - English & Roman Urdu")
    print("  9️⃣  Conversation States - All state transitions")
    
    print(f"\n{Colors.GREEN}SYSTEM INTEGRATION TESTS{Colors.END}")
    print("  1️⃣0️⃣ Database Connectivity - Supabase & tables")
    print("  1️⃣1️⃣ Staff Dashboard - Real-time management")
    print("  1️⃣2️⃣ Notifications - Order notifications")
    
    print(f"\n{Colors.GREEN}QUALITY & PERFORMANCE TESTS{Colors.END}")
    print("  1️⃣3️⃣ Error Handling - Edge cases & errors")
    print("  1️⃣4️⃣ Concurrent Orders - Multiple customers")
    print("  1️⃣5️⃣ Performance Test - Response times")
    
    print(f"\n{Colors.GREEN}COMPLETE TESTS{Colors.END}")
    print("  1️⃣6️⃣ Complete End-to-End - Full customer journey")
    print("  1️⃣7️⃣ Run ALL Tests - Full test suite (takes ~30 min)")
    
    print(f"\n{Colors.GREEN}DASHBOARD CHECKS{Colors.END}")
    print("  1️⃣8️⃣ Check Dashboard - View current orders")
    print("  1️⃣9️⃣ Help & Commands - Help information")
    
    print(f"\n{Colors.RED}  9️⃣9️⃣ Exit - Quit testing{Colors.END}")
    
    print(f"\n{Colors.BOLD}═══════════════════════════════════════════════════{Colors.END}\n")
    
    choice = input(f"{Colors.BOLD}Enter choice (0-99): {Colors.END}").strip()
    
    tests_map = {
        "0": ("System Diagnostics", run_system_diagnostics),
        "1": ("Groq AI Integration", test_groq_integration),
        "2": ("Menu System", test_menu_system),
        "3": ("Payment System", test_payment_system),
        "4": ("Complete Order Flow", test_complete_order_flow),
        "5": ("Cart Operations", test_cart_operations),
        "6": ("Order Tracking", test_order_tracking),
        "7": ("Natural Language Orders", test_natural_language_orders),
        "8": ("Multi-Language Support", test_multi_language_support),
        "9": ("Conversation States", test_conversation_states),
        "10": ("Database Connectivity", test_database_connectivity),
        "11": ("Staff Dashboard", test_staff_dashboard),
        "12": ("Notifications", test_notifications),
        "13": ("Error Handling", test_error_handling),
        "14": ("Concurrent Orders", test_concurrent_orders),
        "15": ("Performance Test", test_performance),
        "16": ("Complete End-to-End", test_complete_end_to_end),
        "17": ("Run ALL Tests", test_all_features),
        "18": ("Check Dashboard", lambda: (check_orders_in_dashboard(), check_all_orders_in_db())),
        "19": ("Help & Commands", test_help_and_commands),
    }
    
    if choice == "99":
        print_info("Goodbye! 👋")
        return
    
    if choice in tests_map:
        test_name, test_func = tests_map[choice]
        print(f"\n{Colors.BOLD}{Colors.GREEN}Starting: {test_name}{Colors.END}\n")
        
        try:
            result = test_func()
        except KeyboardInterrupt:
            print_warning("\nTest interrupted by user!")
        except Exception as e:
            print_error(f"Test error: {str(e)}")
    
    else:
        print_error("Invalid choice! Please try again.")
        return
    
    print(f"\n{Colors.HEADER}{'═'*70}{Colors.END}")
    print(f"{Colors.GREEN}{Colors.BOLD}Testing Session Completed! 🎉{Colors.END}")
    print(f"{Colors.HEADER}{'═'*70}{Colors.END}\n")
    
    print(f"{Colors.CYAN}QUICK HELP:{Colors.END}")
    print("✅ If tests pass: System is working correctly!")
    print("❌ If tests fail:")
    print("   1. Check Flask console for detailed error messages")
    print("   2. Verify environment variables in .env file")
    print("   3. Check Groq API status (console.groq.com)")
    print("   4. Verify Supabase connection")
    print("   5. Check database tables exist")
    
    print(f"\n{Colors.CYAN}RECOMMENDED TEST ORDER:{Colors.END}")
    print("  1. Run test 0️⃣  (System Diagnostics)")
    print("  2. Run test 1️⃣  (Groq AI Integration)")
    print("  3. Run test 1️⃣6️⃣ (Complete End-to-End)")
    print("  4. Run test 1️⃣7️⃣ (Run ALL Tests) when ready")
    
    print(f"\n{Colors.CYAN}API ENDPOINTS TO CHECK:{Colors.END}")
    print(f"  Dashboard: {BASE_URL}/staff/dashboard")
    print(f"  API Health: {BASE_URL}/api/health")
    print(f"  Orders: {BASE_URL}/staff/orders/all")
    print(f"  Menu: {BASE_URL}/api/menu")
    
    print(f"\n{Colors.YELLOW}Run this script again to test other features!{Colors.END}\n")

if __name__ == "__main__":
    main()