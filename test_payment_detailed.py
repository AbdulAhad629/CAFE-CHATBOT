"""
Test payment creation with detailed feedback
"""
import requests
import time

BASE_URL = "http://localhost:5000"
WEBHOOK_URL = f"{BASE_URL}/webhook/test-message"

phone = "923009999999"

print("\n" + "="*70)
print("PAYMENT CREATION TEST WITH DETAILED LOGGING")
print("="*70 + "\n")

print("📱 Creating order with JAZZCASH payment method...\n")
print("Watch Flask console for payment creation messages!")
print("Look for: [PAYMENT] ✅ Created payment ...\n")

steps = [
    ("menu", "Menu"),
    ("1", "Category 1"),
    ("1 burger", "1 burger"),
    ("checkout", "Checkout"),
    ("2", "JazzCash method"),
    ("yes", "Confirm"),
]

for msg, name in steps:
    print(f"▶️  {name}...", end=" ")
    requests.post(WEBHOOK_URL, json={"from": phone, "text": msg})
    time.sleep(0.3)
    print("✓")

print("\n" + "-"*70)
print("Checking if payment was created...\n")

# Give it a moment to process
time.sleep(1)

# Check the latest order
r = requests.get(f"{BASE_URL}/staff/orders/all")
if r.status_code == 200:
    orders = r.json().get('data', [])
    if orders:
        latest = orders[-1]
        print(f"Latest order: #{latest['id']}")
        print(f"  Payment Method: {latest.get('payment_method')}")
        print(f"  Payment ID: {latest.get('payment_id')}")
        print(f"  Amount: PKR {latest.get('total')}")
        
        if latest.get('payment_id'):
            print("\n✅ SUCCESS! Payment ID created and linked to order!")
        else:
            print("\n❌ Payment ID is still NULL")
            print("\n💡 Check Flask console for error messages:")
            print("   Look for: [PAYMENT] ❌ Error...")

print("\n" + "="*70 + "\n")
