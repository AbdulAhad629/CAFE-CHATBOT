"""
Test order creation through running chatbot and log payment info
"""
import requests
import time

BASE_URL = "http://localhost:5000"
WEBHOOK_URL = f"{BASE_URL}/webhook/test-message"

phone = "923008888888"

print("\n" + "="*70)
print("PAYMENT CREATION TEST VIA CHATBOT")
print("="*70 + "\n")

print("Placing order with cash payment...\n")

# Menu
print("1️⃣  Sending: menu")
requests.post(WEBHOOK_URL, json={"from": phone, "text": "menu"})
time.sleep(1)

# Category
print("2️⃣  Sending: 1")
requests.post(WEBHOOK_URL, json={"from": phone, "text": "1"})
time.sleep(1)

# Item
print("3️⃣  Sending: 1 pizza")
requests.post(WEBHOOK_URL, json={"from": phone, "text": "1 pizza"})
time.sleep(1)

# Checkout
print("4️⃣  Sending: checkout")
requests.post(WEBHOOK_URL, json={"from": phone, "text": "checkout"})
time.sleep(1)

# Payment method (cash = 1)
print("5️⃣  Sending: 1 (cash payment)")
requests.post(WEBHOOK_URL, json={"from": phone, "text": "1"})
time.sleep(1)

# Confirm
print("6️⃣  Sending: yes")
resp = requests.post(WEBHOOK_URL, json={"from": phone, "text": "yes"})
print(f"   Status: {resp.status_code}\n")

print("✅ Order should be created now!")
print("\nCheck Flask console for these log messages:")
print("   [ORDER] Creating order #X, use_payment=True")
print("   [PAYMENT] Attempting to create payment for order #X")
print("   [PAYMENT] ✅ Payment created: PAY-X-YYYY")
print("\nIf you see '[PAYMENT] ⚠️  Payment service not available', that's the problem!")
print("\n" + "="*70 + "\n")
