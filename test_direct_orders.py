"""
Direct order creation test - bypassing chatbot
This helps diagnose if orders ARE being created properly
"""
import requests
import json

BASE_URL = "http://localhost:5000"

# Test data
order1 = {
    "student_id": 1,
    "items": [
        {
            "menu_item_id": 1,
            "quantity": 2,
            "subtotal": 500
        },
        {
            "menu_item_id": 8,
            "quantity": 1,
            "subtotal": 100
        }
    ],
    "total": 600
}

order2 = {
    "student_id": 2,
    "items": [
        {
            "menu_item_id": 5,
            "quantity": 2,
            "subtotal": 900
        }
    ],
    "total": 900
}

print("\n" + "="*70)
print("DIRECT ORDER CREATION TEST".center(70))
print("="*70 + "\n")

for i, order in enumerate([order1, order2], 1):
    print(f"[{i}] Creating order directly...")
    print(f"    Student ID: {order['student_id']}")
    print(f"    Total: PKR {order['total']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/orders/",
            json=order,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            order_id = data.get('data', {}).get('order_id')
            print(f"    ✅ Order #{order_id} created successfully!\n")
        else:
            print(f"    ❌ Failed: {response.status_code}")
            print(f"    {response.text}\n")
    
    except Exception as e:
        print(f"    ❌ Error: {e}\n")

print("Checking if orders appear on dashboard...")
try:
    response = requests.get(f"{BASE_URL}/staff/orders/pending")
    data = response.json()
    orders = data.get('data', [])
    
    print(f"✅ Found {len(orders)} pending orders on dashboard\n")
    for order in orders:
        print(f"Order #{order['id']}: {order['status'].upper()}")

except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*70 + "\n")
