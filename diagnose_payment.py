"""
Test payment by checking what gets logged
"""
import requests
import time
import subprocess
import sys

BASE_URL = "http://localhost:5000"
WEBHOOK_URL = f"{BASE_URL}/webhook/test-message"

print("\n" + "="*70)
print("DIAGNOSTIC: Payment Service Check")
print("="*70 + "\n")

# First check: Can we import payment_service from the running app?
print("Testing if flask app can load payment_service...\n")

test_code = """
import sys
sys.path.insert(0, 'd:/whatsapp-cafeteria-bot')

try:
    # This is what chatbot_service does
    from app.services.payment_service import payment_service
    print("✅ payment_service imported successfully")
    print(f"Instance type: {type(payment_service)}")
    print(f"Has create_payment method: {hasattr(payment_service, 'create_payment')}")
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
"""

result = subprocess.run([sys.executable, '-c', test_code], capture_output=True, text=True)
print("STDOUT:", result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("\n" + "="*70)
print("Now checking if orders table has payment_id field...")
print("="*70 + "\n")

# Check orders table structure
try:
    response = requests.get(f"{BASE_URL}/api/orders")
    if response.status_code == 200:
        orders = response.json().get('data', [])
        if orders:
            first_order = orders[0]
            print(f"Sample order keys: {list(first_order.keys())}")
            print(f"Has 'payment_id' field: {'payment_id' in first_order}")
            if 'payment_id' in first_order:
                print(f"Sample payment_id values:")
                for order in orders[:3]:
                    print(f"  Order #{order['id']}: payment_id = {order.get('payment_id')}")
        else:
            print("No orders found")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*70 + "\n")
