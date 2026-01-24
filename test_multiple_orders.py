"""
Quick test to place multiple orders with different customers
"""
import requests
import time

BASE_URL = "http://localhost:5000"
TEST_ENDPOINT = f"{BASE_URL}/webhook/test-message"
ORDERS_CHECK = f"{BASE_URL}/staff/orders/pending"

# Place 3 orders from different customers
orders = [
    ("+923001111111", "2 burger aur 1 coffee"),
    ("+923002222222", "3 pizza aur chai"),
    ("+923003333333", "1 burger, 2 fries, aur 1 cold coffee"),
]

print("\n" + "="*70)
print("PLACING MULTIPLE ORDERS TEST".center(70))
print("="*70 + "\n")

for i, (phone, message) in enumerate(orders, 1):
    print(f"[{i}] Placing order from {phone}...")
    print(f"    Message: {message}")
    
    try:
        response = requests.post(
            TEST_ENDPOINT,
            json={"from": phone, "message": message},
            timeout=45
        )
        
        if response.status_code == 200:
            print(f"    ✅ Order placed successfully!\n")
        else:
            print(f"    ❌ Failed with status {response.status_code}\n")
    
    except Exception as e:
        print(f"    ❌ Error: {e}\n")
    
    time.sleep(2)

print("Waiting 3 seconds for database sync...")
time.sleep(3)

print("\nChecking dashboard for orders...")
try:
    response = requests.get(ORDERS_CHECK)
    data = response.json()
    orders_data = data.get('data', [])
    
    print(f"\n✅ Found {len(orders_data)} pending orders:\n")
    for order in orders_data:
        order_id = order.get('id')
        status = order.get('status')
        total = order.get('total')
        
        student = order.get('students', {})
        if isinstance(student, list):
            student = student[0] if student else {}
        
        student_name = student.get('name', 'Unknown')
        whatsapp = student.get('whatsapp_number', 'N/A')
        
        items = order.get('order_items', [])
        items_str = ", ".join([f"{item['quantity']}x {item['menu_items']['name']}" for item in items]) if items else "N/A"
        
        print(f"Order #{order_id}:")
        print(f"  Status: {status.upper()}")
        print(f"  Customer: {student_name} ({whatsapp})")
        print(f"  Items: {items_str}")
        print(f"  Total: PKR {total}\n")

except Exception as e:
    print(f"Error checking orders: {e}")

# Also check order statuses
print("\nChecking ALL orders and their statuses...")
try:
    response = requests.get(f"{BASE_URL}/staff/orders/all")
    data = response.json()
    all_orders = data.get('data', [])
    
    print(f"Total orders in database: {len(all_orders)}\n")
    
    status_count = {}
    for order in all_orders:
        status = order.get('status', 'unknown')
        status_count[status] = status_count.get(status, 0) + 1
    
    print("Orders by status:")
    for status, count in sorted(status_count.items()):
        print(f"  {status.upper()}: {count}")

except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*70 + "\n")
