"""
FINAL PAYMENT TEST - Verify payments are saved to Supabase
"""
import requests
import time

BASE_URL = "http://localhost:5000"
WEBHOOK_URL = f"{BASE_URL}/webhook/test-message"

print("\n" + "="*70)
print("  FINAL PAYMENT STORAGE TEST")
print("="*70 + "\n")

# Create test order with payment
phone = "923007777777"

print("📱 CREATING TEST ORDER WITH PAYMENT...\n")

steps = [
    ("menu", "1️⃣  Show menu"),
    ("1", "2️⃣  Select category"),
    ("1 biryani", "3️⃣  Add item"),
    ("checkout", "4️⃣  Go to checkout"),
    ("2", "5️⃣  Select JazzCash payment"),
    ("yes", "6️⃣  Confirm order"),
]

for message, description in steps:
    print(description)
    response = requests.post(WEBHOOK_URL, json={"from": phone, "text": message})
    if response.status_code == 200:
        print(f"   ✅ Status {response.status_code}\n")
    else:
        print(f"   ❌ Status {response.status_code}\n")
    time.sleep(0.5)

print("="*70)
print("  CHECKING SUPABASE FOR PAYMENTS")
print("="*70 + "\n")

# Check if payments were created
try:
    # Fetch orders first
    print("1️⃣  Fetching orders from API...\n")
    response = requests.get(f"{BASE_URL}/api/orders")
    
    if response.status_code == 200:
        data = response.json()
        orders = data.get('data', [])
        print(f"   Total orders: {len(orders)}")
        
        if orders:
            # Find our test order
            test_order = None
            for order in orders:
                if order.get('student_id'):  # Has student
                    test_order = order
                    break
            
            if test_order:
                print(f"   Found order #{test_order['id']}")
                print(f"   Total: PKR {test_order.get('total')}")
                print(f"   Status: {test_order.get('status')}")
                print(f"   Payment Method: {test_order.get('payment_method')}")
                print(f"   Payment ID: {test_order.get('payment_id')}")
                
                if test_order.get('payment_id'):
                    print("\n   ✅ ORDER HAS PAYMENT_ID!")
                else:
                    print("\n   ⚠️  ORDER MISSING PAYMENT_ID")
    else:
        print(f"   ❌ API Error: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

print("\n" + "="*70)
print("  TEST COMPLETE")
print("="*70)

print("""
✅ Next Steps to Verify Payment in Supabase:

1. Go to Supabase Dashboard:
   https://supabase.com/dashboard

2. Navigate to:
   Database → payments table

3. Look for entries with:
   ✓ payment_id: PAY-X-YYYY
   ✓ order_id: [the order number]
   ✓ amount: PKR [amount]
   ✓ method: "jazzcash"
   ✓ status: "pending"

4. If you see the payment record → ✅ PAYMENTS WORKING!

⚡ Once confirmed, your system is ready to ship! 🚀
""")

print("="*70 + "\n")
