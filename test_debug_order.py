"""
Debug script to trace order creation through chatbot
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"
TEST_ENDPOINT = f"{BASE_URL}/webhook/test-message"
ORDERS_ALL = f"{BASE_URL}/staff/orders/all"

print("\n" + "="*70)
print("CHATBOT ORDER CREATION DEBUG".center(70))
print("="*70 + "\n")

# Get initial order count
print("[1] Getting initial order count...")
try:
    response = requests.get(ORDERS_ALL)
    initial_count = len(response.json().get('data', []))
    print(f"    ✅ Initial orders: {initial_count}\n")
except:
    initial_count = 0
    print(f"    ❌ Could not get initial count\n")

# Send message 1
phone1 = "+923111111111"
message1 = "2 burger aur 1 coffee"

print(f"[2] Sending message 1 from {phone1}...")
print(f"    Message: {message1}")
print(f"    Expected: Creates student, cart with 2 burgers + 1 coffee")

try:
    response = requests.post(
        TEST_ENDPOINT,
        json={"from": phone1, "message": message1},
        timeout=45
    )
    print(f"    Response: {response.status_code}")
    data = response.json()
    print(f"    Status: {data.get('status')}\n")
except Exception as e:
    print(f"    ❌ Error: {e}\n")

time.sleep(2)

# Check if message was processed
print("[3] Checking orders after first message...")
try:
    response = requests.get(ORDERS_ALL)
    orders_after_msg1 = response.json().get('data', [])
    new_count = len(orders_after_msg1)
    print(f"    Total orders: {new_count}")
    print(f"    New orders created: {new_count - initial_count}\n")
    
    if new_count > initial_count:
        new_order = orders_after_msg1[0]
        print(f"    Latest order:")
        print(f"      ID: {new_order.get('id')}")
        print(f"      Status: {new_order.get('status')}")
        print(f"      Student ID: {new_order.get('student_id')}")
        print(f"      Total: PKR {new_order.get('total')}\n")
except Exception as e:
    print(f"    ❌ Error: {e}\n")

# Send checkout message 1
print(f"[4] Sending checkout message from {phone1}...")
print(f"    Message: checkout")

try:
    response = requests.post(
        TEST_ENDPOINT,
        json={"from": phone1, "message": "checkout"},
        timeout=45
    )
    print(f"    Response: {response.status_code}")
    data = response.json()
    print(f"    Status: {data.get('status')}\n")
except Exception as e:
    print(f"    ❌ Error: {e}\n")

time.sleep(2)

# Confirm checkout
print(f"[5] Confirming order from {phone1}...")
print(f"    Message: yes")

try:
    response = requests.post(
        TEST_ENDPOINT,
        json={"from": phone1, "message": "yes"},
        timeout=45
    )
    print(f"    Response: {response.status_code}")
    data = response.json()
    print(f"    Status: {data.get('status')}\n")
except Exception as e:
    print(f"    ❌ Error: {e}\n")

time.sleep(3)

# Check final count
print("[6] Final check - all orders...")
try:
    response = requests.get(ORDERS_ALL)
    final_data = response.json().get('data', [])
    final_count = len(final_data)
    
    print(f"    Total orders in database: {final_count}")
    print(f"    Orders created in this test: {final_count - initial_count}\n")
    
    # Show last 3 orders
    if final_data:
        print(f"    Last 3 orders:")
        for order in final_data[:3]:
            student = order.get('students', {})
            if isinstance(student, list):
                student = student[0] if student else {}
            student_name = student.get('name', 'Unknown')
            phone = student.get('whatsapp_number', 'N/A')
            
            print(f"      Order #{order['id']}: {order['status'].upper()} - PKR {order['total']} ({student_name})")

except Exception as e:
    print(f"    ❌ Error: {e}")

print("\n" + "="*70 + "\n")
