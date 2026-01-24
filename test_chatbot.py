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

def test_help_and_commands():
    """Test help and command features"""
    print_header("❓ HELP & COMMANDS TEST")
    
    tests = [
        ("Help Command", "help"),
        ("Menu Command", "menu"),
        ("Cancel Command", "cancel"),
    ]
    
    for i, (test_name, message) in enumerate(tests, 1):
        print_step(f"TEST {i}/{len(tests)}: {test_name}")
        send_message(message)
        time.sleep(1)
    
    print_success("Help and commands tests completed!")

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
    ║   WHATSAPP CAFETERIA CHATBOT - GROQ TESTING TOOL v3.0        ║
    ╚═══════════════════════════════════════════════════════════════╝
    {Colors.END}
    
    {Colors.CYAN}NEW FEATURES IN THIS VERSION:
    ✅ Groq API integration testing
    ✅ Natural language order testing
    ✅ Environment variable checks
    ✅ System health diagnostics
    ✅ Increased timeout for AI processing (45s)
    ✅ Better response time tracking
    {Colors.END}
    """)
    
    print(f"\n{Colors.BOLD}Choose test type:{Colors.END}\n")
    print("0. 🔧 System Diagnostics (START HERE!)")
    print("1. 🤖 Groq AI Integration Test")
    print("2. 🗣️ Natural Language Orders Test")
    print("3. 🔄 Complete Order Flow Test")
    print("4. 🛒 Cart Operations Test")
    print("5. 📍 Order Tracking Test")
    print("6. ❓ Help & Commands Test")
    print("7. 📊 Check Dashboard Orders")
    print("9. ❌ Exit")
    
    choice = input(f"\n{Colors.BOLD}Enter choice: {Colors.END}").strip()
    
    if choice == "0":
        if run_system_diagnostics():
            print_info("\nSystem is ready! You can run other tests now.")
        else:
            print_warning("\nFix the issues above before running other tests.")
    
    elif choice == "1":
        test_groq_integration()
    
    elif choice == "2":
        test_natural_language_orders()
    
    elif choice == "3":
        test_complete_order_flow()
    
    elif choice == "4":
        test_cart_operations()
    
    elif choice == "5":
        test_order_tracking()
    
    elif choice == "6":
        test_help_and_commands()
    
    elif choice == "7":
        print_header("📊 DASHBOARD ORDERS CHECK")
        pending = check_orders_in_dashboard()
        print_info("")
        total = check_all_orders_in_db()
    
    elif choice == "9":
        print_info("Goodbye!")
        return
    
    else:
        print_error("Invalid choice!")
        return
    
    print(f"\n{Colors.HEADER}{'═'*70}{Colors.END}")
    print(f"{Colors.GREEN}{Colors.BOLD}Testing finished! 🎉{Colors.END}")
    print(f"{Colors.HEADER}{'═'*70}{Colors.END}\n")
    
    print(f"{Colors.CYAN}Debugging Tips:{Colors.END}")
    print("1. If Groq API fails:")
    print("   - Check GROQ_API_KEY in .env")
    print("   - Check Groq console: https://console.groq.com")
    print("   - Verify API rate limits (30 req/min)")
    print("2. If timeouts occur:")
    print("   - Groq may be slow during peak hours")
    print("   - Check your internet connection")
    print("   - Check Flask console for errors")
    print("3. Check Flask console for detailed error messages")
    print("4. Verify Supabase connection is stable")
    print(f"\n{Colors.YELLOW}Run this script again to test more features!{Colors.END}\n")

if __name__ == "__main__":
    main()