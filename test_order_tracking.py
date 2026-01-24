"""
Order Tracking Test - Verify tracking functionality
"""
import requests
import time

BASE_URL = "http://localhost:5000"
TEST_ENDPOINT = f"{BASE_URL}/webhook/test-message"
ORDERS_ALL = f"{BASE_URL}/staff/orders/all"

print("\n" + "="*70)
print("ORDER TRACKING TEST".center(70))
print("="*70 + "\n")

# Get an order ID to track
print("[1] Fetching available orders...")
try:
    response = requests.get(ORDERS_ALL)
    orders = response.json().get('data', [])
    
    if orders:
        order_to_track = orders[0]
        order_id = order_to_track['id']
        customer_phone = order_to_track['students'][0]['whatsapp_number'] if isinstance(order_to_track['students'], list) else order_to_track['students']['whatsapp_number']
        
        print(f"    ✅ Found order #{order_id}")
        print(f"    Status: {order_to_track['status']}")
        print(f"    Total: PKR {order_to_track['total']}\n")
    else:
        print("    ❌ No orders found in database\n")
        exit(1)
except Exception as e:
    print(f"    ❌ Error: {e}\n")
    exit(1)

# Test 1: Track latest order (no order ID)
print("[2] Testing: Track latest order (sending 'track')")
print(f"    From: {customer_phone}")
print(f"    Message: 'track'")

try:
    response = requests.post(
        TEST_ENDPOINT,
        json={"from": customer_phone, "message": "track"},
        timeout=45
    )
    
    if response.status_code == 200:
        print(f"    ✅ Response: {response.status_code}\n")
    else:
        print(f"    ❌ Response: {response.status_code}\n")
except Exception as e:
    print(f"    ❌ Error: {e}\n")

time.sleep(2)

# Test 2: Track specific order
print("[3] Testing: Track specific order")
print(f"    From: {customer_phone}")
print(f"    Message: 'track {order_id}'")

try:
    response = requests.post(
        TEST_ENDPOINT,
        json={"from": customer_phone, "message": f"track {order_id}"},
        timeout=45
    )
    
    if response.status_code == 200:
        print(f"    ✅ Response: {response.status_code}\n")
    else:
        print(f"    ❌ Response: {response.status_code}\n")
except Exception as e:
    print(f"    ❌ Error: {e}\n")

time.sleep(2)

# Test 3: Status command
print("[4] Testing: Status command")
print(f"    From: {customer_phone}")
print(f"    Message: 'status'")

try:
    response = requests.post(
        TEST_ENDPOINT,
        json={"from": customer_phone, "message": "status"},
        timeout=45
    )
    
    if response.status_code == 200:
        print(f"    ✅ Response: {response.status_code}\n")
    else:
        print(f"    ❌ Response: {response.status_code}\n")
except Exception as e:
    print(f"    ❌ Error: {e}\n")

time.sleep(2)

# Test 4: Order history
print("[5] Testing: Order history command")
print(f"    From: {customer_phone}")
print(f"    Message: 'my orders'")

try:
    response = requests.post(
        TEST_ENDPOINT,
        json={"from": customer_phone, "message": "my orders"},
        timeout=45
    )
    
    if response.status_code == 200:
        print(f"    ✅ Response: {response.status_code}\n")
    else:
        print(f"    ❌ Response: {response.status_code}\n")
except Exception as e:
    print(f"    ❌ Error: {e}\n")

print("="*70)
print("✅ TRACKING TEST COMPLETED".center(70))
print("="*70)
print("\nCheck Flask console for response messages")
print("Expected: Bot sends order status, items, and estimated time\n")
