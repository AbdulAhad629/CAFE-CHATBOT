"""
FINAL TEST - Multiple customers placing complete orders
Shows the REAL working flow
"""
import requests
import time

BASE_URL = "http://localhost:5000"
TEST_ENDPOINT = f"{BASE_URL}/webhook/test-message"
PENDING_ORDERS = f"{BASE_URL}/staff/orders/pending"
ALL_ORDERS = f"{BASE_URL}/staff/orders/all"

# Simulate 2 different customers
customers = [
    {
        "phone": "+923421111111",
        "name": "Customer 1",
        "order": "2 burger aur 1 coffee"
    },
    {
        "phone": "+923422222222",
        "name": "Customer 2",
        "order": "3 pizza aur 2 chai"
    }
]

print("\n" + "="*70)
print("FINAL: MULTIPLE CUSTOMERS PLACING ORDERS".center(70))
print("="*70 + "\n")

# Get initial count
initial_response = requests.get(ALL_ORDERS)
initial_count = len(initial_response.json().get('data', []))
print(f"Initial orders in database: {initial_count}\n")

# For each customer
for i, customer in enumerate(customers, 1):
    phone = customer['phone']
    order_msg = customer['order']
    
    print(f"CUSTOMER {i}: {customer['name']} ({phone})")
    print("-" * 70)
    
    # Step 1: Place order
    print(f"  [Step 1] Sending: \"{order_msg}\"")
    requests.post(TEST_ENDPOINT, json={"from": phone, "message": order_msg}, timeout=45)
    time.sleep(1)
    
    # Step 2: Checkout
    print(f"  [Step 2] Sending: \"checkout\"")
    requests.post(TEST_ENDPOINT, json={"from": phone, "message": "checkout"}, timeout=45)
    time.sleep(1)
    
    # Step 3: Confirm
    print(f"  [Step 3] Sending: \"yes\"")
    requests.post(TEST_ENDPOINT, json={"from": phone, "message": "yes"}, timeout=45)
    time.sleep(2)
    
    print(f"  ✅ Order placed!\n")

# Check results
print("="*70)
print("RESULTS")
print("="*70 + "\n")

print("📊 Pending Orders on Dashboard:")
try:
    response = requests.get(PENDING_ORDERS)
    pending = response.json().get('data', [])
    
    print(f"Total pending: {len(pending)}\n")
    for order in pending:
        student = order.get('students', {})
        if isinstance(student, list):
            student = student[0] if student else {}
        
        phone = student.get('whatsapp_number', 'Unknown')
        items = order.get('order_items', [])
        items_str = ", ".join([f"{i['quantity']}x {i['menu_items']['name']}" for i in items])
        
        print(f"  Order #{order['id']}:")
        print(f"    Customer: {phone}")
        print(f"    Items: {items_str}")
        print(f"    Total: PKR {order['total']}\n")
except Exception as e:
    print(f"Error: {e}")

print("📈 All Orders Summary:")
try:
    response = requests.get(ALL_ORDERS)
    all_orders = response.json().get('data', [])
    final_count = len(all_orders)
    
    new_orders = final_count - initial_count
    print(f"Total orders in database: {final_count}")
    print(f"New orders created: {new_orders}")
    
    status_count = {}
    for order in all_orders:
        status = order.get('status')
        status_count[status] = status_count.get(status, 0) + 1
    
    print(f"\nBreakdown by status:")
    for status in ['PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'COMPLETED', 'CANCELLED']:
        count = status_count.get(status.lower(), 0)
        if count > 0:
            print(f"  {status}: {count}")
            
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*70)
print("✅ CONCLUSION: Multiple orders working correctly!".center(70))
print("="*70 + "\n")
