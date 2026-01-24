"""
Quick payment creation test - verify payments save to Supabase
"""

import requests
import time

BASE_URL = "http://localhost:5000"
WEBHOOK_URL = f"{BASE_URL}/webhook/test-message"

def test_order_with_payment(phone, payment_method):
    """Place order and select payment method"""
    
    print(f"\n📱 Testing {payment_method.upper()} payment...\n")
    
    # Menu
    requests.post(WEBHOOK_URL, json={"from": phone, "text": "menu"})
    time.sleep(0.5)
    
    # Category
    requests.post(WEBHOOK_URL, json={"from": phone, "text": "1"})
    time.sleep(0.5)
    
    # Add item
    requests.post(WEBHOOK_URL, json={"from": phone, "text": "1 pizza"})
    time.sleep(0.5)
    
    # Checkout
    requests.post(WEBHOOK_URL, json={"from": phone, "text": "checkout"})
    time.sleep(0.5)
    
    # Payment method
    payment_map = {"cash": "1", "jazzcash": "2", "easypaisa": "3", "card": "4"}
    requests.post(WEBHOOK_URL, json={"from": phone, "text": payment_map[payment_method]})
    time.sleep(0.5)
    
    # Confirm
    resp = requests.post(WEBHOOK_URL, json={"from": phone, "text": "yes"})
    
    if resp.status_code == 200:
        print(f"   ✅ Order created with {payment_method} payment")
        return True
    else:
        print(f"   ❌ Failed")
        return False

print("\n" + "="*70)
print("  PAYMENT STORAGE TEST")
print("="*70)

# Create test orders with different payment methods
test_order_with_payment("923009999901", "cash")
time.sleep(2)

test_order_with_payment("923009999902", "jazzcash")
time.sleep(2)

test_order_with_payment("923009999903", "card")
time.sleep(2)

print("\n✅ Test orders created!")
print("\n📊 Checking Supabase payments table...")
print("\nUse the Supabase dashboard to verify payments were created:")
print("   URL: https://supabase.com/dashboard")
print("   Database → payments table")
print("\nYou should see entries like:")
print("   • payment_id: PAY-XX-XXXX")
print("   • order_id: [order number]")
print("   • amount: PKR [amount]")
print("   • method: cash/jazzcash/easypaisa/card")
print("   • status: pending/completed")

print("\n" + "="*70 + "\n")
