"""
Chatbot Testing Script - FIXED VERSION
Increased timeout and better error handling
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"
TEST_ENDPOINT = f"{BASE_URL}/webhook/test-message"
ORDER_API = f"{BASE_URL}/api/orders"
PHONE = "+923001234567"

# INCREASED TIMEOUT FROM 10 TO 30 SECONDS
REQUEST_TIMEOUT = 30

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

def send_message(message, phone=PHONE, retry=True):
    """Send a test message to the chatbot"""
    print(f"\n{Colors.BLUE}{'─'*70}{Colors.END}")
    print(f"{Colors.BOLD}📤 USER: {message}{Colors.END}")
    print(f"{Colors.BLUE}{'─'*70}{Colors.END}")
    
    payload = {
        "from": phone,
        "message": message
    }
    
    try:
        print_info(f"Sending request... (timeout: {REQUEST_TIMEOUT}s)")
        response = requests.post(
            TEST_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT  # INCREASED TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Status: {result.get('status')}")
            print_info("Bot response logged in Flask console")
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
        print_warning("  1. Database query is slow")
        print_warning("  2. WhatsApp API is slow (if using real WhatsApp)")
        print_warning("  3. Too many operations in one request")
        
        if retry:
            print_info("Retrying once...")
            time.sleep(2)
            return send_message(message, phone, retry=False)
        return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def update_order_status(order_id, new_status):
    """Update order status via API"""
    print_step(f"Updating Order #{order_id} status to '{new_status}'")
    
    try:
        response = requests.patch(
            f"{ORDER_API}/{order_id}/status",
            json={"status": new_status},
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Order status updated!")
            print_info(f"Notification sent: {result.get('notification_sent', False)}")
            time.sleep(0.5)
            return result
        else:
            print_error(f"Failed to update status: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error updating status: {str(e)}")
        return None

def get_order_details(order_id):
    """Get order details via API"""
    print_step(f"Fetching Order #{order_id} details")
    
    try:
        response = requests.get(f"{ORDER_API}/{order_id}", timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            order = result.get('data', {})
            print_success("Order details retrieved!")
            print_info(f"Order ID: #{order.get('id')}")
            print_info(f"Status: {order.get('status')}")
            print_info(f"Total: PKR {order.get('total')}")
            return order
        else:
            print_error(f"Order not found: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error fetching order: {str(e)}")
        return None

def get_recent_orders():
    """Get recent orders"""
    print_step("Fetching recent orders (last 24 hours)")
    
    try:
        response = requests.get(f"{ORDER_API}/recent", timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            orders = result.get('data', [])
            print_success(f"Found {len(orders)} recent orders")
            for order in orders[:5]:
                print_info(f"Order #{order['id']} - PKR {order['total']} - {order['status']}")
            return orders
        else:
            print_error(f"Failed: {response.text}")
            return []
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return []

def check_flask_server():
    """Check if Flask server is running and responding"""
    print_header("🔍 CHECKING FLASK SERVER")
    
    try:
        print_info("Pinging Flask server...")
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print_success("Flask server is running!")
            data = response.json()
            print_info(f"API: {data.get('message')}")
            print_info(f"Version: {data.get('version')}")
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

def test_simple_message():
    """Test a single simple message"""
    print_header("🧪 SIMPLE MESSAGE TEST")
    print_info("Testing basic chatbot response\n")
    
    result = send_message("help")
    
    if result:
        print_success("Simple test passed!")
        return True
    else:
        print_error("Simple test failed!")
        print_warning("Check Flask console for errors")
        return False

def test_complete_order_flow():
    """Test complete order flow from start to finish"""
    print_header("🤖 COMPLETE ORDER FLOW TEST")
    print_info("This simulates a full customer journey from start to finish\n")
    
    steps = [
        ("Start Conversation", "hi"),
        ("Select Category", "Main Course"),
        ("Select Item", "Chicken Burger"),
        ("Enter Quantity", "2"),
        ("View Cart", "cart"),
        ("Start Checkout", "checkout"),
        ("Confirm Order", "yes")
    ]
    
    failed_steps = []
    
    for i, (step_name, message) in enumerate(steps, 1):
        print_step(f"TEST {i}/{len(steps)}: {step_name}")
        result = send_message(message)
        
        if not result:
            failed_steps.append(step_name)
            print_warning(f"Step '{step_name}' failed, continuing...")
        
        time.sleep(1)  # Small delay between steps
    
    print_header("✅ COMPLETE ORDER FLOW TEST FINISHED")
    
    if failed_steps:
        print_warning(f"Failed steps: {', '.join(failed_steps)}")
        print_info("Check Flask console for error details")
    else:
        print_success("All steps passed!")
    
    print_info("Check Flask console for full conversation log")
    print_info("Check Supabase 'orders' table for new order")

def test_order_tracking():
    """Test order tracking feature"""
    print_header("📍 ORDER TRACKING TEST")
    
    tests = [
        ("Track Latest Order", "track"),
        ("Track Specific Order", "track 1"),
        ("Status Command", "status")
    ]
    
    for i, (test_name, message) in enumerate(tests, 1):
        print_step(f"TEST {i}/{len(tests)}: {test_name}")
        send_message(message)
        time.sleep(1)
    
    print_success("Order tracking tests completed!")

def test_order_history():
    """Test order history feature"""
    print_header("📜 ORDER HISTORY TEST")
    
    print_step("TEST: View Order History")
    send_message("my orders")
    
    print_success("Order history test completed!")

def test_help_command():
    """Test help command"""
    print_header("❓ HELP COMMAND TEST")
    
    print_step("TEST: Show Help")
    send_message("help")
    
    print_success("Help command test completed!")

def test_cart_operations():
    """Test cart operations"""
    print_header("🛒 CART OPERATIONS TEST")
    
    tests = [
        ("View Empty Cart", "cart"),
        ("Start Order", "menu"),
        ("Select Category", "Main Course"),
        ("Select Item", "Pizza"),
        ("Enter Quantity", "1"),
        ("View Cart Again", "cart"),
        ("Clear Cart", "clear cart")
    ]
    
    for i, (test_name, message) in enumerate(tests, 1):
        print_step(f"TEST {i}/{len(tests)}: {test_name}")
        send_message(message)
        time.sleep(0.5)
    
    print_success("Cart operations tests completed!")

def test_api_endpoints():
    """Test various API endpoints"""
    print_header("🔌 API ENDPOINTS TEST")
    
    print_step("TEST 1: Get Recent Orders")
    get_recent_orders()
    time.sleep(1)
    
    print_step("TEST 2: Get Order Stats")
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        response = requests.get(
            f"{ORDER_API}/stats?start_date={today}&end_date={today}",
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            stats = response.json().get('data', {})
            print_success("Stats retrieved!")
            print_info(f"Total Orders: {stats.get('total_orders', 0)}")
            print_info(f"Total Revenue: PKR {stats.get('total_revenue', 0)}")
            print_info(f"Average Order: PKR {stats.get('average_order_value', 0):.2f}")
        else:
            print_error("Failed to get stats")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    time.sleep(1)
    
    print_step("TEST 3: Get Pending Count")
    try:
        response = requests.get(f"{ORDER_API}/pending-count", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            count = response.json().get('data', {}).get('pending_count', 0)
            print_success(f"Pending orders: {count}")
        else:
            print_error("Failed to get count")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    print_success("API endpoints tests completed!")

def main():
    print(f"""
    {Colors.HEADER}{Colors.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║     WHATSAPP CAFETERIA CHATBOT - TESTING TOOL v2.0           ║
    ╚═══════════════════════════════════════════════════════════════╝
    {Colors.END}
    
    {Colors.CYAN}IMPROVEMENTS IN THIS VERSION:
    ✅ Increased timeout from 10s to 30s
    ✅ Automatic retry on timeout
    ✅ Better error messages
    ✅ Server connectivity check
    ✅ Graceful failure handling
    {Colors.END}
    """)
    
    # First check if Flask is running
    if not check_flask_server():
        return
    
    print(f"\n{Colors.BOLD}Choose test type:{Colors.END}\n")
    print("0. 🧪 Simple Test (start here if having issues)")
    print("1. 🔄 Complete Order Flow")
    print("2. 📍 Order Tracking Test")
    print("3. 📜 Order History Test")
    print("4. ❓ Help Command Test")
    print("5. 🛒 Cart Operations Test")
    print("6. 🔌 API Endpoints Test")
    print("9. ❌ Exit")
    
    choice = input(f"\n{Colors.BOLD}Enter choice: {Colors.END}").strip()
    
    if choice == "0":
        test_simple_message()
    elif choice == "1":
        test_complete_order_flow()
    elif choice == "2":
        test_order_tracking()
    elif choice == "3":
        test_order_history()
    elif choice == "4":
        test_help_command()
    elif choice == "5":
        test_cart_operations()
    elif choice == "6":
        test_api_endpoints()
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
    print("1. If timeouts persist:")
    print("   - Check Flask console for slow database queries")
    print("   - Check Supabase connection is stable")
    print("   - Try disabling WhatsApp API calls temporarily")
    print("2. Check Flask console for detailed error messages")
    print("3. Verify Supabase tables have correct data")
    print(f"\n{Colors.YELLOW}Run this script again to test more features!{Colors.END}\n")

if __name__ == "__main__":
    main()